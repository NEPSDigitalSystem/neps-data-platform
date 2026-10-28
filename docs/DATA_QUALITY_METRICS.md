# Data quality metrics

L05 defines local reporting conventions against the retained V3.1 model. These measures describe observed data and processing coverage. In-range answers do not establish factual accuracy, measurement equivalence, scientific eligibility or permission to use the data.

## Scope and reproducibility

Report project, destination, country scope, event/repeat filters, observation grain, source contract version/hash, reviewed source metadata version/hash, validator version and report code commit. Latest source identity/destination is the default observation grain. Keep historical revision counts separate. Participant reporting deduplicates native source IDs or separate NDS IDs explicitly. Research-only reports cannot measure completeness among contacts still waiting in intake.

The [SQL README](sql_queries/README.md) defines namespace filters and read-only execution. [quality_metrics.py](../etl/analytics/quality_metrics.py) gives pure local examples using the current historical contract and shared validator. It does not accept a deployed metadata approval or establish that the historical contract matches a live project. Recompute under the approved source metadata and record the rules version before operational comparison. SQL reads persisted legacy issues; it does not reconstruct every current validator state or prove that an old validation layer used today's rules.

Every proportion returns null when its denominator is zero. Report its numerator and denominator beside the fraction. Do not substitute zero for unmeasurable coverage. Aggregation uses pooled numerators/denominators for the same metric stratum, not an unweighted mean of percentages with different denominators. Do not pool different contracts, validation rules or permission scopes.

## Completeness

The fixed historical respondent set has 188 questions. Administrative fields, source IDs, observed completion flags and historical derived/calculated fields are outside that respondent denominator. The technical missingness control can affect interpretation without becoming an extra respondent question.

| Measure | Numerator | Denominator | Exclusions and interpretation |
| --- | --- | --- | --- |
| Recorded completeness | Respondent fields whose keys exist and whose values are neither JSON null nor empty string | 188 per latest observation | Counts observed refused/unknown/invalid codes and any other present JSON value as recorded. It does not imply usability. Nested checkbox representations follow the retained JSON representation |
| Usable completeness | Respondent fields with current validator state valid and confirmed applicable branch | Respondent fields with branch true and no declared not_applicable state | Exclude branch-false and declared not_applicable fields. Exclude and separately count unknown applicability. Missing, null, empty, refused, unknown, invalid and unverified answers in known-applicable fields remain in the denominator |
| Applicability coverage | Respondent fields with resolved applicability, including excluded fields | 188 | Report confirmed applicable, excluded and applicability-unverified counts separately. A high conditional usable percentage can coexist with poor applicability coverage |

The helper forms branch predicates only from validated valid fields. An invalid/refused/unknown parent cannot establish applicability. It evaluates branches for absent children too, so a proven inapplicable absent child is not counted as a missing required answer. These conventions are reporting measures, not changes to source receipt or scientific selection.

Worked example. Three unconditional respondent answers are recorded: willing_24m is declared refusal `99`, k6_1 is valid `0`, k6_2 is undeclared `99`. Recorded completeness is 3/188. Exactly one of these is usable. The helper also reports the full applicable denominator and unresolved branches, rather than using three as the usable-completeness denominator. A separate age answer does not increase the 188-question count.

## Validity and coding consistency

| Measure | Numerator | Denominator | Missingness and limits |
| --- | --- | --- | --- |
| Respondent field validity | Applicable respondent fields with state valid | Valid plus invalid applicable respondent fields | Excludes missing, null, empty, refused, unknown, not_applicable and unverified states. Publish evaluated count and applicability coverage. Covers type and declared-code/bound checks, not truth |
| Numeric/date validity | Valid fields declared as integer, number or date_ymd text, with confirmed applicable branch | Valid plus invalid such fields | Includes relevant administrative fields such as age_years, separately from respondent completeness. Parse/type and declared-bound failures are invalid. Do not invent an absent upper bound |
| Radio/dropdown coding consistency | Nonblank observed applicable radio/dropdown answers whose exact string code appears in that field's declared choices | All nonblank observed applicable radio/dropdown answers, excluding declared not_applicable fields | Declared refusal/unknown codes can be coding-consistent while unusable. Booleans, numeric JSON codes and undeclared strings fail exact-code checks. Checkbox coding needs its separate multi-option validator and is outside this radio/dropdown denominator |

