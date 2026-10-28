# Integration acceptance blueprint

Updated in L08 on 28 October 2026 for `de/local-data-engineering-tasks`, based on L06 commit `58d2129` and the recorded working diff. Frank accepted L07 and authorised L08 by instructing "proceed to the next". L08 disposable PostgreSQL acceptance is complete. L09 has not started. See [implementation status](../../docs/IMPLEMENTATION_STATUS.md), [handover index](../../docs/HANDOVER_INDEX.md) and [lineage](../../docs/DATA_LINEAGE.md).

## Acceptance stages and prerequisites

| Stage | Preconditions | Evidence needed to finish |
| --- | --- | --- |
| Local synthetic checks | Correct task branch, original .venv, no real environment file, unchanged references, synthetic fixtures and injected test policies | Actual command, interpreter/dependency versions, HEAD/diff, test output and integrity checks. L07 accepted at Milestone C |
| L08 disposable PostgreSQL | Local package accepted, Docker available, pinned PostgreSQL image usable, a new output directory, no existing database supplied | Full ordinary and PostgreSQL suites with zero skips, all six SQL results versus independent expectations, concurrency/roles/recovery and cleanup records. DONE_INTEGRATION for the disposable synthetic fixture, 384 tests and 742 subtests passed, no skips |
| L09 native source and NDS service | Owner-approved endpoint/project/DAG/destination references, actual metadata/ID/events/repeats, consent/completion evidence, authorised synthetic or explicitly approved test scope, real downstream adapters/API contract | Verified native export compatibility, receipt independent of NDS, denied/unavailable/correction/retry cases, actual mapping and purpose access, joint authorised service evidence |

All local tasks stay on the same open task branch. Inspect changes and preserve other work before running checks. The following first block reads state only:

```bash
cd '/home/frank/Documents/GitHub/neps-data-platform' || exit 1
test "$(git branch --show-current)" = 'de/local-data-engineering-tasks' || exit 1
git status --short --branch
.venv/bin/python --version
.venv/bin/python -m pip check
```

The current local environment is Python 3.14.8. CI lists Python 3.11/3.14, while the application Dockerfile uses 3.15. Test the chosen deployment runtime separately. The current image does not copy docs/sql_queries, so packaging/mounting those assets must be resolved if reporting runs there. Do not use a successful host-based PostgreSQL test as image acceptance.

## Local command set

Run from the repository root. The clean process environment excludes inherited source/database configuration; no .env file is present in the recorded checkout. If one is added later, inspect its use before testing rather than reading or printing secret contents. Current fixtures supply their own synthetic settings.

```bash
env -i PATH="$PATH" LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m scripts.build_v31_dictionary --check

env -i PATH="$PATH" LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest \
  tests/test_v31_workflow.py tests/test_v31_independent_workflow_qa.py \
  tests/test_v31_source_runtime.py tests/test_v31_source_runtime_qa.py \
  tests/test_v31_source_intake_qa.py tests/test_v31_schema_evolution.py \
  tests/test_v31_connector.py tests/test_v31_connector_qa.py -q

env -i PATH="$PATH" LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest \
  tests/test_quality_metrics.py tests/test_query_library.py -q

env -i PATH="$PATH" LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest \
  tests/postgresql --collect-only -q
```

The dictionary command uses Python module invocation so repository imports resolve. The older direct `python scripts/build_v31_dictionary.py` invocation needs an explicit import path and is not the command used here. Collection of PostgreSQL cases runs no database fixture. Current collection has 25 cases, including six reporting tests and two golden persistence/workflow tests. It is not query execution.

For an ordinary regression without PostgreSQL opt-in, choose a new evidence path and retain the output and exit code:

```bash
env -i PATH="$PATH" LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest \
  tests -q --tb=short --junitxml=/tmp/neps-l07-results-NEW.xml
```

E05 and L07 recorded 359 ordinary tests, 742 subtests and 23 PostgreSQL skips before L08 added two database tests. A current ordinary run without opt-in would leave 25 PostgreSQL cases pending. L08's actual full PostgreSQL run passed 384 tests and 742 subtests with no skips. Missing or incomplete opt-in must not be mistaken for a database pass. Unexpected skips/failures block the applicable stage.

## Expected synthetic source-to-result sequence

The existing `tests/test_v31_workflow.py` fixture creates a fresh in-memory store, enables SQLite foreign keys, seeds an explicitly synthetic separate NDS mapping and injects test-only source/NDS/applicability policies. Its native API transport is mocked POST metadata/records/metadata. These policies do not establish actual permissions.

For a fresh synthetic identity, fixed source-version label and unchanged metadata, inspect counts before any explicit review/export call adds audit actions:

