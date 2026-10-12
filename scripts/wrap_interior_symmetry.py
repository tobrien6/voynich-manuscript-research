"""Check bounded certificates for conditional interior symmetry of IID wrapping."""

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BASE = Path('research/line-wrap/interior')
PLAN = BASE / 'PLAN.md'
SETTINGS = BASE / 'settings.json'
RESULT = BASE / 'certificates.json'
PROTOCOL_COMMIT = '1a5a02a54147c0d1c30762f6ec9bc4585249e7d2'
METHOD = 'iid-greedy-wrap-interior-symmetry-v1'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode('utf-8')


def load_settings():
    raws = {}
    for path in (PLAN, SETTINGS):
        raw = (ROOT / path).read_bytes()
        frozen = subprocess.check_output(['git', 'show', f'{PROTOCOL_COMMIT}:{path.as_posix()}'], cwd=ROOT)
        require(raw == frozen, 'frozen protocol changed: ' + path.as_posix())
        raws[path] = raw
    settings = json.loads(raws[SETTINGS])
    require(type(settings['schema_version']) is int and settings['schema_version'] == 1
            and settings['analysis_id'] == METHOD, 'unknown certificate protocol')
    require(settings['theorem_minimum_row_tokens'] == 2
            and settings['scoring_minimum_row_tokens'] == 5, 'row domains changed')
    commit = settings['accepted_input_commit']
    require(type(commit) is str and re.fullmatch('[0-9a-f]{40}', commit), 'require exact accepted commit')
    for path, checksum in settings['input_sha256'].items():
        raw = (ROOT / path).read_bytes()
        require(digest(raw) == checksum, 'accepted artifact changed: ' + path)
        old = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT)
        require(raw == old, 'accepted Git blob changed: ' + path)
    return settings, raws


def law(item):
    support = item['support']
    require(type(support) is list and support and support == sorted(set(support))
            and all(type(x) is int and x > 0 for x in support), 'positive distinct support required')
    require(len(item['probabilities']) == len(support)
            and all(type(x) is str for x in item['probabilities']), 'exact rational probabilities required')
    probabilities = [Fraction(x) for x in item['probabilities']]
    require(all(x > 0 for x in probabilities) and sum(probabilities) == 1, 'invalid IID law')
    return dict(zip(support, probabilities))


def geometry(probabilities, capacity, separator):
    require(type(capacity) is int and capacity >= max(probabilities)
            and type(separator) is int and separator >= 0, 'invalid additive geometry')


def row_event_weight(row, probabilities, capacity, separator):
    """Ordered completed-row event weight conditional on its first width."""
    geometry(probabilities, capacity, separator)
    require(len(row) >= 2 and all(type(x) is int and x in probabilities for x in row),
            'the theorem needs at least two supported token positions')
    total = sum(row) + separator * (len(row) - 1)
    if total > capacity:
        return Fraction(0)
    weight = Fraction(1)
    for width in row[1:]:
        weight *= probabilities[width]
    tail = sum((p for width, p in probabilities.items()
                if total + separator + width > capacity), Fraction(0))
    return weight * tail


def wrap(values, capacity, separator):
    """Sequential append/carry trace; final row is never overflow-closed."""
    require(type(capacity) is int and capacity > 0 and type(separator) is int and separator >= 0,
            'invalid geometry')
    rows, current, used, start = [], [], 0, 0
    for index, width in enumerate(values):
        require(type(width) is int and 0 < width <= capacity, 'invalid token width')
        if current and used + separator + width > capacity:
            rows.append({'lengths': current, 'start': start, 'end_exclusive': index,
                         'occupied_width': used, 'carried_next_first': width})
            current, used, start = [], 0, index
        if current:
            used += separator
        current.append(width)
        used += width
    return rows, {'lengths': current, 'start': start, 'occupied_width': used,
                  'closed_by_overflow': False}


def scores(interior):
    """Exact accepted full and half centered normalized adjacent products."""
    require(len(interior) >= 3 and all(type(x) is int and x > 0 for x in interior),
            'scores require at least three positive interior widths')
    m, total = len(interior), sum(interior)
    deviations = [m * x - total for x in interior]
    squared = sum(x * x for x in deviations)
    if not squared:
        return Fraction(0), Fraction(0)
    adjacent = sum(a * b for a, b in zip(deviations, deviations[1:]))
    raw = Fraction(m * adjacent, (m - 1) * squared)
    cut = (m + 1) // 2
    early, late = deviations[:cut], deviations[cut:]
    half_adjacent = sum((Fraction(sum(b) ** 2 - sum(x * x for x in b), len(b))
                         for b in (early, late)), Fraction(0))
    half_adjacent += Fraction(sum(early) * sum(late), len(early) * len(late))
    half_expected = Fraction(m, (m - 1) * squared) * half_adjacent
    return raw + Fraction(1, m - 1), raw - half_expected


