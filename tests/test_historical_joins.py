import contextlib
from dataclasses import replace
import hashlib
import io
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_historical_joins as module
from scripts.audit_historical_interlinear import HistoricalRecord
from scripts.global_repeated_types import counts, boundary_diagnostics
from scripts.reconstruct_historical_tokens import encoded


def fixture(originals, retained=None, reasons=None, envelopes=None):
    retained = retained if retained is not None else [list(range(len(row))) for row in originals]
    reasons = reasons if reasons is not None else [[] for _ in originals]
    envelopes = envelopes if envelopes is not None else [("f1r", "P") for _ in originals]
    native, rows = [], []
    for i, (original, indices, why, (page, unit)) in enumerate(zip(originals, retained, reasons, envelopes, strict=True)):
        locator = f"{page}.{unit}.{i + 1};H"
        native.append(HistoricalRecord(locator, page, unit, str(i + 1), "H", ".".join(original), 1 + 3 * i))
        rows.append({"locator": locator, "tokens": [original[j] for j in indices],
                     "original_token_indices": indices, "exclusion_reasons": why})
    flat = [{"token": token, "locator": row["locator"], "original_token_index": index}
            for row in rows for token, index in zip(row["tokens"], row["original_token_indices"], strict=True)]
    summary = {"ring_policy": "exclude_R2", "f66r_column_unit": "M",
               "flat_corpus_sha256": hashlib.sha256(encoded(flat)).hexdigest(),
               "record_corpus_sha256": hashlib.sha256(encoded(rows)).hexdigest()}
    baseline = {**summary, "tokens": len(flat), "distinct_types": len({r["token"] for r in flat}),
                "observed": counts([r["token"] for r in flat]), "observed_boundary_diagnostics": boundary_diagnostics(flat)}
    return summary, {"records": rows, "flat_tokens_with_provenance": flat}, baseline, native, originals


