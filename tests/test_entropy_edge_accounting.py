from collections import Counter
import itertools
import math
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
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

    def copied_fixture(self, directory):
        root = Path(directory) / "fixture"
        scripts = root / "scripts"
        scripts.mkdir(parents=True)
        original = Path(__file__).resolve().parents[1]
        for name in ("entropy_edge_accounting.py", "representation_entropy_demo.py"):
            shutil.copyfile(original / "scripts" / name, scripts / name)
        plan = root / "research/representation/ENTROPY_EDGES_PLAN.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("Invented temporary plan; no actual source or manuscript data")
        sources = root / "research/literature/entropy-methods.json"
        sources.parent.mkdir(parents=True)
        sources.write_text('{"synthetic": true}')
        return root, (plan, sources, scripts / "entropy_edge_accounting.py",
                      scripts / "representation_entropy_demo.py")

    def test_hardlink_outputs_are_rejected_and_both_paths_preserve_their_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root, protected = self.copied_fixture(directory)
            for index, source in enumerate(protected):
                alias = Path(directory) / f"output-alias-{index}.json"
                os.link(source, alias)
                before = source.read_bytes()
                result = subprocess.run([sys.executable, str(root / "scripts/entropy_edge_accounting.py"),
                                         "--output", str(alias)], cwd=root, capture_output=True, text=True)
                with self.subTest(source=source.name):
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn("must not overwrite", result.stderr)
                    self.assertEqual(source.read_bytes(), before)
                    self.assertEqual(alias.read_bytes(), before)

    def test_symlink_workspace_invocation_preserves_resolved_pin_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = self.copied_fixture(directory)
            alias = Path(directory) / "workspace-alias"
            alias.symlink_to(root, target_is_directory=True)
            direct, linked = root / "direct.json", root / "linked.json"
            for entry, output in ((root, direct), (alias, linked)):
                result = subprocess.run([sys.executable, str(entry / "scripts/entropy_edge_accounting.py"),
                                         "--output", str(output)], cwd=root, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(direct.read_bytes(), linked.read_bytes())


if __name__ == "__main__":
    unittest.main()
