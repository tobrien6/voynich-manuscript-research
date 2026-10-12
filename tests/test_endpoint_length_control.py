from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
from fractions import Fraction
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from math import factorial, prod, sqrt
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
from scripts.audit_transliterations import ROOT
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


@lru_cache(None)
def direct_positions(strata, edges):
    """Assign involved identities to slots directly; no chain contraction."""
    size = len(strata)
    identities = sorted({i for edge in edges for i in edge if i not in (0, size-1)})
    choices = [[slot for slot in range(1, size-1) if strata[slot] == strata[i]] for i in identities]
    total = valid = 0
    for assignment in product(*choices):
        if len(set(assignment)) != len(assignment):
            continue
        positions = {0:0, size-1:size-1, **dict(zip(identities, assignment))}
        total += 1
        valid += all(positions[b] == positions[a] + 1 for a,b in edges)
    return Fraction(valid, total)


def restricted_orders(strata):
    """Independent complete order enumeration, branching only on allowed slots."""
    size = len(strata)
    if size == 1:
        return [(0,)]
    def walk(path, remaining):
        if not remaining:
            yield (*path,size-1)
        else:
            slot = len(path)
            for identity in sorted(remaining):
                if strata[identity] == strata[slot]:
                    yield from walk((*path,identity),remaining-{identity})
    return list(walk((0,),set(range(1,size-1))))


