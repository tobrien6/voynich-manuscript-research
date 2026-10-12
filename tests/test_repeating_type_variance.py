from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import permutations, product
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import repeating_type_variance as module
from scripts import repeating_types as parent
from scripts import token_baselines
from scripts.audit_transliterations import load_sources
from scripts.repetition_moments import conditional_moments
from test_repeating_types import synthetic_root


def exact(field):
    parts = field.split('/')
    return Fraction(int(Decimal(parts[0])), int(Decimal(parts[1])) if len(parts) == 2 else 1)


def brute_moments(rows):
    slots = [row for _, row in rows]
    outcomes = []
    for orders in product(*(set(permutations([v for v in row if v is not None])) for row in slots)):
        repeating = set()
        for original, order in zip(slots, orders):
            available = iter(order)
            placed = [None if v is None else next(available) for v in original]
            repeating.update(placed[i] for i in range(len(placed) - 1)
                             if placed[i] is not None and placed[i] == placed[i + 1])
        outcomes.append(len(repeating))
    mean = Fraction(sum(outcomes), len(outcomes))
    return mean, Fraction(sum(v * v for v in outcomes), len(outcomes)) - mean * mean


def variance_fixture(root):
    synthetic_root(root)
    for identifier, text in [('ZL3b', 'a.a.b.b'), ('IT2a', 'a.b.a.b')]:
        raw = f'#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> {text}\n'.encode()
        (root / f'data/raw/{identifier}.txt').write_bytes(raw)
    catalog_path = root / 'data/transliterations.json'
    catalog = json.loads(catalog_path.read_bytes())
    for source in catalog['sources']:
        raw = (root / source['path']).read_bytes()
        source['sha256'], source['bytes'] = parent.hashlib.sha256(raw).hexdigest(), len(raw)
    catalog_path.write_bytes(parent.encoded(catalog))
    with patch.object(token_baselines, 'load_sources', return_value=load_sources(root=root)):
        reference = token_baselines.baselines(repetitions=1, seed=1)
    (root / parent.BASELINE).write_bytes(parent.encoded(reference))
    shutil.copyfile(module.ROOT / module.ENGINE, root / module.ENGINE)
    (root / module.PLAN).write_text('Synthetic variance plan only.\n')
    result = subprocess.run([sys.executable, '-B', str(root / 'scripts/repeating_types.py'),
                             '--output', str(root / module.MEAN_REPORT)], capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stderr)
    return root


