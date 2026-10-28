# NEPS Data Platform

The NEPS Data Platform implements independent REDCap source receipt, versioned
PostgreSQL storage and provisional V3.1 scoring. The supported collector and
separate NDS processing libraries have synthetic local evidence. Actual source,
backend, ML/AI and portal service acceptance remains owner work.

`ingest-v31` is a development/testing shortcut with deferred history, policy,
schema and identifier repairs. Use the current implementation status to assess
each component before an authorised integration run.

## Local engineering documents

- [Implementation status and acceptance boundaries](docs/IMPLEMENTATION_STATUS.md)
- [Verified 83-entry handover index](docs/HANDOVER_INDEX.md)
- [Integration blueprint and environment handover](tests/integration/README.md)
- [Lineage](docs/DATA_LINEAGE.md), [quality rules](docs/DATA_QUALITY_RULES.md),
  [scoring algorithm](docs/SCORING_ALGORITHM.md) and [SQL/metric guidance](docs/sql_queries/README.md)

## Table of Contents

1. [Architecture](#architecture)
2. [Repository Layout](#repository-layout)
3. [Quick Start](#quick-start)
4. [Environment Configuration](#environment-configuration)
5. [CLI Usage](#cli-usage)
6. [V3.1 Baseline Ingest](#v31-baseline-ingest)
7. [Migrations](#migrations)
8. [Testing](#testing)
9. [Docker](#docker)
10. [Retired Legacy Paths](#retired-legacy-paths)

## Architecture

```
┌──────────────────────────┐
│  REDCap source           │
│  mock or production      │
└────────────┬─────────────┘
             │  Extract
             ▼
┌──────────────────────────┐
│  Extract layer           │
│  mock_client             │
│  production_client       │
└────────────┬─────────────┘
             │  Contract + scoring
             ▼
┌──────────────────────────┐
│  V3.1 layer              │
│  contracts, scorer,      │
│  intake, repository      │
└────────────┬─────────────┘
             │  Load
             ▼
┌──────────────────────────┐
│  PostgreSQL              │
│  nds_v31_source          │
│  nds_v31_derived         │
│  nds_v31_audit ...       │
└────────────┬─────────────┘
             │
             ▼
   backend  ·  ML/AI  ·  portal
```

Source receipt and downstream eligibility are deliberately separate concerns. The
platform stores every authorised export first; NDS registration, NDS IDs and
purpose consent gate the downstream processing stage, not source receipt.

## Repository Layout

| Path | Contents |
| --- | --- |
| `etl/main.py` | CLI entry point and subcommands |
| `etl/config.py` | Settings model and secret-file resolution |
| `etl/ingest_v31_simple.py` | Operator path behind `ingest-v31` |
| `etl/extract/` | Mock and production REDCap clients |
| `etl/contracts/` | `data_contract_v31.json`, the 73-item core manifest |
| `etl/scoring/` | V3.1 subscale and composite scoring |
| `etl/intake/` | Independent source intake, history and queue |
| `etl/repository/` | Versioned V3.1 storage and integrity helpers |
| `alembic/versions/` | Migrations 001 to 004 |
| `ops/` | DBA review material and the storage snapshot CLI |
| `scripts/verify_postgresql.py` | Full suite against a disposable PostgreSQL |
| `tests/` | Unit and contract tests |

## Quick Start

### Prerequisites

- CI lists Python 3.11 and 3.14. The local reviewed environment uses 3.14.8.
  The Dockerfile uses Python 3.15, which needs separate application-image acceptance.
- PostgreSQL reachable through `DATABASE_URL` or `DATABASE_URL_FILE`.
- Docker only for the container build and the synthetic PostgreSQL test run.

### Installation

```bash
git clone https://github.com/NEPSDigitalSystem/neps-data-platform.git
cd neps-data-platform
python -m venv .venv
```

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Configure

```bash
cp .env.example .env
```

Set `WAREHOUSE_SCHEMA` to the approved application schema. Migrations and the
V3.1 ingest refuse to start without it. Never commit credentials; reference
mounted files through `DATABASE_URL_FILE` and `REDCAP_API_TOKEN_FILE`.

### Development shortcut example

These are reference commands for an authorised synthetic development store.
The shortcut does not provide the supported intake/history/permission flow.

```bash
python -m etl.main migrate
python -m etl.main ingest-v31
```

## Environment Configuration

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | `development`, `staging` or `production`. Default `development` |
| `LOG_LEVEL` | structlog level. Default `INFO` |
| `DATABASE_URL` | Full PostgreSQL URL |
| `DATABASE_URL_FILE` | Mounted file whose contents replace `DATABASE_URL` |
| `WAREHOUSE_SCHEMA` | Application schema holding the `nds_v31_*` tables and `alembic_version`. Required for any PostgreSQL run |
| `REDCAP_API_URL` | Source endpoint, including the service `/api` prefix |
| `REDCAP_API_TOKEN` | Source token. Required when `REDCAP_MOCK_ENABLED=false` |
| `REDCAP_API_TOKEN_FILE` | Mounted file whose contents replace `REDCAP_API_TOKEN` |
| `REDCAP_MOCK_ENABLED` | `true` routes to the hosted mock service. Default `true` |
| `REDCAP_PROJECT_ID` | Project namespace written into identity keys |
| `SOURCE_INTAKE_ENABLED` | Explicit activation of independent source intake. Default `false` |
| `SOURCE_DESTINATION` | Storage destination recorded on every stored revision |
| `SOURCE_SERVICE_IDENTITY` | Collector identity used by the intake workflow |
| `SOURCE_EVENT_MODE` | `auto`, `unverified`, `classic` or `longitudinal`. Default `auto` |

`WAREHOUSE_SCHEMA` must match `[a-z][a-z0-9_]{0,62}` and must not be `pg_*` or
`information_schema`. An existing revision history in a different schema blocks
execution instead of silently restarting the chain. The DBA provisions the schema
and reviews history before the first migration.

`SOURCE_INTAKE_ENABLED` defaults to `false`. Configuration alone does not prove
real export or destination permission; the source owner must verify service,
project and destination rights before activation. `auto` preserves native event
and repeat identifiers if the project changes mode; pin `classic` or
`longitudinal` only when verified.

## CLI Usage

```bash
python -m etl.main --help
```

| Command | Behaviour |
| --- | --- |
| `health` | Checks database and source connectivity. Exits 1 if the database is unreachable |
| `migrate` | Applies Alembic migrations to head. Requires `WAREHOUSE_SCHEMA` |
| `ingest-v31` | Loads the V3.1 baseline and writes source revisions plus scores |
| `collect-source` | Full independent source receipt. Requires `SOURCE_INTAKE_ENABLED=true` |
| `sync`, `sync --full` | Compatibility alias that dispatches to `collect-source`. Exits 1 when intake is disabled |
| `sync --metadata-only`, `sync --dry-run` | Retired. Exit 1 without source or database work |
| `analyze` | Retired distress analysis. Exits 1 without reading configuration or data |

Examples:

```bash
python -m etl.main health
python -m etl.main migrate
python -m etl.main ingest-v31
python -m etl.main collect-source
```

The downstream queue, participant-link and policy interfaces are libraries. No
worker or requeue CLI is supplied yet. Backend owners provide trusted identity and
purpose-consent services; scientific owners provide applicability decisions.

## V3.1 Baseline Ingest

`python -m etl.main ingest-v31` is the operator path that loads the baseline
screening dataset:

1. Reads `etl/contracts/data_contract_v31.json`, which travels with the package.
   A shortcut-specific contract digest is recorded. Its serialization differs
   from the supported workflow's canonical contract digest.
2. Fetches `GET /api/v31/baseline` from the configured source. The hosted mock
   service returns 150 participants at 223 fields each, with `study_id` of the
   form `MOCK-0001`.
3. Writes one row per participant to `nds_v31_source`: identity, revision, change
   hash, payload, country, contract hash and storage destination.
4. Scores each record with the V3.1 scorer and upserts the subscale results into
   `nds_v31_derived`.

The shortcut fixes source revision at 1. Conflicting source inserts do nothing,
while derived rows upsert on `(source_id, calculation_version)`. A corrected
answer can therefore leave the earlier source payload and replace its derived
result. This is the deferred N02 history defect. The supported intake/repository
path appends revisions and retains provenance, as described in the lineage.

`EPI` and `NSES` remain `NULL` unless screening applicability has been confirmed
externally. The scorer refuses to guess for out-of-school or unknown status, so
a `null` there is a deliberate unavailable state, not a failure.

`SOURCE_DESTINATION` is required; the command exits 1 without it.

## Migrations

| Revision | Contents |
| --- | --- |
| `001_initial` | Legacy fixed-table schema |
| `002_independent_source_intake` | Adds the nine `nds_v31_*` tables |
| `003_legacy_columns` | Adds eleven nullable legacy columns and rejects incompatible manual repairs |
| `004_storage_integrity` | Scopes research revisions by storage destination and adds intake head, revision and queue constraints |

The head revision is `004_storage_integrity`. Upgrades add schema and integrity
repairs without deleting retained rows. Migration 002 blocks rollback of nonempty
tables; 003 and 004 require reviewed forward repair. Historical migration 001 has
a destructive schema downgrade and must not be used as a recovery procedure.

Review the revision range and offline SQL before execution:

```bash
python -m alembic history
python -m alembic upgrade head --sql
```

`ops/de03_role_grants.sql` is a candidate privilege specification for DBA review.
Runtime roles must not own the tables or inherit the owner, and raw and audit rows
receive no `UPDATE`, `DELETE` or `TRUNCATE` grants. These grants do not implement
per-project row-level access or prove live source permissions.

## Testing

The normal suite runs directly from any checkout. Contract paths are relative, so
moving the repository does not change the contract or scoring version.

```bash
pytest tests -q
```

Tests under `tests/postgresql` exercise real database integrity, roles,
concurrency and recovery. They require an explicit synthetic scope, supplied as
`NEPS_DE03_PG_URL_FILE`, `NEPS_DE03_APPROVED=synthetic-disposable` and
`NEPS_DE03_CONTAINER`. Without that configuration they skip, and a skipped check
is not a PostgreSQL pass.

To execute the whole suite against a new disposable PostgreSQL instance:

```bash
python scripts/verify_postgresql.py --evidence-dir /tmp/neps-postgresql-review
```

This needs Docker and a new evidence directory. It uses a pinned image, publishes
only on loopback, creates no permanent volume, and removes its container
afterwards. It never reads an existing database URL or source token. CI runs the
same procedure and rejects skipped tests.

The supplied dictionary, mapping workbook, ordered field map, country displays and
independent scoring cases live under `tests/fixtures`. Their original SHA256
values are checked, and the scientific rules they encode have not changed.

## Docker

```bash
docker build -t neps-data-platform:local .
```

The image runs as an unprivileged `neps` user and ships `etl/`, `alembic/` and
`ops/`. It contains no CLI default subcommand, so the runtime owner supplies the
invocation.

It currently omits `docs/sql_queries/`. DevOps must package or mount those reviewed
SQL files if the reporting helper is used inside the image. Host-checkout tests do
not establish that deployment packaging or the Python 3.15 image works.

In the infrastructure stack the service starts with:

```bash
python -m etl.main migrate && python -m etl.main ingest-v31
```

`migrate` always runs at start because it is idempotent. The V3.1 ingest is a
batch pull owned by the scheduler, so it runs at boot only when
`V31_BOOTSTRAP_ON_START=true` (the local development default, off in staging).
The service reads its database password and source token from `/run/secrets/` and
requires `WAREHOUSE_SCHEMA` to be set.

## Retired Legacy Paths

On 15 October 2026 the data engineer approved retirement of the fixed-table sync
and the distress analysis. Both entry points now fail before any data access.

- The fixed-table sync could discard fields, overwrite history and miss late
  corrections.
- The distress analysis used an unapproved threshold and replaced or dropped its
  result table.

Retirement does not delete existing tables or records. The legacy loading helpers
and the mock adapter remain for compatibility tests; the collection path does not
call them.

Purging mock data before a production cutover is handled outside Alembic by
`neps-infrastructure/scripts/purge-mock-data.sh` and its `.bat` counterpart. No
migration truncates data, so a forward upgrade is always non-destructive.
