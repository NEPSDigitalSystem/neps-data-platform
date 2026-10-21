"""Independent source intake fixtures; no real responses or permissions."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.exc import OperationalError

from etl.intake.v31 import (Claim, Intake, IntakeDenied, IntakeUnavailable, QueueConflict,
                           RecordIdentity, audit, head, metadata, pending, raw)

CONTRACT = json.loads((Path(__file__).parents[1] / "etl/contracts/data_contract_v31.json").read_text(encoding="utf-8"))


class SourcePolicy:
    """Synthetic source-service policy, deliberately without NDS lookup APIs."""
    def __init__(self):
        self.scopes = []
        self.allowed = True
        self.nds_state = "unknown"

    def authorises(self, scope):
        self.scopes.append(scope)
        return (self.allowed is True and scope.project == "SYNTHETIC-PROJECT"
                and scope.destination == "SYNTHETIC-DESTINATION"
                and scope.service_identity == "SYNTHETIC-ENVIRONMENT-SERVICE"
                and scope.actor in {"source-service", "worker"})


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "synthetic.sqlite"
        self.engine = create_engine("sqlite:///" + str(self.path), hide_parameters=True)
        metadata.create_all(self.engine)
        self.policy = SourcePolicy()
        self.now = 1000.0
        self.service = self.make_service()
        self.identity = RecordIdentity("SYNTHETIC-PROJECT", "RC-UNKNOWN-001", "baseline_arm_1", "", "")

    def tearDown(self):
        self.engine.dispose()
        self.directory.cleanup()

    def make_service(self, **changes):
        config = dict(project="SYNTHETIC-PROJECT", destination="SYNTHETIC-DESTINATION",
                      service_identity="SYNTHETIC-ENVIRONMENT-SERVICE", policy=self.policy,
                      clock=lambda: self.now)
        config.update(changes)
        return Intake(self.engine, **config)

    def payload(self, count=188):
        result = {name: "" if i % 3 == 0 else "99" if i % 3 == 1 else "0"
                  for i, name in enumerate(CONTRACT["question_fields"][:count])}
        result.update(study_id=self.identity.source_id, redcap_event_name=self.identity.event,
                      redcap_repeat_instrument="", redcap_repeat_instance="",
                      neps31_screening_complete="2", neps31_extended_baseline_complete="0")
        return result

    def rows(self, table):
        with self.engine.connect() as connection:
            return [dict(row) for row in connection.execute(select(table)).mappings()]

    def test_source_receipt_independent_unknown_withdrawn_and_different_nds_consent(self):
        for state in ["unknown", "not_registered", "withdrawn", "NDS-consent-absent", "different-NDS-ID"]:
            with self.subTest(nds_state=state):
                self.policy.nds_state = state  # Never consulted by source authorisation.
                sid = self.service.receive(self.identity, self.payload(), "SYNTHETIC-v31", "source-service")
                self.assertEqual(self.rows(raw)[0]["id"], sid)
                self.assertEqual(self.rows(pending)[0]["state"], "pending")
        self.assertEqual(len(self.rows(raw)), 1)
        self.assertTrue(all(scope.action == "receive" for scope in self.policy.scopes))

    def test_all188_and_extra_source_consent_evidence_preserved_verbatim(self):
        payload = self.payload()
        # This is a synthetic additional source instrument, never an assertion
        # that the supplied V3.1 dictionary has consent fields.
        payload.update(SYNTHETIC_source_survey_consent="source-native-code-7",
                       SYNTHETIC_consent_evidence={"version": "synthetic-original", "unanswered": None},
                       checkbox___99="1", source_offline_timestamp="2026-01-01T00:00:00Z")
        snapshot = [{"field_name": "study_id"}, {"field_name": "SYNTHETIC_source_survey_consent"}]
        original = copy.deepcopy(payload)
        sid = self.service.receive(self.identity, payload, "SYNTHETIC-v31", "source-service",
                                   metadata_snapshot=snapshot)
        payload["SYNTHETIC_source_survey_consent"] = "caller-mutated"
        snapshot[0]["field_name"] = "caller-mutated"
        stored = self.rows(raw)[0]
        self.assertEqual(stored["id"], sid)
        self.assertEqual(stored["payload"], original)
        self.assertEqual(stored["metadata_snapshot"][0]["field_name"], "study_id")
        self.assertTrue(set(CONTRACT["question_fields"]).issubset(stored["payload"]))
        self.assertNotIn("NDS-consent", stored["payload"])
        claim = self.service.claim("worker")
        self.assertEqual(claim.metadata_snapshot, stored["metadata_snapshot"])
        self.assertEqual(claim.metadata_hash, stored["metadata_hash"])
        self.assertEqual(claim.record_id_field, "study_id")
        self.assertEqual(claim.contract_hash, stored["contract_hash"])

    def test_partial_completed_late_and_corrected_sources_append_revisions(self):
        partial = self.payload(73)
        first = self.service.receive(self.identity, partial, "source-v1", "source-service")
        partial["neps31_screening_complete"] = "0"
        second = self.service.receive(self.identity, partial, "source-v1", "source-service")
        late = self.payload(188)
        late["neps31_extended_baseline_complete"] = "2"
        third = self.service.receive(self.identity, late, "source-v1", "source-service")
        self.assertEqual(len({first, second, third}), 3)
        self.assertEqual([r["revision"] for r in self.rows(raw)], [1, 2, 3])
        self.assertEqual(self.rows(raw)[0]["payload"]["neps31_screening_complete"], "2")
        self.assertEqual(len(self.rows(pending)), 3)

    def test_unchanged_replay_after_process_reload_has_one_envelope_queue_and_audit(self):
        sid = self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        self.engine.dispose()
        self.engine = create_engine("sqlite:///" + str(self.path), hide_parameters=True)
        self.service = self.make_service()
        self.assertEqual(self.service.receive(self.identity, self.payload(), "source-v1", "source-service"), sid)
        self.assertEqual(len(self.rows(raw)), 1)
        self.assertEqual(len(self.rows(pending)), 1)
        self.assertEqual(len(self.rows(audit)), 1)

    def test_metadata_drift_stored_for_downstream_and_actual_recordkey_can_differ(self):
        payload = self.payload()
        del payload["study_id"]
        payload["source_registry_id"] = self.identity.source_id
        first = self.service.receive(self.identity, payload, "source-v1", "source-service",
                                    record_id_field="source_registry_id", metadata_snapshot=[{"field_name": "source_registry_id"}])
        second = self.service.receive(self.identity, payload, "source-v1", "source-service",
                                     record_id_field="source_registry_id", metadata_snapshot=[{"field_name": "source_registry_id", "extra": "new"}])
        self.assertNotEqual(first, second)
        self.assertEqual(self.rows(raw)[0]["record_id_field"], "source_registry_id")
        self.assertNotEqual(self.rows(raw)[0]["metadata_hash"], self.rows(raw)[1]["metadata_hash"])

    def test_project_event_repeat_identity_separates_records(self):
        one = RecordIdentity("SYNTHETIC-PROJECT", "RC-UNKNOWN-001", "followup_arm_1", "neps31_screening", "1")
        two = RecordIdentity("SYNTHETIC-PROJECT", "RC-UNKNOWN-001", "followup_arm_1", "neps31_screening", "2")
        ids = []
        for identity in [one, two]:
            ids.append(self.service.receive(identity, {"study_id": identity.source_id}, "source-v1", "source-service"))
        self.assertNotEqual(*ids)
        self.assertEqual([row["revision"] for row in self.rows(raw)], [1, 1])

    def test_source_downstream_failure_durable_retry_and_idempotent_ack(self):
        sid = self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        claim = self.service.claim("worker")
        self.assertIsInstance(claim, Claim)
        self.assertEqual(claim.source_revision_id, sid)
        self.assertEqual(claim.attempts, 1)
        self.assertIsNone(self.service.claim("worker"))
        self.assertTrue(self.service.fail(sid, claim.claim_token, "worker", "nds_unavailable", retry_delay=10))
        self.assertIsNone(self.service.claim("worker"))
        self.now += 10
        retry = self.make_service().claim("worker")
        self.assertEqual(retry.payload, self.payload())
        self.assertEqual(retry.attempts, 2)
        self.assertTrue(self.service.ack(sid, retry.claim_token, "worker"))
        self.assertTrue(self.service.ack(sid, retry.claim_token, "worker"))
        self.assertIsNone(self.service.claim("worker"))
        self.assertEqual(len(self.rows(raw)), 1)
        self.assertEqual(self.rows(pending)[0]["state"], "acknowledged")

    def test_worker_crash_lease_recovery_and_stale_ack_denied(self):
        sid = self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        first = self.service.claim("worker", lease_seconds=5)
        self.now += 5
        replacement = self.make_service().claim("worker")
        self.assertEqual(replacement.source_revision_id, sid)
        self.assertNotEqual(replacement.claim_token, first.claim_token)
        with self.assertRaises(QueueConflict): self.service.ack(sid, first.claim_token, "worker")
        self.assertTrue(self.service.ack(sid, replacement.claim_token, "worker"))

    def test_policy_credential_configuration_missing_or_denied_is_closed(self):
        for option in [dict(policy=None), dict(project=None), dict(destination=None), dict(service_identity=None)]:
            with self.subTest(option=option):
                with self.assertRaises(IntakeDenied):
                    self.make_service(**option).receive(self.identity, self.payload(), "source-v1", "source-service")
        self.policy.allowed = False
        with self.assertRaises(IntakeDenied): self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        self.assertEqual(self.rows(raw), [])

    def test_each_queue_action_requires_exact_service_permission(self):
        sid = self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        claim = self.service.claim("worker")
        self.policy.allowed = False
        for action in [lambda: self.service.pending_rows("worker"), lambda: self.service.claim("worker"),
                       lambda: self.service.fail(sid, claim.claim_token, "worker", "mapping_pending"),
                       lambda: self.service.ack(sid, claim.claim_token, "worker")]:
            with self.assertRaises(IntakeDenied): action()
        self.assertEqual(self.rows(pending)[0]["state"], "processing")

    def test_per_record_transaction_rolls_back_raw_head_queue_on_database_failure(self):
        def reject_queue(conn, cursor, statement, parameters, context, executemany):
            if statement.startswith("INSERT INTO nds_v31_intake_pending"):
                raise OperationalError("SYNTHETIC-SECRET", {}, Exception("SYNTHETIC-SECRET"))
        event.listen(self.engine, "before_cursor_execute", reject_queue)
        with self.assertRaises(IntakeUnavailable) as caught:
            self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        self.assertNotIn("SYNTHETIC-SECRET", str(caught.exception))
        event.remove(self.engine, "before_cursor_execute", reject_queue)
        for table in [raw, head, pending, audit]: self.assertEqual(self.rows(table), [])
        self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        self.assertEqual(len(self.rows(raw)), 1)

    def test_no_failure_body_storage_logs_or_implicit_json_coercion(self):
        sid = self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        claim = self.service.claim("worker")
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            with self.assertRaises(ValueError):
                self.service.fail(sid, claim.claim_token, "worker", "SYNTHETIC-SECRET-BODY")
            self.service.fail(sid, claim.claim_token, "worker", "processing_restricted")
        self.assertEqual(output.getvalue() + errors.getvalue(), "")
        self.assertEqual(self.rows(pending)[0]["failure_code"], "processing_restricted")
        for malformed in [{1: "not-native-json"}, {"x": float("nan")}, {"x": ("tuple",)}]:
            with self.assertRaises(ValueError): self.service.receive(self.identity, malformed, "source-v1", "source-service")
        self.assertEqual(len(self.rows(raw)), 1)

    def test_approved_requeue_keeps_raw_metadata_and_is_idempotent_while_pending(self):
        sid = self.service.receive(self.identity, self.payload(), "source-v1", "source-service",
                                   metadata_snapshot=[{"field_name": "study_id", "source_version": "synthetic"}])
        original = self.rows(raw)
        claim = self.service.claim("worker")
        self.service.ack(sid, claim.claim_token, "worker")
        self.assertTrue(self.service.requeue(sid, "worker"))
        self.assertTrue(self.service.requeue(sid, "worker"))
        self.assertEqual(self.rows(raw), original)
        self.assertEqual(len([row for row in self.rows(audit) if row["action"] == "requeued"]), 1)
        replacement = self.service.claim("worker")
        self.assertEqual(replacement.source_revision_id, sid)
        self.assertEqual(replacement.attempts, 2)
        self.assertEqual(replacement.metadata_snapshot, original[0]["metadata_snapshot"])
        with self.assertRaises(QueueConflict): self.service.ack(sid, claim.claim_token, "worker")

    def test_requeue_cannot_steal_active_lease_and_can_recover_expired_or_retry(self):
        sid = self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        claim = self.service.claim("worker", lease_seconds=5)
        with self.assertRaises(QueueConflict): self.service.requeue(sid, "worker")
        self.assertEqual(self.rows(pending)[0]["claim_token"], claim.claim_token)
        self.now += 5
        self.assertTrue(self.service.requeue(sid, "worker"))
        retry = self.service.claim("worker")
        self.service.fail(sid, retry.claim_token, "worker", "mapping_pending", retry_delay=100)
        self.assertTrue(self.service.requeue(sid, "worker"))
        self.assertEqual(self.rows(pending)[0]["failure_code"], None)
        self.assertEqual(self.rows(pending)[0]["state"], "pending")

    def test_requeue_requires_explicit_permission_and_destination_project_scope(self):
        sid = self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        self.policy.allowed = False
        with self.assertRaises(IntakeDenied): self.service.requeue(sid, "worker")
        self.policy.allowed = True
        class OtherDestinationPolicy:
            def authorises(self, scope): return True  # Synthetic different approved destination.
        other = self.make_service(destination="SYNTHETIC-OTHER", policy=OtherDestinationPolicy())
        with self.assertRaises(QueueConflict): other.requeue(sid, "worker")
        other_project = self.make_service(project="SYNTHETIC-OTHER-PROJECT", policy=OtherDestinationPolicy())
        with self.assertRaises(QueueConflict): other_project.requeue(sid, "worker")
        self.assertEqual(self.rows(pending)[0]["state"], "pending")

    def test_full_export_disappearance_restoration_is_audit_only_idempotent(self):
        self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        original = self.rows(raw)
        expected_absent = dict(present=0, not_seen=1, newly_not_seen=1, restored=0)
        self.assertEqual(self.service.reconcile([], "source-service", full_export_succeeded=True), expected_absent)
        expected_absent["newly_not_seen"] = 0
        self.assertEqual(self.service.reconcile([], "source-service", full_export_succeeded=True), expected_absent)
        self.assertEqual(len([r for r in self.rows(audit) if r["action"] == "not_seen_in_full_export"]), 1)
        self.assertEqual(self.rows(raw), original)
        restored = self.service.reconcile([self.identity], "source-service", full_export_succeeded=True)
        self.assertEqual(restored, dict(present=1, not_seen=0, newly_not_seen=0, restored=1))
        restored["restored"] = 0
        self.assertEqual(self.service.reconcile([self.identity], "source-service", full_export_succeeded=True), restored)
        self.assertEqual(self.rows(raw), original)
        self.assertEqual(self.rows(pending)[0]["state"], "pending")

    def test_incremental_correction_does_not_clear_not_seen_full_export_marker(self):
        self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        self.service.reconcile([], "source-service", full_export_succeeded=True)
        amended = self.payload()
        amended["k6_1"] = "2"
        sid = self.service.receive(self.identity, amended, "source-v1", "source-service")
        result = self.service.reconcile([], "source-service", full_export_succeeded=True)
        self.assertEqual(result, dict(present=0, not_seen=1, newly_not_seen=0, restored=0))
        self.service.reconcile([self.identity], "source-service", full_export_succeeded=True)
        marker = [r for r in self.rows(audit) if r["action"] == "seen_in_full_export"][0]
        self.assertEqual(marker["source_revision_id"], sid)

    def test_reconciliation_denied_unconfirmed_or_incomplete_and_destination_scoped(self):
        self.service.receive(self.identity, self.payload(), "source-v1", "source-service")
        for confirmed in [False, None, 1, "success"]:
            with self.assertRaises(ValueError):
                self.service.reconcile([], "source-service", full_export_succeeded=confirmed)
        missing = RecordIdentity("SYNTHETIC-PROJECT", "SYNTHETIC-NOT-RECEIVED")
        with self.assertRaises(ValueError):
            self.service.reconcile([missing], "source-service", full_export_succeeded=True)
        self.policy.allowed = False
        with self.assertRaises(IntakeDenied):
            self.service.reconcile([], "source-service", full_export_succeeded=True)
        self.policy.allowed = True
        class OtherDestinationPolicy:
            def authorises(self, scope): return True
        other = self.make_service(destination="SYNTHETIC-OTHER", policy=OtherDestinationPolicy())
        self.assertEqual(other.reconcile([], "source-service", full_export_succeeded=True),
                         dict(present=0, not_seen=0, newly_not_seen=0, restored=0))
        with self.assertRaises(IntakeDenied):
            self.service.reconcile([RecordIdentity("OTHER-PROJECT", "SYNTHETIC")],
                                   "source-service", full_export_succeeded=True)
        self.assertEqual(len(self.rows(audit)), 1)


if __name__ == "__main__": unittest.main()
