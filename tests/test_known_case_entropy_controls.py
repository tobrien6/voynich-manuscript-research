from collections import Counter
from fractions import Fraction
import math
import unittest

from scripts.known_case_entropy_controls import generate, report, scores


def independent_information(counts, target):
    groups = {}
    selected = 0
    for word, count in counts.items():
        if 'A' in word or target in word:
            selected += count
            groups.setdefault(word.replace('A', target), []).append(count)
    info = sum(sum(group) * math.log2(sum(group)) - sum(count * math.log2(count) for count in group)
               for group in groups.values())
    return info / selected, info / sum(counts.values())


class KnownCaseEntropyTests(unittest.TestCase):
    def test_generation_recovers_base_counts_under_the_declared_case_rule(self):
        for total, capitals in [(2, 1), (100, 99), (2, 0), (2, 2)]:
            base, observed = generate(total, capitals, 99, 99)
            recovered = Counter()
            for word, count in observed.items():
                recovered[word.lower()] += count
            self.assertEqual(recovered, Counter(base))
            self.assertEqual(sum(observed.values()), total + 198)

    def test_all_six_scores_match_an_independent_collision_information_formula(self):
        for total, capitals in [(2, 1), (100, 99)]:
            _, observed = generate(total, capitals, 99, 99)
            for target in ['a', 'b', 'x']:
                value = scores(observed, target)
                subset, whole = independent_information(observed, target)
                self.assertAlmostEqual(value['subset_decrease_bits'], subset, places=13)
                self.assertAlmostEqual(value['whole_decrease_bits'], whole, places=13)
                weight = Fraction(value['affected_occurrences'], value['all_occurrences'])
                self.assertAlmostEqual(value['whole_decrease_bits'], float(weight) * value['subset_decrease_bits'], places=13)

    def test_true_case_can_lose_under_either_declared_definition(self):
        result = report()
        self.assertEqual(result['source_symbol'].lower(), result['known_case_target'])
        balanced, skewed = result['cases']
        self.assertEqual(balanced['rankings'][0]['maximizers'], ['a'])
        self.assertEqual(balanced['rankings'][1]['maximizers'], ['b'])
        self.assertEqual(skewed['rankings'][0]['maximizers'], ['b'])
        self.assertEqual(skewed['rankings'][1]['maximizers'], ['b'])
        self.assertEqual([rank['known_case_target_is_maximizer'] for case in result['cases'] for rank in case['rankings']],
                         [True, False, False, False])

    def test_invalid_generation_parameters_fail(self):
        for values in [(True, 1, 99, 99), (2, -1, 99, 99), (2, 3, 99, 99), (0, 0, 99, 99), (2, 1, 0, 99)]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                generate(*values)


if __name__ == '__main__':
    unittest.main()
