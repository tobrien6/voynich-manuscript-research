from contextlib import redirect_stderr
import io
from itertools import combinations, product
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.audit_historical_record_order import optimal_pairs, compare_orders, main, READS, build, ROOT
from scripts.audit_historical_record_projections import compare_records, projection_records


def enumerated_alignments(left, right):
    """Independent exhaustive index-subsequence oracle, without DP tables."""
    for size in range(min(len(left), len(right)), -1, -1):
        alignments = []
        for a in combinations(range(len(left)), size):
            for b in combinations(range(len(right)), size):
                if tuple(left[i] for i in a) == tuple(right[j] for j in b):
                    alignments.append(tuple(zip(a, b)))
        if alignments:
            return size, alignments


def records(bodies, historical, page):
    if historical:
        return [SimpleNamespace(page=page, unit='P', body=b, transcriber='H',
                locator=f'{page}.P.{i};H', physical_line=10+i) for i, b in enumerate(bodies)]
    return [SimpleNamespace(page=page, text=b, kind='P0', transcriber=None, present=True,
            identifier=f'{page}.{i},+P0', line_number=20+i) for i, b in enumerate(bodies)]


def fixture(root):
    paths = [*(root / p for p in READS), root / 'data/transliterations.json',
             root / 'data/historical/catalog.json', root / 'data/historical/native.zip',
             root / 'data/raw/native.txt', root / 'scripts/audit_historical_record_order.py',
             root / 'scripts/paragraph_token_corpus.py']
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('public synthetic fixture')
    (root / 'data/transliterations.json').write_text('{"sources":[{"path":"data/raw/native.txt"}]}')
    return paths


class OrderMathTests(unittest.TestCase):
    def test_exhaustive_all_optimal_index_pairs_and_mandatory_intersection(self):
        sequences = [s for n in range(5) for s in product('ab', repeat=n)]
        for left in sequences:
            for right in sequences:
                expected_length, alignments = enumerated_alignments(left, right)
                result = optimal_pairs(left, right)
                union = set().union(*(set(a) for a in alignments))
                intersection = set(alignments[0]).intersection(*(set(a) for a in alignments[1:]))
                actual = {(p['historical_nonempty_index'], p['modern_nonempty_index'])
                          for p in result['candidate_pairs']}
                mandatory = {(p['historical_nonempty_index'], p['modern_nonempty_index'])
                             for p in result['candidate_pairs'] if p['mandatory_in_every_maximum_pairing']}
                self.assertEqual(result['maximum_order_preserving_pairs'], expected_length)
                self.assertEqual(actual, union)
                self.assertEqual(mandatory, intersection)
                self.assertEqual(result['maximum_pairing_unique'], len(alignments) == 1)
                self.assertEqual(result['minimum_total_unmatched_records'], len(left)+len(right)-2*expected_length)
                counts = [0] * expected_length
                for p in result['candidate_pairs']:
                    pair = (p['historical_nonempty_index'], p['modern_nonempty_index'])
                    ranks = {a.index(pair)+1 for a in alignments if pair in a}
                    self.assertEqual(ranks, {p['matched_rank_one_based']})
                    counts[p['matched_rank_one_based']-1] += 1
                self.assertEqual(result['rank_candidate_counts'], counts)

    def test_duplicates_remain_ambiguous_and_common_prefix_can_be_mandatory(self):
        result = optimal_pairs(['a', 'b', 'a'], ['a', 'a', 'b'])
        self.assertEqual(result['maximum_order_preserving_pairs'], 2)
        self.assertEqual(result['rank_candidate_counts'], [2, 2])
        self.assertEqual(result['mandatory_pair_count'], 0)
        result = optimal_pairs(['a', 'b', 'c'], ['a', 'c', 'b'])
        self.assertEqual(result['mandatory_pair_count'], 1)
        self.assertEqual(result['candidate_pairs'][0], {'historical_nonempty_index': 0,
            'modern_nonempty_index': 0, 'matched_rank_one_based': 1,
            'mandatory_in_every_maximum_pairing': True})

    def test_invalid_sequence_elements_rejected(self):
        for values in [[''], [1], [True], [None]]:
            with self.assertRaises(ValueError):
                optimal_pairs(values, ['a'])

    def test_complete_cohort_controls_empty_descriptors_and_exclusions(self):
        old = records(['a', '%%%!', 'b'], True, 'f1r') + records(['a', 'a'], True, 'f2r') + records(['c'], True, 'f3r')
        modern = SimpleNamespace(loci=records(['b', '???', 'a'], False, 'f1r') + records(['a', 'a'], False, 'f2r') + records(['d'], False, 'f3r'))
        parent = compare_records(old, modern)
        a = projection_records(old, True); b = projection_records(modern.loci, False)
        result = compare_orders(a, b, parent)
        self.assertEqual(result['summary']['selected_equal_multiset_pages'], 2)
        self.assertEqual([p['page_id'] for p in result['order_different_pages']], ['f1r'])
        row = result['order_different_pages'][0]
        self.assertEqual(row['minimum_unmatched_historical_records'], 1)
        self.assertEqual(row['historical_empty_projection_records'][0]['source_order_index_zero_based_on_page'], 1)
        self.assertEqual([r['source_order_index_zero_based_on_page'] for r in row['historical_nonempty_records_in_source_order']], [0, 2])
        self.assertEqual(result['equal_order_controls'][0]['page_id'], 'f2r')
        self.assertTrue(result['equal_order_controls'][0]['only_identity_index_pairs'])
        self.assertEqual(result['excluded_pages'][0]['page_id'], 'f3r')
        with self.assertRaisesRegex(ValueError, 'multiset'):
            compare_orders(a, {**b, 'f1r': [('x', {})]}, parent)
        broken = {**parent, 'summary': {**parent['summary'], 'equal_bag_different_record_order_page_ids': []}}
        with self.assertRaisesRegex(ValueError, 'selection'):
            compare_orders(a, b, broken)


