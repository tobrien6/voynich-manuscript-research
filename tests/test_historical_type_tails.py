import contextlib
from fractions import Fraction
import hashlib
import io
from itertools import product
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import historical_type_tails as module
from scripts import historical_repeated_types as global_parent
from scripts.reconstruct_historical_tokens import encoded


def fraction(record):
    return Fraction(int(record["numerator_hex"], 16), int(record["denominator_hex"], 16))


def fixture(rows):
    records = [{"locator": f"fixture{i};H", "tokens": row, "original_token_indices": list(range(len(row))),
                "exclusion_reasons": []} for i, row in enumerate(rows)]
    flat = [{"token": token, "locator": row["locator"], "original_token_index": i}
            for row in records for i, token in enumerate(row["tokens"])]
    summary = {"ring_policy": "exclude_R2", "f66r_column_unit": "M",
               "record_corpus_sha256": hashlib.sha256(encoded(records)).hexdigest(),
               "flat_corpus_sha256": hashlib.sha256(encoded(flat)).hexdigest()}
    corpus = {"records": records, "flat_tokens_with_provenance": flat}
    g = global_parent.assay_variant(summary, corpus, {"seed": 0, "trials": 10})
    reference = module.parent.assay_variant(summary, corpus, g, {"seed": 0, "trials": 10})
    plan = {"seed": 0, "new_trials": 4, "first_new_trial": 10, "last_new_trial": 13, "decimal_precision": 50}
    return summary, corpus, reference, plan


