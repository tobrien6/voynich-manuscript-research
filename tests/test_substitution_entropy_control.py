from collections import Counter
from fractions import Fraction
import math
import unittest

from scripts.substitution_entropy_control import TOY_COUNTS, measure, report


def direct_entropy(counts):
    total = sum(counts.values())
    return sum(-(count / total) * math.log2(count / total) for count in counts.values())


class SubstitutionEntropyControlTests(unittest.TestCase):
    def test_balanced_merge_has_known_conditional_and_whole_scores(self):
        result = measure({'ax': 1, 'bx': 1, 'z': 2}, 'a', 'b')
        self.assertEqual(result['subset_entropy_decrease_bits'], 1)
        self.assertEqual(result['whole_entropy_decrease_bits'], 0.5)
        self.assertEqual(result['selected_mass_fraction'], {'numerator': '1', 'denominator': '2'})

    def test_no_type_collision_preserves_entropy_exactly(self):
        result = measure({'ac': 3, 'bd': 2, 'z': 4}, 'a', 'b')
        self.assertEqual(result['collision_classes'], [])
        self.assertEqual(result['subset_entropy_decrease_bits'], 0)
        self.assertEqual(result['whole_entropy_decrease_bits'], 0)
        self.assertEqual(result['all_types_before'], result['all_types_after'])

    def test_simultaneous_all_occurrence_merge_is_symmetric_and_mass_weighted(self):
        counts = {'ab': 1, 'ba': 2, 'aa': 3, 'bb': 4, 'none': 5}
        forward = measure(counts, 'a', 'b')
        backward = measure(counts, 'b', 'a')
        self.assertAlmostEqual(forward['whole_entropy_decrease_bits'], backward['whole_entropy_decrease_bits'])
        self.assertEqual(forward['selected_occurrences'], 10)
        self.assertEqual(forward['selected_types_after'], 1)
        self.assertAlmostEqual(forward['whole_entropy_decrease_bits'],
                               (10 / 15) * forward['subset_entropy_decrease_bits'])

    def test_complete_toy_score_reversal_matches_direct_entropy_and_exact_mass(self):
        results = [measure(TOY_COUNTS, 'A', target) for target in ['B', 'C']]
        for result in results:
            target = result['target']
            transformed = Counter()
            for word, frequency in TOY_COUNTS.items():
                transformed[word.replace('A', target)] += frequency
            selected = {word: frequency for word, frequency in TOY_COUNTS.items() if 'A' in word or target in word}
            merged_selected = Counter()
            for word, frequency in selected.items():
                merged_selected[word.replace('A', target)] += frequency
            self.assertAlmostEqual(result['whole_entropy_decrease_bits'],
                                   direct_entropy(TOY_COUNTS) - direct_entropy(transformed), places=13)
            self.assertAlmostEqual(result['subset_entropy_decrease_bits'],
                                   direct_entropy(selected) - direct_entropy(merged_selected), places=13)
            fraction = result['selected_mass_fraction']
            weight = Fraction(int(fraction['numerator']), int(fraction['denominator']))
            self.assertAlmostEqual(result['whole_entropy_decrease_bits'],
                                   float(weight) * result['subset_entropy_decrease_bits'], places=13)
        self.assertEqual(report()['largest_subset_decrease_target'], 'B')
        self.assertEqual(report()['largest_whole_decrease_target'], 'C')

    def test_invalid_count_or_mapping_is_rejected(self):
        for counts, source, target in [({}, 'a', 'b'), ({'a': True}, 'a', 'b'),
                                       ({'a': 0}, 'a', 'b'), ({'a': 1}, 'a', 'a'),
                                       ({'a': 1}, 'ab', 'b'), ({'z': 1}, 'a', 'b')]:
            with self.subTest(counts=counts, source=source, target=target), self.assertRaises(ValueError):
                measure(counts, source, target)


if __name__ == '__main__':
    unittest.main()
