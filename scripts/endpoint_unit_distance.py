"""Paired endpoint edit-distance sensitivity to accepted EVA segment policies."""

import argparse
from collections import Counter
from fractions import Fraction
from pathlib import Path

try:
    from .anchored_path_moments import weighted_moments
    from .audit_eva_token_coverage import encoded
    from .audit_transliterations import ROOT
    from .eva_unit_sensitivity import ordered_patterns, segment
    from .paragraph_endpoint_distance import build as parent_build, summary, rational
    from .paragraph_token_corpus import build as corpus_build, digest, protect_outputs, strict_json
except ImportError:
    from anchored_path_moments import weighted_moments
    from audit_eva_token_coverage import encoded
    from audit_transliterations import ROOT
    from eva_unit_sensitivity import ordered_patterns, segment
    from paragraph_endpoint_distance import build as parent_build, summary, rational
    from paragraph_token_corpus import build as corpus_build, digest, protect_outputs, strict_json


PLAN = Path('research/transliteration/ENDPOINT_UNIT_SENSITIVITY_PLAN.md')
PARENT = Path('research/transliteration/paragraph_endpoint_distance.json')
SETTINGS = Path('research/baselines/eva-unit-protocol.json')
VERSION = 'paired-anchored-endpoint-eva-unit-distance-v1'
PINS = {
    str(PARENT): '1d17ec6362d9ec203c7e4d9218b3713cc03a1036b10a362f86c6814647e63818',
    str(SETTINGS): 'a2ded6526829759169d9462708ea00f969ebe47127acf5c90e2f0b1e7e2fc3ec',
    'scripts/paragraph_endpoint_distance.py': '783420f1dd49cc29c992d7c09994d9f176bbe221660b063584cb95260b3346fe',
    'scripts/anchored_path_moments.py': '6b366d33f7d606ee5a5d3ae32d1519973547256c22a5f2b73842fc33d9b3633a',
    'scripts/eva_unit_sensitivity.py': '4a780a8c2d26380951c34bd219d27bd9995ab8c451617dbc68c3bb8feddff4f8',
}
POLICY_IDS = ('ascii_letters', 'bench_sequences', 'bench_and_minim_sequences')
BENCH = ('ch', 'Ch', 'sh', 'Sh', 'cth', 'cTh', 'ckh', 'cKh', 'cph', 'cPh', 'cfh', 'cFh')
MINIM = tuple(prefix + ending for ending in 'nlrm' for prefix in ('i', 'ii', 'iii'))
EXAMPLES = ('cTHh', 'cthh', 'ITh', 'ith', 'Ao', 'Yk', 'Ee', 'Oy', 'Qo')


def policies(settings):
    records = settings['policies']
    if tuple(p['id'] for p in records) != POLICY_IDS:
        raise ValueError('exactly the three accepted unit policies required')
    patterns = [ordered_patterns(p['patterns']) for p in records]
    if patterns != [(), ordered_patterns(list(BENCH)), ordered_patterns(list(BENCH + MINIM))]:
        raise ValueError('accepted finite unit maps changed')
    if tuple(settings['fallback_examples_not_grouped']) != EXAMPLES:
        raise ValueError('accepted fallback-example audit changed')
    return patterns


def sequence_distance(left, right):
    """Normalized unit-cost Levenshtein distance over literal segment labels."""
    if any(not isinstance(x, (list, tuple)) or any(not isinstance(s, str) or not s for s in x)
           for x in (left, right)):
        raise ValueError('edit inputs must be sequences of nonempty segment labels')
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (a != b)))
        previous = current
    denominator = max(len(left), len(right))
    return Fraction(previous[-1], denominator) if denominator else Fraction()


def matrix(endpoints):
    return [[None if a == b else sequence_distance(endpoints[a][1], endpoints[b][0])
             for b in range(len(endpoints))] for a in range(len(endpoints))]


def difference(grouped, ascii_weights):
    return [[None if a == b else grouped[a][b] - ascii_weights[a][b]
             for b in range(len(grouped))] for a in range(len(grouped))]


def record_moments(weights):
    result = weighted_moments(weights)
    return {
        **summary(result['observed'], result['mean'], result['variance'], len(weights) - 1),
        'diagonal_variance': rational(result['diagonal_variance']),
        'twice_covariance_sum': rational(result['twice_covariance']),
        **{key: result[key] for key in ('nonzero_weight_possible_edges', 'joint_events_evaluated',
                                      'zero_joint_events', 'positive_joint_events',
                                      'possible_interior_orders', 'invariant')},
    }


def as_fraction(value):
    return Fraction(value['numerator'], value['denominator'])


