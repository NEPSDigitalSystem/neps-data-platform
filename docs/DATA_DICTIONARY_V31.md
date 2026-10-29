# V3.1 data dictionary

This document records all 223 fields in the supplied historical V3.1 dictionary. It preserves field types, labels, codes, validation, branching and analytical notes. It is not a statement of deployed REDCap configuration or scientific approval.

## Sources and regeneration

Contract version: `NEPS-V3.1-local-evidence-3-independent-redcap-intake`.

Canonical contract SHA256: `69b9b8b62e4909ea834f22f033ace3f399b8c92a3458a3ff965d61657ba66b97`.

Dictionary metadata SHA256: `46d6873ade73bcaecee90d440db918b0da8ef7f337be318d5b1e03aeb614e7eb`.

The [saved contract](../etl/contracts/data_contract_v31.json) reconciles the 18-column dictionary, mapping workbook, ordered map and proposed country displays. The [reference inventory](../tests/fixtures/v31_sources.json) records the original file hashes. Source paths below are relative to `tests/fixtures/v31_reference`.

Regenerate or verify this file from the repository root. The command refuses to generate if the reconciled sources differ from the saved contract or the retained reference/golden hashes fail.

```bash
.venv/bin/python -m scripts.build_v31_dictionary
.venv/bin/python -m scripts.build_v31_dictionary --check
```

| Source | Archive member | SHA256 |
| --- | --- | --- |
| NEPS Master CRF V3.1- REDCap Data Dictionary/NEPS_Master_CRF_V3_1_REDCap_18_Column_Data_Dictionary.csv |  | 81e392fb4a3a72c82bb935a998b0dfcc2bf15f6080e8da4d27d12c8483e13ea7 |
| NEPS_V3_1_Mapping_Workbook.xlsx |  | c783dadb4a5f7ec4a05debc9deed4766f11910d6c8028dbd4e9bb29bc016cf01 |
| NEPS Master CRF V3.1/NEPS_V3_1_Priority_Order_REDCap_Build_Package.zip |  | 159a57ac76a43f7b5390e2b3dc8325213151ce40d7501b22645937d400a1e327 |
| NEPS Master CRF V3.1- Country Adaptations/Education_Level_Crosswalk_Country_Display.csv |  | 24787d021f0e8db7dbb4b3988350f0e613b69510e0485f12fde3f527c93a3ddc |
| NEPS Master CRF V3.1- Country Adaptations/NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |  | 0ea594aa961be3226571e07788cd6013b59a44ce1a08cc25bf9c8b613ea65e62 |
| NEPS Master CRF V3.1/NEPS_V3_1_Priority_Order_REDCap_Build_Package.zip | NEPS_V3_1_Ordered_Item_to_Analysis_Map.csv | 53c0a21a6795e689de4bf43e8335fcefc33cee122592cf1058a3224d52f9998f |

## Field counts

| Classification | Fields |
| --- | --- |
| Imported / system field | 11 |
| System output / registry action | 7 |
| Respondent question | 188 |
| Technical response-format control | 1 |
| Derived variable / system output | 16 |

There are 188 respondent questions and 35 other fields. The ordered map has 222 rows. The only dictionary-only row is `attack_freq_missing`, a technical response-format control.

| Form | All dictionary fields | Respondent questions |
| --- | --- | --- |
| neps31_registry | 12 | 0 |
| neps31_screening | 73 | 73 |
| neps31_cohort_interest | 5 | 5 |
| neps31_extended_baseline | 75 | 74 |
| neps31_yeb | 19 | 19 |
| neps31_ycad | 17 | 17 |
| neps31_derived | 16 | 0 |
| neps31_cohort_review | 6 | 0 |

| Core index | Scoring items |
| --- | --- |
| EPI | 10 |
| ESI | 10 |
| SBI | 19 |
| MHDI | 6 |
| PFI | 28 |

## How to read field definitions

Native dictionary columns appear with their exact names. Only nonempty native values are printed for each field. Omitted native columns are empty strings in the original row; no default has been added. All 18 columns remain in the saved contract and participate in metadata hashes.

Radio and dropdown fields use the listed stored codes. A text field may additionally specify integer, number or date validation. Bounds come from the native validation columns; an empty bound does not supply an artificial limit. Blank Required Field flags are preserved, not converted into downstream scoring or eligibility rules.

An absent key, JSON null and an empty string remain distinct source states. A declared special response code has the meaning printed for that field. Do not use 99, 98 or 96 universally. No 73-item screening choice list declares any of those codes. Explicit analytical missingness or applicability is separate from inventing a raw code.

For attack frequency, `attack_freq` stores an actual integer of at least 2 when its branch applies. `attack_freq_missing` stores the separate response status. Numeric counts of 98 or 99 do not become missing merely because another field uses those codes.

## Decisions outside this dictionary

- The age field declares integer bounds 12-24; the local checklist asks for 10-19. Resolve any separate cohort restriction before enforcing eligibility. This document retains the original field bounds.
- Historical study_id notes refer to import from an NDS registry. The later approved independent-intake design preserves source-issued IDs and links a separate NDS ID downstream. The deployed native ID field still needs source metadata evidence. Original notes below remain verbatim and do not override that later design decision.
- The historical dictionary has no consent-named field. `screen_form_complete` has its own declared 0/1/2 codes and does not prove survey consent, NDS purpose consent or completion of every deployed instrument.
- Country display rows are proposed crosswalk/English-display metadata. They do not establish translation acceptance, measurement equivalence or transfer permission.
- Derived-field definitions do not prove that the pipeline populates each named output. Scoring remains provisional. Burden/profile rules and IWI coefficients require their stated approvals.

## Derived field definitions

| Field | Validation | Minimum | Maximum | Analytical definition |
| --- | --- | --- | --- | --- |
| age_band | integer | 1 | 3 | 12–14 / 15–19 / 20–24, derived from imported age_years; never entered by participant |
| brs_raw | number | 1 | 5 | 1–5; reverse items 2,4,6; complete six |
| mspss_raw | number | 1 | 7 | 1–7; all twelve for NEPS version; original subscales may be reported |
| gse_raw | number | 10 | 40 | 10–40; complete ten |
| k6_raw | number | 0 | 24 | 0–24; complete six |
| epi_100 | number | 0 | 100 | Arithmetic mean of 5 two-item dimension 0–100 scores; complete 10 |
| esi_100 | number | 0 | 100 | Arithmetic mean of 5 two-item 0–100 dimensions; complete 10 |
| sbi_100 | number | 0 | 100 | Mean of four normalised dimension means across 19 source items; all 19 |
| mhdi_100 | number | 0 | 100 | 100 × k6_raw / 24 |
| pfi_100 | number | 0 | 100 | Arithmetic mean of normalised BRS, MSPSS, GSE 0–100 values |
| nses_100 | number | 0 | 100 | 0.30×EPI + 0.25×ESI + 0.20×SBI + 0.20×MHDI + 0.05×(100−PFI), 0–100 |
| screen_score_status | integer |  |  | 1 complete \| 2 missing responses \| 3 structurally not applicable \| 4 unresolved response code \| 5 source not verified |
| stressor_burden_count | integer | 0 |  | Requires externally adopted indicator dictionary and thresholds: do not infer from NSES or 5 indices |
| stressor_burden_class | integer |  |  | 0–2 low; 3–5 moderate; 6–8 high; ≥9 very high, ONLY after unique indicator rules exist |
| stressor_profile |  |  |  | Profile derived from available indices under separately specified classification rules |
| iwi_score | number | 0 | 100 | Not compute from V3 assets alone until source 12-to-20 recoding and published coefficients implemented |

`k6_raw` declares 0-24; the scorer uses a result named `K6_total`. They are not a blanket 0-100 output. Likewise `brs_raw`, `mspss_raw` and `gse_raw` have their own ranges. Name mapping and implemented computations belong to the scoring review.

## Field index

| Order | Field | Form | Core 73 |
| --- | --- | --- | --- |
| 1 | study_id | neps31_registry | No |
| 2 | country | neps31_registry | No |
| 3 | site_id | neps31_registry | No |
| 4 | site_setting | neps31_registry | No |
| 5 | recruit_src | neps31_registry | No |
| 6 | screen_date | neps31_registry | No |
| 7 | crf_version | neps31_registry | No |
| 8 | form_lang | neps31_registry | No |
| 9 | age_years | neps31_registry | No |
| 10 | sex_report | neps31_registry | No |
| 11 | study_resident | neps31_registry | No |
| 12 | screen_form_complete | neps31_registry | No |
| 13 | epi_expectations_1 | neps31_screening | Yes |
| 14 | epi_expectations_2 | neps31_screening | Yes |
| 15 | epi_failure_1 | neps31_screening | Yes |
| 16 | epi_failure_2 | neps31_screening | Yes |
| 17 | epi_caregivers_1 | neps31_screening | Yes |
| 18 | epi_caregivers_2 | neps31_screening | Yes |
| 19 | epi_future_1 | neps31_screening | Yes |
| 20 | epi_future_2 | neps31_screening | Yes |
| 21 | epi_progress_1 | neps31_screening | Yes |
| 22 | epi_progress_2 | neps31_screening | Yes |
| 23 | esi_finstrain_1 | neps31_screening | Yes |
| 24 | esi_finstrain_2 | neps31_screening | Yes |
| 25 | esi_food_1 | neps31_screening | Yes |
| 26 | esi_food_2 | neps31_screening | Yes |
| 27 | esi_educost_1 | neps31_screening | Yes |
| 28 | esi_educost_2 | neps31_screening | Yes |
| 29 | esi_materials_1 | neps31_screening | Yes |
| 30 | esi_materials_2 | neps31_screening | Yes |
| 31 | esi_transport_1 | neps31_screening | Yes |
| 32 | esi_transport_2 | neps31_screening | Yes |
| 33 | sbi_loved_1 | neps31_screening | Yes |
| 34 | sbi_loved_2 | neps31_screening | Yes |
| 35 | sbi_loved_3 | neps31_screening | Yes |
| 36 | sbi_loved_4 | neps31_screening | Yes |
| 37 | sbi_loved_5 | neps31_screening | Yes |
| 38 | sbi_loved_6 | neps31_screening | Yes |
| 39 | sbi_loved_7 | neps31_screening | Yes |
| 40 | sbi_loved_8 | neps31_screening | Yes |
| 41 | sbi_comm_1 | neps31_screening | Yes |
| 42 | sbi_comm_2 | neps31_screening | Yes |
| 43 | sbi_comm_3 | neps31_screening | Yes |
| 44 | sbi_comm_4 | neps31_screening | Yes |
| 45 | sbi_self_1 | neps31_screening | Yes |
| 46 | sbi_self_2 | neps31_screening | Yes |
| 47 | sbi_self_3 | neps31_screening | Yes |
| 48 | sbi_self_4 | neps31_screening | Yes |
| 49 | sbi_help_1 | neps31_screening | Yes |
| 50 | sbi_help_2 | neps31_screening | Yes |
| 51 | sbi_help_3 | neps31_screening | Yes |
| 52 | k6_1 | neps31_screening | Yes |
| 53 | k6_2 | neps31_screening | Yes |
| 54 | k6_3 | neps31_screening | Yes |
| 55 | k6_4 | neps31_screening | Yes |
| 56 | k6_5 | neps31_screening | Yes |
| 57 | k6_6 | neps31_screening | Yes |
| 58 | brs_01 | neps31_screening | Yes |
| 59 | brs_02 | neps31_screening | Yes |
| 60 | brs_03 | neps31_screening | Yes |
| 61 | brs_04 | neps31_screening | Yes |
| 62 | brs_05 | neps31_screening | Yes |
| 63 | brs_06 | neps31_screening | Yes |
| 64 | mspss_01 | neps31_screening | Yes |
| 65 | mspss_02 | neps31_screening | Yes |
| 66 | mspss_03 | neps31_screening | Yes |
| 67 | mspss_04 | neps31_screening | Yes |
| 68 | mspss_05 | neps31_screening | Yes |
| 69 | mspss_06 | neps31_screening | Yes |
| 70 | mspss_07 | neps31_screening | Yes |
| 71 | mspss_08 | neps31_screening | Yes |
| 72 | mspss_09 | neps31_screening | Yes |
| 73 | mspss_10 | neps31_screening | Yes |
| 74 | mspss_11 | neps31_screening | Yes |
| 75 | mspss_12 | neps31_screening | Yes |
| 76 | gse_01 | neps31_screening | Yes |
| 77 | gse_02 | neps31_screening | Yes |
| 78 | gse_03 | neps31_screening | Yes |
| 79 | gse_04 | neps31_screening | Yes |
| 80 | gse_05 | neps31_screening | Yes |
| 81 | gse_06 | neps31_screening | Yes |
| 82 | gse_07 | neps31_screening | Yes |
| 83 | gse_08 | neps31_screening | Yes |
| 84 | gse_09 | neps31_screening | Yes |
| 85 | gse_10 | neps31_screening | Yes |
| 86 | willing_24m | neps31_cohort_interest | No |
| 87 | contact_24m | neps31_cohort_interest | No |
| 88 | wp3_willing | neps31_cohort_interest | No |
| 89 | wp4_willing | neps31_cohort_interest | No |
| 90 | wp6_willing | neps31_cohort_interest | No |
| 91 | currently_school | neps31_extended_baseline | No |
| 92 | ever_school | neps31_extended_baseline | No |
| 93 | school_level | neps31_extended_baseline | No |
| 94 | not_school_reason | neps31_extended_baseline | No |
| 95 | self_school_perf | neps31_extended_baseline | No |
| 96 | household_language | neps31_extended_baseline | No |
| 97 | internet_home | neps31_extended_baseline | No |
| 98 | father_ed | neps31_extended_baseline | No |
| 99 | mother_ed | neps31_extended_baseline | No |
| 100 | household_members | neps31_extended_baseline | No |
| 101 | living_arrangement | neps31_extended_baseline | No |
| 102 | caregiver_prim | neps31_extended_baseline | No |
| 103 | parent_alive | neps31_extended_baseline | No |
| 104 | caregiver_abroad | neps31_extended_baseline | No |
| 105 | caregiver_education | neps31_extended_baseline | No |
| 106 | family_mh_hist | neps31_extended_baseline | No |
| 107 | school_days_missed | neps31_extended_baseline | No |
| 108 | work_status | neps31_extended_baseline | No |
| 109 | care_duties | neps31_extended_baseline | No |
| 110 | epix_exams_1 | neps31_extended_baseline | No |
| 111 | epix_exams_2 | neps31_extended_baseline | No |
| 112 | epix_teacher_1 | neps31_extended_baseline | No |
| 113 | epix_teacher_2 | neps31_extended_baseline | No |
| 114 | asset_01 | neps31_extended_baseline | No |
| 115 | asset_02 | neps31_extended_baseline | No |
| 116 | asset_03 | neps31_extended_baseline | No |
| 117 | asset_04 | neps31_extended_baseline | No |
| 118 | asset_05 | neps31_extended_baseline | No |
| 119 | asset_06 | neps31_extended_baseline | No |
| 120 | asset_07 | neps31_extended_baseline | No |
| 121 | asset_08 | neps31_extended_baseline | No |
| 122 | asset_water | neps31_extended_baseline | No |
| 123 | asset_toilet | neps31_extended_baseline | No |
| 124 | asset_floor | neps31_extended_baseline | No |
| 125 | asset_sleeprooms | neps31_extended_baseline | No |
| 126 | sbi_exp_gate | neps31_extended_baseline | No |
| 127 | sbi_exper_1 | neps31_extended_baseline | No |
| 128 | sbi_exper_2 | neps31_extended_baseline | No |
| 129 | sbi_exper_3 | neps31_extended_baseline | No |
| 130 | sbi_exper_4 | neps31_extended_baseline | No |
| 131 | seek_01 | neps31_extended_baseline | No |
| 132 | seek_02 | neps31_extended_baseline | No |
| 133 | seek_03 | neps31_extended_baseline | No |
| 134 | seek_04 | neps31_extended_baseline | No |
| 135 | seek_08 | neps31_extended_baseline | No |
| 136 | ypw_01 | neps31_extended_baseline | No |
| 137 | ypw_02 | neps31_extended_baseline | No |
| 138 | ypw_03 | neps31_extended_baseline | No |
| 139 | ypw_04 | neps31_extended_baseline | No |
| 140 | ypw_05 | neps31_extended_baseline | No |
| 141 | ypw_06 | neps31_extended_baseline | No |
| 142 | ypw_07 | neps31_extended_baseline | No |
| 143 | ypw_08 | neps31_extended_baseline | No |
| 144 | ypw_09 | neps31_extended_baseline | No |
| 145 | ypw_10 | neps31_extended_baseline | No |
| 146 | ypw_11 | neps31_extended_baseline | No |
| 147 | ypw_12 | neps31_extended_baseline | No |
| 148 | ypw_13 | neps31_extended_baseline | No |
| 149 | ypw_14 | neps31_extended_baseline | No |
| 150 | bully_30d | neps31_extended_baseline | No |
| 151 | attack_12m | neps31_extended_baseline | No |
| 152 | fight_12m | neps31_extended_baseline | No |
| 153 | substance_ever | neps31_extended_baseline | No |
| 154 | bully_type | neps31_extended_baseline | No |
| 155 | attack_freq_missing | neps31_extended_baseline | No |
| 156 | attack_freq | neps31_extended_baseline | No |
| 157 | attack_by | neps31_extended_baseline | No |
| 158 | substance_30d | neps31_extended_baseline | No |
| 159 | caregiver_substance | neps31_extended_baseline | No |
| 160 | family_disrupt_current | neps31_extended_baseline | No |
| 161 | community_safety | neps31_extended_baseline | No |
| 162 | social_family_contact | neps31_extended_baseline | No |
| 163 | social_peer_contact | neps31_extended_baseline | No |
| 164 | social_community | neps31_extended_baseline | No |
| 165 | sleep_hunger_context | neps31_extended_baseline | No |
| 166 | yeb_01 | neps31_yeb | No |
| 167 | yeb_02 | neps31_yeb | No |
| 168 | yeb_03 | neps31_yeb | No |
| 169 | yeb_04 | neps31_yeb | No |
| 170 | yeb_05 | neps31_yeb | No |
| 171 | yeb_06 | neps31_yeb | No |
| 172 | yeb_07 | neps31_yeb | No |
| 173 | yeb_08 | neps31_yeb | No |
| 174 | yeb_09 | neps31_yeb | No |
| 175 | yeb_10 | neps31_yeb | No |
| 176 | yeb_11 | neps31_yeb | No |
| 177 | yeb_12 | neps31_yeb | No |
| 178 | yeb_13 | neps31_yeb | No |
| 179 | yeb_14 | neps31_yeb | No |
| 180 | yeb_imp_study | neps31_yeb | No |
| 181 | yeb_imp_work | neps31_yeb | No |
| 182 | yeb_imp_home | neps31_yeb | No |
| 183 | yeb_imp_rel | neps31_yeb | No |
| 184 | yeb_imp_activities | neps31_yeb | No |
| 185 | ycad_01 | neps31_ycad | No |
| 186 | ycad_02 | neps31_ycad | No |
| 187 | ycad_03 | neps31_ycad | No |
| 188 | ycad_04 | neps31_ycad | No |
| 189 | ycad_05 | neps31_ycad | No |
| 190 | ycad_06 | neps31_ycad | No |
| 191 | ycad_07 | neps31_ycad | No |
| 192 | ycad_08 | neps31_ycad | No |
| 193 | ycad_09 | neps31_ycad | No |
| 194 | ycad_10 | neps31_ycad | No |
| 195 | ycad_11 | neps31_ycad | No |
| 196 | ycad_12 | neps31_ycad | No |
| 197 | ycad_13 | neps31_ycad | No |
| 198 | ycad_14 | neps31_ycad | No |
| 199 | ycad_time_harm | neps31_ycad | No |
| 200 | ycad_time_viol | neps31_ycad | No |
| 201 | ycad_time_sep | neps31_ycad | No |
| 202 | age_band | neps31_derived | No |
| 203 | brs_raw | neps31_derived | No |
| 204 | mspss_raw | neps31_derived | No |
| 205 | gse_raw | neps31_derived | No |
| 206 | k6_raw | neps31_derived | No |
| 207 | epi_100 | neps31_derived | No |
| 208 | esi_100 | neps31_derived | No |
| 209 | sbi_100 | neps31_derived | No |
| 210 | mhdi_100 | neps31_derived | No |
| 211 | pfi_100 | neps31_derived | No |
| 212 | nses_100 | neps31_derived | No |
| 213 | screen_score_status | neps31_derived | No |
| 214 | stressor_burden_count | neps31_derived | No |
| 215 | stressor_burden_class | neps31_derived | No |
| 216 | stressor_profile | neps31_derived | No |
| 217 | iwi_score | neps31_derived | No |
| 218 | cohort_eligible | neps31_cohort_review | No |
| 219 | cohort_status | neps31_cohort_review | No |
| 220 | cohort_reason | neps31_cohort_review | No |
| 221 | cohort_reviewer | neps31_cohort_review | No |
| 222 | selection_batch | neps31_cohort_review | No |
| 223 | longitud_id | neps31_cohort_review | No |

