import contextlib
from fractions import Fraction
import io
import itertools
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import repetition_distances as module
from scripts.ivtff import parse_ivtff


def enumerate_joint(slots):
    positions = [i for i, value in enumerate(slots) if value is not None]
    values = [slots[i] for i in positions]
    outcomes = []
    for permutation in set(itertools.permutations(values)):
        placed = [None] * len(slots)
        for position, value in zip(positions, permutation):
            placed[position] = value
        outcomes.append([sum(placed[i] is not None and placed[i + distance] is not None
                             and placed[i] == placed[i + distance]
                             for i in range(max(0, len(slots) - distance)))
                         for distance in module.DISTANCES])
    means = [Fraction(sum(row[i] for row in outcomes), len(outcomes)) for i in range(4)]
    covariance = [[sum((row[i] - means[i]) * (row[j] - means[j]) for row in outcomes) / len(outcomes)
                   for j in range(4)] for i in range(4)]
    return means, covariance


class RepetitionDistanceTests(unittest.TestCase):
    def test_full_covariance_matches_exhaustive_permutations_for_every_exclusion_mask(self):
        for mask in range(64):
            slots = [value if mask & (1 << i) else None for i, value in enumerate('aabbbc')]
            with self.subTest(mask=mask):
                actual = module.distance_moments(slots)
                mean, covariance = enumerate_joint(slots)
                self.assertEqual(actual['expected'], mean)
                self.assertEqual(actual['covariance'], covariance)

    def test_excluded_interiors_keep_their_original_distance(self):
        actual = module.distance_moments(['a', None, 'a', 'b'])
        self.assertEqual(actual['eligible_pairs'], [1, 1, 1, 0])
        self.assertEqual(actual['observed_equal_pairs'], [0, 1, 0, 0])
        self.assertEqual(actual['pairs_spanning_excluded_interior_slots'], [0, 1, 1, 0])
        self.assertEqual(actual['expected'][:3], [Fraction(1, 3)] * 3)
        # The three different pairs exhaust this bag's one equal pair.
        self.assertEqual(actual['covariance'][0][1], Fraction(-1, 9))

    def test_degenerate_bags_and_empty_denominators_are_explicit(self):
        for slots in ([], [None], ['a'], list('abcde'), list('aaaaa'), ['a', None, 'a']):
            with self.subTest(slots=slots):
                summary = module.summarize([['synthetic', slots]])
                for distance in summary['distances']:
                    self.assertEqual(distance['conditional_variance'], 0)
                    self.assertTrue(distance['zero_conditional_variance'])
                    self.assertIsNone(distance['observed_minus_expected_in_sd'])
                    if not distance['eligible_pairs']:
                        self.assertIsNone(distance['observed_rate'])
                        self.assertIsNone(distance['conditional_expected_rate'])

    def test_independent_loci_add_all_cross_distance_covariances(self):
        slots = ['a', 'a', 'b', None, 'b']
        one = module.distance_moments(slots)
        both = module.summarize([['second', slots], ['first', slots]])
        reversed_rows = module.summarize([['first', slots], ['second', slots]])
        self.assertEqual(both, reversed_rows)
        for i in range(4):
            self.assertEqual(Fraction(both['distances'][i]['conditional_expected_pairs_fraction']),
                             2 * one['expected'][i])
            for j in range(4):
                self.assertEqual(Fraction(both['conditional_covariance_fractions'][i][j]),
                                 2 * one['covariance'][i][j])

    def test_invalid_tokens_distances_and_duplicate_loci_fail(self):
        for slots in ('aab', ['', 'a'], [False], [1]):
            with self.subTest(slots=slots), self.assertRaises(ValueError):
                module.distance_moments(slots)
        for distances in ([], [0], [-1], [True], [1, 1], '1234'):
            with self.subTest(distances=distances), self.assertRaises(ValueError):
                module.distance_moments(['a', 'b'], distances)
        with self.assertRaisesRegex(ValueError, 'distinct nonempty locus keys'):
            module.summarize([['same', ['a']], ['same', ['b']]])

    def test_paired_cohort_and_uncertainty_policies_keep_source_specific_slots(self):
        header = '#=IVTFF Eva- 2.0 M\n<f1r>\n'
        left = parse_ivtff(header + '<f1r.1,@P0> a,[a:b].?.a\n<f1r.2,+P0> b.a\n')
        right = parse_ivtff(header + '<f1r.1,@P0> a.a.b.a\n<f1r.3,+P0> b.a\n')
        sources = [({'id': 'IT2a', 'url': 'urn:synthetic:IT', 'sha256': 'synthetic'}, right),
                   ({'id': 'ZL3b', 'url': 'urn:synthetic:ZL', 'sha256': 'synthetic'}, left)]
        report = module.distance_report(sources)
        self.assertEqual(report['selection']['count'], 1)
        self.assertEqual([source['id'] for source in report['sources']], ['ZL3b', 'IT2a'])
        variants = report['sources'][0]['variants']
        self.assertEqual([variant['retained_tokens'] for variant in variants], [2, 3, 1, 2])
        self.assertEqual([variant['apparent_token_slots'] for variant in variants], [4, 4, 3, 3])
        self.assertEqual(variants[0]['distances'][2]['observed_equal_pairs'], 1)
        self.assertEqual(variants[0]['distances'][0]['eligible_pairs'], 0)

    def test_cli_rejects_direct_symlink_and_hardlink_input_outputs_before_calculation(self):
        with tempfile.TemporaryDirectory(prefix='synthetic-distance-output-') as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            native = root / 'native.txt'
            native.write_bytes(b'Synthetic source only.\n')
            (root / 'data/transliterations.json').write_text(json.dumps({'sources': [{'path': 'native.txt'}]}))
            linked = root / 'linked.json'
            linked.symlink_to(native)
            hardlinked = root / 'hardlinked.json'
            os.link(native, hardlinked)
            for output in (native, linked, hardlinked, root / 'data/transliterations.json'):
                with self.subTest(output=output), patch.object(module, 'ROOT', root), \
                        patch.object(module, 'distance_report') as calculate, \
                        patch('sys.argv', ['distances', '--output', str(output)]), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as failed:
                    module.main()
                self.assertEqual(failed.exception.code, 1)
                calculate.assert_not_called()
                self.assertEqual(native.read_bytes(), b'Synthetic source only.\n')
            target = root / 'unrelated-report.json'
            with patch.object(module, 'ROOT', root), patch.object(module, 'distance_report', return_value={'synthetic': True}), \
                    patch('sys.argv', ['distances', '--output', str(target)]):
                module.main()
            self.assertEqual(json.loads(target.read_text()), {'synthetic': True})


if __name__ == '__main__':
    unittest.main()
