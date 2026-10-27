# NEPS V3.1 data quality rules

L03, 23 October 2026. Frank confirmed an inclusive age range of 12 to 24. This replaces the checklist's proposed 10 to 19 rule. The historical dictionary already declares 12 to 24, so the source contract needs no edit.

The validator reports problems while preserving the original payload, including unknown fields, absent keys, nulls, empty strings and invalid answers. It does not grant source access, consent, destination permission or cohort enrolment. All examples and automated checks use synthetic records.

## Implementation and scope

[etl/validation/v31_validator.py](../etl/validation/v31_validator.py) contains the pure checks. [Repository validation and review](../etl/repository/v31.py) use those checks after the existing permission boundary. The independent source intake remains separate and receives authorised partial or changed exports without an NDS registration dependency.

`validate` returns a copied payload, the analytical answer values, structured issues, per-field states, age eligibility and the existing repository issue representation. Each issue identifies its field, rule ID, severity, observed state and whether that field must be excluded from analytical use. `blocks_field` does not reject a whole receipt. Missing contributors make dependent scores unavailable under the [scoring rules](SCORING_ALGORITHM.md).

`validate_scores` checks the ten-result rational JSON envelope before repository storage. It returns structured issues. An explained unavailable score is informational. Malformed values, invalid ranges or inconsistent dependencies block storage of that score envelope. Generic historical derivations without a score envelope retain their existing behavior.

The rules version is `NEPS-V3.1-validation-1;age-12-24`. No function contacts a service or database. The repository calls the validator within its existing authorised operations.

## Rule register

| ID | Fields and accepted values | State and severity | Effect on downstream use | Authority |
| --- | --- | --- | --- | --- |
| V01 | Every reviewed field; distinguish absent key, explicit null and empty string | absent, null or empty; info | Unavailable field. Preserve explicit null/empty in the answer layer and original presence in raw data. No global mandatory-field rule | Native metadata has blank Required Field flags; complete-item scoring specification |
| V02 | Text fields use native validation type and declared bounds. Transport numbers and dates are strings | invalid; error | Exclude malformed or out-of-range fields | All 18 native dictionary columns |
| V03 | Radio/dropdown choices use that field's exact stored codes. Checkbox values use declared option keys and string 0, 1 or empty | invalid; error | Exclude invalid fields. Do not normalize codes | Native choice lists and reviewed source metadata |
| V04 | Declared semantic labels or explicit missingness evidence for a reviewed field | missing, refused, unknown, not_applicable or invalid; warning, or error for invalid | Exclude unavailable answers. Never convert them to zero | Field-specific labels and separately supplied reason metadata |
| V05 | Branching uses supported equality, and/or and grouping with validated predicate answers. Unsupported validation types also remain unverified | not_applicable or unverified; warning | Exclude inapplicable or unverified answers | Native branching and reviewed metadata |
| V06 | An unreviewed field remains in the copied/raw payload | unknown_field; warning | Exclude from analytical interpretation until metadata review | Independent-source retention policy |
| V07 | Imported, administrative and derived native fields stay outside the respondent answer layer | source_only; info, plus any separate field error | Prevent respondent answers from supplying administrative or calculated results | Contract field roles. attack_freq_missing is the explicit technical-control exception |
| V08 | screen_form_complete accepts string 0, 1 or 2 | invalid; error for any undeclared code | Report invalid completion. Valid completion does not replace answer completeness or grant permission | Historical native completion field |
| V09 | All ten scorer results must satisfy their own ranges, exact JSON types and unavailable-state rules | invalid, outside_score_range, unexplained_unavailable or unavailable_dependency; error. Explained unavailable_score is info | Reject a malformed score envelope. Retain an explained unavailable result as null | L02 scoring review and workflow serialization |
| V10 | Repository processing requires current trusted registry consent, processing permission, action permission, known country and destination transfer permission | Existing AccessDenied boundary for denied or unavailable decisions | Deny the relevant NDS operation. Independent source intake retains its own service-authorisation boundary | Existing PolicyAdapter and approved source/NDS separation |
| V11 | age_years must satisfy the inclusive 12 through 24 age policy | ineligible_age; error when age is invalid or outside range. Missing age remains unknown | Report age_eligible false for invalid/out-of-range age, true for a valid age in range, null for absent/null/empty age | Frank's explicit decision on 23 October 2026 |

V10 reuses the existing repository checks. It is not a second permission system in the pure validator. The tests cover supplied, denied, non-boolean and unavailable synthetic decisions. They do not establish actual service rights.

## Field scales and types

| Fields or summary | Accepted values |
| --- | --- |
| EPI, SBI and BRS core items | Native strings 1 through 5 |
| ESI and K6 core items | Native strings 0 through 4 |
| MSPSS items | Native strings 1 through 7 |
| GSE items | Native strings 1 through 4 |
| country | 1 Ghana, 2 Sierra Leone, 3 Tanzania |
| age_years | Integer string, 12 through 24 |
| household_members and asset_sleeprooms | Integer string, minimum 0, no declared maximum |
| attack_freq | Integer string, minimum 2, no declared maximum, with its native branch and separate control |
| screen_date | Valid calendar date formatted YYYY-MM-DD |
| brs_raw | Numeric string, 1 through 5 |
| mspss_raw | Numeric string, 1 through 7 |
| gse_raw | Numeric string, 10 through 40 |
| k6_raw | Numeric string, 0 through 24 |
| Native normalized index fields | Numeric string, 0 through 100 |

The [full dictionary](DATA_DICTIONARY_V31.md) supplies every other choice list, bound and branch. No universal Likert range applies. A declared maximum remains absent where the dictionary leaves it empty.

