"""Pure local-evidence V3.1 scoring. No recruitment or clinical decisions.

Fractions retain full arithmetic precision. Persistence and permission checks
belong to an authorised integration, which is not supplied by this module.
"""
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from etl.contracts.v31 import canonical_digest

ALGORITHM = 'NEPS-V3.1-provisional-corrected-1;complete-items-only;equal-dimensions'
UNAVAILABLE = frozenset({'missing', 'refused', 'unknown', 'not_applicable', 'invalid'})


@dataclass(frozen=True)
class ItemIssue:
    field: str
    state: str


@dataclass(frozen=True)
class Score:
    value: Fraction | None
    issues: tuple[ItemIssue, ...] = ()


@dataclass(frozen=True)
class ScoringResult:
    scores: dict[str, Score]
    algorithm_version: str
    contract_sha256: str
    source_sha256: str
    provisional: bool = True


def composite(epi, esi, sbi, mhdi, pfi):
    """Only arithmetic, never a recruitment criterion."""
    values = [Fraction(str(v)) for v in (epi, esi, sbi, mhdi, pfi)]
    if any(v < 0 or v > 100 for v in values):
        raise ValueError('Component score outside 0–100')
    a, b, c, d, e = values
    return (30*a + 25*b + 20*c + 20*d + 5*(100-e))/100


class Scorer:
    def __init__(self, contract):
        self.contract_hash = canonical_digest(contract)
        self.groups = {}
        self.codes = {}
        self.reverse = set()
        core = contract['core_73_fields']
        fields = [f for f in contract['fields'] if f['core_73']]
        if len(core) != 73 or len(set(core)) != 73 or set(core) != {f['name'] for f in fields} or len(fields) != 73:
            raise ValueError('Unverified core membership')
        expected = {
            ('EPI', 'expectations'): (2, 1, 5), ('EPI', 'failure'): (2, 1, 5),
            ('EPI', 'caregivers'): (2, 1, 5), ('EPI', 'future'): (2, 1, 5),
            ('EPI', 'progress'): (2, 1, 5), ('ESI', 'finstrain'): (2, 0, 4),
            ('ESI', 'food'): (2, 0, 4), ('ESI', 'educost'): (2, 0, 4),
            ('ESI', 'materials'): (2, 0, 4), ('ESI', 'transport'): (2, 0, 4),
            ('SBI', 'anticipated_loved'): (8, 1, 5),
            ('SBI', 'anticipated_community'): (4, 1, 5),
            ('SBI', 'self_stigma_expect'): (4, 1, 5),
            ('SBI', 'help_seeking_self_stigma'): (3, 1, 5),
            ('MHDI', 'K6'): (6, 0, 4), ('PFI', 'resilience'): (6, 1, 5),
            ('PFI', 'social_support'): (12, 1, 7), ('PFI', 'self_efficacy'): (10, 1, 4),
        }
        for field in fields:
            name, meta, mapping = field['name'], field['dictionary_metadata'], field['analysis_mapping']
            if canonical_digest(meta) != field['dictionary_metadata_sha256']:
                raise ValueError('Dictionary hash mismatch')
            group = (mapping['NSES_index'], mapping['NSES_dimension'])
            if group not in expected or meta['Field Type'] != 'radio':
                raise ValueError('Unverified scoring group/type')
            _, lower, upper = expected[group]
            codes = [c.split(',', 1)[0].strip() for c in meta['Choices, Calculations, OR Slider Labels'].split('|')]
            if len(codes) != len(set(codes)) or set(codes) != {str(v) for v in range(lower, upper+1)}:
                raise ValueError('Unverified scoring codes')
            self.codes[name] = set(codes)
            self.groups.setdefault(group, []).append(name)
            direction = mapping['scoring_or_direction']
            if direction == '6−raw':
                self.reverse.add(name)
            elif direction:
                raise ValueError('Unverified scoring direction')
        if set(self.groups) != set(expected) or any(len(self.groups[g]) != expected[g][0] for g in expected):
            raise ValueError('Unverified dimension membership/count')
        # Exact source-map reverse entries, not inferred from a name pattern.
        if self.reverse != {'brs_02', 'brs_04', 'brs_06'}:
            raise ValueError('Unverified BRS reversal mapping')
        code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.version = ALGORITHM + ':' + canonical_digest({'contract': self.contract_hash, 'code': code_hash})

    def score(self, responses, *, missingness=None, epi_applicable=False, source_context=None):
        """epi_applicable=True requires externally confirmed applicability.

        Default unavailable prevents guessing for out-of-school/unknown status.
        missingness is explicit validated semantic evidence, not invented codes.
        Raw 98/99 are invalid for these screening fields in the actual dictionary.
        """
        missingness = missingness or {}
        if set(missingness) - set(self.codes) or any(v not in UNAVAILABLE for v in missingness.values()):
            raise ValueError('Unsupported semantic missingness')
        if type(epi_applicable) is not bool:
            raise ValueError('Applicability must be explicitly boolean')
        parsed, issues = {}, {}
        for name, valid_codes in self.codes.items():
            raw = responses.get(name)
            state = missingness.get(name)
            if state is None:
                if raw is None or raw == '':
                    state = 'missing'
                elif type(raw) not in (str, int) or str(raw) not in valid_codes:
                    state = 'invalid'
            if state:
                issues[name] = ItemIssue(name, state)
            else:
                parsed[name] = Fraction(int(raw))
        def group_score(group, lower, span):
            names = self.groups[group]
            unavailable = tuple(issues[n] for n in names if n in issues)
            if unavailable:
                return Score(None, unavailable)
            values = [6-parsed[n] if n in self.reverse else parsed[n] for n in names]
            return Score((sum(values)/len(values)-lower)/span*100)
        def mean(scores):
            problems = tuple(i for s in scores for i in s.issues)
            return Score(None, problems) if any(s.value is None for s in scores) else Score(sum(s.value for s in scores)/len(scores))
        output = {}
        for index, lower in [('EPI', 1), ('ESI', 0), ('SBI', 1)]:
            output[index] = mean([group_score(g, lower, 4) for g in self.groups if g[0] == index])
        if not epi_applicable:
            output['EPI'] = Score(None, output['EPI'].issues + (ItemIssue('EPI', 'applicability_unverified'),))
        output['MHDI'] = group_score(('MHDI', 'K6'), 0, 4)
        mhdi = output['MHDI']
        output['K6_total'] = Score(mhdi.value*24/100 if mhdi.value is not None else None, mhdi.issues)
        output['BRS_100'] = group_score(('PFI', 'resilience'), 1, 4)
        output['MSPSS_100'] = group_score(('PFI', 'social_support'), 1, 6)
        output['GSE_100'] = group_score(('PFI', 'self_efficacy'), 1, 3)
        output['PFI'] = mean([output[n] for n in ('BRS_100', 'MSPSS_100', 'GSE_100')])
        components = [output[n] for n in ('EPI', 'ESI', 'SBI', 'MHDI', 'PFI')]
        output['NSES'] = Score(None, tuple(i for s in components for i in s.issues)) if any(s.value is None for s in components) else Score(composite(*(s.value for s in components)))
        source_hash = canonical_digest({'responses': {n: responses[n] for n in self.codes if n in responses},
                                        'missingness': missingness, 'epi_applicable': epi_applicable,
                                        'source_context': source_context})
        return ScoringResult(output, self.version, self.contract_hash, source_hash)
