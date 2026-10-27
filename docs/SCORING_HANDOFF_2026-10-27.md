# V3.1 Unicode scoring regression checks

The scoring contract stores the reverse direction as `6−raw`, with the
Unicode minus U+2212. Decoding its UTF-8 bytes as Windows CP1252 corrupts that
text, and the scorer correctly rejects the unverified direction. Contract and
golden-fixture reads must specify `encoding="utf-8"`.

## Files and regression coverage

- `etl/contracts/data_contract_v31.json` contains the scoring contract.
- `tests/fixtures/SCORING_GOLDEN.json` contains 24 independent reference cases.
- `tests/fixtures/v31_reference` contains the contract's reference sources.
- `tests/test_v31_unicode_regression.py` reproduces CP1252 corruption, checks the
  actual scoring and contract loaders under that default, and runs all five
  reversal examples for each of `brs_02`, `brs_04` and `brs_06`.

The golden-fixture SHA-256 is
`ca258870f4649b0a246f479f072037920715465efb905e5dba6955ad3437a7e6`.
The scorer, contract, core manifest and independent fixture bytes are unchanged.

## Run the focused checks

Install `requirements.txt` and `requirements-dev.txt` in a clean Python
environment. Run this command from the repository root:

```text
python -m pytest tests/test_v31_unicode_regression.py tests/test_v31_scoring.py tests/test_v31_scoring_qa.py tests/test_v31_contract.py tests/test_v31_contract_qa.py tests/test_contract_portability.py tests/test_ingest_v31_contract.py -q -ra --junitxml=v31-scoring-results.xml
```

For native Windows testing, disable Python UTF-8 mode before invoking Python.
In PowerShell:

```powershell
$env:PYTHONUTF8 = "0"
python -c "import locale, platform, sys; print(sys.version); print(platform.platform()); print(locale.getencoding()); print('utf8_mode', sys.flags.utf8_mode)"
```

Then run the focused pytest command above. Return the tested commit, runtime
output, pytest output and JUnit report when reporting a failure. The CP1252
regression runs even when the machine's actual default encoding is UTF-8.

The `V3.1 scoring regression` workflow runs these checks on Windows and Linux
with Python 3.11 and 3.14. Native Windows CI results remain pending review.

## Verification on 27 October 2026

| Check | Result |
| --- | --- |
| Focused Unicode, scoring, contract, source-integrity and packaging tests | 64 passed, 679 subtests passed |
| Full suite with disposable PostgreSQL 18.6 | 336 passed, 742 subtests passed, no failures or skips |
| Removal of explicit UTF-8 from the loaders in memory | Regression detected in all four scoring and contract suites |
| Golden cases, source hashes and contract regeneration after relocation | Passed |
| PostgreSQL recovery and disposable-container removal | Verified |

Run the existing database verification on a Docker-enabled machine with a new
output directory:

```text
python scripts/verify_postgresql.py --evidence-dir PATH_TO_NEW_EVIDENCE_DIRECTORY
```

The script creates its own synthetic database, runs the full suite, saves the
test and recovery evidence, and removes the container. A skipped database test
does not count as a database pass.

## NSES clarification

The provisional NSES formula and independent expected results remain unchanged.
Resolving the reported formula discrepancy requires both expressions, source
document versions and page references, and a worked example. The scientific or
measurement owner must approve any formula change. Passing engineering tests
does not grant scientific approval or establish analyst acceptance.
