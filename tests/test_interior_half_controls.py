from collections import Counter
import copy
from fractions import Fraction
import hashlib
import itertools
from pathlib import Path
import subprocess
import sys
import unittest

from scripts import interior_length_order as parent
from scripts.interior_half_controls import (
    exact_centered_score, exact_half_expectation, halves, summarize,
    control_rows, verify_parent,
)


def permitted_permutations(values):
    early, late = halves(values)
    return [list(a + b) for a in itertools.permutations(early)
            for b in itertools.permutations(late)]


class HalfPositionControlsTests(unittest.TestCase):
    def test_exact_expectation_under_permitted_permutations(self):
        for values in ([1, 3, 2], [1, 2, 3], [1, 2, 3, 4],
                       [1, 1, 3, 4, 4], [1, 2, 4, 5, 6, 7], [4, 4, 4]):
            controls = permitted_permutations(values)
            mean = sum((exact_centered_score(x) for x in controls), Fraction()) / len(controls)
            self.assertEqual(mean, 0)
            m, squared, _ = parent.components(values)
            actual = sum((Fraction(m * parent.components(x)[2], (m - 1) * squared)
                          if squared else Fraction(0) for x in controls), Fraction()) / len(controls)
            self.assertEqual(exact_half_expectation(values), actual)

    def test_unpermutable_and_other_degenerate_cases_are_zero(self):
        for values in ([1, 1, 4, 4], [2, 2, 2], [1, 3, 2]):
            for permuted in permitted_permutations(values):
                self.assertEqual(exact_centered_score(permuted), 0)
        # This nonconstant-half example is intentionally not counted by the
        # narrower both-half-constant counter in the report.
        self.assertFalse(all(len(set(b)) == 1 for b in halves([1, 3, 2])))

    def test_odd_even_and_singleton_split(self):
        self.assertEqual(halves([1, 2, 3]), ([1, 2], [3]))
        self.assertEqual(halves([1, 2, 3, 4]), ([1, 2], [3, 4]))
        self.assertEqual(halves([1, 2, 3, 4, 5]), ([1, 2, 3], [4, 5]))
        with self.assertRaises(ValueError):
            halves([1, 2])

    def test_controls_preserve_halves_identities_and_fixed_endpoints(self):
        tokens = ["q" * 100, "a", "bb", "ccc", "dddd", "eeeee", "y" * 200]
        rows = [("f67r1", "f67r1.1", parent.interior_lengths(tokens))]
        digest = hashlib.sha256(parent.compact(rows)).hexdigest()
        for trial in range(10):
            controlled = control_rows(rows, digest, 17, trial)
            self.assertEqual(controlled[0][:2], rows[0][:2])
            for a, b in zip(halves(rows[0][2]), halves(controlled[0][2])):
                self.assertEqual(Counter(a), Counter(b))
        self.assertEqual(tokens[0], "q" * 100)
        self.assertEqual(tokens[-1], "y" * 200)
        self.assertEqual(rows[0][2], [1, 2, 3, 4, 5])
        self.assertEqual(control_rows(rows, digest, 17, 2), control_rows(rows, digest, 17, 2))

    def test_half_moments_remain_invariant(self):
        rows = [("f1r", "f1r.1", [1, 2, 3, 7, 8, 9])]
        digest = hashlib.sha256(parent.compact(rows)).hexdigest()
        expectation = exact_half_expectation(rows[0][2])
        for trial in range(10):
            self.assertEqual(exact_half_expectation(control_rows(rows, digest, 1, trial)[0][2]), expectation)

    def test_parent_guard_rejects_changed_source_keys_lengths_or_observation(self):
        rows = [("f1r", "f1r.1", [1, 2, 3, 4])]
        original = {"source_id": "fixture", "source_sha256": "a" * 64, "spacing": "split",
                    "loci": 1, "length_corpus_sha256": hashlib.sha256(parent.compact(rows)).hexdigest(),
                    "interior_tokens": 4, "interior_adjacent_pairs": 3, "constant_interior_loci": 0,
                    "source_page_ids": 1, "mean_centered_association": parent.mean_score(rows),
                    "exact_uncentered_null_expectation": -1 / 3}
        source = {"id": "fixture", "sha256": "a" * 64}
        verify_parent(original, source, "split", rows)
        for field in ("source_sha256", "loci", "length_corpus_sha256", "mean_centered_association"):
            changed = copy.deepcopy(original)
            changed[field] = "changed" if isinstance(changed[field], str) else changed[field] + 1
            with self.assertRaises(ValueError):
                verify_parent(changed, source, "split", rows)
        with self.assertRaises(ValueError):
            verify_parent(original, source, "split", [("f1r", "f1r.2", [1, 2, 3, 4])])
        with self.assertRaises(ValueError):
            verify_parent(original, source, "split", [("f1r", "f1r.1", [1, 2, 3, 5])])

    def test_equal_locus_weight_and_all_trial_tail(self):
        rows = [("f1r", "f1r.1", [1, 4, 2, 3, 5]), ("f1r", "f1r.2", [1] * 20)]
        result = summarize(rows, repetitions=19, seed=3)
        self.assertAlmostEqual(result["half_centered_association"], float(exact_centered_score(rows[0][2])) / 2)
        self.assertEqual(result["constant_interior_loci"], 1)
        self.assertEqual(result["both_half_constant_loci"], 1)
        self.assertEqual(len(result["control_statistics"]), 19)
        count = sum(abs(x) >= abs(result["half_centered_association"]) - 1e-12 for x in result["control_statistics"])
        self.assertEqual(result["exploratory_two_sided_tail"], (1 + count) / 20)
        self.assertAlmostEqual(result["half_centered_association"], result["unrestricted_centered_association"]
                               - result["half_minus_unrestricted_expectation"])

    def test_full_cohort_denominator_keeps_unpermutable_rows(self):
        result = summarize([("f1r", "f1r.1", [1, 1, 4, 4]), ("f1r", "f1r.2", [2] * 3)], 9, 1)
        self.assertEqual(result["loci"], 2)
        self.assertAlmostEqual(result["half_centered_association"], 0)
        self.assertEqual(result["exploratory_two_sided_tail"], 1)
        self.assertEqual(result["both_half_constant_loci"], 2)

    def test_cli_protects_parent_and_raw_sources(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("research/transliteration/interior_length_order.json", "data/raw/ZL3b-n.txt"):
            path = root / name
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(root / "scripts/interior_half_controls.py"),
                                     "--output", str(path)], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not overwrite", result.stderr)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