class HistoricalTypeTailTests(unittest.TestCase):
    def test_inclusive_ties_two_tail_rules_and_plus_one_are_distinct(self):
        result = module.tail_summary(3, Fraction(2), [0, 1, 2, 3, 4, 4])
        self.assertEqual(result["upper_tail"]["inclusive_exceedances"], 3)
        self.assertEqual(result["upper_tail"]["ties_at_observed_score"], 1)
        self.assertEqual(result["centered_two_sided"]["inclusive_exceedances"], 5)
        self.assertEqual(result["centered_two_sided"]["ties_at_observed_score"], 2)
        self.assertEqual(fraction(result["upper_tail"]["raw_frequency"]), Fraction(1, 2))
        self.assertEqual(fraction(result["upper_tail"]["plus_one_rank_score"]), Fraction(4, 7))
        self.assertEqual(fraction(result["centered_two_sided"]["plus_one_rank_score"]), Fraction(6, 7))

    def test_exact_fractional_center_prevents_false_rounded_ties(self):
        mean = Fraction(2 ** 16000 - 1, 2 ** 16001)
        self.assertEqual(float(mean), .5)
        result = module.tail_summary(1, mean, [0, 1])
        self.assertEqual(result["centered_two_sided"]["inclusive_exceedances"], 1)
        self.assertEqual(result["centered_two_sided"]["ties_at_observed_score"], 1)
        self.assertEqual(fraction(result["exact_parent_mean_B"]), mean)

    def test_zero_exceedances_constant_controls_and_single_sample_are_retained(self):
        zero = module.tail_summary(9, Fraction(0), [0, 0, 0])
        for name in ("upper_tail", "centered_two_sided"):
            self.assertEqual(zero[name]["inclusive_exceedances"], 0)
            self.assertEqual(fraction(zero[name]["plus_one_rank_score"]), Fraction(1, 4))
        fixed = module.tail_summary(1, Fraction(1), [1, 1, 1])
        self.assertEqual(fixed["B_histogram"], {"1": 3})
        self.assertEqual(fraction(fixed["new_unbiased_sample_variance_B"]), 0)
        self.assertEqual(fraction(fixed["centered_two_sided"]["plus_one_rank_score"]), 1)
        self.assertIsNone(module.tail_summary(1, Fraction(1), [1])["new_unbiased_sample_variance_B"])

    def test_plus_one_scores_are_conservative_on_exhaustive_ideal_iid_nulls_with_ties(self):
        for distribution in ([0, 1, 1, 2], [0, 0, 1], [1]):
            mean = Fraction(sum(distribution), len(distribution))
            for trials in (1, 2, 3):
                summaries = [module.tail_summary(outcome[0], mean, outcome[1:])
                             for outcome in product(distribution, repeat=trials + 1)]
                for name in ("upper_tail", "centered_two_sided"):
                    scores = [fraction(summary[name]["plus_one_rank_score"]) for summary in summaries]
                    for numerator in range(trials + 2):
                        alpha = Fraction(numerator, trials + 1)
                        rejected = Fraction(sum(score <= alpha for score in scores), len(scores))
                        self.assertLessEqual(rejected, alpha)

    def test_complete_disjoint_trial_block_hashes_originals_and_replay(self):
        payload = fixture([["a"], [], ["a"]])
        result = module.sample_case(payload)
        self.assertEqual([row["trial"] for row in result["all_new_control_trials"]], [10, 11, 12, 13])
        self.assertEqual(result["original_ten_controls"], payload[2]["all_ten_controls"])
        self.assertEqual(result["distinct_new_control_hashes"], 1)
        self.assertEqual(len(result["all_new_control_trials"]), 4)
        self.assertEqual(result["tail_summary"]["B_histogram"], {"1": 4})
        self.assertEqual(result, module.sample_case(payload))

    def test_serial_and_four_worker_outputs_are_identical_for_synthetic_cases(self):
        payloads = [fixture(rows) for rows in ([list("ab"), list("ab")], [list("aabb")], [["a"], [], ["a"]], [])]
        self.assertEqual(module.execute_cases(payloads, 1), module.execute_cases(payloads, 4))

    def test_strict_inputs_and_overlapping_or_incomplete_trial_blocks_fail(self):
        for args in ((True, Fraction(1), [1]), (1, .5, [1]), (1, Fraction(-1), [1]), (1, Fraction(1), []),
                     (1, Fraction(1), [True]), (1, Fraction(1), [-1])):
            with self.assertRaises(ValueError):
                module.tail_summary(*args)
        for key, bad in (("first_new_trial", 9), ("last_new_trial", 15), ("seed", True), ("new_trials", 0)):
            payload = list(fixture([list("ab")]))
            payload[3][key] = bad
            with self.assertRaises(ValueError):
                module.sample_case(payload)
        with self.assertRaises(ValueError):
            module.display_fraction(Fraction(1, 2), True)

    def test_corpus_observation_provenance_and_original_trial_mismatches_fail(self):
        for mode in ("record_corpus_sha256", "flat_corpus_sha256", "observed", "flat", "old_trials"):
            payload = list(fixture([list("aab")]))
            if mode.endswith("sha256"):
                payload[0][mode] = "0" * 64
            elif mode == "observed":
                payload[2]["observed"]["distinct_repeating_types_B"] += 1
            elif mode == "flat":
                payload[1]["flat_tokens_with_provenance"][0]["original_token_index"] = 9
                digest = hashlib.sha256(encoded(payload[1]["flat_tokens_with_provenance"])).hexdigest()
                payload[0]["flat_corpus_sha256"] = payload[2]["flat_corpus_sha256"] = digest
            else:
                payload[2]["all_ten_controls"][0]["trial"] = 10
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                module.sample_case(payload)

    def test_frozen_dependency_drift_and_parent_replay_fail_before_new_jobs(self):
        for mode in ("drift", "parent"):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for name in (*module.FROZEN_PATHS, module.PLAN_PATH):
                    target = root / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(module.ROOT / name, target)
                module.load_plan(root)
                if mode == "drift":
                    target = root / module.MEAN_REPORT
                    target.write_bytes(target.read_bytes() + b"\n")
                with patch.object(module.parent, "run_study", return_value={"wrong": 1}), patch.object(module, "execute_cases") as jobs:
                    with self.assertRaises(ValueError):
                        module.run_study(root)
                    jobs.assert_not_called()

    def test_all_protected_aliases_before_and_during_computation_preserve_bytes(self):
        for name in (*module.FROZEN_PATHS, module.PLAN_PATH, module.HUMAN_PLAN, "scripts/historical_type_tails.py"):
            for kind, late in (("direct", False), ("symlink", False), ("hardlink", False), ("symlink", True), ("hardlink", True)):
                with self.subTest(name=name, kind=kind, late=late), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    source = root / name
                    source.parent.mkdir(parents=True)
                    source.write_bytes(b"preserve frozen source")
                    output = source if kind == "direct" else root / "output.json"
                    def alias():
                        if kind == "symlink":
                            output.symlink_to(source)
                        elif kind == "hardlink":
                            os.link(source, output)
                    def compute(_root):
                        if late:
                            alias()
                        return {"synthetic": "must not overwrite source"}
                    if not late:
                        alias()
                    with patch.object(module, "ROOT", root), patch.object(module, "__file__", str(root / "scripts/historical_type_tails.py")):
                        with patch.object(module, "run_study", side_effect=compute) as builder, patch("sys.argv", ["tails", "--output", str(output)]):
                            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                                module.main()
                            self.assertEqual(error.exception.code, 1)
                            if not late:
                                builder.assert_not_called()
                    self.assertEqual(source.read_bytes(), b"preserve frozen source")
                    self.assertEqual(output.read_bytes(), b"preserve frozen source")

    def test_strict_failed_checks_preserve_existing_output(self):
        for content in ('{"x":false}', '{"x":0.0}', '{"x":0,"x":0}'):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                output, check = root / "output.json", root / "check.json"
                output.write_bytes(b"preserve prior report")
                check.write_text(content)
                with patch.object(module, "ROOT", root), patch.object(module, "run_study", return_value={"x": 0}):
                    with patch("sys.argv", ["tails", "--output", str(output), "--check", str(check)]):
                        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                            module.main()
                self.assertEqual(output.read_bytes(), b"preserve prior report")


if __name__ == "__main__":
    unittest.main()
