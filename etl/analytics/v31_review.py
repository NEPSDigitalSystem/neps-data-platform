"""Count-only review of authorised source snapshots; no cohort decisions.

Callers must authorise access before supplying a snapshot. The repository
review method provides that boundary; this pure helper exposes no raw answers.
"""
from collections import Counter
from etl.contracts.v31 import canonical_digest


def completion(contract, payload, validated_values, issues):
    stages = {'screening': ['neps31_screening'], 'cohort_interest': ['neps31_cohort_interest'],
              'extended_baseline': ['neps31_extended_baseline'],
              'detailed_psychosocial': ['neps31_yeb', 'neps31_ycad']}
    groups = {name: [] for name in stages}
    for field in contract['fields']:
        if field['respondent_question']:
            form = field['dictionary_metadata']['Form Name']
            for name, forms in stages.items():
                if form in forms:
                    groups[name].append(field['name'])
    result = {}
    for stage, names in groups.items():
        counts = Counter()
        for name in names:
            if name not in payload:
                counts['absent'] += 1
            elif payload[name] is None:
                counts['null'] += 1
            elif payload[name] == '':
                counts['empty'] += 1
            elif name in issues:
                counts[issues[name]] += 1
            elif name in validated_values:
                counts['valid'] += 1
            else:
                counts['unverified'] += 1
        result[stage] = {'expected': len(names), 'states': dict(counts),
                         'complete_valid': counts['valid'] == len(names)}
    return {'contract_sha256': canonical_digest(contract), 'question_count': 188,
            'stages': result, 'all_valid': all(x['complete_valid'] for x in result.values())}
