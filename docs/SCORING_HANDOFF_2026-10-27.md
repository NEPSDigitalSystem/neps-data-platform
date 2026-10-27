# Analyst scoring handoff, 27 October 2026

Branch approved by Frank: `fix/v31-unicode-scoring-regression`.
Starting commit: `42f6e635d7df9ed867327776fe345d9d5cfc94d4` on
`de/local-data-engineering-tasks`.

The source is the two-page "NEPS NDS V3.1 Engineering Handoff: Unicode
Regression Tests" PDF from the analyst. Its SHA-256 is
`a21bc3319d3513871e6cdc6e13b2df108e8587c25e9f5fcd4d89d06c9d9a705d`.
The original remains in Frank's NEPS Obsidian `Data Analyst request` folder.

## End-of-day steps and completion gates

Complete each step before moving to the next. Elapsed times are working estimates.

1. Confirm scope and branch, about 15 minutes. Record the clean starting commit,
   original PDF hash, scorer hash, contract hash and golden-fixture hash. Complete
   when the agreed branch exists and existing engineering work is preserved.
2. Reproduce and compare, about 30 minutes. Run the existing contract and scoring
   suites. Reproduce the reported UTF-8 bytes decoded as Windows CP1252. Complete
   when the corrupted direction fails verification and explicit UTF-8 succeeds.
3. Close regression gaps, about 45 minutes. Exercise the actual test-suite setup
   calls under a CP1252 default and an unrelated working directory. Check all five
   reversal examples for each reversed item. Complete when these tests fail if
   the explicit UTF-8 reads regress. Preserve scientific rules and fixture bytes.
4. Run verification, about 45 minutes. Execute Unicode, scoring, contract, source
   integrity, relocation and packaged-contract tests. Run the full ordinary suite,
   then the existing disposable PostgreSQL procedure if available. Save commands,
   exit codes, JUnit results and logs. Record skips and blockers separately.
5. Review against the original PDF, about 30 minutes. Fill every acceptance row
   below with executed evidence. Inspect the complete diff and protected hashes.
   Complete when the report distinguishes local CP1252 coverage, native Windows
   coverage, analyst acceptance and scientific approval.
6. Prepare delivery, about 15 minutes. Create a local commit and a reviewable
   patch. Give the analyst the exact commands and request the NSES discrepancy
   details. Decide whether to share the patch for Windows verification before a
   push or push the tested branch to run the new Windows CI. Merge and deployment
   require separate review and are outside this handoff.

## Starting position

The starting branch already has explicit UTF-8 contract and golden reads in both
scoring suites. The golden fixture is packaged at
`tests/fixtures/SCORING_GOLDEN.json`. Contract suites use
`tests/fixtures/v31_reference`, and the portability suite checks the supplied
source hashes and regeneration after relocation. These fixes are inherited, not
new production-code changes made for this handoff.

The baseline focused run passed 39 tests and 679 subtests. The work adds a direct
regression for the analyst's reported failure and cross-platform CI evidence.

## Verification against the original PDF

| PDF requirement | Evidence or completion gate | Status |
| --- | --- | --- |
| Page 1, engineering action 1, explicit UTF-8 | Actual scoring and contract suite setup runs under a mocked CP1252 default | PASS locally; four in-memory removal probes detected the regression |
| Page 1, action 2, preserve Unicode minus and match scorer | Assert U+2212 direction and exact BRS reverse membership; reproduce rejection of corrupted direction | PASS |
| Page 1, action 3, resolve golden path | Existing repo-local fixture loads from an unrelated working directory; original bytes match source manifest | PASS |
| Page 1, action 4, Unicode and wider tests | Focused and full test logs with exit codes and JUnit reports | PASS locally; Windows not run; 17 database checks skipped |
| Page 1, action 5, document actual results | Final results and remaining constraints below | PASS |
| Page 1, acceptance, 1->5 through 5->1 | Fifteen explicit response/item examples through the real scorer | PASS |
| Page 1, acceptance, no Unicode verification error | Actual existing scoring suites pass under CP1252 default | PASS locally; native Windows confirmation pending |
| Page 1, acceptance, unchanged golden outputs | All 24 independent cases pass; fixture hash stays unchanged | PASS against supplied provisional fixture; scientific approval remains separate |
| Page 2, source documents missing at recorded paths | Regenerate contract from bundled references and relocated references with verified hashes | PASS |
| Page 2, NSES discrepancy | Obtain both formulas, source references and a worked example; measurement owner decides | Open scientific input |

Native Windows execution is separate from deterministic CP1252 reproduction on
Linux. The dedicated workflow tests Windows and Linux on Python 3.11 and 3.14
with Python UTF-8 mode disabled. It can execute only after remote publication.
No native Windows result or analyst sign-off is claimed by a local Linux pass.

## Analyst retest commands

From a checkout of the agreed branch or an applied review patch, use a clean
environment. In PowerShell:

```powershell
py -3.14 -m venv .venv-handoff
.\.venv-handoff\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
$env:PYTHONUTF8 = "0"
.\.venv-handoff\Scripts\python.exe -c "import locale, platform, sys; print(sys.version); print(platform.platform()); print(locale.getencoding()); print('utf8_mode', sys.flags.utf8_mode)"
.\.venv-handoff\Scripts\python.exe -m pytest tests/test_v31_unicode_regression.py tests/test_v31_scoring.py tests/test_v31_scoring_qa.py tests/test_v31_contract.py tests/test_v31_contract_qa.py tests/test_contract_portability.py tests/test_ingest_v31_contract.py -q -ra --junitxml=v31-windows-results.xml
```