## Field definitions

### 001 study_id

| Property | Source definition |
| --- | --- |
| Variable / Field Name | study_id |
| Form Name | neps31_registry |
| Section Header | NEPS Digital System registry and identification (administrative form) |
| Field Type | text |
| Field Label | Pseudonymous NEPS study participant ID |
| Field Note | REDCap record identifier, imported from NEPS Digital System. Do not collect participant name or consent here. |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 9decf7c185664b9d9d75aa9a2dd198209d2b4c9109ccb6083c4c57957e49d737 |
| Analysis label | Pseudonymous NEPS study participant ID |
| Analysis response definition | Free text; limited/controlled as defined in notes |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | Generated by participant registry; do not derive from email Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 002 country

| Property | Source definition |
| --- | --- |
| Variable / Field Name | country |
| Form Name | neps31_registry |
| Field Type | radio |
| Field Label | Country of recruitment |
| Choices, Calculations, OR Slider Labels | 1, Ghana \| 2, Sierra Leone \| 3, Tanzania |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 13b34e3043a5b5e718e669edfb1fffc394470e9a30a6e239dce941fa1e9b180d |
| Analysis label | Country of recruitment |
| Analysis response definition | 1, Ghana \| 2, Sierra Leone \| 3, Tanzania |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | Must be validated with site registry Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 003 site_id

| Property | Source definition |
| --- | --- |
| Variable / Field Name | site_id |
| Form Name | neps31_registry |
| Field Type | text |
| Field Label | Approved study site identifier |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 8cd99f8ca20ded491693f40224d6ec7237f7725082afbb1fe382c1f4efbbf912 |
| Analysis label | Approved study site identifier |
| Analysis response definition | Free text; limited/controlled as defined in notes |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | Use site registry; no free-text codes Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 004 site_setting

| Property | Source definition |
| --- | --- |
| Variable / Field Name | site_setting |
| Form Name | neps31_registry |
| Field Type | radio |
| Field Label | Study setting |
| Choices, Calculations, OR Slider Labels | 1, Urban \| 2, Peri-urban \| 3, Rural |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 5d3a9a3075eaf4a66e9baebf6a3f597502a71c577c30f008549a0e9a615e8432 |
| Analysis label | Study setting |
| Analysis response definition | 1, Urban \| 2, Peri-urban \| 3, Rural |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | Definitions in site manual Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 005 recruit_src

| Property | Source definition |
| --- | --- |
| Variable / Field Name | recruit_src |
| Form Name | neps31_registry |
| Field Type | radio |
| Field Label | Recruitment source |
| Choices, Calculations, OR Slider Labels | 1, School \| 2, Technical or vocational \| 3, Tertiary institution \| 4, Community |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 47f768364b0ecd190f698d03d53c7783e28000d8be2432d42a03a592f340ab05 |
| Analysis label | Recruitment source |
| Analysis response definition | 1, School \| 2, Technical or vocational \| 3, Tertiary institution \| 4, Community |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | One canonical recruitment source Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 006 screen_date

| Property | Source definition |
| --- | --- |
| Variable / Field Name | screen_date |
| Form Name | neps31_registry |
| Field Type | text |
| Field Label | Screening date |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Text Validation Type OR Show Slider Number | date_ymd |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 516a17cc1519c2a33f1d48110edc15a2a7df4c24cba3575f1e84bfd8297e82a0 |
| Analysis label | Screening date |
| Analysis response definition | YYYY-MM-DD |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | Use local date with audit timestamp Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 007 crf_version

| Property | Source definition |
| --- | --- |
| Variable / Field Name | crf_version |
| Form Name | neps31_registry |
| Field Type | text |
| Field Label | CRF version administered |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | b6ba0a58677ee0cdd2b78eb08221c0b4679520361d17318de8e1b540b4d62742 |
| Analysis label | CRF version administered |
| Analysis response definition | Free text; limited/controlled as defined in notes |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | System constant: 3.0-SCI-DRAFT until release Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 008 form_lang

| Property | Source definition |
| --- | --- |
| Variable / Field Name | form_lang |
| Form Name | neps31_registry |
| Field Type | radio |
| Field Label | Language administered |
| Choices, Calculations, OR Slider Labels | 1, English \| 2, Akan/Twi \| 3, Krio \| 4, Kiswahili \| 5, Other approved language |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | fbe24f69845216e269dddbe49ff505ebedd8bc94e5b905dfb3ac6a582f1050f4 |
| Analysis label | Language administered |
| Analysis response definition | 1, English \| 2, Akan/Twi \| 3, Krio \| 4, Kiswahili \| 5, Other approved language |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | Only approved translation codes Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 009 age_years

| Property | Source definition |
| --- | --- |
| Variable / Field Name | age_years |
| Form Name | neps31_registry |
| Field Type | text |
| Field Label | Age in completed years at screening |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Text Validation Type OR Show Slider Number | integer |
| Text Validation Min | 12 |
| Text Validation Max | 24 |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 17d6664225da58fbe022be0a7fd94530206ceeb6c198a09b09d8b266ca73a591 |
| Analysis label | Age in completed years at screening |
| Analysis response definition | Whole number 12–24 |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | Birth date may remain restricted in consent registry; use accurate age Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 010 sex_report

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sex_report |
| Form Name | neps31_registry |
| Field Type | radio |
| Field Label | Sex as recorded by participant |
| Choices, Calculations, OR Slider Labels | 1, Boy/male \| 2, Girl/female \| 99, Prefer not to answer |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 7b44eb6a331750de0ef2adadfe753124def012f035f5e59597e869d1f4f34e03 |
| Analysis label | Sex as recorded by participant |
| Analysis response definition | 1, Boy/male \| 2, Girl/female \| 99, Prefer not to answer |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | Source V2 uses boy/girl; adapt approved culturally appropriate terms Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 011 study_resident

| Property | Source definition |
| --- | --- |
| Variable / Field Name | study_resident |
| Form Name | neps31_registry |
| Field Type | radio |
| Field Label | Lives within an approved NEPS study area? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | Imported / system field |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | b4fb47310c73381a877b637a7d206ef9bd8c3687ad25a6165df0d80dcca3b5fd |
| Analysis label | Lives within an approved NEPS study area? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | Verify against site list Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 012 screen_form_complete

| Property | Source definition |
| --- | --- |
| Variable / Field Name | screen_form_complete |
| Form Name | neps31_registry |
| Field Type | radio |
| Field Label | Screening form status |
| Choices, Calculations, OR Slider Labels | 0, Incomplete \| 1, Unverified \| 2, Complete and reviewed |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | System output / registry action |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 34d7ce5283baded4309ddc61520698c0b1cf5672c24b640f6bd184b055de518d |
| Analysis label | Screening form status |
| Analysis response definition | 0, Incomplete \| 1, Unverified \| 2, Complete and reviewed |
| Analysis construct | ADMIN |
| Analysis index | ADMIN |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p1 and Recruitment Plan §§4,14,16–18 |
| Analysis control note | Collector completion != valid index completeness Digital System source of truth. No consent/assent/guardian permission stored in REDCap. |
| Analysis administration stage | 00 Digital prefill |
| Analysis implementation note | Do not display as survey question. |

### 013 epi_expectations_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_expectations_1 |
| Form Name | neps31_screening |
| Section Header | Educational pressure (EPI) |
| Field Type | radio |
| Field Label | I feel under pressure to achieve success through education or training. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | Reference: Current views about current, previous or desired education |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f8f7ccadd6628bc64498f7d8cd98e9d6692e050a0c79f659a09a412321376889 |
| Analysis label | I feel under pressure to achieve success through education or training. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | expectations |
| Analysis index | EPI |
| Analysis dimension | expectations |
| Analysis reference period | Current views about current, previous or desired education |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.1 |
| Analysis control note | Original NEPS item, not a validated PPAPS item. Relevance across school status to be cognitively tested. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 1 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 014 epi_expectations_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_expectations_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | People important to me expect more educational progress from me than I feel able to achieve. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | Reference: Current views about current, previous or desired education |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 97a2bc4d848f1bb64f13c796a75456177c1131cf6b0f2dd5dd19875d3db10312 |
| Analysis label | People important to me expect more educational progress from me than I feel able to achieve. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | expectations |
| Analysis index | EPI |
| Analysis dimension | expectations |
| Analysis reference period | Current views about current, previous or desired education |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.1 |
| Analysis control note | Original NEPS item, not a validated PPAPS item. Relevance across school status to be cognitively tested. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 2 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 015 epi_failure_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_failure_1 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I worry that failing to reach my education or training goals will let other people down. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | Reference: Current views about current, previous or desired education |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 3657c07ecaa82597c365a3f8c2522bd40f9f7470ae3f8f76b89cff1f38672678 |
| Analysis label | I worry that failing to reach my education or training goals will let other people down. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | failure |
| Analysis index | EPI |
| Analysis dimension | failure |
| Analysis reference period | Current views about current, previous or desired education |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.1 |
| Analysis control note | Original NEPS item, not a validated PPAPS item. Relevance across school status to be cognitively tested. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 3 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 016 epi_failure_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_failure_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | The possibility of not reaching my education or training goals causes me stress. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | Reference: Current views about current, previous or desired education |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | bd01e02ed344b0b47753d97f594b21568fdd83a633d5e4bc92a11953f5a64a22 |
| Analysis label | The possibility of not reaching my education or training goals causes me stress. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | failure |
| Analysis index | EPI |
| Analysis dimension | failure |
| Analysis reference period | Current views about current, previous or desired education |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.1 |
| Analysis control note | Original NEPS item, not a validated PPAPS item. Relevance across school status to be cognitively tested. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 4 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 017 epi_caregivers_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_caregivers_1 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | Parents, caregivers or other important adults put pressure on me to succeed in education or training. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | Reference: Current views about current, previous or desired education |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f437eaee0465a8a31474e39b9cd452b9022e4866796f88dbf06b362d7517ca19 |
| Analysis label | Parents, caregivers or other important adults put pressure on me to succeed in education or training. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | caregivers |
| Analysis index | EPI |
| Analysis dimension | caregivers |
| Analysis reference period | Current views about current, previous or desired education |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.1 |
| Analysis control note | Original NEPS item, not a validated PPAPS item. Relevance across school status to be cognitively tested. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 5 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 018 epi_caregivers_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_caregivers_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I worry about how adults close to me will react if my education or training plans do not work out. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | Reference: Current views about current, previous or desired education |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 8657093eb0196a7efe3a3f545c6226e52658e594d2233caa3453c10584b88e79 |
| Analysis label | I worry about how adults close to me will react if my education or training plans do not work out. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | caregivers |
| Analysis index | EPI |
| Analysis dimension | caregivers |
| Analysis reference period | Current views about current, previous or desired education |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.1 |
| Analysis control note | Original NEPS item, not a validated PPAPS item. Relevance across school status to be cognitively tested. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 6 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 019 epi_future_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_future_1 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | Uncertainty about future education or training opportunities worries me. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | Reference: Current views about current, previous or desired education |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 865d35367d8b76df197c68b8feb5d69482f07037bbede9d10592ee0c9957e936 |
| Analysis label | Uncertainty about future education or training opportunities worries me. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | future |
| Analysis index | EPI |
| Analysis dimension | future |
| Analysis reference period | Current views about current, previous or desired education |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.1 |
| Analysis control note | Original NEPS item, not a validated PPAPS item. Relevance across school status to be cognitively tested. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 7 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 020 epi_future_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_future_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I feel stressed when I think about whether I can continue, return to or progress in education or training. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | Reference: Current views about current, previous or desired education |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f7fb5b54cad677f59a7e29b773fee1c44235c3942a037e436423bdca389241fd |
| Analysis label | I feel stressed when I think about whether I can continue, return to or progress in education or training. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | future |
| Analysis index | EPI |
| Analysis dimension | future |
| Analysis reference period | Current views about current, previous or desired education |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.1 |
| Analysis control note | Original NEPS item, not a validated PPAPS item. Relevance across school status to be cognitively tested. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 8 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 021 epi_progress_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_progress_1 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I feel under pressure about how much progress I am making towards my education or training goals. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | Reference: Current views about current, previous or desired education |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 9dc4b877945663aab520f57e45d60ccb2434979800f40c8b5254c0ad263feaf7 |
| Analysis label | I feel under pressure about how much progress I am making towards my education or training goals. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | progress |
| Analysis index | EPI |
| Analysis dimension | progress |
| Analysis reference period | Current views about current, previous or desired education |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.1 |
| Analysis control note | Original NEPS item, not a validated PPAPS item. Relevance across school status to be cognitively tested. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 9 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 022 epi_progress_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_progress_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I feel I am falling behind where I should be in education or training. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | Reference: Current views about current, previous or desired education |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 60dcb9fb93cb035f47c9ec2ea7e2ddbd7d7d57721fd12eb4931786c1577844ae |
| Analysis label | I feel I am falling behind where I should be in education or training. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | progress |
| Analysis index | EPI |
| Analysis dimension | progress |
| Analysis reference period | Current views about current, previous or desired education |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.1 |
| Analysis control note | Original NEPS item, not a validated PPAPS item. Relevance across school status to be cognitively tested. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 10 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 023 esi_finstrain_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_finstrain_1 |
| Form Name | neps31_screening |
| Section Header | Economic stress (ESI) |
| Field Type | radio |
| Field Label | During the past 12 months, how often did your household struggle to pay for basic necessities? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | ec3de54af11f65a1c7e6b4d4406734ed716e5dca307d959db5d6cbe8d69f7c00 |
| Analysis label | During the past 12 months, how often did your household struggle to pay for basic necessities? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | finstrain |
| Analysis index | ESI |
| Analysis dimension | finstrain |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.2 |
| Analysis control note | Frequency wording is new and needs cognitive validation; do not label as FIES, HFIAS or a validated economic-stress scale. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 11 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 024 esi_finstrain_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_finstrain_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 12 months, how often did you worry because your household did not have enough money? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | d8cae6192f6d6282d3f86262838f98ee784defe140b0c48a472363c14f422a97 |
| Analysis label | During the past 12 months, how often did you worry because your household did not have enough money? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | finstrain |
| Analysis index | ESI |
| Analysis dimension | finstrain |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.2 |
| Analysis control note | Frequency wording is new and needs cognitive validation; do not label as FIES, HFIAS or a validated economic-stress scale. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 12 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 025 esi_food_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_food_1 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 12 months, how often did you have to eat less than you needed because there was not enough money or food? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 5d59a3d357730e04f7fd2f5cdddd59f53653629094ccc38c248f7b835b3116dd |
| Analysis label | During the past 12 months, how often did you have to eat less than you needed because there was not enough money or food? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | food |
| Analysis index | ESI |
| Analysis dimension | food |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.2 |
| Analysis control note | Frequency wording is new and needs cognitive validation; do not label as FIES, HFIAS or a validated economic-stress scale. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 13 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 026 esi_food_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_food_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 12 months, how often did you skip a meal because your household could not afford enough food? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | a7abb19441bebb625eee2a0a04c042b1af4b6029f5efbb2ce2df11dc81dbbb30 |
| Analysis label | During the past 12 months, how often did you skip a meal because your household could not afford enough food? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | food |
| Analysis index | ESI |
| Analysis dimension | food |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.2 |
| Analysis control note | Frequency wording is new and needs cognitive validation; do not label as FIES, HFIAS or a validated economic-stress scale. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 14 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 027 esi_educost_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_educost_1 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 12 months, how often did lack of money make it difficult for you to start, continue, return to or progress in education or training? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | efedf08b5dfd8376e008fc00698b5bc24f9133e91784c830fb64585e97db9169 |
| Analysis label | During the past 12 months, how often did lack of money make it difficult for you to start, continue, return to or progress in education or training? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | educost |
| Analysis index | ESI |
| Analysis dimension | educost |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.2 |
| Analysis control note | Frequency wording is new and needs cognitive validation; do not label as FIES, HFIAS or a validated economic-stress scale. If no education/training opportunity ever existed, 96 structural NA, never zero; ESI completeness and subgroup comparability must be reported. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 15 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 028 esi_educost_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_educost_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 12 months, how often did school or training fees, examinations or related costs prevent you from doing something you needed to do for education? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | aa6e84753fac53bde1adce881a4a4a24e474033cd029d012a0233adac81fb271 |
| Analysis label | During the past 12 months, how often did school or training fees, examinations or related costs prevent you from doing something you needed to do for education? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | educost |
| Analysis index | ESI |
| Analysis dimension | educost |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.2 |
| Analysis control note | Frequency wording is new and needs cognitive validation; do not label as FIES, HFIAS or a validated economic-stress scale. If no education/training opportunity ever existed, 96 structural NA, never zero; ESI completeness and subgroup comparability must be reported. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 16 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 029 esi_materials_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_materials_1 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 12 months, how often did you lack needed books, learning materials or devices because of their cost? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | fb4690c7997936a78c51c318aac8b3fe235c19a8d493abb126dba94d5e0b51d5 |
| Analysis label | During the past 12 months, how often did you lack needed books, learning materials or devices because of their cost? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | materials |
| Analysis index | ESI |
| Analysis dimension | materials |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.2 |
| Analysis control note | Frequency wording is new and needs cognitive validation; do not label as FIES, HFIAS or a validated economic-stress scale. If no education/training opportunity ever existed, 96 structural NA, never zero; ESI completeness and subgroup comparability must be reported. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 17 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 030 esi_materials_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_materials_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 12 months, how often did internet or data costs prevent you from accessing learning or training materials? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 64ce1fae1c5ac6b005c43abed635bfadf733784cba9e26d88af75b207cb968a8 |
| Analysis label | During the past 12 months, how often did internet or data costs prevent you from accessing learning or training materials? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | materials |
| Analysis index | ESI |
| Analysis dimension | materials |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.2 |
| Analysis control note | Frequency wording is new and needs cognitive validation; do not label as FIES, HFIAS or a validated economic-stress scale. If no education/training opportunity ever existed, 96 structural NA, never zero; ESI completeness and subgroup comparability must be reported. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 18 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 031 esi_transport_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_transport_1 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 12 months, how often did transport costs stop you from attending a needed educational or training activity? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 934f2cacde82802924b432034efbcb35e6b2c70715f2f94339929b2f754e86e1 |
| Analysis label | During the past 12 months, how often did transport costs stop you from attending a needed educational or training activity? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | transport |
| Analysis index | ESI |
| Analysis dimension | transport |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.2 |
| Analysis control note | Frequency wording is new and needs cognitive validation; do not label as FIES, HFIAS or a validated economic-stress scale. If no education/training opportunity ever existed, 96 structural NA, never zero; ESI completeness and subgroup comparability must be reported. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 19 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 032 esi_transport_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_transport_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 12 months, how often did transport or related expenses limit access to school, training or an opportunity to return to education? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f2ceba872f7ac06626651d6fcf8e61f17a223652ec86dbad6810c0a26cfc8316 |
| Analysis label | During the past 12 months, how often did transport or related expenses limit access to school, training or an opportunity to return to education? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | transport |
| Analysis index | ESI |
| Analysis dimension | transport |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new proposed items grounded in Recruitment Plan §7.2 |
| Analysis control note | Frequency wording is new and needs cognitive validation; do not label as FIES, HFIAS or a validated economic-stress scale. If no education/training opportunity ever existed, 96 structural NA, never zero; ESI completeness and subgroup comparability must be reported. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 20 |
| Analysis implementation note | 10 original core items; retain 5 two-item dimensions. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 033 sbi_loved_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_loved_1 |
| Form Name | neps31_screening |
| Section Header | Anticipated stigma from loved ones |
| Field Type | radio |
| Field Label | If I had a mental health problem and my friends or family knew, they would think less of me. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 70940df4cae9fd1b1ac6a82392c3821dffd777a20674c96b5a88a3a36bc45360 |
| Analysis label | If I had a mental health problem and my friends or family knew, they would think less of me. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_loved |
| Analysis index | SBI |
| Analysis dimension | anticipated_loved |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p16 |
| Analysis control note | Check source instrument identity, reproduction/adaptation permission and translation. V2 phrasing contains typo corrected here. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 21 |
| Analysis implementation note | Original eight-item block intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 034 sbi_loved_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_loved_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | If I had a mental health problem and my friends or family knew, they would see me as weak. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 218740404fb4be8b508ac06124a9a6b313a375a496de1bac9dc003f4ce241245 |
| Analysis label | If I had a mental health problem and my friends or family knew, they would see me as weak. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_loved |
| Analysis index | SBI |
| Analysis dimension | anticipated_loved |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p16 |
| Analysis control note | Check source instrument identity, reproduction/adaptation permission and translation. V2 phrasing contains typo corrected here. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 22 |
| Analysis implementation note | Original eight-item block intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 035 sbi_loved_3

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_loved_3 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | If I had a mental health problem and my friends or family knew, they would feel uncomfortable around me. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 5bf1819073635889549bc30e0007c7120982dbaca331daf2370c185438d127a8 |
| Analysis label | If I had a mental health problem and my friends or family knew, they would feel uncomfortable around me. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_loved |
| Analysis index | SBI |
| Analysis dimension | anticipated_loved |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p16 |
| Analysis control note | Check source instrument identity, reproduction/adaptation permission and translation. V2 phrasing contains typo corrected here. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 23 |
| Analysis implementation note | Original eight-item block intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 036 sbi_loved_4

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_loved_4 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | If I had a mental health problem and my friends or family knew, they would not want to be around me. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 0241cc5a2db4b6232aec72b5307584c74142c3b74be05416912a5d0b60760ffb |
| Analysis label | If I had a mental health problem and my friends or family knew, they would not want to be around me. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_loved |
| Analysis index | SBI |
| Analysis dimension | anticipated_loved |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p16 |
| Analysis control note | Check source instrument identity, reproduction/adaptation permission and translation. V2 phrasing contains typo corrected here. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 24 |
| Analysis implementation note | Original eight-item block intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 037 sbi_loved_5

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_loved_5 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | If I had a mental health problem and my friends or family knew, they would think I was faking. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 87e4486e8e7860da0a9f26a0840e1f464761231ccd2204662a7758500282f5f5 |
| Analysis label | If I had a mental health problem and my friends or family knew, they would think I was faking. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_loved |
| Analysis index | SBI |
| Analysis dimension | anticipated_loved |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p16 |
| Analysis control note | Check source instrument identity, reproduction/adaptation permission and translation. V2 phrasing contains typo corrected here. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 25 |
| Analysis implementation note | Original eight-item block intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 038 sbi_loved_6

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_loved_6 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | If I had a mental health problem and my friends or family knew, they would be afraid that I might be violent or dangerous. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | fb945d15ca771ce83523ed678ce530e04ee610a04743b9a9d275205f44c18480 |
| Analysis label | If I had a mental health problem and my friends or family knew, they would be afraid that I might be violent or dangerous. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_loved |
| Analysis index | SBI |
| Analysis dimension | anticipated_loved |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p16 |
| Analysis control note | Check source instrument identity, reproduction/adaptation permission and translation. V2 phrasing contains typo corrected here. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 26 |
| Analysis implementation note | Original eight-item block intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 039 sbi_loved_7

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_loved_7 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | If I had a mental health problem and my friends or family knew, they would think that I could not be trusted. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | c6392d0fe6f7bcdb01feb3fcd4671025fc3465bdddf00db862c41c3658ea0135 |
| Analysis label | If I had a mental health problem and my friends or family knew, they would think that I could not be trusted. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_loved |
| Analysis index | SBI |
| Analysis dimension | anticipated_loved |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p16 |
| Analysis control note | Check source instrument identity, reproduction/adaptation permission and translation. V2 phrasing contains typo corrected here. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 27 |
| Analysis implementation note | Original eight-item block intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 040 sbi_loved_8

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_loved_8 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | If I had a mental health problem and my friends or family knew, they would avoid talking to me. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 54a871794c18d2ae96ff891e07cff96ba7e4c2427006b96f408208928d4a0584 |
| Analysis label | If I had a mental health problem and my friends or family knew, they would avoid talking to me. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_loved |
| Analysis index | SBI |
| Analysis dimension | anticipated_loved |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p16 |
| Analysis control note | Check source instrument identity, reproduction/adaptation permission and translation. V2 phrasing contains typo corrected here. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 28 |
| Analysis implementation note | Original eight-item block intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 041 sbi_comm_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_comm_1 |
| Form Name | neps31_screening |
| Section Header | Community and self-directed stigma |
| Field Type | radio |
| Field Label | People in my school, training setting or community would treat me differently if they knew I had a mental health problem. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 012377f29c8315e8dbb947e4a8810e413f5938228fea8384e85ca1a3974f379d |
| Analysis label | People in my school, training setting or community would treat me differently if they knew I had a mental health problem. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_community |
| Analysis index | SBI |
| Analysis dimension | anticipated_community |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new replacement for V2 p17 mislabelled school/work module |
| Analysis control note | V2 school heading contains workplace-only content; not reused unchanged. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 29 |
| Analysis implementation note | Four community + four self-stigma items. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 042 sbi_comm_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_comm_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I would worry that people around me would stop including me if they knew I had a mental health problem. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 9222bab1b6fd452097a941e025ce9ee40e39bbf4173828c884c23a168fa03188 |
| Analysis label | I would worry that people around me would stop including me if they knew I had a mental health problem. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_community |
| Analysis index | SBI |
| Analysis dimension | anticipated_community |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new replacement for V2 p17 mislabelled school/work module |
| Analysis control note | V2 school heading contains workplace-only content; not reused unchanged. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 30 |
| Analysis implementation note | Four community + four self-stigma items. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 043 sbi_comm_3

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_comm_3 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | People around me would judge my abilities unfairly if they knew I had a mental health problem. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 48a71be8e8c0e24b95c669766522df482f030dc5251a467734364fdc92a88097 |
| Analysis label | People around me would judge my abilities unfairly if they knew I had a mental health problem. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_community |
| Analysis index | SBI |
| Analysis dimension | anticipated_community |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new replacement for V2 p17 mislabelled school/work module |
| Analysis control note | V2 school heading contains workplace-only content; not reused unchanged. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 31 |
| Analysis implementation note | Four community + four self-stigma items. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 044 sbi_comm_4

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_comm_4 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I would worry that talking about a mental health problem would affect how other people respect me. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 66de20edb101141f08d565cf09e3c88ebc9501be28e21f39577e1c29f655819c |
| Analysis label | I would worry that talking about a mental health problem would affect how other people respect me. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | anticipated_community |
| Analysis index | SBI |
| Analysis dimension | anticipated_community |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new replacement for V2 p17 mislabelled school/work module |
| Analysis control note | V2 school heading contains workplace-only content; not reused unchanged. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 32 |
| Analysis implementation note | Four community + four self-stigma items. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 045 sbi_self_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_self_1 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I would feel ashamed of myself if I needed support for a mental health problem. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 298b80e5998f235e6d160c96714a9857ef2dd9d42230ada39e521275599760c5 |
| Analysis label | I would feel ashamed of myself if I needed support for a mental health problem. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | self_stigma_expect |
| Analysis index | SBI |
| Analysis dimension | self_stigma_expect |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS newly proposed stigma items; Recruitment Plan §7.3 |
| Analysis control note | Hypothetical wording; never claim this measures experienced internalised stigma. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 33 |
| Analysis implementation note | Four community + four self-stigma items. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 046 sbi_self_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_self_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I would think less of myself if I experienced a mental health problem. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 7e443b54c7a1b286152d11de183d2c4242d8e35358b551288e4072208ffed1b3 |
| Analysis label | I would think less of myself if I experienced a mental health problem. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | self_stigma_expect |
| Analysis index | SBI |
| Analysis dimension | self_stigma_expect |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS newly proposed stigma items; Recruitment Plan §7.3 |
| Analysis control note | Hypothetical wording; never claim this measures experienced internalised stigma. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 34 |
| Analysis implementation note | Four community + four self-stigma items. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 047 sbi_self_3

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_self_3 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I would blame myself for having emotional or mental health difficulties. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | fd1d4ca90a722dd55b6a8f474d39cac3f51f4a3a4df76a2653ed84aa37057456 |
| Analysis label | I would blame myself for having emotional or mental health difficulties. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | self_stigma_expect |
| Analysis index | SBI |
| Analysis dimension | self_stigma_expect |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS newly proposed stigma items; Recruitment Plan §7.3 |
| Analysis control note | Hypothetical wording; never claim this measures experienced internalised stigma. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 35 |
| Analysis implementation note | Four community + four self-stigma items. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 048 sbi_self_4

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_self_4 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | Having a mental health problem would make me feel that I am less capable than other young people. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 781533bdb2509450327e87d3096944140b26fa0d8c5c4f0941eb61cf45d6f59a |
| Analysis label | Having a mental health problem would make me feel that I am less capable than other young people. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | self_stigma_expect |
| Analysis index | SBI |
| Analysis dimension | self_stigma_expect |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS newly proposed stigma items; Recruitment Plan §7.3 |
| Analysis control note | Hypothetical wording; never claim this measures experienced internalised stigma. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 36 |
| Analysis implementation note | Four community + four self-stigma items. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 049 sbi_help_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_help_1 |
| Form Name | neps31_screening |
| Section Header | Help-seeking self-stigma |
| Field Type | radio |
| Field Label | Seeing a mental health provider would make me feel weak. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 40c82182ce6d4ec862d48f7fdb9f1142c1082cdcba856e5a795f4d216e628ab6 |
| Analysis label | Seeing a mental health provider would make me feel weak. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | help_seeking_self_stigma |
| Analysis index | SBI |
| Analysis dimension | help_seeking_self_stigma |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p15 items 5–7 |
| Analysis control note | Original Beliefs About Treatment Seeking has 8 items: remaining 5 are separate treatment barriers, not in SBI. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 37 |
| Analysis implementation note | Three help-seeking stigma items; completes SBI. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 050 sbi_help_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_help_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I would think less of myself if I were to seek mental health treatment. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | d9a237cd36fab33aba559f8e8a311e4d36cffaf606a39d69b546a5313c49d014 |
| Analysis label | I would think less of myself if I were to seek mental health treatment. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | help_seeking_self_stigma |
| Analysis index | SBI |
| Analysis dimension | help_seeking_self_stigma |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p15 items 5–7 |
| Analysis control note | Original Beliefs About Treatment Seeking has 8 items: remaining 5 are separate treatment barriers, not in SBI. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 38 |
| Analysis implementation note | Three help-seeking stigma items; completes SBI. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 051 sbi_help_3

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_help_3 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | If I sought mental health treatment, I would feel stupid for not being able to fix the problem on my own. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 9393ae293dca3bfcd2d9dc98241c1a8977591feec54936e57e916648d8fdd938 |
| Analysis label | If I sought mental health treatment, I would feel stupid for not being able to fix the problem on my own. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | help_seeking_self_stigma |
| Analysis index | SBI |
| Analysis dimension | help_seeking_self_stigma |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p15 items 5–7 |
| Analysis control note | Original Beliefs About Treatment Seeking has 8 items: remaining 5 are separate treatment barriers, not in SBI. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 39 |
| Analysis implementation note | Three help-seeking stigma items; completes SBI. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 052 k6_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | k6_1 |
| Form Name | neps31_screening |
| Section Header | Current psychological distress (K6) |
| Field Type | radio |
| Field Label | During the past 30 days, how often did you feel nervous? |
| Choices, Calculations, OR Slider Labels | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 929106ef0926891c30bc3b051516dc2b8924ee137c9c69cea398dd975c80bd41 |
| Analysis label | During the past 30 days, how often did you feel nervous? |
| Analysis response definition | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Analysis construct | K6 |
| Analysis index | MHDI |
| Analysis dimension | K6 |
| Analysis reference period | Past 30 days |
| Analysis applicability | all eligible |
| Analysis provenance | Kessler et al (2003), official Harvard scale; NEW relative to V2 |
| Analysis control note | Verify and reproduce precise authorised official K6 wording by edition; scale freely usable with citation; score 0–24; standardise x/24×100; no imported diagnostic cutoff. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 40 |
| Analysis implementation note | Retain all six K6 items as one contiguous block. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 053 k6_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | k6_2 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 30 days, how often did you feel hopeless? |
| Choices, Calculations, OR Slider Labels | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 7ca23be735b91b59b9fceb148b8f4854df12a39bffef4cd3af922a0db92bb7b6 |
| Analysis label | During the past 30 days, how often did you feel hopeless? |
| Analysis response definition | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Analysis construct | K6 |
| Analysis index | MHDI |
| Analysis dimension | K6 |
| Analysis reference period | Past 30 days |
| Analysis applicability | all eligible |
| Analysis provenance | Kessler et al (2003), official Harvard scale; NEW relative to V2 |
| Analysis control note | Verify and reproduce precise authorised official K6 wording by edition; scale freely usable with citation; score 0–24; standardise x/24×100; no imported diagnostic cutoff. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 41 |
| Analysis implementation note | Retain all six K6 items as one contiguous block. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 054 k6_3

