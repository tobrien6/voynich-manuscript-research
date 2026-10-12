from collections import Counter
from decimal import Decimal
from fractions import Fraction
from itertools import combinations_with_replacement, permutations, product
import unittest

from scripts.record_repeated_type_variance import exact_type_variance, joint_no_repeat, spread_diagnostics, two_type_endpoints


def exhaustive_moments(rows):
    values = []
    for shuffled in product(*(set(permutations(row)) for row in rows)):
        flat = [token for row in shuffled for token in row]
        values.append(len({a for a, b in zip(flat, flat[1:]) if a == b}))
    mean = Fraction(sum(values), len(values))
    variance = Fraction(sum(v * v for v in values), len(values)) - mean * mean
    return mean, variance


class RecordTypeVarianceTests(unittest.TestCase):
    def test_endpoint_matrices_match_all_three_category_strings_through_length_seven(self):
        for m in range(1, 8):
            denominators, endpoints = Counter(), Counter()
            for row in product(range(3), repeat=m):
                ca, cb = row.count(1), row.count(2)
                denominators[ca, cb] += 1
                if not any(a == b and a != 0 for a, b in zip(row, row[1:])):
                    endpoints[ca, cb, row[0], row[-1]] += 1
            for (ca, cb), denominator in denominators.items():
                with self.subTest(m=m, ca=ca, cb=cb):
                    expected = tuple(tuple(Fraction(endpoints[ca, cb, a, b], denominator) for b in range(3)) for a in range(3))
                    self.assertEqual(two_type_endpoints(m, ca, cb), expected)

    def test_global_mean_and_variance_match_all_7421_tiny_record_bag_configurations(self):
        bags = [bag for n in range(4) for bag in combinations_with_replacement("abc", n)]
        checked = 0
        for records in range(4):
            for rows in product(bags, repeat=records):
                if sum(map(len, rows)) > 8:
                    continue
                expected_mean, expected_variance = exhaustive_moments(rows)
                actual = exact_type_variance(rows)
                if (actual["mean_B"], actual["variance_B"]) != (expected_mean, expected_variance):
                    self.fail(f"moment mismatch for {rows}: {actual['mean_B']}, {actual['variance_B']}")
                self.assertEqual(actual["variance_B"], actual["marginal_variance_sum"] + actual["twice_covariance_adjustment"])
                self.assertEqual(actual["distinct_types"], actual["zero_repeat_probability_types"] +
                                 actual["forced_repeating_types"] + actual["variable_indicator_types"])
                checked += 1
        self.assertEqual(checked, 7421)

    def test_positive_negative_and_constant_indicator_covariance(self):
        positive = exact_type_variance([list("aabb")])
        self.assertEqual(positive["variance_B"], Fraction(2, 3))
        self.assertEqual(positive["positive_covariance_pairs"], 1)
        negative = exact_type_variance([list("ab"), list("ab")])
        self.assertEqual(negative["variance_B"], Fraction(1, 4))
        self.assertEqual(negative["type_pair_covariance_sum"], Fraction(-1, 16))
        self.assertEqual(negative["negative_covariance_pairs"], 1)
        fixed = exact_type_variance([["a"], [], ["a"]])
        self.assertEqual((fixed["mean_B"], fixed["variance_B"], fixed["forced_repeating_types"]), (1, 0, 1))
        self.assertEqual(fixed["variable_indicator_types"], 0)

    def test_disjoint_bag_domains_and_shared_inactive_runs_have_zero_covariance(self):
        disjoint = exact_type_variance([list("aax"), ["z"], list("bby")])
        self.assertEqual(disjoint["variable_pairs_sharing_records"], 0)
        self.assertEqual(disjoint["disjoint_record_variable_pairs"], 1)
        self.assertEqual(disjoint["type_pair_covariance_sum"], 0)
        rows = [list("aab"), ["z"], ["a"], list("bbc")]
        actual = exact_type_variance(rows)
        self.assertEqual(actual["variable_pairs_sharing_records"], 1)
        self.assertEqual(actual["zero_covariance_shared_pairs"], 1)
        self.assertEqual(actual["components_with_inactive_side_skipped"], 1)
        self.assertEqual((actual["mean_B"], actual["variance_B"]), exhaustive_moments(rows))

    def test_chained_overlap_components_and_empty_records_preserve_full_join_path(self):
        rows = [list("aab"), ["b"], list("abbc"), ["a"], list("abbc")]
        actual = exact_type_variance(rows)
        self.assertGreater(actual["joint_components_evaluated"], 0)
        self.assertEqual((actual["mean_B"], actual["variance_B"]), exhaustive_moments(rows))
        with_empty = [rows[0], [], *rows[1:]]
        self.assertEqual(actual, exact_type_variance(with_empty))
        # Adjacent singleton A records make a joining repeat certain, even when
        # the single-record kernels each have no internal edge.
        self.assertEqual(joint_no_repeat([(1, 1, 0), (1, 1, 0)]), 0)
        self.assertEqual(joint_no_repeat([(1, 1, 0), (1, 0, 1)]), 1)

    def test_case_and_bijective_type_relabeling_preserve_only_literal_identity(self):
        rows = [["a", "A"], ["a", "A"]]
        expected = exact_type_variance(rows)
        renamed = [[{"a": "opaque-long", "A": "X*"}[t] for t in row] for row in rows]
        self.assertEqual(expected, exact_type_variance(renamed))
        self.assertEqual(expected["distinct_types"], 2)

    def test_invalid_typed_counts_rows_and_joint_shapes_fail_without_cache_aliases(self):
        two_type_endpoints(1, 0, 1)
        for args in ((True, 0, 1), (1, False, True), (0, 0, 0), (3, 2, 2), (2, -1, 1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                two_type_endpoints(*args)
        for shape in ("bad", [(1, False, 1)], [(0, 0, 0)], [(1, 1, 1)], [(2, 1)]):
            with self.assertRaises(ValueError):
                joint_no_repeat(shape)
        for rows in ("text", [[None]], [["a b"]]):
            with self.assertRaises(ValueError):
                exact_type_variance(rows)

    def test_decimal_diagnostics_preserve_positive_underflow_and_undefined_constant_scale(self):
        tiny = spread_diagnostics(Fraction(1, 2 ** 16000), Fraction(1, 2 ** 8000))
        self.assertFalse(tiny["zero_conditional_variance"])
        self.assertIsNone(tiny["variance_approx"])
        self.assertIsNone(tiny["standard_deviation_approx"])
        self.assertGreater(Decimal(tiny["variance_decimal"]), 0)
        self.assertAlmostEqual(tiny["centered_B_in_conditional_SD_approx"], 1)
        fixed = spread_diagnostics(0, 0)
        self.assertTrue(fixed["zero_conditional_variance"])
        self.assertIsNone(fixed["centered_B_in_conditional_SD_decimal"])
        self.assertIsNone(fixed["centered_B_in_conditional_SD_approx"])
        for args in ((-1, 0), (0, 1), (1, 0, True)):
            with self.assertRaises(ValueError):
                spread_diagnostics(*args)


if __name__ == "__main__":
    unittest.main()
