from decimal import Decimal
from fractions import Fraction
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from scripts.native_substitution_normalizations import canonical_hash, decimal_score, factors, information_vector, load, native_counts, produce, ranking, signature


class NativeSubstitutionTests(unittest.TestCase):
    def test_balanced_classes_have_exact_known_prime_scores(self):
        self.assertEqual(information_vector([[1, 1]]), ((2, 2),))
        self.assertEqual(decimal_score(signature(((2, 2),), 2)), Decimal(1))
        self.assertEqual(decimal_score(signature(((2, 2),), 4)), Decimal('0.5'))
        self.assertEqual(information_vector([]), ())
        self.assertEqual(decimal_score(signature((), 3)), 0)

    def test_prime_expression_matches_direct_entropy_information(self):
        vector = information_vector([[1, 99], [2, 3, 7]])
        expected = sum(sum(counts) * math.log2(sum(counts)) - sum(count * math.log2(count) for count in counts)
                       for counts in [[1, 99], [2, 3, 7]]) / 200
        self.assertAlmostEqual(float(decimal_score(signature(vector, 200))), expected, places=13)
        for value in [1, 2, 12, 99, 100, 17597]:
            self.assertEqual(math.prod(prime ** power for prime, power in factors(value)), value)

    def test_exact_ties_survive_different_count_scale_and_preserve_all_candidates(self):
        left = information_vector([[1, 1]])
        right = information_vector([[2, 2]])
        self.assertEqual(signature(left, 2), signature(right, 4))
        result = ranking('A', [{'symbol': 'C', 'vector': right, 'denominator': 4},
                               {'symbol': 'B', 'vector': left, 'denominator': 2}], 'subset')
        self.assertEqual(result['positive_maximizers'], ['B', 'C'])
        self.assertEqual(result['status'], 'resolved_positive')

    def test_zero_maximum_is_not_assigned_as_a_positive_replacement(self):
        result = ranking('A', [{'symbol': 'B', 'vector': (), 'denominator': 2},
                               {'symbol': 'C', 'vector': (), 'denominator': 3}], 'subset')
        self.assertEqual(result['status'], 'no_positive_optimum')
        self.assertEqual(result['positive_maximizers'], [])
        self.assertEqual(result['possible_maximizers'], ['B', 'C'])

    def test_unequal_exact_scores_inside_fixed_numeric_guard_remain_unresolved(self):
        denominator = 10 ** 65
        result = ranking('A', [{'symbol': 'B', 'vector': ((2, denominator),), 'denominator': denominator},
                               {'symbol': 'C', 'vector': ((2, denominator + 1),), 'denominator': denominator}], 'whole')
        self.assertEqual(result['status'], 'numerically_unresolved')
        self.assertIsNone(result['positive_maximizers'])
        self.assertEqual(result['possible_maximizers'], ['B', 'C'])

    def test_invalid_integer_classes_or_input_pin_fail(self):
        for values in [[[1]], [[True, 1]], [[0, 1]]]:
            with self.assertRaises(ValueError):
                information_vector(values)
        for value in [0, True, -1]:
            with self.assertRaises(ValueError):
                factors(value)
        with self.assertRaisesRegex(ValueError, 'exact author-associated'):
            native_counts(b'changed corpus bytes')

    def test_dependency_drift_fails_before_input_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'scripts').mkdir()
            (root / 'scripts/substitution_entropy_control.py').write_bytes(b'changed dependency')
            source = Mock()
            with patch('scripts.native_substitution_normalizations.ROOT', root), \
                    self.assertRaisesRegex(ValueError, 'dependency drift'):
                produce(source)
            source.read_bytes.assert_not_called()

    def test_report_comparison_preserves_json_types_and_rejects_duplicates(self):
        self.assertNotEqual(canonical_hash({'count': 1}), canonical_hash({'count': True}))
        self.assertNotEqual(canonical_hash({'count': 1}), canonical_hash({'count': 1.0}))
        for raw in [b'{"count":1,"count":2}', b'{"count":NaN}']:
            with self.assertRaises(ValueError):
                load(raw)


if __name__ == '__main__':
    unittest.main()