class RepeatingTypeVarianceTests(unittest.TestCase):
    def test_joint_counts_match_direct_original_coordinate_three_color_assignments(self):
        for size in range(8):
            for mask in range(1 << size):
                positions = [i for i in range(size) if mask & (1 << i)]
                slots = ['x' if i in positions else None for i in range(size)]
                _, _, components = parent.adjacency_graph(slots)
                totals, valid = Counter(), Counter()
                for colors in product('ABO', repeat=len(positions)):
                    placed = dict(zip(positions, colors))
                    key = colors.count('A'), colors.count('B')
                    totals[key] += 1
                    if not any(placed.get(i) in ('A', 'B') and placed.get(i) == placed.get(i + 1)
                               for i in range(size - 1)):
                        valid[key] += 1
                for counts, total in totals.items():
                    with self.subTest(size=size, mask=mask, counts=counts):
                        self.assertEqual(module.joint_no_repeat_probability(components, *counts),
                                         Fraction(valid[counts], total))

    def test_global_variance_matches_exhaustive_locus_permutations(self):
        cases = [[], [['a']], [list('aaaa')], [list('aabb')], [list('aaabb')],
                 [list('aab'), list('aab')], [list('aabb'), list('aabb')],
                 [['a', 'a', None, 'b', None, 'b']] * 2,
                 [list('aa'), list('aabb')], [list('aabc'), ['a', None, 'b', 'b']],
                 [list('abc'), [], ['a', None, 'a']]]
        for values in cases:
            rows = [[str(i), slots] for i, slots in enumerate(values)]
            expected_mean, expected_variance = brute_moments(rows)
            with self.subTest(values=values):
                result = module.summarize(rows)
                self.assertEqual(exact(result['conditional_expected_repeating_types_fraction']), expected_mean)
                self.assertEqual(exact(result['conditional_variance_fraction']), expected_variance)

    def test_signed_covariance_global_deduplication_and_forced_types(self):
        full = module.summarize([['one', list('aabb')]])
        self.assertEqual(exact(full['type_pair_covariance_sum_fraction']), Fraction(1, 12))
        self.assertEqual(exact(full['conditional_variance_fraction']), Fraction(2, 3))
        sparse = module.summarize([['one', ['a', 'a', None, 'b', None, 'b']]])
        self.assertEqual(exact(sparse['type_pair_covariance_sum_fraction']), Fraction(-1, 36))
        twice = module.summarize([['one', list('aabb')], ['two', list('aabb')]])
        self.assertEqual(exact(twice['type_pair_covariance_sum_fraction']), Fraction(7, 144))
        sparse_twice = module.summarize([['one', ['a', 'a', None, 'b', None, 'b']],
                                         ['two', ['a', 'a', None, 'b', None, 'b']]])
        self.assertEqual(exact(sparse_twice['type_pair_covariance_sum_fraction']), Fraction(-49, 1296))
        aab = module.summarize([['one', list('aab')], ['two', list('aab')]])
        self.assertEqual(exact(aab['conditional_variance_fraction']), Fraction(8, 81))
        forced = module.summarize([['forced', list('aa')], ['other', list('aabb')]])
        self.assertEqual(forced['forced_repeating_types'], 1)
        self.assertEqual(forced['forced_indicator_shared_pairs'], 1)
        self.assertEqual(exact(forced['conditional_variance_fraction']), Fraction(1, 4))
        disjoint = module.summarize([['one', list('aab')], ['two', list('ccd')]])
        self.assertEqual(disjoint['type_pairs_with_shared_opportunity'], 0)
        self.assertEqual(exact(disjoint['conditional_variance_fraction']), Fraction(4, 9))

    def test_single_locus_double_occurrences_match_accepted_pair_moments_for_all_masks(self):
        for mask in range(64):
            slots = [v if mask & (1 << i) else None for i, v in enumerate('aabbcc')]
            values, edges, _ = parent.adjacency_graph(slots)
            pair = conditional_moments(values, edges)
            actual = module.summarize([['fixture', slots]])
            self.assertEqual(exact(actual['conditional_expected_repeating_types_fraction']), pair['expected'])
            self.assertEqual(exact(actual['conditional_variance_fraction']), pair['variance'])

    def test_exact_zero_tiny_scales_large_serialization_and_context_are_preserved(self):
        constant = module.summarize([['constant', list('aaaa')]])
        self.assertTrue(constant['zero_conditional_variance'])
        self.assertIsNone(constant['observed_minus_expected_in_sd'])
        with localcontext() as context:
            context.prec = 1
            result = module.summarize([[str(i), list('abacabcaa')] for i in range(3884)])
        self.assertGreater(exact(result['conditional_variance_fraction']), 0)
        self.assertFalse(result['zero_conditional_variance'])
        self.assertIsNone(result['conditional_variance_approx'])
        self.assertGreater(result['conditional_standard_deviation'], 0)
        self.assertEqual(json.loads(parent.encoded(result)), result)
        extreme = module.diagnostics(Fraction(1, 10 ** 2000), Fraction(1))
        self.assertIsNone(extreme['conditional_standard_deviation'])
        self.assertIsNone(extreme['observed_minus_expected_in_sd'])
        self.assertGreater(Decimal(extreme['conditional_standard_deviation_decimal']), 0)
        with self.assertRaises(ValueError):
            module.diagnostics(Fraction(0), Fraction(1))

    def test_invalid_marked_counts_fail(self):
        for counts in ((True, 1), (-1, 2), (3, 2), (1.5, 1)):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                module.joint_no_repeat_probability([4], *counts)

    def test_complete_cli_parent_replay_typed_cache_and_protected_outputs(self):
        with tempfile.TemporaryDirectory(prefix='synthetic-type-variance-') as directory:
            root = variance_fixture(Path(directory))
            script = root / module.ENGINE
            protected = [root / module.PLAN, root / module.MEAN_REPORT, script, root / 'data/raw/ZL3b.txt']
            before = {path: path.read_bytes() for path in protected}
            for i, path in enumerate(protected):
                symlink, hardlink = root / f'symbolic-{i}.json', root / f'hard-{i}.json'
                symlink.symlink_to(path)
                os.link(path, hardlink)
                for output in (path, symlink, hardlink):
                    result = subprocess.run([sys.executable, '-B', str(script), '--output', str(output)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn('output aliases', result.stderr)
                    self.assertEqual({p: p.read_bytes() for p in protected}, before)
            target = root / 'variance.json'
            result = subprocess.run([sys.executable, '-B', str(script), '--output', str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            contents = json.loads(target.read_bytes())
            self.assertTrue(all(exact(v['conditional_variance_fraction']) == Fraction(2, 3)
                                for source in contents['sources'] for v in source['variants']))
            check = subprocess.run([sys.executable, '-B', str(script), '--check', str(target)], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            contents['schema_version'] = True
            target.write_bytes(parent.encoded(contents))
            bad = subprocess.run([sys.executable, '-B', str(script), '--check', str(target)], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            mean = json.loads((root / module.MEAN_REPORT).read_bytes())
            mean['sources'][0]['variants'][0]['observed_distinct_repeating_types'] += 1
            (root / module.MEAN_REPORT).write_bytes(parent.encoded(mean))
            failed = subprocess.run([sys.executable, '-B', str(script), '--output', str(root / 'failed.json')], capture_output=True, text=True)
            self.assertEqual(failed.returncode, 1)
            self.assertIn('complete parent replay', failed.stderr)
            self.assertFalse((root / 'failed.json').exists())


if __name__ == '__main__':
    unittest.main()
