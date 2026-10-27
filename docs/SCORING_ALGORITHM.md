# NEPS V3.1 provisional scoring algorithm

Reviewed for L02 on 22 October 2026. The existing scorer agrees with the supplied V3.1 rules and the 24 independent golden cases. This establishes local computational agreement. Scientific approval for selection, clinical interpretation and comparisons across schooling contexts remains outstanding.

The implementation is [etl/scoring/v31.py](../etl/scoring/v31.py). It calculates ten named results from the exact 73 screening items. It does not need all 188 respondent questions to calculate a screening score. Extra questions never enter a score denominator.

## Source authority and scope

The supplied measurement and analysis manual, section 3, and the scoring rules dated 10 October 2026, sections 1 through 4, specify the arithmetic below. The latter document, section 9, permits development testing with synthetic records. Its section 2 explicitly reserves scientific approval of the corrected composite before selection use.

The [verified contract](../etl/contracts/data_contract_v31.json), [core manifest](../etl/contracts/core73_manifest_v31.json) and [data dictionary](DATA_DICTIONARY_V31.md) retain exact field membership, choices, analytical groups and BRS direction. The [golden fixture](../tests/fixtures/SCORING_GOLDEN.json) was authored independently of the scorer and remains unchanged.

| Source | SHA256 |
| --- | --- |
| Measurement and analysis manual, NEPS_Generic_Master_CRF_V3_1_Analysis_and_Scoring_Manual.docx | `d7af31f477cc3fc44273c7b69bfa40d0f14eae1959b5abd9695a60dd6ab71796` |
| Scoring rules and operational decisions, 10 October 2026 | `047dabc6a71e3f56bec958925d6524a4671e274fe0324b5debb961e527700400` |
| Independent SCORING_GOLDEN.json | `ca258870f4649b0a246f479f072037920715465efb905e5dba6955ad3437a7e6` |

The manuals remain in the NEPS handover's `NDS_Team/reference_sources` folder. The L02 evidence contains numbered text extracts and exact source paths. Local source agreement does not verify deployed REDCap metadata, permissions or participant eligibility.

## Input contract

`Scorer(contract).score(responses, missingness=..., epi_applicable=..., source_context=...)` returns a `ScoringResult`. Each score has a `value` and item-level `issues`.

Core answers must be a native integer code or its exact decimal string, such as `2` or `"2"`. A boolean, float, padded string, `"01"` or `"1.0"` is invalid. The scorer checks each field's own choices. It does not trim, round or coerce malformed answers. Repository validation may impose a stricter transport requirement, such as REDCap strings.

| Fields | Count | Allowed integer codes | Direction before aggregation |
| --- | --- | --- | --- |
| EPI | 10 | 1 through 5 | Higher pressure |
| ESI | 10 | 0 through 4 | Higher hardship |
| SBI | 19 | 1 through 5 | Higher stigma |
| K6 | 6 | 0 through 4 | Higher distress |
| BRS | 6 | 1 through 5 | Reverse brs_02, brs_04, brs_06; higher adjusted value means more resilience |
| MSPSS | 12 | 1 through 7 | Higher support |
| GSE | 10 | 1 through 4 | Higher self-efficacy |

The constructor verifies 73 unique core fields, dictionary row hashes, supported group counts, radio choices, scale bounds and the exact three reversal entries. It is not a substitute for reviewing a changed scientific contract. The contract and manifest regression checks establish the supplied field membership.

## Educational pressure

Each EPI dimension has two required items.

| Dimension | Exact fields |
| --- | --- |
| Expectations | epi_expectations_1, epi_expectations_2 |
| Failure | epi_failure_1, epi_failure_2 |
| Caregivers | epi_caregivers_1, epi_caregivers_2 |
| Future | epi_future_1, epi_future_2 |
| Progress | epi_progress_1, epi_progress_2 |

For each dimension, calculate its mean, subtract 1, divide by 4 and multiply by 100. EPI is the arithmetic mean of those five normalized dimension scores. All ten valid answers and explicit external applicability confirmation are required.

