from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.anchored_path_moments import constraints_probability, event_probability, weighted_moments
from scripts.audit_eva_token_coverage import encoded
from scripts.paragraph_token_corpus import build as corpus_build, coverage
from scripts.paragraph_endpoint_distance import (
    COVERAGE, PLAN, analyze, build, levenshtein, normalized_distance, main,
)
from test_paragraph_token_corpus import LEFT, fixture


def orders(size):
    return [(0,)] if size == 1 else [(0, *middle, size - 1) for middle in permutations(range(1, size - 1))]


def exhaustive_moments(weights):
    values = [sum((weights[a][b] for a, b in zip(order, order[1:])), Fraction())
              for order in orders(len(weights))]
    mean = sum(values, Fraction()) / len(values)
    variance = sum(((v - mean) ** 2 for v in values), Fraction()) / len(values)
    return mean, variance


def synthetic_root(root):
    fixture(root, left=LEFT, right=LEFT)
    (root / PLAN).write_text('Fixed synthetic edit-distance plan.\n')
    (root / COVERAGE).write_bytes(encoded(coverage(corpus_build(root))))
    return root


@lru_cache(None)
def direct_position_probability(size, canonical_edges):
    """Count position assignments, without contracting chains or calling its counter."""
    edges = [(size - 1 if a == -1 else a, size - 1 if b == -1 else b)
             for a, b in canonical_edges]
    if any(a == b or a == size - 1 or b == 0 for a, b in edges):
        return Fraction()
    if len({a for a, _ in edges}) != len(edges) or len({b for _, b in edges}) != len(edges):
        return Fraction()
    identities = sorted({i for edge in edges for i in edge if i not in (0, size - 1)})
    valid = total = 0
    for slots in permutations(range(1, size - 1), len(identities)):
        positions = {0: 0, size - 1: size - 1, **dict(zip(identities, slots))}
        total += 1
        valid += all(positions[b] == positions[a] + 1 for a, b in edges)
    return Fraction(valid, total)


def independent_probability(size, edges):
    # Sort original identities rather than the production encounter-order renaming.
    inner = sorted({i for edge in edges for i in edge if i not in (0, size - 1)})
    ranks = {node: i + 1 for i, node in enumerate(inner)}
    mapping = lambda node: 0 if node == 0 else (-1 if node == size - 1 else ranks[node])
    canonical = tuple(sorted((mapping(a), mapping(b)) for a, b in edges))
    return direct_position_probability(size, canonical)


