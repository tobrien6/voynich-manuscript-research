import contextlib
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_historical_reddy_envelopes as module
from scripts.audit_historical_interlinear import HistoricalRecord


def fixture(bodies, r_tokens, h_keys=None, r_keys=None):
    h_keys = h_keys or [("f1r", "P1", str(i + 1), "H") for i in range(len(bodies))]
    r_keys = r_keys or [("f1r", "P1", str(i + 1), "H") for i in range(len(r_tokens))]
    native = [HistoricalRecord(f"{p}.{u}.{n};{t}", p, u, n, t, body, 2 + i * 3)
              for i, ((p, u, n, t), body) in enumerate(zip(h_keys, bodies, strict=True))]
    annotated = [{"header": key, "native_file_line": 1 + i * 2, "tokens": tokens}
                 for i, (key, tokens) in enumerate(zip(r_keys, r_tokens, strict=True))]
    return native, annotated


def compare(*args, special_codes=None, **kwargs):
    return module.compare_records(*module.describe_sources(*fixture(*args, **kwargs), special_codes or set()))


class HistoricalReddyEnvelopeTests(unittest.TestCase):
    def test_equal_totals_preserve_opposing_local_count_differences(self):
        result = compare(["a.b", "c"], [["X"], ["Y", "Z"]])
        summary = result["summary"]
        self.assertEqual(summary["h_fallback"]["tokens"], summary["reddy"]["tokens"])
        self.assertEqual(summary["h_fallback"]["shared_count_comparison"], {
            "equal_records": 0, "unequal_records": 2, "positive_records": 1, "negative_records": 1,
            "positive_sum": 1, "negative_sum": -1, "net_sum": 0, "absolute_sum": 2})
        self.assertTrue(result["shared_order"]["exact_shared_order_equal"])
        self.assertEqual([row["h"]["ordinal"] for row in result["all_union_records"]], [0, 1])
        self.assertEqual([row["h"]["file_line"] for row in result["all_union_records"]], [2, 5])

    def test_one_sided_empty_and_page_populations_all_remain(self):
        result = compare(["a", "!--", "b.c"], [["X"], ["Y", "Z", "W"]],
                         h_keys=[("f1r", "P1", "1", "H"), ("f1r", "P1", "2", "H"), ("f2r", "P", "1", "H")],
                         r_keys=[("f1r", "P1", "1", "H"), ("f3r", "P", "1", "H")])
        self.assertEqual([result["summary"][n] for n in ("union_records", "shared_records", "h_only_records", "reddy_only_records")], [4, 1, 2, 1])
        self.assertEqual(result["summary"]["h_fallback"]["empty_records"], 1)
        self.assertEqual(result["summary"]["h_fallback"]["unmatched_tokens"], 2)
        self.assertEqual(result["summary"]["reddy"]["unmatched_tokens"], 3)
        self.assertEqual([row["page"] for row in result["pages"]], ["f1r", "f2r", "f3r"])
        for stream in module.STREAMS:
            self.assertEqual(sum(p[stream]["tokens"] for p in result["pages"]), result["summary"][stream]["tokens"])
        empty = result["all_union_records"][1]
        self.assertIsNone(empty["shared_h_minus_reddy"]["h_fallback"])
        self.assertIsNone(empty["reddy"])

    def test_shared_order_uses_original_sequences_not_sorted_keys(self):
        keys = [("f1r", "P1", "10", "H"), ("f1r", "P1", "2", "H")]
        result = compare(["a", "b"], [["X"], ["Y"]], h_keys=keys, r_keys=list(reversed(keys)))
        order = result["shared_order"]
        self.assertFalse(order["exact_shared_order_equal"])
        self.assertEqual(len(order["discordant_shared_ranks"]), 2)
        self.assertNotEqual(order["h_ordered_shared_keys_sha256"], order["reddy_ordered_shared_keys_sha256"])
        self.assertEqual(order["discordant_shared_ranks"][0]["h_key"], list(keys[0]))

    def test_literal_case_unit_suffix_tag_distinctions_are_not_merged(self):
        keys = [("f1r", "P1", "1", "H"), ("f1r", "P", "1", "H"), ("f1r", "p1", "1", "H"),
                ("f1r", "P1", "1a", "H"), ("F1r", "P1", "1", "H"), ("f1r", "P1", "1", "U")]
        result = compare(["a"], [["X"] for _ in keys], r_keys=keys)
        self.assertEqual(result["summary"]["shared_records"], 1)
        self.assertEqual(result["summary"]["reddy_only_records"], 5)

    def test_both_fixed_normalizations_keep_code_fallback_effects(self):
        result = compare(["a{code}.b", "a{code}", "a!b%c-d=e,f", "{comment}"],
                         [["X", "Y"], ["X"], ["X", "Y", "Z", "W"]], special_codes={"code"})
        self.assertEqual(result["summary"]["h_fallback"]["tokens"], 7)
        self.assertEqual(result["summary"]["h_code_deleted"]["tokens"], 5)
        self.assertEqual(result["summary"]["h_code_deleted"]["empty_records"], 2)
        first = result["all_union_records"][0]
        self.assertNotEqual(first["h"]["fallback_token_vector_sha256"], first["h"]["code_deleted_token_vector_sha256"])
        self.assertNotIn("tokens", first["h"])

    def test_duplicates_malformed_keys_source_order_and_counts_fail(self):
        rows, other = module.describe_sources(*fixture(["a", "b"], [["X"], ["Y"]]), set())
        for mode in ("duplicate", "key", "ordinal", "file_line", "count"):
            changed = json.loads(json.dumps(rows))
            if mode == "duplicate": changed[1]["key"] = changed[0]["key"]
            elif mode == "key": changed[0]["key"][1] = "P 1"
            elif mode == "ordinal": changed[0]["ordinal"] = False
            elif mode == "file_line": changed[1]["file_line"] = changed[0]["file_line"]
            else: changed[0]["fallback_tokens"] = True
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                module.compare_records(changed, other)
        native, annotated = fixture(["a"], [["X"]])
        with self.assertRaises(ValueError): module.describe_sources([replace(native[0], transcriber="U")], annotated, set())
        for raw in (b"<f1r P1 1> X\n", b"<f1r P1 1 H>\n", b"<f1r P1 1 H> X\n<f1r P1 1 H> Y\n"):
            with self.assertRaises(ValueError): module.reddy.annotated(raw)

    def test_all_frozen_dependencies_and_options_are_enforced(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in (*module.FROZEN, module.PLAN):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(module.ROOT / name, target)
            module.load_plan(root)
            for name in module.FROZEN:
                target = root / name
                original = target.read_bytes()
                target.write_bytes(original + b" ")
                with self.subTest(name=name), self.assertRaises(ValueError): module.load_plan(root)
                target.write_bytes(original)
            plan = module.read_json(root / module.PLAN)
            for key, value in (("manual_exclusions", True), ("ordinal_base", False), ("reference_snapshot", "other")):
                changed = {**plan, key: value}
                (root / module.PLAN).write_text(json.dumps(changed))
                with self.subTest(key=key), self.assertRaises(ValueError): module.load_plan(root)
            changed = {**plan, "dependency_hashes": {**plan["dependency_hashes"], "extra": "x"}}
            (root / module.PLAN).write_text(json.dumps(changed))
            with self.assertRaises(ValueError): module.load_plan(root)

    def test_complete_parent_comparison_rejects_extra_fields_booleans_and_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "parent.json"
            path.write_text('{"count": 1, "all": [2, 3]}')
            module.check_parent({"count": 1, "all": [2, 3]}, path)
            for value in ({"count": True, "all": [2, 3]}, {"count": 1, "all": [2, 4]}, {"count": 1, "all": [2, 3], "extra": 0}):
                with self.assertRaises(ValueError): module.check_parent(value, path)
            for value in ('{"count": NaN}', '{"count": 1, "count": 1}'):
                path.write_text(value)
                with self.assertRaises(ValueError): module.read_json(path)

    def test_three_parent_replay_failures_precede_new_comparison(self):
        with patch.object(module.reddy, "read_selected", return_value={}), \
                patch.object(module.reddy, "make_report", return_value={}), \
                patch.object(module, "audit", return_value={}), \
                patch.object(module, "reconstruct", return_value=({}, {})), \
                patch.object(module, "compare_records") as compare_mock:
            for fail_at in range(3):
                def checker(value, path, seen=[]):
                    seen.append(path)
                    if len(seen) == fail_at + 1:
                        raise ValueError("parent mismatch")
                with self.subTest(fail_at=fail_at), patch.object(module, "check_parent", side_effect=checker), self.assertRaises(ValueError):
                    module.run_audit(Path("unused"))
                compare_mock.assert_not_called()

    def test_all_protected_inputs_reject_early_and_late_aliases_without_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root, reference = Path(temp) / "root", Path(temp) / "reference"
            producer = root / "scripts/producer.py"
            protected = [root / name for name in (*module.FROZEN, module.PLAN, module.HUMAN_PLAN)] + [producer]
            protected += [reference / name for name in module.reddy.SELECTED]
            for i, source in enumerate(protected):
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(f"source-{i}".encode())
            originals = [p.read_bytes() for p in protected]
            with patch.object(module, "ROOT", root), patch.object(module, "__file__", str(producer)):
                for source in protected:
                    for mode in ("direct", "early_symlink", "early_hardlink", "late_symlink", "late_hardlink"):
                        output = source if mode == "direct" else Path(temp) / "output.json"
                        if output != source and output.exists(): output.unlink()
                        def link():
                            if "symlink" in mode: output.symlink_to(source)
                            else: os.link(source, output)
                        if mode.startswith("early"): link()
                        def calculate(*args):
                            if mode.startswith("late"): link()
                            return {"new": "report"}
                        with self.subTest(source=source, mode=mode), \
                                patch("sys.argv", ["audit", "--reference", str(reference), "--output", str(output)]), \
                                patch.object(module, "run_audit", side_effect=calculate) as mocked, \
                                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                            module.main()
                        self.assertEqual(error.exception.code, 1)
                        self.assertEqual(mocked.call_count, int(mode.startswith("late")))
                        self.assertEqual([p.read_bytes() for p in protected], originals)
                        if output != source: output.unlink()

    def test_failed_serialization_and_check_preserve_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output, check = root / "output.json", root / "check.json"
            output.write_bytes(b"preserve")
            check.write_text('{"other": 2}')
            for result, extra in (({"value": float("nan")}, []), ({"value": 1}, ["--check", str(check)])):
                with patch("sys.argv", ["audit", "--reference", str(root), "--output", str(output), *extra]), \
                        patch.object(module, "run_audit", return_value=result), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): module.main()
                self.assertEqual(output.read_bytes(), b"preserve")


if __name__ == "__main__":
    unittest.main()
