from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import unittest

from scripts import grouped_predictor_controls as module


class Draws:
    def __init__(self, values):
        self.values = iter(values)
        self.bounds = []

    def below(self, bound):
        self.bounds.append(bound)
        value = next(self.values)
        assert value in range(bound)
        return value


def parent_fixture():
    rows = [{"locus_key": f"f{i+1}r.1", "page_id": f"f{i+1}r", "group_id": f"g{i}",
             "source_label": "A" if i % 2 else "B", "transitions": 3, "fold": i}
            for i in range(5)]
    return {"method": "grouped-length-prediction-v1", "selection": {"loci": 5},
            "folds": {"count": 5, "group_assignments": [
                {"group_id": row["group_id"], "fold": row["fold"],
                 "locus_keys": [row["locus_key"]], "source_page_ids": [row["page_id"]]}
                for row in rows]},
            "treatments": [{"source_id": "ZL3b", "spacing": "split", "loci": rows}]}


class GroupedPredictorControlTests(unittest.TestCase):
    def test_same_draws_give_exact_boundary_processes_and_are_always_consumed(self):
        expected = {0: [1, 10, 5], 1: [1, 1, 5], 3: [1, 1, 1]}
        for quarters, values in expected.items():
            draws = Draws([0, 0, 9, 1, 4])
            self.assertEqual(module.sequence(3, quarters, draws), values)
            self.assertEqual(draws.bounds, [10, 4, 10, 4, 10])
        # Strict u < k: u=3 uses the innovation even for k=3.
        self.assertEqual(module.sequence(3, 3, Draws([0, 3, 4, 3, 9])), [1, 5, 10])
        for size, quarters in ((2, 1), (True, 1), (3, 2), (3, True)):
            with self.assertRaises(ValueError):
                module.sequence(size, quarters, Draws([]))

    def test_oracle_matches_independent_closed_form_from_match_counts(self):
        rows = [{"lengths": [1, 1, 2, 3, 3]}]
        for quarters, diagonal, off in ((0, .1, .1), (1, .325, .075), (3, .775, .025)):
            result = module.oracle_score(rows, quarters)
            expected = 2 * math.log2(10 * diagonal) + 2 * math.log2(10 * off)
            self.assertEqual(result["transitions"], 4)
            self.assertEqual(result["equal_adjacent_classes"], 2)
            self.assertAlmostEqual(result["gain_bits"], expected)
            self.assertAlmostEqual(result["known_process_loss_bits"], -2 * math.log2(diagonal) - 2 * math.log2(off))
            self.assertAlmostEqual(module.ideal_gain(quarters),
                                   diagonal * math.log2(10 * diagonal) + 9 * off * math.log2(10 * off))
            self.assertAlmostEqual(diagonal + 9 * off, 1)
        self.assertEqual(module.oracle_score(rows, 0)["gain_bits"], 0)
        self.assertEqual(module.ideal_gain(0), 0)
        for values in ([], [1, 2], [1, True, 2], [1, 11, 2]):
            with self.assertRaises(ValueError):
                module.oracle_score([{"lengths": values}], 1)

    def test_layout_uses_only_metadata_and_retains_labels_and_all_folds(self):
        data = parent_fixture()
        templates, assignments = module.layout_from_report(data)
        changed = deepcopy(data)
        for row in changed["treatments"][0]["loci"]:
            row["gain_bits"] = "ignored observed gain"
            row["baseline_loss_bits"] = "ignored observed model"
            row["lengths"] = "ignored observed classes"
        self.assertEqual(module.layout_from_report(changed), (templates, assignments))
        rows = module.simulate(templates, 0, "independent_uniform")
        self.assertEqual([r["label"] for r in rows], [r["label"] for r in templates])
        self.assertTrue(all(len(r["lengths"]) == 4 for r in rows))
        result = module.estimator.evaluate(rows, assignments)
        self.assertEqual(result["summary"]["transitions"], 15)
        self.assertEqual(len(result["groups"]), 5)
        for fold in result["folds"]:
            self.assertFalse(set(fold["training_group_ids"]) & set(fold["scoring_group_ids"]))
        compact = module.compact_evaluation(result)
        self.assertEqual(compact["summary"], result["summary"])
        self.assertEqual(compact["groups"], result["groups"])
        self.assertTrue(all("fitted_counts" not in fold and "fitted_counts_sha256" in fold
                            for fold in compact["folds"]))

    def test_incomplete_duplicate_or_inconsistent_layout_is_rejected(self):
        mutations = [lambda d: d["treatments"][0]["loci"].pop(),
                     lambda d: d["treatments"].append(deepcopy(d["treatments"][0])),
                     lambda d: d["treatments"][0]["loci"][0].update(fold=True),
                     lambda d: d["treatments"][0]["loci"][0].update(source_label=""),
                     lambda d: d["treatments"][0]["loci"][0].update(transitions=2.5),
                     lambda d: d["treatments"][0]["loci"][0].update(page_id="wrong"),
                     lambda d: d["folds"]["group_assignments"][0]["locus_keys"].append("f2r.1")]
        for mutation in mutations:
            data = parent_fixture()
            mutation(data)
            with self.assertRaises(ValueError):
                module.layout_from_report(data)

    def test_streams_replay_and_separate_replicates_cases_and_loci(self):
        templates, _ = module.layout_from_report(parent_fixture())
        for row in templates:
            row["interior_size"] = 24
        original = deepcopy(templates)
        rows = module.simulate(templates, 0, "independent_uniform")
        self.assertEqual(rows, module.simulate(templates, 0, "independent_uniform"))
        self.assertEqual(templates, original)
        self.assertNotEqual(rows, module.simulate(templates, 1, "independent_uniform"))
        self.assertNotEqual(rows, module.simulate(templates, 0, "persistence_quarter"))
        self.assertEqual(len({tuple(row["lengths"]) for row in rows}), 5)
        # Verify the first draw directly from the specified byte-stream definition.
        parameters = [module.METHOD, 20261012, 0, "independent_uniform", templates[0]["key"]]
        key = hashlib.sha256(json.dumps(parameters, separators=(",", ":")).encode()).digest()
        counter = 0
        while True:
            first = hashlib.sha256(key + counter.to_bytes(16, "big")).digest()[0]
            if first < 250:
                break
            counter += 1
        self.assertEqual(rows[0]["lengths"][0], first % 10 + 1)
        for replicate, case in ((True, "independent_uniform"), (64, "independent_uniform"), (0, "other")):
            with self.assertRaises(ValueError):
                module.simulate(templates, replicate, case)

    def test_aggregation_retains_adverse_values_and_uses_every_replicate(self):
        records = [{"replicate": i, "summary": {
            "fixed_diagnostic_preference": i == 0,
            "micro_gain_bits_per_transition": gain,
            "group_macro_gain_bits_per_transition": gain / 2,
            "locus_macro_gain_bits_per_transition": gain / 4},
            "oracle": {"gain_bits_per_transition": 0}} for i, gain in enumerate((1, -3))]
        summary = module.summarize_replicates(records)
        self.assertEqual(summary["replicates"], 2)
        self.assertEqual(summary["fixed_criterion_hits"], 1)
        self.assertEqual(summary["micro_gain_bits_per_transition"], {"mean": -1, "min": -3, "max": 1})
        for invalid in ([], [records[0], records[0]]):
            with self.assertRaises(ValueError):
                module.summarize_replicates(invalid)

    def test_output_guards_include_resolved_and_hardlink_aliases(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            names = set(module.PINS) | {module.PLAN}
            for name in names:
                source = root / name
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("synthetic protected fixture")
                for alias_type in ("direct", "symbolic", "hard"):
                    alias = root / f"{source.name}-{alias_type}"
                    if alias_type == "direct":
                        alias = source
                    elif alias_type == "symbolic":
                        alias.symlink_to(source)
                    else:
                        os.link(source, alias)
                    with self.assertRaisesRegex(ValueError, "must not overwrite"):
                        module.protect_output(alias, root)
                    self.assertEqual(source.read_text(), "synthetic protected fixture")
            for name in ("data/new.json", "scripts/new.py"):
                with self.assertRaises(ValueError):
                    module.protect_output(root / name, root)
            module.protect_output(root / "separate-report.json", root)

    def test_pin_drift_fails_before_layout_is_interpreted(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in module.PINS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((module.ROOT / name).read_bytes())
            path = root / module.PARENT
            path.write_bytes(path.read_bytes() + b"drift")
            with self.assertRaisesRegex(ValueError, "pinned input changed"):
                module.load_layout(root)


if __name__ == "__main__":
    unittest.main()
