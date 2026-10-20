"""Build the local REDCap contract from the actual supplied source documents.

This contract is evidence of local metadata only. It never grants service,
participant-processing or country-transfer permissions.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
import zipfile

NAME = "Variable / Field Name"
FORM = "Form Name"
TYPE = "Field Type"
CHOICES = "Choices, Calculations, OR Slider Labels"
BRANCH = "Branching Logic (Show field only if...)"
DICTIONARY_HEADERS = [
    NAME, FORM, "Section Header", TYPE, "Field Label", CHOICES, "Field Note",
    "Text Validation Type OR Show Slider Number", "Text Validation Min", "Text Validation Max",
    "Identifier?", BRANCH, "Required Field?", "Custom Alignment",
    "Question Number (surveys only)", "Matrix Group Name", "Matrix Ranking?", "Field Annotation",
]
COUNTRY_LOCALES = {"Ghana": "en_GH", "Sierra Leone": "en_SL", "Tanzania": "en_TZ"}
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
MAX_MEMBER_BYTES = 25 * 1024 * 1024


class ContractError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value):
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode("utf-8"))


def csv_rows(data):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ContractError("Missing or duplicate CSV headers")
    rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ContractError("Malformed CSV row width")
    return rows


def archive_member(path, name):
    """Read a bounded regular member without extracting archive contents."""
    member = PurePosixPath(name)
    if member.is_absolute() or ".." in member.parts or "\\" in name:
        raise ContractError("Unsafe archive member path")
    with zipfile.ZipFile(path) as archive:
        matches = [x for x in archive.infolist() if x.filename == name]
        if len(matches) != 1:
            raise ContractError("Missing or duplicate archive member")
        info = matches[0]
        mode = info.external_attr >> 16
        if mode & 0o170000 not in (0, 0o100000) or info.is_dir():
            raise ContractError("Archive member must be a regular file")
        if info.file_size > MAX_MEMBER_BYTES:
            raise ContractError("Archive member exceeds evidence size limit")
        return archive.read(info)


def xlsx_rows(path, sheet_name):
    """Read actual XLSX sheet values with stdlib; preserve sparse columns."""
    book = ET.fromstring(archive_member(path, "xl/workbook.xml"))
    relation_id = next((s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                       for s in book.findall("m:sheets/m:sheet", NS)
                       if s.get("name") == sheet_name), None)
    if relation_id is None:
        raise ContractError("Missing workbook sheet: " + sheet_name)
    rels = ET.fromstring(archive_member(path, "xl/_rels/workbook.xml.rels"))
    target = next((r.get("Target") for r in rels if r.get("Id") == relation_id
                   and r.get("TargetMode") != "External"), None)
    if not target:
        raise ContractError("Missing internal sheet relation")
    target = target.lstrip("/") if target.startswith("/") else "xl/" + target
    shared = []
    with zipfile.ZipFile(path) as z:
        if "xl/sharedStrings.xml" in z.namelist():
            shared = ["".join(x.itertext()) for x in
                      ET.fromstring(archive_member(path, "xl/sharedStrings.xml")).findall("m:si", NS)]
    values = []
    for row in ET.fromstring(archive_member(path, target)).findall(".//m:sheetData/m:row", NS):
        cells = {}
        for cell in row.findall("m:c", NS):
            col = 0
            for char in cell.get("r", ""):
                if char.isalpha():
                    col = col * 26 + ord(char.upper()) - ord("A") + 1
                else:
                    break
            if not col:
                raise ContractError("Workbook cell has no column address")
            value = cell.find("m:v", NS)
            if cell.get("t") == "inlineStr":
                inline = cell.find("m:is", NS)
                text = "".join(inline.itertext()) if inline is not None else ""
            elif cell.get("t") == "s":
                text = shared[int(value.text)]
            else:
                text = value.text if value is not None else ""
            cells[col - 1] = text
        values.append([cells.get(i, "") for i in range(max(cells, default=-1) + 1)])
    if not values:
        raise ContractError("Empty workbook sheet")
    header = values[0]
    return [dict(zip(header, row + [""] * (len(header) - len(row)))) for row in values[1:]]


def unique_rows(rows, key):
    result = {}
    for row in rows:
        value = row[key]
        if not value or value in result:
            raise ContractError("Empty or duplicate field: " + value)
        result[value] = row
    return result


def metadata_drift(expected, observed):
    """Compare complete dictionary metadata, including order and all 18 columns.

    An API adapter must explicitly convert approved API metadata to these
    columns; this function does not assume unverified API metadata equivalence.
    """
    left, right = unique_rows(expected, NAME), unique_rows(observed, NAME)
    changes = []
    for name in sorted(left.keys() | right.keys()):
        if name not in left:
            changes.append({"field": name, "reason": "added"})
        elif name not in right:
            changes.append({"field": name, "reason": "removed"})
        else:
            keys = sorted(k for k in left[name].keys() | right[name].keys()
                          if left[name].get(k) != right[name].get(k))
            if keys:
                changes.append({"field": name, "reason": "metadata_changed", "columns": keys})
    if [r[NAME] for r in expected] != [r[NAME] for r in observed]:
        changes.append({"reason": "field_order_changed"})
    return changes


def build_contract(dictionary, mapping, workbook, core_sheet, country_sources, sources):
    fields = unique_rows(dictionary, NAME)
    mapped = unique_rows(mapping, "field_name")
    base = unique_rows(workbook, "field_name")
    core = unique_rows(core_sheet, "field_name")
    if len(dictionary) != 223 or any(list(row) != DICTIONARY_HEADERS for row in dictionary):
        raise ContractError("V3.1 dictionary requires 223 rows and exact 18-column header sequence")
    if mapped.keys() != base.keys():
        raise ContractError("Ordered map and workbook field membership disagree")
    for name, row in base.items():
        if any(mapping_value != mapped[name].get(key) for key, mapping_value in row.items()):
            raise ContractError("Ordered map disagrees with workbook metadata: " + name)
    missing = fields.keys() - mapped.keys()
    if missing != {"attack_freq_missing"} or mapped.keys() - fields.keys():
        raise ContractError("Unexpected dictionary/mapping discrepancy")
    technical = fields["attack_freq_missing"]
    if (technical[TYPE] != "radio" or technical[CHOICES] !=
            "1, I can provide a number | 98, Do not know | 99, Prefer not to answer"
            or technical[BRANCH] != "[attack_12m] = '2'"
            or "Technical response-format field for attack_freq" not in technical["Field Note"]):
        raise ContractError("Unverified technical response-control metadata")
    questions = [name for name, row in mapped.items() if row["field_kind"] == "Respondent question"]
    scoring = [name for name, row in mapped.items() if row["NSES_core_73"] == "YES"]
    if len(questions) != 188 or len(scoring) != 73 or set(scoring) != core.keys():
        raise ContractError("Explicit question/core-73 membership failed reconciliation")
    if set(scoring) - set(questions):
        raise ContractError("Scoring field is not a respondent question")
    for name in scoring:
        if core[name] != base[name] or fields[name][FORM] != "neps31_screening":
            raise ContractError("Core-73 workbook/screening disagreement")
    form_counts = {}
    for name in questions:
        form = fields[name][FORM]
        form_counts[form] = form_counts.get(form, 0) + 1
    if form_counts != {"neps31_screening": 73, "neps31_cohort_interest": 5,
                       "neps31_extended_baseline": 74, "neps31_yeb": 19, "neps31_ycad": 17}:
        raise ContractError("Question stage counts disagree")
    country_by_field = {}
    for source_name, rows in country_sources.items():
        for row in rows:
            if row.get("country") not in COUNTRY_LOCALES:
                raise ContractError("Country display has an unrecognised country")
            if "locale_key" in row and row["locale_key"] != COUNTRY_LOCALES[row["country"]]:
                raise ContractError("Country display locale disagrees with named country")
            name = row.get("field_name", row.get("source_field"))
            if name not in fields:
                raise ContractError("Country display references unknown field: " + str(name))
            if "form_name" in row and row["form_name"] != fields[name][FORM]:
                raise ContractError("Country display form disagrees with dictionary: " + name)
            column = {"field_label": "Field Label", "field_note": "Field Note",
                      "coded_choice_labels": CHOICES}.get(row.get("element"))
            if column and row["default_text"] != fields[name][column]:
                raise ContractError("Country display default disagrees with dictionary: " + name)
            if "NEPS_common_code" in row:
                codes = {c.split(",", 1)[0].strip() for c in fields[name][CHOICES].split("|")}
                if row["NEPS_common_code"] not in codes:
                    raise ContractError("Country display references undeclared common code: " + name)
            country_by_field.setdefault(name, []).append({"source": source_name, "metadata": row})
    contract_fields = []
    for order, row in enumerate(dictionary, 1):
        name = row[NAME]
        analytical = mapped.get(name)
        contract_fields.append({
            "name": name, "dictionary_order": order, "dictionary_metadata": row,
            "dictionary_metadata_sha256": canonical_digest(row),
            "analysis_mapping": analytical,
            "kind": analytical["field_kind"] if analytical else "Technical response-format control",
            "respondent_question": name in questions, "core_73": name in scoring,
            "country_display": country_by_field.get(name, []),
            "destination_type": "source-preserving string or checkbox code map",
            "transformation_policy": "retain original codes and missingness; no implicit zero or recoding",
            "event_repeat_context": "UNVERIFIED - retain source record/event/instrument/instance identifiers",
            "sensitivity": "authenticated source intake; downstream access uses separate NDS purpose permissions",
        })
    return {
        "contract_version": "NEPS-V3.1-local-evidence-3-independent-redcap-intake",
        "participant_linkage": {
            "id_issuer": "REDCap",
            "source_record_id_field": "study_id",
            "namespace": ["redcap_project_id", "study_id"],
            "decision_source": "User instruction, 12 October 2026: REDCap independently collects survey consent/responses; NDS separate consent/registration/IDs occur after export",
            "nds_authority": ["registration", "consent", "processing_permissions"],
            "nds_id_issuer": "NDS - separate namespace after source export",
            "policy": "Preserve REDCap-issued ID and survey data verbatim. Full source intake requires no NDS registration, NDS ID or NDS consent. Map to a separate NDS ID downstream without overwriting source ID.",
            "unregistered_policy": "Receive all source data durably and queue for later NDS registration; separate NDS consent applies to downstream NDS purposes only",
            "survey_consent": "User confirms survey consent in REDCap; actual field/form not present in supplied dictionary and remains UNVERIFIED. Preserve real exported evidence; never infer from completion/willingness.",
            "offline_policy": "REDCap collection/completion independent of NDS; offline device data reach server before API export; retry and full reconciliation after connectivity returns",
            "generation_configuration": "UNVERIFIED: deployed REDCap record auto-numbering/ID rules require configuration evidence; no numbering pattern invented",
        },
        "verification_scope": "local supplied documents only; live REDCap metadata NOT TESTED",
        "sources": sources,
        "source_precedence": ["18-column dictionary: executable field names/codes/branching",
                              "mapping workbook: explicit respondent/core membership and analytical meaning",
                              "ordered map: reconciled analytical metadata plus administration order",
                              "country CSVs: proposed display crosswalks; no measurement-equivalence claim"],
        "dictionary_sha256": canonical_digest(dictionary),
        "counts": {"dictionary_fields": 223, "respondent_questions": 188, "core_73": 73,
                   "question_forms": form_counts},
        "question_fields": questions, "core_73_fields": scoring, "fields": contract_fields,
        "open_count_control": {"count_field": "attack_freq", "control_field": "attack_freq_missing",
                               "numeric_control_code": "1", "unknown_code": "98", "refusal_code": "99",
                               "policy": "retain count and control independently; unknown/refusal are never numeric counts"},
        "unresolved": ["Live imported REDCap metadata/events/repeating configuration and API identity not verified",
                       "Applicable country-transfer approvals and participant-processing authorisation not supplied",
                       "Country displays are proposed; local translation review and measurement equivalence are not demonstrated"],
    }


def build_from_sources(reference_root):
    root = Path(reference_root).resolve()
    dictionary_path = root / "NEPS Master CRF V3.1- REDCap Data Dictionary/NEPS_Master_CRF_V3_1_REDCap_18_Column_Data_Dictionary.csv"
    workbook_path = root / "NEPS_V3_1_Mapping_Workbook.xlsx"
    package = root / "NEPS Master CRF V3.1/NEPS_V3_1_Priority_Order_REDCap_Build_Package.zip"
    member = "NEPS_V3_1_Ordered_Item_to_Analysis_Map.csv"
    country_dir = root / "NEPS Master CRF V3.1- Country Adaptations"
    countries = [country_dir / "Education_Level_Crosswalk_Country_Display.csv",
                 country_dir / "NEPS_V3_1_MLM_Country_English_Display_Manifest.csv"]
    sources = []
    for path in [dictionary_path, workbook_path, package] + countries:
        sources.append({"path": path.relative_to(root).as_posix(), "sha256": digest(path.read_bytes())})
    sources.append({"path": package.relative_to(root).as_posix(), "archive_member": member,
                    "sha256": digest(archive_member(package, member))})
    return build_contract(csv_rows(dictionary_path.read_bytes()),
                          csv_rows(archive_member(package, member)),
                          xlsx_rows(workbook_path, "Full Item Map"),
                          xlsx_rows(workbook_path, "NSES 73 Items"),
                          {p.name: csv_rows(p.read_bytes()) for p in countries}, sources)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    contract = build_from_sources(args.reference_root)
    args.output.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(contract["counts"], sort_keys=True))