class HistoricalJoinTests(unittest.TestCase):
    def test_complete_bridged_and_direct_cases_reconcile_scope_and_source_context(self):
        args = fixture([list("aa"), ["z"], list("ab"), ["b"]], retained=[[0, 1], [], [0, 1], [0]],
                       reasons=[[], ["f66r_column"], [], []],
                       envelopes=[("f1r", "P"), ("f1r", "L"), ("f1r", "P"), ("f2r", "P")])
        result = module.audit_variant(*args)
        self.assertEqual(result["joining_edges_by_native_class"],
                         {"same_page_same_unit": 1, "same_page_different_unit": 0, "different_page": 1})
        self.assertEqual(result["equal_joins_by_selected_H_adjacency"],
                         {"consecutive_selected_H": 1, "spans_empty_H_records": 1})
        first, second = result["all_equal_join_events"]
        self.assertEqual([r["flat_left_token_index"] for r in (first, second)], [1, 3])
        self.assertEqual(first["token"], "a")
        self.assertTrue(first["type_also_repeats_within_records"])
        self.assertFalse(second["type_also_repeats_within_records"])
        self.assertEqual(first["left"]["endpoint_normalized_index"], 1)
        self.assertEqual(first["right"]["selected_H_ordinal"], 2)
        skipped = first["intervening_empty_H_records"]
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0]["empty_status"], "whole_record_excluded")
        self.assertEqual(skipped[0]["exclusion_reasons"], ["f66r_column"])
        self.assertEqual(skipped[0]["normalized_tokens_before_manual_exclusions"], 1)
        self.assertEqual(skipped[0]["physical_source_file_line"], 4)
        self.assertEqual(skipped[0]["raw_body_sha256"], hashlib.sha256(b"z").hexdigest())

    def test_naturally_empty_and_manual_token_deletion_are_distinguished(self):
        args = fixture([["a"], [], ["z"], ["a"]], retained=[[0], [], [], [0]])
        case = module.audit_variant(*args)["all_equal_join_events"][0]
        self.assertEqual([r["empty_status"] for r in case["intervening_empty_H_records"]],
                         ["normalized_empty", "manual_token_deletion_left_empty"])
        self.assertTrue(all(r["retained_tokens"] == 0 for r in case["intervening_empty_H_records"]))

    def test_case_sensitive_noncyclic_and_empty_populations(self):
        for rows in ([], [[]], [["a"]], [["a"], ["A"]], [["a"], ["b"], ["a"]]):
            with self.subTest(rows=rows):
                result = module.audit_variant(*fixture(rows))
                self.assertEqual(result["all_equal_join_events"], [])
                self.assertEqual(sum(result["joining_edges_by_native_class"].values()),
                                 max(0, sum(bool(row) for row in rows) - 1))

    def test_same_page_unit_change_remains_separate_from_page_change(self):
        args = fixture([["x"], ["x"], ["x"]],
                       envelopes=[("f1r", "P"), ("f1r", "L"), ("f2r", "L")])
        cases = module.audit_variant(*args)["all_equal_join_events"]
        self.assertEqual([c["native_join_class"] for c in cases], ["same_page_different_unit", "different_page"])
        self.assertEqual([c["joining_edge_ordinal"] for c in cases], [0, 1])

    def test_native_order_physical_file_lines_and_indices_are_verified(self):
        for mode in ("order", "physical_line", "bool_index", "duplicate_index", "source_token"):
            summary, corpus, baseline, native, normalized = fixture([list("aa"), ["a"]])
            if mode == "order":
                native.reverse()
            elif mode == "physical_line":
                native[1] = replace(native[1], physical_line=native[0].physical_line)
            elif mode == "bool_index":
                corpus["records"][0]["original_token_indices"][0] = False
            elif mode == "duplicate_index":
                corpus["records"][0]["original_token_indices"] = [0, 0]
            else:
                normalized[0][0] = "wrong"
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "record order or retained endpoint"):
                module.audit_variant(summary, corpus, baseline, native, normalized)

    def test_flat_and_both_corpus_hash_mismatches_fail(self):
        for mode in ("flat", "flat_corpus_sha256", "record_corpus_sha256"):
            args = list(fixture([["a"], ["a"]]))
            if mode == "flat":
                args[1]["flat_tokens_with_provenance"][0]["token"] = "wrong"
            else:
                args[0][mode] = "0" * 64
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                module.audit_variant(*args)

    def test_global_reference_identity_counts_and_type_distinctions_are_verified(self):
        for key, value in (("f66r_column_unit", "L"), ("tokens", 99), ("distinct_types", 99),
                           ("observed", {"equal_pair_events_A": True, "distinct_repeating_types_B": 1,
                                         "asterisk_bearing_pair_events": 0, "asterisk_bearing_repeating_types": 0})):
            args = list(fixture([["a"], ["a"]]))
            args[2][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "global input/observed"):
                module.audit_variant(*args)

    def test_dependency_drift_fails_before_reconstruction(self):
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
                with self.assertRaisesRegex(ValueError, "dependency differs"):
                    module.run_audit(root)
                rebuild.assert_not_called()

    def test_all_protected_aliases_before_and_during_computation_preserve_bytes(self):
        for name in (*module.FROZEN_PATHS, module.PLAN_PATH, module.HUMAN_PLAN, "scripts/audit_historical_joins.py"):
            for kind, late in (("direct", False), ("symlink", False), ("hardlink", False), ("symlink", True), ("hardlink", True)):
                with self.subTest(name=name, kind=kind, late=late), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    source = root / name
                    source.parent.mkdir(parents=True)
                    source.write_bytes(b"preserve protected bytes")
                    output = source if kind == "direct" else root / "output.json"
                    def alias():
                        if kind == "symlink":
                            output.symlink_to(source)
                        elif kind == "hardlink":
                            os.link(source, output)
                    def build(_root):
                        if late:
                            alias()
                        return {"synthetic": "do not overwrite protected source"}
                    if not late:
                        alias()
                    with patch.object(module, "ROOT", root), patch.object(module, "__file__", str(root / "scripts/audit_historical_joins.py")):
                        with patch.object(module, "run_audit", side_effect=build) as builder, patch("sys.argv", ["audit", "--output", str(output)]):
                            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                                module.main()
                            self.assertEqual(error.exception.code, 1)
                            if not late:
                                builder.assert_not_called()
                    self.assertEqual(source.read_bytes(), b"preserve protected bytes")
                    self.assertEqual(output.read_bytes(), b"preserve protected bytes")

    def test_strict_check_failures_preserve_preexisting_output(self):
        for content in ('{"x":false}', '{"x":0.0}', '{"x":0,"x":0}'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                output, check = root / "output.json", root / "check.json"
                output.write_bytes(b"preserve prior output")
                check.write_text(content)
                with patch.object(module, "ROOT", root), patch.object(module, "run_audit", return_value={"x": 0}):
                    with patch("sys.argv", ["audit", "--output", str(output), "--check", str(check)]):
                        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                            module.main()
                self.assertEqual(output.read_bytes(), b"preserve prior output")


if __name__ == "__main__":
    unittest.main()
