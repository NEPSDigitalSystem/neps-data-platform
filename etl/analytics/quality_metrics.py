"""Exact local reporting examples over synthetic or authorised observations.

No database, policy lookup, scientific thresholds or source mutation.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction

from etl.validation.v31_validator import branch_state, validate, RULES_VERSION


def rate(numerator, denominator):
    if (type(numerator) is not int or type(denominator) is not int
            or not 0 <= numerator <= denominator):
        raise ValueError('Counts must satisfy 0 <= numerator <= denominator')
    return None if denominator == 0 else Fraction(numerator, denominator)


def _fraction(value):
    if type(value) not in (int, Fraction):
        raise ValueError('Use exact integers or Fractions, not floats or text')
    return Fraction(value)


def quality_summary(payload, contract):
    """Current-rule question metrics; not a deployed-metadata approval check."""
    result = validate(payload, contract)
    fields = {f['name']: f['dictionary_metadata'] for f in contract['fields']
              if f['respondent_question']}
    predicates = {name: payload[name] for name, state in result.states.items()
                  if state == 'valid' and name in payload}
    applicable, excluded, unresolved = [], [], []
    for name, meta in fields.items():
        branch = branch_state(meta['Branching Logic (Show field only if...)'], predicates)
        if branch is False or result.states[name] == 'not_applicable':
            excluded.append(name)
        elif branch is None:
            unresolved.append(name)
        else:
            applicable.append(name)
    recorded = sum(name in payload and payload[name] not in (None, '') for name in fields)
    valid = sum(result.states[name] == 'valid' for name in applicable)
    invalid = sum(result.states[name] == 'invalid' for name in applicable)
    coded_attempts, declared_codes = 0, 0
    for name in applicable:
        meta = fields[name]
        if meta['Field Type'] not in ('radio', 'dropdown') or name not in payload or payload[name] in (None, ''):
            continue
        coded_attempts += 1
        choices = {part.split(',', 1)[0].strip() for part in
                   meta['Choices, Calculations, OR Slider Labels'].split('|') if ',' in part}
        declared_codes += type(payload[name]) is str and payload[name] in choices
    numeric_valid, numeric_invalid = 0, 0
    for field in contract['fields']:
        name, meta = field['name'], field['dictionary_metadata']
        if (meta['Field Type'] == 'text' and
                meta['Text Validation Type OR Show Slider Number'] in ('integer', 'number', 'date_ymd') and
                branch_state(meta['Branching Logic (Show field only if...)'], predicates) is True):
            numeric_valid += result.states[name] == 'valid'
            numeric_invalid += result.states[name] == 'invalid'
    return dict(rules_version=RULES_VERSION, expected_questions=len(fields),
                question_states=dict(Counter(result.states[name] for name in fields)),
                recorded=recorded, recorded_completeness=rate(recorded, len(fields)),
                applicable=len(applicable), excluded=len(excluded), applicability_unverified=len(unresolved),
                usable=valid, usable_completeness=rate(valid, len(applicable)),
                valid=valid, invalid=invalid, validity=rate(valid, valid + invalid),
                coded_attempts=coded_attempts, declared_codes=declared_codes,
                coding_consistency=rate(declared_codes, coded_attempts),
                numeric_date_valid=numeric_valid, numeric_date_invalid=numeric_invalid,
                numeric_date_validity=rate(numeric_valid, numeric_valid + numeric_invalid))


def moments(values):
    """Complete available values only. Callers select one comparable stratum."""
    items = sorted(_fraction(value) for value in values if value is not None)
    n = len(items)
    if not n:
        return dict(n=0, mean=None, median=None, sample_sd=None)
    mean = sum(items) / n
    median = items[n // 2] if n % 2 else (items[n // 2 - 1] + items[n // 2]) / 2
    with localcontext() as context:
        context.prec = 28
        variance = None if n < 2 else sum((x - mean) ** 2 for x in items) / (n - 1)
        sd = None if variance is None else (Decimal(variance.numerator) / Decimal(variance.denominator)).sqrt()
    return dict(n=n, mean=mean, median=median, sample_sd=sd)


def correlation(pairs):
    """Pairwise-complete Pearson r, 28-digit Decimal, no significance test."""
    values = [(_fraction(x), _fraction(y)) for x, y in pairs if x is not None and y is not None]
    n = len(values)
    if n < 2:
        return dict(n=n, r=None, reason='insufficient_pairs')
    mx = sum(x for x, _ in values) / n
    my = sum(y for _, y in values) / n
    xx = sum((x - mx) ** 2 for x, _ in values)
    yy = sum((y - my) ** 2 for _, y in values)
    xy = sum((x - mx) * (y - my) for x, y in values)
    if not xx or not yy:
        return dict(n=n, r=None, reason='constant_input')
    with localcontext() as context:
        context.prec = 28
        decimal = lambda x: Decimal(x.numerator) / Decimal(x.denominator)
        r = decimal(xy) / (decimal(xx) * decimal(yy)).sqrt()
    return dict(n=n, r=r, reason=None)


def composite_check(components, observed):
    """Independent arithmetic check. Missing components cannot imply zero."""
    names = ('EPI', 'ESI', 'SBI', 'MHDI', 'PFI')
    values = [components.get(name) for name in names]
    if any(value is None for value in values):
        return dict(expected=None, matches=observed is None, reason='unavailable_component')
    a, b, c, d, e = map(_fraction, values)
    if any(not 0 <= value <= 100 for value in (a, b, c, d, e)):
        raise ValueError('Normalized components must be in 0 through 100')
    expected = Fraction(3, 10)*a + Fraction(1, 4)*b + Fraction(1, 5)*c + Fraction(1, 5)*d + Fraction(1, 20)*(100-e)
    return dict(expected=expected, matches=observed is not None and _fraction(observed) == expected, reason=None)
