from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from fractions import Fraction
import io
from itertools import combinations, permutations, product
import json
from math import factorial
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.paragraph_boundary_repetition import build as build_parent
from scripts.paragraph_token_corpus import build as build_corpus, coverage
from scripts.paragraph_order_control import (
    COVERAGE, PARENT, PLAN, analyze, build, constraints_probability, fraction, main, order_moments,
)
from test_paragraph_boundary_repetition import synthetic_root as boundary_root
from test_paragraph_token_corpus import fixture


def orders(size):
    if size == 1:
        return [(0,)]
    return [(0, *middle, size - 1) for middle in permutations(range(1, size - 1))]


def direct_moments(rows):
    values = [sum(rows[a][-1] == rows[b][0] for a, b in zip(order, order[1:]))
              for order in orders(len(rows))]
    mean = Fraction(sum(values), len(values))
    return mean, sum((Fraction(v) - mean) ** 2 for v in values) / len(values)


def direct_edge_probability(size, edges):
    """Independent event count by assigning positions to involved identities."""
    if any(a == b or a == size - 1 or b == 0 for a, b in edges):
        return Fraction()
    interior = sorted({i for edge in edges for i in edge if i not in (0, size - 1)})
    assignments = permutations(range(1, size - 1), len(interior))
    valid = total = 0
    for locations in assignments:
        positions = {0: 0, size - 1: size - 1, **dict(zip(interior, locations))}
        total += 1
        valid += all(positions[b] == positions[a] + 1 for a, b in edges)
    return Fraction(valid, total)


def synthetic_root(root):
    boundary_root(root)
    (root / PLAN).write_text('Fixed synthetic anchored-order plan.\n')
    (root / PARENT).write_bytes(encoded(build_parent(root)))
    return root


