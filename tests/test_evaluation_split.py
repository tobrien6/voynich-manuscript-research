"""Synthetic cases for scientific split errors; no real Voynich corpus/split."""

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_evaluation_split.py"
SPEC = importlib.util.spec_from_file_location("evaluation_split", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CORPUS = b"synthetic input for split checks\n"


def example():
    units = []
    for number in range(1, 4):
        units.append({
            "unit_id": f"synthetic-{number}",
            "partition": "development" if number < 3 else "evaluation",
            "folio_ids": [str(number)],
            "canvas_ids": [f"urn:synthetic:canvas:{number}"],
            "dependency_groups": [f"synthetic-group-{number}"],
            "source_refs": ["Synthetic fixture; no actual manuscript material"],
            "prior_exposure": {
                "state": "known" if number < 3 else "none_reported",
                "note": "Synthetic declaration only; no real exposure history",
                "declared_by": "test fixture", "recorded_at": "2000-01-01T00:00:00Z",
                "used_for_development": number < 3,
            },
        })
    return {
        "schema_version": 1, "split_id": "synthetic-v1", "candidate_version": "synthetic-rule-v1",
        "status": "frozen", "evaluation_claim": "unseen_material",
        "created_at": "2000-01-01T00:00:00Z", "frozen_at": "2000-01-02T00:00:00Z",
        "fit_started_at": "2000-01-03T00:00:00Z",
        "input": {"edition": "synthetic-v1", "source": "test fixture",
                  "sha256": hashlib.sha256(CORPUS).hexdigest()},
        "expected_counts": {"development": 2, "evaluation": 1}, "units": units,
    }


class EvaluationSplitTests(unittest.TestCase):
    def assert_rejected(self, split, expected, input_bytes=CORPUS, require_frozen=True):
        errors = MODULE.validate(split, input_bytes, require_frozen)["errors"]
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_valid_frozen_split(self):
        self.assertEqual(MODULE.validate(example(), CORPUS, True)["errors"], [])

    def test_json_loader_preserves_valid_declarations(self):
        split = example()
        self.assertEqual(MODULE.load_split_json(json.dumps(split)), split)

    def test_duplicate_exposure_members_cannot_hide_an_unresolved_freeze(self):
        raw = json.dumps(example()).replace(
            '"state": "none_reported"',
            '"state": "unknown", "state": "none_reported"')
        # Ordinary decoding discards the first declaration and would pass.
        self.assertEqual(MODULE.validate(json.loads(raw), CORPUS, True)["errors"], [])
        with self.assertRaisesRegex(ValueError, "duplicate object member: 'state'"):
            MODULE.load_split_json(raw)

    def test_duplicate_members_fail_at_all_depths_and_after_escape_decoding(self):
        for raw in ('{"status":"draft","status":"frozen"}',
                    '{"input":{"sha256":"a","sha256":"a"}}',
                    '{"units":[{"partition":"development","partition":"evaluation"}]}',
                    r'{"state":"unknown","st\u0061te":"none_reported"}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "duplicate object member"):
                MODULE.load_split_json(raw)

    def test_non_json_numeric_constants_are_rejected(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant), self.assertRaisesRegex(ValueError, "non-JSON numeric constant"):
                MODULE.load_split_json('{"extension":' + constant + '}')

    def test_cli_rejects_ambiguous_json_without_a_pass_or_traceback(self):
        raw = json.dumps(example()).replace(
            '"state": "none_reported"',
            '"state": "unknown", "state": "none_reported"')
        with tempfile.TemporaryDirectory() as directory:
            split_path = Path(directory) / "split.json"
            input_path = Path(directory) / "input.txt"
            split_path.write_text(raw, encoding="utf-8")
            input_path.write_bytes(CORPUS)
            result = subprocess.run([sys.executable, str(SCRIPT), str(split_path),
                                     "--input", str(input_path), "--require-frozen"],
                                    capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL: Split JSON has a duplicate object member", result.stderr)
        self.assertNotIn("PASS:", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_still_accepts_a_valid_frozen_synthetic_split(self):
        with tempfile.TemporaryDirectory() as directory:
            split_path = Path(directory) / "split.json"
            input_path = Path(directory) / "input.txt"
            split_path.write_text(json.dumps(example()), encoding="utf-8")
            input_path.write_bytes(CORPUS)
            result = subprocess.run([sys.executable, str(SCRIPT), str(split_path),
                                     "--input", str(input_path), "--require-frozen"],
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: declared frozen split", result.stdout)

    def test_same_leaf_on_both_sides_of_split(self):
        split = example()
        split["units"][2]["folio_ids"] = ["1"]
        self.assert_rejected(split, "physical folio 1")

    def test_shared_foldout_canvas_across_partitions(self):
        split = example()
        split["units"][2]["canvas_ids"] = ["urn:synthetic:canvas:1"]
        self.assert_rejected(split, "canvas urn:synthetic:canvas:1")

    def test_repeated_passages_cannot_cross_partitions(self):
        split = example()
        split["units"][0]["dependency_groups"] = ["repeated-passage"]
        split["units"][2]["dependency_groups"] = ["repeated-passage"]
        self.assert_rejected(split, "Dependency group repeated-passage")

    def test_related_development_units_can_share_a_group(self):
        split = example()
        split["units"][0]["dependency_groups"] = ["repeated-passage"]
        split["units"][1]["dependency_groups"] = ["repeated-passage"]
        self.assertEqual(MODULE.validate(split, CORPUS, True)["errors"], [])

    def test_multiple_panels_cannot_inflate_same_leaf_unit_count(self):
        split = example()
        split["units"][1]["folio_ids"] = ["1"]
        self.assert_rejected(split, "combine related sides/panels")

    def test_identifier_whitespace_cannot_disguise_a_shared_canvas(self):
        split = example()
        split["units"][2]["canvas_ids"] = ["urn:synthetic:canvas:1 "]
        self.assert_rejected(split, "surrounding whitespace")

    def test_unknown_evaluation_exposure_blocks_freeze(self):
        split = example()
        split["units"][2]["prior_exposure"]["state"] = "unknown"
        self.assert_rejected(split, "exposure/development use remains unresolved")

    def test_draft_can_keep_unknown_exposure_with_a_warning(self):
        split = example()
        split.update(status="draft", frozen_at=None, fit_started_at=None)
        split["units"][2]["prior_exposure"].update(state="unknown", used_for_development=None)
        report = MODULE.validate(split, CORPUS)
        self.assertEqual(report["errors"], [])
        self.assertTrue(any("unresolved" in warning for warning in report["warnings"]))
        self.assert_rejected(split, "not frozen")

    def test_inspected_material_is_not_unseen(self):
        split = example()
        split["units"][2]["prior_exposure"]["state"] = "known"
        self.assert_rejected(split, "known exposure contradicts unseen_material")
        split["evaluation_claim"] = "excluded_from_fitting"
        self.assertEqual(MODULE.validate(split, CORPUS, True)["errors"], [])

    def test_development_use_invalidates_evaluation(self):
        split = example()
        split["evaluation_claim"] = "excluded_from_fitting"
        split["units"][2]["prior_exposure"].update(state="known", used_for_development=True)
        self.assert_rejected(split, "evaluation material was used for development")

    def test_input_changed_or_not_supplied(self):
        self.assert_rejected(example(), "Input bytes differ", input_bytes=CORPUS + b"changed")
        self.assert_rejected(example(), "requires input bytes", input_bytes=None)

    def test_fit_cannot_precede_or_coincide_with_freeze(self):
        for started in ["2000-01-01T00:00:00Z", "2000-01-02T00:00:00Z"]:
            split = example()
            split["fit_started_at"] = started
            self.assert_rejected(split, "strictly before fitting")

    def test_exposure_declaration_cannot_postdate_freeze(self):
        split = example()
        split["units"][2]["prior_exposure"]["recorded_at"] = "2000-01-04T00:00:00Z"
        self.assert_rejected(split, "exposure declaration postdates")

    def test_counts_and_unit_duplicates_are_rejected(self):
        split = example()
        split["expected_counts"]["development"] = 8
        self.assert_rejected(split, "differ from expected_counts")
        split = example()
        split["units"].append(deepcopy(split["units"][0]))
        self.assert_rejected(split, "duplicate unit identifier")

    def test_timezones_and_malformed_fields_are_rejected_cleanly(self):
        for field, value in [("created_at", "2000-01-01"), ("status", []),
                             ("evaluation_claim", {}), ("units", None),
                             ("schema_version", True)]:
            split = example()
            split[field] = value
            self.assertTrue(MODULE.validate(split, CORPUS, True)["errors"])
        for field in ["partition", "folio_ids", "prior_exposure"]:
            split = example()
            split["units"][0][field] = []
            self.assertTrue(MODULE.validate(split, CORPUS, True)["errors"])

    def test_absent_history_is_not_an_explicit_null_declaration(self):
        split = example()
        del split["fit_started_at"]
        self.assert_rejected(split, "fit_started_at: required field is missing")
        split = example()
        del split["units"][0]["prior_exposure"]["used_for_development"]
        self.assert_rejected(split, "declare development use explicitly")


if __name__ == "__main__":
    unittest.main()
