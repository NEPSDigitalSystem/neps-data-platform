"""Durable REDCap source receipt and pending processing over existing SQLAlchemy.

No registry, NDS registration, NDS consent or score dependency is imported.
Schema creation and live activation are caller-controlled, never import effects.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import time
from typing import Protocol
from uuid import uuid4

from sqlalchemy import (Column, Float, ForeignKey, Integer, JSON, MetaData, String, func,
                        Table, UniqueConstraint, and_, insert, or_, select, update)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index
from etl.load.locking import lock_identity


metadata = MetaData()
raw = Table("nds_v31_intake_raw", metadata,
    Column("id", String, primary_key=True), Column("project", String, nullable=False),
    Column("identity_key", String, nullable=False), Column("identity", JSON, nullable=False),
    Column("revision", Integer, nullable=False), Column("payload", JSON, nullable=False),
    Column("payload_hash", String, nullable=False), Column("source_version", String, nullable=False),
    Column("record_id_field", String, nullable=False), Column("metadata_snapshot", JSON),
    Column("metadata_hash", String),
    Column("contract_hash", String, nullable=False), Column("received_at", Float, nullable=False),
    Column("destination", String, nullable=False), UniqueConstraint("identity_key", "revision"))
head = Table("nds_v31_intake_head", metadata,
    Column("identity_key", String, primary_key=True), Column("revision", Integer, nullable=False),
    Column("source_revision_id", String, ForeignKey(raw.c.id), nullable=False))
pending = Table("nds_v31_intake_pending", metadata,
    Column("source_revision_id", String, ForeignKey(raw.c.id), primary_key=True),
    Column("state", String, nullable=False), Column("attempts", Integer, nullable=False),
    Column("failure_code", String), Column("next_attempt_at", Float, nullable=False),
    Column("claim_token", String), Column("claim_actor", String), Column("lease_until", Float))
audit = Table("nds_v31_intake_audit", metadata,
    Column("id", String, primary_key=True), Column("source_revision_id", String, ForeignKey(raw.c.id), nullable=False),
    Column("action", String, nullable=False), Column("actor", String, nullable=False), Column("at", Float, nullable=False))

# Post-004 integrity. Frozen migration 002 remains unchanged.
raw.append_constraint(UniqueConstraint("identity_key", "revision", "id", name="uq_intake_head_target"))
head.append_constraint(ForeignKeyConstraint(
    ["identity_key", "revision", "source_revision_id"],
    [raw.c.identity_key, raw.c.revision, raw.c.id], name="fk_intake_head_revision"))
for table in (raw, head):
    table.append_constraint(CheckConstraint("revision > 0", name=f"ck_{table.name}_revision"))
raw.append_constraint(CheckConstraint(
    "(identity->>'project') IS NOT DISTINCT FROM project", name="ck_intake_project").ddl_if(dialect="postgresql"))
pending.append_constraint(CheckConstraint(
    "state IN ('pending', 'retry', 'processing', 'acknowledged')", name="ck_pending_state"))
pending.append_constraint(CheckConstraint("attempts >= 0", name="ck_pending_attempts"))
pending.append_constraint(CheckConstraint(
    "state NOT IN ('processing', 'acknowledged') OR "
    "(claim_token IS NOT NULL AND claim_actor IS NOT NULL AND lease_until IS NOT NULL)", name="ck_pending_claim"))
Index("ix_pending_ready", pending.c.state, pending.c.next_attempt_at, pending.c.lease_until)
Index("ix_intake_scope", raw.c.project, raw.c.destination, raw.c.received_at, raw.c.revision)

FAILURE_CODES = frozenset({"nds_unavailable", "mapping_pending", "processing_restricted",
                           "destination_unavailable", "transient_failure", "internal_failure"})


class IntakeDenied(PermissionError):
    pass


class IntakeUnavailable(RuntimeError):
    pass


class QueueConflict(RuntimeError):
    pass


@dataclass(frozen=True)
class RecordIdentity:
    """REDCap source namespace, explicitly independent of any NDS ID."""
    project: str
    source_id: str
    event: str = ""
    instrument: str = ""
    instance: str = ""

    def __post_init__(self):
        if any(type(value) is not str for value in asdict(self).values()) or not self.project or not self.source_id:
            raise ValueError("Explicit REDCap project and source record identity required")
        if self.instance and (not self.instance.isdigit() or int(self.instance) < 1):
            raise ValueError("Source repeat instance must be positive")
        if self.instrument and not self.instance:
            raise ValueError("Source repeating instrument requires instance")


@dataclass(frozen=True)
class ServiceScope:
    action: str
    project: str
    destination: str
    service_identity: str
    actor: str


class IntakePolicy(Protocol):
    """Authenticate service and actual project/destination permissions only.

    The adapter must verify current applicable source export/storage boundaries.
    An NDS registry lookup or NDS downstream consent is not an intake gate.
    This module supplies no production adapter and assumes no legal approval.
    """
    def authorises(self, scope: ServiceScope) -> bool: ...


@dataclass(frozen=True)
class Claim:
    source_revision_id: str
    claim_token: str
    identity: RecordIdentity
    payload: dict
    source_version: str
    attempts: int
    record_id_field: str
    metadata_snapshot: object
    metadata_hash: str | None
    contract_hash: str


def canonical(value):
    """Strict JSON-semantic copy; reject implicit string-key conversions/NaN."""
    def check(item):
        if isinstance(item, dict):
            if any(type(key) is not str for key in item):
                raise ValueError("Source JSON object keys must be strings")
            for child in item.values(): check(child)
        elif isinstance(item, list):
            for child in item: check(child)
        elif item is not None and type(item) not in (str, bool, int, float):
            raise ValueError("Source payload must contain native JSON values")
    check(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


class Intake:
    def __init__(self, engine, *, project=None, destination=None, service_identity=None,
                 policy: IntakePolicy | None = None, clock=time.time):
        self.engine, self.project, self.destination = engine, project, destination
        self.service_identity, self.policy, self.clock = service_identity, policy, clock
        contract = json.loads((Path(__file__).parents[1] / "contracts/data_contract_v31.json").read_text())
        self.contract_hash = digest(contract)
        self.record_id_field = contract["fields"][0]["name"]

    def _permit(self, action, actor, project=None):
        # Credentials are configured externally; never read them from payload.
        if (any(type(value) is not str or not value for value in
                (self.project, self.destination, self.service_identity, actor))
                or self.policy is None or self.engine.echo
                or (project is not None and project != self.project)):
            raise IntakeDenied("Configured source service and destination policy required")
        try:
            permitted = self.policy.authorises(ServiceScope(action, self.project, self.destination,
                                                            self.service_identity, actor))
        except Exception:
            raise IntakeDenied("Source service policy unavailable") from None
        if permitted is not True:
            raise IntakeDenied("Source service action is not authorised")

    def _audit(self, connection, sid, action, actor):
        connection.execute(insert(audit).values(id=str(uuid4()), source_revision_id=sid,
                                               action=action, actor=actor, at=self.clock()))

    def receive(self, identity: RecordIdentity, payload, source_version, actor, *,
                record_id_field=None, metadata_snapshot=None):
        if not isinstance(identity, RecordIdentity):
            raise ValueError("Explicit source RecordIdentity required")
        self._permit("receive", actor, identity.project)
        if type(payload) is not dict or type(source_version) is not str or not source_version:
            raise ValueError("Observed source JSON and explicit version required")
        copied = json.loads(canonical(payload))
        source_key = self.record_id_field if record_id_field is None else record_id_field
        if type(source_key) is not str or not source_key:
            raise ValueError("Explicit source record ID field required")
        if type(copied.get(source_key)) is not str or copied[source_key] != identity.source_id:
            raise ValueError("Source record ID must be present as its native string value")
        actual_metadata = None if metadata_snapshot is None else json.loads(canonical(metadata_snapshot))
        actual_metadata_hash = None if actual_metadata is None else digest(actual_metadata)
        for name, expected in ((source_key, identity.source_id),
                               ("redcap_event_name", identity.event),
                               ("redcap_repeat_instrument", identity.instrument),
                               ("redcap_repeat_instance", identity.instance)):
            if name in copied and str(copied[name]) != expected:
                raise ValueError("Source envelope identity disagrees with exported payload")
        key = digest({"source_identity": asdict(identity), "destination": self.destination})
        change_hash = digest({"payload": copied, "source_version": source_version,
                              "contract_hash": self.contract_hash, "record_id_field": source_key,
                              "metadata_hash": actual_metadata_hash})
        # Compare-and-swap head serialises same-identity amendments, including
        # concurrent unchanged retries. Every raw+queue+audit write is atomic.
        for attempt in range(3):
            try:
                with self.engine.begin() as connection:
                    lock_identity(connection, "source-receipt", key)
                    current = connection.execute(select(head).where(head.c.identity_key == key)).mappings().first()
                    revision = 1 if current is None else current["revision"] + 1
                    if current:
                        previous = connection.execute(select(raw).where(raw.c.id == current["source_revision_id"])).mappings().one()
                        if previous["destination"] != self.destination or previous["project"] != self.project:
                            raise IntakeDenied("Source receipt namespace differs from authorised destination")
                        if previous["payload_hash"] == change_hash:
                            return previous["id"]
                    sid = str(uuid4())
                    connection.execute(insert(raw).values(id=sid, project=identity.project,
                        identity_key=key, identity=asdict(identity), revision=revision,
                        payload=copied, payload_hash=change_hash, source_version=source_version,
                        record_id_field=source_key, metadata_snapshot=actual_metadata,
                        metadata_hash=actual_metadata_hash,
                        contract_hash=self.contract_hash, received_at=self.clock(), destination=self.destination))
                    if current is None:
                        connection.execute(insert(head).values(identity_key=key, revision=revision, source_revision_id=sid))
                    else:
                        result = connection.execute(update(head).where(and_(head.c.identity_key == key,
                            head.c.revision == current["revision"])).values(revision=revision, source_revision_id=sid))
                        if result.rowcount != 1:
                            raise QueueConflict("Concurrent source revision; retry")
                    connection.execute(insert(pending).values(source_revision_id=sid, state="pending",
                        attempts=0, next_attempt_at=self.clock()))
                    self._audit(connection, sid, "received", actor)
                    return sid
            except (IntegrityError, QueueConflict):
                if attempt == 2:
                    raise IntakeUnavailable("Source receipt contention; retry safely") from None
            except SQLAlchemyError:
                raise IntakeUnavailable("Source receipt store unavailable; retry safely") from None

    def pending_rows(self, actor):
        self._permit("pending", actor)
        try:
            with self.engine.connect() as connection:
                rows = connection.execute(select(pending).join(raw, raw.c.id == pending.c.source_revision_id)
                    .where(and_(raw.c.project == self.project, raw.c.destination == self.destination))
                    .order_by(raw.c.received_at, raw.c.revision)).mappings().all()
                return [dict(row) for row in rows]
        except SQLAlchemyError:
            raise IntakeUnavailable("Source pending store unavailable") from None

    def claim(self, actor, *, lease_seconds=60):
        self._permit("claim", actor)
        if type(lease_seconds) is not int or not 1 <= lease_seconds <= 3600:
            raise ValueError("Bounded processing lease required")
        now = self.clock()
        eligible = or_(and_(pending.c.state.in_(["pending", "retry"]), pending.c.next_attempt_at <= now),
                       and_(pending.c.state == "processing", pending.c.lease_until <= now))
        try:
            with self.engine.begin() as connection:
                row = connection.execute(select(raw, pending.c.attempts).join(pending, raw.c.id == pending.c.source_revision_id)
                    .where(and_(raw.c.project == self.project, raw.c.destination == self.destination, eligible))
                    .order_by(raw.c.received_at, raw.c.revision).limit(1)
                    .with_for_update(of=pending, skip_locked=True)).mappings().first()
                if row is None: return None
                token = str(uuid4())
                result = connection.execute(update(pending).where(and_(pending.c.source_revision_id == row["id"], eligible))
                    .values(state="processing", claim_token=token, claim_actor=actor,
                            lease_until=now + lease_seconds, attempts=pending.c.attempts + 1))
                if result.rowcount != 1: return None
                self._audit(connection, row["id"], "claimed", actor)
                return Claim(row["id"], token, RecordIdentity(**row["identity"]), row["payload"],
                             row["source_version"], row["attempts"] + 1, row["record_id_field"],
                             row["metadata_snapshot"], row["metadata_hash"], row["contract_hash"])
        except SQLAlchemyError:
            raise IntakeUnavailable("Source pending claim unavailable") from None

    def _finish(self, sid, token, actor, action, failure_code=None, retry_delay=0):
        self._permit(action, actor)
        try:
            with self.engine.begin() as connection:
                row = connection.execute(select(pending, raw.c.project, raw.c.destination).join(raw, raw.c.id == pending.c.source_revision_id)
                    .where(pending.c.source_revision_id == sid)).mappings().first()
                if row is None or row["project"] != self.project or row["destination"] != self.destination:
                    raise QueueConflict("Source processing claim unavailable")
                if row["claim_token"] != token or row["claim_actor"] != actor:
                    raise QueueConflict("Source processing claim no longer current")
                if action == "ack" and row["state"] == "acknowledged": return True
                if row["state"] != "processing" or row["lease_until"] <= self.clock():
                    raise QueueConflict("Source processing lease no longer current")
                values = {"state": "acknowledged"} if action == "ack" else {
                    "state": "retry", "failure_code": failure_code, "next_attempt_at": self.clock() + retry_delay,
                    "claim_token": None, "claim_actor": None, "lease_until": None}
                result = connection.execute(update(pending).where(and_(pending.c.source_revision_id == sid,
                    pending.c.state == "processing", pending.c.claim_token == token,
                    pending.c.claim_actor == actor, pending.c.lease_until > self.clock())).values(**values))
                if result.rowcount != 1: raise QueueConflict("Source processing claim no longer current")
                self._audit(connection, sid, action, actor)
                return True
        except SQLAlchemyError:
            raise IntakeUnavailable("Source pending transition unavailable") from None

    def fail(self, source_revision_id, claim_token, actor, failure_code, *, retry_delay=0):
        if failure_code not in FAILURE_CODES:
            raise ValueError("Only sanitised source processing failure codes are permitted")
        if type(retry_delay) is not int or not 0 <= retry_delay <= 86400:
            raise ValueError("Bounded retry delay required")
        return self._finish(source_revision_id, claim_token, actor, "fail", failure_code, retry_delay)

    def ack(self, source_revision_id, claim_token, actor):
        return self._finish(source_revision_id, claim_token, actor, "ack")

    def requeue(self, source_revision_id, actor):
        """Explicit policy-approved reprocessing without altering source history.

        Repeated calls while already pending are idempotent. No active worker's
        lease can be stolen; a completed, retrying or expired claim may reset.
        Mapping/calculation policy decisions remain with the trusted provider.
        """
        self._permit("requeue", actor)
        now = self.clock()
        try:
            with self.engine.begin() as connection:
                row = connection.execute(select(pending, raw.c.project, raw.c.destination)
                    .join(raw, raw.c.id == pending.c.source_revision_id)
                    .where(pending.c.source_revision_id == source_revision_id)).mappings().first()
                if row is None or row["project"] != self.project or row["destination"] != self.destination:
                    raise QueueConflict("Source reprocessing revision unavailable")
                if row["state"] == "pending":
                    return True
                if row["state"] == "processing" and row["lease_until"] > now:
                    raise QueueConflict("Source processing lease is still active")
                permitted_state = or_(pending.c.state.in_(["acknowledged", "retry"]),
                                      and_(pending.c.state == "processing", pending.c.lease_until <= now))
                result = connection.execute(update(pending).where(and_(
                    pending.c.source_revision_id == source_revision_id, permitted_state))
                    .values(state="pending", failure_code=None, next_attempt_at=now,
                            claim_token=None, claim_actor=None, lease_until=None))
                if result.rowcount != 1:
                    raise QueueConflict("Source reprocessing state changed; retry safely")
                self._audit(connection, source_revision_id, "requeued", actor)
                return True
        except SQLAlchemyError:
            raise IntakeUnavailable("Source reprocessing transition unavailable") from None

    def reconcile(self, observed_identities, actor, *, full_export_succeeded=False):
        """Audit current credential visibility after a complete successful export.

        No source payload is changed or deleted, and absence never implies
        withdrawal/deletion. Only another successful full export clears markers.
        The collector must finish every raw receipt before invoking this method.
        """
        self._permit("reconcile", actor)
        if full_export_succeeded is not True:
            raise ValueError("Successful complete source export must be explicitly confirmed")
        observed = set()
        for identity in observed_identities:
            if not isinstance(identity, RecordIdentity) or identity.project != self.project:
                raise IntakeDenied("Full source reconciliation identity scope differs")
            observed.add(digest({"source_identity": asdict(identity), "destination": self.destination}))
        actions = ("not_seen_in_full_export", "seen_in_full_export")
        for attempt in range(3):
            try:
                with self.engine.begin() as connection:
                    latest = connection.execute(select(raw.c.id, raw.c.identity_key)
                        .join(head, head.c.source_revision_id == raw.c.id)
                        .where(and_(raw.c.project == self.project, raw.c.destination == self.destination))).mappings().all()
                    if observed - {row["identity_key"] for row in latest}:
                        raise ValueError("Full source receipts must complete before reconciliation")
                    counts = {"present": 0, "not_seen": 0, "newly_not_seen": 0, "restored": 0}
                    for row in latest:
                        markers = dict(connection.execute(select(audit.c.action, func.count())
                            .join(raw, raw.c.id == audit.c.source_revision_id)
                            .where(and_(raw.c.identity_key == row["identity_key"], audit.c.action.in_(actions)))
                            .group_by(audit.c.action)).all())
                        absent = markers.get(actions[0], 0) > markers.get(actions[1], 0)
                        seen = row["identity_key"] in observed
                        counts["present" if seen else "not_seen"] += 1
                        if seen == (not absent):
                            continue
                        action = actions[1] if seen else actions[0]
                        sequence = sum(markers.values()) + 1
                        # Deterministic per-identity ordinal enforces a single
                        # marker even when full-export reconciliation overlaps.
                        marker_id = digest({"identity_key": row["identity_key"], "presence_marker": sequence})
                        connection.execute(insert(audit).values(id=marker_id, source_revision_id=row["id"],
                            action=action, actor=actor, at=self.clock()))
                        counts["restored" if seen else "newly_not_seen"] += 1
                    return counts
            except IntegrityError:
                if attempt == 2:
                    raise IntakeUnavailable("Source reconciliation contention; retry safely") from None
            except SQLAlchemyError:
                raise IntakeUnavailable("Source reconciliation audit unavailable") from None
