import contextlib
from dataclasses import replace
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import shutil
import string
import tempfile
import unittest
from unittest.mock import patch

from scripts import historical_currier_definition as module
from scripts.audit_historical_interlinear import HistoricalRecord


def definition():
    return module.Definition([{"currier": left, "eva": right, "line": i}
                              for i, (left, right) in enumerate(zip("ABCDEF", ["a", "b", "aa", "ab", "ba", "bb"]), 5)])


def native(bodies):
    return [HistoricalRecord(f"f1r.P.{i};H", "f1r", "P", str(i), "H", body, 2 + i * 3)
            for i, body in enumerate(bodies, 1)]


def source_fixture(reference):
    # Fictional definitions, not a copy of the author's 38-rule payload.
    left = list(string.digits + string.ascii_uppercase + "nv")
    right = ["n", "v", "a"] + ["a" + c for c in string.ascii_lowercase] + ["b" + c for c in string.ascii_lowercase[:9]]
    lines = ["##BIT  Curr Eva- ", "#=%", "<(comment)>", "#(comment) "] + [f"{a} {b}" for a, b in zip(left, right, strict=True)]
    raw = ("\n".join(lines) + "\n").encode("ascii")
    sha = lambda value: hashlib.sha256(value).hexdigest()
    artifacts = []
    for name, value in zip(module.REFERENCES, [raw, b"fictional manual", b"fictional readme"], strict=True):
        (reference / name).write_bytes(value)
        artifacts.append({"reference_name": name, "bytes": len(value), "sha256": sha(value)})
    # Independent trie computes the fictional catalog's complete synthetic ledger.
    trie = {}
    for a, b in zip(left, right, strict=True):
        node = trie
        for c in b: node = node.setdefault(c, {})
        node["end"] = a
    def decode(value):
        pos, result = 0, []
        while pos < len(value):
            node, i, last = trie, pos, None
            while i < len(value) and value[i] in node:
                node = node[value[i]]; i += 1
                if "end" in node: last = (node["end"], i)
            if last is None: result.append(value[pos]); pos += 1
            else:
                symbol, pos = last
                result.append(symbol)
        return "".join(result)
    failures = []
    for i, j in itertools.product(range(38), repeat=2):
        a, b = left[i] + left[j], right[i] + right[j]
        back = decode(b)
        if back != a:
            failures.append({"input_rule_lines": [i + 5, j + 5], "currier_input_sha256": sha(a.encode()),
                             "eva_output_sha256": sha(b.encode()), "currier_roundtrip_sha256": sha(back.encode()),
                             "input_codepoints": len(a), "eva_codepoints": len(b), "roundtrip_codepoints": len(back)})
    counts = {n: sum(len(s) == n for s in right) for n in sorted(set(map(len, right)))}
    return {"artifacts": artifacts,
            "all_rule_metadata": [{"physical_file_line": i, "left_sha256": sha(a.encode()), "right_sha256": sha(b.encode()),
                                   "left_codepoints": len(a), "right_codepoints": len(b), "raw_line_sha256": sha(lines[i - 1].encode())}
                                  for i, (a, b) in enumerate(zip(left, right, strict=True), 5)],
            "rule_structure": {"physical_lines": 42, "line_endings": "LF", "final_newline": True,
                               "header_sha256": sha(lines[0].encode()), "header_column_codes": ["Curr", "Eva-"],
                               "direction_restriction": None, "separator_marker": "%",
                               "comment_definitions": [{"start": "<", "end": ">", "kind": "limited_extent"},
                                                       {"start": "#", "kind": "full_line", "explicit_terminal_space": True}],
                               "rules": 38, "unique_left_strings": 38, "unique_right_strings": 38,
                               "left_codepoint_lengths": [{"length": 1, "rules": 38}],
                               "right_codepoint_lengths": [{"length": n, "rules": v} for n, v in counts.items()],
                               "right_proper_prefix_pairs": [{"prefix_rule_line": i + 5, "longer_rule_line": j + 5}
                                                             for i, a in enumerate(right) for j, b in enumerate(right) if i != j and b.startswith(a)],
                               "membership_probe_universe": "abcdefghijklmnopqrstuvwxyz*",
                               "codepoints_absent_anywhere_in_right_strings": sorted(module.ALPHABET - set("".join(right)))},
            "synthetic_roundtrip": {"cohort": "Every ordered pair of the 38 distinct Currier rule codes; no manuscript text",
                                    "algorithm": "Concatenate original right-column definitions, then consume input left to right using the longest matching right-column string and emit its left-column code; noncumulative; unmatched characters copied opaquely",
                                    "cases": 1444, "failures": len(failures), "passes": 1444 - len(failures), "all_failed_cases": failures}}


