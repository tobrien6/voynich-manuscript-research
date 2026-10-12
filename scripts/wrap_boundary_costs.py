"""Exact finite labelled-IID wrapping calibration; no manuscript input."""

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BASE = 'research/line-wrap/boundary'
PROTOCOL_COMMIT = '93d77fa935be05abbd9110f613eb60038663463c'
# The squash merge preserves the frozen bytes in main history; the original
# topic-plan commit remains chronology, rather than a runtime dependency.
PROTOCOL_SOURCE_COMMIT = '4fe88fd8df8ae35ff9761b6442fd6adda0a27ee0'
REFERENCES = ('research/line-wrap/PROTOCOL.md', 'research/line-wrap/parameters.json',
              'research/line-wrap/RESULTS.md', 'scripts/greedy_wrap_control.py',
              'research/line-wrap/interior/PROOF.md', 'research/transliteration/ENDPOINT_EDIT_DISTANCE.md',
              'scripts/paragraph_endpoint_distance.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def frozen_inputs():
    current = {}
    for name in ('PLAN.md', 'settings.json'):
        path = BASE + '/' + name
        raw = (ROOT / path).read_bytes()
        old = subprocess.check_output(['git', 'show', PROTOCOL_SOURCE_COMMIT + ':' + path], cwd=ROOT)
        require(raw == old, 'frozen protocol differs: ' + path)
        current[name] = raw
    settings = json.loads(current['settings.json'])
    require(settings['schema_version'] == 1
            and settings['analysis_id'] == 'labelled-iid-wrapping-boundary-cost-v1'
            and set(settings['reference_sha256']) == set(REFERENCES)
            and settings['finite_stream_tokens'] == 7 and settings['separator_width'] == 1
            and len(settings['cases']) == 8, 'wrong frozen calibration domain')
    for path, expected in settings['reference_sha256'].items():
        raw = subprocess.check_output(['git', 'show', settings['accepted_reference_commit'] + ':' + path], cwd=ROOT)
        require(sha(raw) == expected, 'archived reference differs: ' + path)
    return settings, {name: sha(raw) for name, raw in current.items()}


def edit_cost(left, right):
    require(isinstance(left, str) and isinstance(right, str) and left and right, 'require two nonempty labels')
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        row = [i]
        for j, b in enumerate(right, 1):
            row.append(min(row[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = row
    return Fraction(previous[-1], max(len(left), len(right)))


def law_record(law):
    labels = law['labels']
    require(isinstance(labels, list) and labels and len(set(labels)) == len(labels)
            and all(isinstance(label, str) and label and label.isascii() for label in labels), 'invalid label support')
    require(len(law['probabilities']) == len(labels) and all(isinstance(p, str) for p in law['probabilities']),
            'require exact probability strings')
    probabilities = [Fraction(p) for p in law['probabilities']]
    require(all(p > 0 for p in probabilities) and sum(probabilities) == 1, 'invalid positive label law')
    widths = [len(label) for label in labels]
    bins = sorted(set(widths))
    width_mass = {w: sum(p for p, width in zip(probabilities, widths) if width == w) for w in bins}
    costs = [[edit_cost(a, b) for b in labels] for a in labels]
    incoming = sum(probabilities[i] * probabilities[j] * costs[i][j]
                   for i in range(len(labels)) for j in range(len(labels)))
    conditional = {(u, v): sum(probabilities[i] * probabilities[j] * costs[i][j]
                               for i in range(len(labels)) for j in range(len(labels))
                               if widths[i] == u and widths[j] == v) / (width_mass[u] * width_mass[v])
                   for u in bins for v in bins}
    record = {'id': law['id'], 'labels': labels, 'probabilities': list(map(str, probabilities)), 'widths': widths,
              'pair_costs': [[str(value) for value in row] for row in costs],
              'width_probabilities': [{'width': w, 'probability': str(width_mass[w])} for w in bins],
              'width_conditioned_costs': [{'left_width': u, 'right_width': v, 'mean_cost': str(conditional[u, v])}
                                          for u in bins for v in bins],
              'incoming_pair_mean_cost': str(incoming)}
    return record, probabilities, costs, conditional, incoming


def wrap_trace(widths, capacity, separator):
    require(type(capacity) is int and capacity > 0 and type(separator) is int and separator >= 0
            and widths and all(type(w) is int and 0 < w <= capacity for w in widths), 'invalid wrapping geometry')
    rows, start, used = [], 0, 0
    for i, width in enumerate(widths):
        if i > start and used + separator + width > capacity:
            rows.append({'start': start, 'end_exclusive': i, 'occupied_width': used,
                         'carried_position': i, 'carried_width': width})
            start, used = i, 0
        if i > start:
            used += separator
        used += width
    return rows, {'start': start, 'end_exclusive': len(widths), 'occupied_width': used, 'closed_by_overflow': False}


def mean_record(observed, matched, denominator, incoming):
    if denominator == 0:
        return {'observed_mean': None, 'width_reference_mean': None,
                'width_centered_mean': None, 'incoming_centered_mean': None}
    return {'observed_mean': str(observed / denominator), 'width_reference_mean': str(matched / denominator),
            'width_centered_mean': str((observed - matched) / denominator),
            'incoming_centered_mean': str(observed / denominator - incoming)}


def case_record(case, law, horizon, separator):
    model, probabilities, costs, conditional, incoming = law_record(law)
    capacity = case['capacity']
    require(type(horizon) is int and horizon > 0 and type(capacity) is int
            and capacity >= 2 * max(model['widths']) + separator, 'capacity must exclude singleton closed rows')
    total_mass = eligible_mass = expected_count = observed = matched = Fraction()
    equal_observed = equal_matched = Fraction()
    signs = {key: Fraction() for key in ('negative', 'zero', 'positive')}
    groups, streams = {}, []
    for identities in product(range(len(model['labels'])), repeat=horizon):
        labels = [model['labels'][i] for i in identities]
        widths = [model['widths'][i] for i in identities]
        probability = Fraction(1)
        for identity in identities:
            probability *= probabilities[identity]
        rows, tail = wrap_trace(widths, capacity, separator)
        edges, s, m = [], Fraction(), Fraction()
        for index, (left, right) in enumerate(zip(rows, rows[1:])):
            a, b = left['end_exclusive'] - 1, right['start']
            require(a + 1 == b, 'boundary occurrence conservation failed')
            cost, expected = costs[identities[a]][identities[b]], conditional[widths[a], widths[b]]
            s += cost; m += expected
            edges.append({'left_row_index': index, 'right_row_index': index + 1,
                          'last_position': a, 'first_position': b, 'width_pair': [widths[a], widths[b]],
                          'observed_cost': str(cost), 'width_reference_cost': str(expected)})
        n = len(edges)
        residual = s - m
        total_mass += probability; expected_count += probability * n
        observed += probability * s; matched += probability * m
        if n:
            eligible_mass += probability
            equal_observed += probability * s / n; equal_matched += probability * m / n
            signs['positive' if residual > 0 else 'negative' if residual < 0 else 'zero'] += probability
        key = tuple(widths)
        if key not in groups:
            groups[key] = {'streams': 0, 'mass': Fraction(), 'count': n, 'observed': Fraction(), 'matched': Fraction()}
        group = groups[key]
        require(group['count'] == n, 'width-only inclusion differs within a width sequence')
        group['streams'] += 1; group['mass'] += probability
        group['observed'] += probability * s; group['matched'] += probability * m
        streams.append({'labels': labels, 'widths': widths, 'probability': str(probability),
                        'completed_rows': rows, 'unclosed_tail': tail, 'boundaries': edges, 'boundary_count': n,
                        'observed_cost_sum': str(s), 'width_reference_sum': str(m), 'width_centered_sum': str(residual),
                        'incoming_centered_sum': str(s - n * incoming),
                        'means': mean_record(s, m, n, incoming)})
    require(total_mass == 1 and sum(signs.values()) == eligible_mass, 'finite probability ledger differs')
    width_classes = []
    for widths, group in sorted(groups.items()):
        require(group['observed'] == group['matched'], 'conditional factorization check failed')
        width_classes.append({'widths': list(widths), 'label_stream_count': group['streams'],
                              'probability_mass': str(group['mass']), 'boundary_count': group['count'],
                              'weighted_observed_sum': str(group['observed']),
                              'weighted_width_reference_sum': str(group['matched']),
                              'means': mean_record(group['observed'], group['matched'],
                                                   group['mass'] * group['count'], incoming)})
    require(observed == matched and equal_observed == equal_matched, 'finite centered expectation differs')
    return {'id': case['id'], 'law_id': law['id'], 'capacity': capacity, 'separator': separator, 'horizon': horizon,
            'status': 'eligible_finite_calibration' if expected_count else 'no_eligible_boundary',
            'total_streams': len(streams), 'eligible_streams': sum(s['boundary_count'] > 0 for s in streams),
            'probability_mass': str(total_mass), 'eligible_probability_mass': str(eligible_mass),
            'no_boundary_probability_mass': str(1 - eligible_mass), 'expected_boundary_count': str(expected_count),
            'weighted_observed_sum': str(observed), 'weighted_width_reference_sum': str(matched),
            'weighted_eligible_stream_mean_sum': str(equal_observed),
            'weighted_eligible_width_reference_mean_sum': str(equal_matched),
            'eligible_residual_sign_probability': {key: str(value) for key, value in signs.items()},
            'pooled_boundaries': mean_record(observed, matched, expected_count, incoming),
            'equal_eligible_streams': mean_record(equal_observed, equal_matched, eligible_mass, incoming),
            'width_classes': width_classes, 'streams': streams}


def build():
    settings, protocol_hashes = frozen_inputs()
    laws = {law['id']: law for law in settings['laws']}
    return {'schema_version': 1, 'analysis_id': settings['analysis_id'], 'status': settings['status'],
            'protocol_commit': PROTOCOL_COMMIT, 'protocol_sha256': protocol_hashes,
            'accepted_reference_commit': settings['accepted_reference_commit'],
            'reference_sha256': settings['reference_sha256'],
            'implementation_sha256': {path: sha((ROOT / path).read_bytes()) for path in
                                      ('scripts/wrap_boundary_costs.py', 'tests/test_wrap_boundary_costs.py')},
            'laws': [law_record(law)[0] for law in settings['laws']],
            'cases': [case_record(case, laws[case['law_id']], settings['finite_stream_tokens'], settings['separator_width'])
                      for case in settings['cases']],
            'limits': ['Known finite IID synthetic labels only; no manuscript fit or physical-line/glyph mapping.',
                       'Widths and selection are label-independent after conditioning on the complete width sequence.',
                       'Both estimands retain initial transients and exclude the unclosed tail; neither is stationary.',
                       'Pooled boundaries and equal eligible streams use different denominators.',
                       'Zero-edge means are undefined; constant-width zero contrasts are retained calibrations.',
                       'No row independence, variance, p-value, language, decipherment or translation claim.']}


def serialize(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode('utf-8')


def protect_output(path):
    require(not path.exists() and not path.is_symlink(), 'output must be a new unlinked file')


def write_new(path, raw):
    protect_output(path)
    with path.open('xb') as stream:
        stream.write(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument('--output', type=Path)
    destination.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output)
        raw = serialize(build())
        if args.check:
            require(args.check.read_bytes() == raw, 'complete calibration record differs')
            print('All frozen inputs and finite stream/cost/probability ledgers reproduce exactly.')
        else:
            write_new(args.output, raw)
            print('Wrote complete known synthetic boundary-cost calibration.')
    except (ValueError, OSError, KeyError, TypeError, ZeroDivisionError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
