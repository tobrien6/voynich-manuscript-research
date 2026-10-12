"""Retain all optimal lossy-record order matches without choosing a crosswalk."""

import argparse
from collections import Counter
from pathlib import Path
import zipfile

try:
    from .audit_historical_record_projections import (
        HELPERS, build as parent_build, digest, load_inputs, projection_records)
    from .audit_eva_token_coverage import encoded, load_json
    from .paragraph_token_corpus import protect_outputs
except ImportError:
    from audit_historical_record_projections import (
        HELPERS, build as parent_build, digest, load_inputs, projection_records)
    from audit_eva_token_coverage import encoded, load_json
    from paragraph_token_corpus import protect_outputs

ROOT = Path(__file__).resolve().parents[1]
PARENT = Path('research/historical/record-projections.json')
PARENT_SHA256 = '161734c02648c5dfa0bf09dc91ed26bf8c3113a378317ef870f13d66c9dcb6e9'
PLAN = Path('research/historical/RECORD_ORDER_PLAN.md')
READS = (PARENT, PLAN, Path('research/historical/lowercase-projection.json'),
         Path('research/historical/RECORD_PROJECTION_PLAN.md'))
IMPLEMENTATIONS = (*HELPERS, 'audit_historical_record_order.py', 'paragraph_token_corpus.py')


def optimal_pairs(left, right):
    """Exact LCS size and union/intersection of optimal index-pair alignments.

    A possible pair has a fixed matched rank: its maximal prefix length plus 1.
    Every optimal alignment uses one pair at each rank, so a rank's sole
    candidate is precisely a pair shared by all optimal alignments.
    """
    if any(type(s) is not str or not s for s in (*left, *right)):
        raise ValueError('sequence elements must be nonempty exact strings')
    n, m = len(left), len(right)
    prefix = [[0] * (m + 1) for _ in range(n + 1)]
    suffix = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            prefix[i + 1][j + 1] = max(prefix[i][j + 1], prefix[i + 1][j],
                                      prefix[i][j] + (left[i] == right[j]))
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            suffix[i][j] = max(suffix[i + 1][j], suffix[i][j + 1],
                               suffix[i + 1][j + 1] + (left[i] == right[j]))
    length = prefix[n][m]
    pairs = []
    for i in range(n):
        for j in range(m):
            if left[i] == right[j] and prefix[i][j] + 1 + suffix[i + 1][j + 1] == length:
                pairs.append({'historical_nonempty_index': i, 'modern_nonempty_index': j,
                              'matched_rank_one_based': prefix[i][j] + 1})
    ranks = Counter(p['matched_rank_one_based'] for p in pairs)
    if sorted(ranks) != list(range(1, length + 1)):
        raise ValueError('optimal pair ranks do not cover the LCS')
    for pair in pairs:
        pair['mandatory_in_every_maximum_pairing'] = ranks[pair['matched_rank_one_based']] == 1
    return {'maximum_order_preserving_pairs': length,
            'minimum_unmatched_historical_records': n - length,
            'minimum_unmatched_modern_records': m - length,
            'minimum_total_unmatched_records': n + m - 2 * length,
            'candidate_pairs': pairs,
            'rank_candidate_counts': [ranks[r] for r in range(1, length + 1)],
            'mandatory_pair_count': sum(p['mandatory_in_every_maximum_pairing'] for p in pairs),
            'maximum_pairing_unique': all(count == 1 for count in ranks.values())}


def descriptors(rows):
    return [{**descriptor, 'nonempty_sequence_index': index,
             'projection_sha256': digest(stream.encode('ascii')),
             'projected_lowercase_symbols': len(stream)}
            for index, (stream, descriptor) in enumerate((s, d) for s, d in rows if s)]


