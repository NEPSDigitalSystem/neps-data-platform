"""Synthetic native-API transport tests; no remote service or approval exercised."""
import copy
import io
import json
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from contextlib import redirect_stdout, redirect_stderr

import requests

from etl.contracts.v31 import DICTIONARY_HEADERS
from etl.extract.production_client import (
    API_METADATA_KEYS, ProductionRedcapClient, RedcapAuthorisationError,
    RedcapClientError, RedcapMetadataDrift,
)

CONTRACT = json.loads((Path(__file__).parents[1] / "etl/contracts/data_contract_v31.json").read_text())


def native_metadata():
    # Independent mapping based on native API keys, preserving all actual values.
    return [{key: field["dictionary_metadata"][header]
             for header, key in zip(DICTIONARY_HEADERS, API_METADATA_KEYS)}
            for field in CONTRACT["fields"]]


def settings(**overrides):
    values = dict(redcap_api_url="https://synthetic.invalid/api/", redcap_api_token="SYNTHETIC-TOKEN",
                  redcap_project_id="SYNTHETIC-PROJECT", app_env="staging",
                  http_timeout_seconds=5, http_max_retries=3)
    values.update(overrides)
    return SimpleNamespace(**values)


class Response:
    def __init__(self, value, status=200):
        self.status_code = status
        self.value = value

    def json(self):
        if isinstance(self.value, Exception):
            raise self.value
        return self.value