| Point | Intake raw/head/pending | Research source/validated/derived | Audit and score expectation |
| --- | --- | --- | --- |
| After collector only | 1 / 1 / 1 pending | 0 / 0 / 0 | One received audit, native ID and observed metadata retained, no NDS callback |
| After separately authorised worker | 1 / 1 / 1 acknowledged | 1 / 1 / 1 | Intake received/claimed/ack, research ingest/derive. Synthetic maximum-protective-resource row has exact NSES 0 |
| Unchanged full replay and worker retry | Counts unchanged | Counts unchanged | No new raw revision or score. Returned received count is exported rows, not newly inserted revisions |
| Corrected answer and worker | 2 / 1 / 2 acknowledged entries | 2 / 2 / 2 | Earlier raw answer and result retained. New intake/research revision and score provenance. Research revision counts are not participant counts |

The supported result envelope has ten outputs with exact numerator/denominator values or explained nulls. It includes algorithm/contract/input hashes and explicit intake revision, native metadata digest, NDS ID, mapping version and metadata policy version. Research raw payload retains the source ID, event/repeat values and JSON missingness. Numeric repeat instance 2 remains an integer in the payload while identity uses string "2". The score cannot establish consent or scientific selection.

The full-188 fixture is a known synthetic arithmetic pattern, not a clinical profile. Partial progression cases have 73, 78, 100, 152 and 188 respondent fields without inventing missing answers. Administrative form flags do not replace item completeness. Explicit review/export rechecks current permissions and adds its own audit entries, so include those actions when comparing audit totals.

## Failure, retry and source-evolution cases

| Case | Required assertion | Existing local evidence or later gate |
| --- | --- | --- |
| No NDS registration, mapping or downstream consent | Authorised raw receipt succeeds; processing stays queued/restricted; no fabricated ID/consent | Independent workflow, intake and repository suites; actual adapters L09 |
| HTTP timeout/429/502/503/504, denied export, redirect, SSL or malformed JSON | Bounded transient retries only; current permission rechecked; failure output has no body/token/participant data | Connector suites; actual TLS/network contract L09 |
| Invalid later ID/event/repeat context | No earlier receipt from that malformed export batch | Source runtime and independent workflow tests |
| Storage failure after some receipts | Earlier committed records survive; no absence markers until all receipts finish; safe replay deduplicates unchanged rows | Interrupted-batch test in independent workflow QA; PostgreSQL transaction tests L08 |
| Added/renamed fields, changed codes/types/branches/API metadata | All authorised raw data and observed metadata retained; unreviewed interpretation deferred | Source schema-evolution suite, owner metadata approval L09 |
| Metadata changes during export | Refresh bounded pre/post snapshots or fail safely, rather than associate answers with a different definition | Schema-evolution tests |
| Removed credential visibility, then restoration | Presence audit markers only; no raw deletion or inferred withdrawal | Intake reconciliation tests |
| Source correction, repeated event/instrument/instance, integer repeat | Distinct source context, revision history and preserved native values; no participant double-count in reports | Workflow/runtime tests and prepared SQL cases |
| NDS outage/withdrawal or changed destination permission | Raw source retained; separate processing/review/export denies or defers with current scope | Workflow/repository suites; live policy L09 |
| Worker lease expiry, stale ack, retry and authorised requeue | One current claim, stale completion rejected, attempts/audit retained, raw unchanged | Intake suites and PostgreSQL concurrency tests |
| Reviewed later metadata version | Process a retained deferred receipt without reimport; retain metadata/mapping/score provenance | Schema-evolution tests. Operational historical-reprocessing/current-view selection still needs an explicit tested adapter rule |

## L08 execution and retained result

The existing helper creates a uniquely named `neps-de03-synthetic-*` container, pins the PostgreSQL image, publishes only to loopback, uses tmpfs rather than a permanent data volume and creates its own private temporary URL file. No existing URL/token is supplied. Docker access is the prerequisite, not a reason to substitute SQLite for PostgreSQL.

```bash
env -i PATH="$PATH" LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python scripts/verify_postgresql.py \
  --evidence-dir /tmp/neps-l08-NEW
```

L08 used /tmp/neps-l08-20261028/run-01, retained under TASK_ROOT/evidence/L08/run-01. Docker 29.9.2 created PostgreSQL 18.6 from the pinned image. Full regression passed 384 tests and 742 subtests with no skips in 34.88 seconds reported by pytest. Recovery counts/hashes matched across all nine tables. The helper removed neps-de03-synthetic-1b45a1646eaf, and an independent inspect confirmed its absence. The reporting.json, golden-native.json and golden-semantic.json records retain assertions and aggregate results without raw responses. For another run, choose a new evidence directory. The helper refuses to overwrite one. Its single pytest invocation runs all ordinary tests and `tests/postgresql`, including `test_reporting_queries.py`, while the synthetic container still exists. The reporting tests execute every SQL file through the read-only helper, compare independent expectations and compare all nine storage counts/hashes before and after. A separate test attempts a write and requires the read-only transaction to reject it. Do not run SQL manually against a removed fixture or count static compilation as a database pass.

