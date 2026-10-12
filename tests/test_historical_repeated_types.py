import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import historical_repeated_types as module
from scripts.reconstruct_historical_tokens import encoded


def variant(tokens):
    rows = [{"locator": "fixture;H", "tokens": tokens,
             "original_token_indices": list(range(len(tokens))), "exclusion_reasons": []}]
    flat = [{"token": t, "locator": "fixture;H", "original_token_index": i} for i, t in enumerate(tokens)]
    summary = {"ring_policy": "exclude_R2", "f66r_column_unit": "M",
               "flat_corpus_sha256": hashlib.sha256(encoded(flat)).hexdigest(),
               "record_corpus_sha256": hashlib.sha256(encoded(rows)).hexdigest()}
    return summary, {"records": rows, "flat_tokens_with_provenance": flat}


class HistoricalRepeatedTypeTests(unittest.TestCase):
    def test_synthetic_variant_retains_all_controls_and_exact_mean_units(self):
        summary, corpus = variant(list("aaaaabb"))
        report = module.assay_variant(summary, corpus, {"seed": 20261012, "trials": 10})
        self.assertEqual(len(report["all_ten_controls"]), 10)
        self.assertEqual([t["trial"] for t in report["all_ten_controls"]], list(range(10)))
        self.assertEqual(report["observed"]["equal_pair_events_A"], 5)
        self.assertEqual(report["observed"]["distinct_repeating_types_B"], 2)
        self.assertAlmostEqual(report["exact_global_null_means"]["B"]["decimal"], 9 / 7)
        self.assertEqual(report, module.assay_variant(summary, corpus, {"seed": 20261012, "trials": 10}))

    def test_zero_denominators_are_retained_as_undefined(self):
        summary, corpus = variant([])
        report = module.assay_variant(summary, corpus, {"seed": 0, "trials": 10})
        self.assertEqual(report["observed_over_exact_mean"], {"A": None, "B": None})
        self.assertEqual(report["observed_over_ten_control_mean"], {"A": None, "B": None})

    def test_both_corpus_digests_are_checked_before_measurement(self):
        for key in ("flat_corpus_sha256", "record_corpus_sha256"):
            summary, corpus = variant(list("aab"))
            summary[key] = "0" * 64
            with self.subTest(key=key), self.assertRaises(ValueError):
                module.assay_variant(summary, corpus, {"seed": 0, "trials": 10})

    def test_dependency_drift_fails_before_reconstruction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (*module.FROZEN_PATHS, module.PLAN_PATH):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(module.ROOT / name, target)
            module.load_plan(root)
            path = root / module.FROZEN_PATHS[0]
            path.write_bytes(path.read_bytes() + b"drift")
            with patch.object(module, "reconstruct") as rebuild:
                with self.assertRaisesRegex(ValueError, "dependency differs"):
                    module.run_study(root)
                rebuild.assert_not_called()

    def test_protected_output_preserves_source_plan_and_existing_output_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protected = root / module.PLAN_PATH
            protected.parent.mkdir(parents=True)
            protected.write_text("preserve plan")
            with patch.object(module, "ROOT", root), patch("sys.argv", ["assay", "--output", str(protected)]):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 1)
            self.assertEqual(protected.read_text(), "preserve plan")
            output = root / "output.json"
            output.write_text("preserve output")
            with patch.object(module, "ROOT", root), patch.object(module, "run_study", side_effect=ValueError("drift")):
                with patch("sys.argv", ["assay", "--output", str(output)]):
                    with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                        module.main()
            self.assertEqual(output.read_text(), "preserve output")


if __name__ == "__main__":
    unittest.main()