def aggregate(records, units):
    observed = sum((as_fraction(r['observed_cost_sum']) for r in records), Fraction())
    mean = sum((as_fraction(r['conditional_mean_cost_sum']) for r in records), Fraction())
    variance = sum((as_fraction(r['conditional_variance_cost_sum']) for r in records), Fraction())
    invariant = [unit['common_unit_id'] for unit, r in zip(units, records) if r['invariant']]
    return {
        **summary(observed, mean, variance, sum(r['boundary_count'] for r in records)),
        'diagonal_variance': rational(sum((as_fraction(r['diagonal_variance']) for r in records), Fraction())),
        'twice_covariance_sum': rational(sum((as_fraction(r['twice_covariance_sum']) for r in records), Fraction())),
        'invariant_paragraphs': len(invariant), 'varying_paragraphs': len(units) - len(invariant),
        'invariant_unit_ids': invariant,
        **{key: sum(r[key] for r in records) for key in ('nonzero_weight_possible_edges',
                    'joint_events_evaluated', 'zero_joint_events', 'positive_joint_events')},
    }


def scope_audit(native_roles, patterns, endpoints):
    pieces = [segment(token, patterns) for token in native_roles]
    hits = Counter({p: 0 for p in patterns})
    uppercase = Counter()
    examples = Counter({p: 0 for p in EXAMPLES})
    for token, row in zip(native_roles, pieces):
        hits.update(p for p in row if len(p) > 1)
        uppercase.update(p for p in row if len(p) == 1 and p.isupper())
        examples.update({p: token.count(p) for p in EXAMPLES})
    return {
        'scope': 'original consecutive-boundary endpoint roles; repeated roles counted separately',
        'endpoint_roles': len(pieces), 'native_ascii_letters': sum(map(len, native_roles)),
        'emitted_segments': sum(map(len, pieces)), 'pattern_hits': dict(sorted(hits.items())),
        'uppercase_single_letter_fallback_counts': dict(sorted(uppercase.items())),
        'unlisted_example_substring_counts': dict(sorted(examples.items())),
        'ordered_all_locus_endpoint_segments_sha256': digest(encoded(endpoints)),
    }


def analyze(corpus, parent, settings, progress=None):
    matches = policies(settings)
    common = [p for p in corpus['paragraphs'] if p['common_eligible']]
    if any(not r['tokens'] for p in common for v in p['variants'] for r in v['loci']):
        raise ValueError('empty endpoint; original cohort cannot be silently filtered')
    if encoded(corpus['cohort']) != encoded(parent['cohort']):
        raise ValueError('parent cohort changed')
    if [p['common_unit_id'] for p in common] != [p['common_unit_id'] for p in parent['paragraphs']]:
        raise ValueError('parent ordered common unit identities changed')
    paragraphs = []
    for pi, (unit, original) in enumerate(zip(common, parent['paragraphs'])):
        identity = {key: unit[key] for key in ('common_unit_id', 'page_id', 'member_keys', 'source_unit_ids')}
        if encoded(identity) != encoded({key: original[key] for key in identity}):
            raise ValueError('parent ordered members or source unit identities changed')
        variants = []
        if len(unit['variants']) != len(original['variants']):
            raise ValueError('parent variant count changed')
        for native, old in zip(unit['variants'], original['variants']):
            key = {name: native[name] for name in ('source_id', 'uncertain_spaces')}
            if encoded(key) != encoded({name: old[name] for name in key}):
                raise ValueError('parent source/spacing order changed')
            rows = native['loci']
            endpoints = [[[segment(r['tokens'][0], ps), segment(r['tokens'][-1], ps)]
                          for r in rows] for ps in matches]
            weights = [matrix(e) for e in endpoints]
            costs = [record_moments(w) for w in weights]
            if encoded([[rational(w) if w is not None else None for w in row] for row in weights[0]]) != encoded(old['cost_matrix']):
                raise ValueError('ASCII cost matrix does not reproduce the complete parent')
            if encoded(costs[0]) != encoded({field: old[field] for field in costs[0]}):
                raise ValueError('ASCII moments do not reproduce the complete parent')
            variants.append({**key,
                'policies': [{'policy_id': ident, **result,
                    **({'cost_matrix': [[rational(w) if w is not None else None for w in row] for row in weights[i]]}
                       if i else {}),
                    'initial_terminal_segment_counts': [[len(a), len(b)] for a, b in endpoints[i]]}
                    for i, (ident, result) in enumerate(zip(POLICY_IDS, costs))],
                'paired_changes': [{'policy_id': POLICY_IDS[i],
                                    **record_moments(difference(weights[i], weights[0]))} for i in (1, 2)]})
        paragraphs.append({**identity, 'variants': variants})
        if progress and (pi + 1) % 50 == 0:
            progress(f'Grouped and paired moments: {pi + 1}/{len(common)} units')
    variants = []
    for vi, old in enumerate(parent['variants']):
        grouped = []
        roles = [token for unit in common for left, right in zip(unit['variants'][vi]['loci'],
                                                               unit['variants'][vi]['loci'][1:])
                 for token in (left['tokens'][-1], right['tokens'][0])]
        for ui, ident in enumerate(POLICY_IDS):
            records = [p['variants'][vi]['policies'][ui] for p in paragraphs]
            value = aggregate(records, paragraphs)
            if ui == 0 and encoded({key: value[key] for key in old if key not in ('source_id', 'uncertain_spaces')}) != encoded(
                    {key: old[key] for key in old if key not in ('source_id', 'uncertain_spaces')}):
                raise ValueError('ASCII aggregate does not reproduce the parent')
            all_endpoints = [[[segment(r['tokens'][0], matches[ui]), segment(r['tokens'][-1], matches[ui])]
                              for r in unit['variants'][vi]['loci']] for unit in common]
            ascii_records = [p['variants'][vi]['policies'][0] for p in paragraphs]
            grouped.append({'policy_id': ident, **value,
                'newly_invariant_from_ascii': [p['common_unit_id'] for p, a, r in zip(paragraphs, ascii_records, records)
                                               if r['invariant'] and not a['invariant']],
                'newly_varying_from_ascii': [p['common_unit_id'] for p, a, r in zip(paragraphs, ascii_records, records)
                                             if not r['invariant'] and a['invariant']],
                'scope_audit': scope_audit(roles, matches[ui], all_endpoints)})
        variants.append({**{key: old[key] for key in ('source_id', 'uncertain_spaces')}, 'policies': grouped,
            'paired_changes': [{'policy_id': POLICY_IDS[i + 1],
                **aggregate([p['variants'][vi]['paired_changes'][i] for p in paragraphs], paragraphs)} for i in (0, 1)]})
    return {'cohort': corpus['cohort'], 'variants': variants, 'paragraphs': paragraphs}


