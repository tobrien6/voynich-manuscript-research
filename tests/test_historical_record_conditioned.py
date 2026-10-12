import contextlib
import hashlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import historical_record_conditioned as module
from scripts.global_repeated_types import boundary_diagnostics, counts, exact_means, exact_record
from scripts.reconstruct_historical_tokens import encoded


def fixture(rows):
    records = [{"locator": f"fixture{i};H", "tokens": row, "original_token_indices": list(range(len(row))),
                "exclusion_reasons": []} for i, row in enumerate(rows)]
    flat = [{"token": t, "locator": row["locator"], "original_token_index": i}
            for row in records for i, t in enumerate(row["tokens"])]
    summary = {"ring_policy": "exclude_R2", "f66r_column_unit": "M",
               "flat_corpus_sha256": hashlib.sha256(encoded(flat)).hexdigest(),
               "record_corpus_sha256": hashlib.sha256(encoded(records)).hexdigest()}
    tokens = [r["token"] for r in flat]
    means = exact_means(tokens)
    baseline = {**summary, "tokens": len(tokens), "distinct_types": len(set(tokens)), "observed": counts(tokens),
                "observed_boundary_diagnostics": boundary_diagnostics(flat),
                "exact_global_null_means": {k: exact_record(means[k]) for k in ("A", "B")}}
    return summary, {"records": records, "flat_tokens_with_provenance": flat}, baseline


class HistoricalRecordConditionedTests(unittest.TestCase):
    def test_matched_fixture_retains_all_trials_and_joined_scope_means(self):
        args = (*fixture([["a"], [], ["a"]]), {"seed": 20261012, "trials": 10})
        result = module.assay_variant(*args)
        self.assertEqual([t["trial"] for t in result["all_ten_controls"]], list(range(10)))
        self.assertEqual(result["exact_A_scope_contributions"]["within_record"]["decimal"], 0)
        self.assertEqual(result["exact_A_scope_contributions"]["cross_record"]["decimal"], 1)
        self.assertEqual(result["exact_conditional_null_means"]["B"]["decimal"], 1)
        self.assertEqual(result["records_including_empty"], 3)
        self.assertEqual(result["nonempty_records"], 2)
        self.assertTrue(all(t["cross_record_pair_events"] == 1 for t in result["all_ten_controls"]))
        self.assertEqual(result, module.assay_variant(*args))

    def test_zero_means_and_negative_differences_serialize_without_infinite_ratios(self):
        result = module.assay_variant(*fixture([["a"], ["b"], ["a"]]), {"seed": 0, "trials": 10})
        self.assertEqual(result["observed_over_exact_conditional_mean"], {"A": None, "B": None})
        self.assertEqual(result["observed_over_ten_control_mean"], {"A": None, "B": None})
        delta = module.fraction_from_record(result["conditional_minus_global_mean"]["B"])
        self.assertEqual(delta, -module.fraction_from_record(result["exact_global_null_means"]["B"]))
        self.assertGreater(delta.denominator, 0)

    def test_both_reconstruction_and_global_input_hashes_must_match(self):
        for key in ("flat_corpus_sha256", "record_corpus_sha256"):
            for target in ("summary", "baseline"):
                summary, corpus, baseline = fixture([list("aab")])
                (summary if target == "summary" else baseline)[key] = "0" * 64
                with self.subTest(key=key, target=target), self.assertRaisesRegex(ValueError, "digest differs"):
                    module.assay_variant(summary, corpus, baseline, {"seed": 0, "trials": 10})

    def test_observed_edge_and_variant_drift_fail_before_conditional_means(self):
        for key in ("tokens", "distinct_types", "observed", "observed_boundary_diagnostics", "f66r_column_unit"):
            summary, corpus, baseline = fixture([list("aab")])
            baseline[key] = None
            with patch.object(module, "exact_record_means") as measure:
                with self.subTest(key=key), self.assertRaisesRegex(ValueError, "population differs"):
                    module.assay_variant(summary, corpus, baseline, {"seed": 0, "trials": 10})
                measure.assert_not_called()

    def test_record_and_flat_slot_disagreement_fails_before_measurement(self):
        summary, corpus, baseline = fixture([list("aab")])
        corpus["records"][0]["original_token_indices"][1] = 9
        summary["record_corpus_sha256"] = hashlib.sha256(encoded(corpus["records"])).hexdigest()
        baseline["record_corpus_sha256"] = summary["record_corpus_sha256"]
        with patch.object(module, "exact_record_means") as measure:
            with self.assertRaisesRegex(ValueError, "slots differ"):
                module.assay_variant(summary, corpus, baseline, {"seed": 0, "trials": 10})
            measure.assert_not_called()

    def test_dependency_drift_fails_before_source_reconstruction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (*module.FROZEN_PATHS, module.PLAN_PATH):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(module.ROOT / name, path)
            module.load_plan(root)
            path = root / module.GLOBAL_REPORT
            path.write_bytes(path.read_bytes() + b"drift")
            with patch.object(module, "reconstruct") as rebuild:
                with self.assertRaisesRegex(ValueError, "conditional dependency differs"):
                    module.run_study(root)
                rebuild.assert_not_called()

    def test_protected_global_report_and_failure_preserve_existing_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protected = root / module.GLOBAL_REPORT
            protected.parent.mkdir(parents=True)
            protected.write_text("preserve global report")
            with patch.object(module, "ROOT", root), patch("sys.argv", ["assay", "--output", str(protected)]):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 1)
            self.assertEqual(protected.read_text(), "preserve global report")
            output, check = root / "output.json", root / "check.json"
            output.write_text("preserve output")
            check.write_text('{}')
            for failure in (True, False):
                with patch.object(module, "ROOT", root), patch.object(module, "run_study") as run:
                    if failure:
                        run.side_effect = ValueError("drift")
                    else:
                        run.return_value = {"different": 1}
                    with patch("sys.argv", ["assay", "--output", str(output), "--check", str(check)]):
                        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                            module.main()
                self.assertEqual(output.read_text(), "preserve output")


if __name__ == "__main__":
    unittest.main()
