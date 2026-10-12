import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import reconstruct_historical_tokens as module
from scripts.audit_historical_interlinear import HistoricalRecord


def record(page="f1r", unit="P", line="1", body="a.b="):
    return HistoricalRecord(f"{page}.{unit}.{line};H", page, unit, line, "H", body, 1)


def plan():
    return {
        "ring_policies": ["exclude_R2", "exclude_single_character_tokens"],
        "f66r_column_units": ["M", "L"], "ring_page": "f57v",
        "ring_units": ["R1", "R2", "R3", "R4"], "figure_label_phrases": ["a b"],
        "resolved_operational_exclusions": [
            {"rule": "column", "page": "f49v", "unit": "L"},
            {"rule": "ring", "page": "f70r1", "unit": "C", "line": "1"}],
        "reported_token_count": 10,
    }


class HistoricalReconstructionTests(unittest.TestCase):
    def test_listed_code_is_removed_before_comment_and_unlisted_code_is_retained(self):
        tokens, events, comments = module.normalize_body("a*{&138}b.c*{&140}d=", {"&138"})
        self.assertEqual(tokens, ["ab", "c*d"])
        self.assertEqual(events, [{"raw_offset": 1, "code": "&138", "character": "*"}])
        self.assertEqual(comments, 2)
        self.assertEqual(module.normalize_body("abk{&K}c=", {"&K"})[0], ["abc"])

    def test_comment_removal_filler_joining_and_four_separator_types_are_explicit(self):
        tokens, events, comments = module.normalize_body("a,b.c-d=e!%f{ . , ! &138 }=", {"&138"})
        self.assertEqual(tokens, ["a", "b", "c", "d", "ef"])
        self.assertEqual(events, [])
        self.assertEqual(comments, 1)
        self.assertEqual(module.normalize_body("a{comment}b=", set())[0], ["ab"])

    def test_unreadable_material_survives_and_empty_records_do_not_become_tokens(self):
        self.assertEqual(module.normalize_body("a*.**=", set())[0], ["a*", "**"])
        self.assertEqual(module.normalize_body("*{&138}!=", {"&138"})[0], [])

    def test_unsupported_or_ambiguous_notation_fails(self):
        for body in ("{&138}a=", "a{&138}{&152}=", "A=", "a'b=", "a{nested{x}}=", "a{bad="):
            with self.subTest(body=body), self.assertRaises(ValueError):
                module.normalize_body(body, {"&138", "&152"})

    def test_unit_and_line_selectors_do_not_spread_to_other_records(self):
        records = [record("f49v", "L"), record("f49v", "P"),
                   record("f70r1", "C", "1"), record("f70r1", "C", "1a")]
        summary, corpus = module.make_variant(records, [["xx"]] * 4, plan(), "exclude_R2", "M")
        self.assertEqual([e["locator"] for e in summary["exclusions"]],
                         ["f49v.L.1;H", "f70r1.C.1;H"])
        self.assertEqual([row["tokens"] for row in corpus["records"]], [[], ["xx"], [], ["xx"]])

    def test_exact_label_matching_does_not_delete_a_phrase_from_larger_text(self):
        records = [record(line="1"), record(line="2")]
        summary, corpus = module.make_variant(records, [["a", "b"], ["x", "a", "b"]], plan(), "exclude_R2", "M")
        self.assertEqual(summary["records_excluded_whole"], 1)
        self.assertEqual(corpus["records"][1]["tokens"], ["x", "a", "b"])

    def test_both_ring_interpretations_keep_their_distinct_provenance(self):
        records = [record("f57v", "R2"), record("f57v", "R4")]
        tokens = [["a", "bc", "*"], ["d", "ef", "g"]]
        s1, c1 = module.make_variant(records, tokens, plan(), "exclude_R2", "M")
        s2, c2 = module.make_variant(records, tokens, plan(), "exclude_single_character_tokens", "M")
        self.assertEqual([row["tokens"] for row in c1["records"]], [[], ["d", "ef", "g"]])
        self.assertEqual([row["tokens"] for row in c2["records"]], [["bc"], ["ef"]])
        self.assertEqual(c2["records"][1]["original_token_indices"], [1])
        self.assertEqual(s1["single_character_ring_tokens_removed"], 0)
        self.assertEqual(s2["single_character_ring_tokens_removed"], 4)

    def test_column_choices_and_original_record_order_are_preserved(self):
        records = [record("f66r", "L"), record("f66r", "M"), record("f2r"), record("f1r")]
        tokens = [["left"], ["middle"], ["two"], ["one"]]
        _, corpus = module.make_variant(records, tokens, plan(), "exclude_R2", "L")
        self.assertEqual([t["token"] for t in corpus["flat_tokens_with_provenance"]], ["middle", "two", "one"])
        self.assertEqual(corpus["flat_tokens_with_provenance"][-1]["locator"], "f1r.P.1;H")
        with self.assertRaises(ValueError):
            module.make_variant(records, tokens, plan(), "other", "M")

    def test_every_declared_variant_reconciles_counts_and_export_hashes(self):
        report, corpus = module.reconstruct()
        self.assertEqual(len(report["variants"]), 4)
        self.assertEqual(len(corpus["variants"]), 4)
        self.assertEqual(report["corpus_export_sha256"], hashlib.sha256(module.encoded(corpus)).hexdigest())
        self.assertEqual(report["source_records_selected"], 5214)
        for summary, export in zip(report["variants"], corpus["variants"], strict=True):
            self.assertEqual(summary["record_corpus_sha256"], hashlib.sha256(module.encoded(export["records"])).hexdigest())
            self.assertEqual(summary["flat_corpus_sha256"], hashlib.sha256(module.encoded(export["flat_tokens_with_provenance"])).hexdigest())
            self.assertEqual(summary["retained_tokens"], len(export["flat_tokens_with_provenance"]))
            self.assertEqual(report["syntactic_normalization"]["tokens_before_manual_exclusions"],
                             summary["retained_tokens"] + summary["normalized_tokens_removed_whole"]
                             + summary["single_character_ring_tokens_removed"])

    def test_drift_fails_before_existing_output_is_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("data/historical/interlinear-16e6.json", "data/historical/text16e6.zip",
                         "research/historical/parser-plan.json"):
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(module.ROOT / name, destination)
            output = root / "output.json"
            output.write_text("preserve")
            archive = root / "data/historical/text16e6.zip"
            archive.write_bytes(archive.read_bytes() + b"drift")
            with patch.object(module, "ROOT", root), patch("sys.argv", ["reconstruct", "--output", str(output)]):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 1)
            self.assertEqual(output.read_text(), "preserve")

    def test_cli_protects_inputs_and_requires_distinct_output_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("data/historical/interlinear-16e6.json", "data/historical/text16e6.zip",
                         "research/historical/parser-plan.json"):
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(module.ROOT / name, destination)
            parser_file = root / "parser.py"
            parser_file.write_text("invented parser fixture")
            paths = [root / "data/historical/interlinear-16e6.json",
                     root / "data/historical/text16e6.zip",
                     root / "research/historical/parser-plan.json", parser_file]
            for path in paths:
                before = path.read_bytes()
                with patch.object(module, "ROOT", root), patch.object(module, "__file__", str(parser_file)):
                    with patch("sys.argv", ["reconstruct", "--corpus-output", str(path)]):
                        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                            module.main()
                        self.assertEqual(error.exception.code, 1)
                self.assertEqual(path.read_bytes(), before)
            output = root / "output.json"
            output.write_text("preserve")
            with patch.object(module, "ROOT", root), patch("sys.argv", ["reconstruct", "--output", str(output), "--corpus-output", str(output)]):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 1)
            self.assertEqual(output.read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
