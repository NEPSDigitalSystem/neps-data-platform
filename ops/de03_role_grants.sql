-- Candidate table grants. DBA supplies existing NOLOGIN/LOGIN role names.
-- Requires psql variables schema, collector, worker, processor, links, reviewer.
-- No role creation, passwords, membership or server configuration occurs here.
-- Runtime roles must not own tables, inherit the owner or bypass row policies.
REVOKE ALL ON ALL TABLES IN SCHEMA :"schema" FROM PUBLIC, :"collector", :"worker", :"processor", :"links", :"reviewer";
REVOKE CREATE ON SCHEMA :"schema" FROM PUBLIC, :"collector", :"worker", :"processor", :"links", :"reviewer";
GRANT USAGE ON SCHEMA :"schema" TO :"collector", :"worker", :"processor", :"links", :"reviewer";
GRANT SELECT, INSERT ON :"schema".nds_v31_intake_raw, :"schema".nds_v31_intake_audit TO :"collector";
GRANT SELECT, INSERT ON :"schema".nds_v31_intake_head TO :"collector";
GRANT UPDATE (revision, source_revision_id) ON :"schema".nds_v31_intake_head TO :"collector";
GRANT INSERT (source_revision_id, state, attempts, next_attempt_at) ON :"schema".nds_v31_intake_pending TO :"collector";
GRANT SELECT ON :"schema".nds_v31_intake_raw, :"schema".nds_v31_intake_pending TO :"worker";
GRANT INSERT ON :"schema".nds_v31_intake_audit TO :"worker";
GRANT UPDATE (state, attempts, failure_code, next_attempt_at, claim_token, claim_actor, lease_until)
    ON :"schema".nds_v31_intake_pending TO :"worker";
GRANT SELECT ON :"schema".nds_v31_participant_links TO :"processor";
GRANT SELECT, INSERT ON :"schema".nds_v31_source, :"schema".nds_v31_validated,
    :"schema".nds_v31_derived, :"schema".nds_v31_audit TO :"processor";
GRANT SELECT, INSERT ON :"schema".nds_v31_participant_links TO :"links";
-- Reviewer is for the approved synthetic acceptance run, not a public data role.
GRANT SELECT ON ALL TABLES IN SCHEMA :"schema" TO :"reviewer";
-- No UPDATE/DELETE/TRUNCATE on retained raw, audit, validated, derived or links.
-- DBA must separately revoke unexpected inherited/pre-existing grants and CREATE
-- on this schema. These grants do not provide per-project row-level isolation.
