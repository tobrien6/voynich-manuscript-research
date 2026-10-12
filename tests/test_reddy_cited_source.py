import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_reddy_cited_source as module


def rows(groups, page="f81v"):
    return [{"header": (page, "P", str(i + 1), "H"), "native_file_line": i * 2 + 1, "tokens": group}
            for i, group in enumerate(groups)]


class ReddyCitedSourceTests(unittest.TestCase):
    def test_every_line_masked_candidate_duplicate_and_context_case_remains(self):
        raw = b"\n<f1r> {comment}\n<f1r.1> AA.[B*]{note}#\n{outer\n<f2r.9> HIDDEN\n{nest} end}\n<f1r.1> C\n<f3r.1> D\nopaque\n"
        x = module.native_census(raw)
        self.assertEqual(x["physical_LF_lines"], 9)
        self.assertEqual(x["line_classification"], {"blank": 1, "comment_only": 3, "page_envelope": 1, "record_envelope": 3, "unrecognized_outside_comment": 1})
        self.assertTrue(x["comment_lexical_model_valid"])
        self.assertEqual(len(x["all_raw_prefix_envelope_candidates"]), 5)
        masked = x["all_raw_prefix_envelope_candidates"][2]
        self.assertEqual(masked["literal_locator"], "f2r.9")
        self.assertFalse(masked["recognized_as_active"])
        self.assertEqual(x["duplicate_record_locators"], [{"literal_locator": "f1r.1", "physical_file_lines": [3, 7]}])
        self.assertEqual(x["out_of_context_records"][0]["literal_locator"], "f3r.1")
        self.assertEqual(x["pages"], [{"literal_page_prefix": "f1r", "record_envelopes": 2}, {"literal_page_prefix": "f3r", "record_envelopes": 1}])
        counts = {r["codepoint"]: r["count"] for r in x["record_body_nonwhitespace_notation_counts_outside_comments"]}
        self.assertEqual(sum(counts.values()), 10)
        for point in ("U+005B", "U+005D", "U+002A", "U+002E", "U+0023"): self.assertEqual(counts[point], 1)
        self.assertFalse(x["word_tokenization_performed"])

    def test_physical_CRLF_transport_and_lexical_errors_are_retained(self):
        raw = b"<f1r>\r\n<f1r.1> \xe9 }{unclosed"
        x = module.native_census(raw)
        self.assertFalse(x["final_LF"])
        self.assertEqual(x["CRLF_sequences"], 1)
        self.assertEqual(x["all_active_page_headers"][0]["raw_physical_line_sha256"], hashlib.sha256(b"<f1r>\r").hexdigest())
        self.assertFalse(x["comment_lexical_model_valid"])
        self.assertEqual([r["error"] for r in x["all_comment_model_errors"]], ["unmatched_closing_brace", "unclosed_comment_at_eof"])
        self.assertIn({"codepoint": "U+00E9", "count": 1}, x["record_body_nonwhitespace_notation_counts_outside_comments"])
        self.assertEqual(sum(x["line_classification"].values()), 2)

    def test_locator_comments_are_never_repaired_into_native_keys(self):
        x = module.native_census(b"<f{comment}1r.2> AA\n{leading}<f1r.3> BB\n<f1r.> {empty}\n")
        self.assertEqual(x["line_classification"]["unrecognized_outside_comment"], 2)
        self.assertEqual(x["all_active_record_envelopes"][0]["opaque_suffix_after_first_dot"], "")
        self.assertFalse(x["all_raw_prefix_envelope_candidates"][0]["literal_syntax_supported"])

    def test_literal_figure_equality_and_complete_source_descriptors(self):
        tokens = ["A", "B*", "**"]
        x = module.compare_figure(tokens, rows([["A"], ["B*", "**"]]), "f81v")
        self.assertTrue(x["exact_token_vector_equal"])
        self.assertEqual(x["all_mismatch_positions"], [])
        self.assertEqual(x["figure_vector_sha256"], x["reference_vector_sha256"])
        self.assertEqual([r["tokens"] for r in x["all_reference_record_descriptors"]], [1, 2])
        self.assertEqual([r["physical_file_line"] for r in x["all_reference_record_descriptors"]], [1, 3])

    def test_symbol_changes_missing_page_and_both_length_tails_remain(self):
        x = module.compare_figure(["I", "O", "**", "TAIL"], rows([["1", "0", "*"]]), "f81v")
        self.assertFalse(x["exact_token_vector_equal"])
        self.assertEqual([r["page_token_index"] for r in x["all_mismatch_positions"]], [0, 1, 2, 3])
        self.assertIsNone(x["all_mismatch_positions"][-1]["reference_token_sha256"])
        self.assertEqual(x["all_mismatch_positions"][1]["reference_provenance"]["local_token_index"], 1)
        y = module.compare_figure(["A"], rows([["A", "B"]]), "f81v")
        self.assertIsNone(y["all_mismatch_positions"][0]["figure_token_sha256"])
        z = module.compare_figure(["A"], rows([["A"]], page="F81v"), "f81v")
        self.assertFalse(z["reference_page_present"])
        self.assertEqual(len(z["all_mismatch_positions"]), 1)

    def test_figure_anchors_ascii_and_native_provenance_failures(self):
        figure = {"first_token": "BAR", "last_two_tokens": ["OPON", "OEFOE"]}
        self.assertEqual(module.figure_tokens(b"BAR A*\nOPON OEFOE\n", figure), ["BAR", "A*", "OPON", "OEFOE"])
        for raw in (b"Bar OPON OEFOE", b"BAR A? OPON OEFOE", b"BAR OPON WRONG", "BAR é OPON OEFOE".encode()):
            with self.assertRaises(ValueError): module.figure_tokens(raw, figure)
        for mode in ("duplicate", "line", "header"):
            changed = rows([["A"], ["B"]])
            if mode == "duplicate": changed[1]["header"] = changed[0]["header"]
            elif mode == "line": changed[1]["native_file_line"] = False
            else: changed[0]["header"] = ("f81v", "P", "1")
            with self.assertRaises(ValueError): module.compare_figure(["A", "B"], changed, "f81v")

    def test_extractor_version_byte_failure_and_exact_fixed_arguments(self):
        figure = module.read_json(module.ROOT / module.PLAN)["figure"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "figure1.txt").write_bytes(b"fixed text")
            good_version = subprocess.CompletedProcess([], 0, stdout=b"", stderr=b"pdftotext version 24.04.0\n")
            bad_version = subprocess.CompletedProcess([], 0, stdout=b"", stderr=b"pdftotext version 25.0\n")
            extracted = subprocess.CompletedProcess([], 0, stdout=b"fixed text", stderr=b"")
            with patch.object(module.subprocess, "run", side_effect=[good_version, extracted]) as run:
                self.assertEqual(module.extract_figure(root, figure), b"fixed text")
                self.assertEqual(run.call_args_list[1].args[0], ["pdftotext", "-f", "2", "-l", "2", "-r", "72", "-x", "314", "-y", "373", "-W", "226", "-H", "317", "-layout", "-nopgbrk", str(root / "paper.pdf"), "-"])
            with patch.object(module.subprocess, "run", return_value=bad_version), self.assertRaises(ValueError): module.extract_figure(root, figure)
            with patch.object(module.subprocess, "run", side_effect=[good_version, subprocess.CompletedProcess([], 0, stdout=b"changed", stderr=b"")]), self.assertRaises(ValueError): module.extract_figure(root, figure)

    def test_all_dependencies_and_fixed_cohort_choices_are_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in (*module.FROZEN, module.PLAN):
                target = root / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(module.ROOT / name, target)
            module.load_plan(root)
            for name in module.FROZEN:
                p = root / name; original = p.read_bytes(); p.write_bytes(original + b" ")
                with self.assertRaises(ValueError): module.load_plan(root)
                p.write_bytes(original)
            plan = module.read_json(root / module.PLAN)
            for key, value in (("current_cited_tokenization", True), ("comparison_cases", ["full"]), ("plan_version", True)):
                (root / module.PLAN).write_text(json.dumps({**plan, key: value}))
                with self.assertRaises(ValueError): module.load_plan(root)
            changed = {**plan, "figure": {**plan["figure"], "crop_y": 372}}
            (root / module.PLAN).write_text(json.dumps(changed))
            with self.assertRaises(ValueError): module.load_plan(root)

    def test_reference_identity_and_complete_parent_failure_precede_scoring(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); pins = {}
            for name in module.REFERENCES:
                raw = b"same" if name in module.REFERENCES[:2] else name.encode()
                (root / name).write_bytes(raw); pins[name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
            plan = {"reference_files": pins}
            module.read_references(root, plan)
            for name in module.REFERENCES:
                p = root / name; original = p.read_bytes(); p.write_bytes(original + b" ")
                with self.assertRaises(ValueError): module.read_references(root, plan)
                p.write_bytes(original)
        with patch.object(module, "read_references", return_value={}), patch.object(module.parent, "read_selected", return_value={}), \
                patch.object(module.parent, "make_report", return_value={}), patch.object(module, "extract_figure") as extract, \
                patch.object(module, "check_report", side_effect=ValueError("parent mismatch")), self.assertRaises(ValueError):
            module.run_audit(Path("unused"))
        extract.assert_not_called()

    def test_all_90_early_late_aliases_preserve_all_protected_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root, reference = Path(temp) / "root", Path(temp) / "reference"; producer = root / "scripts/producer.py"
            paths = [root / n for n in (*module.FROZEN, module.PLAN, module.HUMAN_PLAN)] + [producer]
            paths += [reference / n for n in module.REFERENCES] + [reference / "reddy" / n for n in module.parent.SELECTED]
            for i, p in enumerate(paths): p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(f"original-{i}".encode())
            originals = [p.read_bytes() for p in paths]; count = 0
            with patch.object(module, "ROOT", root), patch.object(module, "__file__", str(producer)):
                for source in paths:
                    for mode in ("direct", "early_symlink", "early_hardlink", "late_symlink", "late_hardlink"):
                        output = source if mode == "direct" else Path(temp) / "output.json"
                        def link():
                            if "symlink" in mode: output.symlink_to(source)
                            else: os.link(source, output)
                        if mode.startswith("early"): link()
                        def run(*args):
                            if mode.startswith("late"): link()
                            return {"result": 1}
                        with patch.object(module, "run_audit", side_effect=run) as mocked, \
                                patch("sys.argv", ["audit", "--reference", str(reference), "--output", str(output)]), \
                                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): module.main()
                        self.assertEqual(mocked.call_count, int(mode.startswith("late")))
                        self.assertEqual([p.read_bytes() for p in paths], originals)
                        if output != source: output.unlink()
                        count += 1
            self.assertEqual(count, 90)

    def test_failed_serialization_check_and_strict_json_preserve_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); output, check = root / "output.json", root / "check.json"
            output.write_bytes(b"preserve"); check.write_text('{"other": 0}')
            for result, extra in (({"value": float("nan")}, []), ({"value": 1}, ["--check", str(check)])):
                with patch.object(module, "run_audit", return_value=result), patch("sys.argv", ["audit", "--reference", str(root), "--output", str(output), *extra]), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): module.main()
                self.assertEqual(output.read_bytes(), b"preserve")
            for invalid in ('{"x": NaN}', '{"x": 1, "x": 1}'):
                check.write_text(invalid)
                with self.assertRaises(ValueError): module.read_json(check)


if __name__ == "__main__": unittest.main()
