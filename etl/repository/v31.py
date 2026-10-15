"""Source-preserving, fail-closed repository over the existing SQLAlchemy stack.

No connection, schema mutation or real registry access occurs on import.
Snapshots are complete observed payloads, never patches implicitly merged with
old answers. Only the supplied trusted adapter grants current permissions.
"""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Protocol
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer, JSON, MetaData, String, Table, UniqueConstraint, select

metadata = MetaData()
raw = Table('nds_v31_source', metadata,
    Column('id', String, primary_key=True), Column('identity_key', String, nullable=False),
    Column('identity', JSON, nullable=False), Column('revision', Integer, nullable=False),
    Column('change_hash', String, nullable=False), Column('source_version', String, nullable=False),
    Column('contract_version', String, nullable=False), Column('payload', JSON, nullable=False),
    Column('country', String, nullable=False), Column('observed_at', String, nullable=False),
    Column('contract_hash', String, nullable=False), Column('storage_destination', String, nullable=False),
    Column('nds_participant_id', String),
    Column('intake_revision_id', String), Column('source_metadata_hash', String),
    Column('source_metadata', JSON),
    UniqueConstraint('identity_key', 'revision'))
validated = Table('nds_v31_validated', metadata,
    Column('source_id', String, ForeignKey(raw.c.id), primary_key=True),
    Column('values', JSON, nullable=False, quote=True), Column('issues', JSON, nullable=False))
derived = Table('nds_v31_derived', metadata,
    Column('id', String, primary_key=True), Column('source_id', String, ForeignKey(raw.c.id), nullable=False),
    Column('calculation_version', String, nullable=False), Column('result', JSON, nullable=False),
    UniqueConstraint('source_id', 'calculation_version'))
audit = Table('nds_v31_audit', metadata,
    Column('id', String, primary_key=True), Column('source_id', String, ForeignKey(raw.c.id), nullable=False),
    Column('action', String, nullable=False), Column('actor', String, nullable=False),
    Column('at', String, nullable=False))


class AccessDenied(PermissionError):
    pass


@dataclass(frozen=True)
class RecordIdentity:
    project: str
    participant: str
    event: str
    instrument: str
    instance: str

    def __post_init__(self):
        if not self.project or not self.participant:
            raise ValueError('Project and participant are required')
        if any(type(x) is not str for x in asdict(self).values()):
            raise ValueError('Identity components must be explicit strings')
        if self.instance and (not self.instance.isdigit() or int(self.instance) < 1):
            raise ValueError('Repeat instance must be positive')
        if self.instrument and not self.instance:
            raise ValueError('Repeating instrument requires instance')


@dataclass(frozen=True)
class RegistryDecision:
    """Trusted current NDS state; never construct from REDCap payload fields."""
    country: str
    processing_allowed: bool
    consent_current: bool
    nds_participant_id: str | None = None


class PolicyAdapter(Protocol):
    def resolve(self, identity: RecordIdentity) -> RegistryDecision: ...
    def permits(self, identity: RecordIdentity, action: str, actor: str, destination: str | None) -> bool: ...
    def transfer_permitted(self, identity: RecordIdentity, destination: str) -> bool: ...


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def branch_state(expression, payload):
    """Strict equality/and/or grammar; missing predicates remain unknown."""
    if not expression:
        return True
    predicates = []
    def replace(match):
        name, code = match.groups()
        val = payload.get(name)
        predicates.append(None if val in (None, '') else val == code)
        return 'p' + str(len(predicates) - 1)
    replaced = re.sub(r"\[([a-z][a-z0-9_]*)\]\s*=\s*'([^']*)'", replace, expression)
    try:
        tree = ast.parse(replaced, mode='eval')
        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Name) and re.fullmatch(r'p\d+', node.id):
                return predicates[int(node.id[1:])]
            if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
                vals = [evaluate(n) for n in node.values]
                if isinstance(node.op, ast.And):
                    return False if False in vals else None if None in vals else True
                return True if True in vals else None if None in vals else False
            raise ValueError('Unsupported branching')
        return evaluate(tree)
    except (SyntaxError, ValueError, IndexError):
        return None


