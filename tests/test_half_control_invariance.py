from collections import Counter
import copy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import half_control_invariance as module
from scripts.half_control_invariance import classify, pinned_json, variation_witness


def numerator(values):
    """Independent integer statistic calculation for exhaustive fixtures."""
    m, total = len(values), sum(values)
    return sum((m * a - total) * (m * b - total)
               for a, b in zip(values, values[1:]))


def permitted(values):
    split = (len(values) + 1) // 2
    return (a + b for a in set(itertools.permutations(values[:split]))
            for b in set(itertools.permutations(values[split:])))


class HalfControlInvarianceTests(unittest.TestCase):
    def assert_witness(self, original, witness):
        before, after = witness
        split = (len(original) + 1) // 2
        for arranged in (before, after):
            self.assertEqual(Counter(arranged[:split]), Counter(original[:split]))
            self.assertEqual(Counter(arranged[split:]), Counter(original[split:]))
        self.assertNotEqual(numerator(before), numerator(after))
        changed = [index for index, (a, b) in enumerate(zip(before, after)) if a != b]
        self.assertEqual(len(changed), 2)
        self.assertEqual(changed[1], changed[0] + 1)
        self.assertEqual(changed[0] < split, changed[1] < split)

    def test_exhaustive_occurrence_feasibility_matches_every_allowed_permutation(self):
        # Seven positions include a four-element block with two internal neighbors;
        # their occurrence multiplicities must be enforced separately.
        vectors = 0
        for size in range(3, 8):
            for values in itertools.product((1, 2, 3), repeat=size):
                with self.subTest(values=values):
                    expected = len({numerator(order) for order in permitted(values)}) == 1
                    witness = variation_witness(values)
                    self.assertEqual(witness is None, expected)
                    if witness is not None:
                        self.assert_witness(values, witness)
                    vectors += 1
        self.assertEqual(vectors, 3267)

    def test_nonconstant_invariants_and_constant_blocks(self):
        for values in ([1, 3, 2], [1, 3, 2, 2], [2, 2, 2, 1, 3],
                       [1, 1, 4, 4], [4, 4, 4]):
            self.assertIsNone(variation_witness(values), values)
        for values in ([1, 2, 3], [1, 2, 3, 4], [1, 2, 2, 1, 2, 2, 2]):
            witness = variation_witness(values)
            self.assertIsNotNone(witness, values)
            self.assert_witness(values, witness)

    def test_affine_invariance_and_inputs_remain_unchanged(self):
        for values in ([1, 3, 2], [2, 2, 2, 1, 3], [1, 2, 3, 4, 5, 6, 7]):
            saved = copy.deepcopy(values)
            expected = variation_witness(values) is None
            for transformed in ([x + 20 for x in values], [7 * x for x in values]):
                self.assertEqual(variation_witness(transformed) is None, expected)
            self.assertEqual(values, saved)

    def test_invalid_lengths_and_duplicate_identities_fail(self):
        for values in ([], [1, 2], [1, 0, 3], [1, True, 3], [1, 2.5, 3]):
            with self.assertRaises(ValueError):
                variation_witness(values)
        for rows in ([], [("f1r", "f1r.1", [1, 2, 3])] * 2):
            with self.assertRaises(ValueError):
                classify(rows)

    def test_partition_identifiers_and_denominator_include_all_invariants(self):
        rows = [("f1r", "f1r.1", [1, 3, 2]),
                ("f1r", "f1r.2", [1, 1, 4, 4]),
                ("f1v", "f1v.1", [1, 2, 3])]
        result = classify(rows)
        self.assertEqual(result["loci"], 3)
        self.assertEqual(result["accepted_effect_denominator"], 3)
        self.assertEqual(result["both_half_constant_loci"], 1)
        self.assertEqual(result["exact_invariant_loci"], 2)
        self.assertEqual(result["additional_invariant_loci"], 1)
        self.assertEqual(result["varying_loci_with_verified_witness"], 1)
        self.assertEqual(result["additional_invariant_identifiers"],
                         [{"page_id": "f1r", "locus_key": "f1r.1"}])
        self.assertEqual(len(result["invariant_identifiers"]), 2)
        self.assertEqual(result["invariant_interior_size_counts"], {"3": 1, "4": 1})
        self.assertEqual(result["additional_invariant_interior_size_counts"], {"3": 1})

    def test_report_pin_rejects_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            data = b'{"synthetic": true}\n'
            path.write_bytes(data)
            self.assertEqual(pinned_json(path, hashlib.sha256(data).hexdigest()),
                             {"synthetic": True})
            with self.assertRaisesRegex(ValueError, "pinned report changed"):
                pinned_json(path, "0" * 64)

    def test_cli_protects_all_catalog_inputs_and_both_accepted_reports(self):
        root = module.ROOT
        catalog = root / "data/transliterations.json"
        paths = [catalog, module.PARENT_PATH, module.HALF_PATH, module.PLAN_PATH]
        paths.extend(root / source["path"] for source in json.loads(catalog.read_text())["sources"])
        for path in paths:
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(root / "scripts/half_control_invariance.py"),
                                     "--output", str(path)], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not overwrite", result.stderr)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