| Property | Source definition |
| --- | --- |
| Variable / Field Name | k6_3 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 30 days, how often did you feel restless or fidgety? |
| Choices, Calculations, OR Slider Labels | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | e735dda5f9ee69b2a8d42a2ea8d9c2d249f358da5beec47c72bc73b71d50ac33 |
| Analysis label | During the past 30 days, how often did you feel restless or fidgety? |
| Analysis response definition | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Analysis construct | K6 |
| Analysis index | MHDI |
| Analysis dimension | K6 |
| Analysis reference period | Past 30 days |
| Analysis applicability | all eligible |
| Analysis provenance | Kessler et al (2003), official Harvard scale; NEW relative to V2 |
| Analysis control note | Verify and reproduce precise authorised official K6 wording by edition; scale freely usable with citation; score 0–24; standardise x/24×100; no imported diagnostic cutoff. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 42 |
| Analysis implementation note | Retain all six K6 items as one contiguous block. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 055 k6_4

| Property | Source definition |
| --- | --- |
| Variable / Field Name | k6_4 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 30 days, how often did you feel so depressed that nothing could cheer you up? |
| Choices, Calculations, OR Slider Labels | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 5193d6b1add3b5533339c4a35a2c13abe7126a6a5df0e025f2a2ed803e3a6a2b |
| Analysis label | During the past 30 days, how often did you feel so depressed that nothing could cheer you up? |
| Analysis response definition | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Analysis construct | K6 |
| Analysis index | MHDI |
| Analysis dimension | K6 |
| Analysis reference period | Past 30 days |
| Analysis applicability | all eligible |
| Analysis provenance | Kessler et al (2003), official Harvard scale; NEW relative to V2 |
| Analysis control note | Verify and reproduce precise authorised official K6 wording by edition; scale freely usable with citation; score 0–24; standardise x/24×100; no imported diagnostic cutoff. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 43 |
| Analysis implementation note | Retain all six K6 items as one contiguous block. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 056 k6_5

| Property | Source definition |
| --- | --- |
| Variable / Field Name | k6_5 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 30 days, how often did you feel that everything was an effort? |
| Choices, Calculations, OR Slider Labels | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 599d2e74e44c340d4b1d3f42d995798f3e5da3e2750467e6f6ceef8d738bf668 |
| Analysis label | During the past 30 days, how often did you feel that everything was an effort? |
| Analysis response definition | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Analysis construct | K6 |
| Analysis index | MHDI |
| Analysis dimension | K6 |
| Analysis reference period | Past 30 days |
| Analysis applicability | all eligible |
| Analysis provenance | Kessler et al (2003), official Harvard scale; NEW relative to V2 |
| Analysis control note | Verify and reproduce precise authorised official K6 wording by edition; scale freely usable with citation; score 0–24; standardise x/24×100; no imported diagnostic cutoff. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 44 |
| Analysis implementation note | Retain all six K6 items as one contiguous block. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 057 k6_6

| Property | Source definition |
| --- | --- |
| Variable / Field Name | k6_6 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | During the past 30 days, how often did you feel worthless? |
| Choices, Calculations, OR Slider Labels | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 2d53800fb2d194224abfbf4104716f050eaf435109edccbdd03975d822e3d0e9 |
| Analysis label | During the past 30 days, how often did you feel worthless? |
| Analysis response definition | 0, None of the time \| 1, A little of the time \| 2, Some of the time \| 3, Most of the time \| 4, All of the time |
| Analysis construct | K6 |
| Analysis index | MHDI |
| Analysis dimension | K6 |
| Analysis reference period | Past 30 days |
| Analysis applicability | all eligible |
| Analysis provenance | Kessler et al (2003), official Harvard scale; NEW relative to V2 |
| Analysis control note | Verify and reproduce precise authorised official K6 wording by edition; scale freely usable with citation; score 0–24; standardise x/24×100; no imported diagnostic cutoff. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 45 |
| Analysis implementation note | Retain all six K6 items as one contiguous block. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 058 brs_01

| Property | Source definition |
| --- | --- |
| Variable / Field Name | brs_01 |
| Form Name | neps31_screening |
| Section Header | Brief Resilience Scale (BRS) |
| Field Type | radio |
| Field Label | I tend to bounce back quickly after hard times. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 24ecc534f0391997e8c32c65c0ca0752bde3f1f5440c3468e5ee2e411b7dd8cf |
| Analysis label | I tend to bounce back quickly after hard times. |
| Analysis response definition | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Analysis construct | resilience |
| Analysis index | PFI |
| Analysis dimension | resilience |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p21; Smith et al 2008 |
| Analysis control note | BRS mean (1–5), normalised (mean−1)/4×100; reverse 2,4,6. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 46 |
| Analysis implementation note | Keep original six-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 059 brs_02

| Property | Source definition |
| --- | --- |
| Variable / Field Name | brs_02 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I have a hard time making it through stressful events. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | e2665388b0c93b3a56e305eb736aeb25c3814ecbb50ad5685da6c9ae3ec14a3b |
| Analysis label | I have a hard time making it through stressful events. |
| Analysis response definition | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Analysis construct | resilience |
| Analysis index | PFI |
| Analysis dimension | resilience |
| Analysis applicability | all eligible |
| Analysis scoring direction | 6−raw |
| Analysis provenance | V2 p21; Smith et al 2008 |
| Analysis control note | BRS mean (1–5), normalised (mean−1)/4×100; reverse 2,4,6. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 47 |
| Analysis implementation note | Keep original six-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 060 brs_03

| Property | Source definition |
| --- | --- |
| Variable / Field Name | brs_03 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | It does not take me long to recover from a stressful event. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 84a7424554e5735c3c7a40d22fd49830380ef6a424b033af500358d1b50f8652 |
| Analysis label | It does not take me long to recover from a stressful event. |
| Analysis response definition | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Analysis construct | resilience |
| Analysis index | PFI |
| Analysis dimension | resilience |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p21; Smith et al 2008 |
| Analysis control note | BRS mean (1–5), normalised (mean−1)/4×100; reverse 2,4,6. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 48 |
| Analysis implementation note | Keep original six-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 061 brs_04

| Property | Source definition |
| --- | --- |
| Variable / Field Name | brs_04 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | It is hard for me to snap back when something bad happens. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 669ed9f386644544f983044a7cd1ec4deea8f80ef84b144799dbe2956bde6f0f |
| Analysis label | It is hard for me to snap back when something bad happens. |
| Analysis response definition | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Analysis construct | resilience |
| Analysis index | PFI |
| Analysis dimension | resilience |
| Analysis applicability | all eligible |
| Analysis scoring direction | 6−raw |
| Analysis provenance | V2 p21; Smith et al 2008 |
| Analysis control note | BRS mean (1–5), normalised (mean−1)/4×100; reverse 2,4,6. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 49 |
| Analysis implementation note | Keep original six-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 062 brs_05

| Property | Source definition |
| --- | --- |
| Variable / Field Name | brs_05 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I usually come through difficult times with little trouble. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | b47d9d6e2beb1a08acf6a6f42d3f72c018cfd8654d99c42c920704e1a2a98cc6 |
| Analysis label | I usually come through difficult times with little trouble. |
| Analysis response definition | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Analysis construct | resilience |
| Analysis index | PFI |
| Analysis dimension | resilience |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p21; Smith et al 2008 |
| Analysis control note | BRS mean (1–5), normalised (mean−1)/4×100; reverse 2,4,6. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 50 |
| Analysis implementation note | Keep original six-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 063 brs_06