A dimension with answers 1 and 4 has mean 2.5 and normalized score 37.5. If the other four dimensions are zero, EPI is 7.5. Supplementary examination and teacher questions are outside this calculation.

## Economic stress

Each ESI dimension has two required items.

| Dimension | Exact fields |
| --- | --- |
| Financial strain | esi_finstrain_1, esi_finstrain_2 |
| Food | esi_food_1, esi_food_2 |
| Education costs | esi_educost_1, esi_educost_2 |
| Materials | esi_materials_1, esi_materials_2 |
| Transport | esi_transport_1, esi_transport_2 |

Divide each dimension mean by 4 and multiply by 100. ESI is the arithmetic mean of the five normalized dimension scores. All ten valid answers are required. Zero is a valid response and can produce a true zero score. Household asset indicators do not enter ESI.

Answers 0 and 3 give a dimension score of 37.5. If the other four dimensions are zero, ESI is 7.5.

## Stigma burden

Each SBI dimension receives one quarter of the index, regardless of its number of items.

| Dimension | Fields | Required count |
| --- | --- | --- |
| Anticipated stigma from loved ones | sbi_loved_1 through sbi_loved_8 | 8 |
| Anticipated community stigma | sbi_comm_1 through sbi_comm_4 | 4 |
| Anticipated self-stigma | sbi_self_1 through sbi_self_4 | 4 |
| Help-seeking self-stigma | sbi_help_1 through sbi_help_3 | 3 |

For each dimension, subtract 1 from the mean, divide by 4 and multiply by 100. SBI is the arithmetic mean of those four scores. All 19 valid answers are required. Experienced-stigma follow-ups remain separate.

If all eight loved-ones responses are 5 and all other SBI responses are 1, the dimension scores are 100, 0, 0 and 0. SBI is 25. Pooling the 19 items would incorrectly produce about 42.1053.

## Distress and K6

Sum `k6_1` through `k6_6` to obtain `K6_total`. Its range is 0 through 24. Calculate MHDI as `100 * K6_total / 24`. All six valid answers are required for either result.

For responses 0, 1, 2, 3, 4 and 1, K6_total is 11 and MHDI is exactly 275/6, about 45.8333. K6_total is a raw total with its own range. It must not be validated as a generic normalized score. Neither output assigns a diagnosis or clinical category.

## Protective factors

PFI averages three normalized questionnaire scores. Each receives one third of PFI, regardless of its item count.

| Component | Fields | Raw summary | Normalization |
| --- | --- | --- | --- |
| BRS_100 | brs_01 through brs_06 | Adjusted six-item mean, 1 through 5 | Subtract 1 from the mean, divide by 4, multiply by 100 |
| MSPSS_100 | mspss_01 through mspss_12 | Twelve-item mean, 1 through 7 | Subtract 1 from the mean, divide by 6, multiply by 100 |
| GSE_100 | gse_01 through gse_10 | Ten-item sum, 10 through 40 | Subtract 10 from the sum, divide by 30, multiply by 100 |

Before taking the BRS mean, replace only `brs_02`, `brs_04` and `brs_06` with `6 - raw`. Keep the original source answers unchanged. Validate availability and code membership before reversal. A missing response never becomes 6 or zero.

The scorer's mean-based GSE expression is algebraically equivalent to the sum-based source definition. Ten answers summing to 23 produce GSE_100 of exactly 130/3.

Calculate PFI as the sum of BRS_100, MSPSS_100 and GSE_100 divided by 3. Each subscale needs all its own items. PFI needs all 28. A complete protective subscale remains available when a different subscale is incomplete.

Raw BRS answers 1, 1, 1, 1, 1 and 1 become 1, 5, 1, 5, 1 and 5. Their adjusted mean is 3, so BRS_100 is 50. Uniform raw 5 also gives 50. For BRS_100 of 100, MSPSS_100 of 0 and GSE_100 of 50, PFI is 50. Pooling the 28 raw answers would change the intended weights and mix incompatible scales.