The three-answer example has field validity 1/2 and coding consistency 2/3. With only age_years `12`, numeric/date validity is 1/1 while recorded respondent completeness remains 0/188. Age `25` yields numeric/date validity 0/1. The approved age bounds are 12 through 24 inclusive. These statements do not create cohort selection criteria.

Treat `98`, `99` and `96` by each dictionary row's labels and branching. No universal replacement with NULL is allowed. For example k6_2 `99` is invalid, while willing_24m `99` is a declared refusal. An open attack count of `99` can be a real count when the separate control and branch permit it. Raw answers remain unchanged.

For [null_analysis.sql](sql_queries/null_analysis.sql), absence of a JSON key, JSON null and empty string are separate raw categories. SQL NULL from a missing joined validation layer is a processing gap. SQL NULL metadata hashes and provenance links are not questionnaire missing answers. Literal numeric zero is observed data.

## Scoring coverage

For each of ten score outputs and each exact algorithm/metadata-policy/source-definition stratum, use latest research observations as the denominator. The numerator is observations with exactly one matching derivation and a valid available output. Report the disjoint unscored, ambiguous, malformed, unavailable and out_of_range counts beside available. Their sum equals the denominator. Do not join all derivations and count joined rows as observations.

A source with two competing matching derivations contributes one ambiguous observation. A source with an unavailable subscale contributes one unavailable observation, not zero score. Coverage of research observations is distinct from coverage among all raw intake contacts. Actual collection, mapping, processing and availability funnels require their own approved denominators and source visibility evidence. See [scoring metrics](SCORING_METRICS.md).

## Contract conformance and provenance coverage

Use `contract_version_check.sql` to report the count of latest rows with an independently expected contract version and canonical hash divided by latest rows in the scope. The query groups historical and latest counts separately. A changed source metadata snapshot is not automatically a contract violation. It needs the metadata-version review documented in the lineage.

Report latest observations with retained adapted metadata hash and with intake revision link, each over all latest observations. Missing values are unknown provenance, not proof of deletion or unauthorised receipt. A stored matching hash is a declaration in the row; this SQL query does not independently recompute canonical JSON hashes or validate all 223 metadata rows. Count unknown/unreviewed source fields separately under the applicable metadata policy. Preserve them in raw storage.

Full contract conformance needs the approved metadata snapshot, source identity/context, field validation and supported score-envelope checks. It cannot be reduced to "all 188 answers are nonempty" or a matching version string. Missing responses can remain contract-compatible partial observations. The pure helper reports current-rule field quality only, not a whole-row certification.

## Country consistency and permission evidence

Country consistency compares a recognised raw string code with the stored trusted country label. Its match numerator is latest observations with matching recognised raw and stored labels. Its denominator is observations with both recognised representations. Report omitted, unmapped and mismatched categories separately. A missing repeat-country answer is omitted, not inconsistent. Multiple raw categories can contain the same participant, so grouped participant counts are not additive.

Permission coverage is a different measure. Its numerator requires an independently evidenced current permission decision for the project, purpose, actor, country and destination at the relevant time. Its denominator is observations/actions requiring that decision. A missing decision is unverified. Country-name equality, a configured flag or a stored NDS ID is insufficient. The SQL library deliberately does not manufacture a permission rate from source columns.

## Acceptance and ownership

L05 local examples and L08 synthetic PostgreSQL execution are complete. On 28 October 2026, all six reporting tests passed within the 384-test full suite, with 742 subtests and no skips. The fixture includes corrections, repeats, country changes, unknown codes, missingness, unmapped IDs, multiple calculation versions and missing metadata. All nine storage counts/hashes match before and after the six reports. In the six selected latest observations, age is present and nonempty in 3/6, two of those three ages meet the reviewed range, EPI is available in 2/6, and 7/8 retained revisions match the expected contract. These are explicit synthetic denominators, not real participant metrics or policy thresholds. Actual source completeness and release scope remain L09.

No operational alert thresholds, scientific interpretation or publication cutoffs are assigned. An owner and approved thresholds are required before adding alerts. No such input is needed to finish these local definitions.
