from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from itertools import combinations, product
import io
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_historical_pairing_counts as audit
from scripts.audit_eva_token_coverage import encoded


def alignments(left,right):
    for size in range(min(len(left),len(right)),-1,-1):
        paths=[tuple(zip(a,b)) for a in combinations(range(len(left)),size)
               for b in combinations(range(len(right)),size)
               if tuple(left[i] for i in a)==tuple(right[j] for j in b)]
        if paths:return size,paths


def fixture(root):
    paths=[*(root/p for p in audit.READS),root/'data/transliterations.json',
           root/'data/raw/native.txt',root/'scripts/audit_historical_pairing_counts.py']
    for path in paths:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text('public synthetic fixture')
    (root/'data/transliterations.json').write_text('{"sources":[{"path":"data/raw/native.txt"}]}')
    return paths


class PairingCountMathTests(unittest.TestCase):
    def test_exhaustive_counts_and_every_through_pair_against_complete_alignment_lists(self):
        sequences=[s for n in range(5) for s in product('ab',repeat=n)]
        for left in sequences:
            for right in sequences:
                length,paths=alignments(left,right)
                result=audit.count_pairings(left,right)
                expected=Counter(pair for path in paths for pair in path)
                actual={(p['historical_nonempty_index'],p['modern_nonempty_index']):p['maximum_pairings_through_pair'] for p in result['candidate_pairs']}
                self.assertEqual(result['maximum_order_preserving_pairs'],length)
                self.assertEqual(result['maximum_pairing_count'],len(paths))
                self.assertEqual(actual,expected)
                self.assertEqual(result['rank_pairing_count_sums'],[len(paths)]*length)
                for p in result['candidate_pairs']:
                    pair=(p['historical_nonempty_index'],p['modern_nonempty_index'])
                    self.assertEqual({path.index(pair)+1 for path in paths if pair in path},{p['matched_rank_one_based']})
                    self.assertEqual(p['mandatory_in_every_maximum_pairing'],all(pair in path for path in paths))

    def test_uniform_alignment_counting_does_not_give_each_rank_candidate_equal_weight(self):
        result=audit.count_pairings(('a','b','a'),('a','a','b'))
        self.assertEqual(result['maximum_pairing_count'],3)
        self.assertEqual([p['maximum_pairings_through_pair'] for p in result['candidate_pairs']],[2,1,2,1])
        self.assertFalse(any(p['mandatory_in_every_maximum_pairing'] for p in result['candidate_pairs']))

    def test_large_counts_are_exact_integers_and_empty_optimum_is_one_pairing(self):
        result=audit.count_pairings(['a']*60,['a']*30)
        self.assertEqual(result['maximum_pairing_count'],math.comb(60,30))
        self.assertGreater(result['maximum_pairing_count'],2**53)
        self.assertTrue(all(type(v) is int for v in result['rank_pairing_count_sums']))
        for left,right in (([],[]),(['a'],[]),(['a'],['b'])):
            result=audit.count_pairings(left,right)
            self.assertEqual(result['maximum_pairing_count'],1)
            self.assertEqual(result['candidate_pairs'],[])

    def test_invalid_projection_elements_are_rejected(self):
        for left in ([''],[True],[1],[None]):
            with self.assertRaises(ValueError):audit.count_pairings(left,['a'])


