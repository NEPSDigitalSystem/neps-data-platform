# DE03 storage and recovery review

This procedure is a candidate for DBA acceptance. The local synthetic fixture is
PostgreSQL 18.6 with a dedicated `neps_source` schema. It is not evidence of the
production version, operational backup service or agreed recovery targets.

## Migration sequence

The owner must confirm the actual database/version, current revision, schema,
search path, role ownership, available storage and maintenance window. Provision
the approved application schema before running Alembic. A history table in a
different schema blocks migration. Review it and any existing V3.1 tables before
choosing the schema. Do not rename or move history by guesswork.

Set `WAREHOUSE_SCHEMA` through the approved configuration mechanism. Keep the
complete database URL in `DATABASE_URL_FILE`. Do not place it on the command line.
Use the reviewed Python environment and commit for these commands:

```bash
python -m alembic history
python -m alembic current
python -m alembic upgrade 001_initial:head --sql
```

For a database already at 002, generate `002_independent_source_intake:head`
instead. Fresh generation is `upgrade head --sql`. Offline SQL does not inspect
the database. The application schema must already exist. Verify each range and
save its checksum before execution. Apply only through the agreed migration role
and approved environment:

```bash
python -m etl.main migrate
```

Migrations 001 and 002 remain frozen. Revision 003 adds four TEXT demographic
columns and seven DOUBLE PRECISION monthly columns, all nullable and without a
backfill. Existing incompatible manual repairs stop the migration. Revision 004
replaces the research identity/revision uniqueness with destination-aware
uniqueness, binds intake heads to the matching identity/revision, and adds
positive-revision and queue-state checks and indexes. No source payload is
rewritten. Invalid existing data stop the transaction for review.

Neither new revision permits destructive automatic downgrade. Never use
migration 001's `DROP SCHEMA CASCADE` for recovery. Restore to an approved separate
target or prepare a reviewed forward repair.

## Roles and retention

Review `ops/de03_role_grants.sql` with the DBA. It needs existing role names and
an approved schema as psql variables. It does not provision accounts or secrets.
The migration owner is separate from runtime roles. Runtime roles must not own
tables, inherit the owner, have superuser or bypass privileges, or CREATE in the
application schema.

Collectors can append receipt/audit rows, advance heads and insert initial queue
entries. Workers can read receipt/queue rows, update queue transition columns and
append audits. Processors can append research/validated/derived/audit rows and
read verified links. The link writer can insert verified bindings, without
UPDATE or DELETE. A reviewer has read-only access in the approved test scope.
None of these roles can UPDATE, DELETE or TRUNCATE retained raw/audit rows.
The owner can still administer the database. These grants do not establish
per-project row policies or live source/NDS permissions.

## Backup and recovery acceptance

The DBA must supply or accept the operational procedure, backup store/retention,
restore target, recovery point and recovery time targets, and acceptance owner.
Do not write a database password in a command or evidence file. Use approved
libpq service/credential references for native tools.

1. Pause the relevant writers through the responsible operator. Record the
   commit, schema and Alembic revision. Confirm no later writes occur during a
   quiesced comparison, or use the DBA's coordinated snapshot procedure.
2. Save a pre-backup count/digest manifest for all nine V3.1 tables using the
   approved read role and `python -m ops.storage_snapshot`. Save legacy table
   counts and schemas separately if retained consumers require them.
3. Use the version-matched `pg_dump --format=custom --no-owner --no-privileges`
   against the approved source. Save the dump checksum, start/end times and
   backup-store reference. Role definitions/grants need their separate review.
4. Have the DBA provision a separate empty restore target. Use
   `pg_restore --single-transaction --exit-on-error --no-owner --no-privileges`.
   Never restore over the source as a shortcut. Restore the reviewed ownership,
   grants and secret references through the DBA's procedure.
5. Compare all nine count/digest entries, revision/head consistency, queue
   states/tokens, links and derivations. Verify schema and revision history.
   Check that old lease tokens fail and an expired claim can resume safely.
6. Measure the full recovery interval, including provisioning, restore,
   verification, role/secret setup and controlled restart. A fast pg_restore
   command alone is not the recovery time objective. Record missing committed
   data and the recovery checkpoint. Obtain the named owner's acceptance before
   routing an operational workload to the restored target.

Example digest command, with authorised file references and a new output path:

```bash
python -m ops.storage_snapshot --url-file /approved/mounted/database-url --schema approved_schema --output /approved/evidence/before.json
```

The local rehearsal's exact native commands and results are in the NEPS evidence
folder. It restores to a separate synthetic database, compares every V3.1 table
and resumes an expired queue lease. It is a small quiesced test, not a promise of
production recovery time, backup retention or storage durability.

## Evidence limits

PostgreSQL tests use real transactions and named database roles. Their injected
source/NDS policies and local trust authentication do not verify live service
identity, country restrictions or backend access. The fixture uses no real
participant data. Production activation, operational backups, server security and
infrastructure configuration remain with their owners.

PostgreSQL documents the effect of unqualified names and schema CREATE rights in
[schemas](https://www.postgresql.org/docs/18/ddl-schemas.html), concurrent updates
in [transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html),
table permissions in [GRANT](https://www.postgresql.org/docs/18/sql-grant.html), and
logical recovery in [SQL dump](https://www.postgresql.org/docs/18/backup-dump.html).
