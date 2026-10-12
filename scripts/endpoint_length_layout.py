"""Exact independent-token counterexample for endpoint edit-cost contrasts."""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path

try:
    from .audit_eva_token_coverage import encoded
    from .audit_transliterations import ROOT
    from .paragraph_endpoint_distance import normalized_distance
    from .paragraph_token_corpus import digest, protect_outputs, strict_json
except ImportError:
    from audit_eva_token_coverage import encoded
    from audit_transliterations import ROOT
    from paragraph_endpoint_distance import normalized_distance
    from paragraph_token_corpus import digest, protect_outputs, strict_json


PLAN = Path('research/baselines/ENDPOINT_LENGTH_LAYOUT_PLAN.md')
METRIC = Path('scripts/paragraph_endpoint_distance.py')
METRIC_SHA = '783420f1dd49cc29c992d7c09994d9f176bbe221660b063584cb95260b3346fe'
TEST = Path('tests/test_endpoint_length_layout.py')
VERSION = 'independent-binary-token-length-layout-v1'
ALPHABET = 'ab'
CONTROLS = ('unrestricted_interior', 'fixed_length_pattern')
FAMILIES = (('blocked_lengths', (1, 1, 1, 2, 2, 2)),
            ('alternating_lengths', (1, 2, 1, 2, 1, 2)),
            ('uniform_short', (1, 1, 1, 1, 1, 1)))
PREDICTIONS = ((Fraction(21, 8), Fraction(23, 8), Fraction(21, 8)),
               (Fraction(25, 8), Fraction(23, 8), Fraction(25, 8)),
               (Fraction(5, 2), Fraction(5, 2), Fraction(5, 2)))


def rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def value(record):
    return Fraction(record['numerator'], record['denominator'])


def validate_lengths(lengths):
    if not isinstance(lengths, (list, tuple)) or not lengths or any(
            type(n) is not int or n not in (1, 2) for n in lengths):
        raise ValueError('nonempty binary-token lengths 1 or 2 required')


def draws(lengths):
    validate_lengths(lengths)
    spaces = [[''.join(letters) for letters in product(ALPHABET, repeat=n)] for n in lengths]
    return product(*spaces)


def identity_orders(lengths, fixed_lengths):
    validate_lengths(lengths)
    if type(fixed_lengths) is not bool:
        raise ValueError('fixed-length choice must be Boolean')
    size = len(lengths)
    if size == 1:
        return [(0,)]
    return [(0, *middle, size - 1) for middle in permutations(range(1, size - 1))
            if not fixed_lengths or all(lengths[node] == lengths[slot]
                                        for slot, node in enumerate(middle, 1))]


def costs(tokens):
    if not isinstance(tokens, (list, tuple)) or not tokens or any(
            not isinstance(token, str) or not token for token in tokens):
        raise ValueError('nonempty token strings required')
    return [[None if a == b else normalized_distance(tokens[a], tokens[b])
             for b in range(len(tokens))] for a in range(len(tokens))]


def histogram(values):
    return [{'value': rational(item), 'count': count} for item, count in sorted(Counter(values).items())]


def path_moments(weights, orders):
    size = len(weights)
    if not size or any(len(row) != size for row in weights):
        raise ValueError('nonempty square weight matrix required')
    for a, row in enumerate(weights):
        for b, weight in enumerate(row):
            if (a == b and weight is not None) or (a != b and not isinstance(weight, Fraction)):
                raise ValueError('off-diagonal Fractions and null diagonal required')
    if not isinstance(orders, (list, tuple)) or not orders or any(not isinstance(order, tuple) for order in orders):
        raise ValueError('distinct complete anchored identity orders required')
    if len(set(orders)) != len(orders) or any(
            len(order) != size or any(type(i) is not int for i in order)
            or set(order) != set(range(size)) or order[0] != 0 or order[-1] != size - 1
            for order in orders):
        raise ValueError('distinct complete anchored identity orders required')
    if tuple(range(size)) not in orders:
        raise ValueError('original identity path must be allowed')
    scores = [sum((weights[a][b] for a, b in zip(order, order[1:])), Fraction()) for order in orders]
    mean = sum(scores, Fraction()) / len(scores)
    variance = sum(((score - mean) ** 2 for score in scores), Fraction()) / len(scores)
    observed = sum((weights[i][i + 1] for i in range(size - 1)), Fraction())
    if variance == 0 and observed != mean:
        raise ValueError('invariant reference contradicts original path')
    return {'possible_identity_orders': len(orders), 'conditional_mean_cost_sum': rational(mean),
            'conditional_variance_cost_sum': rational(variance), 'centered_cost_sum': rational(observed - mean),
            'path_cost_histogram': histogram(scores), 'invariant': variance == 0}


def pair_expectations():
    results = []
    for left_length, right_length in product((1, 2), repeat=2):
        pairs = [(a[0], b[0]) for a, b in product(draws((left_length,)), draws((right_length,)))]
        mean = sum((normalized_distance(a, b) for a, b in pairs), Fraction()) / len(pairs)
        expected = Fraction(1, 2) if left_length == right_length else Fraction(5, 8)
        if mean != expected:
            raise ValueError('fixed binary-pair expectation failed')
        results.append({'left_length': left_length, 'right_length': right_length,
                        'pair_count': len(pairs), 'expected_cost': rational(mean)})
    return results


