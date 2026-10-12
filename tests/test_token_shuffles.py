from collections import Counter, defaultdict
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("token_controls", ROOT / "scripts" / "shuffle_token_lines.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FIXTURE = ROOT / "research" / "token-controls" / "synthetic-corpus.json"


class TokenControlTests(unittest.TestCase):
    def test_line_control_retains_every_line_multiset_and_context(self):
        raw = FIXTURE.read_bytes()
        source = json.loads(raw)
        control = MODULE.make_control(raw, "line", 1729, 0)
        self.assertEqual(control["provenance"], source["provenance"])
        for original, permuted in zip(source["lines"], control["lines"]):
            self.assertEqual(Counter(original["tokens"]), Counter(permuted["tokens"]))
            self.assertEqual({k: v for k, v in original.items() if k != "tokens"},
                             {k: v for k, v in permuted.items() if k != "tokens"})
        self.assertEqual(control["lines"][2]["tokens"], [])
        self.assertEqual(control["lines"][4]["tokens"], ["Q"])

    def test_folio_side_control_never_moves_tokens_between_sides(self):
        raw = FIXTURE.read_bytes()
        source = json.loads(raw)
        control = MODULE.make_control(raw, "folio-side", 1729, 0)
        def counts(lines):
            result = defaultdict(Counter)
            for line in lines:
                result[line["folio_side"]].update(line["tokens"])
            return result
        self.assertEqual(counts(source["lines"]), counts(control["lines"]))
        self.assertEqual([len(line["tokens"]) for line in source["lines"]],
                         [len(line["tokens"]) for line in control["lines"]])
        self.assertEqual([(line["folio_side"], line["line_id"]) for line in source["lines"]],
                         [(line["folio_side"], line["line_id"]) for line in control["lines"]])

    def test_fixed_algorithm_reproduces_both_committed_controls(self):
        raw = FIXTURE.read_bytes()
        for scope, name in (("line", "example-line-control.json"), ("folio-side", "example-folio-side-control.json")):
            output = json.dumps(MODULE.make_control(raw, scope, 1729, 0), indent=2, ensure_ascii=False) + "\n"
            self.assertEqual(output.encode(), (FIXTURE.parent / name).read_bytes())
            self.assertEqual(MODULE.make_control(raw, scope, 1729, 0), MODULE.make_control(raw, scope, 1729, 0))

    def test_ambiguous_input_or_stale_token_annotations_are_rejected(self):
        original = json.loads(FIXTURE.read_bytes())
        variants = []
        duplicate = copy.deepcopy(original)
        duplicate["lines"].append(duplicate["lines"][0])
        variants.append(duplicate)
        annotated = copy.deepcopy(original)
        annotated["lines"][0]["token_confidence"] = [1, 1, 1, 1]
        variants.append(annotated)
        panel = copy.deepcopy(original)
        panel["lines"][0]["folio_side"] = "67r1"
        variants.append(panel)
        whitespace = copy.deepcopy(original)
        whitespace["lines"][0]["tokens"][0] = "two tokens"
        variants.append(whitespace)
        missing_provenance = copy.deepcopy(original)
        missing_provenance["provenance"].pop("tokenization")
        variants.append(missing_provenance)
        control = MODULE.make_control(FIXTURE.read_bytes(), "line", 1729, 0)
        variants.append(control)
        for value in variants:
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.make_control(json.dumps(value).encode(), "line", 1729, 0)

    def test_rejection_draw_does_not_reduce_out_of_range_values(self):
        class Digest:
            def __init__(self, first):
                self.first = first
            def digest(self):
                return bytes([self.first]) + bytes(31)
        # For bound 3, byte 255 must be rejected; accepting 3 then gives 0.
        # A modulo-only implementation would accept 255 on its first draw.
        with patch.object(MODULE.hashlib, "sha256", side_effect=[Digest(255), Digest(3)]):
            draws = MODULE.HashDraws(bytes(32))
            self.assertEqual(draws.below(3), 0)
            self.assertEqual(draws.counter, 2)

    def test_cli_digest_gate_preserves_existing_output_on_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "control.json"
            output.write_text("existing result")
            command = [sys.executable, str(ROOT / "scripts" / "shuffle_token_lines.py"), str(FIXTURE),
                       "--scope", "line", "--seed", "1729", "--trial", "0", "--expected-sha256", "0" * 64,
                       "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(), "existing result")
            copied = Path(directory) / "source.json"
            copied.write_bytes(FIXTURE.read_bytes())
            command = [sys.executable, str(ROOT / "scripts" / "shuffle_token_lines.py"), str(copied),
                       "--scope", "line", "--seed", "1729", "--trial", "0", "--output", str(copied)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(copied.read_bytes(), FIXTURE.read_bytes())


if __name__ == "__main__":
    unittest.main()
