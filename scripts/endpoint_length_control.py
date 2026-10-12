"""Preserve native endpoint-length patterns in fixed-cohort edit-cost controls."""

import argparse
from collections import Counter
from fractions import Fraction
from math import factorial
from pathlib import Path

try:
    from .audit_eva_token_coverage import encoded, IDENTITY_FIELDS
    from .audit_transliterations import ROOT
    from .paragraph_token_corpus import build as corpus_build, digest, protect_outputs, strict_json
    from .paragraph_endpoint_distance import build as parent_build, normalized_distance, rational, summary
    from .stratified_path_moments import weighted_moments
except ImportError:
    from audit_eva_token_coverage import encoded, IDENTITY_FIELDS
    from audit_transliterations import ROOT
    from paragraph_token_corpus import build as corpus_build, digest, protect_outputs, strict_json
    from paragraph_endpoint_distance import build as parent_build, normalized_distance, rational, summary
    from stratified_path_moments import weighted_moments


PLAN = Path('research/transliteration/ENDPOINT_LENGTH_CONTROL_PLAN.md')
PARENT = Path('research/transliteration/paragraph_endpoint_distance.json')
VERSION = 'anchored-endpoint-length-strata-v1'
CONTROLS = ('variant_endpoint_lengths', 'common_endpoint_lengths')
PINS = {
    str(PARENT): '1d17ec6362d9ec203c7e4d9218b3713cc03a1036b10a362f86c6814647e63818',
    'scripts/paragraph_endpoint_distance.py': '783420f1dd49cc29c992d7c09994d9f176bbe221660b063584cb95260b3346fe',
    'scripts/anchored_path_moments.py': '6b366d33f7d606ee5a5d3ae32d1519973547256c22a5f2b73842fc33d9b3633a',
}


def fraction(record):
    return Fraction(record['numerator'], record['denominator'])


def partition(labels):
    keys, ids = {}, []
    for label in labels:
        key = tuple(label)
        if key not in keys:
            keys[key] = len(keys)
        ids.append(keys[key])
    return ids


def moment_record(result, size):
    return {**summary(result['observed'], result['mean'], result['variance'], size - 1),
            'diagonal_variance': rational(result['diagonal_variance']),
            'twice_covariance_sum': rational(result['twice_covariance']),
            'adjacency_probability_matrix': [[None if p is None else rational(p) for p in row]
                                              for row in result['probabilities']],
            **{key: result[key] for key in ('nonzero_weight_possible_edges', 'joint_events_evaluated',
                'zero_joint_events', 'positive_joint_events', 'possible_interior_orders', 'invariant')}}


