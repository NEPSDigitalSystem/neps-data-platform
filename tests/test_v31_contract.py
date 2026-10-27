"""Independent assertions against the supplied V3.1 source contract.

No participant responses, API identity or live system are used.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from etl.contracts.v31 import (ContractError, NAME, archive_member,
                               build_from_sources, canonical_digest, metadata_drift)

REPO = Path(__file__).resolve().parents[1]
CONTRACT = REPO / "etl/contracts/data_contract_v31.json"
REFERENCE_ROOT = REPO / "tests/fixtures/v31_reference"

# Explicit independent manifest transcribed from the actual workbook NSES 73
# Items sheet; no prefix-based inference of membership is permitted.
EXPECTED_CORE = """
epi_expectations_1 epi_expectations_2 epi_failure_1 epi_failure_2
epi_caregivers_1 epi_caregivers_2 epi_future_1 epi_future_2 epi_progress_1 epi_progress_2
esi_finstrain_1 esi_finstrain_2 esi_food_1 esi_food_2 esi_educost_1 esi_educost_2
esi_materials_1 esi_materials_2 esi_transport_1 esi_transport_2
sbi_loved_1 sbi_loved_2 sbi_loved_3 sbi_loved_4 sbi_loved_5 sbi_loved_6 sbi_loved_7 sbi_loved_8
sbi_comm_1 sbi_comm_2 sbi_comm_3 sbi_comm_4 sbi_self_1 sbi_self_2 sbi_self_3 sbi_self_4
sbi_help_1 sbi_help_2 sbi_help_3 k6_1 k6_2 k6_3 k6_4 k6_5 k6_6
brs_01 brs_02 brs_03 brs_04 brs_05 brs_06
mspss_01 mspss_02 mspss_03 mspss_04 mspss_05 mspss_06 mspss_07 mspss_08
mspss_09 mspss_10 mspss_11 mspss_12
gse_01 gse_02 gse_03 gse_04 gse_05 gse_06 gse_07 gse_08 gse_09 gse_10
""".split()


class V31ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.metadata = [f["dictionary_metadata"] for f in cls.contract["fields"]]

    def test_all_question_membership_and_actual_stage_counts(self):
        self.assertEqual(len(self.contract["question_fields"]), 188)
        fields = {f["name"]: f for f in self.contract["fields"]}
        self.assertEqual(len(fields), 223)
        counts = {}
        for name in self.contract["question_fields"]:
            self.assertEqual(fields[name]["analysis_mapping"]["field_kind"], "Respondent question")
            form = fields[name]["dictionary_metadata"]["Form Name"]
            counts[form] = counts.get(form, 0) + 1
        self.assertEqual(counts, {"neps31_screening": 73, "neps31_cohort_interest": 5,
                                  "neps31_extended_baseline": 74, "neps31_yeb": 19,
                                  "neps31_ycad": 17})
        self.assertNotIn("attack_freq_missing", self.contract["question_fields"])

    def test_exact_scoring_manifest_and_index_counts(self):
        self.assertEqual(self.contract["core_73_fields"], EXPECTED_CORE)
        counts = {}
        for field in self.contract["fields"]:
            if field["core_73"]:
                index = field["analysis_mapping"]["NSES_index"]
                counts[index] = counts.get(index, 0) + 1
        self.assertEqual(counts, {"EPI": 10, "ESI": 10, "SBI": 19, "MHDI": 6, "PFI": 28})

    def test_saved_core_manifest_matches_verified_membership_and_provenance(self):
        manifest = json.loads((CONTRACT.parent / "core73_manifest_v31.json")
                              .read_text(encoding="utf-8"))
        self.assertEqual([field["name"] for field in manifest["fields"]], EXPECTED_CORE)
        self.assertEqual(manifest["contract_version"], self.contract["contract_version"])
        self.assertEqual(manifest["dictionary_sha256"], self.contract["dictionary_sha256"])
        self.assertEqual(manifest["source_hashes"], self.contract["sources"])
        self.assertEqual(manifest["participant_linkage"], self.contract["participant_linkage"])
        self.assertEqual(manifest["verification_scope"], self.contract["verification_scope"])
        fields = {field["name"]: field for field in self.contract["fields"]}
        for saved in manifest["fields"]:
            field = fields[saved["name"]]
            mapping = field["analysis_mapping"]
            with self.subTest(field=saved["name"]):
                self.assertEqual(saved, {
                    "name": field["name"],
                    "index": mapping["NSES_index"],
                    "dimension": mapping["NSES_dimension"],
                    "direction": mapping["scoring_or_direction"],
                    "reference_period": mapping["reference_period"],
                    "choices": field["dictionary_metadata"]["Choices, Calculations, OR Slider Labels"],
                })

    def test_every_dictionary_column_preserved_and_hashed(self):
        for field in self.contract["fields"]:
            self.assertEqual(len(field["dictionary_metadata"]), 18)
            self.assertEqual(field["dictionary_metadata_sha256"],
                             canonical_digest(field["dictionary_metadata"]))
        self.assertEqual(self.contract["dictionary_sha256"], canonical_digest(self.metadata))

    def test_drift_detects_changes_in_every_column(self):
        for column in self.metadata[0]:
            with self.subTest(column=column):
                changed = copy.deepcopy(self.metadata)
                changed[0][column] += "-synthetic-drift"
                self.assertTrue(metadata_drift(self.metadata, changed))
        self.assertFalse(metadata_drift(self.metadata, copy.deepcopy(self.metadata)))

    def test_drift_detects_order_added_removed_duplicate_fields(self):
        changed = copy.deepcopy(self.metadata)
        changed[0], changed[1] = changed[1], changed[0]
        self.assertIn({"reason": "field_order_changed"}, metadata_drift(self.metadata, changed))
        self.assertIn({"field": "study_id", "reason": "removed"},
                      metadata_drift(self.metadata, self.metadata[1:]))
        with self.assertRaises(ContractError):
            metadata_drift(self.metadata, self.metadata + [self.metadata[0]])

    def test_country_metadata_source_links_and_codes(self):
        school = next(f for f in self.contract["fields"] if f["name"] == "school_level")
        crosswalk = [d for d in school["country_display"] if "NEPS_common_code" in d["metadata"]]
        self.assertEqual(len(crosswalk), 24)
        self.assertEqual({d["metadata"]["country"] for d in crosswalk},
                         {"Ghana", "Sierra Leone", "Tanzania"})
        self.assertTrue(all(d["source"] == "Education_Level_Crosswalk_Country_Display.csv"
                            for d in crosswalk))
        choices = school["dictionary_metadata"]["Choices, Calculations, OR Slider Labels"]
        codes = {choice.split(",", 1)[0].strip() for choice in choices.split("|")}
        self.assertTrue(all(d["metadata"]["NEPS_common_code"] in codes for d in crosswalk))

    def test_technical_missingness_has_separate_native_codes(self):
        control = self.contract["open_count_control"]
        self.assertEqual(control["control_field"], "attack_freq_missing")
        self.assertEqual(control["unknown_code"], "98")
        self.assertEqual(control["refusal_code"], "99")
        self.assertEqual(control["numeric_control_code"], "1")

    def test_full_188_fixture_transport_preserves_unanswered_values(self):
        fixture = json.loads((CONTRACT.parent / "synthetic_188_unanswered.json").read_text(encoding="utf-8"))
        responses = fixture["responses"]
        self.assertEqual(set(responses), set(self.contract["question_fields"]))
        self.assertEqual(len(responses), 188)
        self.assertTrue(all(value == "" for value in responses.values()))
        self.assertEqual(json.loads(json.dumps(responses)), responses)
        self.assertEqual(fixture["technical_controls"], {"attack_freq_missing": ""})

    def test_unsafe_archive_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("../evil", "synthetic")
                link = zipfile.ZipInfo("link")
                link.external_attr = 0o120777 << 16
                archive.writestr(link, "target")
            for member in ["../evil", "/evil", "link"]:
                with self.subTest(member=member), self.assertRaises(ContractError):
                    archive_member(path, member)

    def test_regeneration_from_actual_documents_matches_saved_contract(self):
        self.assertEqual(build_from_sources(REFERENCE_ROOT), self.contract)


if __name__ == "__main__":
    unittest.main()
