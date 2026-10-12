import contextlib
from decimal import localcontext
from fractions import Fraction
import gzip
import hashlib
import importlib
import io
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import independent_position_length as m


def references():
    settings = json.loads((m.ROOT / m.SETTINGS).read_text())
    for name, wanted in settings['reference_sha256'].items():
        if hashlib.sha256((m.ROOT / name).read_bytes()).hexdigest() != wanted:
            raise ValueError('active reference differs before import')
    return (importlib.import_module('scripts.interior_length_order'),
            importlib.import_module('scripts.interior_half_controls'))


class IndependentPositionTests(unittest.TestCase):
    def test_local_scores_match_pinned_accepted_methods(self):
        full, half = references()
        for vector in ([1, 4, 3], [1, 1, 2, 3], [7, 3, 4, 1, 2], [1, 4, 2, 2, 3, 5], [4, 4, 4, 4]):
            result = m.score(vector)
            self.assertEqual(sum(result['unrestricted_centered']), full.exact_score(vector))
            self.assertEqual(sum(result['half_centered']), half.exact_centered_score(vector))
            self.assertEqual(sum(result['half_expectation']), half.exact_half_expectation(vector))

    def test_component_expectations_against_complete_local_occurrence_permutations(self):
        for vector in ([1, 4, 3], [1, 1, 2, 3], [7, 3, 4, 1, 2], [1, 4, 2, 2, 3, 5], [4, 4, 4, 4]):
            reference = m.score(vector)
            cut = (len(vector) + 1) // 2
            for scope, population in (
                ('unrestricted', itertools.permutations(vector)),
                ('half', (a + b for a, b in itertools.product(
                    itertools.permutations(vector[:cut]), itertools.permutations(vector[cut:]))))):
                records = [m.score(order) for order in population]
                means = [sum((r['raw'][i] for r in records), Fraction()) / len(records) for i in range(3)]
                self.assertEqual(means, reference[scope + '_expectation'])

    def test_constant_singleton_and_affine_cases_keep_exact_zero_components(self):
        zero = m.score([2, 2, 2])
        self.assertTrue(zero['constant'])
        for field in m.FIELDS:
            self.assertEqual(zero[field], [0, 0, 0])
        vector = [1, 3, 2]
        original = m.score(vector)
        self.assertEqual(original['half_centered'][2], 0)
        self.assertEqual(m.score([7 * x + 2 for x in vector]), original)
        self.assertEqual(m.score([30 - x for x in vector]), original)

    def test_family_laws_and_direction_pairing_on_single_local_outcomes(self):
        self.assertEqual(m.values('flat', 3, [1, 0, 1]), [3, 2, 3])
        self.assertEqual(m.values('half_step', 3, [1, 0, 1]), [3, 2, 6])
        self.assertEqual(m.values('increasing', 3, [1, 0, 1]), [3, 3, 5])
        self.assertEqual(m.values('decreasing', 3, [1, 0, 1]), [5, 3, 3])
        bits = [1, 0, 1, 0, 0, 1, 1]
        left = m.values('decreasing', 7, bits)
        right = m.values('increasing', 7, [1 - b for b in bits])
        self.assertEqual(left, [11 - x for x in right])
        self.assertEqual(m.score(left), m.score(right))

    def test_generic_population_covariance_uses_slot_means(self):
        means, covariance = m.population_counts([[1, 2], [1, 4], [3, 2], [3, 4]])
        self.assertEqual(means, [2, 3])
        self.assertEqual(covariance, [[1, 0], [0, 1]])
        for rows in ([], [[]], [[1], [1, 2]], [[True]], [[1.]]):
            with self.assertRaises(ValueError):
                m.population_counts(rows)

    def test_invalid_counts_noise_sizes_and_family_names_are_refused(self):
        for vector in (None, '123', [], [1, 2], [1, True, 2], [1, 2., 3], [1, 0, 3]):
            with self.assertRaises(ValueError):
                m.score(vector)
        for family, size, bits in (('unknown', 3, [0, 0, 0]), ('flat', 2, [0, 0]),
                                  ('flat', 3., [0, 0, 0]), ('flat', 3, [0, 0]),
                                  ('flat', 3, [0, True, 0]), ('flat', 3, [0, 2, 0]), ('flat', 3, None)):
            with self.assertRaises(ValueError):
                m.values(family, size, bits)

    def test_fixed_primary_rule_retains_zero_negative_and_positive_outcomes(self):
        for values, expected in (([1, -3, 1], False), ([1, 1, 0], False), ([1, -1, 1], True)):
            result = m.summarize_primary({'family': 'invented', 'size': 8,
                                        'ensemble_components': {'half_centered': [m.large(Fraction(v)) for v in values]}})
            self.assertEqual(result['all_fixed_counterexample_predictions_pass'], expected)

    def test_changed_pin_blocks_enumeration(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / m.PLAN
            path.parent.mkdir(parents=True)
            path.write_text('changed')
            with patch.object(m, 'ROOT', root), patch.object(m, 'ensemble') as ensemble, \
                    self.assertRaisesRegex(ValueError, 'input changed'):
                m.report()
            ensemble.assert_not_called()

    def test_historical_reference_drift_is_checked_without_import_or_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / m.SETTINGS
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'reference_commit': 'historical', 'reference_sha256': {'score.py': m.PINS[m.PLAN]}}))
            with patch.object(m, 'ROOT', root), patch.object(m, 'PINS', {m.SETTINGS: hashlib.sha256(path.read_bytes()).hexdigest()}), \
                    patch.object(m.subprocess, 'check_output', return_value=b'changed') as read, \
                    self.assertRaisesRegex(ValueError, 'historical score reference changed'):
                m.inputs()
            read.assert_called_once_with(['git', 'show', 'historical:score.py'], cwd=root)

    def test_initial_direct_symbolic_hard_and_directory_redirect_aliases(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / m.PLAN
            path.parent.mkdir(parents=True)
            path.write_text('preserve')
            symbolic = root / 'symbolic'
            symbolic.symlink_to(path)
            hard = root / 'hard'
            hard.hardlink_to(path)
            redirect = root / 'redirect'
            redirect.symlink_to(path.parent, target_is_directory=True)
            with patch.object(m, 'ROOT', root):
                for target in (path, symbolic, hard, redirect / path.name, root / 'data' / 'new.json', Path(m.__file__)):
                    with self.assertRaises(ValueError):
                        m.protect_output(target)
                m.protect_output(root / 'new.json')

    def test_existing_and_late_unlisted_source_aliases_are_refused_exclusively(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'data' / 'source.txt'
            source.parent.mkdir()
            source.write_text('preserve')
            output = root / 'output.json'
            output.hardlink_to(source)
            with patch.object(m, 'ROOT', root), patch.object(m, 'report') as calculate, \
                    patch('sys.argv', ['position', '--new-report', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                m.main()
            calculate.assert_not_called()
            output.unlink()
            def serialize(_, compressed=False):
                output.hardlink_to(source)
                return b'{}\n'
            with patch.object(m, 'ROOT', root), patch.object(m, 'report', return_value={}), \
                    patch.object(m, 'serialize', side_effect=serialize), patch('sys.argv', ['position', '--new-report', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                m.main()
            self.assertEqual(source.read_text(), 'preserve')

    def test_lossless_compression_and_exact_byte_check_do_not_mask_scalar_types(self):
        raw = m.serialize({'flag': False, 'count': 0})
        zipped = m.serialize({'flag': False, 'count': 0}, compressed=True)
        self.assertEqual(gzip.decompress(zipped), raw)
        self.assertEqual(zipped[4:8], bytes(4))
        self.assertFalse(zipped[3] & 8)
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'output.json.gz'
            output.write_bytes(m.serialize({'count': False}, compressed=True))
            with patch.object(m, 'protect_output'), patch.object(m, 'report', return_value={'count': 0}), \
                    patch('sys.argv', ['position', '--check', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                m.main()

    def test_large_aggregate_encoding_preserves_global_numeric_contexts(self):
        before = sys.get_int_max_str_digits()
        value = Fraction(10 ** 9000 + 1, 10 ** 9001 + 3)
        with localcontext() as context:
            context.prec = 2
            record = m.large(value)
            self.assertEqual(m.decode(record), value)
            self.assertEqual(context.prec, 2)
            self.assertEqual(json.loads(m.serialize(record)), record)
        self.assertEqual(sys.get_int_max_str_digits(), before)


if __name__ == '__main__':
    unittest.main()
