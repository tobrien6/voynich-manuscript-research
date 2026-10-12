from collections import Counter
from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.endpoint_length_layout import (
    PLAN, METRIC, TEST, FAMILIES, build, draws, identity_orders, costs, path_moments,
    pair_expectations, rational, main, family,
)
from test_paragraph_token_corpus import fixture


@lru_cache(None)
def independent_edit(a,b):
    if not a:return len(b)
    if not b:return len(a)
    return min(1+independent_edit(a[1:],b),1+independent_edit(a,b[1:]),
               (a[0]!=b[0])+independent_edit(a[1:],b[1:]))


def grouped_orders(lengths,fixed):
    size=len(lengths)
    if size==1:return [(0,)]
    groups={}
    for slot in range(1,size-1):groups.setdefault(lengths[slot] if fixed else 0,[]).append(slot)
    slots=list(groups.values());results=[]
    for choices in product(*(list(permutations(group)) for group in slots)):
        path=list(range(size))
        for positions,identities in zip(slots,choices):
            for position,identity in zip(positions,identities):path[position]=identity
        results.append(tuple(path))
    return results


def edge_moments(weights,paths):
    edges=list(product(range(len(weights)),repeat=2))
    edges=[edge for edge in edges if edge[0]!=edge[1]]
    sets=[set(zip(path,path[1:])) for path in paths]
    probabilities={edge:Fraction(sum(edge in s for s in sets),len(sets)) for edge in edges}
    mean=sum((weights[a][b]*probabilities[a,b] for a,b in edges),Fraction())
    variance=sum((weights[a][b]**2*probabilities[a,b]*(1-probabilities[a,b]) for a,b in edges),Fraction())
    for first,second in combinations(edges,2):
        joint=Fraction(sum(first in s and second in s for s in sets),len(sets))
        variance+=2*weights[first[0]][first[1]]*weights[second[0]][second[1]]*(joint-probabilities[first]*probabilities[second])
    return mean,variance


