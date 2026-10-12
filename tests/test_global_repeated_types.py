from fractions import Fraction
from itertools import permutations
import unittest

from scripts.global_repeated_types import (
    boundary_diagnostics, counts, exact_means, exact_record, ratio, whole_text_control,
)


class RepeatedTypeTests(unittest.TestCase):
    def test_types_and_overlapping_pair_events_are_different_units(self):
        self.assertEqual(counts(["a", "a", "a", "b", "b", "a", "a"])["equal_pair_events_A"], 4)
        self.assertEqual(counts(["a", "a", "a", "b", "b", "a", "a"])["distinct_repeating_types_B"], 2)
        self.assertEqual(counts(["a", "b", "a"])["equal_pair_events_A"], 0)

    def test_exact_means_match_exhaustive_distinct_multiset_permutations(self):
        cases = [[], ["a"], list("ab"), list("aab"), list("aaab"), list("aabb"),
                 list("aaabb"), list("aabbc"), list("aaabbc"), list("aaaabbc"), list("aaabbcc")]
        for tokens in cases:
            results = [counts(p) for p in set(permutations(tokens))]
            expected = exact_means(tokens)
            with self.subTest(tokens=tokens):
                self.assertEqual(expected["A"], Fraction(sum(r["equal_pair_events_A"] for r in results), len(results)))
                self.assertEqual(expected["B"], Fraction(sum(r["distinct_repeating_types_B"] for r in results), len(results)))

    def test_empty_unique_and_forced_repeat_boundaries(self):
        for tokens in ([], ["a"], list("abcd")):
            self.assertEqual(exact_means(tokens)["B"], 0)
        forced = exact_means(list("aaaab"))
        self.assertEqual(forced["B"], 1)
        self.assertEqual(forced["forced_repeating_types"], 1)
        self.assertIsNone(ratio(0, Fraction(0)))

    def test_case_and_bijective_type_relabeling_preserve_only_declared_identity(self):
        self.assertEqual(counts(["a", "A"])["distinct_repeating_types_B"], 0)
        tokens = list("aaabbc")
        mapping = {"a": "long", "b": "X", "c": "??"}
        renamed = [mapping[t] for t in tokens]
        self.assertEqual(counts(tokens), counts(renamed))
        self.assertEqual(exact_means(tokens), exact_means(renamed))

    def test_asterisk_diagnostics_do_not_change_the_metric(self):
        result = counts(["a*", "a*", "a*", "b", "b"])
        self.assertEqual(result, {"equal_pair_events_A": 3, "distinct_repeating_types_B": 2,
                                  "asterisk_bearing_pair_events": 2, "asterisk_bearing_repeating_types": 1})

    def test_joining_and_gap_diagnostics_reconcile_overlapping_type_sets(self):
        flat = [{"token": "a", "locator": "L1", "original_token_index": 0},
                {"token": "a", "locator": "L1", "original_token_index": 2},
                {"token": "a", "locator": "L2", "original_token_index": 0}]
        d = boundary_diagnostics(flat)
        self.assertEqual(d["within_record_pair_events"], 1)
        self.assertEqual(d["cross_record_pair_events"], 1)
        self.assertEqual(d["types_repeating_in_both_scopes"], 1)
        self.assertEqual(d["equal_pair_events_on_index_gap_edges"], 1)
        self.assertEqual(d["within_record_repeating_types"] + d["cross_record_repeating_types"]
                         - d["types_repeating_in_both_scopes"], 1)

    def test_control_replay_multiset_and_strict_seed_parameters(self):
        tokens = list("aabbccd")
        args = (tokens, "0" * 64, "exclude_R2", "M", 20261012, 0)
        one = whole_text_control(*args)
        self.assertEqual(one, whole_text_control(*args))
        self.assertCountEqual(one, tokens)
        with self.assertRaises(ValueError):
            whole_text_control(tokens, "0" * 64, "exclude_R2", "M", True, 0)

    def test_hex_rationals_round_trip_and_invalid_tokens_fail(self):
        value = Fraction(2 ** 16000 + 1, 2 ** 15999 + 3)
        record = exact_record(value)
        self.assertEqual(Fraction(int(record["numerator_hex"], 16), int(record["denominator_hex"], 16)), value)
        for tokens in ("text", [""], ["a b"], [None]):
            with self.subTest(tokens=tokens), self.assertRaises(ValueError):
                counts(tokens)


if __name__ == "__main__":
    unittest.main()
