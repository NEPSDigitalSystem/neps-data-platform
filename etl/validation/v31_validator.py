"""Field-specific checks. No I/O, permissions, coercion or source filtering."""
from __future__ import annotations

import ast
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import re

RULES_VERSION = "NEPS-V3.1-validation-1;age-12-24"
SEMANTIC = frozenset({"missing", "refused", "unknown", "not_applicable", "invalid"})
# Match declared labels, never a universal numeric missing-value convention.
LABEL_STATES = {
    "Prefer not to answer": "refused", "Prefer not": "refused",
    "Do not know": "unknown", "Unsure": "unknown",
    "Not applicable": "not_applicable", "Never attended": "not_applicable",
    "Not attending school/training": "not_applicable",
    "No such responsibilities": "not_applicable", "No such family": "not_applicable",
    "Not available locally": "not_applicable",
}


@dataclass(frozen=True)
class Issue:
    field: str
    rule: str
    severity: str
    observed_state: str
    blocks_field: bool


@dataclass(frozen=True)
class ValidationResult:
    payload: dict
    values: dict
    issues: tuple[Issue, ...]
    states: dict[str, str]
    age_eligible: bool | None
    legacy_issues: dict[str, str]

    def summary(self):
        """Counts only, suitable for the already-authorised review endpoint."""
        return {"rules_version": RULES_VERSION, "age_eligible": self.age_eligible,
                "state_counts": dict(Counter(self.states.values())),
                "issue_counts": dict(Counter(i.rule for i in self.issues))}


def branch_state(expression, payload):
    """Strict equality/and/or grammar; missing predicates remain unknown."""
    if not expression:
        return True
    predicates = []
    def replace(match):
        name, code = match.groups()
        val = payload.get(name)
        predicates.append(None if val in (None, '') else val == code)
        return 'p' + str(len(predicates) - 1)
    replaced = re.sub(r"\[([a-z][a-z0-9_]*)\]\s*=\s*'([^']*)'", replace, expression)
    try:
        tree = ast.parse(replaced, mode='eval')
        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Name) and re.fullmatch(r'p\d+', node.id):
                return predicates[int(node.id[1:])]
            if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
                vals = [evaluate(n) for n in node.values]
                if isinstance(node.op, ast.And):
                    return False if False in vals else None if None in vals else True
                return True if True in vals else None if None in vals else False
            raise ValueError('Unsupported branching')
        return evaluate(tree)
    except (SyntaxError, ValueError, IndexError):
        return None


def _check(value, meta):
    """Return state, rule and legacy diagnostic for one present nonblank value."""
    kind = meta['Field Type']
    choices = dict(part.strip().split(',', 1) for part in
                   meta['Choices, Calculations, OR Slider Labels'].split('|') if ',' in part)
    choices = {code: label.strip() for code, label in choices.items()}
    if kind in ('radio', 'dropdown'):
        if type(value) is not str or value not in choices:
            return 'invalid', 'V03', 'invalid_code'
        state = LABEL_STATES.get(choices[value], 'valid')
        return state, 'V04' if state != 'valid' else '', state
    if kind == 'checkbox':
        if (type(value) is not dict or set(value) - set(choices)
                or any(type(v) is not str or v not in ('0', '1', '') for v in value.values())):
            return 'invalid', 'V03', 'invalid_checkbox'
        return 'valid', '', ''
    validation = meta['Text Validation Type OR Show Slider Number']
    if kind != 'text' or validation not in ('', 'integer', 'number', 'date_ymd'):
        return 'unverified', 'V05', 'validator_unverified'
    if type(value) is not str:
        return 'invalid', 'V02', 'invalid_text'
    if not validation:
        return 'valid', '', ''
    if validation == 'date_ymd':
        try:
            if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
                raise ValueError
            parsed = date.fromisoformat(value)
            lower, upper = (date.fromisoformat(meta[key]) if meta[key] else None
                            for key in ('Text Validation Min', 'Text Validation Max'))
        except ValueError:
            return 'invalid', 'V02', 'invalid_date'
    else:
        pattern = r'[+-]?[0-9]+' if validation == 'integer' else r'[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)'
        if not re.fullmatch(pattern, value):
            return 'invalid', 'V02', 'invalid_' + validation
        try:
            parsed = Decimal(value)
            lower, upper = (Decimal(meta[key]) if meta[key] else None
                            for key in ('Text Validation Min', 'Text Validation Max'))
        except InvalidOperation:
            return 'unverified', 'V05', 'validator_unverified'
    if (lower is not None and parsed < lower) or (upper is not None and parsed > upper):
        return 'invalid', 'V02', 'outside_dictionary_range'
    return 'valid', '', ''