| Property | Source definition |
| --- | --- |
| Variable / Field Name | brs_06 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I tend to take a long time to get over set-backs in my life. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f5aca072351caa8a42014305726014b0baa8004428894a990a5d26d2798f0607 |
| Analysis label | I tend to take a long time to get over set-backs in my life. |
| Analysis response definition | 1, Strongly disagree \| 2, Disagree \| 3, Neutral \| 4, Agree \| 5, Strongly agree |
| Analysis construct | resilience |
| Analysis index | PFI |
| Analysis dimension | resilience |
| Analysis applicability | all eligible |
| Analysis scoring direction | 6−raw |
| Analysis provenance | V2 p21; Smith et al 2008 |
| Analysis control note | BRS mean (1–5), normalised (mean−1)/4×100; reverse 2,4,6. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 51 |
| Analysis implementation note | Keep original six-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 064 mspss_01

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_01 |
| Form Name | neps31_screening |
| Section Header | Perceived social support (MSPSS) |
| Field Type | radio |
| Field Label | There is a special person who is around when I am in need. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | e639c0634d3fe5e98e4d9baecf8c691be99ecb7e4c593dacd8757efe96f9df87 |
| Analysis label | There is a special person who is around when I am in need. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 52 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 065 mspss_02

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_02 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | There is a special person with whom I can share joys and sorrows. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | c486c158eafac613db20c978fedc696d5cfc7b753a69a89cf1cf963d2bfd2109 |
| Analysis label | There is a special person with whom I can share joys and sorrows. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 53 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 066 mspss_03

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_03 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | My family really tries to help me. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 8c0229196b538f9c7cc53d3fce7009b5ec98e59f8a8a89f779d9430ee8de8b7d |
| Analysis label | My family really tries to help me. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 54 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 067 mspss_04

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_04 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I get the emotional help and support I need from my family. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | ea51d122a7842d0581c03da206629d81b4f56e50591a5d2fe968ae7b8822cb90 |
| Analysis label | I get the emotional help and support I need from my family. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 55 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 068 mspss_05

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_05 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I have a special person who is a real source of comfort to me. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | e32b1f1429dd9cc1932199d9fb407fca4289b1f8b48081fd385fd205a33380cd |
| Analysis label | I have a special person who is a real source of comfort to me. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 56 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 069 mspss_06

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_06 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | My friends really try to help me. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | fded16e9c9b126b975b781eb24151c9d02682b3bfb05bd00c0e1a3aa7270a7c3 |
| Analysis label | My friends really try to help me. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 57 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 070 mspss_07

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_07 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I can count on my friends when things go wrong. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 28f215d73e473e69c6ccc12de17cc5afb8671f859e23f68c53febd2395f2b9df |
| Analysis label | I can count on my friends when things go wrong. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 58 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 071 mspss_08

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_08 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I can talk about my problems with my family. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 8f23b6d69d9e8868d9682ab668b509b18b22f4ff2cdb71e2123ed39d14e20993 |
| Analysis label | I can talk about my problems with my family. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 59 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 072 mspss_09

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_09 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I have friends with whom I can share my joys and sorrows. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | be18813f1ec9d4d85cc860f50bc44fe8c1f1ce2db616311c835a9720771980f3 |
| Analysis label | I have friends with whom I can share my joys and sorrows. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 60 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 073 mspss_10

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_10 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | There is a special person in my life who cares about my feelings. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | fc907bbcee31ef320fd2cbc111340cf875b3072ad3c6ad807c6c863d4bfee377 |
| Analysis label | There is a special person in my life who cares about my feelings. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 61 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 074 mspss_11

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_11 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | My family is willing to help me make decisions. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 4bf070ff7c6d1135f185d94bebb913bbdc66d01a8b3f28c34fabf92a699e1de0 |
| Analysis label | My family is willing to help me make decisions. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 62 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 075 mspss_12

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_12 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I can talk about my problems with my friends. |
| Choices, Calculations, OR Slider Labels | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 5f771e99921cde469a187904b12c7ffb508b04d7cf9b8ceebe375b3aeac8b98f |
| Analysis label | I can talk about my problems with my friends. |
| Analysis response definition | 1, Very strongly disagree \| 2, Strongly disagree \| 3, Mildly disagree \| 4, Neutral \| 5, Mildly agree \| 6, Strongly agree \| 7, Very strongly agree |
| Analysis construct | social_support |
| Analysis index | PFI |
| Analysis dimension | social_support |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp13–14; Zimet et al 1988 |
| Analysis control note | MSPSS overall mean 1–7; (mean−1)/6×100. Subscales: SO 1/2/5/10, family 3/4/8/11, friend 6/7/9/12. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 63 |
| Analysis implementation note | Keep original twelve-item scale intact. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 076 gse_01

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_01 |
| Form Name | neps31_screening |
| Section Header | General Self-Efficacy (GSE) |
| Field Type | radio |
| Field Label | I can always manage to solve difficult problems if I try hard enough. |
| Choices, Calculations, OR Slider Labels | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 6d6e01c61c93b015eeef9a877e52fe4c0cfdf34515553632b1b6742e8543ccd0 |
| Analysis label | I can always manage to solve difficult problems if I try hard enough. |
| Analysis response definition | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Analysis construct | self_efficacy |
| Analysis index | PFI |
| Analysis dimension | self_efficacy |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p25; Schwarzer &amp; Jerusalem 1995 |
| Analysis control note | GSE sum 10–40; (sum−10)/30×100; no reversals. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 64 |
| Analysis implementation note | Keep original ten-item scale intact; screening ends here. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 077 gse_02

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_02 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | If someone opposes me, I can find the means and ways to get what I want. |
| Choices, Calculations, OR Slider Labels | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 906d32e2bc6b200feb0b38b5c7e0dfde7fc9b1c028abe4e2bca73d0e2c6f0a40 |
| Analysis label | If someone opposes me, I can find the means and ways to get what I want. |
| Analysis response definition | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Analysis construct | self_efficacy |
| Analysis index | PFI |
| Analysis dimension | self_efficacy |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p25; Schwarzer &amp; Jerusalem 1995 |
| Analysis control note | GSE sum 10–40; (sum−10)/30×100; no reversals. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 65 |
| Analysis implementation note | Keep original ten-item scale intact; screening ends here. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 078 gse_03

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_03 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | It is easy for me to stick to my aims and accomplish my goals. |
| Choices, Calculations, OR Slider Labels | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 86a692c8c96bccedcccbf2c744185bf758f084f39223dd74fe07852509e261dc |
| Analysis label | It is easy for me to stick to my aims and accomplish my goals. |
| Analysis response definition | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Analysis construct | self_efficacy |
| Analysis index | PFI |
| Analysis dimension | self_efficacy |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p25; Schwarzer &amp; Jerusalem 1995 |
| Analysis control note | GSE sum 10–40; (sum−10)/30×100; no reversals. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 66 |
| Analysis implementation note | Keep original ten-item scale intact; screening ends here. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 079 gse_04

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_04 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I am confident that I could deal efficiently with unexpected events. |
| Choices, Calculations, OR Slider Labels | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 0abec5872d36d1f031ee798111afe559784fa52711f044d4fa6c15e3976cbdb4 |
| Analysis label | I am confident that I could deal efficiently with unexpected events. |
| Analysis response definition | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Analysis construct | self_efficacy |
| Analysis index | PFI |
| Analysis dimension | self_efficacy |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p25; Schwarzer &amp; Jerusalem 1995 |
| Analysis control note | GSE sum 10–40; (sum−10)/30×100; no reversals. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 67 |
| Analysis implementation note | Keep original ten-item scale intact; screening ends here. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 080 gse_05

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_05 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | Thanks to my resourcefulness, I know how to handle unforeseen situations. |
| Choices, Calculations, OR Slider Labels | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 0086dd13d77c2463ccffe49e3d5b7cbb3d3d6fe32ed34f36be9a072b3860248d |
| Analysis label | Thanks to my resourcefulness, I know how to handle unforeseen situations. |
| Analysis response definition | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Analysis construct | self_efficacy |
| Analysis index | PFI |
| Analysis dimension | self_efficacy |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p25; Schwarzer &amp; Jerusalem 1995 |
| Analysis control note | GSE sum 10–40; (sum−10)/30×100; no reversals. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 68 |
| Analysis implementation note | Keep original ten-item scale intact; screening ends here. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 081 gse_06

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_06 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I can solve most problems if I invest the necessary effort. |
| Choices, Calculations, OR Slider Labels | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 95ca5dd029e4df8d8312caff6132fbd37cb32f9cf740ad503b8cbaafcdd02176 |
| Analysis label | I can solve most problems if I invest the necessary effort. |
| Analysis response definition | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Analysis construct | self_efficacy |
| Analysis index | PFI |
| Analysis dimension | self_efficacy |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p25; Schwarzer &amp; Jerusalem 1995 |
| Analysis control note | GSE sum 10–40; (sum−10)/30×100; no reversals. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 69 |
| Analysis implementation note | Keep original ten-item scale intact; screening ends here. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 082 gse_07

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_07 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I can remain calm when facing difficulties because I can rely on my coping abilities. |
| Choices, Calculations, OR Slider Labels | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | aa5f39778f45ec3eb93edba1e0b365c6135183be7739384ca400e9f89303e92b |
| Analysis label | I can remain calm when facing difficulties because I can rely on my coping abilities. |
| Analysis response definition | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Analysis construct | self_efficacy |
| Analysis index | PFI |
| Analysis dimension | self_efficacy |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p25; Schwarzer &amp; Jerusalem 1995 |
| Analysis control note | GSE sum 10–40; (sum−10)/30×100; no reversals. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 70 |
| Analysis implementation note | Keep original ten-item scale intact; screening ends here. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 083 gse_08

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_08 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | When I am confronted with a problem, I can usually find several solutions. |
| Choices, Calculations, OR Slider Labels | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | c2b413c9fbeaf58ac2f6aa48910855ebc433c7c55f3f884e48b1eda50d2d2218 |
| Analysis label | When I am confronted with a problem, I can usually find several solutions. |
| Analysis response definition | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Analysis construct | self_efficacy |
| Analysis index | PFI |
| Analysis dimension | self_efficacy |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p25; Schwarzer &amp; Jerusalem 1995 |
| Analysis control note | GSE sum 10–40; (sum−10)/30×100; no reversals. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 71 |
| Analysis implementation note | Keep original ten-item scale intact; screening ends here. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 084 gse_09

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_09 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | If I am in trouble, I can usually think of a solution. |
| Choices, Calculations, OR Slider Labels | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 4e6bf6ce6ce84416b3ce7981113a98294cd10aa95bf3a3719591ead74cab742e |
| Analysis label | If I am in trouble, I can usually think of a solution. |
| Analysis response definition | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Analysis construct | self_efficacy |
| Analysis index | PFI |
| Analysis dimension | self_efficacy |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p25; Schwarzer &amp; Jerusalem 1995 |
| Analysis control note | GSE sum 10–40; (sum−10)/30×100; no reversals. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 72 |
| Analysis implementation note | Keep original ten-item scale intact; screening ends here. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 085 gse_10

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_10 |
| Form Name | neps31_screening |
| Field Type | radio |
| Field Label | I can usually handle whatever comes my way. |
| Choices, Calculations, OR Slider Labels | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | Yes |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | af648673145616131342990553848e9c51d8acb0a989785fbeaa5d4121626abf |
| Analysis label | I can usually handle whatever comes my way. |
| Analysis response definition | 1, Not at all true \| 2, Hardly true \| 3, Moderately true \| 4, Exactly true |
| Analysis construct | self_efficacy |
| Analysis index | PFI |
| Analysis dimension | self_efficacy |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p25; Schwarzer &amp; Jerusalem 1995 |
| Analysis control note | GSE sum 10–40; (sum−10)/30×100; no reversals. |
| Analysis administration stage | 01 NSES |
| Analysis respondent order | 73 |
| Analysis implementation note | Keep original ten-item scale intact; screening ends here. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 086 willing_24m

| Property | Source definition |
| --- | --- |
| Variable / Field Name | willing_24m |
| Form Name | neps31_cohort_interest |
| Section Header | Longitudinal follow-up interest |
| Field Type | radio |
| Field Label | Willing to be followed up for 24 months? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not applicable; 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 92038ec5fdd922c8cb8328f6552621e2f73f2f315d4297d0d08f1dfd3cbee753 |
| Analysis label | Willing to be followed up for 24 months? |
| Analysis response definition | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 02 Cohort |
| Analysis respondent order | 74 |
| Analysis implementation note | Exactly five willingness/availability questions; not consent or automatic selection. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 087 contact_24m

| Property | Source definition |
| --- | --- |
| Variable / Field Name | contact_24m |
| Form Name | neps31_cohort_interest |
| Field Type | radio |
| Field Label | Available for planned 24-month follow-up? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not applicable; 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 7d15409a00b0d7a997383c768a1057d9c682308bc7d56cdf496b4baca5d899ce |
| Analysis label | Available for planned 24-month follow-up? |
| Analysis response definition | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 02 Cohort |
| Analysis respondent order | 75 |
| Analysis implementation note | Exactly five willingness/availability questions; not consent or automatic selection. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 088 wp3_willing

| Property | Source definition |
| --- | --- |
| Variable / Field Name | wp3_willing |
| Form Name | neps31_cohort_interest |
| Field Type | radio |
| Field Label | Willing to be considered for WP3 biological and neurocognitive assessments, subject to consent and eligibility? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not applicable; 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 135bfc91fdd0d163b90d889fbae1796f540f97b249c8e05eca43f6ba20a845c1 |
| Analysis label | Willing to be considered for WP3 biological and neurocognitive assessments, subject to consent and eligibility? |
| Analysis response definition | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 02 Cohort |
| Analysis respondent order | 76 |
| Analysis implementation note | Exactly five willingness/availability questions; not consent or automatic selection. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 089 wp4_willing

| Property | Source definition |
| --- | --- |
| Variable / Field Name | wp4_willing |
| Form Name | neps31_cohort_interest |
| Field Type | radio |
| Field Label | Willing to participate in WP4 longitudinal psychosocial follow-up? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not applicable; 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 0c1ad8336f1940316a0dadd939798b6bd7551fe003ba20255187b3f21617be73 |
| Analysis label | Willing to participate in WP4 longitudinal psychosocial follow-up? |
| Analysis response definition | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 02 Cohort |
| Analysis respondent order | 77 |
| Analysis implementation note | Exactly five willingness/availability questions; not consent or automatic selection. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 090 wp6_willing

| Property | Source definition |
| --- | --- |
| Variable / Field Name | wp6_willing |
| Form Name | neps31_cohort_interest |
| Field Type | radio |
| Field Label | Willing to be considered for WP6 activities and follow-up, where appropriate? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not applicable; 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 68d05bbb25b0c36217114fc6902b98b7b3e2e707ca04e02d4e21c0b6723bceec |
| Analysis label | Willing to be considered for WP6 activities and follow-up, where appropriate? |
| Analysis response definition | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 02 Cohort |
| Analysis respondent order | 78 |
| Analysis implementation note | Exactly five willingness/availability questions; not consent or automatic selection. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 091 currently_school

| Property | Source definition |
| --- | --- |
| Variable / Field Name | currently_school |
| Form Name | neps31_extended_baseline |
| Section Header | Education and household profile |
| Field Type | radio |
| Field Label | Currently attending school, vocational training or tertiary education? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | d7f864d7a801f6634856f99d5bcec82f4c4f572767df6a0a97725d57b2630147 |
| Analysis label | Currently attending school, vocational training or tertiary education? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 79 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 092 ever_school

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ever_school |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Ever attended any form of school or formal training? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 2719bd8e6605e1f880ebb0e4ad4649a290bb631ac2296d7c723c8530cc04f6bb |
| Analysis label | Ever attended any form of school or formal training? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 80 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 093 school_level

| Property | Source definition |
| --- | --- |
| Variable / Field Name | school_level |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Current or most recent level of education |
| Choices, Calculations, OR Slider Labels | 1, Never attended \| 2, Primary \| 3, Junior secondary \| 4, Senior secondary \| 5, Technical/vocational \| 6, Tertiary \| 7, Postgraduate \| 8, Other |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 1843ba94e8288236b5dc418efef2047d3eda2cde47cd861ecdf0f6c949c55d02 |
| Analysis label | Current or most recent level of education |
| Analysis response definition | 1, Never attended \| 2, Primary \| 3, Junior secondary \| 4, Senior secondary \| 5, Technical/vocational \| 6, Tertiary \| 7, Postgraduate \| 8, Other |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 81 |
| Country display references | 33 rows; countries: Ghana, Sierra Leone, Tanzania; sources: Education_Level_Crosswalk_Country_Display.csv, NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 094 not_school_reason

| Property | Source definition |
| --- | --- |
| Variable / Field Name | not_school_reason |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Main reason for not currently attending |
| Choices, Calculations, OR Slider Labels | 1, Completed \| 2, Financial barriers \| 3, Discontinued \| 4, Working \| 5, Health or disability \| 6, Family responsibilities \| 7, Other \| 98, Do not know \| 99, Prefer not |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not. These labels apply to this field only. |
| Dictionary row SHA256 | 3d6c4d324d1034201fa70ea39a4df41600284d97c33359fda73821cc337a6922 |
| Analysis label | Main reason for not currently attending |
| Analysis response definition | 1, Completed \| 2, Financial barriers \| 3, Discontinued \| 4, Working \| 5, Health or disability \| 6, Family responsibilities \| 7, Other \| 98, Do not know \| 99, Prefer not |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 82 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 095 self_school_perf

| Property | Source definition |
| --- | --- |
| Variable / Field Name | self_school_perf |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | How do you rate your current or most recent academic performance? |
| Choices, Calculations, OR Slider Labels | 1, Very poor \| 2, Below average \| 3, Average \| 4, Above average \| 5, Excellent \| 96, Never attended \| 98, Do not know |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Never attended; 98, Do not know. These labels apply to this field only. |
| Dictionary row SHA256 | 486413821a4c38b23fe8313dc0019eb7e03ac4a428773e1c695b102121b5ab16 |
| Analysis label | How do you rate your current or most recent academic performance? |
| Analysis response definition | 1, Very poor \| 2, Below average \| 3, Average \| 4, Above average \| 5, Excellent \| 96, Never attended \| 98, Do not know |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 83 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 096 household_language

| Property | Source definition |
| --- | --- |
| Variable / Field Name | household_language |
| Form Name | neps31_extended_baseline |
| Field Type | text |
| Field Label | Main language spoken at home |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 3010b34af4f877e4909f78b187c4a9c2f73be465300e6b2ab89446f9b1232a1a |
| Analysis label | Main language spoken at home |
| Analysis response definition | Free text; limited/controlled as defined in notes |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 84 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 097 internet_home

| Property | Source definition |
| --- | --- |
| Variable / Field Name | internet_home |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Reliable access to internet at home? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 65559058446e99b7b46c842082a47c9be6e7f61763d326b9c5cacc3e965d6b56 |
| Analysis label | Reliable access to internet at home? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 85 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 098 father_ed

| Property | Source definition |
| --- | --- |
| Variable / Field Name | father_ed |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Father or relevant male caregiver highest education |
| Choices, Calculations, OR Slider Labels | 0, None \| 1, Primary \| 2, Secondary \| 3, Post-secondary \| 4, University or higher \| 96, Not applicable \| 98, Do not know \| 99, Prefer not |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not applicable; 98, Do not know; 99, Prefer not. These labels apply to this field only. |
| Dictionary row SHA256 | 30982951251fe41f5c545b0d7cfaf776952c8070ea9fef1c70aff1287d6188cf |
| Analysis label | Father or relevant male caregiver highest education |
| Analysis response definition | 0, None \| 1, Primary \| 2, Secondary \| 3, Post-secondary \| 4, University or higher \| 96, Not applicable \| 98, Do not know \| 99, Prefer not |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 86 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 099 mother_ed

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mother_ed |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Mother or relevant female caregiver highest education |
| Choices, Calculations, OR Slider Labels | 0, None \| 1, Primary \| 2, Secondary \| 3, Post-secondary \| 4, University or higher \| 96, Not applicable \| 98, Do not know \| 99, Prefer not |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not applicable; 98, Do not know; 99, Prefer not. These labels apply to this field only. |
| Dictionary row SHA256 | a47bc1ae334a954499804b3aaa77f2eeb8b34056b4dfeba04be2c36022dd045c |
| Analysis label | Mother or relevant female caregiver highest education |
| Analysis response definition | 0, None \| 1, Primary \| 2, Secondary \| 3, Post-secondary \| 4, University or higher \| 96, Not applicable \| 98, Do not know \| 99, Prefer not |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 87 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 100 household_members

| Property | Source definition |
| --- | --- |
| Variable / Field Name | household_members |
| Form Name | neps31_extended_baseline |
| Field Type | text |
| Field Label | Number of people usually living in household |
| Text Validation Type OR Show Slider Number | integer |
| Text Validation Min | 0 |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 47f1ef18bb53bae613b90d721277ec52b5a7d78acb4720862aadec41f11ce0dc |
| Analysis label | Number of people usually living in household |
| Analysis response definition | Non-negative integer |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 88 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 101 living_arrangement

