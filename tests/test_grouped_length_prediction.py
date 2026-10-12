from collections import Counter
import copy
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import unittest

from scripts.audit_transcription_images import dependency_components
from scripts.grouped_length_prediction import (
    aggregate, declare_folds, evaluate, fit, fold_for, group_index,
    length_class, model_record, probabilities, transitions,
)


def row(key, group, lengths, label="A", page="f1r"):
    return {"key": key, "group": group, "lengths": lengths, "label": label, "page": page}


class GroupedLengthPredictionTests(unittest.TestCase):
    def test_fixed_classes_and_target_half_include_crossing_pair(self):
        self.assertEqual([length_class(x) for x in (1, 9, 10, 50)], [1, 9, 10, 10])
        self.assertEqual(transitions(row("r", "g", [1, 2, 3, 4, 5])),
                         [(("A", 0), 1, 2), (("A", 0), 2, 3),
                          (("A", 1), 3, 4), (("A", 1), 4, 5)])
        self.assertEqual(transitions(row("r", "g", [1, 2, 3, 4])),
                         [(("A", 0), 1, 2), (("A", 1), 2, 3), (("A", 1), 3, 4)])
        for x in (0, True, -1, 2.5):
            with self.assertRaises(ValueError):
                length_class(x)

    def test_probabilities_match_hand_computed_training_counts(self):
        model = fit([row("r", "g", [1, 2, 1, 2])])
        q0, q1 = probabilities(model, ("A", 0), 1, 2)
        self.assertEqual(q0, float(Fraction(2, 11)))
        self.assertAlmostEqual(q1, float(Fraction(31, 121)))
        q0, q1 = probabilities(model, ("A", 1), 2, 1)
        self.assertEqual(q0, float(Fraction(1, 6)))
        self.assertAlmostEqual(q1, float(Fraction(8, 33)))
        for c in (("A", 0), ("A", 1), ("unseen", 1)):
            for x in range(1, 11):
                probabilities_by_target = [probabilities(model, c, x, y) for y in range(1, 11)]
                self.assertAlmostEqual(sum(p[0] for p in probabilities_by_target), 1)
                self.assertAlmostEqual(sum(p[1] for p in probabilities_by_target), 1)

    def test_unseen_previous_class_backs_off_and_unseen_context_is_uniform(self):
        model = fit([row("r", "g", [1, 2, 1, 2])])
        q0, q1 = probabilities(model, ("A", 0), 10, 2)
        self.assertEqual(q0, q1)
        self.assertEqual(probabilities(model, ("B", 0), 1, 2), (0.1, 0.1))
        for x, y in ((True, 1), (0, 2), (1, 11)):
            with self.assertRaises(ValueError):
                probabilities(model, ("A", 0), x, y)

    def fixture(self):
        rows = [row(f"r{i}", f"g{i}", [1, 2, 1, 2]) for i in range(5)]
        rows.append(row("r5", "g0", [2, 1, 2, 1], page="f1v"))
        return rows, {f"g{i}": i for i in range(5)}

    def test_every_locus_scored_once_and_group_stays_disjoint(self):
        rows, assignments = self.fixture()
        result = evaluate(rows, assignments)
        self.assertEqual(Counter(x["locus_key"] for x in result["loci"]), Counter(x["key"] for x in rows))
        self.assertEqual({x["fold"] for x in result["loci"] if x["group_id"] == "g0"}, {0})
        for fold in result["folds"]:
            self.assertFalse(set(fold["training_group_ids"]) & set(fold["scoring_group_ids"]))
            self.assertEqual(fold["training_loci"] + fold["loci"], len(rows))
        self.assertEqual(result["summary"]["transitions"], 18)
        self.assertEqual(sum(f["transitions"] for f in result["folds"]), 18)

    def test_scoring_fold_values_cannot_change_its_fitted_parameters(self):
        rows, assignments = self.fixture()
        original = evaluate(rows, assignments)
        changed = copy.deepcopy(rows)
        for r in changed:
            if assignments[r["group"]] == 0:
                r["lengths"] = [10, 10, 10, 10]
                r["label"] = "B"
        modified = evaluate(changed, assignments)
        self.assertEqual(original["folds"][0]["fitted_counts"], modified["folds"][0]["fitted_counts"])
        self.assertEqual(original["folds"][0]["fitted_counts_sha256"], modified["folds"][0]["fitted_counts_sha256"])
        self.assertNotEqual(original["folds"][1]["fitted_counts_sha256"], modified["folds"][1]["fitted_counts_sha256"])

    def test_aggregation_and_fixed_preference_use_declared_denominators(self):
        rows, assignments = self.fixture()
        r = evaluate(rows, assignments)
        summary = r["summary"]
        self.assertAlmostEqual(summary["micro_gain_bits_per_transition"],
                               (summary["baseline_loss_bits"] - summary["transition_loss_bits"]) / 18)
        self.assertAlmostEqual(summary["group_macro_gain_bits_per_transition"],
                               sum(g["micro_gain_bits_per_transition"] for g in r["groups"]) / 5)
        self.assertEqual(summary["fixed_diagnostic_preference"],
                         summary["micro_gain_bits_per_transition"] > 0
                         and summary["group_macro_gain_bits_per_transition"] > 0
                         and summary["positive_fold_count"] >= 4)
        self.assertEqual(aggregate(r["loci"])["loci"], 6)

    def test_source_contexts_and_counts_are_separate(self):
        m = fit([row("a", "g", [1, 2, 1], "A"), row("b", "h", [3, 4, 3], "B")])
        self.assertEqual(m["targets"][("A", 0)], {2: 1})
        self.assertEqual(m["targets"][("B", 0)], {4: 1})
        self.assertEqual({r["source_label"] for r in model_record(m)}, {"A", "B"})

    def test_empty_folds_duplicate_loci_or_bad_assignments_fail(self):
        rows, assignments = self.fixture()
        for invalid_rows, invalid_assignments in (
            (rows + [rows[0]], assignments),
            (rows, {**assignments, "extra": 0}),
            (rows, {k: 0 for k in assignments}),
            (rows, {**assignments, "g0": 0.0}),
        ):
            with self.assertRaises(ValueError):
                evaluate(invalid_rows, invalid_assignments)

    def image_fixture(self):
        canvas_rows = [
            {"explicit_folio_sides": "88r", "canvas_uri": "c1"},
            {"explicit_folio_sides": "88v;89r", "canvas_uri": "c2"},
            {"explicit_folio_sides": "89v;90r", "canvas_uri": "c3"},
            {"explicit_folio_sides": "90v", "canvas_uri": "c4"},
        ]
        groups = dependency_components(canvas_rows)
        report = {"dependency_components": groups, "pages": [
            {"page_id": "f88r", "side_reference_status": "side_references_matched", "dependency_group": groups[0]["group_id"]},
            {"page_id": "f90v1", "side_reference_status": "side_references_matched", "dependency_group": groups[0]["group_id"]},
        ], "indexed_canvas_ids_by_leaf": {"88": ["c1", "c2"], "89": ["c2", "c3"], "90": ["c3", "c4"]}}
        return report, canvas_rows

    def test_whole_index_transitive_component_keeps_both_sides_and_panels(self):
        report, canvas_rows = self.image_fixture()
        groups, pages = group_index(report, canvas_rows)
        self.assertEqual(groups, [{"group_id": "yale-leaves:88+89+90", "folio_ids": ["88", "89", "90"]}])
        self.assertEqual(pages["f88r"], pages["f90v1"])
        changed = copy.deepcopy(report)
        changed["pages"][1]["dependency_group"] = "fake-separate-group"
        self.assertIsNone(group_index(changed, canvas_rows)[1]["f90v1"])
        changed = copy.deepcopy(report)
        changed["dependency_components"][0]["folio_ids"] = ["88", "90"]
        with self.assertRaises(ValueError):
            group_index(changed, canvas_rows)

    def test_unsupported_selected_page_and_empty_fold_are_not_silently_dropped(self):
        report, canvas_rows = self.image_fixture()
        with self.assertRaisesRegex(ValueError, "supported dependency"):
            declare_folds([row("x", "ignored", [1, 2, 3], page="f117v")], report, canvas_rows)
        with self.assertRaisesRegex(ValueError, "empty"):
            declare_folds([row("x", "ignored", [1, 2, 3], page="f88r")], report, canvas_rows)
        self.assertEqual(fold_for("yale-leaves:88+89+90"), fold_for("yale-leaves:88+89+90"))

    def test_fold_manifest_retains_full_component_canvases_and_original_keys(self):
        report, canvas_rows = self.image_fixture()
        selected = [row("f88r.1", "ignored", [1, 2, 3], page="f88r"),
                    row("f90v1.1", "ignored", [1, 2, 3], page="f90v1")]
        # Additional independent synthetic leaves make all five fixed folds
        # nonempty; their source values do not affect group hashing.
        for leaf in range(1, 41):
            canvas_rows.append({"explicit_folio_sides": f"{leaf}r", "canvas_uri": f"independent-{leaf}"})
            report["pages"].append({"page_id": f"f{leaf}r", "side_reference_status": "side_references_matched",
                                    "dependency_group": f"yale-leaves:{leaf}"})
            report["indexed_canvas_ids_by_leaf"][str(leaf)] = [f"independent-{leaf}"]
            selected.append(row(f"f{leaf}r.1", "ignored", [1, 2, 3], page=f"f{leaf}r"))
        report["dependency_components"] = dependency_components(canvas_rows)
        assignments, manifest, pages = declare_folds(selected, report, canvas_rows)
        joined = next(m for m in manifest if m["group_id"] == "yale-leaves:88+89+90")
        self.assertEqual(joined["folio_ids"], ["88", "89", "90"])
        self.assertEqual(joined["canvas_ids"], ["c1", "c2", "c3", "c4"])
        self.assertEqual(joined["locus_keys"], ["f88r.1", "f90v1.1"])
        self.assertEqual(pages["f88r"], pages["f90v1"])
        self.assertEqual(set(assignments.values()), set(range(5)))
        self.assertEqual(sum(len(m["locus_keys"]) for m in manifest), len(selected))

    def test_cli_protects_pinned_parent_and_source(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("data/raw/ZL3b-n.txt", "research/transliteration/interior_length_order.json"):
            path = root / name
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(root / "scripts/grouped_length_prediction.py"),
                                     "--output", str(path)], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not overwrite", result.stderr)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
