# NEPS data platform

This Python pipeline receives authorised REDCap exports into retained source
revisions. NDS registration, NDS IDs and purpose consent apply to the separate
downstream processing stage. They do not filter source receipt.

## Current integration

The V3.1 handover adds the source connector, contracts, intake/history/queue,
participant-link storage, downstream repository, provisional scorer and completion
review. Migration `002_independent_source_intake` adds nine tables. Schema creation
is explicit. Constructing a collector does not migrate the database.

`SOURCE_INTAKE_ENABLED` defaults to `false`. Configuration alone does not prove
real export or destination permission. The source owner must verify service,
project and destination rights before activation. PostgreSQL migrations, live API
behaviour and operational permissions require separate acceptance evidence.

The data engineer approved retirement of legacy fixed-table sync and distress
analysis on 15 October 2026. Both entry points fail before data access. The old
sync could discard fields, overwrite history and miss corrections. The old
analysis used an unapproved threshold and replaced or dropped its result table.
Retirement does not delete existing tables or records. Legacy loading helpers and
mock adapter remain for compatibility tests; collection does not call them.

## Local Python environment

Use an isolated environment and the declared dependency files:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
```

The current container uses Python 3.14 and CI declares Python 3.11. Local DE02
results are for Python 3.14 only. Do not infer a Python 3.11 or container pass.

The full source-contract and golden-scoring tests need the supplied handover's
reference layout. After reviewing and integrating the data-platform patch, use
its portable helper. Supply the actual handover and merged checkout paths:

```bash
NEPS_HANDOVER='/home/frank/Documents/Syncthing/Obsidian/Work/NEPS/NDS_Team'
NEPS_SOURCE_TREE='/path/to/reviewed/data-platform-worktree'
NEPS_VERIFY_PARENT="$(mktemp -d /tmp/neps-de-verify-XXXXXX)"
python3 "$NEPS_HANDOVER/prepare_verification.py" "$NEPS_SOURCE_TREE" --output "$NEPS_VERIFY_PARENT/work"
NEPS_TEST_TREE="$NEPS_VERIFY_PARENT/work/reference_root/REDCap_NDS Build/nds-work/neps-data-platform-main"
cd "$NEPS_TEST_TREE"
/path/to/isolated/venv/bin/python -m pytest tests -q
```

The output directory must be new. The helper copies code, tests and supplied
reference documents, excludes `.env` and secret/data files, and regenerates only
the copied contract's reference paths. Prepare a fresh copy after code changes.
Run with synthetic settings and no inherited real secret-file configuration.
SQLite tests and injected policies verify local behaviour only. They do not prove
PostgreSQL concurrency or actual service permissions.

## Source intake configuration

Use the existing approved secret store and mounted-file references. Never commit
credentials or include their values in commands or logs. Source activation needs
reviewed database migrations and actual source/destination permission evidence.

| Setting | Purpose |
| --- | --- |
| `DATABASE_URL_FILE` | Mounted file containing a complete database URL |
| `REDCAP_API_URL` | Verified HTTPS API endpoint |
| `REDCAP_API_TOKEN_FILE` | Mounted source service token |
| `REDCAP_MOCK_ENABLED` | Must be `false` for independent source collection |
| `REDCAP_PROJECT_ID` | Verified source project namespace |
| `SOURCE_INTAKE_ENABLED` | Explicit activation, default `false` |
| `SOURCE_DESTINATION` | Approved source store destination |
| `SOURCE_SERVICE_IDENTITY` | Verified collector identity |
| `SOURCE_EVENT_MODE` | `auto` preserves native event/repeat context; strict modes need verified configuration |

The source workflow exports the complete authorised project scope, including
partial responses and additional fields. It retains payloads and metadata before
interpretation. Full reconciliation supports late corrections. Missing records
produce visibility audit markers and never imply withdrawal or deletion.

## Commands

```bash
python -m etl.main --help
```

| Command | Behaviour |
| --- | --- |
| `collect-source` | Full source receipt when explicitly enabled and configured |
| `sync` or `sync --full` | Compatibility alias for source receipt when enabled; otherwise exits 1 |
| `sync --metadata-only` or `sync --dry-run` | Exits 1 without collection or database work |
| `analyze` | Retired, exits 1 without reading configuration or data |
| `health` | Explicit connectivity check, requires an approved environment |
| `migrate` | Explicit database migration, requires reviewed SQL and an approved environment |

The downstream queue, participant-link and policy interfaces are libraries.
No worker or requeue CLI is supplied yet. Backend owners provide trusted identity
and purpose-consent services. Scientific owners provide applicability decisions.
The supplied scorer remains provisional and preserves unavailable states.

## Migration and container review

Review migration history and offline SQL inside an isolated synthetic environment:

```bash
python -m alembic history
python -m alembic upgrade head --sql
```

Full upgrade SQL includes migration 001. Review the revision range and schema/search
path with the DBA before execution. Migration 001's destructive downgrade is not
a recovery procedure. Migration 002 refuses destructive rollback with retained data.

```bash
docker build -t neps-data-platform:review .
```

A container build is separate evidence. The current image command has no CLI
subcommand, so the runtime owner must provide a reviewed invocation. No deployment
or scheduler activation follows from a local test pass.
