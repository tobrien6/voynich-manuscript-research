from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations, product
import unittest

from scripts.global_repeated_types import counts, exact_means
from scripts.record_conditioned_repeated_types import endpoint_matrix, exact_record_means, record_controls


class RecordConditionedRepeatTests(unittest.TestCase):
    def test_endpoint_matrices_match_all_small_occupancy_subsets(self):
        for m in range(1, 9):
            for c in range(m + 1):
                subsets = list(combinations(range(m), c))
                observed = Counter()
                for occupied in subsets:
                    if not any(b == a + 1 for a, b in zip(occupied, occupied[1:])):
                        observed[(int(0 in occupied), int(m - 1 in occupied))] += 1
                with self.subTest(m=m, c=c):
                    self.assertEqual(endpoint_matrix(m, c),
                                     tuple(tuple(Fraction(observed[(a, b)], len(subsets))
                                                 for b in (0, 1)) for a in (0, 1)))

    def test_full_edge_means_match_exhaustive_independent_record_permutations(self):
        cases = [[], [[]], [["a"]], [list("ab"), list("aab")],
                 [["a"], [], ["a"]], [list("aa"), list("ab")],
                 [list("aab"), list("bbc")], [list("aab"), list("a"), list("aba")],
                 [list("ab"), list("cc"), list("ab")], [list("aaab"), list("aabb")],
                 [list("ab"), list("ab"), list("ab"), list("ab")]]
        for rows in cases:
            samples = [counts([t for row in rs for t in row])
                       for rs in product(*(set(permutations(row)) for row in rows))]
            means = exact_record_means(rows)
            with self.subTest(rows=rows):
                for name, field in (("A", "equal_pair_events_A"), ("B", "distinct_repeating_types_B")):
                    self.assertEqual(means[name], Fraction(sum(s[field] for s in samples), len(samples)))
                self.assertEqual(means["A"], means["A_within_record"] + means["A_cross_record"])

    def test_empty_records_do_not_break_a_measured_join(self):
        result = exact_record_means([["a"], [], ["a"]])
        self.assertEqual(result["A_within_record"], 0)
        self.assertEqual(result["A_cross_record"], 1)
        self.assertEqual(result["B"], 1)
        self.assertEqual(result["forced_repeating_types"], 1)

    def test_absent_type_records_reset_run_endpoints(self):
        result = exact_record_means([["a"], ["b"], ["a"]])
        self.assertEqual(result["B"], 0)
        self.assertEqual(result["A_cross_record"], 0)

    def test_one_record_reduces_to_global_means_and_relabeling_preserves_them(self):
        for tokens in ([], list("ab"), list("aaabbcc"), list("aaaaabb")):
            actual = exact_record_means([tokens])
            expected = exact_means(tokens)
            self.assertEqual((actual["A"], actual["B"]), (expected["A"], expected["B"]))
        rows = [["a", "A", "a"], ["A", "A", "b*"]]
        renamed = [[{"a": "long", "A": "X", "b*": "Y"}[t] for t in row] for row in rows]
        self.assertEqual(exact_record_means(rows), exact_record_means(renamed))

    def test_controls_replay_and_preserve_each_record_with_empty_slots(self):
        rows = [list("aaabbc"), [], list("dde"), ["X*"]]
        args = (rows, ["r1", "r2", "r3", "r4"], "0" * 64, "exclude_R2", "M", 20261012, 0)
        actual = record_controls(*args)
        self.assertEqual(actual, record_controls(*args))
        self.assertEqual(rows, [list("aaabbc"), [], list("dde"), ["X*"]])
        for original, shuffled in zip(rows, actual):
            self.assertEqual(Counter(original), Counter(shuffled))
            self.assertEqual(len(original), len(shuffled))
        self.assertEqual(actual[1], [])
        other_trial = record_controls(*args[:-1], 1)
        self.assertNotEqual(actual, other_trial)

    def test_invalid_inputs_fail_before_control_sampling(self):
        for m, c in ((0, 0), (2, 3), (True, 1), (1, -1)):
            with self.assertRaises(ValueError):
                endpoint_matrix(m, c)
        for rows in ("ab", [[None]], [["a b"]]):
            with self.assertRaises(ValueError):
                exact_record_means(rows)
        args = ([["a"], ["b"]], ["r1", "r2"], "0" * 64, "exclude_R2", "M", 0, 0)
        for index, bad in ((1, ["r1", "r1"]), (2, "wrong"), (5, True), (6, -1)):
            altered = list(args)
            altered[index] = bad
            with self.assertRaises(ValueError):
                record_controls(*altered)


if __name__ == "__main__":
    unittest.main()