Use a development environment without live source or database credentials.
Return the commit or patch hash, runtime output, pytest output and JUnit report.
The CP1252 regression still runs if that Windows installation defaults to UTF-8.

Equivalent local commands:

```bash
.venv/bin/python -m pip check
.venv/bin/python -m pytest tests/test_v31_unicode_regression.py tests/test_v31_scoring.py tests/test_v31_scoring_qa.py tests/test_v31_contract.py tests/test_v31_contract_qa.py tests/test_contract_portability.py tests/test_ingest_v31_contract.py -q -ra --junitxml=/tmp/v31-scoring-focused.xml
.venv/bin/python -m pytest tests -q -ra --junitxml=/tmp/v31-scoring-full.xml
.venv/bin/python scripts/verify_postgresql.py --evidence-dir /tmp/v31-scoring-postgresql-new
git diff --check
```

The PostgreSQL output directory must not exist before the command starts.
The script creates and removes its own labelled disposable synthetic database.

## Results and decisions

Local verification completed on 27 October 2026 with Python 3.14.8 on Linux.
This section records verification completed before the first remote push. Frank
subsequently approved publishing the tested branch to obtain native Windows CI.
Merge remains pending review of that result. The attempted push was rejected
by GitHub with "Invalid username or token". No branch publication or native
Windows CI run has occurred. Restore Git authentication or install and connect
the GitHub integration with repository access, then retry the approved push.

| Check | Actual result |
| --- | --- |
| Existing scoring and contract baseline | 39 passed, 679 subtests passed |
| Focused Unicode, scoring, contract, integrity and packaging | 64 passed, 679 subtests passed, zero failed or skipped |
| Full ordinary suite | 319 passed, 17 skipped, 742 subtests passed, zero failures |
| New regression coverage | 21 cases, including fifteen explicit reversal examples |
| Removal of UTF-8 in memory | All four scoring/contract suite regressions detected |
| Dependencies | pip check passed |
| Workflow syntax | YAML parsed locally; native Windows CI not yet executed |
| Protected bytes | Scorer, contract, core manifest, golden fixture, source manifest and original PDF unchanged |
| Disposable PostgreSQL | Blocked, Docker daemon unavailable; the 17 skips are not passes |

The golden fixture SHA-256 remains
`ca258870f4649b0a246f479f072037920715465efb905e5dba6955ad3437a7e6`.

[Machine-readable results](evidence/scoring-handoff-2026-10-27/summary.json),
[baseline log](evidence/scoring-handoff-2026-10-27/baseline.log),
[focused log](evidence/scoring-handoff-2026-10-27/focused.log),
[full log](evidence/scoring-handoff-2026-10-27/full.log),
[starting hashes](evidence/scoring-handoff-2026-10-27/initial-state.json),
[protected-file check](evidence/scoring-handoff-2026-10-27/protected-files.json),
and [removal probes](evidence/scoring-handoff-2026-10-27/mutation-check.json)
are retained with this branch. Detailed JUnit files remain in
`/tmp/neps-scoring-handoff-20261027` and will also be included in the local review
bundle. Test runs removed inherited source, NEPS, database and warehouse settings.
The focused run disabled Python UTF-8 mode as well as exercising CP1252 directly.

The Docker CLI is present, but the daemon check reported no usable
`/var/run/docker.sock`. No database container, migration or live database action
ran. Run the documented disposable verification on a Docker-enabled machine to
obtain database evidence. No host service was started for this task.

The NSES formula is unchanged. The analyst's PDF does not supply the conflicting
expressions or a worked example. Ask for both formulas, document versions and page
references. The scientific or measurement owner must decide the rule before any
formula or independent expected result changes. Matching the supplied provisional
golden cases does not grant scientific approval.

## Decisions for Frank

1. Delivery route. The strict pre-push option is to give the analyst the local
   patch or Git bundle and get a Windows result before publishing. The faster
   shared-review option is to publish this locally verified branch and let its
   dedicated Windows CI run before any merge. The second option needs agreement
   because native Windows verification would happen after the push. Frank approved the shared-review option on 27 October 2026. Publish the
   locally verified branch, review all Windows and Linux CI results, and keep
   merge pending that review.
2. NSES scope. Frank approved keeping this encoding/path handoff separate,
   retaining the provisional formula, and requesting the missing discrepancy
   evidence from the analyst and scientific owner. No formula or golden expected
   value change is authorised by this engineering handoff.

## Draft reply to the analyst

> I have checked your handoff against the current V3.1 development version. The
> UTF-8 reads and repository-local fixture paths are present. I added a regression
> that reproduces the CP1252 corruption and verifies the actual test loaders under
> that default, including all five reversal values for each reversed BRS item.
>
> The focused run passed 64 tests and 679 subtests. The full local suite passed
> 319 tests and 742 subtests, with 17 database checks skipped because the disposable
> PostgreSQL environment was unavailable. The original scoring rules and golden
> fixture bytes are unchanged.
>
> Native Windows verification and your acceptance are still pending. Please run
> the supplied Windows commands against the same version and return the output,
> JUnit file, Python version and commit or patch hash. Please also send both NSES
> formulas, their document/page references and a worked example so the measurement
> owner can confirm the intended rule. I have not changed the formula.