| Property | Source definition |
| --- | --- |
| Variable / Field Name | living_arrangement |
| Form Name | neps31_extended_baseline |
| Section Header | Family, caregiving and current context |
| Field Type | radio |
| Field Label | Who do you currently live with? |
| Choices, Calculations, OR Slider Labels | 1, Parent(s) \| 2, Other caregiver(s) \| 3, Partner/spouse \| 4, Other family \| 5, On my own \| 6, Shared accommodation \| 7, Other |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 0db49616f79bf6bbc2191e87c9a89712e1dcf2bfc4adbe91619806253fa310f1 |
| Analysis label | Who do you currently live with? |
| Analysis response definition | 1, Parent(s) \| 2, Other caregiver(s) \| 3, Partner/spouse \| 4, Other family \| 5, On my own \| 6, Shared accommodation \| 7, Other |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 pp2–3,8; Plan §§4,14 |
| Analysis control note | Exact choice lists for country harmonisation to be approved |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 89 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 102 caregiver_prim

| Property | Source definition |
| --- | --- |
| Variable / Field Name | caregiver_prim |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Who is mainly responsible for your day-to-day care or support? |
| Choices, Calculations, OR Slider Labels | 1, Parent \| 2, Grandparent \| 3, Other relative \| 4, Foster or non-relative caregiver \| 5, Partner \| 6, Self \| 7, Other \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | c2c6324c55dfd40b4efb5c4f87b904cbe6829f27a690a5c1cf7d09ce5447f3ac |
| Analysis label | Who is mainly responsible for your day-to-day care or support? |
| Analysis response definition | 1, Parent \| 2, Grandparent \| 3, Other relative \| 4, Foster or non-relative caregiver \| 5, Partner \| 6, Self \| 7, Other \| 99, Prefer not to answer |
| Analysis construct | B. Context |
| Analysis index | NONE |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 Family Structure p2–3 and NEPS V3.1 reconciliation; revised generic wording |
| Analysis control note | One contextual source only; not scored as NSES or adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 90 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 103 parent_alive

| Property | Source definition |
| --- | --- |
| Variable / Field Name | parent_alive |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Are both of your biological parents currently alive? |
| Choices, Calculations, OR Slider Labels | 1, Both \| 2, Only mother \| 3, Only father \| 4, Neither \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 2f2ab336ca0323737ddcb509683d2cc01a8779bf323f19a5fcc5876324e48d21 |
| Analysis label | Are both of your biological parents currently alive? |
| Analysis response definition | 1, Both \| 2, Only mother \| 3, Only father \| 4, Neither \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | B. Context |
| Analysis index | NONE |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 Family Structure p2–3 and NEPS V3.1 reconciliation; revised generic wording |
| Analysis control note | One contextual source only; not scored as NSES or adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 91 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 104 caregiver_abroad

| Property | Source definition |
| --- | --- |
| Variable / Field Name | caregiver_abroad |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Does a parent or principal caregiver currently live outside the country? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 5071cc69a89cc10aa45f3d0162622bf745c64a58cedd78290f2f2d5b7f1af185 |
| Analysis label | Does a parent or principal caregiver currently live outside the country? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | B. Context |
| Analysis index | NONE |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 Family Structure p2–3 and NEPS V3.1 reconciliation; revised generic wording |
| Analysis control note | One contextual source only; not scored as NSES or adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 92 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 105 caregiver_education

| Property | Source definition |
| --- | --- |
| Variable / Field Name | caregiver_education |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | What is the highest education level completed by your main caregiver, if different from your parents? |
| Choices, Calculations, OR Slider Labels | 0, None \| 1, Primary \| 2, Secondary \| 3, Post-secondary non-university \| 4, University or above \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not applicable; 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 2793451a60750f2c1e8805f4eb2dda98d202f5f4b4417eb1b93b9653a03d1fa6 |
| Analysis label | What is the highest education level completed by your main caregiver, if different from your parents? |
| Analysis response definition | 0, None \| 1, Primary \| 2, Secondary \| 3, Post-secondary non-university \| 4, University or above \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | B. Context |
| Analysis index | NONE |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 Family Structure p2–3 and NEPS V3.1 reconciliation; revised generic wording |
| Analysis control note | One contextual source only; not scored as NSES or adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 93 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 106 family_mh_hist

| Property | Source definition |
| --- | --- |
| Variable / Field Name | family_mh_hist |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | As far as you know, has a close family member ever experienced a diagnosed mental health condition? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 523335aada8c59ced3c480026e14db9af6c32efc1af1c0441cac6dbdcacf86c6 |
| Analysis label | As far as you know, has a close family member ever experienced a diagnosed mental health condition? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | B. Context |
| Analysis index | NONE |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 Family Structure p2–3 and NEPS V3.1 reconciliation; revised generic wording |
| Analysis control note | One contextual source only; not scored as NSES or adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 94 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 107 school_days_missed

| Property | Source definition |
| --- | --- |
| Variable / Field Name | school_days_missed |
| Form Name | neps31_extended_baseline |
| Field Type | dropdown |
| Field Label | During the past 30 days, on how many days did you miss school or training when you would otherwise have attended? |
| Choices, Calculations, OR Slider Labels | 0, 0 days \| 1, 1 day \| 2, 2 days \| 3, 3 days \| 4, 4 days \| 5, 5 days \| 6, 6 days \| 7, 7 days \| 8, 8 days \| 9, 9 days \| 10, 10 days \| 11, 11 days \| 12, 12 days \| 13, 13 days \| 14, 14 days \| 15, 15 days \| 16, 16 days \| 17, 17 days \| 18, 18 days \| 19, 19 days \| 20, 20 days \| 21, 21 days \| 22, 22 days \| 23, 23 days \| 24, 24 days \| 25, 25 days \| 26, 26 days \| 27, 27 days \| 28, 28 days \| 29, 29 days \| 30, 30 days \| 96, Not attending school/training \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Answers are 0–30 days, or an applicable non-numeric response code. Matches the original response specification. |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not attending school/training; 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 900567b6dab2c8e8e5cbe5d264560017d7faa39652dda7257c0981232983cb6a |
| Analysis label | During the past 30 days, on how many days did you miss school or training when you would otherwise have attended? |
| Analysis response definition | 0–30, Number of days \| 96, Not attending school or training \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | B. Education |
| Analysis index | NONE |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 Family Structure p2–3 and NEPS V3.1 reconciliation; revised generic wording |
| Analysis control note | One contextual source only; not scored as NSES or adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 95 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 108 work_status

| Property | Source definition |
| --- | --- |
| Variable / Field Name | work_status |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Are you currently doing paid work or regular unpaid work for a household or family business? |
| Choices, Calculations, OR Slider Labels | 0, Neither \| 1, Paid work \| 2, Unpaid family work \| 3, Both \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 68d116d7747348aa6e71eedfc5a718b60bf7753751ec1c714cbff1bf26d572d9 |
| Analysis label | Are you currently doing paid work or regular unpaid work for a household or family business? |
| Analysis response definition | 0, Neither \| 1, Paid work \| 2, Unpaid family work \| 3, Both \| 99, Prefer not to answer |
| Analysis construct | B. Context |
| Analysis index | NONE |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 Family Structure p2–3 and NEPS V3.1 reconciliation; revised generic wording |
| Analysis control note | One contextual source only; not scored as NSES or adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 96 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 109 care_duties

| Property | Source definition |
| --- | --- |
| Variable / Field Name | care_duties |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | During the past 30 days, how often did caring for others in your household affect your study, training, work or usual activities? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often \| 96, No such responsibilities |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, No such responsibilities. These labels apply to this field only. |
| Dictionary row SHA256 | 8be9687bc9a33220c4f55fd4c8ef3f676f945ddb48b52da318927f86731faeab |
| Analysis label | During the past 30 days, how often did caring for others in your household affect your study, training, work or usual activities? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often \| 96, No such responsibilities |
| Analysis construct | B. Context |
| Analysis index | NONE |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 Family Structure p2–3 and NEPS V3.1 reconciliation; revised generic wording |
| Analysis control note | One contextual source only; not scored as NSES or adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 97 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 110 epix_exams_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epix_exams_1 |
| Form Name | neps31_extended_baseline |
| Section Header | Additional school/training pressure |
| Field Type | radio |
| Field Label | Upcoming examinations or assessments cause me stress. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | If hidden by branching, REDCap stores blank, NOT numeric code 96. Handle structural not-applicable on export/analysis. |
| Branching Logic (Show field only if...) | [currently_school] = '1' |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 41ba87eceb8ad0e2d88aa853171f0ba9d1f6cbc0a632547fa4fd6ca92f1d56ee |
| Analysis label | Upcoming examinations or assessments cause me stress. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | exams |
| Analysis index | EPI_EXT |
| Analysis dimension | exams |
| Analysis applicability | currently_school=1; otherwise NA=96 |
| Analysis provenance | NEPS new proposed items; Plan §7.1 |
| Analysis control note | Compute separate school-context extension only. Do not count in cross-school-status EPI core. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 98 |
| Analysis implementation note | Applicability uses currently_school collected in B1. |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 111 epix_exams_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epix_exams_2 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | I find it difficult to relax because of examination or assessment expectations. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | If hidden by branching, REDCap stores blank, NOT numeric code 96. Handle structural not-applicable on export/analysis. |
| Branching Logic (Show field only if...) | [currently_school] = '1' |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 15fc3185d1c9e054e7ddc3cf4fc14922ac895ce244e95f3f043e764983e8ced0 |
| Analysis label | I find it difficult to relax because of examination or assessment expectations. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | exams |
| Analysis index | EPI_EXT |
| Analysis dimension | exams |
| Analysis applicability | currently_school=1; otherwise NA=96 |
| Analysis provenance | NEPS new proposed items; Plan §7.1 |
| Analysis control note | Compute separate school-context extension only. Do not count in cross-school-status EPI core. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 99 |
| Analysis implementation note | Applicability uses currently_school collected in B1. |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 112 epix_teacher_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epix_teacher_1 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | I feel under pressure to meet expectations set by teachers or trainers. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | If hidden by branching, REDCap stores blank, NOT numeric code 96. Handle structural not-applicable on export/analysis. |
| Branching Logic (Show field only if...) | [currently_school] = '1' |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 5367997404b1b4ae376ee6a41032913d9bd4040499659e2ea85797dcea7f2383 |
| Analysis label | I feel under pressure to meet expectations set by teachers or trainers. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | teacher |
| Analysis index | EPI_EXT |
| Analysis dimension | teacher |
| Analysis applicability | currently_school=1; otherwise NA=96 |
| Analysis provenance | NEPS new proposed items; Plan §7.1 |
| Analysis control note | Compute separate school-context extension only. Do not count in cross-school-status EPI core. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 100 |
| Analysis implementation note | Applicability uses currently_school collected in B1. |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 113 epix_teacher_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epix_teacher_2 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | The way teachers or trainers respond to my performance makes me feel pressured. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Field Note | If hidden by branching, REDCap stores blank, NOT numeric code 96. Handle structural not-applicable on export/analysis. |
| Branching Logic (Show field only if...) | [currently_school] = '1' |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | aed129971410d3ed72d51193c8d09672dc4da5b3d29baf5ca130dd7f8d32ea24 |
| Analysis label | The way teachers or trainers respond to my performance makes me feel pressured. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | teacher |
| Analysis index | EPI_EXT |
| Analysis dimension | teacher |
| Analysis applicability | currently_school=1; otherwise NA=96 |
| Analysis provenance | NEPS new proposed items; Plan §7.1 |
| Analysis control note | Compute separate school-context extension only. Do not count in cross-school-status EPI core. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 101 |
| Analysis implementation note | Applicability uses currently_school collected in B1. |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 114 asset_01

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_01 |
| Form Name | neps31_extended_baseline |
| Section Header | Household resources: possessions and electricity |
| Field Type | radio |
| Field Label | Does your household own a television set? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | f7eea6113bffd41d77410c7a96c95382009aa80dae8deceb3aee0a4f105652d3 |
| Analysis label | Does your household own a television set? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | asset |
| Analysis index | DEPRIVATION |
| Analysis dimension | asset |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 1–8 |
| Analysis control note | Proxy not IWI; unusual grouping of basic/expensive utensils needs redesign. Assets vary by country. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 102 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 115 asset_02

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_02 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Does your household own a refrigerator? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | a6844eb4726021e6632e8623e7d4f970df98c1f7b2333d1a88152fd8a4aa597d |
| Analysis label | Does your household own a refrigerator? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | asset |
| Analysis index | DEPRIVATION |
| Analysis dimension | asset |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 1–8 |
| Analysis control note | Proxy not IWI; unusual grouping of basic/expensive utensils needs redesign. Assets vary by country. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 103 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 116 asset_03

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_03 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Does your household own a telephone (mobile or landline)? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | af453c41440c61fba76de3763c8867e7f031d9d2d96a2daed6b705cad72cd114 |
| Analysis label | Does your household own a telephone (mobile or landline)? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | asset |
| Analysis index | DEPRIVATION |
| Analysis dimension | asset |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 1–8 |
| Analysis control note | Proxy not IWI; unusual grouping of basic/expensive utensils needs redesign. Assets vary by country. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 104 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 117 asset_04

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_04 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Does your household own a bicycle? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | aca195df9ec2884d51aa46347b1a2ca7fd9d477dd2aef22910edf2371d7d2055 |
| Analysis label | Does your household own a bicycle? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | asset |
| Analysis index | DEPRIVATION |
| Analysis dimension | asset |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 1–8 |
| Analysis control note | Proxy not IWI; unusual grouping of basic/expensive utensils needs redesign. Assets vary by country. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 105 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 118 asset_05

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_05 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Does your household own a car? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | c8fc4b7bca9c8ccd38859aa1cd90d9845564e9a31414397f8f3844bbacd2a8ff |
| Analysis label | Does your household own a car? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | asset |
| Analysis index | DEPRIVATION |
| Analysis dimension | asset |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 1–8 |
| Analysis control note | Proxy not IWI; unusual grouping of basic/expensive utensils needs redesign. Assets vary by country. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 106 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 119 asset_06

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_06 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Does your household own any of the listed basic household items (table, clock, kettle, radio, fan or blender)? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 815625bb492229d0470a7f7a96ef9bf38526a85681ade8cd0db3e99b82ed577c |
| Analysis label | Does your household own any of the listed basic household items (table, clock, kettle, radio, fan or blender)? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | asset |
| Analysis index | DEPRIVATION |
| Analysis dimension | asset |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 1–8 |
| Analysis control note | Proxy not IWI; unusual grouping of basic/expensive utensils needs redesign. Assets vary by country. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 107 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 120 asset_07

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_07 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Does your household own any of the listed larger household items (washing machine, computer, motorcycle, air conditioner or generator)? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 1720cdf7a7bfc06132e8f0384faea72abcd6b9e4693f2d9222e1225f0cfa8fba |
| Analysis label | Does your household own any of the listed larger household items (washing machine, computer, motorcycle, air conditioner or generator)? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | asset |
| Analysis index | DEPRIVATION |
| Analysis dimension | asset |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 1–8 |
| Analysis control note | Proxy not IWI; unusual grouping of basic/expensive utensils needs redesign. Assets vary by country. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 108 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 121 asset_08

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_08 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Does your home have access to electricity? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 1f5a5a146ac9ac4652fec357d0dc41a85cb06d9e30a2f014e022526c6a1d1c65 |
| Analysis label | Does your home have access to electricity? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | asset |
| Analysis index | DEPRIVATION |
| Analysis dimension | asset |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 1–8 |
| Analysis control note | Proxy not IWI; unusual grouping of basic/expensive utensils needs redesign. Assets vary by country. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 109 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 122 asset_water

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_water |
| Form Name | neps31_extended_baseline |
| Section Header | Household resources: water, toilet, floor and rooms |
| Field Type | radio |
| Field Label | What is the primary drinking-water source used by the household? |
| Choices, Calculations, OR Slider Labels | 1, Surface water \| 2, Unprotected well \| 3, Borehole \| 4, Protected well \| 5, Public tap \| 6, Private tap \| 7, Sachet/bottled \| 8, Tanker \| 9, Other \| 98, Do not know |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know. These labels apply to this field only. |
| Dictionary row SHA256 | 0bdbaff444bbe33f00bb9c0d8385d136d95a6a162ea257f9ff08115b9f647774 |
| Analysis label | What is the primary drinking-water source used by the household? |
| Analysis response definition | 1, Surface water \| 2, Unprotected well \| 3, Borehole \| 4, Protected well \| 5, Public tap \| 6, Private tap \| 7, Sachet/bottled \| 8, Tanker \| 9, Other \| 98, Do not know |
| Analysis construct | water |
| Analysis index | DEPRIVATION |
| Analysis dimension | water |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 9–12 |
| Analysis control note | IWI coding: borehole and protected well are middle-quality per Global Data Lab; record raw water type here, not low/medium/high label. Published coefficients needed. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 110 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 123 asset_toilet

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_toilet |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | What toilet or sanitation facility does the household mainly use? |
| Choices, Calculations, OR Slider Labels | 1, None/open defaecation \| 2, Pit latrine \| 3, Public toilet \| 4, KVIP \| 5, Private flush \| 6, Other \| 98, Do not know |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know. These labels apply to this field only. |
| Dictionary row SHA256 | c295e9c795bfcffe11005878f88f88975c65265c799ac49f48c11bbaf687d44c |
| Analysis label | What toilet or sanitation facility does the household mainly use? |
| Analysis response definition | 1, None/open defaecation \| 2, Pit latrine \| 3, Public toilet \| 4, KVIP \| 5, Private flush \| 6, Other \| 98, Do not know |
| Analysis construct | toilet |
| Analysis index | DEPRIVATION |
| Analysis dimension | toilet |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 9–12 |
| Analysis control note | Avoid V2 judgement that boreholes are inherently low-quality. Capture actual categories before deriving context-specific metrics. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 111 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 124 asset_floor

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_floor |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | What is the main floor material in the home? |
| Choices, Calculations, OR Slider Labels | 1, Earth/soil \| 2, Concrete/cement \| 3, Wood \| 4, Tiles/terrazzo \| 5, Other \| 98, Do not know |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know. These labels apply to this field only. |
| Dictionary row SHA256 | a666819b0adbcee4bd42a21bb850c39d75981d7232446428ca79060836268ae7 |
| Analysis label | What is the main floor material in the home? |
| Analysis response definition | 1, Earth/soil \| 2, Concrete/cement \| 3, Wood \| 4, Tiles/terrazzo \| 5, Other \| 98, Do not know |
| Analysis construct | floor |
| Analysis index | DEPRIVATION |
| Analysis dimension | floor |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 9–12 |
| Analysis control note | Avoid V2 judgement that boreholes are inherently low-quality. Capture actual categories before deriving context-specific metrics. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 112 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 125 asset_sleeprooms

