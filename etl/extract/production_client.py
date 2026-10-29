from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
import time
from typing import Any, Callable
from urllib.parse import urlsplit

import requests

from etl.config import Settings
from etl.contracts.v31 import DICTIONARY_HEADERS, metadata_drift
from etl.contracts.v31 import canonical_digest
from etl.extract.metadata_normalizer import normalize_metadata
from etl.models.metadata import MetadataModel

# Verified against REDCap's Vanderbilt-maintained external-module API source.
# A local adapter does not verify the deployed REDCap version/configuration.
API_METADATA_KEYS = [
    "field_name", "form_name", "section_header", "field_type", "field_label",
    "select_choices_or_calculations", "field_note",
    "text_validation_type_or_show_slider_number", "text_validation_min",
    "text_validation_max", "identifier", "branching_logic", "required_field",
    "custom_alignment", "question_number", "matrix_group_name", "matrix_ranking",
    "field_annotation",
]
TRANSIENT_STATUS = frozenset({429, 502, 503, 504})


class RedcapClientError(RuntimeError):
    """Sanitised error without token, URL, payload, record or server body."""


class RedcapAuthorisationError(RedcapClientError):
    pass


class RedcapMetadataDrift(RedcapClientError):
    pass


@dataclass(frozen=True)
class ExportScope:
    """Requested scope an approved external policy provider validates before HTTP.

    This never asserts that approval exists. The provider must check actual
    project-level country/data boundaries and environment-managed identity.
    Post-download country filtering cannot authorise the original transfer.
    """
    operation: str
    project_id: str
    environment: str
    api_endpoint: str
    service_identity_fingerprint: str
    fields: tuple[str, ...]
    events: tuple[str, ...]
    records: tuple[str, ...]
    full_project_records: bool
    allowed_response_fields: tuple[str, ...]


@dataclass(frozen=True)
class SourceSnapshot:
    records: list[dict[str, Any]]
    metadata: list[dict[str, Any]]
    metadata_sha256: str
    record_id_field: str
    contract_drift: list[dict[str, Any]]


def metadata_to_dictionary(raw: Any) -> list[dict[str, str]]:
    """Strict, lossless adapter for the actual native 18-key metadata shape."""
    if not isinstance(raw, list) or not raw:
        raise RedcapMetadataDrift("REDCap metadata is unavailable or unsupported")
    rows = []
    for field in raw:
        if (not isinstance(field, dict) or set(field) != set(API_METADATA_KEYS)
                or any(not isinstance(value, str) for value in field.values())):
            raise RedcapMetadataDrift("REDCap metadata schema differs from approved local adapter")
        rows.append({header: field[key] for header, key in zip(DICTIONARY_HEADERS, API_METADATA_KEYS)})
    return rows


