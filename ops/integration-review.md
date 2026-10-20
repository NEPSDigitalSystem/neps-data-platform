# Data-platform integration review

The integration combines the reviewed DE02/DE03 implementation with main at
`6a4da224d3e09d99fc6a36afdd28da5dd7c5ccb6`. The newer remote handover branch
repeats the original patch and omits the later retirement and storage repairs.
Only its explicit UTF-8 reads were carried over. Original handover files remain
unchanged. No other repository is part of this change.

## Resulting behaviour

- Authorised REDCap receipt retains source payloads, metadata, revisions and
  queue/audit history before NDS registration, ID mapping or purpose consent.
  The collector remains disabled by default. Live source permissions are pending.
- Legacy fixed-table sync and distress analysis remain retired. Their CLI and
  library entry points fail before data access. No existing data is deleted.
- Frozen migrations 001/002 are unchanged. Additive 003/004 repair eleven nullable
  legacy columns and destination/head/queue integrity. PostgreSQL schema selection
  is explicit. Bare PostgreSQL URLs use the declared psycopg2 driver.
- Research revisions, exports and derivation remain scoped to their stored
  destination, including identical payloads accepted by separately scoped policies.
- Supplied reference documents and independent scoring cases are in test fixtures
  with their original hashes. Normal pytest runs no longer depend on external
  author paths. Relative contract source names make regeneration location independent.
- CI covers Python 3.11/3.14 and real disposable PostgreSQL, saves recovery evidence,
  audits both requirement files and scans the built image on PRs. Dependency PRs
  require human review. The previous title-based merge comment is removed.
- The ETL image includes the recovery snapshot utility and keeps its non-root user.

The contract path normalisation changes its hash once. Scientific definitions,
formulas, reference bytes and dictionary hashes are unchanged. Existing retained
source revisions and results keep their recorded hashes. Interpretation and
recalculation remain separately controlled.

## Reproduce the checks

Install both requirement files in an isolated Python environment. From the repo:

```sh
python -m pytest tests -q
python scripts/verify_postgresql.py --evidence-dir /tmp/neps-postgresql-review
docker build -t neps-data-platform:review .
docker run --rm --network none neps-data-platform:review python -m etl.main --help
docker run --rm --network none neps-data-platform:review python -m ops.storage_snapshot --help
```

Use a new evidence directory. Normal pytest skips PostgreSQL when its explicit
fixture settings are absent. The full runner rejects skips. It creates its own
loopback-only PostgreSQL 18.6 fixture, uses synthetic data and removes its container.
For container-hosted tests, `--network` accepts only an existing internal network
with the synthetic name prefix and DE03 label. That mode publishes no database
ports. The fixture verifies both transports instead of accepting arbitrary URLs.

Local evidence dated 20 October 2026 records the normal and full suites, separate
Python environments, exact resolved packages, recovery digests, offline SQL,
workflow validation, image smoke checks and dependency audit. The evidence and
PR draft are in Frank's NEPS notes folder. All eight original test assets and
83 handover manifest entries retain their original bytes. Assertions were retained.

## PR and operational boundaries

Open the PR against `main`. GitHub-hosted CI has not run before the PR exists.
Review its results before merging. The existing push workflow can publish an
image and deploy when its host variable is configured. Repository environment
reviewer/branch protections are owner-controlled settings and were not verified
by local tests. The owner must confirm the production deployment gate before merge.
This integration does not change infrastructure services or activate deployment.

DE03 recovery acceptance owner, accepted procedure and RPO/RTO remain TBD by
Frank's explicit deferral. Local dump/restore and queue recovery are test evidence,
not DBA acceptance. DE04 has not started. Live REDCap/backend interfaces, source
scope, destination permissions, scientific operational use and production
activation remain with their assigned owners and tasks.
