from collections import Counter
import itertools
import math
from pathlib import Path
import subprocess
import sys
import unittest

from scripts.entropy_edge_accounting import count_entropy, edge_summary


class EntropyEdgeAccountingTests(unittest.TestCase):
    def test_two_units_distinguish_full_population_from_observed_successor(self):
        result = edge_summary("ab")
        self.assertEqual(result["unit_count"], 2)
        self.assertEqual(result["edge_count"], 1)
        self.assertEqual(result["bits"]["full_unit_entropy"], 1)
        self.assertEqual(result["bits"]["pair_minus_full_unit_entropy"], -1)
        self.assertEqual(result["bits"]["conditional_successor_entropy_on_edges"], 0)
        self.assertEqual(result["successor_mass_using_full_unit_denominator"], [
            {"unit": "a", "outgoing_count": 1, "full_count": 1, "row_mass": 1},
            {"unit": "b", "outgoing_count": 0, "full_count": 1, "row_mass": 0},
        ])

    def test_manual_branching_successors_and_endpoint_mass(self):
        result = edge_summary("aab")
        self.assertEqual(result["bits"]["conditional_successor_entropy_on_edges"], 1)
        self.assertAlmostEqual(result["bits"]["pair_minus_full_unit_entropy"],
                               1 + 2 / 3 * math.log2(2 / 3) + 1 / 3 * math.log2(1 / 3))
        result = edge_summary("abba")
        self.assertAlmostEqual(result["bits"]["conditional_successor_entropy_on_edges"], 2 / 3)
        rows = {row["unit"]: row for row in result["successor_mass_using_full_unit_denominator"]}
        self.assertEqual(rows["a"]["row_mass"], 0.5)
        self.assertEqual(rows["b"]["row_mass"], 1)

    def test_deterministic_successors_do_not_require_equal_marginal_populations(self):
        for sequence in ("aaaa", "aba", "abcabc"):
            with self.subTest(sequence=sequence):
                result = edge_summary(sequence)
                self.assertEqual(result["bits"]["conditional_successor_entropy_on_edges"], 0)
        self.assertGreater(edge_summary("aba")["bits"]["pair_minus_full_unit_entropy"], 0)
        self.assertLess(edge_summary("abcabc")["bits"]["pair_minus_full_unit_entropy"], 0)

    def test_exhaustive_binary_edges_match_independent_successor_distributions(self):
        for size in range(2, 8):
            for sequence in itertools.product("ab", repeat=size):
                by_left = {}
                for left, right in zip(sequence, sequence[1:]):
                    by_left.setdefault(left, []).append(right)
                expected = 0.0
                for successors in by_left.values():
                    counts = Counter(successors)
                    entropy = -sum(count / len(successors) * math.log2(count / len(successors))
                                   for count in counts.values())
                    expected += len(successors) / (size - 1) * entropy
                result = edge_summary(sequence)
                self.assertAlmostEqual(result["bits"]["conditional_successor_entropy_on_edges"], expected)
                self.assertGreaterEqual(result["bits"]["conditional_successor_entropy_on_edges"], 0)
                self.assertAlmostEqual(result["bits"]["pair_minus_full_unit_entropy"] - expected,
                                       result["bits"]["difference_from_using_full_marginal"])

    def test_atomic_labels_are_not_resegmented_and_inputs_remain_unchanged(self):
        original = ["ch", "x", "ch"]
        result = edge_summary(original)
        self.assertEqual(original, ["ch", "x", "ch"])
        self.assertEqual(result["unit_count"], 3)
        self.assertEqual(result["units"], original)
        self.assertEqual(result["bits"]["conditional_successor_entropy_on_edges"], 0)

    def test_undefined_and_invalid_count_populations_fail(self):
        for sequence in ("", "a", [], ["a", ""], [1, 2], None):
            with self.subTest(sequence=sequence), self.assertRaises(ValueError):
                edge_summary(sequence)
        for counts in ({}, {"a": 0}, {"a": -1}, {"a": True}, {"a": 0.5}):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                count_entropy(counts)

    def test_cli_cannot_overwrite_pinned_implementation_or_plan(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts/entropy_edge_accounting.py"
        for path in (script, root / "research/representation/ENTROPY_EDGES_PLAN.md"):
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(script), "--output", str(path)],
                                    cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not overwrite", result.stderr)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