| Property | Source definition |
| --- | --- |
| Variable / Field Name | asset_sleeprooms |
| Form Name | neps31_extended_baseline |
| Field Type | text |
| Field Label | How many sleeping rooms does the household use? |
| Text Validation Type OR Show Slider Number | integer |
| Text Validation Min | 0 |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 59d9deffaf8b28685850eafcb4ce35d35f3ec861df6fd7ee6179aecf4083b223 |
| Analysis label | How many sleeping rooms does the household use? |
| Analysis response definition | Non-negative integer |
| Analysis construct | sleeprooms |
| Analysis index | DEPRIVATION |
| Analysis dimension | sleeprooms |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p4 Wealth Index items 9–12 |
| Analysis control note | Avoid V2 judgement that boreholes are inherently low-quality. Capture actual categories before deriving context-specific metrics. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 113 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 126 sbi_exp_gate

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_exp_gate |
| Form Name | neps31_extended_baseline |
| Section Header | Experienced stigma |
| Field Type | radio |
| Field Label | During the past 12 months, did you experience emotional or mental health difficulties that someone else knew about? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Past 12 months |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not applicable; 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | ae1d1fd9e105b891230ebeef9815c2ccab01abaddc8d82487379a60b8e55a305 |
| Analysis label | During the past 12 months, did you experience emotional or mental health difficulties that someone else knew about? |
| Analysis response definition | 0, No \| 1, Yes \| 96, Not applicable \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | experienced |
| Analysis index | SBI_CONTEXT |
| Analysis dimension | experienced |
| Analysis reference period | Past 12 months |
| Analysis applicability | all eligible |
| Analysis provenance | NEPS new |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 114 |
| Analysis implementation note | First field sbi_exp_gate governs 4 follow-ups. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 127 sbi_exper_1

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_exper_1 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | In the past 12 months, how often did someone exclude you because they knew or believed you had emotional or mental health difficulties? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months If hidden by branching, REDCap stores blank, NOT numeric code 96. Handle structural not-applicable on export/analysis. |
| Branching Logic (Show field only if...) | [sbi_exp_gate] = '1' |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 22828db8987af4548262de028a8a18cb9cc67ef204f6592158b3ffbc3a251f60 |
| Analysis label | In the past 12 months, how often did someone exclude you because they knew or believed you had emotional or mental health difficulties? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | enacted_experienced |
| Analysis index | SBI_CONTEXT |
| Analysis dimension | enacted_experienced |
| Analysis reference period | Past 12 months |
| Analysis applicability | sbi_exp_gate=1; otherwise 96 (structural NA) |
| Analysis provenance | NEPS new; Recruitment Plan §7.3 |
| Analysis control note | Must not impute 0 if not asked. Interpret mental health-related stigma, not generic bullying. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 115 |
| Analysis implementation note | First field sbi_exp_gate governs 4 follow-ups. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 128 sbi_exper_2

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_exper_2 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | In the past 12 months, how often did someone make hurtful comments about you because they knew or believed you had emotional or mental health difficulties? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months If hidden by branching, REDCap stores blank, NOT numeric code 96. Handle structural not-applicable on export/analysis. |
| Branching Logic (Show field only if...) | [sbi_exp_gate] = '1' |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | fcc43a67296ebd837f06998904ec676a5f31bcce84edfe756d8abbab09640807 |
| Analysis label | In the past 12 months, how often did someone make hurtful comments about you because they knew or believed you had emotional or mental health difficulties? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | enacted_experienced |
| Analysis index | SBI_CONTEXT |
| Analysis dimension | enacted_experienced |
| Analysis reference period | Past 12 months |
| Analysis applicability | sbi_exp_gate=1; otherwise 96 (structural NA) |
| Analysis provenance | NEPS new; Recruitment Plan §7.3 |
| Analysis control note | Must not impute 0 if not asked. Interpret mental health-related stigma, not generic bullying. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 116 |
| Analysis implementation note | First field sbi_exp_gate governs 4 follow-ups. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 129 sbi_exper_3

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_exper_3 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | In the past 12 months, how often were you treated unfairly in education, training or work because of an actual or assumed mental health difficulty? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months If hidden by branching, REDCap stores blank, NOT numeric code 96. Handle structural not-applicable on export/analysis. |
| Branching Logic (Show field only if...) | [sbi_exp_gate] = '1' |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 35a70874e64ac72d1884f681dfba754f081a45049c2c6302c3246f7ea6abea86 |
| Analysis label | In the past 12 months, how often were you treated unfairly in education, training or work because of an actual or assumed mental health difficulty? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | enacted_experienced |
| Analysis index | SBI_CONTEXT |
| Analysis dimension | enacted_experienced |
| Analysis reference period | Past 12 months |
| Analysis applicability | sbi_exp_gate=1; otherwise 96 (structural NA) |
| Analysis provenance | NEPS new; Recruitment Plan §7.3 |
| Analysis control note | Must not impute 0 if not asked. Interpret mental health-related stigma, not generic bullying. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 117 |
| Analysis implementation note | First field sbi_exp_gate governs 4 follow-ups. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 130 sbi_exper_4

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_exper_4 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | In the past 12 months, how often did you avoid seeking support because you had previously experienced negative treatment about your mental health? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: Past 12 months If hidden by branching, REDCap stores blank, NOT numeric code 96. Handle structural not-applicable on export/analysis. |
| Branching Logic (Show field only if...) | [sbi_exp_gate] = '1' |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | b1476b02213d28d2262b35c5a990c0cb6439f9493152d9c5dd9face837e07932 |
| Analysis label | In the past 12 months, how often did you avoid seeking support because you had previously experienced negative treatment about your mental health? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | enacted_experienced |
| Analysis index | SBI_CONTEXT |
| Analysis dimension | enacted_experienced |
| Analysis reference period | Past 12 months |
| Analysis applicability | sbi_exp_gate=1; otherwise 96 (structural NA) |
| Analysis provenance | NEPS new; Recruitment Plan §7.3 |
| Analysis control note | Must not impute 0 if not asked. Interpret mental health-related stigma, not generic bullying. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 118 |
| Analysis implementation note | First field sbi_exp_gate governs 4 follow-ups. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 131 seek_01

| Property | Source definition |
| --- | --- |
| Variable / Field Name | seek_01 |
| Form Name | neps31_extended_baseline |
| Section Header | Help-seeking beliefs |
| Field Type | radio |
| Field Label | A problem would have to be really bad for me to be willing to seek mental health care. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | ebe6c765a3b717d5e0aac60e01cbb19472c103c8f55ec013bc562ce144fb8190 |
| Analysis label | A problem would have to be really bad for me to be willing to seek mental health care. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | Help-seeking attitudes / reluctance |
| Analysis index | HELP_SEEKING_CONTEXT |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 p15 Beliefs About Treatment Seeking (remainder after SBI items 5–7) |
| Analysis control note | Avoid re-asking V2 items 5–7: already captured as sbi_help_1–3. Do not sum eight-item source as an established scale without confirmed instructions. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 119 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 132 seek_02

| Property | Source definition |
| --- | --- |
| Variable / Field Name | seek_02 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | I would feel uncomfortable talking about my problems with a mental health provider. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 4e88a556108269ebb7fb709c0c8df71aa0d4f66a507a8abb7282ecfa2d1652b6 |
| Analysis label | I would feel uncomfortable talking about my problems with a mental health provider. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | Help-seeking attitudes / reluctance |
| Analysis index | HELP_SEEKING_CONTEXT |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 p15 Beliefs About Treatment Seeking (remainder after SBI items 5–7) |
| Analysis control note | Avoid re-asking V2 items 5–7: already captured as sbi_help_1–3. Do not sum eight-item source as an established scale without confirmed instructions. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 120 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 133 seek_03

| Property | Source definition |
| --- | --- |
| Variable / Field Name | seek_03 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | If I had a mental health problem, I would prefer to deal with it myself rather than to seek treatment. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | d1e658b740e70075163a103c11d07a854af9d3d2c805852e3c8b0bd3ab77b01a |
| Analysis label | If I had a mental health problem, I would prefer to deal with it myself rather than to seek treatment. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | Help-seeking attitudes / reluctance |
| Analysis index | HELP_SEEKING_CONTEXT |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 p15 Beliefs About Treatment Seeking (remainder after SBI items 5–7) |
| Analysis control note | Avoid re-asking V2 items 5–7: already captured as sbi_help_1–3. Do not sum eight-item source as an established scale without confirmed instructions. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 121 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 134 seek_04

| Property | Source definition |
| --- | --- |
| Variable / Field Name | seek_04 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Most mental health problems can be dealt with without seeking professional help. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 5dfadaf08e55cab516347134d4226ca49d04d8a84960825dab5ac5e55d2c9e43 |
| Analysis label | Most mental health problems can be dealt with without seeking professional help. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | Help-seeking attitudes / reluctance |
| Analysis index | HELP_SEEKING_CONTEXT |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 p15 Beliefs About Treatment Seeking (remainder after SBI items 5–7) |
| Analysis control note | Avoid re-asking V2 items 5–7: already captured as sbi_help_1–3. Do not sum eight-item source as an established scale without confirmed instructions. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 122 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 135 seek_08

| Property | Source definition |
| --- | --- |
| Variable / Field Name | seek_08 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | I would not want to share personal information with a mental health provider. |
| Choices, Calculations, OR Slider Labels | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 7f765a993687befff58071069ae1fa699221a26a4580c528964b8245dbabca4b |
| Analysis label | I would not want to share personal information with a mental health provider. |
| Analysis response definition | 1, Strongly disagree \| 2, Somewhat disagree \| 3, Neither agree nor disagree \| 4, Somewhat agree \| 5, Strongly agree |
| Analysis construct | Help-seeking attitudes / reluctance |
| Analysis index | HELP_SEEKING_CONTEXT |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 p15 Beliefs About Treatment Seeking (remainder after SBI items 5–7) |
| Analysis control note | Avoid re-asking V2 items 5–7: already captured as sbi_help_1–3. Do not sum eight-item source as an established scale without confirmed instructions. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 123 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 136 ypw_01

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_01 |
| Form Name | neps31_extended_baseline |
| Section Header | NEPS positive wellbeing: meaning and emotion |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I had a reason to look forward to the coming days. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | ebbbc9dddd999d6248e8032fee77db9b82819cb8324b572cc568907c7726524b |
| Analysis label | Thinking about the past 30 days: I had a reason to look forward to the coming days. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Future orientation / hope |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 124 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 137 ypw_02

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_02 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I felt that an important part of my life had meaning. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | b487e0a131968f082c5e2ee429ad33d8891a88ad0ebf8501f962f17d2af0f229 |
| Analysis label | Thinking about the past 30 days: I felt that an important part of my life had meaning. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Meaning / purpose |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 125 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 138 ypw_03

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_03 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I could name something in my future that mattered to me. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 50161e41b3234a4b367479f0a2aa13fd524a7d10eec67d2f452a012ee02f0071 |
| Analysis label | Thinking about the past 30 days: I could name something in my future that mattered to me. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Future direction |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 126 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 139 ypw_04

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_04 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I felt that making progress towards something important was worthwhile. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | bf6d0c38aae145f4121fbf51d8638086116a36b018d5e4d0f6f967f494b356b3 |
| Analysis label | Thinking about the past 30 days: I felt that making progress towards something important was worthwhile. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Purposeful engagement |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 127 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 140 ypw_05

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_05 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I experienced moments of enjoyment in ordinary daily life. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | cd92fb6844f4d72eb22ebc2399f38acbf59a910158f07d36b953026dbd5448ca |
| Analysis label | Thinking about the past 30 days: I experienced moments of enjoyment in ordinary daily life. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Positive affect |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 128 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 141 ypw_06

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_06 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I felt content with at least one part of my life. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 6db707fad9979141ab960d5e4eda4cd5b3c3d4f9e2b9a420999c1c26b3bc395a |
| Analysis label | Thinking about the past 30 days: I felt content with at least one part of my life. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Life contentment |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 129 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 142 ypw_07

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_07 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I experienced a sense of peace or calm during part of my day. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | d11902acb90ca5508a3cbad072dfbcc402c5c11afe37e7a4c06e56eba65b8736 |
| Analysis label | Thinking about the past 30 days: I experienced a sense of peace or calm during part of my day. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Positive emotional state |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 130 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 143 ypw_08

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_08 |
| Form Name | neps31_extended_baseline |
| Section Header | NEPS positive wellbeing: belonging and growth |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I felt welcome in a place where I chose to spend time. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | c184677ad1887a02ed0e4dc3083ef9cc5ec460c059488044082c351dca3cd6c8 |
| Analysis label | Thinking about the past 30 days: I felt welcome in a place where I chose to spend time. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Belonging |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 131 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 144 ypw_09

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_09 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I felt accepted for who I am by at least one group I belonged to. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f56555cd7b2682d48aa84ca9ccbf7180a0bb2f409b6eacdef32479f2c6b7c262 |
| Analysis label | Thinking about the past 30 days: I felt accepted for who I am by at least one group I belonged to. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Social acceptance |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 132 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 145 ypw_10

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_10 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I felt that my presence contributed something positive to a group or community. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | e82500df8a02fe0da93e516385ee29df6f6b21d0122bf290bbbf2c1abb09add6 |
| Analysis label | Thinking about the past 30 days: I felt that my presence contributed something positive to a group or community. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Meaningful contribution |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 133 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 146 ypw_11

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_11 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: People made space for me to express my views in matters affecting me. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | cd897ee7977b2c26802f0f3f3bb13dfc731994869697e45f676f56f8a0b932a2 |
| Analysis label | Thinking about the past 30 days: People made space for me to express my views in matters affecting me. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Voice / recognition |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 134 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 147 ypw_12

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_12 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I felt respected when I expressed an opinion different from someone else’s. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | fff7ba98a23678e44da38caf773d879fa4d4258e5afbb50d7c06d2f8a9588a8a |
| Analysis label | Thinking about the past 30 days: I felt respected when I expressed an opinion different from someone else’s. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Respect for voice |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 135 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 148 ypw_13

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_13 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I noticed a positive change in myself. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 1d083f086e0cc943b2d501444d1050ad68aa2b46d8bdc1c9db2d0cf9c3bac749 |
| Analysis label | Thinking about the past 30 days: I noticed a positive change in myself. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Personal growth |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 136 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 149 ypw_14

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ypw_14 |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Thinking about the past 30 days: I discovered an interest or ability that made me curious to learn more. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 35c03d1307bac80479b071f697ce6db34cc9bed2208331cf99b7fe5f421790d2 |
| Analysis label | Thinking about the past 30 days: I discovered an interest or ability that made me curious to learn more. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Always |
| Analysis construct | Exploration / growth |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original wellbeing wording; concepts from positive functioning and African youth research [5,9,10]; NOT Ryff scale |
| Analysis control note | Do not combine with BRS/MSPSS/GSE. No validated NEPS total score or clinical interpretation; domain descriptives pending empirical factor evidence. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 137 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 150 bully_30d

| Property | Source definition |
| --- | --- |
| Variable / Field Name | bully_30d |
| Form Name | neps31_extended_baseline |
| Section Header | Recent bullying, violence and substance use |
| Field Type | radio |
| Field Label | During the past 30 days, how often were you bullied? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, 1–2 days \| 2, Several days \| 3, Most days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | e44c0efe85e1aae14586c9af70605948cb8e4ea1cb3f3343b825eafd92714e63 |
| Analysis label | During the past 30 days, how often were you bullied? |
| Analysis response definition | 0, Never \| 1, 1–2 days \| 2, Several days \| 3, Most days |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p7 |
| Analysis control note | No automation of clinical diagnosis. Flag routing follows approved safeguarding SOP. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 138 |
| Analysis implementation note | Keep bully_30d, attack_12m before respective follow-ups. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 151 attack_12m

| Property | Source definition |
| --- | --- |
| Variable / Field Name | attack_12m |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | During the past 12 months, did you experience a physical attack? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Once \| 2, More than once \| 99, Prefer not |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 99, Prefer not. These labels apply to this field only. |
| Dictionary row SHA256 | 6763589c8fef2d2bc52bad1352d3e54fbf6c60b33d2718890f8ead6e69b6dde3 |
| Analysis label | During the past 12 months, did you experience a physical attack? |
| Analysis response definition | 0, No \| 1, Once \| 2, More than once \| 99, Prefer not |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p6 |
| Analysis control note | No automation of clinical diagnosis. Flag routing follows approved safeguarding SOP. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 139 |
| Analysis implementation note | Keep bully_30d, attack_12m before respective follow-ups. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 152 fight_12m

| Property | Source definition |
| --- | --- |
| Variable / Field Name | fight_12m |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | During the past 12 months, were you involved in a physical fight? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, 1–2 times \| 2, More than twice \| 99, Prefer not |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 99, Prefer not. These labels apply to this field only. |
| Dictionary row SHA256 | 097f7fcff832c7b72f41315d22d744eceb9c7d81297295b57224de122aa14e2e |
| Analysis label | During the past 12 months, were you involved in a physical fight? |
| Analysis response definition | 0, Never \| 1, 1–2 times \| 2, More than twice \| 99, Prefer not |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p6 |
| Analysis control note | No automation of clinical diagnosis. Flag routing follows approved safeguarding SOP. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 140 |
| Analysis implementation note | Keep bully_30d, attack_12m before respective follow-ups. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 153 substance_ever

| Property | Source definition |
| --- | --- |
| Variable / Field Name | substance_ever |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | Have you ever used alcohol or another substance? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Alcohol \| 2, Other drug/substance \| 3, Both \| 98, Unsure \| 99, Prefer not |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Unsure; 99, Prefer not. These labels apply to this field only. |
| Dictionary row SHA256 | a55051866cc0160055d69f9b208f8ce416a5186a5c26bc856de629e32bb20d17 |
| Analysis label | Have you ever used alcohol or another substance? |
| Analysis response definition | 0, Never \| 1, Alcohol \| 2, Other drug/substance \| 3, Both \| 98, Unsure \| 99, Prefer not |
| Analysis construct | CONTEXT |
| Analysis index | CONTEXT |
| Analysis applicability | all eligible |
| Analysis provenance | V2 p5 |
| Analysis control note | No automation of clinical diagnosis. Flag routing follows approved safeguarding SOP. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 141 |
| Analysis implementation note | Keep bully_30d, attack_12m before respective follow-ups. |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 154 bully_type

| Property | Source definition |
| --- | --- |
| Variable / Field Name | bully_type |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | If you were bullied in the past 30 days, which form occurred most often? |
| Choices, Calculations, OR Slider Labels | 1, Physical \| 2, Mocking or insulting \| 3, Exclusion \| 4, Sexual remarks \| 5, Digital messages/social media \| 6, Other \| 99, Prefer not to answer |
| Field Note | Reference: As stated in question |
| Branching Logic (Show field only if...) | ([bully_30d] = '1' or [bully_30d] = '2' or [bully_30d] = '3') |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | aabb56e7831e80d724d18258f0ef43fbb6e7ef3d74fe7a3676152a455f402635 |
| Analysis label | If you were bullied in the past 30 days, which form occurred most often? |
| Analysis response definition | 1, Physical \| 2, Mocking or insulting \| 3, Exclusion \| 4, Sexual remarks \| 5, Digital messages/social media \| 6, Other \| 99, Prefer not to answer |
| Analysis construct | Recent bullying type |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | bully_30d IN (1,2,3) |
| Analysis provenance | V2 p7; consolidated |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 142 |
| Analysis implementation note | Keep bully_30d, attack_12m before respective follow-ups. |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 155 attack_freq_missing

| Property | Source definition |
| --- | --- |
| Variable / Field Name | attack_freq_missing |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | If attacked more than once, can you provide the number of times? |
| Choices, Calculations, OR Slider Labels | 1, I can provide a number \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Technical response-format field for attack_freq. The original substantive frequency question is unchanged. |
| Branching Logic (Show field only if...) | [attack_12m] = '2' |
| Classification | Technical response-format control |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | e525691e5e2eaeb470304b87c337e1b334c23440e930b170fd372b7a790b296b |

### 156 attack_freq

| Property | Source definition |
| --- | --- |
| Variable / Field Name | attack_freq |
| Form Name | neps31_extended_baseline |
| Field Type | text |
| Field Label | If physically attacked more than once during the past 12 months, approximately how many times did it happen? |
| Field Note | Enter the actual number of attacks (2 or more). For do not know/prefer not, use the accompanying response-status field; no artificial upper limit is imposed. Reference: As stated in question |
| Text Validation Type OR Show Slider Number | integer |
| Text Validation Min | 2 |
| Branching Logic (Show field only if...) | ([attack_12m] = '2' and [attack_freq_missing] = '1') |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No inline missing sentinel. Read attack_freq_missing separately: 1 permits a numeric count, 98 is unknown and 99 is refusal. Counts of 98 or 99 are not automatically missing. |
| Dictionary row SHA256 | 724aea454676ba39ae6c1db680e701d206ed3762d02f5eea772543bce92b5f40 |
| Analysis label | If physically attacked more than once during the past 12 months, approximately how many times did it happen? |
| Analysis response definition | Whole number &gt;1 \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Attack frequency |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | attack_12m=2 |
| Analysis provenance | V2 p6; retained |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 143 |
| Analysis implementation note | Keep bully_30d, attack_12m before respective follow-ups. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 157 attack_by

| Property | Source definition |
| --- | --- |
| Variable / Field Name | attack_by |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | If physically attacked during the past 12 months, who was primarily involved? |
| Choices, Calculations, OR Slider Labels | 1, Household member / relative \| 2, Person known in community or school \| 3, Stranger \| 4, Multiple categories \| 99, Prefer not to answer |
| Field Note | Reference: As stated in question |
| Branching Logic (Show field only if...) | ([attack_12m] = '1' or [attack_12m] = '2') |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | bf602bf9ae02518611e2275bc213348aba7ef14f6467d2e3c4cdea647c121a8e |
| Analysis label | If physically attacked during the past 12 months, who was primarily involved? |
| Analysis response definition | 1, Household member / relative \| 2, Person known in community or school \| 3, Stranger \| 4, Multiple categories \| 99, Prefer not to answer |
| Analysis construct | Attack source |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | attack_12m IN (1,2) |
| Analysis provenance | V2 p6; retained |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 144 |
| Analysis implementation note | Keep bully_30d, attack_12m before respective follow-ups. |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 158 substance_30d