@lru_cache(None)
def independent_edit(left,right):
    if not left:return len(right)
    if not right:return len(left)
    return min(1+independent_edit(left[1:],right),1+independent_edit(left,right[1:]),
               (left[0]!=right[0])+independent_edit(left[1:],right[1:]))


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

    def test_every_real_cost_partition_probability_joint_and_moment_independently(self):
        # Added after the first result. Expected values use direct position
        # assignments, complete allowed paths and independent recursive edits.
        import json,hashlib
        report=json.loads((ROOT/'research/transliteration/endpoint_length_control.json').read_bytes())
        parent=json.loads((ROOT/PARENT).read_bytes())
        corpus=corpus_build(ROOT)
        units=[u for u in corpus['paragraphs'] if u['common_eligible']]
        self.assertEqual(report['cohort'],parent['cohort'])
        self.assertEqual(len(units),len(report['paragraphs']))
        exact=lambda r:Fraction(r['numerator'],r['denominator'])
        rational_expected=lambda f:{'numerator':f.numerator,'denominator':f.denominator}
        for name,sha in report['inputs']['pinned_dependency_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha)
        for name,sha in report['inputs']['implementation_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest(),sha)
        self.assertEqual(hashlib.sha256((ROOT/PLAN).read_bytes()).hexdigest(),report['inputs']['plan_sha256'])
        checked_joints=0
        for u,p,original in zip(units,report['paragraphs'],parent['paragraphs']):
            for key in ('common_unit_id','page_id','member_keys','source_unit_ids'):
                self.assertEqual(p[key],u[key]);self.assertEqual(p[key],original[key])
            lengths=[[(len(row['tokens'][0]),len(row['tokens'][-1])) for row in v['loci']] for v in u['variants']]
            common=[tuple(n for pairs in lengths for n in pairs[i]) for i in range(len(lengths[0]))]
            self.assertEqual(p['common_length_vectors'],[list(x) for x in common])
            for vi,(v,r,old) in enumerate(zip(u['variants'],p['variants'],original['variants'])):
                for key in ('source_id','uncertain_spaces'):self.assertEqual(r[key],v[key]);self.assertEqual(r[key],old[key])
                self.assertEqual(r['initial_terminal_ascii_lengths'],[list(x) for x in lengths[vi]])
                rows=v['loci'];size=len(rows)
                costs=[[None if a==b else Fraction(independent_edit(rows[a]['tokens'][-1],rows[b]['tokens'][0]),max(len(rows[a]['tokens'][-1]),len(rows[b]['tokens'][0]))) for b in range(size)] for a in range(size)]
                self.assertEqual([[None if x is None else rational_expected(x) for x in row] for row in costs],old['cost_matrix'])
                for ci,record in enumerate(r['controls']):
                    self.assertEqual(record['control_id'],('variant_endpoint_lengths','common_endpoint_lengths')[ci])
                    labels=lengths[vi] if ci==0 else common
                    representatives=sorted({labels.index(label) for label in labels})
                    strata=tuple(representatives.index(labels.index(label)) for label in labels)
                    self.assertEqual(record['stratum_ids'],list(strata))
                    groups=[{'stratum_id':label,'identity_indices':[i for i in range(1,size-1) if strata[i]==label]} for label in sorted(set(strata[1:-1]))]
                    self.assertEqual(record['interior_strata'],groups)
                    paths=restricted_orders(strata)
                    count=prod(factorial(len(g['identity_indices'])) for g in groups)
                    self.assertEqual(len(paths),count);self.assertEqual(record['possible_interior_orders'],count)
                    self.assertEqual(record['retained_order_fraction'],rational_expected(Fraction(count,factorial(max(size-2,0)))))
                    values=[sum((costs[a][b] for a,b in zip(path,path[1:])),Fraction()) for path in paths]
                    mean=sum(values,Fraction())/count
                    variance=sum(((value-mean)**2 for value in values),Fraction())/count
                    observed=sum((costs[i][i+1] for i in range(size-1)),Fraction())
                    for field,value in [('observed_cost_sum',observed),('conditional_mean_cost_sum',mean),('conditional_variance_cost_sum',variance),('centered_cost_sum',observed-mean)]:
                        self.assertEqual(record[field],rational_expected(value))
                    self.assertEqual(record['boundary_count'],size-1)
                    self.assertEqual(record['invariant'],variance==0)
                    self.assertEqual(record['newly_invariant_from_parent'],variance==0 and not old['invariant'])
                    self.assertEqual(record['expected_cost_change_from_parent'],rational_expected(mean-exact(old['conditional_mean_cost_sum'])))
                    self.assertEqual(record['variance_change_from_parent'],rational_expected(variance-exact(old['conditional_variance_cost_sum'])))
                    probabilities=[[None if a==b else direct_positions(strata,((a,b),)) for b in range(size)] for a in range(size)]
                    self.assertEqual(record['adjacency_probability_matrix'],[[None if x is None else rational_expected(x) for x in row] for row in probabilities])
                    edges=[(a,b) for a in range(size) for b in range(size) if a!=b and costs[a][b] and probabilities[a][b]]
                    diagonal=sum((costs[a][b]**2*probabilities[a][b]*(1-probabilities[a][b]) for a,b in edges),Fraction())
                    covariance=Fraction();zero=0
                    for left,right in combinations(edges,2):
                        joint=direct_positions(strata,tuple(sorted((left,right))))
                        self.assertEqual(event_probability(strata,[left,right]),joint)
                        covariance+=costs[left[0]][left[1]]*costs[right[0]][right[1]]*(joint-probabilities[left[0]][left[1]]*probabilities[right[0]][right[1]])
                        zero+=joint==0;checked_joints+=1
                    joints=len(edges)*(len(edges)-1)//2
                    self.assertEqual(record['nonzero_weight_possible_edges'],len(edges))
                    self.assertEqual(record['joint_events_evaluated'],joints)
                    self.assertEqual(record['zero_joint_events'],zero)
                    self.assertEqual(record['positive_joint_events'],joints-zero)
                    self.assertEqual(record['diagonal_variance'],rational_expected(diagonal))
                    self.assertEqual(record['twice_covariance_sum'],rational_expected(2*covariance))
                    self.assertEqual(diagonal+2*covariance,variance)
                    for field,value in [('observed_mean_cost',observed),('conditional_expected_mean_cost',mean),('centered_mean_cost',observed-mean)]:
                        if size>1:self.assertAlmostEqual(record[field],float(value/(size-1)),places=15)
                        else:self.assertIsNone(record[field])
                    self.assertAlmostEqual(record['conditional_sd_cost_sum'],sqrt(float(variance)),places=15)
                    if variance:self.assertAlmostEqual(record['sd_scaled_contrast'],float(observed-mean)/sqrt(float(variance)),places=15)
                    else:self.assertIsNone(record['sd_scaled_contrast'])
        for vi,(variant,old) in enumerate(zip(report['variants'],parent['variants'])):
            for ci,aggregate in enumerate(variant['controls']):
                records=[p['variants'][vi]['controls'][ci] for p in report['paragraphs']]
                total=lambda field:sum((exact(r[field]) for r in records),Fraction())
                boundaries=sum(r['boundary_count'] for r in records)
                for field in ('observed_cost_sum','conditional_mean_cost_sum','conditional_variance_cost_sum','centered_cost_sum','diagonal_variance','twice_covariance_sum'):
                    self.assertEqual(aggregate[field],rational_expected(total(field)))
                self.assertEqual(aggregate['boundary_count'],boundaries)
                for field in ('nonzero_weight_possible_edges','joint_events_evaluated','zero_joint_events','positive_joint_events'):
                    self.assertEqual(aggregate[field],sum(r[field] for r in records))
                invariant=[p['common_unit_id'] for p,r in zip(report['paragraphs'],records) if r['invariant']]
                newly=[p['common_unit_id'] for p,r in zip(report['paragraphs'],records) if r['newly_invariant_from_parent']]
                self.assertEqual(aggregate['invariant_unit_ids'],invariant);self.assertEqual(aggregate['newly_invariant_unit_ids'],newly)
                self.assertEqual(aggregate['invariant_units'],len(invariant));self.assertEqual(aggregate['varying_units'],len(records)-len(invariant))
                self.assertEqual(aggregate['units_with_multiple_orders'],sum(r['possible_interior_orders']>1 for r in records))
                self.assertEqual(aggregate['units_with_reduced_order_freedom'],sum(exact(r['retained_order_fraction'])<1 for r in records))
                self.assertEqual(aggregate['possible_order_count_histogram'],dict(Counter(str(r['possible_interior_orders']) for r in records)))
                self.assertEqual(aggregate['expected_cost_change_from_parent'],rational_expected(total('conditional_mean_cost_sum')-exact(old['conditional_mean_cost_sum'])))
                self.assertEqual(aggregate['variance_change_from_parent'],rational_expected(total('conditional_variance_cost_sum')-exact(old['conditional_variance_cost_sum'])))
                for field,source in [('observed_mean_cost','observed_cost_sum'),('conditional_expected_mean_cost','conditional_mean_cost_sum'),('centered_mean_cost','centered_cost_sum')]:
                    self.assertAlmostEqual(aggregate[field],float(total(source)/boundaries),places=15)
                self.assertAlmostEqual(aggregate['centered_mean_change_from_parent'],float(total('centered_cost_sum')/boundaries)-old['centered_mean_cost'],places=15)
                variance=total('conditional_variance_cost_sum')
                self.assertAlmostEqual(aggregate['conditional_sd_cost_sum'],sqrt(float(variance)),places=15)
                self.assertAlmostEqual(aggregate['sd_scaled_contrast'],float(total('centered_cost_sum'))/sqrt(float(variance)),places=15)
        self.assertEqual(checked_joints,sum(c['joint_events_evaluated'] for v in report['variants'] for c in v['controls']))


if __name__ == '__main__':
    unittest.main()
