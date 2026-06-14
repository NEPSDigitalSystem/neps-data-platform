# neps-redcap-sync

<<<<<<< Updated upstream
NEPS Digital ETL: sync REDCap or mock REDCap data into the central PostgreSQL warehouse.

## What this does

- Extracts records from mock REDCap in development or production REDCap when credentials are available.
- Normalizes REDCap-style records into the backend schema tables in the `redcap` Postgres schema.
- Loads `participants`, `consent_records`, `survey_responses`, `distress_screenings`, `referrals`, and `wp6_sessions`.
- Stores REDCap metadata in `redcap.raw_redcap_metadata`.
- Tracks sync state in `redcap.etl_sync_state` and run history in `redcap.etl_run_log`.
- Exposes simple SQL views named `redcap.v_<table>` for each loaded backend table.

`mock-redcap-service/` is development-only. It is ignored by Git and excluded from Docker builds; the production image copies only `etl/`, `alembic/`, and `alembic.ini`.

## Quick Start
=======
NEPS Digital ETL: sync REDCap (or mock REDCap) data into the central PostgreSQL warehouse.

## What this does

- Extracts records from **mock REDCap** (development) or **real REDCap** (production)
- Loads raw landing tables in the `redcap` Postgres schema
- Exposes analyst-friendly SQL views (`redcap.v_redcap_*`)
- Tracks sync state in `redcap.etl_sync_state` and `redcap.etl_run_log`

The [`mock-redcap-service/`](mock-redcap-service/) folder is a **development-only** stand-in for production REDCap. It is excluded from the Docker image via [`.dockerignore`](.dockerignore).

## Quick start (local)

### 1. Install dependencies
>>>>>>> Stashed changes

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

<<<<<<< Updated upstream
Start Postgres locally:
=======
### 2. Start Postgres + mock REDCap API

The mock API is served by `neps-backend` with the mock router mounted. Use the provided compose file:

```bash
docker compose -f mock-redcap-service/docker-compose.mock.yml up -d postgres
# Start neps-backend separately with mock router mounted, or use the full compose stack
```

If you only have Postgres locally:
>>>>>>> Stashed changes

```bash
docker run -d --name neps-postgres \
  -e POSTGRES_USER=neps \
  -e POSTGRES_PASSWORD=neps_password \
  -e POSTGRES_DB=neps_db \
  -p 5432:5432 postgres:15-alpine
```

<<<<<<< Updated upstream
Point `REDCAP_API_URL` in `.env` at a running mock API. The local default is:

```bash
REDCAP_API_URL=http://localhost:8000/api/redcap
REDCAP_MOCK_ENABLED=true
```

Run migrations and sync:

```bash
python -m etl.main migrate
python -m etl.main sync --full
```

Useful commands:

```bash
python -m etl.main health
python -m etl.main sync --metadata-only
python -m etl.main sync --dry-run
python -m etl.main sync --full
```

## Query Loaded Data

```sql
SELECT COUNT(*) FROM redcap.participants;
SELECT COUNT(*) FROM redcap.consent_records;
SELECT COUNT(*) FROM redcap.survey_responses;
SELECT COUNT(*) FROM redcap.distress_screenings;
SELECT COUNT(*) FROM redcap.wp6_sessions;
SELECT * FROM redcap.v_participants LIMIT 10;
SELECT * FROM redcap.etl_run_log ORDER BY started_at DESC LIMIT 5;
```

Re-running `sync --full` should be idempotent because upserts use natural keys such as `record_id`, `(record_id, month)`, `(record_id, screening_date)`, and `(record_id, session_number)`.

## Test The Codebase

Install dependencies first:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Run all unit tests:

```bash
pytest tests/ -v
```

Run a quick syntax/import check:

```bash
python -m compileall etl tests
```

Verify the Docker build excludes local-only mock code:
=======
Point `REDCAP_API_URL` in `.env` at a running mock API (default: `http://localhost:8000/api/redcap`).

### 3. Run migrations

```bash
python -m etl.main migrate
```

### 4. Run sync

```bash
# Metadata only
python -m etl.main sync --metadata-only

# Dry run (extract metadata, no DB writes for records)
python -m etl.main sync --dry-run

# Full sync (default for mock mode)
python -m etl.main sync --full

# Health check
python -m etl.main health
```

### 5. Query loaded data

```sql
SELECT COUNT(*) FROM redcap.raw_redcap_demographics;
SELECT COUNT(*) FROM redcap.raw_redcap_monthly_self_report;
SELECT * FROM redcap.v_redcap_demographics LIMIT 10;
SELECT * FROM redcap.etl_run_log ORDER BY started_at DESC LIMIT 5;
```

## How to test

### Unit tests (no external services)

Uses HTTP mocks and fixtures — does not import `mock-redcap-service/` code.

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

Tests cover:

- Config and secret loading (`tests/test_config.py`)
- `.dockerignore` excludes mock folder (`tests/test_dockerignore.py`)
- Mock REDCap HTTP client (`tests/test_mock_client.py`)
- Record routing and normalization (`tests/test_normalizer.py`, `tests/test_parser.py`)

### Verify Docker image excludes mock folder
>>>>>>> Stashed changes

