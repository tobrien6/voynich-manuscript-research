import contextlib
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_historical_reddy_types as module
from tests.test_historical_reddy_envelopes import fixture


def graph(h_groups, r_groups, ordinals=None):
    ordinals = list(range(len(h_groups))) if ordinals is None else ordinals
    records = [{"key": ["f1r", "P1", str(i + 1), "H"], "h_ordinal": ordinal,
                "reddy_ordinal": i, "h_tokens": a, "reddy_tokens": b}
               for i, (a, b, ordinal) in enumerate(zip(h_groups, r_groups, ordinals, strict=True))]
    return module.compare_types(records)


def sha(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class HistoricalReddyTypeTests(unittest.TestCase):
    def test_bijective_relabeling_preserves_full_partition_and_all_repeats(self):
        x = graph([list("aa"), list("aba")], [list("XX"), list("XYX")])
        self.assertTrue(x["equality_partition_identical"])
        self.assertEqual(x["type_pair_edges"], 2)
        for pop in x["populations"].values():
            self.assertEqual((pop["tokens"], pop["types"], pop["A_equal_edges"], pop["B_repeated_types"]), (5, 2, 2, 1))
            self.assertEqual(pop["B_by_edge_class"], {"within_record": 1, "joining": 1})
            self.assertEqual(pop["B_overlap_within_and_joining"], 1)
        self.assertEqual(x["all_discordant_repeat_events"], [])
        self.assertEqual(len(x["all_joining_edges"]), 1)
        pair = next(e for e in x["edges"] if e["h_type_sha256"] == sha("a"))
        self.assertEqual(pair["support_positions"], [[0, 0], [0, 1], [1, 0], [1, 2]])
        self.assertEqual(pair["occurrences"], 4)

    def test_merges_splits_and_nonfunctional_both_directions_remain(self):
        cases = [([list("ab")], [list("XX")], True, False, "reddy_only_equal"),
                 ([list("aa")], [list("XY")], False, True, "h_only_equal"),
                 ([list("aabb")], [list("XYXY")], False, False, "h_only_equal")]
        for a, b, hf, rf, event in cases:
            with self.subTest(a=a, b=b):
                x = graph(a, b)
                self.assertFalse(x["equality_partition_identical"])
                self.assertEqual(x["populations"]["h"]["functional_to_other_domain"], hf)
                self.assertEqual(x["populations"]["reddy"]["functional_to_other_domain"], rf)
                self.assertGreater(x["repeat_event_matrix"]["all"][event], 0)
                self.assertTrue(x["all_discordant_repeat_events"])

    def test_same_A_B_totals_can_hide_different_events_and_partitions(self):
        x = graph([list("aabc")], [list("XYZZ")])
        self.assertEqual([x["populations"][s]["A_equal_edges"] for s in ("h", "reddy")], [1, 1])
        self.assertEqual([x["populations"][s]["B_repeated_types"] for s in ("h", "reddy")], [1, 1])
        self.assertFalse(x["equality_partition_identical"])
        self.assertEqual([e["flat_left_index"] for e in x["all_discordant_repeat_events"]], [0, 2])
        y = graph([list("aba")], [list("XYZ")])
        self.assertEqual(y["all_discordant_repeat_events"], [])
        self.assertFalse(y["equality_partition_identical"])
        self.assertEqual(y["unordered_position_pair_matrix"]["h_only_equal"], 1)

    def test_empty_and_singleton_domains_have_no_cyclic_edges(self):
        for h, r in (([], []), ([[]], [[]]), ([["a"]], [["X"]])):
            x = graph(h, r)
            self.assertTrue(x["equality_partition_identical"])
            self.assertEqual(x["repeat_edge_population"], 0)
            self.assertEqual(x["all_joining_edges"], [])
            self.assertTrue(all(pop["B_repeated_types"] == 0 for pop in x["populations"].values()))

    def test_asterisks_and_unicode_are_preserved_in_separate_hash_domains(self):
        x = graph([["a*", "a*", "b"]], [["é", "*", "é"]])
        self.assertEqual(x["populations"]["h"]["asterisk_types"], 1)
        self.assertEqual(x["populations"]["h"]["asterisk_occurrences"], 2)
        self.assertEqual(x["populations"]["reddy"]["asterisk_occurrences"], 1)
        self.assertEqual({n["type_sha256"] for n in x["nodes"]["reddy"]}, {sha("é"), sha("*")})
        self.assertNotIn("a*", json.dumps(x))
        self.assertNotIn("é", json.dumps(x, ensure_ascii=False))
        self.assertEqual(x["paired_tokens"], 3)

    def test_all_1365_binary_partition_pairs_agree_with_direct_position_pair_oracle(self):
        checked = 0
        for n in range(6):
            for symbols in itertools.product(range(4), repeat=n):
                a = ["a" if symbol & 1 else "b" for symbol in symbols]
                b = ["X" if symbol & 2 else "Y" for symbol in symbols]
                x = graph([a], [b])
                expected = dict.fromkeys(("both_equal", "h_only_equal", "reddy_only_equal", "neither_equal"), 0)
                adjacent = dict.fromkeys(expected, 0)
                def label(i, j):
                    left, right = a[i] == a[j], b[i] == b[j]
                    return "both_equal" if left and right else "h_only_equal" if left else "reddy_only_equal" if right else "neither_equal"
                for i, j in itertools.combinations(range(n), 2): expected[label(i, j)] += 1
                for i in range(n - 1): adjacent[label(i, i + 1)] += 1
                self.assertEqual(x["unordered_position_pair_matrix"], {"all_unordered_position_pairs": n * (n - 1) // 2, **expected})
                self.assertEqual(x["repeat_event_matrix"]["all"], adjacent)
                self.assertEqual(x["equality_partition_identical"], expected["h_only_equal"] + expected["reddy_only_equal"] == 0)
                for side, tokens in (("h", a), ("reddy", b)):
                    equal_positions = {tokens[i] for i in range(n - 1) if tokens[i] == tokens[i + 1]}
                    self.assertEqual(x["populations"][side]["B_repeated_types"], len(equal_positions))
                    self.assertEqual(sum(node["occurrences"] for node in x["nodes"][side]), n)
                supports = [tuple(p) for e in x["edges"] for p in e["support_positions"]]
                self.assertEqual(sorted(supports), [(0, i) for i in range(n)])
                self.assertEqual(sum(e["occurrences"] for e in x["edges"]), n)
                checked += 1
        self.assertEqual(checked, 1365)

    def test_literal_pairing_keeps_empty_H_record_and_fallback_code(self):
        keys = [("f1r", "P1", str(i), "H") for i in range(1, 4)]
        native, annotated = fixture(["a{code}", "{comment}!--", "a"], [["X"], ["X"]], h_keys=keys, r_keys=[keys[0], keys[2]])
        paired, ledger = module.pair_records(native, annotated)
        self.assertEqual([r["h_ordinal"] for r in paired], [0, 2])
        self.assertEqual(paired[0]["h_tokens"], ["a"])
        self.assertEqual(len(ledger["all_unmatched_records"]), 1)
        x = module.compare_types(paired)
        self.assertEqual(x["all_joining_edges"][0]["intervening_selected_H_ordinals"], [1])
        self.assertEqual(x["repeat_event_matrix"]["joining"]["both_equal"], 1)
        self.assertEqual(x["populations"]["h"]["B_by_edge_class"]["within_record"], 0)

    def test_unmatched_nonempty_count_and_shared_order_fail_without_optimized_pairing(self):
        keys = [("f1r", "P1", str(i), "H") for i in (1, 2)]
        cases = [fixture(["a", "b"], [["X"]]),
                 fixture(["a"], [["X"], ["Y"]]),
                 fixture(["a.b"], [["X"]]),
                 fixture(["a", "b"], [["X"], ["Y"]], h_keys=keys, r_keys=list(reversed(keys)))]
        for args in cases:
            with self.assertRaises(ValueError): module.pair_records(*args)

    def test_bad_paired_ordinals_counts_tokens_and_hash_collision_fail(self):
        records = [{"key": ["f1r", "P1", "1", "H"], "h_ordinal": 0, "reddy_ordinal": 0, "h_tokens": ["a"], "reddy_tokens": ["X"]}]
        for key, value in (("h_ordinal", False), ("reddy_ordinal", -1), ("reddy_tokens", ["X", "Y"]), ("h_tokens", ["a b"])):
            with self.subTest(key=key), self.assertRaises(ValueError): module.compare_types([{**records[0], key: value}])
        for a, b in ((list("ab"), list("XX")), (list("aa"), list("XY"))):
            with patch.object(module.parent, "digest", return_value="collision"), self.assertRaises(ValueError): graph([a], [b])
        with self.assertRaises(ValueError):
            module.compare_types([records[0], {**records[0], "h_ordinal": 1, "reddy_ordinal": 1}])

    def test_every_frozen_dependency_and_critical_option_is_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in (*module.FROZEN, module.PLAN):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(module.ROOT / name, target)
            module.load_plan(root)
            for name in module.FROZEN:
                path = root / name
                original = path.read_bytes()
                path.write_bytes(original + b" ")
                with self.subTest(name=name), self.assertRaises(ValueError): module.load_plan(root)
                path.write_bytes(original)
            plan = module.parent.read_json(root / module.PLAN)
            for key, value in (("h_special_codes", ["code"]), ("include_asterisk_tokens", False), ("sample", True), ("plan_version", True)):
                (root / module.PLAN).write_text(json.dumps({**plan, key: value}))
                with self.subTest(key=key), self.assertRaises(ValueError): module.load_plan(root)

    def test_failed_complete_parent_replay_precedes_new_analysis(self):
        with patch.object(module.parent, "run_audit", return_value={}), \
                patch.object(module.parent, "check_parent", side_effect=ValueError("parent mismatch")), \
                patch.object(module, "pair_records") as pair_mock, self.assertRaises(ValueError):
            module.run_audit(Path("unused"))
        pair_mock.assert_not_called()

    def test_all_120_early_and_late_output_aliases_preserve_every_protected_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root, reference = Path(temp) / "root", Path(temp) / "reference"
            producer = root / "scripts/producer.py"
            protected = [root / name for name in (*module.FROZEN, module.PLAN, module.HUMAN_PLAN)] + [producer]
            protected += [reference / name for name in module.parent.reddy.SELECTED]
            for i, path in enumerate(protected):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"original-{i}".encode())
            originals = [p.read_bytes() for p in protected]
            count = 0
            with patch.object(module, "ROOT", root), patch.object(module, "__file__", str(producer)):
                for source in protected:
                    for mode in ("direct", "early_symlink", "early_hardlink", "late_symlink", "late_hardlink"):
                        output = source if mode == "direct" else Path(temp) / "output.json"
                        def link():
                            if "symlink" in mode: output.symlink_to(source)
                            else: os.link(source, output)
                        if mode.startswith("early"): link()
                        def run(*args):
                            if mode.startswith("late"): link()
                            return {"result": 1}
                        with self.subTest(source=source, mode=mode), patch.object(module, "run_audit", side_effect=run) as mocked, \
                                patch("sys.argv", ["audit", "--reference", str(reference), "--output", str(output)]), \
                                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                            module.main()
                        self.assertEqual(error.exception.code, 1)
                        self.assertEqual(mocked.call_count, int(mode.startswith("late")))
                        self.assertEqual([p.read_bytes() for p in protected], originals)
                        if output != source: output.unlink()
                        count += 1
            self.assertEqual(count, 120)

    def test_failed_serialization_or_complete_check_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output, check = root / "out.json", root / "check.json"
            output.write_bytes(b"preserve")
            check.write_text('{"other": 0}')
            for result, extra in (({"value": float("nan")}, []), ({"value": 1}, ["--check", str(check)])):
                with patch.object(module, "run_audit", return_value=result), \
                        patch("sys.argv", ["audit", "--reference", str(root), "--output", str(output), *extra]), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): module.main()
                self.assertEqual(output.read_bytes(), b"preserve")

    def test_removed_protected_name_variants_are_refused_before_final_write(self):
        for phase in ("calculation", "serialization"):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as temp:
                base = Path(temp); root, reference, empty = base / "root", base / "reference", base / "empty"
                root.mkdir(); reference.mkdir(); empty.mkdir()
                (reference / "data").mkdir()
                target = reference / "data/voy.ann.wds"
                target.write_bytes(b"synthetic protected input")
                output_parent = base / "output-parent"
                output_parent.symlink_to(empty, target_is_directory=True)
                output = output_parent / "VOY.ANN.WDS"
                variant = reference / "DATA"
                if not variant.exists() or not variant.samefile(reference / "data"): variant = reference / "data"
                original_dumps = json.dumps

                def changed(*args, **kwargs):
                    target.unlink()
                    output_parent.unlink()
                    output_parent.symlink_to(variant, target_is_directory=True)
                    return {"fixture": 1} if phase == "calculation" else original_dumps(*args, **kwargs)

                with patch.object(module, "ROOT", root), \
                        patch.object(module, "run_audit", side_effect=changed if phase == "calculation" else None,
                                     return_value={"fixture": 1}), \
                        patch.object(module.json, "dumps", side_effect=changed if phase == "serialization" else original_dumps), \
                        patch("sys.argv", ["audit", "--reference", str(reference), "--output", str(output)]), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 1)
                self.assertFalse(target.exists())
                self.assertFalse(output.exists())

    def test_entry_resolved_targets_survive_source_symlink_retargeting(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); root, reference, empty = base / "root", base / "reference", base / "empty"
            root.mkdir(); reference.mkdir(); empty.mkdir()
            original_target = base / "OriginalReference.txt"
            original_target.write_bytes(b"synthetic")
            (reference / "data").mkdir()
            source = reference / "data/voy.ann.wds"
            source.symlink_to(original_target)
            output_parent = reference / "output-parent"
            output_parent.symlink_to(empty, target_is_directory=True)
            output = output_parent / "originalreference.TXT"

            def changed(*args, **kwargs):
                original_target.unlink()
                source.unlink(); source.symlink_to(base / "different.txt")
                output_parent.unlink(); output_parent.symlink_to(base, target_is_directory=True)
                return {"fixture": 1}

            with patch.object(module, "ROOT", root), patch.object(module, "run_audit", side_effect=changed), \
                    patch("sys.argv", ["audit", "--reference", str(reference), "--output", str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): module.main()
            self.assertFalse(original_target.exists())
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
