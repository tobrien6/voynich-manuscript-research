import contextlib
import copy
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import plot_historical_repeat_nulls as module


def accepted():
    return module.load_reports(module.ROOT / module.GLOBAL_PATH, module.ROOT / module.CONDITIONAL_PATH)


class HistoricalRepeatFigureTests(unittest.TestCase):
    def test_all_four_exact_mean_comparisons_and_scope_residuals_are_retained(self):
        data = module.figure_data(*accepted())
        self.assertEqual(len(data["points"]), 4)
        self.assertEqual([p["observed"] for p in data["points"]],
                         [{"A": 313, "B": 114}, {"A": 314, "B": 115}, {"A": 314, "B": 114}, {"A": 315, "B": 115}])
        for point in data["points"]:
            self.assertEqual(point["all_adjacent_edges"], point["tokens"] - 1)
            self.assertGreater(point["observed_over_exact_mean"]["global"]["A"], 2)
            self.assertLess(point["observed_over_exact_mean"]["native_record"]["A"], 1)
            self.assertGreater(point["observed_over_exact_mean"]["native_record"]["B"], 1)
            scopes = point["A_conditional_scope_residuals"]
            self.assertGreater(scopes["within_record"], 0)
            self.assertLess(scopes["cross_record"], 0)
            self.assertAlmostEqual(scopes["within_record"] + scopes["cross_record"], scopes["total"])

    def test_missing_duplicate_and_reordered_variant_populations_are_rejected(self):
        for mode in ("missing", "duplicate", "reordered"):
            g, c = accepted()
            if mode == "missing":
                c["variants"].pop()
            elif mode == "duplicate":
                c["variants"][1] = copy.deepcopy(c["variants"][0])
            else:
                g["variants"].reverse()
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                module.figure_data(g, c)

    def test_mismatched_inputs_edges_observed_units_and_nulls_are_rejected(self):
        for mode in ("corpus", "edges", "observed", "null", "population_type"):
            g, c = accepted()
            if mode == "corpus":
                c["variants"][0]["flat_corpus_sha256"] = "0" * 64
            elif mode == "edges":
                c["edge_scope"] = "within-record edges only"
            elif mode == "observed":
                c["variants"][0]["observed"]["distinct_repeating_types_B"] += 1
            elif mode == "null":
                c["condition_on"] = "one pooled bag"
            else:
                g["variants"][0]["tokens"] = c["variants"][0]["tokens"] = 37759.0
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                module.figure_data(g, c)

    def test_exact_mean_display_ratio_and_residual_drift_are_rejected(self):
        for mode in ("decimal", "ratio", "scope", "total"):
            g, c = accepted()
            if mode == "decimal":
                c["variants"][0]["exact_conditional_null_means"]["B"]["decimal"] += 1
            elif mode == "ratio":
                g["variants"][0]["observed_over_exact_mean"]["B"] += 1
            elif mode == "scope":
                c["variants"][0]["exact_A_scope_contributions"]["cross_record"] = {"numerator_hex": "0x1", "denominator_hex": "0x1", "decimal": 1.0}
            else:
                c["variants"][0]["observed_minus_conditional_mean"]["A"] = {"numerator_hex": "-0x1", "denominator_hex": "0x1", "decimal": -1.0}
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                module.figure_data(g, c)
        for record in ({"numerator_hex": "0x1", "denominator_hex": "0x0", "decimal": 0},
                       {"numerator_hex": "0x1", "denominator_hex": "0x1", "decimal": True}):
            with self.assertRaises(ValueError):
                module.exact(record)

    def test_changed_report_bytes_fail_before_any_existing_artifact_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "changed-global.json"
            source.write_bytes((module.ROOT / module.GLOBAL_PATH).read_bytes() + b"\n")
            targets = [root / (module.STEM + suffix) for suffix in (".png", ".svg", ".json")]
            for target in targets:
                target.write_bytes(b"preserve prior artifact")
            with patch("sys.argv", ["figure", "--global-input", str(source), "--output-dir", str(root)]):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 1)
            self.assertTrue(all(target.read_bytes() == b"preserve prior artifact" for target in targets))

    def test_report_dependency_plan_producer_and_cross_artifact_aliases_are_blocked(self):
        for kind in ("symlink", "hardlink"):
            for protected in ("global", "conditional", "dependency", "plan", "producer", "other_artifact"):
                with self.subTest(kind=kind, protected=protected), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    output = root / "figures"
                    output.mkdir()
                    g, c = root / "global.json", root / "conditional.json"
                    dep = root / "dependency.dat"
                    plan = root / module.EXTRA_INPUTS[0]
                    plan.parent.mkdir(parents=True)
                    producer = root / "producer.py"
                    other = output / (module.STEM + ".svg")
                    choices = {"global": g, "conditional": c, "dependency": dep, "plan": plan, "producer": producer, "other_artifact": other}
                    for path in choices.values():
                        path.write_bytes(b"preserve protected bytes")
                    target = output / (module.STEM + ".png")
                    source = choices[protected]
                    target.symlink_to(source) if kind == "symlink" else os.link(source, target)
                    with patch.object(module, "ROOT", root), patch.object(module, "__file__", str(producer)):
                        with self.assertRaises(ValueError):
                            module.write_artifacts([b"new png", b"new svg", b"new json"], output, g, c,
                                                   [{"frozen_dependency_hashes": {"dependency.dat": "unused"}}])
                    self.assertEqual(source.read_bytes(), b"preserve protected bytes")
                    self.assertEqual(target.read_bytes(), b"preserve protected bytes")

    def test_direct_report_alias_and_alias_created_after_initial_check_preserve_outputs(self):
        for mode in ("direct", "late_symlink", "late_hardlink"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                g = root / (module.STEM + ".png") if mode == "direct" else root / "global.json"
                c = root / "conditional.json"
                g.write_bytes(b"preserve global report")
                c.write_bytes(b"preserve conditional report")
                png, svg, companion = [root / (module.STEM + suffix) for suffix in (".png", ".svg", ".json")]
                svg.write_bytes(b"preserve existing svg")
                companion.write_bytes(b"preserve existing companion")
                original_guard = module.protect_targets
                calls = 0
                def guard(*args):
                    nonlocal calls
                    result = original_guard(*args)
                    calls += 1
                    if calls == 1 and mode != "direct":
                        png.symlink_to(g) if mode == "late_symlink" else os.link(g, png)
                    return result
                with patch.object(module, "protect_targets", side_effect=guard):
                    with self.assertRaises(ValueError):
                        module.write_artifacts([b"new png", b"new svg", b"new companion"], root, g, c, [])
                self.assertEqual(g.read_bytes(), b"preserve global report")
                self.assertEqual(c.read_bytes(), b"preserve conditional report")
                self.assertEqual(svg.read_bytes(), b"preserve existing svg")
                self.assertEqual(companion.read_bytes(), b"preserve existing companion")


if __name__ == "__main__":
    unittest.main()