class HistoricalCurrierDefinitionTests(unittest.TestCase):
    def test_greedy_and_opaque_offsets_match_character_accounting(self):
        output, uses, unmatched, matched = definition().convert("aab*c")
        self.assertEqual(output, "CB*c")
        self.assertEqual(dict(uses), {7: 1, 6: 1})
        self.assertEqual(unmatched, [{"source_offset": 3, "codepoint": "U+002A"}, {"source_offset": 4, "codepoint": "U+0063"}])
        self.assertEqual(matched, 3)
        self.assertEqual(definition().expand(output), "aab*c")

    def test_lowercase_output_is_not_rescanned_and_decoder_condition_is_required(self):
        x = module.Definition([{"currier": "n", "eva": "x", "line": 1}, {"currier": "D", "eva": "n", "line": 2}])
        self.assertEqual(x.convert("xn")[0], "nD")
        self.assertEqual(x.expand("nD"), "xn")
        with self.assertRaises(ValueError): module.Definition([{"currier": "n", "eva": "x", "line": 1}])

    def test_all_20439_short_allowed_tokens_decode_and_remain_injective(self):
        model, outputs, count = definition(), {}, 0
        for length in range(1, 4):
            for chars in itertools.product(sorted(module.ALPHABET), repeat=length):
                original = "".join(chars)
                output, uses, unmatched, matched = model.convert(original)
                self.assertEqual(model.expand(output), original)
                self.assertEqual(matched + len(unmatched), len(original))
                self.assertEqual(sum(uses.values()) + len(unmatched), len(output))
                self.assertNotIn(output, outputs)
                outputs[output] = original; count += 1
        self.assertEqual(count, 20439)

    def test_record_type_coverage_and_repeat_scopes_keep_empty_records(self):
        x = module.analyze(native(["a.a", "{comment}!--", "a.b*", "b*.b*"]), definition())
        self.assertEqual((x["records"], x["empty_records"], x["tokens"]), (4, 1, 6))
        self.assertEqual((x["fully_defined_tokens"], x["tokens_with_unmatched_symbols"]), (3, 3))
        self.assertEqual((x["input_types"], x["output_types"]), (2, 2))
        self.assertEqual(x["input_repeat_counts"], x["output_repeat_counts"])
        self.assertEqual(x["input_repeat_counts"], {"A": 4, "B": 2, "within_A": 2, "joining_A": 2,
                         "within_B": 2, "joining_B": 2, "B_scope_overlap": 2, "within_opportunities": 3, "joining_opportunities": 2})
        self.assertEqual(x["all_flattened_joins_spanning_empty_H"][0]["intervening_normalized_empty_H_ordinals"], [1])
        self.assertEqual(len(x["all_unmatched_events"]), 3)
        self.assertEqual(sum(r["uses"] for r in x["all_rule_use_counts"]), 6)
        self.assertTrue(any(r["uses"] == 0 for r in x["all_rule_use_counts"]))

    def test_natural_empty_singleton_and_normalizer_fallbacks_are_retained(self):
        for bodies, expected in (([], 0), (["!--"], 0), (["a{code}"], 1)):
            x = module.analyze(native(bodies), definition())
            self.assertEqual(x["tokens"], expected)
            self.assertEqual(x["input_repeat_counts"]["A"], 0)
            self.assertTrue(x["all_tokens_decode_exactly"])

    def test_bad_definitions_source_keys_order_tokens_and_hash_collisions_fail(self):
        for rows in ([{"currier": "A", "eva": "a", "line": 1}, {"currier": "A", "eva": "b", "line": 2}],
                     [{"currier": "A", "eva": "a", "line": 1}, {"currier": "B", "eva": "a", "line": 2}],
                     [{"currier": "A", "eva": "a", "line": 1}, {"currier": "B", "eva": "b", "line": 1}],
                     [{"currier": "AA", "eva": "a", "line": 1}], [{"currier": "A", "eva": "a*", "line": 1}]):
            with self.assertRaises(ValueError): module.Definition(rows)
        rows = native(["a", "b"])
        for changed in ([replace(rows[0], locator="wrong")], [replace(rows[0], transcriber="U")],
                        [rows[0], rows[0]], list(reversed(rows))):
            with self.assertRaises(ValueError): module.analyze(changed, definition())
        for token in ("", "A", "é", "a b"):
            with self.assertRaises(ValueError): definition().convert(token)
        with patch.object(module, "sha", return_value="collision"), self.assertRaises(ValueError): module.analyze(rows, definition())

    def test_full_fictional_source_catalog_and_all_corrupt_diagnostics_are_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            reference = Path(temp)
            catalog = source_fixture(reference)
            self.assertEqual(len(module.verify_definition(reference, catalog).rows), 38)
            for mode in ("row_hash", "prefix", "failure", "algorithm", "typed_count", "header", "source_hash"):
                changed = json.loads(json.dumps(catalog))
                if mode == "row_hash": changed["all_rule_metadata"][0]["right_sha256"] = "wrong"
                elif mode == "prefix": changed["rule_structure"]["right_proper_prefix_pairs"] = []
                elif mode == "failure": changed["synthetic_roundtrip"]["all_failed_cases"] = []
                elif mode == "algorithm": changed["synthetic_roundtrip"]["algorithm"] = "other"
                elif mode == "typed_count": changed["rule_structure"]["final_newline"] = 1
                elif mode == "header": changed["rule_structure"]["header_sha256"] = "wrong"
                else: changed["artifacts"][0]["sha256"] = "wrong"
                with self.subTest(mode=mode), self.assertRaises(ValueError): module.verify_definition(reference, changed)
            for name in module.REFERENCES:
                path = reference / name; original = path.read_bytes(); path.write_bytes(original + b" ")
                with self.assertRaises(ValueError): module.verify_definition(reference, catalog)
                path.write_bytes(original)

    def test_each_frozen_dependency_and_critical_policy_is_enforced(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in (*module.FROZEN, module.PLAN):
                target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(module.ROOT / name, target)
            module.load_plan(root)
            for name in module.FROZEN:
                path = root / name; original = path.read_bytes(); path.write_bytes(original + b" ")
                with self.assertRaises(ValueError): module.load_plan(root)
                path.write_bytes(original)
            plan = module.read_json(root / module.PLAN)
            for key, value in (("unmatched_policy", "drop"), ("h_special_codes", ["code"]), ("comparison_performed", True), ("plan_version", True)):
                (root / module.PLAN).write_text(json.dumps({**plan, key: value}))
                with self.assertRaises(ValueError): module.load_plan(root)

    def test_both_complete_parent_failures_precede_new_H_analysis(self):
        with patch.object(module, "verify_definition", return_value=definition()), \
                patch.object(module, "audit", return_value={}), patch.object(module, "reconstruct", return_value=({}, {})), \
                patch.object(module, "analyze") as analyze:
            for fail_at in (1, 2):
                seen = []
                def checker(value, path):
                    seen.append(path)
                    if len(seen) == fail_at: raise ValueError("parent mismatch")
                with patch.object(module, "check_report", side_effect=checker), self.assertRaises(ValueError): module.run_audit(Path("unused"))
                analyze.assert_not_called()

    def test_all_70_early_late_aliases_preserve_every_protected_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root, reference = Path(temp) / "root", Path(temp) / "reference"
            producer = root / "scripts/producer.py"
            paths = [root / n for n in (*module.FROZEN, module.PLAN, module.HUMAN_PLAN)] + [producer]
            paths += [reference / n for n in module.REFERENCES]
            for i, p in enumerate(paths): p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(f"original-{i}".encode())
            original = [p.read_bytes() for p in paths]; count = 0
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
                        self.assertEqual([p.read_bytes() for p in paths], original)
                        if output != source: output.unlink()
                        count += 1
            self.assertEqual(count, 70)

    def test_failed_serialization_and_strict_check_preserve_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); output, check = root / "out.json", root / "check.json"
            output.write_bytes(b"preserve"); check.write_text('{"other": 0}')
            for result, extra in (({"value": float("nan")}, []), ({"value": 1}, ["--check", str(check)])):
                with patch.object(module, "run_audit", return_value=result), \
                        patch("sys.argv", ["audit", "--reference", str(root), "--output", str(output), *extra]), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): module.main()
                self.assertEqual(output.read_bytes(), b"preserve")


if __name__ == "__main__": unittest.main()