## Composite score

```text
NSES = [30*EPI + 25*ESI + 20*SBI + 20*MHDI + 5*{100-PFI}] / 100
```

Higher EPI, ESI, SBI and MHDI increase NSES. Higher PFI decreases NSES. The protective contribution is 5% of the protective deficit, `100 - PFI`. The theoretical NSES range is 0 through 100.

All five indices must be available. The scorer does not drop an unavailable component, change weights or impute an answer. The standalone `composite` helper only performs bounded component arithmetic. It does not check raw completeness, applicability or permissions.

| Component-only example | Score | Weighted contribution |
| --- | --- | --- |
| EPI | 80 | 24 |
| ESI | 60 | 15 |
| SBI | 40 | 8 |
| MHDI | 20 | 4 |
| PFI | 70 | 1.5 |
| NSES | | 52.5 |

This is the manual's component arithmetic example. MHDI of 20 cannot arise from six integer K6 answers because it would require a raw total of 4.8. Do not present this example as a complete 73-answer record.

The independent fixture also supplies a realizable full-response example with EPI, ESI, SBI and MHDI of 50, BRS_100 and MSPSS_100 of 50, and GSE_100 of 0. PFI is exactly 100/3. NSES is exactly 305/6, about 50.8333.

At the endpoints, burden indices all zero with PFI of 100 give NSES of zero. Burden indices all 100 with PFI of zero give NSES of 100. Reaching those PFI endpoints requires the correct BRS reversal pattern.

## Unavailable answers and applicability

| Input condition | Scorer state | Result |
| --- | --- | --- |
| Key absent, explicit null or empty string | missing | Affected scores unavailable |
| Undeclared code or malformed type | invalid | Affected scores unavailable |
| Explicit semantic reason missing, refused, unknown, not_applicable or invalid | Supplied state | Takes precedence over a numeric raw answer; affected scores unavailable |
| EPI applicability not confirmed | applicability_unverified on EPI | EPI and NSES unavailable |

The `missingness` mapping accepts only core field names and the five listed semantic states. Unsupported fields or states raise `ValueError`. These reasons are separate verified metadata, not new REDCap response codes. None of the 73 fields declares raw 96, 98 or 99. Those raw values are invalid. Analytical notes mentioning structural 96 do not authorize inserting it into native core answers.

Every unavailable score has `value=None` plus its item issues. An unavailable item prevents its dimension or subscale, its parent index and NSES from being calculated. Unaffected indices remain available. K6 absence affects both K6_total and MHDI. An unavailable BRS item affects BRS_100 and PFI while complete MSPSS_100 and GSE_100 remain available. The scorer does not expose the intermediate EPI, ESI or SBI dimension scores as separate result entries.

`epi_applicable` must be a boolean and defaults to false. False means the scorer lacks confirmation. It does not distinguish confirmed structural inapplicability from an unknown context. True requires external evidence. The scorer does not derive it from age, country, schooling labels, source completion or consent. Item-level `not_applicable` can retain a more specific reason.

The manuals leave education and cost comparability for participants outside formal schooling unresolved. Valid ESI codes allow arithmetic in this pure scorer; that does not establish applicability. A trusted caller must supply any confirmed item-level reasons. Local tests set applicability only for synthetic examples and do not define an operational schooling policy.

Source key presence and original values remain intact. Absent, null and empty answers all prevent the same affected score, but their source hashes differ. A complete 73-item screen can coexist with an incomplete 188-item questionnaire. Score availability does not establish baseline completion, eligibility, consent or permission to process.

## Result names and ranges

| Returned name | Inclusive range when available | Related native derived field |
| --- | --- | --- |
| EPI | 0 through 100 | epi_100 |
| ESI | 0 through 100 | esi_100 |
| SBI | 0 through 100 | sbi_100 |
| MHDI | 0 through 100 | mhdi_100 |
| K6_total | 0 through 24, integer | k6_raw |
| BRS_100 | 0 through 100 | No dedicated normalized native field |
| MSPSS_100 | 0 through 100 | No dedicated normalized native field |
| GSE_100 | 0 through 100 | No dedicated normalized native field |
| PFI | 0 through 100 | pfi_100 |
| NSES | 0 through 100 | nses_100 |