def half_key(interior):
    cut = (len(interior) + 1) // 2
    return tuple(sorted(interior[:cut])), tuple(sorted(interior[cut:]))


def mean(values):
    require(values, 'empty mean is undefined')
    return sum(values, Fraction(0)) / len(values)


def certify_case(case, probabilities, separator):
    a, z, bag, capacity = case['first'], case['last'], case['interior'], case['capacity']
    geometry(probabilities, capacity, separator)
    require(type(bag) is list and len(bag) <= 8, 'bounded interior bag required')
    orders = sorted(set(permutations(bag)))
    row = [a, *bag, z]
    weight = row_event_weight(row, probabilities, capacity, separator)
    total = sum(row) + separator * (len(row) - 1)
    status = ('zero_condition_exceeds_capacity' if total > capacity else
              'zero_condition_no_overflow' if not weight else
              'completed_short' if len(row) < 5 else 'completed_eligible')
    require(status == case['expected_status'], 'known class status differs: ' + case['id'])
    result = {'id': case['id'], 'law_id': case['law_id'], 'capacity': capacity,
              'first': a, 'last': z, 'interior_bag': bag, 'row_tokens': len(row),
              'occupied_width': total, 'status': status, 'candidate_unique_orders': len(orders),
              'per_order_event_weight_given_first': str(weight),
              'class_event_weight_given_first': str(weight * len(orders)),
              'conditional_order_probability': str(Fraction(1, len(orders))) if weight else None,
              'mean_full_centered': None, 'mean_half_centered': None, 'orders': [], 'half_classes': []}
    if not weight:
        return result
    full, half, groups = [], [], defaultdict(list)
    for order in orders:
        row = [a, *order, z]
        require(row_event_weight(row, probabilities, capacity, separator) == weight,
                'ordered event weights are not equal')
        next_events = []
        prefix_product = Fraction(1)
        for value in row[1:]:
            prefix_product *= probabilities[value]
        sequential_sum = Fraction(0)
        for incoming, probability in probabilities.items():
            traced, tail = wrap(row + [incoming], capacity, separator)
            closes = bool(traced and traced[0]['lengths'] == row)
            event = prefix_product * probability if closes else Fraction(0)
            sequential_sum += event
            next_events.append({'width': incoming, 'closes_selected_row': closes,
                                'event_weight_given_first': str(event)})
        require(sequential_sum == weight, 'sequential overflow and product/tail formula differ')
        c, h = scores(order) if len(row) >= 5 else (None, None)
        result['orders'].append({'interior': list(order),
                                 'event_weight_given_first': str(weight),
                                 'conditional_probability': result['conditional_order_probability'],
                                 'full_centered': str(c) if c is not None else None,
                                 'half_centered': str(h) if h is not None else None,
                                 'next_width_events': next_events})
        if c is not None:
            full.append(c)
            half.append(h)
            groups[half_key(order)].append(h)
    if full:
        require(mean(full) == mean(half) == 0, 'conditional centered mean is not zero')
        result['mean_full_centered'], result['mean_half_centered'] = '0', '0'
        for (early, late), values in sorted(groups.items()):
            require(mean(values) == 0, 'within-half class mean is not zero')
            result['half_classes'].append({'early_bag': list(early), 'late_bag': list(late),
                                          'unique_orders': len(values),
                                          'conditional_order_probability': str(Fraction(1, len(values))),
                                          'mean_half_centered': '0'})
    return result