class EndpointDistanceTests(unittest.TestCase):
    def test_edit_distance_matches_independent_recursive_program_on_small_strings(self):
        @lru_cache(None)
        def independent(a, b):
            if not a: return len(b)
            if not b: return len(a)
            return min(1 + independent(a[1:], b), 1 + independent(a, b[1:]),
                       (a[0] != b[0]) + independent(a[1:], b[1:]))
        strings = [''.join(chars) for n in range(4) for chars in product('ab', repeat=n)]
        for a, b in product(strings, repeat=2):
            self.assertEqual(levenshtein(a, b), independent(a, b))
            self.assertEqual(normalized_distance(a, b), normalized_distance(b, a))
        self.assertEqual(levenshtein('ab', 'ba'), 2)
        self.assertEqual(normalized_distance('A', 'a'), 1)
        self.assertEqual(normalized_distance('', ''), 0)
        self.assertEqual(normalized_distance('', 'ab'), 1)

    def test_cached_identity_isomorphism_preserves_all_small_single_pair_probabilities(self):
        for size in range(1, 8):
            arrangements = orders(size)
            edges = list(product(range(size), repeat=2))
            actual_sets = [set(zip(order, order[1:])) for order in arrangements]
            for edge in edges:
                expected = Fraction(sum(edge in path for path in actual_sets), len(actual_sets))
                self.assertEqual(event_probability(size, [edge]), expected)
            for a, b in combinations(edges, 2):
                expected = Fraction(sum(a in path and b in path for path in actual_sets), len(actual_sets))
                self.assertEqual(event_probability(size, [a, b]), expected)
                self.assertEqual(event_probability(size, [a, b]), constraints_probability(size, [a, b]))

    def test_arbitrary_rational_weight_moments_match_exhaustive_identity_orders(self):
        for size in range(1, 8):
            for seed in range(5):
                weights = [[None if a == b else Fraction((3 * a + 7 * b + seed) % 11 - 5, (a + b) % 3 + 1)
                            for b in range(size)] for a in range(size)]
                before = deepcopy(weights)
                actual = weighted_moments(weights)
                expected_mean, expected_variance = exhaustive_moments(weights)
                self.assertEqual(actual['mean'], expected_mean)
                self.assertEqual(actual['variance'], expected_variance)
                self.assertEqual(actual['diagonal_variance'] + actual['twice_covariance'], expected_variance)
                self.assertEqual(actual['positive_joint_events'] + actual['zero_joint_events'], actual['joint_events_evaluated'])
                self.assertEqual(weights, before)

    def test_constant_and_row_only_costs_remain_invariant_despite_order_choices(self):
        for size in range(2, 8):
            for row_only in (False, True):
                weights = [[None if a == b else Fraction(a + 1 if row_only else 1, 3)
                            for b in range(size)] for a in range(size)]
                result = weighted_moments(weights)
                self.assertEqual(result['variance'], 0)
                self.assertEqual(result['observed'], result['mean'])
                self.assertTrue(result['invariant'])

    def test_invalid_weight_shapes_types_and_event_indices_rejected(self):
        for weights in ([], [[None, Fraction(1)]], [[Fraction(0)]], [[None, 1], [Fraction(1), None]]):
            with self.subTest(weights=weights), self.assertRaises(ValueError): weighted_moments(weights)
        for size, edges in ((True, []), (0, []), (3, [(True, 1)]), (3, [(0, 3)])):
            with self.assertRaises(ValueError): event_probability(size, edges)
        with self.assertRaises(ValueError): levenshtein(None, 'a')

    def test_complete_synthetic_corpus_retains_singletons_case_metadata_and_all_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory))
            record = build(root)
            corpus = corpus_build(root)
        self.assertEqual(record['cohort']['common_eligible_units'], 5)
        self.assertEqual(len(record['paragraphs']), 5)
        self.assertTrue(all(v['boundary_count'] == 1 and v['invariant_paragraphs'] == 5 for v in record['variants']))
        self.assertTrue(all(v['sd_scaled_contrast'] is None for v in record['variants']))
        pr = next(p for p in record['paragraphs'] if p['member_keys'] == ['f1r.4'])
        self.assertEqual(pr['variants'][0]['loci'][0]['locator'], '=')
        self.assertEqual(pr['variants'][0]['loci'][0]['variables']['L'], 'B')
        self.assertTrue(all('tokens' not in row for p in record['paragraphs'] for v in p['variants'] for row in v['loci']))
        before = deepcopy(corpus)
        analyze(corpus)
        self.assertEqual(corpus, before)

    def test_nonempty_cohort_cannot_silently_drop_an_endpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = corpus_build(synthetic_root(Path(directory)))
        corpus['paragraphs'][0]['variants'][0]['loci'][0]['tokens'] = []
        with self.assertRaisesRegex(ValueError, 'no silent filtering'): analyze(corpus)

    def test_changed_parent_coverage_rejected_before_new_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory))
            value = json.loads((root / COVERAGE).read_text())
            value['cohort']['common_eligible_units'] += 1
            (root / COVERAGE).write_bytes(encoded(value))
            with patch('scripts.paragraph_endpoint_distance.analyze') as analyzer, \
                    self.assertRaisesRegex(ValueError, 'complete pinned-source corpus replay'): build(root)
            analyzer.assert_not_called()

    def test_cli_protects_initial_and_late_source_plan_aliases(self):
        for kind in ('symlink', 'hardlink'):
            with tempfile.TemporaryDirectory() as directory:
                root = synthetic_root(Path(directory));target = root / PLAN
                before = target.read_bytes();output = root / 'late.json'
                def alias_during_build(*args, **kwargs):
                    if kind == 'symlink': output.symlink_to(target)
                    else: os.link(target, output)
                    return {'cohort': {'common_eligible_units': 0}}
                with patch('scripts.paragraph_endpoint_distance.ROOT', root), \
                        patch('scripts.paragraph_endpoint_distance.build', side_effect=alias_during_build), \
                        patch('sys.argv', ['edit.py', '--output', str(output)]), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): main()
                self.assertEqual(target.read_bytes(), before)
                with patch('scripts.paragraph_endpoint_distance.ROOT', root), \
                        patch('scripts.paragraph_endpoint_distance.build') as producer, \
                        patch('sys.argv', ['edit.py', '--output', str(output)]), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): main()
                producer.assert_not_called()

    def test_complete_cli_replay_handles_valid_outputs_and_rejects_matrix_type_json_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory));output = root / 'report.json'
            with patch('scripts.paragraph_endpoint_distance.ROOT', root), \
                    patch('sys.argv', ['edit.py', '--output', str(output)]), redirect_stdout(io.StringIO()): main()
            report = json.loads(output.read_text());self.assertEqual(report, build(root))
            with patch('scripts.paragraph_endpoint_distance.ROOT', root), \
                    patch('sys.argv', ['edit.py', '--check', str(output)]), redirect_stdout(io.StringIO()): main()
            changed = deepcopy(report)
            unit = next(p for p in changed['paragraphs'] if len(p['member_keys']) == 2)
            unit['variants'][0]['cost_matrix'][0][1]['numerator'] += 1
            typed = deepcopy(report);typed['schema_version'] = True
            for raw in (encoded(changed), encoded(typed), b'{"x":1,"x":2}', b'{"x":NaN}'):
                output.write_bytes(raw)
                with patch('scripts.paragraph_endpoint_distance.ROOT', root), \
                        patch('sys.argv', ['edit.py', '--check', str(output)]), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): main()

    def test_real_costs_and_moments_by_independent_string_and_position_programs(self):
        root = Path(__file__).resolve().parents[1]
        record = json.loads((root / 'research/transliteration/paragraph_endpoint_distance.json').read_text())
        corpus = corpus_build(root)
        units = {p['common_unit_id']: p for p in corpus['paragraphs'] if p['common_eligible']}
        self.assertEqual({p['common_unit_id'] for p in record['paragraphs']}, set(units))
        def f(value): return Fraction(value['numerator'], value['denominator'])
        @lru_cache(None)
        def distance(a, b):
            if not a: return len(b)
            if not b: return len(a)
            return min(1 + distance(a[1:], b), 1 + distance(a, b[1:]),
                       (a[0] != b[0]) + distance(a[1:], b[1:]))
        totals = [{'observed': Fraction(), 'mean': Fraction(), 'variance': Fraction(), 'invariant': 0}
                  for _ in range(4)]
        for paragraph in record['paragraphs']:
            native = units[paragraph['common_unit_id']]
            for vi, (variant, source) in enumerate(zip(paragraph['variants'], native['variants'])):
                rows = source['loci'];size = len(rows)
                weights = [[None if a == b else Fraction(distance(rows[a]['tokens'][-1], rows[b]['tokens'][0]),
                                                        max(len(rows[a]['tokens'][-1]), len(rows[b]['tokens'][0])))
                            for b in range(size)] for a in range(size)]
                expected_matrix = [[None if w is None else {'numerator': w.numerator, 'denominator': w.denominator}
                                    for w in row] for row in weights]
                self.assertEqual(variant['cost_matrix'], expected_matrix)
                probabilities = {(a, b): independent_probability(size, [(a, b)])
                                 for a in range(size) for b in range(size) if a != b}
                for (a, b), p in probabilities.items():
                    self.assertEqual(f(variant['adjacency_probability_matrix'][a][b]), p)
                edges = [edge for edge, p in probabilities.items() if p and weights[edge[0]][edge[1]]]
                mean = sum((weights[a][b] * probabilities[a, b] for a, b in edges), Fraction())
                diagonal = sum((weights[a][b] ** 2 * probabilities[a, b] * (1 - probabilities[a, b])
                                for a, b in edges), Fraction())
                covariance = Fraction()
                for first, second in combinations(edges, 2):
                    q = independent_probability(size, [first, second])
                    covariance += weights[first[0]][first[1]] * weights[second[0]][second[1]] * (
                        q - probabilities[first] * probabilities[second])
                variance = diagonal + 2 * covariance
                observed = sum((weights[i][i + 1] for i in range(size - 1)), Fraction())
                self.assertEqual(f(variant['observed_cost_sum']), observed)
                self.assertEqual(f(variant['conditional_mean_cost_sum']), mean)
                self.assertEqual(f(variant['conditional_variance_cost_sum']), variance)
                self.assertEqual(f(variant['diagonal_variance']), diagonal)
                self.assertEqual(f(variant['twice_covariance_sum']), 2 * covariance)
                self.assertEqual(variant['invariant'], variance == 0)
                totals[vi]['observed'] += observed;totals[vi]['mean'] += mean
                totals[vi]['variance'] += variance;totals[vi]['invariant'] += variance == 0
        for variant, total in zip(record['variants'], totals):
            self.assertEqual(f(variant['observed_cost_sum']), total['observed'])
            self.assertEqual(f(variant['conditional_mean_cost_sum']), total['mean'])
            self.assertEqual(f(variant['conditional_variance_cost_sum']), total['variance'])
            self.assertEqual(variant['invariant_paragraphs'], total['invariant'])


if __name__ == '__main__':
    unittest.main()
