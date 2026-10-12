from collections import Counter
from fractions import Fraction
import hashlib
import itertools
from pathlib import Path
import subprocess
import sys
import unittest

from scripts.interior_length_order import (
    compact, control_rows, exact_score, interior_lengths, mean_score, prepare,
    score, summarize, uncentered_expectation,
)
from scripts.ivtff import parse_ivtff


class InteriorLengthOrderTests(unittest.TestCase):
    def test_exact_expectation_over_all_distinguishable_permutations(self):
        for values in ([1, 2, 3], [1, 1, 2, 3], [2, 4, 5, 8, 9], [4, 4, 4]):
            permutations = list(itertools.permutations(values))
            expectation = sum((exact_score(p) for p in permutations), Fraction()) / len(permutations)
            self.assertEqual(expectation, 0)
            self.assertAlmostEqual(
                sum(score(p) for p in permutations) / len(permutations), 0, places=14)

    def test_without_replacement_correction_and_constant_case(self):
        self.assertEqual(uncentered_expectation([1, 2, 3]), -0.5)
        self.assertEqual(uncentered_expectation([1, 1, 1]), 0)
        self.assertEqual(score([1, 1, 1]), 0)
        self.assertEqual(exact_score([1, 1, 1]), Fraction(0))

    def test_endpoint_strings_do_not_supply_interior_pairs(self):
        original = ["a", "bc", "def", "ghij", "k"]
        changed = ["x" * 100, "bc", "def", "ghij", "y" * 200]
        self.assertEqual(interior_lengths(original), [2, 3, 4])
        self.assertEqual(interior_lengths(original), interior_lengths(changed))

    def test_equal_locus_weighting_and_fixed_constant_denominator(self):
        rows = [("f1r", "f1r.1", [1, 2, 3]), ("f1r", "f1r.2", [1] * 20)]
        self.assertEqual(mean_score(rows), score([1, 2, 3]) / 2)
        with self.assertRaises(ValueError):
            mean_score([])

    def test_deterministic_controls_preserve_every_locus_multiset(self):
        rows = [("f67r1", "f67r1.1", [1, 1, 2, 4]),
                ("fRos", "fRos.1", [1, 5, 6, 9, 2]),
                ("f1r", "f1r.1", [2, 2, 2])]
        digest = hashlib.sha256(compact(rows)).hexdigest()
        result = control_rows(rows, digest, 17, 3)
        self.assertEqual(result, control_rows(rows, digest, 17, 3))
        self.assertEqual(result[0][2], [2, 1, 4, 1])
        for original, control in zip(rows, result):
            self.assertEqual(original[:2], control[:2])
            self.assertEqual(Counter(original[2]), Counter(control[2]))
        self.assertEqual(rows[0][2], [1, 1, 2, 4])

    def test_invalid_statistic_inputs_fail(self):
        for values in ([1, 2], [1, 0, 2], [1, True, 2], [1, 2.5, 3]):
            with self.assertRaises(ValueError):
                score(values)
        for tokens in (["a", "b", "c"], ["a", "b", "é", "d", "e"],
                       ["a", "b", "?", "d", "e"]):
            with self.assertRaises(ValueError):
                interior_lengths(tokens)

    def fixture_sources(self):
        common = ("<f1r.1,@P0> a.bb.ccc.dddd.e\n"
                  "<f1r.2,+P0> a.bb,[c:dd].ee.f\n"
                  "<f1r.3,+P0> a.bb<->ccc.dddd.e\n"
                  "<f1r.4,+P0> a.bb,cc.dd.e\n"
                  "<f1r.5,+P1> a.bb.ccc.dddd.e\n"
                  "<f1r.6,!P0> a.bb.ccc.dddd.e\n"
                  "<f1r.7,+P0> a.bb.ccc.dddd.e\n")
        return [({"id": source_id}, parse_ivtff(
            f"#=IVTFF {alphabet} 2.0 M\n<f1r>\n" + common + extra))
            for source_id, alphabet, extra in (
                ("ZL3b", "Eva-", "<f1r.8,+P0> a.bb.ccc.dddd.e\n"),
                ("IT2a", "EvaT", ""))]

    def test_common_cohort_excludes_ambiguity_drawing_short_and_wrong_kind(self):
        treatments, accepted, selection = prepare(self.fixture_sources())
        self.assertEqual(accepted, ["f1r.1", "f1r.7"])
        self.assertEqual(selection["shared_present_P0_loci"], 5)
        self.assertEqual(selection["eligible_in_all_adapters"], 4)
        self.assertEqual(selection["eligible_after_drawing_exclusion"], 3)
        self.assertEqual(selection["eligible_after_minimum_token_exclusion"], 2)
        self.assertEqual(len(treatments), 4)
        excluded = {r["locus_key"]: r["reasons"] for r in selection["exclusions"]}
        self.assertIn("ZL3b/split:alternative_reading", excluded["f1r.2"])
        self.assertIn("ZL3b/join:drawing_interruption", excluded["f1r.3"])
        self.assertIn("ZL3b/join:fewer_than_five_tokens", excluded["f1r.4"])

    def test_unrelated_alphabets_cannot_expand_or_change_the_paired_cohort(self):
        sources = self.fixture_sources()
        expected = prepare(sources)
        extra = ({"id": "GC-fixture"}, parse_ivtff(
            "#=IVTFF v101 2.0 M\n<f1r>\n<f1r.1,@P0> x\n"))
        self.assertEqual(prepare(sources + [extra]), expected)

    def test_cli_rejects_source_overwrite_before_computing(self):
        root = Path(__file__).resolve().parents[1]
        source = root / "data/raw/ZL3b-n.txt"
        before = source.read_bytes()
        result = subprocess.run(
            [sys.executable, str(root / "scripts/interior_length_order.py"),
             "--output", str(source)], cwd=root,
            capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must not overwrite a pinned source", result.stderr)
        self.assertEqual(source.read_bytes(), before)

    def test_report_tail_uses_all_trials_and_preserves_identical_inputs(self):
        treatments, accepted, _ = prepare(self.fixture_sources())
        a = summarize(treatments[("ZL3b", "split")], accepted, 9, 10)
        b = summarize(treatments[("IT2a", "join")], accepted, 9, 10)
        self.assertEqual(a, b)
        self.assertEqual(len(a["control_statistics"]), 9)
        tail_count = sum(abs(x) >= abs(a["mean_centered_association"]) - 1e-12
                         for x in a["control_statistics"])
        self.assertEqual(a["exploratory_two_sided_tail"], (1 + tail_count) / 10)
        self.assertEqual(a["loci"], 2)
        self.assertEqual(a["interior_adjacent_pairs"], 4)
        with self.assertRaises(ValueError):
            summarize(treatments[("ZL3b", "split")], accepted, 0, 10)


if __name__ == "__main__":
    unittest.main()
