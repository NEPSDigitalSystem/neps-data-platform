# neps-redcap-sync

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

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

Start Postgres locally:

```bash
docker run -d --name neps-postgres \
  -e POSTGRES_USER=neps \
  -e POSTGRES_PASSWORD=neps_password \
  -e POSTGRES_DB=neps_db \
  -p 5432:5432 postgres:15-alpine
```

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

```bash
docker build -t neps-data-platform:test .
docker run --rm neps-data-platform:test ls /app
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

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `DATABASE_URL_FILE` | Path to file containing DB URL |
| `REDCAP_API_URL` | Mock or production REDCap base URL |
| `REDCAP_API_TOKEN` | API token, required when `REDCAP_MOCK_ENABLED=false` |
| `REDCAP_API_TOKEN_FILE` | Path to token secret file |
| `REDCAP_MOCK_ENABLED` | `true` for mock API, `false` for real REDCap |
| `REDCAP_PROJECT_ID` | Project identifier stored in sync state |

## Production REDCap

When KNUST/CAIH credentials or a final production service contract are available, update the production extractor in `etl/extract/production_client.py` so it emits the same normalized entity records as the mock client. The loader and database schema expect these entities: `participants`, `consent_records`, `survey_responses`, `distress_screenings`, `referrals`, and `wp6_sessions`.