| Property | Source definition |
| --- | --- |
| Variable / Field Name | substance_30d |
| Form Name | neps31_extended_baseline |
| Section Header | Household and social context |
| Field Type | radio |
| Field Label | In the past 30 days, have you consumed alcohol or used another psychoactive substance? |
| Choices, Calculations, OR Slider Labels | 0, None \| 1, Alcohol only \| 2, Other psychoactive substance only \| 3, Both \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: As stated in question |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 39df9d46901c39e1d7785df6fdea5a78ffdaef0aeea13fa6240fd9c2edcc70ee |
| Analysis label | In the past 30 days, have you consumed alcohol or used another psychoactive substance? |
| Analysis response definition | 0, None \| 1, Alcohol only \| 2, Other psychoactive substance only \| 3, Both \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Recent substance exposure |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS temporal specification; V2 lifetime question kept as substance_ever |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 145 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 159 caregiver_substance

| Property | Source definition |
| --- | --- |
| Variable / Field Name | caregiver_substance |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | As far as you know, has a parent or principal caregiver ever used alcohol or other substances in a way that disrupted family life? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: As stated in question |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | f1fdb0cb351840c2a291e830c7ddbbbb78404806a69ded47ad2c8692f30a65ad |
| Analysis label | As far as you know, has a parent or principal caregiver ever used alcohol or other substances in a way that disrupted family life? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Caregiver substance-related disruption |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | All eligible participants |
| Analysis provenance | V2 p5 caretaker substance question, redesigned to focus on family effect without treating any alcohol use as dysfunction |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 146 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 160 family_disrupt_current

| Property | Source definition |
| --- | --- |
| Variable / Field Name | family_disrupt_current |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | During the past 12 months, was your family living arrangement changed by an event outside your control? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: As stated in question |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | bb08240b5a83107524cf6069b41ca3e5c8b72661e88f9c19595f3d52702dc540 |
| Analysis label | During the past 12 months, was your family living arrangement changed by an event outside your control? |
| Analysis response definition | 0, No \| 1, Yes \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Recent family disruption |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original contextual extension, non-equivalent to historical ycad family events |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 147 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 161 community_safety

| Property | Source definition |
| --- | --- |
| Variable / Field Name | community_safety |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | During the past 12 months, how often did you avoid ordinary activities because you felt unsafe where you lived? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: As stated in question |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f774c08563556ab6cb519d610ce4ae1c97ef374ea7e220e06b7fdad528ae5e2c |
| Analysis label | During the past 12 months, how often did you avoid ordinary activities because you felt unsafe where you lived? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | Current perceived safety |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | All eligible participants |
| Analysis provenance | NEPS-original; not childhood adversity |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 148 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 162 social_family_contact

| Property | Source definition |
| --- | --- |
| Variable / Field Name | social_family_contact |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | During the past 30 days, how often did you have contact with family members outside your immediate household? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, A few times \| 3, Weekly \| 4, Most days \| 96, No such family \| 99, Prefer not to answer |
| Field Note | Reference: As stated in question |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, No such family; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | bd8630d0d04df625533f8c88f2bbe5258c994f48fb17c5efc9aacc0eae9a89c4 |
| Analysis label | During the past 30 days, how often did you have contact with family members outside your immediate household? |
| Analysis response definition | 0, Never \| 1, Once \| 2, A few times \| 3, Weekly \| 4, Most days \| 96, No such family \| 99, Prefer not to answer |
| Analysis construct | Social network contact structure |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | All eligible participants |
| Analysis provenance | Condensed context, replaces age-inappropriate V2 24-question SNI module; NO claim of standard SNI score |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 149 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 163 social_peer_contact

| Property | Source definition |
| --- | --- |
| Variable / Field Name | social_peer_contact |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | During the past 30 days, how often did you spend time or communicate with friends or peers? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, A few times \| 3, Weekly \| 4, Most days \| 99, Prefer not to answer |
| Field Note | Reference: As stated in question |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | d0fd7d360bf52cc71e70b4059ad2ed95e1d2ac37489a67d71e9f95f43a1e4188 |
| Analysis label | During the past 30 days, how often did you spend time or communicate with friends or peers? |
| Analysis response definition | 0, Never \| 1, Once \| 2, A few times \| 3, Weekly \| 4, Most days \| 99, Prefer not to answer |
| Analysis construct | Social network contact structure |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | All eligible participants |
| Analysis provenance | Condensed context, NOT validated SNI score |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 150 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 164 social_community

| Property | Source definition |
| --- | --- |
| Variable / Field Name | social_community |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | During the past 30 days, did you take part in a community, religious, sports, youth or other group activity? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 96, Not available locally \| 99, Prefer not to answer |
| Field Note | Reference: As stated in question |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 96, Not available locally; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | fd536c1bdb2e876a4c5d5e55dc717576166cf54bd84090860873df6f93b2030b |
| Analysis label | During the past 30 days, did you take part in a community, religious, sports, youth or other group activity? |
| Analysis response definition | 0, No \| 1, Yes \| 96, Not available locally \| 99, Prefer not to answer |
| Analysis construct | Community engagement |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | All eligible participants |
| Analysis provenance | Do not score religious participation as intrinsically protective or required for wellbeing |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 151 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 165 sleep_hunger_context

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sleep_hunger_context |
| Form Name | neps31_extended_baseline |
| Field Type | radio |
| Field Label | During the past 30 days, how often was your sleep interrupted by work, caring responsibilities or household conditions? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Field Note | Reference: As stated in question |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 3ae435fed48a683de3ddf8c28985533d03549129a5638d1693896686d169d26a |
| Analysis label | During the past 30 days, how often was your sleep interrupted by work, caring responsibilities or household conditions? |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Very often |
| Analysis construct | Structural causes of interrupted sleep |
| Analysis index | NONE |
| Analysis reference period | As stated in question |
| Analysis applicability | All eligible participants |
| Analysis provenance | Separates YEB sleep-related emotional disturbance from material/daily context |
| Analysis control note | Single owner of this construct; keep separate from current screening scores and historical adversity. |
| Analysis administration stage | 03 Extended |
| Analysis respondent order | 152 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 166 yeb_01

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_01 |
| Form Name | neps31_yeb |
| Section Header | NEPS emotional, behavioural and social functioning |
| Field Type | radio |
| Field Label | During the past 30 days: Strong feelings interrupted an activity I wanted or needed to finish. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f05e48cd60997e7d7b89a2312c2a651491daa8784b1b9bc17c7c217ea1a9b53f |
| Analysis label | During the past 30 days: Strong feelings interrupted an activity I wanted or needed to finish. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Emotional interference |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 153 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 167 yeb_02

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_02 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: After becoming upset, I found it difficult to return to my usual activities. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 8ac6bfd1c86af1b0d2b44319524b93b0e106dab8d1b3f2ea5043ce65126344b7 |
| Analysis label | During the past 30 days: After becoming upset, I found it difficult to return to my usual activities. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Emotional regulation impact |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 154 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 168 yeb_03

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_03 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: I avoided an activity I wanted to join because I expected an upsetting interaction. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 9ed2a6dcffa25a09c91564d40806e2d1b0a202f5486d1b3a49881a28c77a7501 |
| Analysis label | During the past 30 days: I avoided an activity I wanted to join because I expected an upsetting interaction. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Social avoidance |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 155 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 169 yeb_04

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_04 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: I stopped taking an interest in activities that usually mattered to me. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | bd817def43795639eb8fbdbbd1fcbfd2f5769ba74c0a64c724967a10dac35d3d |
| Analysis label | During the past 30 days: I stopped taking an interest in activities that usually mattered to me. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Reduced interest |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 156 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 170 yeb_05

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_05 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: I struggled to concentrate on a task even when I had enough time and few interruptions. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | e9c83557ce19a9baea8d7cea750e6402aabc43910afc8d5acb9e896cbb80552a |
| Analysis label | During the past 30 days: I struggled to concentrate on a task even when I had enough time and few interruptions. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Attention in suitable conditions |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 157 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 171 yeb_06

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_06 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: I had difficulty keeping track of what I was doing despite having understood the task. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 6d1e0769c29dfaf0a13f80587f2d52b83e947e96029f2db5682b5e02e13a465d |
| Analysis label | During the past 30 days: I had difficulty keeping track of what I was doing despite having understood the task. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Task memory / engagement |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 158 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 172 yeb_07

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_07 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: When I became frustrated, I found it hard to keep an argument from becoming more serious. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | d50dad4159bf4e0f5a6078cc6bb5f92033c2d0ea30f0b1d54b34ba7ec3f43c1d |
| Analysis label | During the past 30 days: When I became frustrated, I found it hard to keep an argument from becoming more serious. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Conflict escalation |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 159 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 173 yeb_08

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_08 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: An action I took when upset damaged a relationship that mattered to me. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 1c1d22b602fa04d293fabf90bb733692f8cc2b41d2f1c61da32497e3f639f9fd |
| Analysis label | During the past 30 days: An action I took when upset damaged a relationship that mattered to me. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Behavioural consequence |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 160 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 174 yeb_09

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_09 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: I stayed away from people I wanted to spend time with because I felt uncomfortable. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 2271b5455a865e7b3d9200bc0f66afb3f25d5b4c599607050b505dd3241cf02c |
| Analysis label | During the past 30 days: I stayed away from people I wanted to spend time with because I felt uncomfortable. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Voluntary social withdrawal |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 161 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 175 yeb_10

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_10 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: A headache or stomach discomfort occurred at a time when I was very worried. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | e4cd5a7726a2743d1b723bf02dc4b0a602ebd7acbbe77d3cf857ba218b004cf9 |
| Analysis label | During the past 30 days: A headache or stomach discomfort occurred at a time when I was very worried. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Somatic distress covariate |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 162 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 176 yeb_11

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_11 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: Thoughts about problems made it difficult for me to fall asleep or stay asleep. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | c27a2452e64add0556a86cdd0c3ceea5ef6d4e3cd8dedd9cadc5916a69da4fa0 |
| Analysis label | During the past 30 days: Thoughts about problems made it difficult for me to fall asleep or stay asleep. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Sleep interference |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 163 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 177 yeb_12

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_12 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: I noticed a change in my appetite during times of emotional difficulty. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | a3c04a749a7454bdf05b0fb4589cf296788085d0dacb52e94181ba5cbea73b46 |
| Analysis label | During the past 30 days: I noticed a change in my appetite during times of emotional difficulty. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Appetite change |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 164 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 178 yeb_13

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_13 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: When someone wanted to talk about a problem, I made time to listen when I could. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 8e3a8f0a534469df089a00b8ecf48cb1fcaed37b337c4051924b70ba9a301178 |
| Analysis label | During the past 30 days: When someone wanted to talk about a problem, I made time to listen when I could. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Positive social response |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 165 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 179 yeb_14

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_14 |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: I included another person who was being left out of a shared activity, when I had the opportunity. |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | c6f65a0fe7d1223cb61fd00c461173489db6f31e705d35a92f100cd8d89715c0 |
| Analysis label | During the past 30 days: I included another person who was being left out of a shared activity, when I had the opportunity. |
| Analysis response definition | 0, Never \| 1, Rarely \| 2, Sometimes \| 3, Often \| 4, Almost every day |
| Analysis construct | Inclusive social behaviour |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original item drafted from functional/somatic/psychosocial concepts; AYPA literature [5], not an AYPA or SDQ item |
| Analysis control note | Do not treat somatic report as psychiatric diagnosis; note possible illness/food insecurity. No SDQ equivalent or validated total. Avoid duplicating K6 in distress score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 166 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 180 yeb_imp_study

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_imp_study |
| Form Name | neps31_yeb |
| Section Header | NEPS functional impact |
| Field Type | radio |
| Field Label | During the past 30 days: To what extent did these difficulties interrupt schooling, learning, study or training? |
| Choices, Calculations, OR Slider Labels | 0, Not at all \| 1, A little \| 2, Somewhat \| 3, Quite a lot \| 4, Extremely |
| Field Note | Reference: Past 30 days |
| Branching Logic (Show field only if...) | ([ever_school] = '1' or [currently_school] = '1') |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 90fde0c7bcf0e71395b9f07a405f58fa8f01e32468973eec1ab0765dc7f8980d |
| Analysis label | During the past 30 days: To what extent did these difficulties interrupt schooling, learning, study or training? |
| Analysis response definition | 0, Not at all \| 1, A little \| 2, Somewhat \| 3, Quite a lot \| 4, Extremely |
| Analysis construct | Functional interference / life area |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | ever_school=1 OR currently_school=1 |
| Analysis provenance | Original NEPS functional-impact design informed by K6 supplementary guidance and AYPA literature [5,6] |
| Analysis control note | Anchor refers to emotional/behavioural difficulties; conditional items are not zero when not applicable; use separate impact profile, not assumed SDQ impact score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 167 |
| Analysis implementation note | School and work impact items use earlier B1/B2 answers. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 181 yeb_imp_work

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_imp_work |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: To what extent did these difficulties interrupt paid or unpaid work? |
| Choices, Calculations, OR Slider Labels | 0, Not at all \| 1, A little \| 2, Somewhat \| 3, Quite a lot \| 4, Extremely |
| Field Note | Reference: Past 30 days |
| Branching Logic (Show field only if...) | ([work_status] = '1' or [work_status] = '2' or [work_status] = '3') |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 91902bc5b17584baa2f37a684447e893439551df544331eae515768fb5682f08 |
| Analysis label | During the past 30 days: To what extent did these difficulties interrupt paid or unpaid work? |
| Analysis response definition | 0, Not at all \| 1, A little \| 2, Somewhat \| 3, Quite a lot \| 4, Extremely |
| Analysis construct | Functional interference / life area |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | work_status IN (1,2,3) |
| Analysis provenance | Original NEPS functional-impact design informed by K6 supplementary guidance and AYPA literature [5,6] |
| Analysis control note | Anchor refers to emotional/behavioural difficulties; conditional items are not zero when not applicable; use separate impact profile, not assumed SDQ impact score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 168 |
| Analysis implementation note | School and work impact items use earlier B1/B2 answers. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 182 yeb_imp_home

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_imp_home |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: To what extent did these difficulties interrupt everyday responsibilities at home? |
| Choices, Calculations, OR Slider Labels | 0, Not at all \| 1, A little \| 2, Somewhat \| 3, Quite a lot \| 4, Extremely |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 09a9dab42773ccf5191043281818bec7d6e693d0a43a3e269876dd46cccca753 |
| Analysis label | During the past 30 days: To what extent did these difficulties interrupt everyday responsibilities at home? |
| Analysis response definition | 0, Not at all \| 1, A little \| 2, Somewhat \| 3, Quite a lot \| 4, Extremely |
| Analysis construct | Functional interference / life area |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | Original NEPS functional-impact design informed by K6 supplementary guidance and AYPA literature [5,6] |
| Analysis control note | Anchor refers to emotional/behavioural difficulties; conditional items are not zero when not applicable; use separate impact profile, not assumed SDQ impact score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 169 |
| Analysis implementation note | School and work impact items use earlier B1/B2 answers. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 183 yeb_imp_rel

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_imp_rel |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: To what extent did these difficulties affect relationships with family, peers or other important people? |
| Choices, Calculations, OR Slider Labels | 0, Not at all \| 1, A little \| 2, Somewhat \| 3, Quite a lot \| 4, Extremely |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f3a0d1a0aeee314b068260dcb9a024e5d6f7a8c460d944122cfb0d4d7cdc6388 |
| Analysis label | During the past 30 days: To what extent did these difficulties affect relationships with family, peers or other important people? |
| Analysis response definition | 0, Not at all \| 1, A little \| 2, Somewhat \| 3, Quite a lot \| 4, Extremely |
| Analysis construct | Functional interference / life area |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | Original NEPS functional-impact design informed by K6 supplementary guidance and AYPA literature [5,6] |
| Analysis control note | Anchor refers to emotional/behavioural difficulties; conditional items are not zero when not applicable; use separate impact profile, not assumed SDQ impact score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 170 |
| Analysis implementation note | School and work impact items use earlier B1/B2 answers. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 184 yeb_imp_activities

