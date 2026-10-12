"""Exact synthetic independent-slot length controls with fixed positional means."""
import argparse
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = 'research/baselines/independent-position-length/'
PLAN = BASE + 'PLAN.md'
SETTINGS = BASE + 'settings.json'
PINS = {
    PLAN: '0f4bf29183101160479a4f558a6449033a8c8c1e578613aeeae9c3a9d110546a',
    SETTINGS: '23bca11f922629bb5d9fed70152db75abb63d225a459a4c99b997a0a3533b686',
}
FAMILIES = ['flat', 'half_step', 'increasing', 'decreasing']
FIELDS = ['raw', 'unrestricted_expectation', 'half_expectation', 'unrestricted_centered', 'half_centered']
COLUMNS = ['bits', 'raw_total', 'unrestricted_centered_total', 'half_centered_total',
           'half_centered_early', 'half_centered_bridge', 'half_centered_late']


def pair(value):
    return [str(value.numerator), str(value.denominator)]


def large(value):
    return {'encoding': 'base16-integer-strings', 'numerator': format(value.numerator, 'x'),
            'denominator': format(value.denominator, 'x'), 'float_approx': float(value)}


def inputs():
    for name, expected in PINS.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError('frozen synthetic input changed: ' + name)
    settings = json.loads((ROOT / SETTINGS).read_text())
    for name, expected in settings['reference_sha256'].items():
        raw = subprocess.check_output(['git', 'show', settings['reference_commit'] + ':' + name], cwd=ROOT)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('frozen historical score reference changed: ' + name)
    return settings


def values(family, size, bits):
    if (family not in FAMILIES or type(size) is not int or size not in range(3, 11)
            or not isinstance(bits, (list, tuple))
            or len(bits) != size or any(type(b) is not int or b not in (0, 1) for b in bits)):
        raise ValueError('declared family, size and complete binary slots required')
    cut = (size + 1) // 2
    offsets = {'flat': [0] * size, 'half_step': [3 * (i >= cut) for i in range(size)],
               'increasing': list(range(size)), 'decreasing': list(reversed(range(size)))}
    return [2 + offset + bit for offset, bit in zip(offsets[family], bits)]


def score(counts):
    if (not isinstance(counts, (list, tuple)) or len(counts) < 3
            or any(type(x) is not int or x <= 0 for x in counts)):
        raise ValueError('three or more positive integer counts required')
    n, total = len(counts), sum(counts)
    deviations = [n * x - total for x in counts]
    squared = sum(x * x for x in deviations)
    scale = Fraction(n, (n - 1) * squared) if squared else Fraction()
    cut = (n + 1) // 2
    early, late = deviations[:cut], deviations[cut:]
    raw = [scale * sum(a * b for a, b in zip(early, early[1:])),
           scale * early[-1] * late[0], scale * sum(a * b for a, b in zip(late, late[1:]))]
    full = [scale * edges * Fraction(-squared, n * (n - 1)) for edges in (cut - 1, 1, n - cut - 1)]
    half = [scale * Fraction(sum(early) ** 2 - sum(x * x for x in early), len(early)),
            scale * Fraction(sum(early) * sum(late), len(early) * len(late)),
            scale * Fraction(sum(late) ** 2 - sum(x * x for x in late), len(late))]
    return {'raw': raw, 'unrestricted_expectation': full, 'half_expectation': half,
            'unrestricted_centered': [a - b for a, b in zip(raw, full)],
            'half_centered': [a - b for a, b in zip(raw, half)], 'constant': not squared}


def population_counts(rows):
    if (not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows)
            or any(type(x) is not int or x <= 0 for row in rows for x in row)):
        raise ValueError('nonempty equal-width outcome population required')
    length = len(rows)
    means = [Fraction(sum(row[i] for row in rows), length) for i in range(len(rows[0]))]
    covariance = [[Fraction(sum(row[i] * row[j] for row in rows), length) - means[i] * means[j]
                   for j in range(len(means))] for i in range(len(means))]
    return means, covariance


