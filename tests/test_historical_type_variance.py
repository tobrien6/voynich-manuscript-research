import contextlib
import hashlib
import io
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import historical_type_variance as module
from scripts import historical_repeated_types as global_parent
from scripts.reconstruct_historical_tokens import encoded


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
    return summary, corpus, reference


class HistoricalTypeVarianceTests(unittest.TestCase):
    def test_exact_join_covariance_and_existing_controls_remain_matched_to_parent(self):
        summary, corpus, reference = fixture([list("ab"), list("ab")])
        result = module.assay_variant(summary, corpus, reference, {"decimal_precision": 50})
        self.assertEqual(result["exact_moments"]["variance_B"]["decimal"], .25)
        self.assertEqual(result["exact_moments"]["type_pair_covariance_sum"]["decimal"], -.0625)
        self.assertEqual(result["spread_diagnostics"]["standard_deviation_approx"], .5)
        self.assertEqual(result["existing_ten_control_B_values"],
                         [row["distinct_repeating_types_B"] for row in reference["all_ten_controls"]])
        self.assertEqual(result["observed_boundary_diagnostics"], reference["observed_boundary_diagnostics"])

    def test_constant_empty_and_forced_types_retain_undefined_sd_scale(self):
        for rows, expected in (([], 0), ([["a"], [], ["a"]], 1)):
            result = module.assay_variant(*fixture(rows), {"decimal_precision": 50})
            self.assertEqual(result["exact_moments"]["mean_B"]["decimal"], expected)
            self.assertEqual(result["exact_moments"]["variance_B"]["decimal"], 0)
            self.assertIsNone(result["spread_diagnostics"]["centered_B_in_conditional_SD_approx"])

    def test_hash_observation_and_parent_mean_mismatches_fail(self):
        for mode in ("record_corpus_sha256", "flat_corpus_sha256", "observed", "mean", "forced"):
            summary, corpus, reference = fixture([list("aabb")])
            if mode.endswith("sha256"):
                summary[mode] = "0" * 64
            elif mode == "observed":
                reference["observed"]["distinct_repeating_types_B"] += 1
            elif mode == "mean":
                reference["exact_conditional_null_means"]["B"] = {"numerator_hex": "0x0", "denominator_hex": "0x1", "decimal": 0}
            else:
                reference["forced_repeating_types_under_conditional_null"] += 1
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                module.assay_variant(summary, corpus, reference, {"decimal_precision": 50})

    def test_dependency_drift_fails_before_parent_or_corpus_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (*module.FROZEN_PATHS, module.PLAN_PATH):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(module.ROOT / name, target)
            module.load_plan(root)
            target = root / module.MEAN_REPORT
            target.write_bytes(target.read_bytes() + b"\n")
            with patch.object(module.parent, "run_study") as parent_replay, patch.object(module, "reconstruct") as corpus_replay:
                with self.assertRaisesRegex(ValueError, "dependency differs"):
                    module.run_study(root)
                parent_replay.assert_not_called()
                corpus_replay.assert_not_called()

    def test_all_frozen_dependency_plan_helper_aliases_are_blocked_before_and_after_computation(self):
        names = (*module.FROZEN_PATHS, module.PLAN_PATH, module.HUMAN_PLAN,
                 "scripts/historical_type_variance.py", "scripts/record_repeated_type_variance.py")
        for name in names:
            for kind, late in (("direct", False), ("symlink", False), ("hardlink", False), ("symlink", True), ("hardlink", True)):
                with self.subTest(name=name, kind=kind, late=late), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    source = root / name
                    source.parent.mkdir(parents=True)
                    source.write_bytes(b"preserve frozen bytes")
                    output = source if kind == "direct" else root / "output.json"
                    def alias():
                        if kind == "symlink":
                            output.symlink_to(source)
                        elif kind == "hardlink":
                            os.link(source, output)
                    def compute(_root):
                        if late:
                            alias()
                        return {"synthetic": "must not overwrite frozen source"}
                    if not late:
                        alias()
                    with patch.object(module, "ROOT", root), patch.object(module, "__file__", str(root / "scripts/historical_type_variance.py")):
                        with patch.object(module, "run_study", side_effect=compute) as builder, patch("sys.argv", ["variance", "--output", str(output)]):
                            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                                module.main()
                            self.assertEqual(error.exception.code, 1)
                            if not late:
                                builder.assert_not_called()
                    self.assertEqual(source.read_bytes(), b"preserve frozen bytes")
                    self.assertEqual(output.read_bytes(), b"preserve frozen bytes")

    def test_complete_parent_replay_mismatch_stops_before_new_corpus_or_moment_work(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (*module.FROZEN_PATHS, module.PLAN_PATH):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(module.ROOT / name, target)
            with patch.object(module.parent, "run_study", return_value={"wrong": "parent"}), patch.object(module, "reconstruct") as rebuild:
                with self.assertRaisesRegex(ValueError, "accepted conditional mean/control report"):
                    module.run_study(root)
                rebuild.assert_not_called()

    def test_failed_strict_report_check_preserves_preexisting_output(self):
        for content in ('{"x":false}', '{"x":0.0}', '{"x":0,"x":0}'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                output, check = root / "output.json", root / "check.json"
                output.write_bytes(b"preserve existing report")
                check.write_text(content)
                with patch.object(module, "ROOT", root), patch.object(module, "run_study", return_value={"x": 0}):
                    with patch("sys.argv", ["variance", "--output", str(output), "--check", str(check)]):
                        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                            module.main()
                self.assertEqual(output.read_bytes(), b"preserve existing report")


if __name__ == "__main__":
    unittest.main()