These are semantic correspondences, not automatic field renames or REDCap writes. The scorer does not emit native `brs_raw`, `mspss_raw` or `gse_raw`. Their declared summaries are respectively an adjusted mean from 1 through 5, a mean from 1 through 7 and a sum from 10 through 40.

The scorer returns per-score issues rather than a single native `screen_score_status` code. Mapping simultaneous issue types into that native field would need an explicit precedence rule. It also does not emit age_band, IWI, stressor burden count, burden class, stressor profile, clinical categories or cohort selection. Those definitions and approvals remain separate work.

## Precision and storage

Every available value is a Python `Fraction`. Normalization, subscale averages and the composite retain exact rational arithmetic. There is no intermediate rounding or clipping. A caller may format a decimal for display, but the formatted value must not become an input to a later calculation.

The reviewed [workflow serializer](../etl/sync/v31_workflow.py) stores a fraction as JSON with integer `numerator` and `denominator`, preserving exact values such as 305/6. It stores unavailable values as JSON null and issues as field/state records. Algorithm, contract and source hashes and the provisional flag accompany the score set. L02 tests the JSON round trip. PostgreSQL storage and recovery acceptance remain L08 work.

## Version and provenance

The human-readable algorithm prefix is `NEPS-V3.1-provisional-corrected-1;complete-items-only;equal-dimensions`. The complete `algorithm_version` appends a digest of the canonical contract hash and the SHA256 of the scorer file bytes. A source edit changes that version even if it only changes a comment. L02 leaves the scorer bytes unchanged.

Canonical hashing serializes JSON with sorted keys, no separator whitespace and UTF-8 characters preserved. The hashes have different purposes.

| Field | Hashed input |
| --- | --- |
| contract_sha256 | Complete supplied contract, including its version and source metadata |
| algorithm_version suffix | contract hash and scorer file hash |
| source_sha256 | Present core response keys and exact values, explicit missingness mapping, applicability boolean and source_context |

Dictionary and reference source hashes remain inside the contract. `source_context` must carry the trusted identity, event, repeat and revision context needed by a caller. The downstream workflow supplies source and intake revision IDs, source version, mapped NDS ID and metadata policy version, and records further receipt metadata alongside the result.

The scorer source hash covers its core scoring inputs. It is not a hash of the complete raw payload. Extra or non-core answers do not change it. The intake/repository retain separate full-payload and revision provenance. String and integer representations hash differently even when they produce equal scores. Source corrections, semantic reasons, applicability and context changes also change the source hash. Reordering JSON keys does not.

The downstream calculation key combines algorithm_version and source_sha256. A changed contract or code version can therefore produce a new calculation even when source answers are unchanged. L02 verifies these distinctions without editing the scientific contract or scorer.

## Verification and remaining decisions

The [primary scoring tests](../tests/test_v31_scoring.py) retain all 24 golden cases and check omission of each required item, exact affected-score propagation, unaffected results and each composite coefficient. The [QA suite](../tests/test_v31_scoring_qa.py) adds independently calculated lower, interior and upper examples for all 18 groups. It checks all native values of each reversed BRS item, adjacent invalid codes and raw 96/98/99 for every core field, semantic states, input preservation, precision and provenance.

Run the scoring checks from the repository with the existing venv and no `.env` file.

```bash
env -i PATH="$PATH" LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  .venv/bin/python -m pytest tests/test_v31_scoring.py tests/test_v31_scoring_qa.py -q -ra
```

L02 needs no new scientific choice to retain this documented provisional behavior. Formal composite approval for selection, structural applicability and comparisons by schooling status remain scientific owner decisions. Burden/profile indicators, IWI coefficients and selection rules need their own definitions. No local arithmetic pass closes those decisions or the deployed-source and PostgreSQL checks.