The prepared reporting seed has 11 research source/validated rows and 10 derivations. The selected Ghana/project/destination scope expects 8 retained revisions, 6 latest observations, 5 native participants, 4 mapped NDS participants and 1 unmapped latest record. An older Ghana revision for F cannot reappear as latest after its correction moves to Tanzania. EPI values 10 and 30 give mean/median 20 and sample SD sqrt(200); unavailable, unscored, ambiguous and malformed observations remain in the coverage counts. See the [SQL README](../../docs/sql_queries/README.md) for all categories, empty/singleton results and exact version filters.

Storage acceptance includes real migrations/constraints/schema, concurrent duplicate/corrected receipts, scoped claims, stale/expired leases, append-only role restrictions and guarded migration rollback. The recovery test seeds all nine tables, dumps and restores into another generated database and compares counts/digests. Its initial intake raw/head/pending/audit counts are 3/2/3/6, with one participant link and 1/1/1/2 research source/validated/derived/audit rows. Compare the emitted recovery record, not production RPO/RTO targets that have not been agreed.

Require zero failures and zero skips, the test run record and JUnit, recovery JSON and container cleanup JSON. The helper removes only its own generated container in finally, even on failure. Review cleanup output and investigate a failed removal using the recorded exact container identity. Do not issue a broad Docker purge. Retain failure/setup logs and fix failed assertions before declaring acceptance. Production DBA sign-off and recovery targets remain separate from this local rehearsal.

## Native service boundary and environment handover

Do not run a live collector from this document before L09 inputs are complete. The operator command names below were checked against this branch's parser. They are invocation references, not L06 execution or permission:

```text
python -m etl.main collect-source
python -m etl.main sync --full
```

Native collection uses authorised HTTPS POST metadata/record exports with raw values and full project reconciliation. The bundled custom mock GET routes and development baseline GET are different contracts. A test of the custom service cannot certify the native collector. Retain actual deployed dictionary, ID field, events, repeats, source consent/completion fields and project/DAG restrictions before enabling collection. Do not infer them from the proposed 224-row candidate or historic study_id notes.

There is no production worker, mapping or requeue command in this task checkout. Supply the actual approved NDS service contract and instantiate the existing downstream interfaces with trusted adapters. Do not copy an always-true test policy into runtime. The separately merged PR 55 command proposal has accepted deferred defects and is not a verified adapter. No endpoint for a new backend or ML service is invented here.

| Handover item | Required non-secret evidence | Responsible owner and current state |
| --- | --- | --- |
| Source reference | Approved environment, HTTPS endpoint reference, source project/DAG scope and native/custom API contract | Source/REDCap owner and DevOps, pending L09 |
| Identity and context | Actual native record-ID field/issuer, classic/longitudinal configuration, event unique names and repeat instrument/instance shape | Source owner, pending L09 |
| Metadata and consent/completion | Full deployed metadata snapshot/hash and real exported fields/branch configuration, including approved offline/mobile behaviour | Source/scientific owners, pending L09. Proposed candidate is not evidence |
| Secret references | Mounted file reference, provisioning owner and rotation/access procedure reference | DevOps. Record references only, never contents, passwords, tokens or signed export URLs |
| Destination and schema | Approved storage destination, application schema, database service reference, migration history and scoped role grants | DBA/DevOps, actual environment pending |
| Source/destination rights | Current export-service, project/DAG/country/purpose/destination approval references | Source, destination and governance owners, pending |
| NDS mapping and permissions | Distinct issued ID, mapping version, current registration/purpose consent, action/actor and transfer checks, denial/revocation results | Backend/NDS identity owner, pending |
| Scientific rule | Applicability, formula/selection evidence, permitted aggregates and participant/repeat interpretation | Scientific owner, pending before those uses |
| Backend/ML/portal | Current component commits, request/response schemas and auth/denial/retry contracts, approved joint test scope | Respective service owners, pending. Historical partial snapshots cannot prove deployed access |
| Deployment/runtime | Python image compatibility, SQL-asset packaging if used, scheduler retry/polling references and release evidence | DevOps, pending; no settings changed here |
| Operational acceptance | Backup/recovery/retention/security/monitoring runbook references, agreed targets and named approvers | Existing DBA/DevOps/governance owners, pending production acceptance |

Draft requests are in the task folder's decisions/OWNER_INPUTS.md. No messages are sent automatically. L07 was accepted and L08 completed for the disposable synthetic fixture. L09 remains NOT_STARTED and needs the verified source, service and permission inputs above before execution. Production approval and deferred shortcut/queue repairs remain separate.
