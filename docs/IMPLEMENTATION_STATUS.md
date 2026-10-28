# Implementation and acceptance status

Reviewed 28 October 2026 for L08 on `de/local-data-engineering-tasks`, after L06 commit `58d2129` plus the recorded working diff. L00 through L07 are DONE_LOCAL. Frank accepted Milestone C and authorised L08 by instructing "proceed to the next". L08 is DONE_INTEGRATION for the disposable synthetic PostgreSQL fixture. L09 actual service acceptance remains NOT_STARTED. No source, backend, ML/AI or deployment acceptance is inferred from a file or interface existing.

## Evidence and status vocabulary

`TASK_ROOT` is `/home/frank/Documents/Syncthing/Obsidian/Work/NEPS/06 Local data engineering tasks`. The source checklist is preserved there as `DATA_ENGINEER_LOCAL_TASKS.md`. Its older DONE claims and examples are historical. The current requirements matrix and this tracker record the reviewed result.

| Evidence | Snapshot and actual scope |
| --- | --- |
| E00 handover | `NDS_Team/PACKAGE_MANIFEST.json` and review files, dated 12 October. All 83 declared path/size/hash entries verified again in L06. Historical ETL 177 tests and 184 subtests, backend 48 tests from an earlier unchanged-component run. No current service acceptance |
| E01 contract | TASK_ROOT/evidence/L01-review.md and L00 reference baseline. Exact historical 223 fields, 18 native dictionary columns, 188 respondent questions and 73 core items |
| E02 scoring | TASK_ROOT/evidence/L02-review.md. Provisional arithmetic, independent golden examples, complete-item behaviour, reversal and exact fractions. No scientific selection approval |
| E03 validation | TASK_ROOT/evidence/L03-review.md. Shared validator and authorised repository/review wiring, age 12 through 24, field-specific missingness/branches and score-envelope checks |
| E04 ingestion/storage | TASK_ROOT/evidence/L04-review.md, code committed as `4ea0a3d`. Full synthetic suite 349 passed and 742 subtests, including 17 PostgreSQL cases, no skips. PostgreSQL 18.6 in a new disposable container. This predates L05 query tests |
| E05 SQL/metrics | TASK_ROOT/evidence/L05-review.md, code committed as `eb7d653`. Local suite 359 passed, 742 subtests and 23 PostgreSQL skips. Six SQL reports VERIFIED_STATIC and six new reporting acceptance cases PENDING_POSTGRESQL |
| E06 handover | TASK_ROOT/evidence/L06-review.md. Manifest reconciliation, source/interface inspection, documented command checks, existing focused synthetic tests and link/inventory verification. No new service/database acceptance |
| E07 final local review | TASK_ROOT/deliverables/LOCAL_COMPLETION_REPORT.md and TASK_ROOT/evidence/L07. Tested L06 commit `58d2129` with a clean tree. Full local suite: 359 passed, 742 subtests passed, 23 expected PostgreSQL skips, no failures/errors or xfails/xpasses. Dependency and 223-field dictionary checks passed. All 99 integrity comparisons and all 83 declared manifest entries verified. Final changes are documentation only. Milestone C was subsequently accepted when Frank instructed "proceed to the next" |
| E08 disposable PostgreSQL | TASK_ROOT/deliverables/POSTGRESQL_ACCEPTANCE_REPORT.md and TASK_ROOT/evidence/L08. Docker 29.9.2, PostgreSQL 18.6, Python 3.14.8. Full run: 384 tests and 742 subtests passed, no failures/errors/skips. Six SQL reports, native/semantic golden persistence, replay/correction, scoped roles/concurrency and nine-table recovery passed. Exact disposable container removed and independently confirmed absent |

DONE_LOCAL means the named local implementation, review, documentation and checks are complete. PENDING_POSTGRESQL means prepared database cases had not executed at the named historical snapshot. VERIFIED_POSTGRESQL and DONE_INTEGRATION here name only the recorded disposable synthetic fixture, not a production or service approval. BLOCKED_OWNER means actual metadata, permission, service or scientific evidence is needed before that operational use. HISTORICAL means a result belongs to its recorded code/environment. DEFERRED_RELEASE means Frank accepted development continuation with named repairs still due before release. These states do not change the formal DE task numbering.