def compare_orders(old, new, parent):
    """Select the complete parent cohort; retain controls and exclusions."""
    detailed, controls, excluded = [], [], []
    for page in parent['page_profiles']:
        page_id = page['page_id']
        if page['nonempty_record_projection_bags_equal'] is not True:
            excluded.append({k: page[k] for k in ('page_id', 'status',
                'nonempty_record_projection_bags_equal', 'nonempty_record_projection_order_equal')})
            continue
        a = [s for s, _ in old[page_id] if s]
        b = [s for s, _ in new[page_id] if s]
        if not a or Counter(a) != Counter(b):
            raise ValueError('selected page differs from the parent equal-multiset cohort')
        if (a == b) is not page['nonempty_record_projection_order_equal']:
            raise ValueError('selected page differs from the parent order flag')
        result = optimal_pairs(a, b)
        common = {'page_id': page_id, 'nonempty_records_per_source': len(a),
                  'historical_empty_projection_records': page['historical_H']['empty_projection_records'],
                  'modern_empty_projection_records': page['modern_IT2a_present']['empty_projection_records']}
        if a == b:
            expected = [(i, i) for i in range(len(a))]
            actual = [(p['historical_nonempty_index'], p['modern_nonempty_index'])
                      for p in result['candidate_pairs']]
            if actual != expected or result['maximum_order_preserving_pairs'] != len(a):
                raise ValueError('equal-order control is not a complete identity pairing')
            controls.append({**common, 'maximum_order_preserving_pairs': len(a),
                             'minimum_unmatched_records_per_source': 0,
                             'only_identity_index_pairs': True})
        else:
            detailed.append({**common, **result,
                             'historical_nonempty_records_in_source_order': descriptors(old[page_id]),
                             'modern_nonempty_records_in_source_order': descriptors(new[page_id])})
    if [p['page_id'] for p in detailed] != parent['summary']['equal_bag_different_record_order_page_ids']:
        raise ValueError('detailed page selection differs from the complete parent list')
    if [p['page_id'] for p in controls] != parent['summary']['equal_nonempty_record_order_page_ids']:
        raise ValueError('identity control selection differs from the complete parent list')
    total_n = sum(p['nonempty_records_per_source'] for p in detailed)
    total_l = sum(p['maximum_order_preserving_pairs'] for p in detailed)
    return {'summary': {
                'selected_equal_multiset_pages': len(detailed) + len(controls),
                'equal_order_control_pages': len(controls), 'order_different_pages': len(detailed),
                'excluded_union_pages': len(excluded),
                'order_different_nonempty_records_per_source': total_n,
                'order_different_maximum_order_preserving_pairs': total_l,
                'order_different_minimum_unmatched_records_per_source': total_n - total_l,
                'order_different_minimum_total_unmatched_records': 2 * (total_n - total_l),
                'order_different_pages_with_unique_maximum_pairing': sum(p['maximum_pairing_unique'] for p in detailed),
                'order_different_candidate_pairs': sum(len(p['candidate_pairs']) for p in detailed),
                'order_different_mandatory_pairs': sum(p['mandatory_pair_count'] for p in detailed)},
            'order_different_pages': detailed, 'equal_order_controls': controls,
            'excluded_pages': excluded}


def build(root=ROOT, loaded=None):
    loaded = loaded or load_inputs(root)
    historical, modern, pins, _ = loaded
    raw = (root / PARENT).read_bytes()
    if digest(raw) != PARENT_SHA256:
        raise ValueError('accepted parent report bytes changed')
    parent = load_json(raw)
    if encoded(parent) != encoded(parent_build(root, loaded)):
        raise ValueError('parent report differs from complete source reconstruction')
    old = projection_records(historical, True)
    new = projection_records(modern.loci, False)
    return {'schema_version': 1, 'method': 'exploratory-native-projected-record-order-lcs-v1',
            'usable_as_verified_locus_crosswalk': False, 'usable_for_statistical_evaluation': False,
            'inputs': {'sources': pins, 'parent_report': {'path': str(PARENT), 'sha256': digest(raw)},
                      'plan': {'path': str(PLAN), 'sha256': digest((root / PLAN).read_bytes())},
                      'implementation_sha256': {'scripts/' + name: digest((root / 'scripts' / name).read_bytes())
                                                for name in IMPLEMENTATIONS}},
            'rules': {'equality': 'exact nonempty source-specific lowercase projected strings before hashing',
                      'order': 'original native source order within exact page ID; no page aliases',
                      'pair_inventory': 'all index pairs on any maximum order-preserving pairing; no selected witness',
                      'mandatory': 'sole possible index pair at its matched rank; conditional combinatorial status only',
                      'unmatched': 'minimum unmatched records per edition; not physical deletions or source errors',
                      'empty_projection': 'descriptors retained separately; never matching evidence',
                      'duplicate_projection': 'observationally indistinguishable; all optimal index candidates retained'},
            'modern_nonexistent_loci_excluded': parent['modern_nonexistent_loci_excluded'],
            **compare_orders(old, new, parent)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        loaded = load_inputs(ROOT)
        reads = [*loaded[3], *(ROOT / p for p in READS)]
        if args.check:
            reads.append(args.check)
        protect_outputs([args.output] if args.output else [], reads, root=ROOT)
        result = build(ROOT, loaded)
        if args.check and encoded(load_json(args.check.read_bytes())) != encoded(result):
            raise ValueError('record-order report differs from complete typed replay')
        if args.output:
            serialized = encoded(result)
            protect_outputs([args.output], reads, root=ROOT)
            args.output.write_bytes(serialized)
        elif not args.check:
            print(encoded(result).decode(), end='')
    except (ValueError, KeyError, OSError, UnicodeError, zipfile.BadZipFile) as error:
        parser.exit(1, f'record order audit failed: {error}\n')
    if args.check or args.output:
        print(f"Verified {result['summary']['selected_equal_multiset_pages']} equal-multiset pages; no locus crosswalk created.")


if __name__ == '__main__':
    main()
