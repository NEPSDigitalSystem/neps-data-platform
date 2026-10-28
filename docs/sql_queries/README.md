# Scoped PostgreSQL reports

L05 prepares these queries for L08. Status is VERIFIED_STATIC and PENDING_POSTGRESQL. SQLAlchemy compilation checks parameter names and prepares SQL, but does not validate PostgreSQL execution or query results. The six acceptance tests in `tests/postgresql/test_reporting_queries.py` remain pending until the disposable fixture runs.

These reports read the research source, validated and derived tables described in [the lineage](../DATA_LINEAGE.md). They do not count all independently retained intake records. An unregistered source contact can remain in intake without a research row. No report here grants access, checks current NDS consent or substitutes for approved country-transfer scope. Use a database role and dataset explicitly authorised for the report.

## Reporting grain

The native source identity is project, source participant ID, event, repeat instrument and repeat instance. Destination scopes storage separately. Rank revisions within identity/destination before filtering country, so an older revision in a formerly reported country cannot become current. Historical revision counts include all matching retained revisions. All other record counts use only rank 1.

A native participant count is distinct native source IDs within the selected project and destination. An NDS participant count is distinct nonempty mapped NDS IDs. Neither count equates a source event/repeat row with a person. Different native IDs can map to one NDS participant, and the same participant can appear in several events or country/version groups. Do not add grouped participant counts as though they were disjoint.

Project and destination are mandatory exact values. Country, event, instrument and instance can each be a specific string or `None` for all values within an already authorised scope. An empty event/instrument/instance string selects the classic or non-repeating empty component. `None` has a different meaning. `country=None` requires approval for the combined scope; it does not authorise a cross-country release.

## Files, parameters and outputs

Every query uses the common scope above. All runtime values are bound by SQLAlchemy. The schema placeholder is replaced only after the shared schema validator accepts the name and PostgreSQL's identifier preparer quotes it.

| Query | Additional required parameters | Output and grain |
| --- | --- | --- |
| `data_counts.sql` | None | One row with retained revisions, latest records, native source participants, mapped NDS participants and unmapped latest records. Empty scope returns zeros |
| `scoring_distribution.sql` | Exact `algorithm_version` and `metadata_policy_version` | One row per contract hash, source metadata hash, stored country and each of ten score names. Counts by score state, mean, median, sample SD, min and max. Empty scope returns no rows |
| `null_analysis.sql` | `field` | One row per contract hash, raw presence state and stored validation diagnostic, with record count. Does not expose field values |
| `country_distribution.sql` | None | One row per contract hash, stored country scope, raw country category and consistency category, with latest-record and participant counts |
| `contract_version_check.sql` | `expected_contract_version`, `expected_contract_hash` | One row per stored contract version/hash pair, with expected-pair match, retained/latest counts, source-version-label count, metadata-snapshot count and latest missing-provenance counts |
| `sample_records.sql` | `dataset_class` is `synthetic` or `approved_deidentified` | At most `sample_limit` rows, default 5, allowed 1 through 20. Only ordinal, revision, contract version/hash, payload key count and presence flags for metadata, intake link and NDS mapping |

`sample_records` emits no source/NDS IDs, raw answers, dates, event/repeat names or free text. Its ordinal is local to the selected result, not a participant pseudonym. The dataset-class parameter records the caller's scope assertion; it does not verify de-identification or permission. Aggregate reports also need disclosure review before release. No small-cell publication threshold is invented here.

The country report uses research `country` as the stored trusted scope label. Raw country values `1`, `2` and `3` are classified only when their JSON type is string. Missing keys, JSON nulls and empty strings remain separate. Other values become `UNMAPPED`, without returning their contents. An unexpected stored scope label becomes `UNMAPPED_SCOPE`. Matching country names or codes does not prove transfer permission. Omitted repeat-country answers are not filled.

The missingness report distinguishes `absent`, `json_null`, `empty` and `present`. Numeric zero and literal strings such as `98` and `99` are present, not SQL NULL. Their field-specific meaning comes from validation metadata. A missing joined validation row is `validation_layer_missing`. Payload columns are SQL NOT NULL, but can contain JSON null. The schema expects record objects; malformed whole-payload shape needs separate investigation. Metadata hashes and intake links can be SQL NULL and are counted separately by the provenance report.