## Component status

| Component | Implementation and local evidence | Integration/service status | Owner input and deferred release condition |
| --- | --- | --- | --- |
| Independent source receipt | [Native client](../etl/extract/production_client.py), [configured runtime](../etl/sync/source_runtime.py), [workflow](../etl/sync/v31_workflow.py), [intake](../etl/intake/v31.py). E04 and focused source/workflow tests. DONE_LOCAL | Actual native API, source ID/events/repeats, export rights and receiving destination are BLOCKED_OWNER under DE04/L09 | Source/REDCap owner and DevOps supply deployed metadata, API contract, DAG/project scope, actual consent/completion evidence and permission references. NDS registration cannot gate authorised source receipt |
| Development baseline shortcut | [ingest_v31_simple.py](../etl/ingest_v31_simple.py). Its baseline fetch/write interface and contract-loader tests exist. Reviewed separately in E04 | Development-only, DEFERRED_RELEASE. Fixed source revision 1 and derived upsert do not establish correction history or supported processing/audit | N01 policy/intake bypass, N02 history loss, N03 schema qualification and N04 namespace collisions remain due before final deployment |
| Provisional scoring | [Scorer](../etl/scoring/v31.py), [algorithm](SCORING_ALGORITHM.md), golden/scoring/Unicode tests. E02/E03/E05. DONE_LOCAL | Scientific use and externally confirmed applicability remain BLOCKED_OWNER. Native Windows CI result was not verified here | Scientific owner supplies applicability, selection/clinical interpretation and any disputed formula evidence. No burden/profile/IWI rules or thresholds invented |
| Validation | [Shared validator](../etl/validation/v31_validator.py), [quality rules](DATA_QUALITY_RULES.md), [tests](../tests/test_validation.py). E03/E05. DONE_LOCAL | Deployed-source comparison remains DE04/L09. Source metadata changes are retained before later reviewed interpretation | Historical dictionary bounds are not automatically cohort selection. No universal 96/98/99 handling; age decision is closed at 12 through 24 |
| Storage and audit | [Nine-table model and lineage](DATA_LINEAGE.md), migrations 001 through 004, role candidate and PostgreSQL tests. E04 executed synthetic constraints/concurrency/recovery | E08 completed 25 PostgreSQL cases, including six reporting and two golden persistence tests. DONE_INTEGRATION for the disposable fixture. Production DBA sign-off is deferred | DBA/DevOps own schema provisioning, privileges, encryption, retention and recovery targets/sign-off. Foreign keys and hashes do not establish current consent or signed audit |
| Separate NDS worker and ID mapping | [DownstreamProcessor](../etl/sync/v31_workflow.py), [ParticipantLinks](../etl/repository/participant_links.py), trusted repository policy interface. Synthetic workflow coverage, E04 | Local libraries implemented. A functioning trusted registration/consent/access adapter and operational worker are BLOCKED_OWNER | Backend/NDS owner must verify distinct IDs, current purpose/action/transfer consent, actor propagation and metadata approval. Historical reprocessing/current-view selection needs an explicit tested rule |
| Queue CLI proposal | This task checkout has no process-queue/requeue/status commands. Cached local main `f2d2a61` contains PR 55; it has not been integrated into this branch | Frank accepted temporary deferral of its known defects. This is not a verified production worker | DevOps owns policy injection, actual grants/applicability, scope/ID wiring, scoped status, actor forwarding, strict approval handling and real-component tests. Merge is not evidence of repair |
| Reporting and quality definitions | [Six SQL reports](sql_queries/README.md), [quality metrics](DATA_QUALITY_METRICS.md), [score metrics](SCORING_METRICS.md), exact local helpers. E05. DONE_LOCAL, VERIFIED_STATIC | All six PostgreSQL reporting cases passed in E08, VERIFIED_POSTGRESQL for synthetic data. Approved real-data aggregates remain L09 | Reporting owner approves population/repeat aggregation and release scope. Alert/disclosure thresholds remain unspecified. Reports do not perform current NDS authorisation |
| Backend research API | Supplied backend patch and partial source deny research access by default, remove signing fallback and disable REDCap-driven registry/consent sync. See [handover index](HANDOVER_INDEX.md) | Historical containment and 48-test report only. No current backend checkout, authenticated endpoint, database integration or deployed API verified | Backend/identity owner provides current commit, API/schema contract, verified identities/roles/consent/country/destination adapters and denial/revocation evidence |
| ML/AI access | Current `analysis/train_random_forest*.py`, risk and trajectory examples import `app.services.redcap_mock`. No trusted repository adapter is imported by the inspected examples | Mock analysis examples are not evidence of authorised warehouse or deployed model service access. Model/service compatibility is BLOCKED_OWNER | ML/AI and backend owners define scoped input schema, authorised access path, version/provenance, approved use and service tests. No model run or analysis-output dataset was opened in L06 |
| Portal/authenticated UI | Supplied `auth.ts` returns null from credentials authorisation. Backend guard defaults to deny | No functioning authenticated UI, browser/UAT or current portal deployment verified | Portal/identity owners provide real sign-in integration and authorised review/export tests. No mock account or authentication bypass is introduced |
| Application image/runtime | Local Python 3.14.8; CI matrices list 3.11 and 3.14. Current [Dockerfile](../Dockerfile) uses Python 3.15 and copies etl/alembic/ops | Python 3.15 application-image and deployment acceptance not established. L08 host tests do not prove image compatibility. SQL files under docs are not copied into that image | DevOps must align/test the selected runtime and package or mount reviewed SQL assets if reports run inside the image. No Dockerfile or deployment configuration changed in L06 |