def certify_stream(fixture, probabilities, separator):
    capacity = fixture['capacity']
    geometry(probabilities, capacity, separator)
    original, tail = wrap(fixture['lengths'], capacity, separator)
    require(len(original) == fixture['expected_completed_rows']
            and tail['lengths'] == fixture['expected_unclosed_tail'], 'whole-stream fixture differs')
    require(all(len(r['lengths']) >= 5 for r in original), 'fixture row is not score eligible')
    alternatives = [sorted(set(permutations(r['lengths'][1:-1]))) for r in original]
    records, full, half, groups = [], [], [], defaultdict(list)
    for chosen in product(*alternatives):
        stream = fixture['lengths'][:]
        for row, middle in zip(original, chosen):
            stream[row['start'] + 1:row['end_exclusive'] - 1] = middle
        traced, current_tail = wrap(stream, capacity, separator)
        invariant = lambda r: {k: v for k, v in r.items() if k != 'lengths'}
        require([invariant(r) for r in traced] == [invariant(r) for r in original]
                and current_tail == tail, 'permutation changed closure or tail')
        require([(r['lengths'][0], r['lengths'][-1]) for r in traced] ==
                [(r['lengths'][0], r['lengths'][-1]) for r in original], 'endpoints changed')
        row_scores = [scores(r['lengths'][1:-1]) for r in traced]
        c, h = mean([x[0] for x in row_scores]), mean([x[1] for x in row_scores])
        probability = Fraction(1)
        for value in stream:
            probability *= probabilities[value]
        full.append(c)
        half.append(h)
        groups[tuple(half_key(middle) for middle in chosen)].append(h)
        records.append({'stream': stream, 'completed_rows': traced, 'unclosed_tail': current_tail,
                        'iid_stream_probability': str(probability),
                        'equal_row_full_centered': str(c), 'equal_row_half_centered': str(h)})
    require(len(records) == fixture['expected_joint_interior_orders'], 'joint orbit size differs')
    require(len({r['iid_stream_probability'] for r in records}) == 1,
            'full-stream IID weights differ')
    require(mean(full) == mean(half) == 0 and all(mean(v) == 0 for v in groups.values()),
            'joint conditional centered means differ')
    original_scores = [scores(r['lengths'][1:-1]) for r in original]
    return {'capacity': capacity, 'original_stream': fixture['lengths'],
            'original_completed_rows': original, 'original_unclosed_tail': tail,
            'original_equal_row_full_centered': str(mean([x[0] for x in original_scores])),
            'original_equal_row_half_centered': str(mean([x[1] for x in original_scores])),
            'joint_unique_orders': len(records), 'conditional_order_probability': str(Fraction(1, len(records))),
            'mean_full_centered': '0', 'mean_half_centered': '0',
            'joint_half_class_sizes': sorted(len(v) for v in groups.values()), 'orders': records}


def build_report():
    settings, raws = load_settings()
    laws = {item['id']: law(item) for item in settings['laws']}
    cases = [certify_case(case, laws[case['law_id']], settings['separator_width'])
             for case in settings['cases']]
    fixture = settings['stream_fixture']
    return {'schema_version': 1, 'analysis_id': METHOD, 'status': settings['status'],
            'protocol_commit': PROTOCOL_COMMIT, 'accepted_input_commit': settings['accepted_input_commit'],
            'protocol_sha256': digest(raws[PLAN]), 'settings_sha256': digest(raws[SETTINGS]),
            'input_sha256': settings['input_sha256'],
            'implementation_sha256': {p: digest((ROOT / p).read_bytes()) for p in
                ('scripts/wrap_interior_symmetry.py', 'tests/test_wrap_interior_symmetry.py')},
            'laws': settings['laws'], 'cases': cases,
            'stream_fixture': certify_stream(fixture, laws[fixture['law_id']], settings['separator_width']),
            'limitations': ['Ideal IID additive-width model only; synthetic certificates are not a corpus sample.',
                            'Conditioning requires positive probability and at least two token positions.',
                            'Score inclusion uses overflow-closed rows with at least five tokens.',
                            'Zero conditional expectation does not imply zero in every realization.',
                            'No stationary assumption or independence between rows is inferred.',
                            'No manuscript geometry, glyph identity, language or translation is established.']}


def protect_output(path):
    require(not path.exists() and not path.is_symlink(), 'output must be a new unlinked file')
    require(not path.resolve().is_relative_to((ROOT / 'data/raw').resolve())
            and not path.resolve().is_relative_to((ROOT / '.git').resolve()), 'protected output directory')


def write_report(path):
    protect_output(path)
    raw = encoded(build_report())
    protect_output(path)
    with path.open('xb') as stream:
        stream.write(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            write_report(args.output)
            print('Wrote all fixed IID wrapping symmetry certificates.')
        else:
            require(args.check.read_bytes() == encoded(build_report()), 'certificate report differs from replay')
            print('All fixed certificates reproduce byte for byte.')
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'wrapping symmetry failed: {error}\n')


if __name__ == '__main__':
    main()
