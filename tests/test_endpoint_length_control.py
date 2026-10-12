from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
from fractions import Fraction
from itertools import combinations, permutations, product
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.anchored_path_moments import weighted_moments as unconditioned
from scripts.audit_eva_token_coverage import encoded
from scripts.paragraph_endpoint_distance import analyze as parent_analyze
from scripts.paragraph_token_corpus import build as corpus_build
from scripts.endpoint_length_control import analyze, main, PLAN, PARENT
from scripts.stratified_path_moments import allowed_orders, event_probability, weighted_moments
from test_paragraph_token_corpus import fixture


def orders(strata):
    size = len(strata)
    if size == 1:
        return [(0,)]
    return [(0, *middle, size - 1) for middle in permutations(range(1, size - 1))
            if all(strata[identity] == strata[slot] for slot, identity in enumerate(middle, 1))]


def exhaustive(weights, strata):
    values = [sum((weights[a][b] for a, b in zip(order, order[1:])), Fraction())
              for order in orders(strata)]
    mean = sum(values, Fraction()) / len(values)
    variance = sum(((x - mean) ** 2 for x in values), Fraction()) / len(values)
    return mean, variance


class EndpointLengthControlTests(unittest.TestCase):
    def test_every_single_and_double_event_for_all_small_binary_patterns(self):
        for size in range(1, 8):
            for inner in product(range(2), repeat=max(size - 2, 0)):
                strata = [0] if size == 1 else [0, *inner, 0]
                paths = [set(zip(order, order[1:])) for order in orders(strata)]
                self.assertEqual(allowed_orders(strata), len(paths))
                self.assertEqual(event_probability(strata, []), 1)
                edges = list(product(range(size), repeat=2))
                for edge in edges:
                    expected = Fraction(sum(edge in path for path in paths), len(paths))
                    self.assertEqual(event_probability(strata, [edge]), expected, (strata, edge))
                    self.assertEqual(event_probability(strata, [edge, edge]), expected)
                for left, right in combinations(edges, 2):
                    expected = Fraction(sum(left in path and right in path for path in paths), len(paths))
                    self.assertEqual(event_probability(strata, [left, right]), expected, (strata, left, right))

    def test_arbitrary_signed_rational_moments_for_every_small_pattern(self):
        for size in range(1, 8):
            for inner in product(range(2), repeat=max(size - 2, 0)):
                strata = [0] if size == 1 else [0, *inner, 0]
                for seed in range(3):
                    weights = [[None if a == b else Fraction((3*a+7*b+seed)%11-5, (a+b)%3+1)
                                for b in range(size)] for a in range(size)]
                    before = deepcopy((weights, strata))
                    result = weighted_moments(weights, strata)
                    mean, variance = exhaustive(weights, strata)
                    self.assertEqual(result['mean'], mean)
                    self.assertEqual(result['variance'], variance)
                    self.assertEqual(result['diagonal_variance'] + result['twice_covariance'], variance)
                    self.assertEqual(result['positive_joint_events'] + result['zero_joint_events'], result['joint_events_evaluated'])
                    self.assertEqual(result['invariant'], variance == 0)
                    self.assertEqual((weights, strata), before)

    def test_one_interior_stratum_reproduces_all_unconditioned_moments(self):
        for size in range(1, 9):
            weights = [[None if a == b else Fraction((a*5+b*3)%13-6, a%3+1)
                        for b in range(size)] for a in range(size)]
            self.assertEqual(weighted_moments(weights, [0]*size), unconditioned(weights))

    def test_interleaved_strata_duplicate_payloads_fixed_anchors_and_invariants(self):
        strata = [1, 1, 2, 1, 2, 1]
        values = ['A', 'B', 'B', 'A', 'C', 'A']
        weights = [[None if a == b else Fraction(values[a] != values[b])
                    for b in range(6)] for a in range(6)]
        self.assertEqual(allowed_orders(strata), 4)
        self.assertEqual((weighted_moments(weights, strata)['mean'], weighted_moments(weights, strata)['variance']), exhaustive(weights, strata))
        for row_only in (True, False):
            weights = [[None if a == b else Fraction(a+1 if row_only else 1, 3)
                        for b in range(6)] for a in range(6)]
            result = weighted_moments(weights, strata)
            self.assertEqual(result['variance'], 0)
            self.assertEqual(result['observed'], result['mean'])
        singleton = weighted_moments(weights, list(range(6)))
        self.assertEqual(singleton['possible_interior_orders'], 1)
        self.assertEqual(singleton['variance'], 0)
        self.assertEqual(event_probability(strata, [(1, 2), (2, 1)]), 0)
        self.assertEqual(event_probability(strata, [(0, 5)]), 0)

    def test_invalid_labels_shapes_weight_types_and_identity_types_rejected(self):
        for labels in ([], [True], ['0'], [-1], [1.0], None):
            with self.assertRaises(ValueError): allowed_orders(labels)
        for edges in ([(True, 1)], [(0, 4)], [(0, 1), (1, 2), (2, 3)], [(0, 1, 2)]):
            with self.assertRaises(ValueError): event_probability([0]*4, edges)
        for weights in ([], [[None]], [[None, 1], [Fraction(1), None]], [[Fraction(0), Fraction(1)], [Fraction(1), None]]):
            with self.assertRaises(ValueError): weighted_moments(weights, [0, 0])

    def synthetic(self):
        directory = tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup)
        body = ('<f1r> <! $L=A>\n<f1r.1,@P0> <%>Ab.cd\n<f1r.2,+P0> x.ab\n'
                '<f1r.3,+P0> xxx.a\n<f1r.4,+P0> z.ab\n<f1r.5,+P0> x,xx.a\n'
                '<f1r.6,+P0> Z.ab\n<f1r.7,+P0> cd.E<$>\n<f1r.8,+P1> <%>End<$>\n')
        root = fixture(Path(directory.name), left=body, right=body.replace('Z.ab','Z.abc'))
        corpus = corpus_build(root)
        return root, corpus, {**parent_analyze(corpus)}

    def test_complete_synthetic_corpus_preserves_costs_identity_and_four_variants(self):
        _, corpus, parent = self.synthetic()
        before = deepcopy((corpus, parent))
        report = analyze(corpus, parent)
        self.assertEqual(report['cohort'], parent['cohort'])
        self.assertEqual(len(report['paragraphs']), 2)
        for unit, old in zip(report['paragraphs'], parent['paragraphs']):
            self.assertEqual(unit['member_keys'], old['member_keys'])
            common = [v['controls'][1]['stratum_ids'] for v in unit['variants']]
            self.assertTrue(all(ids == common[0] for ids in common))
            for variant, original in zip(unit['variants'], old['variants']):
                self.assertEqual(len(variant['controls']), 2)
                for control in variant['controls']:
                    self.assertEqual(control['observed_cost_sum'], original['observed_cost_sum'])
                    self.assertLessEqual(control['possible_interior_orders'], original['possible_interior_orders'])
        for variant, old in zip(report['variants'], parent['variants']):
            for control in variant['controls']:
                self.assertEqual(control['boundary_count'], old['boundary_count'])
                self.assertEqual(control['observed_cost_sum'], old['observed_cost_sum'])
                self.assertEqual(control['invariant_units'] + control['varying_units'], 2)
        self.assertEqual((corpus, parent), before)
        self.assertNotIn(b'"tokens"', encoded(report))

    def test_source_parent_drift_and_empty_endpoints_cannot_be_silently_filtered(self):
        _, corpus, parent = self.synthetic()
        for mode in ('cost', 'unit', 'variant', 'locus', 'cohort', 'empty'):
            c, p = deepcopy(corpus), deepcopy(parent)
            if mode == 'cost':p['paragraphs'][0]['variants'][0]['cost_matrix'][0][1]['numerator'] += 1
            if mode == 'unit':p['paragraphs'][0]['member_keys'].reverse()
            if mode == 'variant':p['paragraphs'][0]['variants'].reverse()
            if mode == 'locus':p['paragraphs'][0]['variants'][0]['loci'].reverse()
            if mode == 'cohort':p['cohort']['common_eligible_units'] = True
            if mode == 'empty':next(x for x in c['paragraphs'] if x['common_eligible'])['variants'][0]['loci'][0]['tokens'] = []
            with self.subTest(mode=mode), self.assertRaises(ValueError): analyze(c, p)

    def test_cli_strict_replay_and_initial_late_symlink_hardlink_input_guards(self):
        root, _, _ = self.synthetic()
        (root / PLAN).write_bytes(b'fixed plan\n');(root / PARENT).write_bytes(b'parent bytes\n')
        target = root/'output.json'
        record = {'cohort': {'common_eligible_units': 2}, 'finite': 1}
        def invoke(args):
            with patch('scripts.endpoint_length_control.ROOT', root), patch('scripts.endpoint_length_control.build', return_value=record), patch('sys.argv', ['control', *args]), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                main()
        invoke(['--output', str(target)]);invoke(['--check', str(target)])
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', encoded({'cohort':{'common_eligible_units':True},'finite':1})):
            target.write_bytes(raw)
            with self.assertRaises(SystemExit): invoke(['--check', str(target)])
        before = (root/PLAN).read_bytes()
        for link in (False, True):
            alias = root/('symlink.json' if link else 'hardlink.json')
            if link:alias.symlink_to(root/PLAN)
            else:os.link(root/PLAN, alias)
            with self.assertRaises(SystemExit): invoke(['--output', str(alias)])
            self.assertEqual((root/PLAN).read_bytes(), before)
        target.unlink()
        original_encoded = encoded
        def late_alias(value):
            raw = original_encoded(value);target.symlink_to(root/PLAN);return raw
        with patch('scripts.endpoint_length_control.encoded', side_effect=late_alias), self.assertRaises(SystemExit):
            invoke(['--output', str(target)])
        self.assertEqual((root/PLAN).read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