class Repository:
    def __init__(self, engine, adapter: PolicyAdapter | None = None, *, storage_destination: str | None = None):
        self.engine, self.adapter = engine, adapter
        self.storage_destination = storage_destination
        self.contract = json.loads((Path(__file__).parents[1] / 'contracts/data_contract_v31.json').read_text())
        self.fields = {f['name']: f['dictionary_metadata'] for f in self.contract['fields']}
        self.contract_hash = digest(self.contract)
        self.source_only = {f['name'] for f in self.contract['fields']
                            if not f['respondent_question'] and f['name'] != 'attack_freq_missing'}
        country_choices = self.fields['country']['Choices, Calculations, OR Slider Labels']
        self.countries = dict(part.strip().split(', ', 1) for part in country_choices.split('|'))

    def _authorise(self, identity, action, actor, destination=None):
        if self.adapter is None or not actor:
            raise AccessDenied('Trusted policy adapter and actor required')
        try:
            state = self.adapter.resolve(identity)
            grant = self.adapter.permits(identity, action, actor, destination)
            transfer = self.adapter.transfer_permitted(identity, destination) if destination is not None else True
        except Exception:
            raise AccessDenied('Trusted policy decision unavailable') from None
        if (not isinstance(state, RegistryDecision) or state.processing_allowed is not True or state.consent_current is not True
                or state.country not in self.countries.values()
                or grant is not True):
            raise AccessDenied('Current registry consent and action permission required')
        if transfer is not True:
            raise AccessDenied('Current destination transfer permission required')
        return state

    def _validate(self, payload, source_fields=None):
        values, issues = {}, {}
        fields = self.fields if source_fields is None else source_fields
        for name, value in payload.items():
            field = fields.get(name)
            if field is None:
                issues[name] = 'unknown_field'
                continue
            if name in self.source_only:
                issues[name] = 'source_only_administrative_or_derived'
                continue
            if value in (None, ''):
                values[name] = value
                continue
            branch = branch_state(field['Branching Logic (Show field only if...)'], payload)
            if branch is not True:
                issues[name] = 'inapplicable' if branch is False else 'branch_unverified'
                continue
            kind = field['Field Type']
            choices = {p.strip().split(',', 1)[0] for p in field['Choices, Calculations, OR Slider Labels'].split('|')}
            if kind in ('radio', 'dropdown') and (type(value) is not str or value not in choices):
                issues[name] = 'invalid_code'
            elif kind == 'checkbox' and (type(value) is not dict or set(value) - choices
                    or any(type(v) is not str or v not in ('0', '1', '') for v in value.values())):
                issues[name] = 'invalid_checkbox'
            elif kind not in ('radio', 'dropdown', 'checkbox'):
                validation = field['Text Validation Type OR Show Slider Number']
                if kind != 'text' or validation not in ('', 'integer'):
                    issues[name] = 'validator_unverified'
                elif type(value) is not str:
                    issues[name] = 'invalid_text'
                elif validation == 'integer':
                    if not re.fullmatch(r'[+-]?\d+', value):
                        issues[name] = 'invalid_integer'
                    else:
                        number = int(value)
                        minimum, maximum = field['Text Validation Min'], field['Text Validation Max']
                        if ((minimum and number < int(minimum)) or
                                (maximum and number > int(maximum))):
                            issues[name] = 'outside_dictionary_range'
                        else:
                            values[name] = value
                else:
                    values[name] = value
            else:
                values[name] = value
        return values, issues

    def ingest(self, identity, payload, source_version, actor='sync', *, nds_participant_id=None, source_metadata=None, intake_revision_id=None):
        if type(self.storage_destination) is not str or not self.storage_destination:
            raise AccessDenied('Explicit approved storage destination required')
        state = self._authorise(identity, 'ingest', actor, self.storage_destination)
        if nds_participant_id is not None and (
                type(nds_participant_id) is not str or not nds_participant_id or
                state.nds_participant_id != nds_participant_id):
            raise AccessDenied('Mapped NDS identity differs from current registration')
        if intake_revision_id is not None and (type(intake_revision_id) is not str or not intake_revision_id):
            raise ValueError('Explicit source intake revision required')
        if not isinstance(payload, dict) or not source_version or type(source_version) is not str:
            raise ValueError('Observed payload and source version required')
        canonical(payload)  # Reject non-JSON/NaN before any write.
        for field, component in [('redcap_event_name', identity.event),
                                 ('redcap_repeat_instrument', identity.instrument),
                                 ('redcap_repeat_instance', identity.instance)]:
            if field in payload and payload[field] != component:
                raise AccessDenied('Source event/repeat linkage differs from trusted identity')
        if payload.get('study_id') != identity.participant:
            raise AccessDenied('Source linkage differs from trusted identity')
        # Repeat/event exports may omit the non-repeating country field. The
        # trusted NDS registry supplies processing scope, never a filled answer.
        if payload.get('country') not in (None, '') and self.countries.get(payload['country']) != state.country:
            raise AccessDenied('Source country differs from trusted registry')
        key = digest(asdict(identity))
        change = digest({'payload': payload, 'source_version': source_version, 'source_metadata': source_metadata,
                         'intake_revision_id': intake_revision_id,
                         'nds_participant_id': nds_participant_id,
                         'contract_version': self.contract['contract_version'], 'contract_hash': self.contract_hash})
        source_fields = None if source_metadata is None else {f['Variable / Field Name']:f for f in source_metadata}
        values, issues = self._validate(payload, source_fields)
        with self.engine.begin() as conn:
            previous = conn.execute(select(raw).where(raw.c.identity_key == key)
                                    .order_by(raw.c.revision.desc()).limit(1)).mappings().first()
            if previous and previous['change_hash'] == change:
                self._audit(conn, previous['id'], 'replay', actor)
                return previous['id']
            sid = str(uuid4())
            conn.execute(raw.insert().values(id=sid, identity_key=key, identity=asdict(identity),
                revision=previous['revision'] + 1 if previous else 1, change_hash=change,
                source_version=source_version, contract_version=self.contract['contract_version'],
                payload=payload, country=state.country, observed_at=datetime.now(timezone.utc).isoformat(),
                contract_hash=self.contract_hash, storage_destination=self.storage_destination, nds_participant_id=nds_participant_id,
                intake_revision_id=intake_revision_id, source_metadata=source_metadata,
                source_metadata_hash=None if source_metadata is None else digest(source_metadata)))
            conn.execute(validated.insert().values(source_id=sid, values=values, issues=issues))
            self._audit(conn, sid, 'ingest', actor)
            return sid

    @staticmethod
    def _audit(conn, sid, action, actor):
        conn.execute(audit.insert().values(id=str(uuid4()), source_id=sid, action=action, actor=actor, at=datetime.now(timezone.utc).isoformat()))

    @staticmethod
    def _check_registration(row, state):
        if row['country'] != state.country or (
                row['nds_participant_id'] is not None and row['nds_participant_id'] != state.nds_participant_id):
            raise AccessDenied('Stored scope differs from current NDS registration')

    def export(self, identity, actor, destination):
        if type(destination) is not str or not destination:
            raise AccessDenied('Explicit approved destination required')
        state = self._authorise(identity, 'export', actor, destination)
        with self.engine.begin() as conn:
            row = conn.execute(select(raw).where(raw.c.identity_key == digest(asdict(identity)))
                               .order_by(raw.c.revision.desc()).limit(1)).mappings().first()
            if row is None:
                return None
            self._check_registration(row, state)
            self._audit(conn, row['id'], 'export', actor)
            return json.loads(canonical(dict(row)))

    def store_derived(self, source_id, calculation_version, result, actor='scoring'):
        if not calculation_version:
            raise ValueError('Calculation version required')
        canonical(result)
        with self.engine.begin() as conn:
            row = conn.execute(select(raw).where(raw.c.id == source_id)).mappings().one()
            identity = RecordIdentity(**row['identity'])
            if type(self.storage_destination) is not str or not self.storage_destination:
                raise AccessDenied('Explicit approved storage destination required')
            state = self._authorise(identity, 'derive', actor, self.storage_destination)
            self._check_registration(row, state)
            latest = conn.execute(select(raw.c.id).where(raw.c.identity_key == row['identity_key'])
                                  .order_by(raw.c.revision.desc()).limit(1)).scalar_one()
            if latest != source_id:
                raise ValueError('Stale source revision')
            existing = conn.execute(select(derived).where(derived.c.source_id == source_id,
                    derived.c.calculation_version == calculation_version)).mappings().first()
            if existing:
                if existing['result'] != result:
                    raise ValueError('Immutable calculation version has different result')
                return existing['id']
            did = str(uuid4())
            conn.execute(derived.insert().values(id=did, source_id=source_id,
                         calculation_version=calculation_version, result=result))
            self._audit(conn, source_id, 'derive', actor)
            return did

    def review(self, identity, actor, destination):
        """Return completion counts only after current scoped permission checks."""
        if type(destination) is not str or not destination:
            raise AccessDenied('Explicit approved destination required')
        state = self._authorise(identity, 'review', actor, destination)
        with self.engine.begin() as conn:
            row = conn.execute(select(raw).where(raw.c.identity_key == digest(asdict(identity)))
                               .order_by(raw.c.revision.desc()).limit(1)).mappings().first()
            if row is None:
                return None
            self._check_registration(row, state)
            layer = conn.execute(select(validated).where(validated.c.source_id == row['id'])).mappings().one()
            from etl.analytics.v31_review import completion
            summary = completion(self.contract, row['payload'], layer['values'], layer['issues'])
            summary.update(source_version=row['source_version'], source_sha256=row['change_hash'], revision=row['revision'])
            self._audit(conn, row['id'], 'review', actor)
            return summary
