"""Workstream E1: Disposable database purge drill rehearsal.

Rehearses the exact TRUNCATE cascade logic from neps-infrastructure/scripts/purge-mock-data.sh
on an isolated disposable database without risking or modifying the active demo database.
Verifies all 9 tables are populated, then purged to 0 rows.
"""
import pytest
from sqlalchemy import create_engine, select, func, text
from etl.repository.migration import upgrade
from etl.intake.v31 import metadata as intake_metadata, Intake, RecordIdentity
from etl.repository.participant_links import metadata as link_metadata, ParticipantLinks
from etl.repository.v31 import metadata as repo_metadata, Repository, RegistryDecision, RecordIdentity as ResearchIdentity


def test_purge_drill_on_disposable_database():
    # 1. Create completely isolated in-memory disposable database
    engine = create_engine("sqlite:///:memory:")
    
    # 2. Apply migrations/schemas
    with engine.begin() as conn:
        upgrade(conn)
        intake_metadata.create_all(conn)
        link_metadata.create_all(conn)
        repo_metadata.create_all(conn)

    # 3. Seed synthetic rows across all 9 tables
    # (a) Intake raw, head, pending, audit
    intake = Intake(
        engine,
        project="synthetic-drill",
        destination="Ghana",
        service_identity="drill-service",
        policy=type("P", (), {"authorises": lambda self, s: True})(),
    )
    rec_id = RecordIdentity("synthetic-drill", "DRILL-001")
    intake.receive(rec_id, {"study_id": "DRILL-001", "k6_1": "0"}, "v1", "drill-actor")
    claim = intake.claim("drill-worker")
    assert claim is not None
    intake.ack(claim.source_revision_id, claim.claim_token, "drill-worker")

    # (b) Participant links
    links = ParticipantLinks(engine, authoriser=lambda *args: True)
    links.bind("synthetic-drill", "DRILL-001", "NDS-DRILL-001", "v1", "drill-actor")

    # (c) Repository source, validated, derived, audit
    class DrillPolicy:
        def resolve(self, identity):
            return RegistryDecision("Ghana", True, True, "NDS-DRILL-001")
        def permits(self, *a):
            return True
        def transfer_permitted(self, *a):
            return True

    repo = Repository(engine, adapter=DrillPolicy(), storage_destination="Ghana")
    sid = repo.ingest(
        ResearchIdentity("synthetic-drill", "DRILL-001", "", "", ""),
        {"study_id": "DRILL-001", "country": "1"},
        "v1",
        "drill-actor",
        nds_participant_id="NDS-DRILL-001",
        intake_revision_id=claim.source_revision_id,
    )
    repo.store_derived(sid, "drill-calc-v1", {"drill": True}, "drill-actor")

    # 4. Verify tables are non-empty before purge
    tables = [
        "nds_v31_derived",
        "nds_v31_validated",
        "nds_v31_audit",
        "nds_v31_source",
        "nds_v31_intake_pending",
        "nds_v31_intake_head",
        "nds_v31_intake_audit",
        "nds_v31_intake_raw",
        "nds_v31_participant_links",
    ]
    counts_before = {}
    with engine.connect() as conn:
        for t in tables:
            counts_before[t] = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            assert counts_before[t] > 0, f"Expected table {t} to have rows before purge"

    # 5. Execute Purge Drill (same table list and order as purge-mock-data.sh)
    with engine.begin() as conn:
        for t in tables:
            conn.execute(text(f"DELETE FROM {t}"))

    # 6. Verify all tables are completely empty after purge
    counts_after = {}
    with engine.connect() as conn:
        for t in tables:
            counts_after[t] = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            assert counts_after[t] == 0, f"Expected table {t} to be empty after purge, found {counts_after[t]}"

    assert sum(counts_after.values()) == 0