def validate(payload, contract, *, source_fields=None, missingness=None):
    """Validate retained values; missing fields never prevent source receipt.

    Transport choices/numbers are exact strings. Administrative/derived values
    receive quality checks but cannot enter the analytical answer layer.
    """
    if type(payload) is not dict:
        raise ValueError('A source payload mapping is required')
    fields = ({f['name']: f['dictionary_metadata'] for f in contract['fields']}
              if source_fields is None else source_fields)
    missingness = {} if missingness is None else missingness
    if set(missingness) - set(fields) or any(s not in SEMANTIC for s in missingness.values()):
        raise ValueError('Unsupported semantic missingness')
    source_only = {f['name'] for f in contract['fields']
                   if not f['respondent_question'] and f['name'] != 'attack_freq_missing'}
    states, diagnostics = {}, {}
    for name, meta in fields.items():
        if name in missingness:
            state = missingness[name]
            states[name], diagnostics[name] = state, ('V04', state)
        elif name not in payload:
            states[name], diagnostics[name] = 'absent', ('V01', '')
        elif payload[name] is None:
            states[name], diagnostics[name] = 'null', ('V01', '')
        elif payload[name] == '':
            states[name], diagnostics[name] = 'empty', ('V01', '')
        else:
            state, rule, legacy = _check(payload[name], meta)
            states[name], diagnostics[name] = state, ('V08' if name == 'screen_form_complete' and rule else rule, legacy)
    # Do not evaluate a branch with a refused, invalid or unknown predicate.
    predicates = {name: payload[name] for name in fields
                  if states[name] == 'valid' and name in payload}
    # Remove inapplicable predicates before evaluating dependent branches.
    # Repeating removals handles chains independently of metadata row order.
    while predicates:
        blocked = [name for name in predicates
                   if branch_state(fields[name]['Branching Logic (Show field only if...)'], predicates) is not True]
        if not blocked:
            break
        for name in blocked:
            del predicates[name]
    values, legacy_issues, issues = {}, {}, []
    for name in dict.fromkeys([*fields, *payload]):
        if name not in fields:
            states[name] = 'unknown_field'
            issues.append(Issue(name, 'V06', 'warning', 'unknown_field', True))
            legacy_issues[name] = 'unknown_field'
            continue
        state = states[name]
        rule, legacy = diagnostics[name]
        if state == 'valid':
            branch = branch_state(fields[name]['Branching Logic (Show field only if...)'], predicates)
            if branch is not True:
                state = 'not_applicable' if branch is False else 'unverified'
                rule, legacy = 'V05', 'inapplicable' if branch is False else 'branch_unverified'
                states[name] = state
        if state != 'valid':
            severity = 'error' if state == 'invalid' else 'info' if state in ('absent', 'null', 'empty') else 'warning'
            issues.append(Issue(name, rule, severity, state, True))
        if name not in payload:
            continue
        if name in source_only:
            legacy_issues[name] = 'source_only_administrative_or_derived'
            issues.append(Issue(name, 'V07', 'info', 'source_only', True))
        elif state in ('valid', 'null', 'empty'):
            values[name] = deepcopy(payload[name])
        else:
            legacy_issues[name] = legacy
    age_eligible = None
    if 'age_years' in payload and states.get('age_years') == 'valid':
        age_eligible = 12 <= int(payload['age_years']) <= 24
    elif 'age_years' in payload and states.get('age_years') == 'invalid':
        age_eligible = False
    if age_eligible is False:
        issues.append(Issue('age_years', 'V11', 'error', 'ineligible_age', True))
    return ValidationResult(deepcopy(payload), values, tuple(issues), states,
                            age_eligible, legacy_issues)


SCORE_NAMES = ('EPI', 'ESI', 'SBI', 'MHDI', 'K6_total', 'BRS_100', 'MSPSS_100', 'GSE_100', 'PFI', 'NSES')


def validate_scores(result):
    """Check the workflow's exact rational JSON representation before storage."""
    scores = result.get('scores') if type(result) is dict else None
    if type(scores) is not dict:
        return (Issue('scores', 'V09', 'error', 'invalid', True),)
    issues = []
    for name in dict.fromkeys([*SCORE_NAMES, *scores]):
        field = 'scores.' + str(name)
        entry = scores.get(name)
        if name not in SCORE_NAMES or type(entry) is not dict or 'value' not in entry:
            issues.append(Issue(field, 'V09', 'error', 'invalid', True))
            continue
        value, reasons = entry['value'], entry.get('issues')
        valid_reasons = (type(reasons) is list and all(type(i) is dict
                         and type(i.get('field')) is str and bool(i['field'])
                         and type(i.get('state')) is str
                         and i.get('state') in SEMANTIC | {'applicability_unverified'} for i in reasons))
        if value is None:
            if not valid_reasons or not reasons:
                issues.append(Issue(field, 'V09', 'error', 'unexplained_unavailable', True))
            else:
                issues.append(Issue(field, 'V09', 'info', 'unavailable_score', False))
            continue
        valid_value = (type(value) is dict and set(value) == {'numerator', 'denominator'}
                       and type(value['numerator']) is int and type(value['denominator']) is int
                       and value['denominator'] > 0)
        if not valid_value or not valid_reasons or reasons:
            issues.append(Issue(field, 'V09', 'error', 'invalid', True))
            continue
        number = Fraction(value['numerator'], value['denominator'])
        if not 0 <= number <= (24 if name == 'K6_total' else 100) or (name == 'K6_total' and number.denominator != 1):
            issues.append(Issue(field, 'V09', 'error', 'outside_score_range', True))
    dependencies = {'MHDI': ('K6_total',), 'K6_total': ('MHDI',),
                    'PFI': ('BRS_100', 'MSPSS_100', 'GSE_100'),
                    'NSES': ('EPI', 'ESI', 'SBI', 'MHDI', 'PFI')}
    for parent, children in dependencies.items():
        entry = scores.get(parent)
        if type(entry) is dict and entry.get('value') is not None:
            if any(type(scores.get(child)) is dict and scores[child].get('value') is None for child in children):
                issues.append(Issue('scores.' + parent, 'V09', 'error', 'unavailable_dependency', True))
    return tuple(issues)