## Original checklist coverage

These are local supplement IDs, not replacements for formal DE01 through DE05.

| ID | Implementation or reviewed equivalent | Local status and evidence | Integration/owner boundary |
| --- | --- | --- | --- |
| S1.1 | Contract generator, canonical contract and dictionary | DONE_LOCAL E01 | Actual source definitions DE04/L09 |
| S1.2 | Existing provisional scorer and golden tests | DONE_LOCAL E02 | Scientific/applicability approval before use |
| S1.3 | Supported client/intake path and separate shortcut review | DONE_LOCAL E04 | Native API and actual permissions L09; shortcut repairs deferred |
| S1.4 | Nine-table model, constraints, indexes and hash/audit meanings | DONE_LOCAL E04 | L08 disposable fixture accepted in E08; production DBA acceptance remains separate |
| S2.1 | Shared validator in repository and review | DONE_LOCAL E03 | Actual source policy/metadata L09 |
| S2.2 | tests/test_validation.py and existing regression suites | DONE_LOCAL E03/E05 | Synthetic database checks passed E08; actual source/service acceptance remains L09 |
| S2.3 | [Quality rules](DATA_QUALITY_RULES.md) | DONE_LOCAL E03 | Owner-defined scientific selection separate |
| S3.1 | [Scoring algorithm](SCORING_ALGORITHM.md) | DONE_LOCAL E02 | Scientific interpretation separate |
| S3.2 | [Lineage](DATA_LINEAGE.md) | DONE_LOCAL E04 | Deployed route verification L09 |
| S3.3 | [223-field dictionary](DATA_DICTIONARY_V31.md) and reproducible generator | DONE_LOCAL E01 | Deployed drift/translation acceptance L09 |
| S3.4 | Same canonical quality-rules document, no duplicate | DONE_LOCAL E03 | Same as S2.3 |
| S4.1 | Existing scoring, QA, golden and Unicode suites | DONE_LOCAL E02/E05 | Stored golden outputs passed E08; Windows CI not verified here |
| S4.2 | Existing connector/intake/runtime/repository/workflow suites | DONE_LOCAL E04 | Actual source-compatible integration L09 |
| S4.3 | [Integration blueprint](../tests/integration/README.md) | DONE_LOCAL E06, commands checked for this branch | L08 executed; actual service acceptance remains L09. No invented worker CLI or endpoint |
| S5.1 | Six SQL files and bound read-only execution helper | DONE_LOCAL E05, VERIFIED_POSTGRESQL E08 | Actual source/reporting scope remains L09 |
| S5.2 | Country-filtered counts and separate raw/trusted-country distribution | DONE_LOCAL E05, explicit revision/participant grain | Query results verified E08; release scope L09 |
| S6.1 | [Quality metrics](DATA_QUALITY_METRICS.md) and exact local examples | DONE_LOCAL E05 | Synthetic SQL/metrics verified E08; actual aggregates/thresholds L09/owners |
| S6.2 | [Scoring metrics](SCORING_METRICS.md), correlation and composite checks | DONE_LOCAL E05 | Synthetic SQL/metrics verified E08; scientific comparison rules remain owner decisions |
| S7.1 | [All 83 handover entries](HANDOVER_INDEX.md) | DONE_LOCAL E06, path/size/hash and component/status mapping | External snapshots remain external; no service acceptance inferred |
| S7.2 | This tracker and historical-evidence reconciliation | DONE_LOCAL E06 | L07 accepted and L08 disposable scope complete; L09 remains open |

