"""Build the Markdown dictionary from reconciled, unchanged V3.1 references.

Run from the checkout with python -m scripts.build_v31_dictionary.
This command does not update the contract, contact services or calculate scores.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path

from etl.contracts.v31 import (
    DICTIONARY_HEADERS,
    build_from_sources,
    canonical_digest,
)

ROOT = Path(__file__).resolve().parents[1]
SPECIAL_CODES = frozenset({'96', '97', '98', '99'})


def cell(value: object) -> str:
    """Preserve source text while escaping Markdown table delimiters and HTML."""
    text = str(value).replace('\r\n', '\n').replace('\r', '\n')
    return (html.escape(text, quote=False).replace('\\', '\\\\')
            .replace('|', '\\|').replace('\n', '<br>'))


def table(headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> list[str]:
    result = ['| ' + ' | '.join(headers) + ' |',
              '| ' + ' | '.join('---' for _ in headers) + ' |']
    result.extend('| ' + ' | '.join(cell(value) for value in row) + ' |'
                  for row in rows)
    return result + ['']


def missing_definition(field: dict) -> str:
    if field['name'] == 'attack_freq':
        return ('No inline missing sentinel. Read attack_freq_missing separately: '
                '1 permits a numeric count, 98 is unknown and 99 is refusal. '
                'Counts of 98 or 99 are not automatically missing.')
    choices = field['dictionary_metadata']['Choices, Calculations, OR Slider Labels']
    declared = [part.strip() for part in choices.split('|')
                if part.split(',', 1)[0].strip() in SPECIAL_CODES]
    if declared:
        return '; '.join(declared) + '. These labels apply to this field only.'
    return 'No special response code declared in the choice metadata.'


def render_dictionary(contract: dict) -> str:
    fields = contract['fields']
    forms = Counter(field['dictionary_metadata']['Form Name'] for field in fields)
    kinds = Counter(field['kind'] for field in fields)
    core = Counter(field['analysis_mapping']['NSES_index']
                   for field in fields if field['core_73'])
    lines = [
        '# V3.1 data dictionary', '',
        'This document records all 223 fields in the supplied historical V3.1 '
        'dictionary. It preserves field types, labels, codes, validation, '
        'branching and analytical notes. It is not a statement of deployed '
        'REDCap configuration or scientific approval.', '',
        '## Sources and regeneration', '',
        f"Contract version: `{contract['contract_version']}`.", '',
        f"Canonical contract SHA256: `{canonical_digest(contract)}`.", '',
        f"Dictionary metadata SHA256: `{contract['dictionary_sha256']}`.", '',
        'The [saved contract](../etl/contracts/data_contract_v31.json) reconciles '
        'the 18-column dictionary, mapping workbook, ordered map and proposed '
        'country displays. The [reference inventory](../tests/fixtures/v31_sources.json) '
        'records the original file hashes. Source paths below are relative to '
        '`tests/fixtures/v31_reference`.', '',
        'Regenerate or verify this file from the repository root. The command '
        'refuses to generate if the reconciled sources differ from the saved '
        'contract or the retained reference/golden hashes fail.', '',
        '```bash', '.venv/bin/python -m scripts.build_v31_dictionary',
        '.venv/bin/python -m scripts.build_v31_dictionary --check', '```', '',
    ]
    lines += table(('Source', 'Archive member', 'SHA256'), [
        (source['path'], source.get('archive_member', ''), source['sha256'])
        for source in contract['sources']])
    lines += ['## Field counts', '']
    lines += table(('Classification', 'Fields'), list(kinds.items()))
    lines += ['There are 188 respondent questions and 35 other fields. '
              'The ordered map has 222 rows. The only dictionary-only row is '
              '`attack_freq_missing`, a technical response-format control.', '']
    lines += table(('Form', 'All dictionary fields', 'Respondent questions'), [
        (form, count, contract['counts']['question_forms'].get(form, 0))
        for form, count in forms.items()])
    lines += table(('Core index', 'Scoring items'), list(core.items()))
    lines += [
        '## How to read field definitions', '',
        'Native dictionary columns appear with their exact names. Only nonempty '
        'native values are printed for each field. Omitted native columns are '
        'empty strings in the original row; no default has been added. All 18 '
        'columns remain in the saved contract and participate in metadata hashes.', '',
        'Radio and dropdown fields use the listed stored codes. A text field '
        'may additionally specify integer, number or date validation. Bounds '
        'come from the native validation columns; an empty bound does not '
        'supply an artificial limit. Blank Required Field flags are preserved, '
        'not converted into downstream scoring or eligibility rules.', '',
        'An absent key, JSON null and an empty string remain distinct source '
        'states. A declared special response code has the meaning printed '
        'for that field. Do not use 99, 98 or 96 universally. No 73-item '
        'screening choice list declares any of those codes. Explicit analytical '
        'missingness or applicability is separate from inventing a raw code.', '',
        'For attack frequency, `attack_freq` stores an actual integer of at '
        'least 2 when its branch applies. `attack_freq_missing` stores the '
        'separate response status. Numeric counts of 98 or 99 do not become '
        'missing merely because another field uses those codes.', '',
        '## Decisions outside this dictionary', '',
        '- The age field declares integer bounds 12-24; the local checklist '
        'asks for 10-19. Resolve any separate cohort restriction before '
        'enforcing eligibility. This document retains the original field bounds.',
        '- Historical study_id notes refer to import from an NDS registry. '
        'The later approved independent-intake design preserves source-issued '
        'IDs and links a separate NDS ID downstream. The deployed native ID '
        'field still needs source metadata evidence. Original notes below '
        'remain verbatim and do not override that later design decision.',
        '- The historical dictionary has no consent-named field. '
        '`screen_form_complete` has its own declared 0/1/2 codes and does not '
        'prove survey consent, NDS purpose consent or completion of every '
        'deployed instrument.',
        '- Country display rows are proposed crosswalk/English-display '
        'metadata. They do not establish translation acceptance, measurement '
        'equivalence or transfer permission.',
        '- Derived-field definitions do not prove that the pipeline populates '
        'each named output. Scoring remains provisional. Burden/profile '
        'rules and IWI coefficients require their stated approvals.', '',
        '## Derived field definitions', '',
    ]
    lines += table(('Field', 'Validation', 'Minimum', 'Maximum', 'Analytical definition'), [
        (field['name'], field['dictionary_metadata']['Text Validation Type OR Show Slider Number'],
         field['dictionary_metadata']['Text Validation Min'],
         field['dictionary_metadata']['Text Validation Max'],
         field['analysis_mapping']['scoring_or_direction'])
        for field in fields if field['kind'] == 'Derived variable / system output'])
    lines += ['`k6_raw` declares 0-24; the scorer uses a result named `K6_total`. '
              'They are not a blanket 0-100 output. Likewise `brs_raw`, '
              '`mspss_raw` and `gse_raw` have their own ranges. Name mapping '
              'and implemented computations belong to the scoring review.', '',
              '## Field index', '']
    lines += table(('Order', 'Field', 'Form', 'Core 73'), [
        (field['dictionary_order'], field['name'],
         field['dictionary_metadata']['Form Name'], 'Yes' if field['core_73'] else 'No')
        for field in fields])
    lines += ['## Field definitions', '']
    analytical_columns = [
        ('question_or_label', 'Analysis label'),
        ('response_code', 'Analysis response definition'),
        ('construct', 'Analysis construct'),
        ('NSES_index', 'Analysis index'),
        ('NSES_dimension', 'Analysis dimension'),
        ('reference_period', 'Analysis reference period'),
        ('display_condition', 'Analysis applicability'),
        ('scoring_or_direction', 'Analysis scoring direction'),
        ('source_provenance', 'Analysis provenance'),
        ('duplication_control', 'Analysis control note'),
        ('administration_stage', 'Analysis administration stage'),
        ('respondent_order', 'Analysis respondent order'),
        ('implementation_note', 'Analysis implementation note'),
    ]
    for field in fields:
        lines += [f"### {field['dictionary_order']:03d} {field['name']}", '']
        rows = [(key, field['dictionary_metadata'][key])
                for key in DICTIONARY_HEADERS if field['dictionary_metadata'][key] != '']
        rows += [('Classification', field['kind']),
                 ('Respondent question', 'Yes' if field['respondent_question'] else 'No'),
                 ('Core 73', 'Yes' if field['core_73'] else 'No'),
                 ('Declared special response codes', missing_definition(field)),
                 ('Dictionary row SHA256', field['dictionary_metadata_sha256'])]
        mapping = field['analysis_mapping'] or {}
        rows += [(label, mapping[key]) for key, label in analytical_columns if mapping.get(key)]
        if field['country_display']:
            countries = sorted({row['metadata']['country'] for row in field['country_display']})
            sources = sorted({row['source'] for row in field['country_display']})
            rows.append(('Country display references',
                         f"{len(field['country_display'])} rows; countries: "
                         + ', '.join(countries) + '; sources: ' + ', '.join(sources)))
        lines += table(('Property', 'Source definition'), rows)
    return '\n'.join(lines).rstrip() + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify without writing')
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/DATA_DICTIONARY_V31.md')
    parser.add_argument('--reference-root', type=Path, default=ROOT / 'tests/fixtures/v31_reference')
    args = parser.parse_args()
    for source in json.loads((ROOT / 'tests/fixtures/v31_sources.json').read_text(encoding='utf-8')):
        data = (ROOT / source['path']).read_bytes()
        if hashlib.sha256(data).hexdigest() != source['sha256']:
            parser.error('Retained reference/golden hash mismatch: ' + source['path'])
    contract = json.loads((ROOT / 'etl/contracts/data_contract_v31.json').read_text(encoding='utf-8'))
    if build_from_sources(args.reference_root) != contract:
        parser.error('Source contract differs from saved contract; review before regeneration')
    document = render_dictionary(contract)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding='utf-8') != document:
            print('Dictionary is missing or stale. Run python -m scripts.build_v31_dictionary.')
            return 1
        print('Dictionary matches all 223 verified source definitions.')
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding='utf-8')
    print(f'Wrote {len(contract["fields"])} verified field definitions to {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
