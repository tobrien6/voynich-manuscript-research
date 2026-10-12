from collections import Counter
import contextlib
import copy
import hashlib
import io
import itertools
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import paired_symbol_entropy as analysis
from scripts.eva_unit_sensitivity import ordered_patterns
from scripts.ivtff import parse_ivtff


def plan():
    return json.loads((analysis.ROOT / analysis.PLAN_PATH).read_bytes())


def paired(left, right=None):
    return [(dict(id=sid), parse_ivtff(text)) for sid, text in
            zip(analysis.SOURCE_IDS, (left, right if right is not None else left))]


def fixture_root(root):
    record = plan()
    for name in analysis.PIN_PATHS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"synthetic pin fixture; never executed")
    catalog = {"sources": [{"id": "fixture", "path": "data/raw/fixture.txt"}]}
    (root / "data/transliterations.json").write_text(json.dumps(catalog))
    raw = root / "data/raw/fixture.txt"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"synthetic original input")
    settings = {"policies": [{"id": name, "patterns": []} for name in analysis.UNIT_IDS]}
    (root / record["unit_policy_file"]).write_text(json.dumps(settings))
    record["input_pins"] = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                            for name in analysis.PIN_PATHS}
    (root / analysis.PLAN_PATH).parent.mkdir(parents=True)
    (root / analysis.PLAN_PATH).write_text(json.dumps(record))
    (root / analysis.PLAN_NOTE).write_text("Synthetic plan note\n")
    return record