Integer validation accepts an optional sign and ASCII digits. It rejects floats, booleans, whitespace, decimal strings and nonnumeric text. Number validation accepts finite ordinary decimal strings, including fractional values. It rejects NaN, Infinity and exponent notation. Date validation checks the exact date format and calendar validity. The validator keeps each original string rather than converting its stored value.

The source transport validator accepts choice strings. The isolated scorer also accepts native integers, as documented in L02. An integer-valued JSON answer is therefore not silently converted into a REDCap string by repository validation.

Administrative and derived source fields receive quality checks, but their values cannot enter the respondent answer layer. Validating a supplied derived field does not adopt it as a trusted calculation or write a replacement value into REDCap.

## Missingness and branches

Raw 96, 98 and 99 are meaningful only where the specific field declares them. None of the 73 core fields declares them. The validator rejects those codes for core items.

Declared labels identify semantic states. The supplied labels Prefer not to answer and Prefer not mean refused. Do not know and Unsure mean unknown. Not applicable, Never attended, Not attending school/training, No such responsibilities, No such family and Not available locally represent structural non-applicability. A reviewed new category with a different label does not inherit these meanings solely because its code is 96, 98 or 99.

Explicit missingness evidence accepts the five supported states for known fields. It takes precedence over an otherwise numeric answer and leaves that raw answer unchanged. Unknown fields or invented reason names in that evidence raise ValueError rather than becoming new conventions.

Branch predicates use validated answers. An invalid, refused, unknown or inapplicable gate does not establish a false condition. Branch chains resolve independently of metadata row order. It leaves the branch unverified. A known false branch marks a present answer not applicable. This prevents unknown schooling or exposure answers from becoming evidence of no exposure.

For repeated attacks, attack_12m must be 2 and attack_freq_missing must be 1 before attack_freq is available. Values 98 and 99 remain real counts when those conditions hold. If the separate control declares unknown or refusal, the count is not interpreted. The validator does not impose an invented upper bound or substitute the control code into the count.

## Completion, age and permission boundaries

| Action | Required evidence and completion behavior |
| --- | --- |
| Independent source receipt | Existing source service authorisation and source identity/metadata context. Partial forms and invalid answers remain retained |
| NDS receipt and validation | Existing current registry, action and destination permissions plus identity/scope checks. Validation reports partial or invalid fields without dropping the raw snapshot |
| Provisional scoring | Valid contributing answers for each score. EPI requires external applicability confirmation. Unavailable contributors make affected scores unavailable. No full-188 requirement |
| Full baseline completion report | Existing review counts require all 188 question values to be valid. A Complete flag alone does not prove this |
| Form status review | 0 means Incomplete, 1 Unverified and 2 Complete and reviewed. None is a consent or transfer permission |
| Age eligibility report | Apply 12 through 24. Unknown age remains unknown, including on partial event/repeat exports. A false age result is not an instruction to erase the source record |
| Cohort selection or clinical use | Separate approved criteria, scientific rules and current rights. L03 does not implement selection or clinical thresholds |
| Export/review/derived storage | Recheck the existing action-specific policy at use time. A valid age, country or score cannot override a denied decision |

L03 preserves provisional scoring and partial-record behavior. Age validation reports eligibility independently from the arithmetic and from permissions. An out-of-range age does not erase core answers or prevent their provisional scores from documenting what the retained source contained. Automated cohort selection remains outside this task.

Country names are display labels. The native field stores strings 1, 2 and 3. A supplied country code does not establish residence, identity, consent or cross-border rights. The existing repository compares any supplied country to the trusted registry scope. Repeated exports may omit country without the validator inserting one. Actual source/destination permission evidence remains DE04/L09 work.

No additional completion gate was introduced. Requiring screen_form_complete of 2 before any partial score could be calculated would change existing behavior and needs a separate operational decision. EPI/cost applicability across schooling contexts and scientific approval for selection also remain separate owner decisions. L03 retains the existing fail-closed applicability rule.

## Score output checks

The ten required results are EPI, ESI, SBI, MHDI, K6_total, BRS_100, MSPSS_100, GSE_100, PFI and NSES. All normalized values use inclusive bounds 0 through 100. K6_total uses 0 through 24 and must be an integer.

Available values must be exact JSON objects with integer numerator and positive integer denominator. Booleans are not integers for this check. Each available value must have an empty issues list. A null value requires at least one valid field/state reason. Empty reasons, malformed fractions, unknown result names and missing required results fail validation.

The allowed reason states match the scorer's missing, refused, unknown, not_applicable, invalid and applicability_unverified states. K6_total and MHDI must be unavailable together. A numeric PFI cannot depend on an unavailable protective subscale. A numeric NSES cannot depend on an unavailable main index. The validator does not invent a replacement score or round an out-of-range value into bounds.

Repository storage rejects a score envelope with a blocking V09 issue before a derived row is written. An explained null remains a valid research result with limited score availability. PostgreSQL acceptance remains L08 work.

## Verification

[tests/test_validation.py](../tests/test_validation.py) covers approved age boundaries and malformed types, real field scales, declared and explicit missingness, branching, open attack counts, country representation, form codes, partial forms, dates/numbers, extra fields, payload copies, score ranges and persistence rejection. It also exercises authorised review, denied/unverified policies and independent source receipt.

Authorised review recomputes quality and completion from the retained payload and metadata using the current rules. It does not rewrite source history or stored validation layers.

The existing contract, scoring, repository, intake, source evolution and workflow suites remain regression checks. Current field definitions, core membership, golden expectations and scientific formulas remain unchanged. The L03 evidence records the selected checkout, exact commands, environment, results and source hashes.
