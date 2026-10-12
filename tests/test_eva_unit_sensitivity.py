"""Known segmentations and paired finite nulls check representation sensitivity."""

import copy
import json
from pathlib import Path
import unittest
from scripts import eva_unit_sensitivity as UNITS
from scripts import locus_position_baseline as ASCII


def settings():
    return json.loads(UNITS.SETTINGS.read_bytes())


NULL = {"seed": "synthetic-unit-test-v1", "replicates": 100}


class UnitTests(unittest.TestCase):
    def test_declared_case_and_bench_and_minim_counts(self):
        policies = settings()["policies"]
        token = "cKhaiin"
        pieces = [UNITS.segment(token, UNITS.ordered_patterns(policy["patterns"])) for policy in policies]
        self.assertEqual([len(row) for row in pieces], [7, 5, 3])
        self.assertEqual(pieces[2], ["cKh", "a", "iin"])
        self.assertTrue(all("".join(row) == token for row in pieces))
        bench = UNITS.ordered_patterns(policies[1]["patterns"])
        self.assertEqual(UNITS.segment("CTH", bench), ["C", "T", "H"])
        self.assertEqual(UNITS.segment("Ch", bench), ["Ch"])

    def test_longest_match_and_longer_unlisted_runs_are_explicit(self):
        patterns = UNITS.ordered_patterns(["ch", "chh"])
        self.assertEqual(UNITS.segment("chh", patterns), ["chh"])
        patterns = UNITS.ordered_patterns(settings()["policies"][2]["patterns"])
        self.assertEqual(UNITS.segment("iiiin", patterns), ["i", "iiin"])

    def test_boundaries_cannot_be_crossed_to_make_a_group(self):
        result = UNITS.measure({"a": ["c", "h"]}, "synthetic", "split", settings(), NULL)
        for policy in result["unit_policies"]:
            self.assertEqual(policy["scope_audit"]["encoded_token_count"], 2)
            self.assertEqual(policy["scope_audit"]["emitted_segment_count"], 2)
            self.assertEqual(policy["observed_equal_locus_mean_contrast"], 0)

    def test_grouped_policy_can_change_sign_or_remove_an_encoded_effect(self):
        result = UNITS.measure({"a": ["ch", "in"]}, "synthetic", "split", settings(), NULL)
        ascii_value, bench, combined = result["unit_policies"]
        self.assertEqual(ascii_value["observed_equal_locus_mean_contrast"], 0)
        self.assertEqual(bench["observed_equal_locus_mean_contrast"], -1)
        self.assertEqual(bench["exact_conditional_null_standard_deviation"], 1)
        self.assertEqual(combined["observed_equal_locus_mean_contrast"], 0)
        self.assertEqual(combined["exact_conditional_null_standard_deviation"], 0)

    def test_paired_change_uses_same_token_indices(self):
        result = UNITS.measure({"a": ["cKh", "iiin"]}, "synthetic", "split", settings(), NULL)
        ascii_value, bench, combined = result["unit_policies"]
        self.assertEqual(ascii_value["observed_equal_locus_mean_contrast"], -1)
        self.assertEqual(bench["observed_equal_locus_mean_contrast"], -3)
        self.assertEqual(bench["paired_change_from_ascii"]["observed_equal_locus_mean_contrast"], -2)
        self.assertEqual(bench["paired_change_from_ascii"]["exact_conditional_null_standard_deviation"], 2)
        self.assertEqual(combined["paired_change_from_ascii"]["exact_conditional_null_standard_deviation"], 1)
        for index in [1, 2]:
            grouped = result["unit_policies"][index]
            delta = grouped["paired_change_from_ascii"]["conditional_null_draws"]
            self.assertEqual(delta, [round(g-a, 12) for g, a in zip(
                grouped["conditional_null_draws"], ascii_value["conditional_null_draws"])])

    def test_ascii_control_matches_parent_helper_exactly(self):
        tokens = {"b": ["cKhaiin", "sh", "x"], "a": ["ch", "iiin"]}
        result = UNITS.measure(tokens, "synthetic", "split", settings(), NULL)["unit_policies"][0]
        original = ASCII.analyze_tokens(tokens, "synthetic", "split",
                                        replicates=NULL["replicates"], seed=NULL["seed"])
        for field in ["observed_equal_locus_mean_contrast", "exact_conditional_null_standard_deviation",
                      "empirical_null_mean", "empirical_null_interval", "conditional_null_draws"]:
            self.assertEqual(result[field], original[field])

    def test_pattern_order_does_not_change_result_after_compilation(self):
        left = settings()
        right = copy.deepcopy(left)
        for policy in right["policies"]:
            policy["patterns"].reverse()
        tokens = {"a": ["chiiin", "cKhaiin"]}
        self.assertEqual(UNITS.measure(tokens, "synthetic", "split", left, NULL),
                         UNITS.measure(tokens, "synthetic", "split", right, NULL))

    def test_unlisted_examples_and_uppercase_fallbacks_remain_visible(self):
        result = UNITS.measure({"a": ["cTHh", "Ao"]}, "synthetic", "split", settings(), NULL)
        audit = result["unit_policies"][1]["scope_audit"]
        self.assertEqual(audit["unlisted_example_substring_counts"]["cTHh"], 1)
        self.assertEqual(audit["unlisted_example_substring_counts"]["Ao"], 1)
        self.assertEqual(audit["uppercase_single_letter_fallback_counts"], {"A": 1, "H": 1, "T": 1})

    def test_invalid_patterns_and_nonplain_tokens_fail(self):
        for patterns in [["ch", "ch"], ["x"], [""], ["c?h"]]:
            with self.assertRaises(ValueError):
                UNITS.ordered_patterns(patterns)
        with self.assertRaises(ValueError):
            UNITS.segment("a?", ())


if __name__ == "__main__":
    unittest.main()