## Selecting scores

Each latest source row contributes one observation per score name. Join derived results only after selecting latest source revisions. Select candidates by the exact algorithm and metadata policy versions. A source row with zero matching results is unscored; with more than one it is ambiguous. The query does not choose the lexicographically first result or invent a derivation timestamp. Its internal minimum ID is used only when the candidate count is exactly one.

Candidate score states are mutually exclusive: unscored, ambiguous, malformed, unavailable, out_of_range and valid. Available values require exact integer numerator/positive integer denominator JSON, an empty issue list, matching result/source contract hash, and valid output bounds. Unavailable values require null and nonempty structured reasons. This is per-output screening, not the full validator's cross-output dependency or independent composite check. Legacy scalar/float shortcut results cannot pass as supported score envelopes. Statistics use only valid values; every other state remains counted.

Grouping by source contract hash and adapted metadata hash prevents mixing those source definitions. Exact algorithm version includes the scorer/contract fingerprint; metadata policy version is explicit. The per-source `calculation_version` also includes a score-input hash, so it is not one shared cohort version and should not be used as a cohort filter. Multiple results under the selected algorithm/policy need a separately approved selection rule or corrected provenance before analysis.

PostgreSQL NUMERIC division, mean and sample SD are decimal approximations. Median uses `percentile_cont` with double precision, about 15 significant digits. Stored rational values remain untouched. Retain full returned precision for calculations, round display only, and report six decimal places by default. See [scoring metrics](../SCORING_METRICS.md) for exact local examples and comparisons.

## Read-only execution

Do not substitute parameters with shell interpolation, Python string formatting or direct SQL editing. Use [query_library.py](../../etl/analytics/query_library.py). It accepts only the six named files, rejects invalid schemas/scopes, binds values, requires PostgreSQL, and opens a repeatable-read read-only transaction with a 15-second statement timeout and a 3-second lock timeout. Separate calls create separate snapshots. Use a quiesced synthetic fixture for cross-report conservation checks, or an owner-approved consistent reporting snapshot for related production reports.

The following is a template for an approved environment after PostgreSQL acceptance. The URL file belongs to that environment. The placeholder project/destination and algorithm must be replaced with the exact approved values. No token or password goes into command arguments or chat.

```bash
cd /home/frank/Documents/GitHub/neps-data-platform
.venv/bin/python - <<'PY'
import json
from pathlib import Path
from sqlalchemy import create_engine
from etl.analytics.query_library import run_query
from etl.load.db import database_url

url = Path('/path/to/approved-read-only-database-url').read_text().strip()
engine = create_engine(database_url(url), hide_parameters=True, echo=False)
try:
    rows = run_query(engine, 'data_counts', 'approved_schema',
                     project='APPROVED-PROJECT', destination='APPROVED-DESTINATION',
                     country='Ghana')
    print(json.dumps(rows, default=str, indent=2))
finally:
    engine.dispose()
PY
```

For the other named queries, supply their additional parameters from the table. Expected contract hashes are canonical JSON digests, not file byte hashes. Use a known approved version/hash pair, rather than deriving the expected value from the same database rows being checked. The reports do not migrate schemas or call REDCap/NDS.

## Acceptance commands

Run local preparation/math tests now:

```bash
env -i PATH="$PATH" LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest \
  tests/test_query_library.py tests/test_quality_metrics.py -q
```

In L08, run the existing helper against a new evidence directory. It discovers the new PostgreSQL tests and runs them before removing its generated container:

```bash
env -i PATH="$PATH" LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python scripts/verify_postgresql.py \
  --evidence-dir /tmp/neps-l08-NEW
```

The fixture skips only when no PostgreSQL opt-in is supplied. Incomplete, unapproved, wrong-backend and unsafe opt-ins fail. No SQLite substitute is accepted. L05 prepares independent expected values for all six queries, rank-before-country filtering, corrections, repeats, unavailable/ambiguous/malformed scores, malicious bound values, empty scopes and a nine-table before/after conservation check. Prepared expectations are not execution evidence.