def build(root=ROOT, progress=None):
    for name, expected in PINS.items():
        path = Path(__file__).parent / Path(name).name if name.startswith('scripts/') else root / name
        if digest(path.read_bytes()) != expected:
            raise ValueError(f'pinned input changed: {name}')
    raw_parent = (root / PARENT).read_bytes()
    parent = strict_json(raw_parent)
    if encoded(parent) != encoded(parent_build(root)):
        raise ValueError('parent differs from complete pinned-source replay')
    corpus = corpus_build(root)
    if digest(encoded(corpus)) != parent['inputs']['canonical_corpus_sha256']:
        raise ValueError('parent canonical corpus changed')
    settings = strict_json((root / SETTINGS).read_bytes())
    return {
        'schema_version': 1, 'producer_version': VERSION,
        'analysis_status': 'post-result exploratory representation sensitivity',
        'sources': corpus['sources'],
        'inputs': {'pinned_dependencies': PINS, 'parent_inputs': parent['inputs'],
                   'plan_path': str(PLAN), 'plan_sha256': digest((root / PLAN).read_bytes()),
                   'implementation_sha256': digest(Path(__file__).read_bytes())},
        'method': {'policies': settings['policies'], 'segmentation': settings['segmentation'],
                   'distance': 'unit-cost Levenshtein over exact native segment labels',
                   'normalization': 'divide by maximum endpoint segment count',
                   'control': parent['method']['control'],
                   'paired_change': 'grouped minus ASCII weights on identical allowed identity orders',
                   'probability_matrices': 'complete pinned parent; unchanged identity distribution',
                   'tail_or_decision_criterion': None},
        **analyze(corpus, parent, settings, progress),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    inputs = [ROOT / PLAN, ROOT / PARENT, ROOT / SETTINGS,
              ROOT / 'research/transliteration/ENDPOINT_EDIT_DISTANCE_PLAN.md',
              ROOT / 'research/transliteration/paragraph_corpus_coverage.json',
              *([args.check] if args.check else [])]
    try:
        protect_outputs([args.output] if args.output else [], inputs, root=ROOT)
        report = build(root=ROOT, progress=print)
        if args.check and encoded(strict_json(args.check.read_bytes())) != encoded(report):
            raise ValueError('unit-distance report differs from complete pinned producer replay')
        if args.output:
            raw = encoded(report)
            protect_outputs([args.output], inputs, root=ROOT)
            args.output.write_bytes(raw)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'endpoint unit distance failed: {error}\n')
    print(f"Verified {report['cohort']['common_eligible_units']} units under all three fixed representations.")


if __name__ == '__main__':
    main()
