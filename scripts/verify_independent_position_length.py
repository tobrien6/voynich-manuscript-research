"""Independent bit-mask, rational-edge and ordered-occurrence synthetic check."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = 'research/baselines/independent-position-length/'
PINS = {BASE + 'PLAN.md': '0f4bf29183101160479a4f558a6449033a8c8c1e578613aeeae9c3a9d110546a',
        BASE + 'settings.json': '23bca11f922629bb5d9fed70152db75abb63d225a459a4c99b997a0a3533b686'}
FIELDS = ['raw', 'unrestricted_expectation', 'half_expectation', 'unrestricted_centered', 'half_centered']
COLUMNS = ['bits', 'raw_total', 'unrestricted_centered_total', 'half_centered_total',
           'half_centered_early', 'half_centered_bridge', 'half_centered_late']


def small(v):
    return [str(v.numerator), str(v.denominator)]


def aggregate(v):
    return {'encoding': 'base16-integer-strings', 'numerator': format(v.numerator, 'x'),
            'denominator': format(v.denominator, 'x'), 'float_approx': float(v)}


def edge_scores(vector):
    n = len(vector)
    assert n >= 3 and all(type(v) is int and v > 0 for v in vector)
    mean = Fraction(sum(vector), n)
    z = [Fraction(v) - mean for v in vector]
    squared = sum(v * v for v in z)
    cut = (n + 1) // 2
    left, right = range(cut), range(cut, n)
    scale = Fraction(n, n - 1) / squared if squared else Fraction()
    result = {field: [Fraction()] * 3 for field in FIELDS}
    def expected(a, b, distinct):
        products = [z[i] * z[j] for i in a for j in b if not distinct or i != j]
        return scale * sum(products, Fraction()) / len(products) if products else Fraction()
    unrestricted = expected(range(n), range(n), True)
    half = [expected(left, left, True), expected(left, right, False), expected(right, right, True)]
    for i in range(n - 1):
        component = 0 if i < cut - 1 else (1 if i == cut - 1 else 2)
        result['raw'][component] += scale * z[i] * z[i + 1]
        result['unrestricted_expectation'][component] += unrestricted
        result['half_expectation'][component] += half[component]
        result['unrestricted_centered'][component] += scale * z[i] * z[i + 1] - unrestricted
        result['half_centered'][component] += scale * z[i] * z[i + 1] - half[component]
    return result


def make_vector(family, n, bits, settings):
    if family == 'flat':
        offsets = [0 for _ in bits]
    elif family == 'half_step':
        offsets = [0 if i < (n + 1) // 2 else settings['half_step_increment'] for i in range(n)]
    elif family == 'increasing':
        offsets = [settings['gradient_increment'] * i for i in range(n)]
    else:
        assert family == 'decreasing'
        offsets = [settings['gradient_increment'] * (n - i - 1) for i in range(n)]
    return [settings['base'] + offset + b for offset, b in zip(offsets, bits)]


def process(family, n, settings):
    weight = Fraction(1, 2 ** n)
    outcomes, vectors, moments = [], [], []
    counts = {scope: Counter({'negative': 0, 'zero': 0, 'positive': 0}) for scope in ('unrestricted', 'half')}
    constants = 0
    for mask in range(2 ** n):
        bits = [(mask >> (n - i - 1)) & 1 for i in range(n)]
        vector = make_vector(family, n, bits, settings)
        score = edge_scores(vector)
        vectors.append(vector)
        moments.append(score)
        constants += len(set(vector)) == 1
        sums = [sum(score[field]) for field in ('raw', 'unrestricted_centered', 'half_centered')]
        outcomes.append([''.join(str(b) for b in bits)] + [small(v) for v in sums + score['half_centered']])
        for scope, value in zip(('unrestricted', 'half'), sums[1:]):
            counts[scope]['negative' if value < 0 else ('positive' if value > 0 else 'zero')] += 1
    means = [sum((Fraction(v[i]) * weight for v in vectors), Fraction()) for i in range(n)]
    covariances = [[sum(((Fraction(v[i]) - means[i]) * (Fraction(v[j]) - means[j]) * weight for v in vectors), Fraction())
                    for j in range(n)] for i in range(n)]
    component_means = {field: [sum((v[field][i] * weight for v in moments), Fraction()) for i in range(3)] for field in FIELDS}
    known = {}
    if family == 'flat':
        known = {scope: sum(component_means[scope + '_centered']) == 0 for scope in ('unrestricted', 'half')}
    elif family == 'half_step':
        known = {'half': sum(component_means['half_centered']) == 0}
    return {'family': family, 'size': n, 'outcomes': outcomes, 'outcome_count': 2 ** n,
            'outcome_weight': small(weight), 'total_probability': small(sum((weight for _ in outcomes), Fraction())),
            'constant_outcomes': constants,
            'ensemble_components': {field: [aggregate(v) for v in values] for field, values in component_means.items()},
            'ensemble_total_scores': {scope: aggregate(sum(component_means[scope + '_centered'])) for scope in ('unrestricted', 'half')},
            'total_score_sign_counts': {scope: dict(values) for scope, values in counts.items()},
            'total_score_sign_probabilities': {scope: {sign: small(weight * count) for sign, count in values.items()}
                                              for scope, values in counts.items()},
            'population_count_means': [small(v) for v in means],
            'population_count_covariance': [[small(v) for v in row] for row in covariances],
            'population_covariance_matches_independent_bits': all(v == (Fraction(1, 4) if i == j else 0)
                for i, row in enumerate(covariances) for j, v in enumerate(row)),
            'known_zero_predictions': known}


def primary(record):
    components = [Fraction(int(v['numerator'], 16), int(v['denominator'], 16))
                  for v in record['ensemble_components']['half_centered']]
    conditions = sum(components) > 0, components[0] > 0, components[2] > 0
    return {'family': record['family'], 'size': record['size'],
            'half_total_strictly_positive': conditions[0], 'early_strictly_positive': conditions[1],
            'late_strictly_positive': conditions[2], 'all_fixed_counterexample_predictions_pass': all(conditions)}


def expected_report(progress=None):
    for name, sha in PINS.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha
    settings = json.loads((ROOT / (BASE + 'settings.json')).read_text())
    for name, sha in settings['reference_sha256'].items():
        raw = subprocess.check_output(['git', 'show', settings['reference_commit'] + ':' + name], cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest() == sha
    records = []
    for family in settings['families']:
        for size in settings['sizes']:
            records.append(process(family, size, settings))
        if progress:
            progress(family + ': independent bit-mask outcomes verified')
    lookup = {(r['family'], r['size']): r for r in records}
    symmetries = []
    for size in settings['sizes']:
        a = lookup['increasing', size]['outcomes']
        b = lookup['decreasing', size]['outcomes']
        equal = sum(down[1:] == up[1:] for down, up in zip(b, reversed(a)))
        symmetries.append({'size': size, 'paired_outcomes': len(a), 'exact_equal_outcomes': equal,
                           'all_six_retained_scores_equal': equal == len(a)})
    return {'schema_version': 1, 'method': 'independent-position-count-exhaustive-control-v1',
            'status': 'fixed invented process ensembles; no manuscript fit or causal mechanism adoption',
            'python_version': platform.python_version(), 'input_pins': PINS,
            'implementation_sha256': hashlib.sha256((ROOT / 'scripts/independent_position_length.py').read_bytes()).hexdigest(),
            'reference_commit': settings['reference_commit'], 'reference_sha256': settings['reference_sha256'],
            'outcome_columns': COLUMNS, 'component_order': ['early', 'bridge', 'late'],
            'outcome_fraction_encoding': 'decimal numerator/denominator string pairs',
            'ensemble_fraction_encoding': 'labelled base16 integer strings plus approximate float',
            'joint_count_law': 'independent fair Bernoulli bits plus fixed position offsets; product probabilities',
            'processes': records, 'gradient_direction_symmetry': symmetries,
            'primary_predictions': [primary(lookup[family, settings['primary_size']]) for family in ('increasing', 'decreasing')],
            'complete_outcome_records': sum(len(r['outcomes']) for r in records),
            'new_random_draws': 0, 'manuscript_rows_scored': 0, 'manuscript_tail_probabilities': 0}


def compare(expected, received):
    options = {'sort_keys': True, 'separators': (',', ':'), 'allow_nan': False}
    if json.dumps(expected, **options) != json.dumps(received, **options):
        raise ValueError('complete typed independent synthetic reconstruction differs')


def main():
    if not __debug__:
        raise ValueError('independent verification requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT / (BASE + 'results.json.gz'))
    args = parser.parse_args()
    try:
        expected = expected_report(progress=lambda message: print(message, flush=True))
        raw = args.report.read_bytes()
        received = json.loads(gzip.decompress(raw) if args.report.suffix == '.gz' else raw)
        compare(expected, received)
    except (AssertionError, ValueError, OSError, EOFError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Independent position-length verification failed: {error}\n')
    print(json.dumps({'outcome_records': expected['complete_outcome_records'], 'outcome_score_values': 6 * expected['complete_outcome_records'],
                      'processes': len(expected['processes']), 'exact_count_covariance_entries': sum(r['size'] ** 2 for r in expected['processes']),
                      'gradient_direction_pairs': sum(r['paired_outcomes'] for r in expected['gradient_direction_symmetry'])}, sort_keys=True))


if __name__ == '__main__':
    main()