def analyze(corpus, parent):
    units = [p for p in corpus['paragraphs'] if p['common_eligible']]
    if encoded(corpus['cohort']) != encoded(parent['cohort']) or len(units) != len(parent['paragraphs']):
        raise ValueError('parent cohort changed')
    identity_fields = ('common_unit_id', 'page_id', 'member_keys', 'source_unit_ids')
    paragraphs = []
    for unit, old_unit in zip(units, parent['paragraphs']):
        identity = {key: unit[key] for key in identity_fields}
        if encoded(identity) != encoded({key: old_unit[key] for key in identity_fields}):
            raise ValueError('parent unit/member identities changed')
        if len(unit['variants']) != 4 or len(old_unit['variants']) != 4:
            raise ValueError('exactly four original variants required')
        lengths = []
        for variant, old in zip(unit['variants'], old_unit['variants']):
            if any(not row['tokens'] for row in variant['loci']):
                raise ValueError('empty endpoint; no silent filtering')
            key = {name: variant[name] for name in ('source_id', 'uncertain_spaces')}
            if encoded(key) != encoded({name: old[name] for name in key}):
                raise ValueError('parent variant order changed')
            loci = variant['loci']
            if encoded([{name: row[name] for name in IDENTITY_FIELDS} for row in loci]) != encoded(
                    [{name: row[name] for name in IDENTITY_FIELDS} for row in old['loci']]):
                raise ValueError('parent ordered locus identities changed')
            lengths.append([[len(row['tokens'][0]), len(row['tokens'][-1])] for row in loci])
        size = len(lengths[0])
        if any(len(pairs) != size for pairs in lengths):
            raise ValueError('paired locus counts changed')
        common = [sum((pairs[i] for pairs in lengths), []) for i in range(size)]
        common_ids = partition(common)
        variants = []
        for vi, (native, old) in enumerate(zip(unit['variants'], old_unit['variants'])):
            rows = native['loci']
            weights = [[None if a == b else normalized_distance(rows[a]['tokens'][-1], rows[b]['tokens'][0])
                        for b in range(size)] for a in range(size)]
            if encoded([[None if w is None else rational(w) for w in row] for row in weights]) != encoded(old['cost_matrix']):
                raise ValueError('parent cost matrix changed')
            controls = []
            for control, ids in zip(CONTROLS, (partition(lengths[vi]), common_ids)):
                result = weighted_moments(weights, ids)
                if rational(result['observed']) != old['observed_cost_sum']:
                    raise ValueError('original observed cost changed')
                controls.append({'control_id': control, 'stratum_ids': ids,
                    'interior_strata': [{'stratum_id': label, 'identity_indices': [i for i in range(1, size - 1) if ids[i] == label]}
                                        for label in sorted(set(ids[1:-1]))],
                    'retained_order_fraction': rational(Fraction(result['possible_interior_orders'], factorial(max(size - 2, 0)))),
                    'newly_invariant_from_parent': result['invariant'] and not old['invariant'],
                    'expected_cost_change_from_parent': rational(result['mean'] - fraction(old['conditional_mean_cost_sum'])),
                    'variance_change_from_parent': rational(result['variance'] - fraction(old['conditional_variance_cost_sum'])),
                    **moment_record(result, size)})
            variants.append({**{name: native[name] for name in ('source_id', 'uncertain_spaces')},
                             'initial_terminal_ascii_lengths': lengths[vi], 'controls': controls})
        paragraphs.append({**identity, 'common_length_vectors': common, 'variants': variants})
    aggregates = []
    for vi, old in enumerate(parent['variants']):
        controls = []
        for ci, control in enumerate(CONTROLS):
            records = [p['variants'][vi]['controls'][ci] for p in paragraphs]
            total = lambda field: sum((fraction(r[field]) for r in records), Fraction())
            value = summary(total('observed_cost_sum'), total('conditional_mean_cost_sum'),
                            total('conditional_variance_cost_sum'), sum(r['boundary_count'] for r in records))
            if value['observed_cost_sum'] != old['observed_cost_sum'] or value['boundary_count'] != old['boundary_count']:
                raise ValueError('parent aggregate observation changed')
            controls.append({'control_id': control, **value,
                'diagonal_variance': rational(total('diagonal_variance')),
                'twice_covariance_sum': rational(total('twice_covariance_sum')),
                'expected_cost_change_from_parent': rational(total('conditional_mean_cost_sum') - fraction(old['conditional_mean_cost_sum'])),
                'variance_change_from_parent': rational(total('conditional_variance_cost_sum') - fraction(old['conditional_variance_cost_sum'])),
                'centered_mean_change_from_parent': (value['centered_mean_cost'] - old['centered_mean_cost']) if value['boundary_count'] else None,
                'invariant_unit_ids': [p['common_unit_id'] for p, r in zip(paragraphs, records) if r['invariant']],
                'newly_invariant_unit_ids': [p['common_unit_id'] for p, r in zip(paragraphs, records) if r['newly_invariant_from_parent']],
                'invariant_units': sum(r['invariant'] for r in records),
                'varying_units': sum(not r['invariant'] for r in records),
                'units_with_multiple_orders': sum(r['possible_interior_orders'] > 1 for r in records),
                'units_with_reduced_order_freedom': sum(r['retained_order_fraction']['numerator'] != r['retained_order_fraction']['denominator'] for r in records),
                'possible_order_count_histogram': dict(sorted(Counter(str(r['possible_interior_orders']) for r in records).items(), key=lambda kv: int(kv[0]))),
                **{field: sum(r[field] for r in records) for field in ('nonzero_weight_possible_edges', 'joint_events_evaluated', 'zero_joint_events', 'positive_joint_events')}})
        aggregates.append({**{name: old[name] for name in ('source_id', 'uncertain_spaces')}, 'controls': controls})
    return {'cohort': corpus['cohort'], 'variants': aggregates, 'paragraphs': paragraphs}


def build(root=ROOT):
    for name, expected in PINS.items():
        if digest((root / name).read_bytes()) != expected:
            raise ValueError('pinned input changed: ' + name)
    parent = strict_json((root / PARENT).read_bytes())
    if encoded(parent) != encoded(parent_build(root)):
        raise ValueError('parent differs from complete pinned-source replay')
    corpus = corpus_build(root)
    if digest(encoded(corpus)) != parent['inputs']['canonical_corpus_sha256']:
        raise ValueError('canonical corpus changed')
    return {'schema_version': 1, 'producer_version': VERSION, 'sources': corpus['sources'],
        'inputs': {'parent_path': str(PARENT), 'parent_sha256': PINS[str(PARENT)],
                   'parent_inputs': parent['inputs'], 'plan_path': str(PLAN),
                   'plan_sha256': digest((root / PLAN).read_bytes()),
                   'pinned_dependency_sha256': PINS,
                   'implementation_sha256': {name: digest((root / 'scripts' / name).read_bytes())
                       for name in ('endpoint_length_control.py', 'stratified_path_moments.py')}},
        'method': {'controls': list(CONTROLS), 'distance': parent['method']['distance'],
                   'normalization': parent['method']['normalization'],
                   'control': 'uniform identity permutations within exact interior length strata; anchors and slot-label pattern fixed',
                   'moments': 'exact rational compatible-chain placement probabilities in the original slot pattern',
                   'comparison': 'reference-distribution differences; no paired random-variable variance',
                   'tail_or_decision_criterion': None}, **analyze(corpus, parent)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    reads = [ROOT / PLAN, *(ROOT / name for name in PINS), *([args.check] if args.check else [])]
    try:
        protect_outputs([args.output] if args.output else [], reads, root=ROOT)
        report = build(ROOT)
        if args.check and encoded(strict_json(args.check.read_bytes())) != encoded(report):
            raise ValueError('length-control report differs from complete typed replay')
        if args.output:
            raw = encoded(report)
            protect_outputs([args.output], reads, root=ROOT)
            args.output.write_bytes(raw)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'endpoint length control failed: {error}\n')
    print(f"Verified {report['cohort']['common_eligible_units']} original units under both fixed length controls.")


if __name__ == '__main__':
    main()