## Reconciliation of earlier DONE claims

The source checklist's baseline ingestion and scoring DONE labels describe an existing development route, not a verified retained-source/permission flow. The supported collector and worker have their separate local evidence. The shortcut still writes revision 1 and can replace a derived result while leaving the earlier source payload. The README's earlier correction-history claim was inaccurate and is corrected in this documentation update.

PostgreSQL has executed local synthetic storage evidence at E04. That does not close production recovery acceptance or execute L05's new reports. Backend API and ML/AI access DONE claims are unsupported as functioning authorised services by this repository and supplied handover. Historical backend tests exercise a containment snapshot; current analysis examples use mock imports. Neither is relabelled as a fresh integration result.

The handover's 177-test evidence is dated 12 October, E04's 349-test PostgreSQL result is dated 27 October before L05, and E05's 359 ordinary tests plus 23 skips is the later SQL-preparation snapshot. These are different scopes, not contradictory totals or interchangeable approvals.

## Formal task and release ownership

The official Obsidian execution status dated 21 October records DE01/DE02 complete, DE03 accepted for continued local development under Frank's instruction, DE04 active and blocked on actual source/permission evidence, and DE05 unstarted. L00-L06 completion does not close DE04 or begin formal DE05. Earlier checkout/remote statements in that historical status are dated snapshots, not today's branch inventory.

Operational runbooks, deployment/scheduling, monitoring/alerts, migration execution, rollback/recovery execution, security/retention approval and production sign-off stay with their assigned owners. L06 adds a [handover checklist and acceptance route](../tests/integration/README.md) and drafts owner requests in TASK_ROOT/decisions/OWNER_INPUTS.md. No owner was contacted automatically.

## Final local review and acceptance gate

L07 rechecked all 20 requirement rows against the original checklist, current implementation, test assertions, documentation and source integrity. The shared validator is wired into repository ingestion and authorised review; score envelopes are checked before V3.1 derived storage. Existing scoring tests use the unchanged independent golden cases. Missingness, partial records, numeric repeat instances and correction history retain their documented boundaries. No new application code, tests, scientific rules or environment settings were needed.

The full ordinary run used the established Python 3.14.8 environment without inherited application settings or a .env file. All 23 skips have the explicit disposable-PostgreSQL prerequisite reason: 17 storage/recovery cases and six reporting cases. These were pending database evidence at the L07 snapshot, not passes. L08 subsequently executed all 25 current PostgreSQL cases with no skips. No Windows CI, application image or actual service acceptance was performed.

Frank accepted the local package and authorised L08 by instructing "proceed to the next" after the completion report. L08 used only the documented new disposable synthetic PostgreSQL fixture. All 384 tests and 742 subtests passed, including six reporting and two new golden persistence/workflow tests. All 99 protected/reference hashes still match. No application code, SQL template, scorer, fixture or migration repair was needed. L09 still needs verified owner inputs. N01-N04, PR 55 queue defects, scientific applicability/selection, production recovery sign-off and the formal DE04 source/permission block remain open in their recorded scopes. No push, merge, deployment or owner contact followed from L07.
