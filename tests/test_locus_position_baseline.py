"""Known finite nulls and invariances check the statistic independently of data."""

import unittest
from scripts import locus_position_baseline as BASELINE


class PositionTests(unittest.TestCase):
    def analyze(self, records, replicates=100):
        return BASELINE.analyze_tokens(records, "synthetic", "split",
                                       replicates=replicates, seed="synthetic-test-v1")

    def test_two_token_locus_has_symmetric_exact_null(self):
        # First place can have length 3 or 1, giving contrasts +2 and -2.
        self.assertEqual(BASELINE.contrast([3, 1]), 2)
        self.assertEqual(BASELINE.contrast([1, 3]), -2)
        self.assertEqual(BASELINE.null_variance([3, 1]), 4)
        result = self.analyze({"a": ["aaa", "b"], "b": ["cc", "dd"]})
        self.assertEqual(result["observed_equal_locus_mean_contrast"], 1)
        self.assertEqual(result["exact_conditional_null_standard_deviation"], 1)
        self.assertEqual(result["empirical_null_interval"]["lower"], -1)
        self.assertEqual(result["empirical_null_interval"]["upper"], 1)

    def test_equal_lengths_have_zero_observation_and_zero_null(self):
        result = self.analyze({"a": ["ab", "cd", "ef"]})
        self.assertEqual(result["observed_equal_locus_mean_contrast"], 0)
        self.assertEqual(result["exact_conditional_null_standard_deviation"], 0)
        self.assertEqual(result["empirical_null_mean"], 0)
        self.assertFalse(result["observed_outside_conditional_null_interval"])

    def test_permutation_changes_observation_but_preserves_frequency_and_null_variance(self):
        left = self.analyze({"a": ["aaa", "b", "cc"]})
        right = self.analyze({"a": ["b", "cc", "aaa"]})
        self.assertNotEqual(left["observed_equal_locus_mean_contrast"],
                            right["observed_equal_locus_mean_contrast"])
        for key in ["encoded_token_count", "distinct_token_string_count", "hapax_token_string_count",
                    "ascii_length_histogram", "most_frequent_encoded_strings",
                    "exact_conditional_null_standard_deviation"]:
            self.assertEqual(left[key], right[key])

    def test_locus_weight_is_equal_despite_different_token_counts(self):
        # Contrasts are 2 and 0: their mean is 1, regardless of second-locus size.
        result = self.analyze({"short": ["aaa", "b"], "long": ["cc"] * 10})
        self.assertEqual(result["observed_equal_locus_mean_contrast"], 1)

    def test_input_order_does_not_change_deterministic_result(self):
        left = {"b": ["a", "bb", "ccc"], "a": ["dddd", "e"]}
        right = dict(reversed(list(left.items())))
        self.assertEqual(self.analyze(left), self.analyze(right))

    def test_counter_draws_are_repeatable_and_in_range(self):
        context = b"synthetic"
        first = [BASELINE.uniform_index(3, context, i) for i in range(100)]
        self.assertEqual(first, [BASELINE.uniform_index(3, context, i) for i in range(100)])
        self.assertEqual(set(first), {0, 1, 2})

    def test_quantile_is_linear_interpolation(self):
        self.assertEqual(BASELINE.quantile([0, 10], 0.25), 2.5)
        self.assertEqual(BASELINE.quantile([5], 0.975), 5)

    def test_counter_invalid_bounds_fail_instead_of_looping(self):
        with self.assertRaises(ValueError):
            BASELINE.uniform_index((1 << 256) + 1, b"synthetic", 0)
        with self.assertRaises(ValueError):
            BASELINE.uniform_index(3, b"synthetic", (1 << 128))

    def test_unsupported_units_and_empty_or_single_token_cohorts_fail(self):
        for records in [{}, {"a": ["x"]}, {"a": ["x", "?"]},
                        {"a": ["x", "é"]}, {"a": ["x", "{ch}"]}]:
            with self.subTest(records=records):
                with self.assertRaises(ValueError):
                    self.analyze(records)


if __name__ == "__main__":
    unittest.main()