```bash
docker build -t neps-data-platform:test .
docker run --rm neps-data-platform:test ls /app
<<<<<<< Updated upstream
```

The container should list application files such as `etl`, `alembic`, and `alembic.ini`, and should not include `mock-redcap-service` or `tests`.

## Integration Test

With Postgres and the mock API running:

```bash
export DATABASE_URL=postgresql://neps:neps_password@localhost:5432/neps_db
export REDCAP_API_URL=http://localhost:8000/api/redcap
export REDCAP_MOCK_ENABLED=true
export REDCAP_PROJECT_ID=NEPS-2025

python -m etl.main migrate
python -m etl.main health
python -m etl.main sync --full
```

Then validate counts:

```sql
SELECT COUNT(*) FROM redcap.participants;
SELECT COUNT(*) FROM redcap.survey_responses;
SELECT COUNT(*) FROM redcap.consent_records;
SELECT COUNT(*) FROM redcap.distress_screenings;
SELECT COUNT(*) FROM redcap.wp6_sessions;
SELECT status, records_extracted, records_loaded
FROM redcap.etl_run_log
ORDER BY started_at DESC
LIMIT 5;
```

## Environment Variables
=======
# Should list etl/ and alembic/ only — no mock-redcap-service/
```

### Integration test (mock REDCap + Postgres)

Requires a running mock API and Postgres:

```bash
# Terminal 1: Postgres
docker run -d --name neps-postgres \
  -e POSTGRES_USER=neps \
  -e POSTGRES_PASSWORD=neps_password \
  -e POSTGRES_DB=neps_db \
  -p 5432:5432 postgres:15-alpine

# Terminal 2: mock API (neps-backend with mock router mounted)
# REDCAP_API_URL=http://localhost:8000/api/redcap

# Terminal 3: ETL
export DATABASE_URL=postgresql://neps:neps_password@localhost:5432/neps_db
export REDCAP_API_URL=http://localhost:8000/api/redcap
export REDCAP_MOCK_ENABLED=true
python -m etl.main migrate
python -m etl.main sync --full
```

Or use the full stack compose:

```bash
docker compose -f mock-redcap-service/docker-compose.mock.yml up -d
docker compose -f mock-redcap-service/docker-compose.mock.yml run --rm neps-data-platform python -m etl.main migrate
docker compose -f mock-redcap-service/docker-compose.mock.yml run --rm neps-data-platform python -m etl.main sync --full
```

Expected results after a successful mock sync:

- ~150 rows in `redcap.raw_redcap_demographics`
- Thousands of rows in `redcap.raw_redcap_monthly_self_report`
- Rows in `redcap.raw_redcap_distress_screening` and `redcap.raw_redcap_wp6_session`
- `redcap.etl_run_log.status = 'success'`

Re-running `sync --full` should be idempotent (no duplicate primary keys).

## Environment variables
>>>>>>> Stashed changes

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
<<<<<<< Updated upstream
| `DATABASE_URL_FILE` | Path to file containing DB URL |
| `REDCAP_API_URL` | Mock or production REDCap base URL |
| `REDCAP_API_TOKEN` | API token, required when `REDCAP_MOCK_ENABLED=false` |
| `REDCAP_API_TOKEN_FILE` | Path to token secret file |
| `REDCAP_MOCK_ENABLED` | `true` for mock API, `false` for real REDCap |
| `REDCAP_PROJECT_ID` | Project identifier stored in sync state |

## Production REDCap

When KNUST/CAIH credentials or a final production service contract are available, update the production extractor in `etl/extract/production_client.py` so it emits the same normalized entity records as the mock client. The loader and database schema expect these entities: `participants`, `consent_records`, `survey_responses`, `distress_screenings`, `referrals`, and `wp6_sessions`.
=======
| `DATABASE_URL_FILE` | Path to file containing DB URL (production secrets) |
| `REDCAP_API_URL` | Mock or production REDCap base URL |
| `REDCAP_API_TOKEN` | API token (required when `REDCAP_MOCK_ENABLED=false`) |
| `REDCAP_API_TOKEN_FILE` | Path to token secret file |
| `REDCAP_MOCK_ENABLED` | `true` = mock API (dev), `false` = real REDCap |
| `REDCAP_PROJECT_ID` | Project identifier stored in sync state |

## Switching to production REDCap

When KNUST/CAIH credentials are available:

```bash
REDCAP_API_URL=https://kcird.org/api/
REDCAP_API_TOKEN_FILE=/run/secrets/redcap_api_token
REDCAP_MOCK_ENABLED=false
python -m etl.main sync --full   # initial backfill
python -m etl.main sync            # incremental thereafter
```

## CLI reference

| Command | Description |
|---------|-------------|
| `python -m etl.main health` | Check DB + REDCap connectivity |
| `python -m etl.main migrate` | Apply Alembic migrations |
| `python -m etl.main sync` | Incremental sync (full refresh in mock mode) |
| `python -m etl.main sync --full` | Full record refresh |
| `python -m etl.main sync --metadata-only` | Sync metadata only |
| `python -m etl.main sync --dry-run` | Extract metadata without loading records |
>>>>>>> Stashed changes