def ensemble(family, size):
    vectors, measured, outcomes = [], [], []
    signs = {scope: {name: 0 for name in ('negative', 'zero', 'positive')}
             for scope in ('unrestricted', 'half')}
    for bits in itertools.product((0, 1), repeat=size):
        vector = values(family, size, bits)
        result = score(vector)
        vectors.append(vector)
        measured.append(result)
        full, half = sum(result['unrestricted_centered']), sum(result['half_centered'])
        for scope, point in (('unrestricted', full), ('half', half)):
            signs[scope]['positive' if point > 0 else ('negative' if point < 0 else 'zero')] += 1
        outcomes.append([''.join(map(str, bits)), pair(sum(result['raw'])), pair(full), pair(half)]
                        + [pair(v) for v in result['half_centered']])
    count = len(outcomes)
    aggregates = {field: [sum((item[field][i] for item in measured), Fraction()) / count for i in range(3)]
                  for field in FIELDS}
    means, covariance = population_counts(vectors)
    independent_covariance = all(value == (Fraction(1, 4) if i == j else 0)
                                 for i, row in enumerate(covariance) for j, value in enumerate(row))
    zero_checks = {}
    if family == 'flat':
        zero_checks = {scope: sum(aggregates[scope + '_centered']) == 0 for scope in ('unrestricted', 'half')}
    if family == 'half_step':
        zero_checks = {'half': sum(aggregates['half_centered']) == 0}
    return {'family': family, 'size': size, 'outcomes': outcomes, 'outcome_count': count,
            'outcome_weight': pair(Fraction(1, count)), 'total_probability': pair(Fraction(1)),
            'constant_outcomes': sum(item['constant'] for item in measured),
            'ensemble_components': {field: [large(v) for v in triplet] for field, triplet in aggregates.items()},
            'ensemble_total_scores': {scope: large(sum(aggregates[scope + '_centered'])) for scope in ('unrestricted', 'half')},
            'total_score_sign_counts': signs,
            'total_score_sign_probabilities': {scope: {name: pair(Fraction(number, count)) for name, number in summary.items()}
                                              for scope, summary in signs.items()},
            'population_count_means': [pair(v) for v in means],
            'population_count_covariance': [[pair(v) for v in row] for row in covariance],
            'population_covariance_matches_independent_bits': independent_covariance,
            'known_zero_predictions': zero_checks}


def decode(value):
    return Fraction(int(value['numerator'], 16), int(value['denominator'], 16))


def summarize_primary(record):
    components = [decode(v) for v in record['ensemble_components']['half_centered']]
    return {'family': record['family'], 'size': record['size'],
            'half_total_strictly_positive': sum(components) > 0,
            'early_strictly_positive': components[0] > 0, 'late_strictly_positive': components[2] > 0,
            'all_fixed_counterexample_predictions_pass': sum(components) > 0 and components[0] > 0 and components[2] > 0}


def report(progress=None):
    settings = inputs()
    results = []
    for family in settings['families']:
        for size in settings['sizes']:
            results.append(ensemble(family, size))
        if progress:
            progress(family + ': all fixed sizes enumerated')
    index = {(r['family'], r['size']): r for r in results}
    symmetries = []
    for size in settings['sizes']:
        increasing = {r[0]: r[1:] for r in index['increasing', size]['outcomes']}
        decreasing = index['decreasing', size]['outcomes']
        passed = sum(row[1:] == increasing[''.join('1' if b == '0' else '0' for b in row[0])] for row in decreasing)
        symmetries.append({'size': size, 'paired_outcomes': len(decreasing), 'exact_equal_outcomes': passed,
                           'all_six_retained_scores_equal': passed == len(decreasing)})
    return {'schema_version': 1, 'method': 'independent-position-count-exhaustive-control-v1',
            'status': 'fixed invented process ensembles; no manuscript fit or causal mechanism adoption',
            'python_version': platform.python_version(), 'input_pins': PINS,
            'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'reference_commit': settings['reference_commit'], 'reference_sha256': settings['reference_sha256'],
            'outcome_columns': COLUMNS, 'component_order': ['early', 'bridge', 'late'],
            'outcome_fraction_encoding': 'decimal numerator/denominator string pairs',
            'ensemble_fraction_encoding': 'labelled base16 integer strings plus approximate float',
            'joint_count_law': 'independent fair Bernoulli bits plus fixed position offsets; product probabilities',
            'processes': results, 'gradient_direction_symmetry': symmetries,
            'primary_predictions': [summarize_primary(index[family, settings['primary_size']])
                                    for family in ('increasing', 'decreasing')],
            'complete_outcome_records': sum(r['outcome_count'] for r in results),
            'new_random_draws': 0, 'manuscript_rows_scored': 0, 'manuscript_tail_probabilities': 0}


def protect_output(path):
    protected = [ROOT / name for name in PINS] + [Path(__file__).resolve()]
    resolved = path.resolve()
    if (any(resolved.is_relative_to((ROOT / name).resolve()) for name in ('data', 'scripts'))
            or any(resolved == p.resolve() or (path.exists() and p.exists() and path.samefile(p)) for p in protected)):
        raise ValueError('output aliases synthetic inputs, source/code directories or producer')


def serialize(value, compressed=False):
    raw = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    return gzip.compress(raw, mtime=0) if compressed else raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--new-report', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        path = args.new_report or args.check
        protect_output(path)
        if args.new_report and (path.exists() or path.is_symlink()):
            raise ValueError('new report destination already exists')
        result = report(progress=lambda message: print(message, flush=True))
        payload = serialize(result, compressed=path.suffix == '.gz')
        if args.check:
            if path.read_bytes() != payload:
                raise ValueError('complete synthetic report differs from byte replay')
        else:
            protect_output(path)
            with path.open('xb') as output:
                output.write(payload)
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Independent position-length control failed: {error}\n')
    print('All 32 process ensembles verified.' if args.check else 'All 32 process ensembles saved.')


if __name__ == '__main__':
    main()