def family(name, lengths, predictions):
    validate_lengths(lengths)
    if len(lengths) != 6:
        raise ValueError('fixed demonstration families require six loci')
    orders = [identity_orders(lengths, flag) for flag in (False, True)]
    count = 2 ** sum(lengths)
    records = []
    for index, tokens in enumerate(draws(lengths)):
        weights = costs(tokens)
        observed = sum((weights[i][i + 1] for i in range(len(tokens) - 1)), Fraction())
        records.append({'draw_index': index, 'tokens': list(tokens), 'probability': rational(Fraction(1, count)),
                        'observed_cost_sum': rational(observed),
                        'controls': [{'control_id': control, **path_moments(weights, allowed)}
                                     for control, allowed in zip(CONTROLS, orders)]})
    if len(records) != count:
        raise ValueError('complete draw cardinality changed')
    observed_mean = sum((value(r['observed_cost_sum']) for r in records), Fraction()) / count
    aggregate = []
    for ci, control in enumerate(CONTROLS):
        items = [r['controls'][ci] for r in records]
        centers = [value(r['centered_cost_sum']) for r in items]
        expectation = sum((value(r['conditional_mean_cost_sum']) for r in items), Fraction()) / count
        center = sum(centers, Fraction()) / count
        aggregate.append({'control_id': control, 'possible_identity_orders': len(orders[ci]),
            'expected_conditional_mean_cost_sum': rational(expectation),
            'expected_centered_cost_sum': rational(center), 'expected_centered_mean_cost': float(center / 5),
            'expected_within_draw_conditional_variance_cost_sum': rational(
                sum((value(r['conditional_variance_cost_sum']) for r in items), Fraction()) / count),
            'centered_cost_sum_histogram': histogram(centers),
            'negative_draws': sum(x < 0 for x in centers), 'zero_draws': sum(x == 0 for x in centers),
            'positive_draws': sum(x > 0 for x in centers),
            'invariant_draws': sum(r['invariant'] for r in items),
            'varying_draws': sum(not r['invariant'] for r in items),
            'expected_cross_length_boundaries': rational(sum((sum(lengths[a] != lengths[b] for a,b in zip(path,path[1:]))
                                                              for path in orders[ci]), Fraction()) / len(orders[ci]))})
    actual = (observed_mean, *(value(r['expected_conditional_mean_cost_sum']) for r in aggregate))
    if actual != predictions:
        raise ValueError('fixed analytical expectation failed in ' + name)
    return {'family_id': name, 'lengths': list(lengths), 'boundary_count': 5, 'draw_count': count,
            'uniform_draw_probability': rational(Fraction(1, count)),
            'original_cross_length_boundaries': sum(a != b for a,b in zip(lengths,lengths[1:])),
            'predicted_mean_cost_sums': {'observed': rational(predictions[0]),
                'unrestricted': rational(predictions[1]), 'length_fixed': rational(predictions[2])},
            'expected_observed_cost_sum': rational(observed_mean), 'controls': aggregate, 'draws': records}


def build(root=ROOT):
    if digest((root / METRIC).read_bytes()) != METRIC_SHA:
        raise ValueError('accepted endpoint metric changed')
    return {'schema_version': 1, 'producer_version': VERSION, 'synthetic_only': True,
        'manuscript_inputs_used': False, 'pending_parent_inputs_used': False,
        'inputs': {'plan_path': str(PLAN), 'plan_sha256': digest((root / PLAN).read_bytes()),
                   'metric_path': str(METRIC), 'metric_sha256': METRIC_SHA,
                   'implementation_sha256': digest((root / 'scripts/endpoint_length_layout.py').read_bytes())},
        'method': {'alphabet': ALPHABET, 'tokens': 'independent fair letters conditional on each fixed length',
                   'loci': 'six distinct identities, one token per locus; first/last endpoint coincide',
                   'distance': 'accepted unit-cost native ASCII Levenshtein divided by maximum token length',
                   'controls': list(CONTROLS), 'moments': 'direct complete allowed-identity-path enumeration',
                   'tail_or_decision_criterion': None},
        'pair_expectations': pair_expectations(),
        'families': [family(name, lengths, prediction) for (name, lengths), prediction in zip(FAMILIES, PREDICTIONS)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    reads = [ROOT / PLAN, ROOT / METRIC, ROOT / TEST, *([args.check] if args.check else [])]
    try:
        protect_outputs([args.output] if args.output else [], reads, root=ROOT)
        report = build(ROOT)
        if args.check and encoded(strict_json(args.check.read_bytes())) != encoded(report):
            raise ValueError('synthetic endpoint report differs from complete typed replay')
        if args.output:
            raw = encoded(report)
            protect_outputs([args.output], reads, root=ROOT)
            args.output.write_bytes(raw)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'endpoint layout demonstration failed: {error}\n')
    print('Verified all 1088 independent-token tuples and both complete order controls; no manuscript fit.')


if __name__ == '__main__':
    main()