class PairingCountWriterTests(unittest.TestCase):
    def invoke(self,root,paths,argv,result,serializer=None):
        with patch.object(audit,'ROOT',root),patch.object(audit,'load_inputs',return_value=([],None,{},set(paths))), \
                patch.object(audit,'build',side_effect=result if callable(result) else None,return_value=result), \
                patch.object(audit,'encoded',side_effect=serializer or encoded), \
                patch('sys.argv',['audit',*argv]),redirect_stderr(io.StringIO()),redirect_stdout(io.StringIO()):
            audit.main()

    def test_existing_direct_symlink_hardlink_and_check_aliases_preserve_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'repo';paths=fixture(root)
            check=Path(d)/'check.json';check.write_text('{"summary":{"selected_equal_multiset_pages":0}}');paths.append(check)
            for target in paths:
                before=target.read_bytes()
                for kind in ('direct','symlink','hardlink'):
                    output=target if kind=='direct' else Path(d)/('alias-'+kind)
                    if kind!='direct':
                        output.unlink(missing_ok=True)
                        output.symlink_to(target) if kind=='symlink' else os.link(target,output)
                    with self.subTest(target=target.name,kind=kind),self.assertRaises(SystemExit):
                        self.invoke(root,paths,['--output',str(output),'--check',str(check)],lambda *a:(_ for _ in ()).throw(AssertionError('must not compute')))
                    self.assertEqual(target.read_bytes(),before)

    def test_late_aliases_from_calculation_and_serialization_cannot_modify_input(self):
        for stage in ('calculation','serialization'):
            for kind in ('symlink','hardlink'):
                with self.subTest(stage=stage,kind=kind),tempfile.TemporaryDirectory() as d:
                    root=Path(d)/'repo';paths=fixture(root);target=root/'data/raw/native.txt';before=target.read_bytes();output=Path(d)/'new.json'
                    def install():
                        output.symlink_to(target) if kind=='symlink' else os.link(target,output)
                    def calculate(*args):
                        if stage=='calculation':install()
                        return {'summary':{'selected_equal_multiset_pages':0}}
                    def serialize(value):
                        raw=encoded(value)
                        if stage=='serialization':install()
                        return raw
                    with self.assertRaises(SystemExit):self.invoke(root,paths,['--output',str(output)],calculate,serialize)
                    self.assertEqual(target.read_bytes(),before)

    def test_typed_duplicate_key_and_nonfinite_failures_preserve_cache_and_do_not_create_output(self):
        result={'summary':{'selected_equal_multiset_pages':0},'maximum_pairing_count':'3'}
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'repo';paths=fixture(root);check=Path(d)/'check.json';output=Path(d)/'new.json'
            for bad in ({**result,'maximum_pairing_count':3},{**result,'maximum_pairing_count':3.0},
                        {'summary':{'selected_equal_multiset_pages':False},'maximum_pairing_count':'3'}):
                raw=encoded(bad);check.write_bytes(raw)
                with self.assertRaises(SystemExit):self.invoke(root,paths,['--check',str(check),'--output',str(output)],result)
                self.assertEqual(check.read_bytes(),raw);self.assertFalse(output.exists())
            for raw in (b'{"x":1,"x":1}',b'{"x":NaN}'):
                check.write_bytes(raw)
                with self.assertRaises(SystemExit):self.invoke(root,paths,['--check',str(check),'--output',str(output)],result)
                self.assertEqual(check.read_bytes(),raw);self.assertFalse(output.exists())
            check.write_bytes(encoded(result));self.invoke(root,paths,['--check',str(check),'--output',str(output)],result)
            self.assertEqual(output.read_bytes(),encoded(result))
            before=output.read_bytes()
            with self.assertRaises(SystemExit):self.invoke(root,paths,['--output',str(output)],result)
            self.assertEqual(output.read_bytes(),before)


class PairingCountNativeTests(unittest.TestCase):
    def test_complete_native_report_replays_with_all_parent_candidates_retained(self):
        result=audit.build()
        self.assertEqual(encoded(result),(audit.ROOT/audit.REPORT).read_bytes())
        self.assertEqual(result['summary']['selected_equal_multiset_pages'],211)
        self.assertEqual(result['summary']['ambiguous_maximum_pairing_pages'],12)
        self.assertEqual(sum(len(p['candidate_pairs']) for p in result['order_different_pages']),885)
        self.assertFalse(result['usable_as_verified_locus_crosswalk'])
        self.assertFalse(result['usable_for_statistical_evaluation'])

    def test_changed_accepted_parent_identity_is_rejected(self):
        with patch.object(audit,'PARENT_SHA256','0'*64),self.assertRaisesRegex(ValueError,'parent bytes changed'):
            audit.build()


if __name__=='__main__':unittest.main()