class Session:
    def __init__(self, *results):
        self.results = list(results)
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class NativeConnectorTests(unittest.TestCase):
    def client(self, session, provider=lambda scope: True, **kwargs):
        return ProductionRedcapClient(settings(**kwargs), session=session,
                                      authorisation_provider=provider, sleep=lambda _: None)

    def test_default_denies_before_any_http_including_health(self):
        for method in ["health_check", "export_metadata", "export_records"]:
            with self.subTest(method=method):
                session = Session()
                client = self.client(session, provider=None)
                with self.assertRaises(RedcapAuthorisationError):
                    getattr(client, method)()
                self.assertEqual(session.calls, [])

    def test_provider_must_explicitly_validate_project_scope_identity(self):
        scopes = []
        def approved_synthetic(scope):
            scopes.append(scope)
            return scope.operation == "metadata"
        session = Session(Response(native_metadata()))
        with self.assertRaises(RedcapAuthorisationError):
            self.client(session, provider=approved_synthetic).export_records()
        self.assertEqual(len(session.calls), 1)
        scope = scopes[-1]
        self.assertEqual(scope.project_id, "SYNTHETIC-PROJECT")
        self.assertEqual(scope.environment, "staging")
        self.assertEqual(len(scope.service_identity_fingerprint), 64)
        self.assertNotIn("SYNTHETIC-TOKEN", repr(scope))
        self.assertTrue(scope.full_project_records)
        self.assertTrue(set(CONTRACT["question_fields"]).issubset(scope.fields))
        for result in [False, None, "approved", 1]:
            with self.subTest(result=result):
                session = Session()
                with self.assertRaises(RedcapAuthorisationError):
                    self.client(session, provider=lambda _: result).export_metadata()
                self.assertEqual(session.calls, [])

    def test_https_and_identity_mandatory_and_no_redirect(self):
        for url in ["http://synthetic.invalid/api", "https://user:secret@synthetic.invalid/api",
                    "https://synthetic.invalid/api?token=secret", "https://synthetic.invalid/api#secret"]:
            with self.subTest(url=url):
                session = Session()
                with self.assertRaises(RedcapAuthorisationError):
                    self.client(session, redcap_api_url=url).export_metadata()
                self.assertEqual(session.calls, [])
        session = Session(Response(native_metadata(), 302))
        with self.assertRaises(RedcapClientError):
            self.client(session).export_metadata()
        self.assertEqual(len(session.calls), 1)
        self.assertIs(session.calls[0][1]["allow_redirects"], False)
        self.assertIs(session.calls[0][1]["verify"], True)
        session = Session()
        with self.assertRaises(RedcapAuthorisationError):
            self.client(session, redcap_api_token="").export_metadata()
        self.assertEqual(session.calls, [])

    def test_native_payload_188_and_full_partial_records_are_untouched(self):
        for count in [73, 100, 188]:
            with self.subTest(count=count):
                raw = {name: "" if i % 3 == 0 else "99" if i % 3 == 1 else "0"
                       for i, name in enumerate(CONTRACT["question_fields"][:count])}
                raw.update(study_id="SYNTHETIC-001", redcap_event_name="synthetic_event_arm_1",
                           redcap_repeat_instrument="neps31_screening", redcap_repeat_instance="2",
                           attack_freq_missing="98")
                original = copy.deepcopy(raw)
                session = Session(Response(native_metadata()), Response([raw]))
                result = self.client(session).export_records(events=["synthetic_event_arm_1"],
                                                             records=["SYNTHETIC-001"])
                self.assertEqual(result, [original])
                self.assertEqual(raw, original)
                self.assertNotIn("_instrument", result[0])
                metadata_payload = session.calls[0][1]["data"]
                self.assertEqual(metadata_payload["content"], "metadata")
                payload = session.calls[1][1]["data"]
                self.assertEqual(payload["content"], "record")
                self.assertEqual(payload["type"], "flat")
                self.assertEqual(payload["rawOrLabel"], "raw")
                self.assertEqual(payload["rawOrLabelHeaders"], "raw")
                self.assertEqual(payload["eventName"], "unique")
                requested = {v for k, v in payload.items() if k.startswith("fields[")}
                self.assertTrue(set(CONTRACT["question_fields"]).issubset(requested))
                self.assertEqual(len(requested), 223)
                self.assertEqual(payload["events[0]"], "synthetic_event_arm_1")
                self.assertEqual(payload["records[0]"], "SYNTHETIC-001")

    def test_requested_subset_retains_registry_id_and_native_indexing(self):
        scopes = []
        session = Session(Response(native_metadata()), Response([]))
        self.client(session, provider=lambda scope: scopes.append(scope) or True).export_records(
            fields=["k6_1"], events=["synthetic_arm_1"], records=["SYNTHETIC-002"],
            date_range_begin="2026-01-01 00:00:00")
        payload = session.calls[1][1]["data"]
        self.assertEqual(payload["fields[0]"], "study_id")
        self.assertEqual(payload["fields[1]"], "k6_1")
        self.assertEqual(payload["dateRangeBegin"], "2026-01-01 00:00:00")
        self.assertFalse(scopes[-1].full_project_records)
        self.assertEqual(scopes[-1].records, ("SYNTHETIC-002",))

    def test_exact_all_column_schema_drift_prevents_record_retrieval(self):
        for key in API_METADATA_KEYS:
            with self.subTest(key=key):
                raw = native_metadata()
                raw[0][key] += "SYNTHETIC-DRIFT"
                session = Session(Response(raw))
                with self.assertRaises(RedcapMetadataDrift):
                    self.client(session).export_records()
                self.assertEqual(len(session.calls), 1)
        for change in ["reorder", "missing_column", "extra_column", "duplicate", "removed"]:
            with self.subTest(change=change):
                raw = native_metadata()
                if change == "reorder": raw[0], raw[1] = raw[1], raw[0]
                elif change == "missing_column": del raw[0]["field_annotation"]
                elif change == "extra_column": raw[0]["unknown_schema"] = ""
                elif change == "duplicate": raw.append(raw[0])
                else: raw.pop()
                session = Session(Response(raw))
                with self.assertRaises(RedcapMetadataDrift):
                    self.client(session).export_records()
                self.assertEqual(len(session.calls), 1)

    def test_raw_metadata_remains_complete(self):
        raw = native_metadata()
        model = self.client(Session(Response(raw))).export_metadata()
        self.assertEqual(model.raw["fields"], raw)
        self.assertEqual(len(model.raw["fields"]), 223)
        self.assertTrue(all(len(row) == 18 for row in model.raw["fields"]))

    def test_retry_only_transient_and_bounded(self):
        for failure in [Response({}, 429), Response({}, 502), Response({}, 503), Response({}, 504),
                        requests.Timeout("SYNTHETIC-TOKEN"), requests.ConnectionError("SYNTHETIC-TOKEN")]:
            with self.subTest(failure=type(failure).__name__):
                session = Session(failure, Response(native_metadata()))
                self.client(session).export_metadata()
                self.assertEqual(len(session.calls), 2)
        session = Session(*(Response({}, 503) for _ in range(3)))
        with self.assertRaises(RedcapClientError):
            self.client(session).export_metadata()
        self.assertEqual(len(session.calls), 3)
        for failure in [Response({}, 403), Response({}, 401), Response({}, 400), Response({}, 500),
                        requests.exceptions.SSLError("SYNTHETIC-TOKEN"),
                        requests.RequestException("SYNTHETIC-TOKEN")]:
            with self.subTest(failure=type(failure).__name__):
                session = Session(failure)
                with self.assertRaises(RedcapClientError):
                    self.client(session).export_metadata()
                self.assertEqual(len(session.calls), 1)

    def test_policy_rechecked_before_retry_and_metadata_not_cached(self):
        decisions = iter([True, False])
        session = Session(Response({}, 503))
        with self.assertRaises(RedcapAuthorisationError):
            self.client(session, provider=lambda _: next(decisions)).export_metadata()
        self.assertEqual(len(session.calls), 1)
        drift = native_metadata()
        drift[0]["field_note"] = "SYNTHETIC-CHANGE"
        session = Session(Response(native_metadata()), Response([]), Response(drift))
        client = self.client(session)
        client.export_records()
        with self.assertRaises(RedcapMetadataDrift): client.export_records()
        self.assertEqual(len(session.calls), 3)

    def test_no_error_body_url_token_or_participant_logging(self):
        marker = "SYNTHETIC-SECRET-BODY-RECORD"
        for failure in [requests.Timeout(marker), Response(ValueError(marker)), Response({"error": marker}, 403)]:
            session = Session(failure)
            output, errors = io.StringIO(), io.StringIO()
            stream = io.StringIO()
            handler = logging.StreamHandler(stream)
            logging.getLogger().addHandler(handler)
            try:
                with redirect_stdout(output), redirect_stderr(errors), self.assertRaises(RedcapClientError) as caught:
                    self.client(session, http_max_retries=1).export_metadata()
                text = str(caught.exception) + output.getvalue() + errors.getvalue() + stream.getvalue()
                for secret in [marker, "SYNTHETIC-TOKEN", "https://synthetic.invalid"]:
                    self.assertNotIn(secret, text)
            finally:
                logging.getLogger().removeHandler(handler)

    def test_unknown_fields_fail_before_http(self):
        session = Session()
        with self.assertRaises(RedcapClientError):
            self.client(session).export_records(fields=["invented"])
        self.assertEqual(session.calls, [])


if __name__ == "__main__":
    unittest.main()
