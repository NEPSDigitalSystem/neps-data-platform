# Scoring metrics

These L05 definitions describe the existing provisional outputs. They do not approve clinical thresholds, selection criteria, country comparisons or EPI applicability. [The algorithm](SCORING_ALGORITHM.md) remains unchanged.

## Observation and version selection

One observation is the latest source revision for native project, participant, event, repeat instrument, repeat instance and storage destination. A participant can have several observations. Default summaries are observation-weighted, not participant-weighted. A participant-level analysis needs an explicit event/repeat or aggregation rule from its scientific owner.

Select exact algorithm and metadata policy versions. Keep source contract hash, adapted metadata hash and stored country separate. Rank source revisions before joining derived results. A source with no matching derivation is unscored; more than one matching derivation is ambiguous. Neither enters numeric summaries. Do not choose a derivation by UUID or presume a timestamp that the table does not contain. The algorithm version identifies scorer/contract code; the calculation version additionally includes the individual score-input hash.

The [SQL distribution query](sql_queries/scoring_distribution.sql) reports ten outputs and all source observations, including unavailable/unscored cases. It screens each output's shape, reasons, contract hash and bounds. The shared score validator additionally checks the whole ten-output envelope and dependency availability. Independent arithmetic checks are a separate acceptance step. An available individual output does not certify that every output in the same legacy envelope is valid.

## Available-value summaries

K6_total must be an integer from 0 through 24. EPI, ESI, SBI, MHDI, BRS_100, MSPSS_100, GSE_100, PFI and NSES are normalized from 0 through 100. Values outside their output range are reported separately and excluded from summaries. Do not apply a 0 through 100 test to raw native questionnaire items, whose scales differ.

| Statistic | Definition | Empty or small sample |
| --- | --- | --- |
| Available count n | Number of unique source observations with one matching valid available output | Zero is retained |
| Mean | Sum of available values divided by n | Null when n is zero |
| Median | Sorted middle value for odd n, arithmetic mean of the two middle values for even n | Null when n is zero |
| Sample SD | Square root of sum of squared deviations from the mean divided by n minus 1 | Null when n is less than 2. Constant values with n at least 2 give zero |
| Minimum and maximum | Extremes of available values | Null when n is zero |

The SQL query uses PostgreSQL `stddev_samp`, not population SD. Always label the convention. Missingness is excluded from numeric summaries, never imputed to zero. The mean of available observations can be biased by missingness; these reports do not correct selection or missing-data mechanisms.

Worked examples. Available values 10, 20 and 30 have n 3, mean 20, median 20 and sample SD 10. With values 10 and 30, sample SD is sqrt(200). With one available value 4, mean and median are 4 and sample SD is null. With no available values all numeric summaries are null.

## Precision

The supported stored envelope represents each available score by integer numerator and positive integer denominator. Keep that representation for exact arithmetic checks. [quality_metrics.py](../etl/analytics/quality_metrics.py) accepts exact integers/Fractions for its local statistics and rejects implicit float/text conversion. It returns exact mean/median and 28-digit Decimal sample SD and Pearson correlation.

PostgreSQL NUMERIC division and aggregates are decimal approximations. `percentile_cont` median uses double precision, about 15 significant digits. Do not round individual observations before aggregation. Retain returned precision and display six decimal places by default. For comparison with exact independently computed values use absolute tolerance 0.000001 in normalized score units for SQL means, medians, SD and correlations. This is a reporting implementation tolerance, not a scientific threshold or permission to alter source data. Exact composite checks use equality of Fractions and no tolerance.

## Correlations

For each requested pair of subscales, retain observations with both valid available outputs under the same source/version/scope rules. Join within the same source UUID; never join separate repeat/event rows by participant alone. Use pairwise-complete samples, with no imputation. Report each pair's n, excluded count, exact version/scope and Pearson r. Different pairs can have different samples, so a correlation matrix must carry its pair counts.

Pearson r is the sum of centered cross-products divided by the square root of the product of the two centered sums of squares. Return null with reason insufficient_pairs for fewer than two pairs. Return null with reason constant_input if either sum of squares is zero. At least two nonconstant pairs can produce a descriptive r; no significance test or minimum research sample size is invented. A two-pair result of 1 is not evidence of a reliable association.

Examples. Pairs 1/2 and 2/4 give r 1. Pairs 1/4 and 2/2 give r -1. A missing partner excludes the whole pair. Pairs 1/4 and 1/2 give null because the first variable is constant. The pure helper verifies these examples. The six SQL files do not include a correlation report; calculate approved pairs from authorised score envelopes using these conventions or a separately reviewed read-only query.

## Missingness and coverage

For each subscale, the denominator is every selected latest source observation, not only scored rows. Report available, unavailable, unscored, ambiguous, malformed and out_of_range counts and proportions. Their sum equals the observation denominator. A zero denominator gives null proportions, with the count still zero. Unavailable outputs need explicit reasons. Malformed or unexplained null envelopes do not become ordinary missing scores.

For reason-specific prevalence, count each observation at most once per subscale/reason, even if several contributing items share that reason. The numerator is unavailable observations carrying the reason; the denominator is all selected observations for that subscale. Reasons can overlap, so reason-specific proportions need not sum to the unavailable proportion. Keep missing, refused, unknown, not_applicable, invalid and applicability_unverified separate. Do not infer EPI applicability from observed answers or substitute raw 96/98/99 across fields.

## Independent composite verification

For a valid available set of component outputs, independently compute:

```text
NSES = 3/10 * EPI + 1/4 * ESI + 1/5 * SBI
       + 1/5 * MHDI + 1/20 * (100 - PFI)
```

Compare exact Fractions to the stored NSES. If any component is unavailable, expected NSES is unavailable. A stored numeric NSES in that case is a dependency mismatch. A complete component set with stored NSES unavailable is also a mismatch needing explanation. Report matched available, matched unavailable, mismatched and malformed counts separately, with tested envelope count and algorithm version. Do not calculate over an ambiguous derivation.

EPI 20, ESI 40, SBI 60, MHDI 80 and PFI 100 produce NSES 44. Stored 45 fails. Missing EPI implies unavailable NSES, not zero. [The independent helper](../etl/analytics/quality_metrics.py) and local tests cover both directions of missingness and the interior arithmetic. Apply the full score validator before decoding and checking a stored envelope. Arithmetic agreement alone does not establish scientific approval or validate original item responses.

## Acceptance state

L05's pure examples and static SQL preparation are local evidence. The six PostgreSQL acceptance tests remain PENDING_POSTGRESQL until L08. They include latest-versus-historical corrections, repeated source observations, a second algorithm/policy, two competing derivations, unavailable and malformed scores, a range failure and singleton/empty samples. The fixture expects available EPI values 10 and 30, with mean/median 20 and sample SD sqrt(200), while retaining all six Ghana observations in the coverage denominator.

L08 executes the full suite with the existing disposable PostgreSQL helper. L09 verifies actual source and approved reporting scope. Scientific owners retain responsibility for cohort interpretation, operational applicability, comparison design and any alert or release thresholds.