class EndpointLengthLayoutTests(unittest.TestCase):
    def test_metric_matches_recursive_pair_costs_and_fixed_pair_predictions(self):
        tokens=['a','b','aa','ab','ba','bb']
        matrix=costs(tokens)
        for a,b in product(range(len(tokens)),repeat=2):
            if a==b:self.assertIsNone(matrix[a][b])
            else:self.assertEqual(matrix[a][b],Fraction(independent_edit(tokens[a],tokens[b]),max(len(tokens[a]),len(tokens[b]))))
        self.assertEqual(costs(['A','a'])[0][1],1)
        records=pair_expectations()
        self.assertEqual(len(records),4)
        for r in records:
            self.assertEqual(r['pair_count'],2**(r['left_length']+r['right_length']))
            self.assertEqual(r['expected_cost'],rational(Fraction(1,2) if r['left_length']==r['right_length'] else Fraction(5,8)))

    def test_all_draws_are_unique_uniform_products_and_pair_marginals_independent(self):
        for name,lengths in FAMILIES:
            records=list(draws(lengths));n=2**sum(lengths)
            self.assertEqual(len(records),n);self.assertEqual(len(set(records)),n)
            self.assertTrue(all([len(token) for token in row]==list(lengths) for row in records))
            for i in range(6):
                counts=Counter(row[i] for row in records)
                self.assertEqual(set(counts.values()),{n//2**lengths[i]})
                for j in range(i+1,6):
                    joint=Counter((row[i],row[j]) for row in records)
                    self.assertEqual(set(joint.values()),{n//2**(lengths[i]+lengths[j])})
                    self.assertEqual(len(joint),2**(lengths[i]+lengths[j]))

    def test_every_small_binary_length_pattern_matches_independent_partition_orders(self):
        for size in range(1,8):
            for lengths in product((1,2),repeat=size):
                for fixed in (False,True):
                    actual=identity_orders(lengths,fixed)
                    expected=grouped_orders(lengths,fixed)
                    self.assertEqual(set(actual),set(expected));self.assertEqual(len(actual),len(expected))
                    self.assertIn(tuple(range(size)),actual)
                    self.assertTrue(all(path[0]==0 and path[-1]==size-1 for path in actual))
        self.assertEqual([len(identity_orders(lengths,True)) for _,lengths in FAMILIES],[4,4,24])
        self.assertEqual([len(identity_orders(lengths,False)) for _,lengths in FAMILIES],[24,24,24])

    def test_signed_path_moments_match_separate_edge_covariance_on_small_examples(self):
        for size in range(1,7):
            for lengths in ([1]*size,[1 if i%2==0 else 2 for i in range(size)], [1 if i<size//2 else 2 for i in range(size)]):
                for fixed in (False,True):
                    weights=[[None if a==b else Fraction((3*a+7*b)%11-5,(a+b)%3+1) for b in range(size)] for a in range(size)]
                    paths=identity_orders(lengths,fixed);before=deepcopy((weights,paths))
                    result=path_moments(weights,paths);mean,variance=edge_moments(weights,grouped_orders(lengths,fixed))
                    self.assertEqual(result['conditional_mean_cost_sum'],rational(mean))
                    self.assertEqual(result['conditional_variance_cost_sum'],rational(variance))
                    self.assertEqual(result['invariant'],variance==0)
                    self.assertEqual(sum(r['count'] for r in result['path_cost_histogram']),len(paths))
                    self.assertEqual((weights,paths),before)

    def test_repeated_payloads_keep_identity_multiplicity_and_invariants_cancel(self):
        for size in range(1,7):
            paths=identity_orders([1]*size,False)
            repeated=path_moments(costs(['a']*size),paths)
            self.assertEqual(repeated['possible_identity_orders'],len(paths))
            self.assertTrue(repeated['invariant']);self.assertEqual(repeated['centered_cost_sum'],rational(Fraction()))
            for mode in ('constant','row','telescoping'):
                weights=[[None if a==b else Fraction(1 if mode=='constant' else (a if mode=='row' else a-b),3) for b in range(size)] for a in range(size)]
                result=path_moments(weights,paths)
                self.assertTrue(result['invariant']);self.assertEqual(result['conditional_variance_cost_sum'],rational(Fraction()))

    def test_invalid_draw_order_matrix_and_metric_pin_inputs_rejected(self):
        for lengths in ([],[True],[0],[3],[1.0],None):
            with self.assertRaises(ValueError):draws(lengths)
        with self.assertRaises(ValueError):identity_orders([1,2],1)
        for tokens in ([],[''],[None]):
            with self.assertRaises(ValueError):costs(tokens)
        for weights in ([],[[Fraction(0)]],[[None,1],[Fraction(1),None]]):
            with self.assertRaises(ValueError):path_moments(weights,[(0,1)])
        for paths in ([],[(1,0)],[(0,1),(0,1)],[(0,True)],[[0,1]],[(0,2)]):
            with self.assertRaises(ValueError):path_moments([[None,Fraction(1)],[Fraction(1),None]],paths)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'scripts').mkdir();(root/METRIC).write_bytes(b'changed metric')
            with self.assertRaisesRegex(ValueError,'metric changed'):build(root)
        with self.assertRaises(ValueError):family('invalid',(1,2),(Fraction(),)*3)

    def test_cli_typed_replay_rejects_tampering_duplicates_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as directory:
            root=fixture(Path(directory));(root/'research/baselines').mkdir();(root/PLAN).write_text('fixed toy plan\n')
            target=root/'report.json';report={'finite':1}
            def run(args):
                with patch('scripts.endpoint_length_layout.ROOT',root),patch('scripts.endpoint_length_layout.build',return_value=report),patch('sys.argv',['demo',*args]),redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):main()
            run(['--output',str(target)]);run(['--check',str(target)])
            for raw in (b'{"finite":true}',b'{"finite":1.0}',b'{"finite":1,"finite":1}',b'{"finite":NaN}',b'{"finite":Infinity}'):
                target.write_bytes(raw)
                with self.assertRaises(SystemExit):run(['--check',str(target)])

    def test_cli_guards_metric_plan_test_and_source_aliases_before_and_after_serialization(self):
        with tempfile.TemporaryDirectory() as directory:
            root=fixture(Path(directory));(root/'research/baselines').mkdir();(root/'scripts').mkdir();(root/'tests').mkdir()
            for name in (PLAN,METRIC,TEST):(root/name).write_bytes(b'preserve input\n')
            target=root/'report.json'
            def run(out):
                with patch('scripts.endpoint_length_layout.ROOT',root),patch('scripts.endpoint_length_layout.build',return_value={'finite':1}),patch('sys.argv',['demo','--output',str(out)]),redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):main()
            for i,name in enumerate((PLAN,METRIC,TEST,Path('data/raw/ZL3b.txt'))):
                original=(root/name).read_bytes()
                for symbolic in (False,True):
                    alias=root/f'alias-{i}-{symbolic}.json'
                    if symbolic:alias.symlink_to(root/name)
                    else:os.link(root/name,alias)
                    with self.assertRaises(SystemExit):run(alias)
                    self.assertEqual((root/name).read_bytes(),original)
            def late(value):
                raw=encoded(value);target.symlink_to(root/PLAN);return raw
            with patch('scripts.endpoint_length_layout.encoded',side_effect=late),self.assertRaises(SystemExit):run(target)
            self.assertEqual((root/PLAN).read_bytes(),b'preserve input\n')


if __name__=='__main__':unittest.main()