| Property | Source definition |
| --- | --- |
| Variable / Field Name | yeb_imp_activities |
| Form Name | neps31_yeb |
| Field Type | radio |
| Field Label | During the past 30 days: To what extent did these difficulties stop you doing activities you wanted to do? |
| Choices, Calculations, OR Slider Labels | 0, Not at all \| 1, A little \| 2, Somewhat \| 3, Quite a lot \| 4, Extremely |
| Field Note | Reference: Past 30 days |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | b7ebb86abf06d550a5f0d53649f677f8170f44bc3817e70735107f9ecb1718b2 |
| Analysis label | During the past 30 days: To what extent did these difficulties stop you doing activities you wanted to do? |
| Analysis response definition | 0, Not at all \| 1, A little \| 2, Somewhat \| 3, Quite a lot \| 4, Extremely |
| Analysis construct | Functional interference / life area |
| Analysis index | NONE |
| Analysis reference period | Past 30 days |
| Analysis applicability | All eligible participants |
| Analysis provenance | Original NEPS functional-impact design informed by K6 supplementary guidance and AYPA literature [5,6] |
| Analysis control note | Anchor refers to emotional/behavioural difficulties; conditional items are not zero when not applicable; use separate impact profile, not assumed SDQ impact score. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 171 |
| Analysis implementation note | School and work impact items use earlier B1/B2 answers. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 185 ycad_01

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_01 |
| Form Name | neps31_ycad |
| Section Header | NEPS adversity: early harmful experiences |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did a caregiver repeatedly humiliate or threaten you in a way that made you afraid? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 7159001f2bf8be69fa709b4a369b193ad9467ea0e165c513cddfc32766edbcf3 |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did a caregiver repeatedly humiliate or threaten you in a way that made you afraid? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Repeated caregiver emotional maltreatment |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 172 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 186 ycad_02

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_02 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did someone responsible for your care repeatedly blame or reject you in a way that made you feel unsafe at home? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | dd85086e05dbf9953178687f97fe3f83747e4dc162b6cf4bb3c6a2e51e3f6dab |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did someone responsible for your care repeatedly blame or reject you in a way that made you feel unsafe at home? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Repeated rejection or intimidation |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 173 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 187 ycad_03

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_03 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did a caregiver or other adult deliberately hurt you physically? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 194596a097af036c871c3e14040a1c4c443e94ba4a2f0ee71dec0040aa809796 |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did a caregiver or other adult deliberately hurt you physically? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Physical maltreatment by adult |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 174 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 188 ycad_04

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_04 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did punishment by an adult cause an injury that affected your daily activities? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 1e16f9ee9d44fb6b647cc9f7418f398914ca71484a3bd76ba06511ff30e7353b |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did punishment by an adult cause an injury that affected your daily activities? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Injury resulting from punishment |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 175 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 189 ycad_05

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_05 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did anyone touch you sexually when you did not want them to? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | fb9408be77965c48e74e1c1a68c20d29edcc99842e01146098d7edd1737af377 |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did anyone touch you sexually when you did not want them to? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Unwanted sexual touching |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 176 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 190 ycad_06

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_06 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did anyone pressure or threaten you to take part in sexual activity? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 30d631508e692b97860a3384e75bf1e8418efd820d0b41944b73d3bd2e58ff79 |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did anyone pressure or threaten you to take part in sexual activity? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Sexual coercion |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 177 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 191 ycad_07

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_07 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), were you repeatedly left without a responsible adult when you needed help to stay safe? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 4a841a171891c5cb7e08967072da6bd58c107e81c539aecea05570ae60109168 |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), were you repeatedly left without a responsible adult when you needed help to stay safe? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Lack of safe supervision |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 178 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 192 ycad_08

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_08 |
| Form Name | neps31_ycad |
| Section Header | NEPS adversity: household/community exposures |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did someone responsible for your care refuse or deliberately withhold help that was available and needed? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | fc8662d1c9949cd39b92976191c528695a8d821f5b80b04d676d309b4c5e87e4 |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did someone responsible for your care refuse or deliberately withhold help that was available and needed? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Caregiver refusal distinct from poverty |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 179 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 193 ycad_09

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_09 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did you witness serious threats or physical violence between people living in your home? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 39289afff990d87067ebcbe4edc18eb7f1395959a2126a936565f39c1b0dd8ed |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did you witness serious threats or physical violence between people living in your home? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Witnessed household violence |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 180 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 194 ycad_10

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_10 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did you personally witness someone being seriously injured or threatened in your community? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | effea942e993c57d17d6db6335de0593282831600781595793873d42ca2afe47 |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did you personally witness someone being seriously injured or threatened in your community? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Witnessed serious community violence |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 181 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 195 ycad_11

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_11 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did your household have to leave its usual home because remaining there was unsafe? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 6bf0e232251bb92fb131548884898d704f793b3dc75c7ef7ab84e8297c81cd4e |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did your household have to leave its usual home because remaining there was unsafe? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Forced relocation due to danger |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 182 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 196 ycad_12

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_12 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did separation from your main caregiver last for six months or longer when you wanted to remain together? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 015deccf827b0ecc52b2ea58ab10ae0fc22413676e72a68910d8071d487007e1 |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did separation from your main caregiver last for six months or longer when you wanted to remain together? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Extended caregiver separation |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 183 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 197 ycad_13

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_13 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did the death of someone who cared for you significantly change who looked after you? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 58b2149331f0bec87ab71a96c0fe3e329660f8a0f108e9159dbd0bf051079a55 |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did the death of someone who cared for you significantly change who looked after you? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Bereavement and caregiving disruption |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 184 |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 198 ycad_14

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_14 |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | Before your 18th birthday (or up to now if you are under 18), did violence or threats stop you from attending ordinary education, training or community activities for a prolonged period? |
| Choices, Calculations, OR Slider Labels | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18; participants under 18 report up to current age |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 5dac8ddd144a18e1853d7a2dcfb2b2c4a36a776ac5f2f356ed3b4a9de4f9ac2c |
| Analysis label | Before your 18th birthday (or up to now if you are under 18), did violence or threats stop you from attending ordinary education, training or community activities for a prolonged period? |
| Analysis response definition | 0, Never \| 1, Once \| 2, More than once \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Activity disruption from violence |
| Analysis index | NONE |
| Analysis reference period | Before age 18; participants under 18 report up to current age |
| Analysis applicability | All eligible participants |
| Analysis provenance | New NEPS-original exposures informed by adverse childhood experiences, WHO ACE-IQ framework, and NEPS Master Proposal [3,7,8]; not CTQ-SF or ACE-IQ |
| Analysis control note | Separate material hardship from intentional omission; not a diagnosis. Do not count current bullying/attack twice; interpret exposure duration differences across age groups. No total severity cutoff. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 185 |
| Country display references | 6 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 199 ycad_time_harm

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_time_harm |
| Form Name | neps31_ycad |
| Section Header | NEPS adversity: timing of reported exposures |
| Field Type | radio |
| Field Label | At approximately what age did the earliest of the reported maltreatment or unwanted sexual experiences first occur? |
| Choices, Calculations, OR Slider Labels | 1, Before age 6 \| 2, Age 6–11 \| 3, Age 12–17 \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18 / up to current age Branch evaluated on applicable historical responses coded 1 or 2. |
| Branching Logic (Show field only if...) | (([ycad_01] = '1' or [ycad_01] = '2') or ([ycad_02] = '1' or [ycad_02] = '2') or ([ycad_03] = '1' or [ycad_03] = '2') or ([ycad_04] = '1' or [ycad_04] = '2') or ([ycad_05] = '1' or [ycad_05] = '2') or ([ycad_06] = '1' or [ycad_06] = '2') or ([ycad_07] = '1' or [ycad_07] = '2') or ([ycad_08] = '1' or [ycad_08] = '2')) |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 5bda56e2add26f6e30ab349ecfd147f9c49bd27b8f7f66a807cefb4ba3ea2b98 |
| Analysis label | At approximately what age did the earliest of the reported maltreatment or unwanted sexual experiences first occur? |
| Analysis response definition | 1, Before age 6 \| 2, Age 6–11 \| 3, Age 12–17 \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Approximate exposure timing |
| Analysis index | NONE |
| Analysis reference period | Before age 18 / up to current age |
| Analysis applicability | Show if [ycad_01]&gt;0 and [ycad_01]&lt;3 or [ycad_02]&gt;0 and [ycad_02]&lt;3 or [ycad_03]&gt;0 and [ycad_03]&lt;3 or [ycad_04]&gt;0 and [ycad_04]&lt;3 or [ycad_05]&gt;0 and [ycad_05]&lt;3 or [ycad_06]&gt;0 and [ycad_06]&lt;3 or [ycad_07]&gt;0 and [ycad_07]&lt;3 or [ycad_08]&gt;0 and [ycad_08]&lt;3 |
| Analysis provenance | NEPS V3.1 new timing design |
| Analysis control note | Coarse category; earliest age cannot resolve repeated exposures. If unknown enter 98; no imputation. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 186 |
| Analysis implementation note | Conditional on earlier I1/I2 responses; do not expose for non-events. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 200 ycad_time_viol

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_time_viol |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | At approximately what age did the earliest reported household or community violence/displacement experience first occur? |
| Choices, Calculations, OR Slider Labels | 1, Before age 6 \| 2, Age 6–11 \| 3, Age 12–17 \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18 / up to current age Branch evaluated on applicable historical responses coded 1 or 2. |
| Branching Logic (Show field only if...) | (([ycad_09] = '1' or [ycad_09] = '2') or ([ycad_10] = '1' or [ycad_10] = '2') or ([ycad_11] = '1' or [ycad_11] = '2') or ([ycad_14] = '1' or [ycad_14] = '2')) |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 9749193a2cff8c0ae97d77d41882ad4bd3fef4616ddde4d5475b0a4aaf5faa4e |
| Analysis label | At approximately what age did the earliest reported household or community violence/displacement experience first occur? |
| Analysis response definition | 1, Before age 6 \| 2, Age 6–11 \| 3, Age 12–17 \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Approximate exposure timing |
| Analysis index | NONE |
| Analysis reference period | Before age 18 / up to current age |
| Analysis applicability | Show if [ycad_09]&gt;0 and [ycad_09]&lt;3 or [ycad_10]&gt;0 and [ycad_10]&lt;3 or [ycad_11]&gt;0 and [ycad_11]&lt;3 or [ycad_14]&gt;0 and [ycad_14]&lt;3 |
| Analysis provenance | NEPS V3.1 new timing design |
| Analysis control note | Coarse category; earliest age cannot resolve repeated exposures. If unknown enter 98; no imputation. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 187 |
| Analysis implementation note | Conditional on earlier I1/I2 responses; do not expose for non-events. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 201 ycad_time_sep

| Property | Source definition |
| --- | --- |
| Variable / Field Name | ycad_time_sep |
| Form Name | neps31_ycad |
| Field Type | radio |
| Field Label | At approximately what age did the earliest reported caregiver separation or major bereavement occur? |
| Choices, Calculations, OR Slider Labels | 1, Before age 6 \| 2, Age 6–11 \| 3, Age 12–17 \| 98, Do not know \| 99, Prefer not to answer |
| Field Note | Reference: Before age 18 / up to current age Branch evaluated on applicable historical responses coded 1 or 2. |
| Branching Logic (Show field only if...) | (([ycad_12] = '1' or [ycad_12] = '2') or ([ycad_13] = '1' or [ycad_13] = '2')) |
| Classification | Respondent question |
| Respondent question | Yes |
| Core 73 | No |
| Declared special response codes | 98, Do not know; 99, Prefer not to answer. These labels apply to this field only. |
| Dictionary row SHA256 | 166eea8110f0080894b0458f6295d8381afecab922a8d2c318434abbd006ee6a |
| Analysis label | At approximately what age did the earliest reported caregiver separation or major bereavement occur? |
| Analysis response definition | 1, Before age 6 \| 2, Age 6–11 \| 3, Age 12–17 \| 98, Do not know \| 99, Prefer not to answer |
| Analysis construct | Approximate exposure timing |
| Analysis index | NONE |
| Analysis reference period | Before age 18 / up to current age |
| Analysis applicability | Show if [ycad_12]&gt;0 and [ycad_12]&lt;3 or [ycad_13]&gt;0 and [ycad_13]&lt;3 |
| Analysis provenance | NEPS V3.1 new timing design |
| Analysis control note | Coarse category; earliest age cannot resolve repeated exposures. If unknown enter 98; no imputation. |
| Analysis administration stage | 04 Detailed |
| Analysis respondent order | 188 |
| Analysis implementation note | Conditional on earlier I1/I2 responses; do not expose for non-events. |
| Country display references | 3 rows; countries: Ghana, Sierra Leone, Tanzania; sources: NEPS_V3_1_MLM_Country_English_Display_Manifest.csv |

### 202 age_band

| Property | Source definition |
| --- | --- |
| Variable / Field Name | age_band |
| Form Name | neps31_derived |
| Section Header | Externally computed screening and analytical outputs (not respondent-facing) |
| Field Type | text |
| Field Label | Study age band |
| Field Note | Downstream 1=12–14, 2=15–19, 3=20–24. Imported coding convention. EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | integer |
| Text Validation Min | 1 |
| Text Validation Max | 3 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f618367175ff075e964c72e4d56a9c72780b365587ea283d958fa07d252cddc8 |
| Analysis label | Study age band |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | Study age band |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | 12–14 / 15–19 / 20–24, derived from imported age_years; never entered by participant |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 203 brs_raw

| Property | Source definition |
| --- | --- |
| Variable / Field Name | brs_raw |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | BRS six-item mean |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 1 |
| Text Validation Max | 5 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | a284a8556ae2bb81aaa1c0fca52b8fe455c4adbc182326e3dab1a029c5bbc922 |
| Analysis label | BRS six-item mean |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | BRS six-item mean |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | 1–5; reverse items 2,4,6; complete six |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 204 mspss_raw

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mspss_raw |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | MSPSS twelve-item mean |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 1 |
| Text Validation Max | 7 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 07bab44cef20bfad0995f59ed5827814e09c336420d6f75b505758fbe7fbbefc |
| Analysis label | MSPSS twelve-item mean |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | MSPSS twelve-item mean |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | 1–7; all twelve for NEPS version; original subscales may be reported |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 205 gse_raw

| Property | Source definition |
| --- | --- |
| Variable / Field Name | gse_raw |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | GSE ten-item sum |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 10 |
| Text Validation Max | 40 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 0848eec8c12f31cb16f4c4d2702815d078c4384189f47ddef2b51d5af7b903ea |
| Analysis label | GSE ten-item sum |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | GSE ten-item sum |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | 10–40; complete ten |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 206 k6_raw

| Property | Source definition |
| --- | --- |
| Variable / Field Name | k6_raw |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | K6 six-item total |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 0 |
| Text Validation Max | 24 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 92ad205a33707a655f9cb36f3c7d3e6719d8b7318c0e7fd5523db61ca6b3a560 |
| Analysis label | K6 six-item total |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | K6 six-item total |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | 0–24; complete six |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 207 epi_100

| Property | Source definition |
| --- | --- |
| Variable / Field Name | epi_100 |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | Educational Pressure Index |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 0 |
| Text Validation Max | 100 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 350c951219439789eef3a599d7fc79898c26370da677c64080d0f81850cd51b2 |
| Analysis label | Educational Pressure Index |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | Educational Pressure Index |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | Arithmetic mean of 5 two-item dimension 0–100 scores; complete 10 |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. Participants with no applicable education/training context: allow 96/structural NA and mark EPI unavailable, not low pressure. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 208 esi_100

| Property | Source definition |
| --- | --- |
| Variable / Field Name | esi_100 |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | Economic Stress Index |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 0 |
| Text Validation Max | 100 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | d31c20ce10fa817f444dae66c42e3bc6ae39c2a6da9d5c5cf598bde92859a8f1 |
| Analysis label | Economic Stress Index |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | Economic Stress Index |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | Arithmetic mean of 5 two-item 0–100 dimensions; complete 10 |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 209 sbi_100

| Property | Source definition |
| --- | --- |
| Variable / Field Name | sbi_100 |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | Stigma Burden Index |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 0 |
| Text Validation Max | 100 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | c4e9bca7f8b4df0729533cff32e40f0d2d41806b86ffef88187c36d105b32aab |
| Analysis label | Stigma Burden Index |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | Stigma Burden Index |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | Mean of four normalised dimension means across 19 source items; all 19 |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 210 mhdi_100

| Property | Source definition |
| --- | --- |
| Variable / Field Name | mhdi_100 |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | Mental Health Distress Index |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 0 |
| Text Validation Max | 100 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 13ae1d82321c85a52b33edc484d5ba01daa799050ed185990621edda665dd6c0 |
| Analysis label | Mental Health Distress Index |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | Mental Health Distress Index |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | 100 × k6_raw / 24 |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 211 pfi_100

| Property | Source definition |
| --- | --- |
| Variable / Field Name | pfi_100 |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | Protective Factors Index |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 0 |
| Text Validation Max | 100 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 6739853ce3c62c8f269a5b450071870d5b041ef3d30f65ee65ffdebbf533f42a |
| Analysis label | Protective Factors Index |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | Protective Factors Index |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | Arithmetic mean of normalised BRS, MSPSS, GSE 0–100 values |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 212 nses_100

| Property | Source definition |
| --- | --- |
| Variable / Field Name | nses_100 |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | NEPS Stress Exposure Score |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 0 |
| Text Validation Max | 100 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 769c66a1f7b5c94d1f21d3a404efbbe9286dafc2dbe01bd2a1fe6108e1362655 |
| Analysis label | NEPS Stress Exposure Score |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | NEPS Stress Exposure Score |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | 0.30×EPI + 0.25×ESI + 0.20×SBI + 0.20×MHDI + 0.05×(100−PFI), 0–100 |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 213 screen_score_status

| Property | Source definition |
| --- | --- |
| Variable / Field Name | screen_score_status |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | Score computation status |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. |
| Text Validation Type OR Show Slider Number | integer |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | e84bc10c134680039a69531bab65408ef518762c22f8ddcb58265eaad2ad29af |
| Analysis label | Score computation status |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | Score computation status |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | 1 complete \| 2 missing responses \| 3 structurally not applicable \| 4 unresolved response code \| 5 source not verified |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 214 stressor_burden_count

| Property | Source definition |
| --- | --- |
| Variable / Field Name | stressor_burden_count |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | Count of separately defined priority stressors |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. Leave blank until approved priority-stressor dictionary/rules are implemented; not computed by this CSV. |
| Text Validation Type OR Show Slider Number | integer |
| Text Validation Min | 0 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 578cf3763d53f39b809402761c215d399abc324c0aceaf3ac0c83ad928c6f7e0 |
| Analysis label | Count of separately defined priority stressors |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | Count of separately defined priority stressors |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | Requires externally adopted indicator dictionary and thresholds: do not infer from NSES or 5 indices |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 215 stressor_burden_class

| Property | Source definition |
| --- | --- |
| Variable / Field Name | stressor_burden_class |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | Stressor burden classification |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. Leave blank until approved priority-stressor dictionary/rules are implemented; not computed by this CSV. |
| Text Validation Type OR Show Slider Number | integer |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 4b69e91f11c1ce6697f243a4b00c079978bfec37c6792381aed6bc12d23abd86 |
| Analysis label | Stressor burden classification |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | Stressor burden classification |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | 0–2 low; 3–5 moderate; 6–8 high; ≥9 very high, ONLY after unique indicator rules exist |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 216 stressor_profile

| Property | Source definition |
| --- | --- |
| Variable / Field Name | stressor_profile |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | Primary stressor profile |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. Leave blank until approved priority-stressor dictionary/rules are implemented; not computed by this CSV. |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 6da96fffba7f042300854da6b2cf6df5bb07cb3a383d1a3b997489c14569c1e4 |
| Analysis label | Primary stressor profile |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | Primary stressor profile |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | Profile derived from available indices under separately specified classification rules |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 217 iwi_score

| Property | Source definition |
| --- | --- |
| Variable / Field Name | iwi_score |
| Form Name | neps31_derived |
| Field Type | text |
| Field Label | International Wealth Index |
| Field Note | EXTERNAL DERIVED OUTPUT: populate from validated NEPS scoring pipeline; no unverified REDCap calculation is embedded. Leave blank until verified published IWI coefficients and recoding are implemented. |
| Text Validation Type OR Show Slider Number | number |
| Text Validation Min | 0 |
| Text Validation Max | 100 |
| Classification | Derived variable / system output |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 56703d7479d539f203993c54eb8a9b72848aedb2f59502f8d6c60f6f88050684 |
| Analysis label | International Wealth Index |
| Analysis response definition | Calculated field, not asked of respondent |
| Analysis construct | International Wealth Index |
| Analysis index | DERIVED |
| Analysis applicability | All eligible participants |
| Analysis scoring direction | Not compute from V3 assets alone until source 12-to-20 recoding and published coefficients implemented |
| Analysis provenance | NEPS V3.0 scoring specification; NEPS recruitment plan; Global Data Lab for IWI |
| Analysis control note | Never enter manually or display as an additional question. Version formula, reference and input completeness. |
| Analysis administration stage | 05 Derived analytics |
| Analysis implementation note | Do not display as survey question. |

### 218 cohort_eligible

| Property | Source definition |
| --- | --- |
| Variable / Field Name | cohort_eligible |
| Form Name | neps31_cohort_review |
| Section Header | Cohort review outputs (not respondent-facing) |
| Field Type | radio |
| Field Label | Meets approved longitudinal cohort eligibility criteria? |
| Choices, Calculations, OR Slider Labels | 0, No \| 1, Yes \| 2, Pending review |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | System output / registry action |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | ba9c4bdc293105cdfec91c9e4850dbe4bbe4e8a4cddb2094f1183b527f0ad26e |
| Analysis label | Meets approved longitudinal cohort eligibility criteria? |
| Analysis response definition | 0, No \| 1, Yes \| 2, Pending review |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 06 Cohort review outputs |
| Analysis implementation note | Do not display as survey question. |

### 219 cohort_status

| Property | Source definition |
| --- | --- |
| Variable / Field Name | cohort_status |
| Form Name | neps31_cohort_review |
| Field Type | radio |
| Field Label | Cohort selection status |
| Choices, Calculations, OR Slider Labels | 0, Not assessed \| 1, Eligible pool \| 2, Selected \| 3, Not selected \| 4, Declined \| 5, Withdrawn |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | System output / registry action |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | cfac422c30cff51f7385942e4fdf0afe7aae92870941776f566ea7fea50e1123 |
| Analysis label | Cohort selection status |
| Analysis response definition | 0, Not assessed \| 1, Eligible pool \| 2, Selected \| 3, Not selected \| 4, Declined \| 5, Withdrawn |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 06 Cohort review outputs |
| Analysis implementation note | Do not display as survey question. |

### 220 cohort_reason

| Property | Source definition |
| --- | --- |
| Variable / Field Name | cohort_reason |
| Form Name | neps31_cohort_review |
| Field Type | text |
| Field Label | Reason for cohort selection/deferral decision |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | System output / registry action |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | f21f448bf2031cb2fe09685501b52ac6f4acdd1bc67afd45db128f6ee984b055 |
| Analysis label | Reason for cohort selection/deferral decision |
| Analysis response definition | Free text; limited/controlled as defined in notes |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 06 Cohort review outputs |
| Analysis implementation note | Do not display as survey question. |

### 221 cohort_reviewer

| Property | Source definition |
| --- | --- |
| Variable / Field Name | cohort_reviewer |
| Form Name | neps31_cohort_review |
| Field Type | text |
| Field Label | Authorised cohort reviewer ID |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | System output / registry action |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 49878d3c0ff3563e734f1028ba6c35ce2c8bb1e939ccf177200f1e0e0b4e5995 |
| Analysis label | Authorised cohort reviewer ID |
| Analysis response definition | Free text; limited/controlled as defined in notes |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 06 Cohort review outputs |
| Analysis implementation note | Do not display as survey question. |

### 222 selection_batch

| Property | Source definition |
| --- | --- |
| Variable / Field Name | selection_batch |
| Form Name | neps31_cohort_review |
| Field Type | text |
| Field Label | Selection batch/version |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | System output / registry action |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | b34026b08206936d4213951c79367d8b750a41972db84c7b401e652996cc936b |
| Analysis label | Selection batch/version |
| Analysis response definition | Free text; limited/controlled as defined in notes |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 06 Cohort review outputs |
| Analysis implementation note | Do not display as survey question. |

### 223 longitud_id

| Property | Source definition |
| --- | --- |
| Variable / Field Name | longitud_id |
| Form Name | neps31_cohort_review |
| Field Type | text |
| Field Label | Linked longitudinal cohort ID |
| Field Note | Imported/managed by NEPS Digital System or authorised study staff; not an additional participant questionnaire. |
| Classification | System output / registry action |
| Respondent question | No |
| Core 73 | No |
| Declared special response codes | No special response code declared in the choice metadata. |
| Dictionary row SHA256 | 8881fe471ce869efe1078747de9b88bd68048bc347ef2cfc3b58cf712b2b9ad9 |
| Analysis label | Linked longitudinal cohort ID |
| Analysis response definition | Free text; limited/controlled as defined in notes |
| Analysis construct | COHORT |
| Analysis index | COHORT |
| Analysis applicability | all eligible |
| Analysis provenance | Recruitment Plan §§10–18 |
| Analysis control note | Collection/approval by authorised study team only |
| Analysis administration stage | 06 Cohort review outputs |
| Analysis implementation note | Do not display as survey question. |