class PairedSymbolEntropyTests(unittest.TestCase):
    def test_manual_branching_and_pooled_edge_weighting(self):
        result = analysis.pooled_statistics([["a", "a", "b"], ["c", "d"]])
        self.assertEqual((result["unit_count"], result["edge_count"], result["terminal_unit_count"]), (5, 3, 2))
        self.assertAlmostEqual(result["bits"]["conditional_successor_entropy"], 2 / 3)
        augmented = analysis.pooled_statistics([["a", "a", "b"], ["c", "d"], ["x"]])
        self.assertEqual(augmented["bits"]["conditional_successor_entropy"],
                         result["bits"]["conditional_successor_entropy"])
        self.assertEqual(augmented["segments_without_edges"], 1)
        self.assertNotEqual(augmented["bits"]["full_unit_entropy"], result["bits"]["full_unit_entropy"])

    def test_all_singletons_have_null_conditional_estimate(self):
        result = analysis.pooled_statistics([["a"], ["b"]])
        self.assertEqual(result["bits"]["full_unit_entropy"], 1)
        self.assertEqual(result["edge_count"], 0)
        self.assertIsNone(result["bits"]["conditional_successor_entropy"])
        self.assertIsNone(result["bits"]["pair_minus_full_unit_entropy"])
        self.assertEqual(result["directed_pair_counts"], [])

    def test_declared_boundaries_do_not_introduce_hidden_edges(self):
        rows = [["ab", "cd"], ["ef"]]
        within = analysis.segments_for(rows, (), "within_token")
        spaced = analysis.segments_for(rows, (), "within_locus_with_space")
        self.assertEqual(within, [["a", "b"], ["c", "d"], ["e", "f"]])
        self.assertEqual(spaced, [["a", "b", "<SPACE>", "c", "d"], ["e", "f"]])
        self.assertEqual(analysis.pooled_statistics(within)["edge_count"], 3)
        self.assertEqual(analysis.pooled_statistics(spaced)["edge_count"], 5)
        self.assertEqual(analysis.pooled_statistics(spaced)["terminal_unit_count"], 2)
        for segments in (within, spaced):
            self.assertFalse(any(row["predecessor"] == "d" and row["successor"] == "e"
                                 for row in analysis.pooled_statistics(segments)["directed_pair_counts"]))

    def test_grouping_preserves_case_and_never_crosses_tokens(self):
        rows = [["chiin", "c", "h", "Chsh"]]
        original = copy.deepcopy(rows)
        patterns = ordered_patterns(["ch", "iin", "Ch", "sh"])
        segments = analysis.segments_for(rows, patterns, "within_token")
        self.assertEqual(segments, [["ch", "iin"], ["c"], ["h"], ["Ch", "sh"]])
        self.assertEqual(["".join(units) for units in segments], rows[0])
        self.assertEqual(rows, original)

    def test_exhaustive_small_segment_populations_match_successor_distributions(self):
        sequences = [list(values) for n in range(1, 4) for values in itertools.product("ab", repeat=n)]
        for first, second in itertools.product(sequences, repeat=2):
            segments = [first, second]
            successors = {}
            for units in segments:
                for left, right in zip(units, units[1:]):
                    successors.setdefault(left, []).append(right)
            edges = sum(map(len, successors.values()))
            result = analysis.pooled_statistics(segments)
            if not edges:
                self.assertIsNone(result["bits"]["conditional_successor_entropy"])
                continue
            expected = 0.0
            for values in successors.values():
                h = -sum(n / len(values) * math.log2(n / len(values)) for n in Counter(values).values())
                expected += len(values) / edges * h
            self.assertAlmostEqual(result["bits"]["conditional_successor_entropy"], expected)
            self.assertAlmostEqual(result["bits"]["pair_minus_full_unit_entropy"] - expected,
                                   result["bits"]["difference_due_to_full_marginal"])

    def test_one_common_cohort_accounts_for_ambiguity_fragments_drawings_and_singletons(self):
        start = "#=IVTFF Eva- 2.0 M\n<f1r>\n"
        left = (start + "<f1r.1,@P0> ab,cd.ef\n<f1r.2,+P0> [a:b].cd\n"
                "<f1r.3,=P0> a.b\n<f1r.4,+P0> a<->b\n<f1r.5,+P0> a\n<f1r.6,+P0> q\n")
        right = left.replace("[a:b].cd", "a.cd").replace("<f1r.6,+P0>", "<f1r.6,+P1>")
        sources = paired(left, right)
        unchanged = copy.deepcopy(sources)
        maps, retained, selection = analysis.prepare(sources, plan())
        self.assertEqual(retained, ["f1r.1", "f1r.5"])
        self.assertEqual((selection["shared_present_P0_loci"], selection["retained_loci"], selection["excluded_loci"]), (5, 2, 3))
        self.assertEqual(selection["source_only_present_P0_keys"], {"ZL3b": ["f1r.6"], "IT2a": []})
        self.assertEqual({item["locus_key"] for item in selection["exclusions"]}, {"f1r.2", "f1r.3", "f1r.4"})
        self.assertTrue(any("alternative_reading" in key for key in selection["reason_counts_may_overlap"]))
        self.assertTrue(any("drawing_interruption" in key for key in selection["reason_counts_may_overlap"]))
        self.assertEqual(maps["ZL3b", "split"]["f1r.1"]["tokens"], ["ab", "cd", "ef"])
        self.assertEqual(maps["ZL3b", "join"]["f1r.1"]["tokens"], ["abcd", "ef"])
        self.assertEqual(sources, unchanged)

    def test_duplicate_or_missing_sources_and_duplicate_keys_fail(self):
        sources = paired("#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> a\n")
        for invalid in (sources[:1], sources + [sources[0]]):
            with self.assertRaisesRegex(ValueError, "exactly one"):
                analysis.prepare(invalid, plan())
        with self.assertRaisesRegex(ValueError, "duplicate source locus"):
            analysis.record_index([{"locus_key": "f1r.1"}] * 2)

    def test_changed_input_pins_and_plan_fields_fail_before_loading_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record = fixture_root(root)
            analysis.load_plan(root)
            path = root / "scripts/ivtff.py"
            before = path.read_bytes()
            path.write_bytes(b"changed fixture")
            with self.assertRaisesRegex(ValueError, "pinned input changed"):
                analysis.load_plan(root)
            path.write_bytes(before)
            record["minimum_tokens"] = True
            (root / analysis.PLAN_PATH).write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "changed plan field"):
                analysis.load_plan(root)

    def test_output_aliases_of_inputs_fail_before_corpus_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture_root(root)
            original = root / "data/raw/fixture.txt"
            symlink, hardlink = root / "symlink.json", root / "hardlink.json"
            symlink.symlink_to(original)
            os.link(original, hardlink)
            before = original.read_bytes()
            for destination in (original, symlink, hardlink):
                with self.subTest(destination=destination):
                    stderr = io.StringIO()
                    with patch.object(analysis, "ROOT", root), patch.object(analysis, "make_report") as run, \
                            patch("sys.argv", ["audit", "--output", str(destination)]), \
                            contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as failure:
                        analysis.main()
                    self.assertEqual(failure.exception.code, 1)
                    run.assert_not_called()
                    self.assertIn("including file aliases", stderr.getvalue())
                    self.assertEqual(original.read_bytes(), before)

    def test_invalid_segment_or_boundary_populations_fail(self):
        for segments in ([], [[]], [[""]], [[1]]):
            with self.assertRaises(ValueError):
                analysis.pooled_statistics(segments)
        with self.assertRaises(ValueError):
            analysis.segments_for([["a"]], (), "across_loci")
        with self.assertRaises(ValueError):
            analysis.segments_for([[]], (), "within_token")


if __name__ == "__main__":
    unittest.main()