class ParagraphOrderTests(unittest.TestCase):
    def test_every_single_and_double_edge_event_against_exact_orders_through_eight_loci(self):
        for size in range(1, 9):
            arrangements = orders(size)
            singles, doubles = Counter(), Counter()
            for order in arrangements:
                edges = sorted(zip(order, order[1:]))
                singles.update(edges)
                doubles.update(combinations(edges, 2))
            possible = list(product(range(size), repeat=2))
            for edge in possible:
                self.assertEqual(constraints_probability(size, [edge]), Fraction(singles[edge], len(arrangements)))
            for a, b in combinations(possible, 2):
                self.assertEqual(constraints_probability(size, [a, b]), Fraction(doubles[a, b], len(arrangements)))

    def test_full_anchored_chains_partial_anchor_join_cycles_and_duplicate_requirements(self):
        self.assertEqual(constraints_probability(4, [(0, 2), (2, 1), (1, 3)]), Fraction(1, 2))
        self.assertEqual(constraints_probability(5, [(0, 2), (2, 4)]), 0)
        self.assertEqual(constraints_probability(4, [(1, 2), (2, 1)]), 0)
        self.assertEqual(constraints_probability(4, [(0, 1), (0, 2)]), 0)
        self.assertEqual(constraints_probability(4, [(1, 2), (0, 2)]), 0)
        self.assertEqual(constraints_probability(4, [(0, 1), (0, 1)]), Fraction(1, 2))
        self.assertEqual(constraints_probability(6, [(1, 2), (3, 4)]), Fraction(1, 12))

    def test_every_binary_endpoint_assignment_through_five_loci_has_exact_moments(self):
        for size in range(1, 6):
            for endpoints in product('ab', repeat=2 * size):
                rows = [list(endpoints[2 * i:2 * i + 2]) for i in range(size)]
                result = order_moments(rows)
                mean, variance = direct_moments(rows)
                self.assertEqual(fraction(result['conditional_mean']), mean)
                self.assertEqual(fraction(result['conditional_variance']), variance)
                self.assertEqual(result['invariant_repeat_count'], variance == 0)

    def test_identical_payloads_keep_identity_multiplicity_and_all_invariant_units(self):
        for size in range(1, 8):
            rows = [['a', 'a'] for _ in range(size)]
            result = order_moments(rows)
            self.assertEqual(result['possible_interior_orders'], factorial(max(size - 2, 0)))
            self.assertEqual(result['observed_repeats'], size - 1)
            self.assertEqual(fraction(result['conditional_mean']), size - 1)
            self.assertEqual(fraction(result['conditional_variance']), 0)
            self.assertIsNone(result['sd_scaled_contrast'])

    def test_endpoint_roles_preserved_even_when_token_interiors_change(self):
        rows = [['a', 'x', 'b'], ['b', 'y', 'a'], ['b', 'z', 'b'], ['a', 'w', 'b']]
        changed = [[row[0], 'NewInterior', row[-1]] for row in rows]
        self.assertEqual(order_moments(rows), order_moments(changed))
        original = deepcopy(rows)
        order_moments(rows)
        self.assertEqual(rows, original)

    def test_bad_sizes_indices_and_empty_loci_are_rejected(self):
        for size in (True, 0, -1):
            with self.assertRaises(ValueError): constraints_probability(size, [])
        for edge in ((True, 1), (0, 3), (0,), (-1, 1)):
            with self.assertRaises(ValueError): constraints_probability(3, [edge])
        for rows in ([], [[]], [['a'], []]):
            with self.assertRaises(ValueError): order_moments(rows)

    def test_synthetic_report_retains_every_unit_metadata_and_unchanged_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory))
            report = build(root)
            parent = build_parent(root)
        self.assertEqual(len(report['paragraphs']), 5)
        self.assertEqual(report['cohort']['common_eligible_units'], 5)
        self.assertTrue(all(v['invariant_paragraphs'] == 5 for v in report['variants']))
        self.assertEqual(report['parent_within_locus_control_summaries'], parent['variants'])
        pr = next(p for p in report['paragraphs'] if p['member_keys'] == ['f1r.4'])
        self.assertEqual(pr['variants'][0]['loci'][0]['locator'], '=')
        self.assertEqual(pr['variants'][0]['loci'][0]['variables']['L'], 'B')
        def walk(value):
            if isinstance(value, dict):
                self.assertNotIn('tokens', value)
                for child in value.values(): walk(child)
            elif isinstance(value, list):
                for child in value: walk(child)
        walk(report)

    def test_parent_omissions_and_empty_variants_never_silently_change_the_cohort(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory))
            corpus, parent = build_corpus(root), build_parent(root)
        altered = deepcopy(parent)
        unit = next(p for p in altered['paragraphs'] if p['boundary_ledger'])
        unit['boundary_ledger'][0]['eligible_in_all_variants'] = False
        with self.assertRaisesRegex(ValueError, 'omits an original boundary'): analyze(corpus, altered)
        altered = deepcopy(corpus)
        altered['paragraphs'][0]['variants'][0]['loci'][0]['tokens'] = []
        with self.assertRaisesRegex(ValueError, 'locus is empty'): analyze(altered, parent)
        altered = deepcopy(parent)
        altered['paragraphs'].pop()
        with self.assertRaisesRegex(ValueError, 'different complete unit'): analyze(corpus, altered)

    def test_paragraph_moments_add_without_dropping_zero_variance_units(self):
        text = ('<f1r>\n<f1r.1,@P0> <%>a.b\n<f1r.2,+P0> c.a\n'
                '<f1r.3,+P0> a.c\n<f1r.4,+P0> b.a\n<f1r.5,+P0> a.b<$>\n'
                '<f1r.6,+P0> <%>a<$>\n')
        with tempfile.TemporaryDirectory() as directory:
            root = fixture(Path(directory), left=text, right=text)
            (root / COVERAGE).write_bytes(encoded(coverage(build_corpus(root))))
            (root / 'research/transliteration/PARAGRAPH_BOUNDARY_PLAN.md').write_text('Synthetic plan.\n')
            parent = build_parent(root)
            corpus = build_corpus(root)
        before = deepcopy(corpus)
        report = analyze(corpus, parent)
        self.assertEqual(len(report['paragraphs']), 2)
        for i, v in enumerate(report['variants']):
            self.assertEqual(v['invariant_paragraphs'], 1)
            self.assertEqual(v['varying_paragraphs'], 1)
            self.assertEqual(fraction(v['conditional_variance']),
                             sum((fraction(p['variants'][i]['conditional_variance']) for p in report['paragraphs']), Fraction()))
            self.assertEqual(v['observed_repeats'], parent['variants'][i]['observed_repeats'])
        self.assertEqual(corpus, before)

    def test_forged_parent_rejected_before_new_control_computation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory))
            parent = json.loads((root / PARENT).read_text())
            parent['variants'][0]['observed_repeats'] += 1
            (root / PARENT).write_bytes(encoded(parent))
            with patch('scripts.paragraph_order_control.analyze') as analyzer, \
                    self.assertRaisesRegex(ValueError, 'complete pinned producer replay'):
                build(root)
            analyzer.assert_not_called()

    def test_output_protection_includes_new_plan_parents_code_and_hardlink_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory))
            targets = [root / PLAN, root / PARENT, root / COVERAGE,
                       Path(__file__).resolve().parents[1] / 'scripts/paragraph_order_control.py']
            for target in targets:
                alias = root / (target.name + '.alias')
                os.link(target, alias)
                for output in (target, alias):
                    before = target.read_bytes()
                    with patch('scripts.paragraph_order_control.ROOT', root), \
                            patch('scripts.paragraph_order_control.build') as producer, \
                            patch('sys.argv', ['order.py', '--output', str(output)]), \
                            redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): main()
                    producer.assert_not_called()
                    self.assertEqual(target.read_bytes(), before)

    def test_cli_rejects_symlink_and_hardlink_created_during_computation(self):
        for kind in ('symlink', 'hardlink'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = synthetic_root(Path(directory))
                target = root / PLAN
                before = target.read_bytes()
                output = root / 'late-alias.json'

                def link_while_computing(*args, **kwargs):
                    if kind == 'symlink':
                        output.symlink_to(target)
                    else:
                        os.link(target, output)
                    return {'cohort': {'common_eligible_units': 0}}

                with patch('scripts.paragraph_order_control.ROOT', root), \
                        patch('scripts.paragraph_order_control.build', side_effect=link_while_computing), \
                        patch('sys.argv', ['order.py', '--output', str(output)]), \
                        redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()), \
                        self.assertRaises(SystemExit): main()
                self.assertEqual(target.read_bytes(), before)

    def test_cli_writes_replays_and_rejects_complete_science_type_and_json_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory))
            output = root / 'order.json'
            with patch('scripts.paragraph_order_control.ROOT', root), \
                    patch('sys.argv', ['order.py', '--output', str(output)]), redirect_stdout(io.StringIO()): main()
            report = json.loads(output.read_text())
            self.assertEqual(report, build(root))
            with patch('scripts.paragraph_order_control.ROOT', root), \
                    patch('sys.argv', ['order.py', '--check', str(output)]), redirect_stdout(io.StringIO()): main()
            altered = deepcopy(report)
            altered['variants'][0]['conditional_mean']['numerator'] += 1
            typed = deepcopy(report)
            typed['schema_version'] = True
            for raw in (encoded(altered), encoded(typed), b'{"x":1,"x":2}', b'{"x":Infinity}'):
                output.write_bytes(raw)
                with patch('scripts.paragraph_order_control.ROOT', root), \
                        patch('sys.argv', ['order.py', '--check', str(output)]), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): main()

    def test_real_report_edges_joints_and_aggregate_moments_by_independent_position_assignments(self):
        root = Path(__file__).resolve().parents[1]
        report = json.loads((root / 'research/transliteration/paragraph_order_control.json').read_text())
        corpus = build_corpus(root)
        units = {p['common_unit_id']: p for p in corpus['paragraphs'] if p['common_eligible']}
        self.assertEqual({p['common_unit_id'] for p in report['paragraphs']}, set(units))
        totals = [{'observed': 0, 'mean': Fraction(), 'variance': Fraction(), 'invariant': 0} for _ in range(4)]
        for paragraph in report['paragraphs']:
            native = units[paragraph['common_unit_id']]
            for vi, (variant, source) in enumerate(zip(paragraph['variants'], native['variants'])):
                rows = [locus['tokens'] for locus in source['loci']]
                size = len(rows)
                edges = [(a, b) for a, b in product(range(size), repeat=2)
                         if a != b and rows[a][-1] == rows[b][0]]
                self.assertEqual([(e['left_locus_index'], e['right_locus_index'])
                                  for e in variant['endpoint_match_edges']], edges)
                probabilities = [direct_edge_probability(size, [e]) for e in edges]
                self.assertEqual([fraction(e['probability']) for e in variant['endpoint_match_edges']], probabilities)
                variance = sum((p * (1 - p) for p in probabilities), Fraction())
                pairs = list(combinations(range(len(edges)), 2))
                self.assertEqual([(p['left_edge_index'], p['right_edge_index'])
                                  for p in variant['edge_pair_covariances']], pairs)
                for (a, b), joint_row in zip(pairs, variant['edge_pair_covariances']):
                    joint = direct_edge_probability(size, [edges[a], edges[b]])
                    covariance = joint - probabilities[a] * probabilities[b]
                    self.assertEqual(fraction(joint_row['joint_probability']), joint)
                    self.assertEqual(fraction(joint_row['covariance']), covariance)
                    variance += 2 * covariance
                mean = sum(probabilities, Fraction())
                observed = sum(rows[i][-1] == rows[i + 1][0] for i in range(size - 1))
                self.assertEqual(fraction(variant['conditional_mean']), mean)
                self.assertEqual(fraction(variant['conditional_variance']), variance)
                self.assertEqual(variant['observed_repeats'], observed)
                self.assertEqual(variant['invariant_repeat_count'], variance == 0)
                totals[vi]['observed'] += observed
                totals[vi]['mean'] += mean
                totals[vi]['variance'] += variance
                totals[vi]['invariant'] += variance == 0
        for variant, total in zip(report['variants'], totals):
            self.assertEqual(variant['observed_repeats'], total['observed'])
            self.assertEqual(fraction(variant['conditional_mean']), total['mean'])
            self.assertEqual(fraction(variant['conditional_variance']), total['variance'])
            self.assertEqual(variant['invariant_paragraphs'], total['invariant'])


if __name__ == '__main__':
    unittest.main()