class OrderWriterTests(unittest.TestCase):
    def test_direct_symlink_hardlink_protected_inputs_and_check_target(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/'repo'; paths = fixture(root)
            check = Path(d)/'check.json'; check.write_text('{"x":1}'); paths.append(check)
            loaded = ([], None, {}, set(paths))
            for target in paths:
                before = target.read_bytes()
                for kind in ('direct', 'symlink', 'hardlink'):
                    output = target if kind == 'direct' else Path(d)/('alias-'+kind)
                    if kind != 'direct':
                        output.unlink(missing_ok=True)
                        output.symlink_to(target) if kind == 'symlink' else os.link(target, output)
                    with self.subTest(target=target.name, kind=kind), \
                            patch('scripts.audit_historical_record_order.ROOT', root), \
                            patch('scripts.paragraph_token_corpus.__file__', str(root/'scripts/paragraph_token_corpus.py')), \
                            patch('scripts.audit_historical_record_order.load_inputs', return_value=loaded), \
                            patch('scripts.audit_historical_record_order.build', side_effect=AssertionError('must not compute')) as producer, \
                            patch('sys.argv', ['audit', '--output', str(output), '--check', str(check)]), \
                            redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                        main()
                    producer.assert_not_called(); self.assertEqual(target.read_bytes(), before)

    def test_typed_and_duplicate_key_check_failures_preserve_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'repo'; paths=fixture(root); loaded=([], None, {}, set(paths))
            check=Path(d)/'check.json'; output=Path(d)/'output.json'
            for text in ['{"count":true}', '{"count":1.0}', '{"count":1,"count":1}', '{"count":NaN}']:
                check.write_text(text); output.write_bytes(b'preserved')
                with patch('scripts.audit_historical_record_order.ROOT', root), \
                        patch('scripts.audit_historical_record_order.load_inputs', return_value=loaded), \
                        patch('scripts.audit_historical_record_order.build', return_value={'count':1}), \
                        patch('sys.argv', ['audit', '--check', str(check), '--output', str(output)]), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    main()
                self.assertEqual(output.read_bytes(), b'preserved')

    def test_alias_introduced_during_computation_or_serialization(self):
        for stage in ('calculation', 'serialization'):
            for kind in ('symlink', 'hardlink'):
                with self.subTest(stage=stage,kind=kind), tempfile.TemporaryDirectory() as d:
                    root=Path(d)/'repo'; paths=fixture(root); loaded=([], None, {}, set(paths))
                    target=root/'data/raw/native.txt'; before=target.read_bytes(); output=Path(d)/'out.json'
                    def introduce():
                        output.symlink_to(target) if kind=='symlink' else os.link(target,output)
                    def calculate(*args):
                        if stage=='calculation': introduce()
                        return {'summary':{'selected_equal_multiset_pages':0}}
                    def serialize(value):
                        raw=encoded(value)
                        if stage=='serialization': introduce()
                        return raw
                    with patch('scripts.audit_historical_record_order.ROOT',root), \
                            patch('scripts.audit_historical_record_order.load_inputs',return_value=loaded), \
                            patch('scripts.audit_historical_record_order.build',side_effect=calculate), \
                            patch('scripts.audit_historical_record_order.encoded',side_effect=serialize), \
                            patch('sys.argv',['audit','--output',str(output)]), \
                            redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                        main()
                    self.assertEqual(target.read_bytes(),before)


class OrderNativeTests(unittest.TestCase):
    def test_complete_native_report_replays_byte_for_byte(self):
        result = build()
        self.assertEqual(result['summary']['selected_equal_multiset_pages'], 211)
        self.assertEqual(result['summary']['order_different_pages'], 29)
        self.assertFalse(result['usable_as_verified_locus_crosswalk'])
        self.assertFalse(result['usable_for_statistical_evaluation'])
        self.assertEqual(encoded(result), (ROOT/'research/historical/record-order.json').read_bytes())

    def test_changed_accepted_parent_identity_fails(self):
        with patch('scripts.audit_historical_record_order.PARENT_SHA256', '0'*64):
            with self.assertRaisesRegex(ValueError, 'parent report bytes changed'):
                build()


if __name__ == '__main__':
    unittest.main()