class ProductionRedcapClient:
    """Native REDCap export with a default-deny production boundary.

    Requests require an explicit policy provider, even with a token.
    source_runtime.build_collector supplies a configured source service grant.
    Injected synthetic test policy/transport establishes neither live identity
    permission nor country-transfer approval.
    """
    source_mode = "production"

    def __init__(self, settings: Settings, *,
                 authorisation_provider: Callable[[ExportScope], bool] | None = None,
                 session: Any | None = None, contract: dict[str, Any] | None = None,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        self._api_url = settings.redcap_api_url
        self._token = settings.redcap_api_token or ""
        self._timeout = settings.http_timeout_seconds
        self._max_attempts = settings.http_max_retries
        self._project_id = settings.redcap_project_id
        self._environment = settings.app_env
        self._authorisation_provider = authorisation_provider
        self._session = session if session is not None else requests.Session()
        self._sleep = sleep
        if contract is None:
            contract = json.loads((Path(__file__).parents[1] / "contracts/data_contract_v31.json")
                                  .read_text(encoding="utf-8"))
        self._contract = contract
        self._dictionary = [field["dictionary_metadata"] for field in contract["fields"]]
        self._field_names = tuple(field["name"] for field in contract["fields"])
        self._raw_metadata: list[dict[str, Any]] | None = None

    @property
    def project_id(self) -> str:
        return self._project_id

    def _authorise(self, scope: ExportScope) -> None:
        url = urlsplit(self._api_url)
        if (url.scheme != "https" or not url.hostname or url.username or url.password
                or url.query or url.fragment):
            raise RedcapAuthorisationError("REDCap export requires a configured secure endpoint")
        if not self._token or not self._project_id:
            raise RedcapAuthorisationError("REDCap export service identity is unavailable")
        if not (1 <= self._max_attempts <= 5 and 1 <= self._timeout <= 120):
            raise RedcapClientError("REDCap transport limits are invalid")
        if self._authorisation_provider is None:
            raise RedcapAuthorisationError("REDCap project export authorisation is unavailable")
        try:
            permitted = self._authorisation_provider(scope)
        except Exception:
            raise RedcapAuthorisationError("REDCap project export authorisation failed") from None
        if permitted is not True:
            raise RedcapAuthorisationError("REDCap project export is not authorised")

    def _scope(self, operation: str, fields=(), events=(), records=()) -> ExportScope:
        return ExportScope(operation, self._project_id, self._environment, self._api_url,
                           hashlib.sha256(self._token.encode()).hexdigest(),
                           tuple(fields), tuple(events), tuple(records), not bool(records),
                           tuple(sorted(self._allowed_response_fields(fields))) if operation == "record" else ())

    def _allowed_response_fields(self, fields) -> set[str]:
        allowed = set(fields) | {"redcap_event_name", "redcap_repeat_instrument", "redcap_repeat_instance"}
        allowed.update(row["Form Name"] + "_complete" for row in self._dictionary)
        for field in self._dictionary:
            if field["Variable / Field Name"] in fields and field["Field Type"] == "checkbox":
                for choice in field["Choices, Calculations, OR Slider Labels"].split("|"):
                    code = choice.split(",", 1)[0].strip()
                    allowed.add(field["Variable / Field Name"] + "___" + code)
        return allowed

    def _post(self, payload: dict[str, Any], scope: ExportScope) -> Any:
        # Request bodies, responses and original errors are never logged.
        for attempt in range(self._max_attempts):
            self._authorise(scope)
            try:
                response = self._session.post(self._api_url, data={"token": self._token, **payload},
                                              timeout=self._timeout, allow_redirects=False, verify=True)
            except requests.exceptions.SSLError:
                raise RedcapClientError("REDCap secure connection failed") from None
            except (requests.Timeout, requests.ConnectionError):
                if attempt + 1 < self._max_attempts:
                    self._sleep(min(2 ** attempt, 8))
                    continue
                raise RedcapClientError("REDCap transport temporarily unavailable") from None
            except requests.RequestException:
                raise RedcapClientError("REDCap request failed") from None
            status = response.status_code
            if status in (401, 403):
                raise RedcapAuthorisationError("REDCap service export was denied")
            if status in TRANSIENT_STATUS and attempt + 1 < self._max_attempts:
                self._sleep(min(2 ** attempt, 8))
                continue
            if not 200 <= status < 300:
                raise RedcapClientError("REDCap export request was unsuccessful")
            try:
                return response.json()
            except (ValueError, requests.RequestException):
                raise RedcapClientError("REDCap export response is not valid JSON") from None
        raise RedcapClientError("REDCap transport limits are invalid")

    def health_check(self) -> dict[str, Any]:
        metadata = self.export_metadata()
        return {"status": "connected", "mode": "production", "field_count": len(metadata.raw["fields"])}

    def export_metadata(self) -> MetadataModel:
        raw = self._post({"content": "metadata", "format": "json", "returnFormat": "json"},
                         self._scope("metadata", self._field_names))
        rows = metadata_to_dictionary(raw)
        try:
            changed = metadata_drift(self._dictionary, rows)
        except ValueError:
            raise RedcapMetadataDrift("REDCap metadata has invalid field membership") from None
        if changed:
            raise RedcapMetadataDrift("REDCap metadata differs from the local approved contract")
        self._raw_metadata = raw
        return normalize_metadata(raw, source_mode="production")

    def export_records(self, *, fields: list[str] | None = None, events: list[str] | None = None,
                       records: list[str] | None = None,
                       date_range_begin: str | None = None) -> list[dict[str, Any]]:
        if fields is not None and (not fields or any(name not in self._field_names for name in fields)):
            raise RedcapClientError("Requested REDCap fields are outside the local contract")
        chosen_fields = list(self._field_names) if fields is None else list(dict.fromkeys(["study_id", *fields]))
        # Recheck full metadata for every retrieval; no cached names-only approval.
        self.export_metadata()
        payload: dict[str, Any] = {
            "content": "record", "format": "json", "returnFormat": "json", "type": "flat",
            "rawOrLabel": "raw", "rawOrLabelHeaders": "raw", "eventName": "unique",
        }
        for key, values in (("fields", chosen_fields), ("events", events), ("records", records)):
            if values:
                for index, value in enumerate(values):
                    payload[f"{key}[{index}]"] = value
        if date_range_begin:
            payload["dateRangeBegin"] = date_range_begin
        result = self._post(payload, self._scope("record", chosen_fields, events or (), records or ()))
        if not isinstance(result, list) or any(not isinstance(row, dict) for row in result):
            raise RedcapClientError("REDCap record response has an unsupported shape")
        allowed = self._allowed_response_fields(chosen_fields)
        for row in result:
            identifier = row.get("study_id")
            if not isinstance(identifier, str) or not identifier:
                raise RedcapClientError("REDCap record linkage is missing or unsupported")
            if records and identifier not in records:
                raise RedcapAuthorisationError("REDCap response exceeds requested record scope")
            if events and row.get("redcap_event_name") not in events:
                raise RedcapAuthorisationError("REDCap response exceeds requested event scope")
            if set(row) - allowed:
                raise RedcapAuthorisationError("REDCap response exceeds requested field scope")
        # Never fabricate an instrument or alter flat response codes/missingness,
        # primary key, event name, repeat instrument or repeat instance.
        return result

    def export_source_snapshot(self, *, date_range_begin: str | None = None) -> SourceSnapshot:
        """Full authorised source intake, independent of NDS registration/consent.

        Omit field/form/completion filters so all source responses, including
        actual additional survey-consent fields, transfer unchanged. Metadata
        drift is retained for downstream review rather than blocking receipt.
        The configured service grant must authorise the whole project export.
        """
        metadata_payload={"content":"metadata", "format":"json", "returnFormat":"json"}
        for schema_attempt in range(3):
            metadata = self._post(metadata_payload,self._scope("metadata"))
            if not isinstance(metadata, list) or not metadata:
                raise RedcapClientError("Source metadata is unavailable")
            if any(not isinstance(f,dict) or not isinstance(f.get('field_name'),str) or
                   not f['field_name'] or not isinstance(f.get('form_name'),str) for f in metadata):
                raise RedcapClientError("Source metadata shape is unsupported")
            fields = tuple(f['field_name'] for f in metadata)
            if len(set(fields)) != len(fields):
                raise RedcapClientError("Source metadata contains duplicate identifiers")
            allowed=set(fields)|{'redcap_event_name','redcap_repeat_instrument','redcap_repeat_instance',
                                'redcap_survey_identifier','redcap_data_access_group'}
            for field in metadata:
                allowed.update({field['form_name']+'_complete',field['form_name']+'_timestamp'})
                if field.get('field_type')=='checkbox':
                    choices=field.get('select_choices_or_calculations','')
                    if type(choices) is not str:
                        raise RedcapClientError("Source checkbox metadata requires review")
                    for choice in choices.split('|'):
                        allowed.add(field['field_name']+'___'+choice.split(',',1)[0].strip())
            scope=ExportScope('record',self._project_id,self._environment,self._api_url,
                              hashlib.sha256(self._token.encode()).hexdigest(),fields,(),(),True,tuple(sorted(allowed)))
            payload={'content':'record','format':'json','returnFormat':'json','type':'flat',
                     'rawOrLabel':'raw','rawOrLabelHeaders':'raw','eventName':'unique',
                     'exportSurveyFields':'true','exportDataAccessGroups':'true'}
            if date_range_begin:
                payload['dateRangeBegin']=date_range_begin
            records=self._post(payload,scope)
            if not isinstance(records,list) or any(not isinstance(row,dict) for row in records):
                raise RedcapClientError("Source records have an unsupported shape")
            # API metadata and records are separate calls. Reconcile around the
            # export to avoid associating changed choices/types with stale schema.
            after=self._post(metadata_payload,self._scope("metadata"))
            if canonical_digest(metadata)!=canonical_digest(after):
                continue
            id_field=fields[0]
            for row in records:
                if type(row.get(id_field)) is not str or not row[id_field]:
                    raise RedcapClientError("Source record identifier is missing")
                if set(row)-allowed:
                    raise RedcapAuthorisationError("Source response exceeds authorised metadata scope")
            try:
                drift=metadata_drift(self._dictionary,metadata_to_dictionary(metadata))
            except (ValueError, RedcapMetadataDrift):
                drift=[{'reason':'source_metadata_adapter_requires_review'}]
            return SourceSnapshot(records,metadata,canonical_digest(metadata),id_field,drift)
        raise RedcapClientError("Source metadata changed during export; retry collection")
