import contextlib
import copy
from decimal import localcontext, ROUND_FLOOR
from fractions import Fraction
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import half_control_moments as module


def direct_numerator(values):
    size, total = len(values), sum(values)
    deviations = [size * value - total for value in values]
    return sum(deviations[index] * deviations[index + 1] for index in range(size - 1))


def occurrence_permutations(values):
    split = (len(values) + 1) // 2
    # Duplicates are retained: this enumerates equally weighted occurrences.
    return (early + late for early in itertools.permutations(values[:split])
            for late in itertools.permutations(values[split:]))


class HalfControlMomentTests(unittest.TestCase):
    def test_signed_block_moments_match_every_injective_assignment(self):
        patterns = ((1,), (2,), (3,), (4,), (1, 1), (1, 2), (1, 3), (2, 2),
                    (1, 1, 1), (1, 1, 2), (1, 1, 1, 1))
        cases = 0
        for size in range(6):
            for values in itertools.product((-1, 0, 2), repeat=size):
                self.assertEqual(module.block_moment(values, ()), 1)
                for exponents in patterns:
                    if len(exponents) > size:
                        continue
                    scores = [math.prod(values[index] ** power for index, power in zip(indices, exponents))
                              for indices in itertools.permutations(range(size), len(exponents))]
                    expected = Fraction(sum(scores), len(scores))
                    self.assertEqual(module.block_moment(values, exponents), expected, (values, exponents))
                    cases += 1
        self.assertEqual(cases, 3918)

    def test_exhaustive_ternary_vectors_match_first_second_and_normalized_moments(self):
        cases = 0
        for size in range(3, 8):
            for values in itertools.product((1, 2, 3), repeat=size):
                scores = [direct_numerator(order) for order in occurrence_permutations(values)]
                mean = Fraction(sum(scores), len(scores))
                second = Fraction(sum(value * value for value in scores), len(scores))
                variance = second - mean ** 2
                result = module.locus_moments(values)
                self.assertEqual(result["numerator_mean"], mean, values)
                self.assertEqual(result["numerator_second_moment"], second, values)
                self.assertEqual(result["numerator_variance"], variance, values)
                total = sum(values)
                squared = sum((size * value - total) ** 2 for value in values)
                scale = Fraction(size, (size - 1) * squared) if squared else Fraction()
                self.assertEqual(result["association_mean"], scale * mean, values)
                self.assertEqual(result["association_variance"], scale ** 2 * variance, values)
                self.assertEqual(result["association_variance"] == 0, len(set(scores)) == 1, values)
                cases += 1
        self.assertEqual(cases, 3267)

    def test_repeated_values_have_occurrence_weights_and_singleton_halves(self):
        for values in ([1, 3, 2], [1, 3, 2, 2], [2, 2, 2, 1, 3], [1, 1, 4, 4], [4, 4, 4]):
            self.assertEqual(module.locus_moments(values)["association_variance"], 0)
        for values in ([1, 2, 3], [1, 2, 3, 4], [1, 2, 2, 1, 2, 2, 2]):
            self.assertGreater(module.locus_moments(values)["association_variance"], 0)
        self.assertEqual(module.block_moment((2, 2, 5), (1, 1)), 8)
        self.assertEqual(module.block_moment((2,), (4,)), 16)

    def test_geometry_multiplicities_include_same_shared_and_disjoint_edges(self):
        for size in range(3, 31):
            means, seconds = module.edge_patterns(size)
            self.assertEqual(sum(count for _, count in means), size - 1)
            self.assertEqual(sum(count for _, count in seconds), (size - 1) ** 2)
            self.assertTrue(all(sum(early) + sum(late) == 2 for (early, late), _ in means))
            self.assertTrue(all(sum(early) + sum(late) == 4 for (early, late), _ in seconds))
        self.assertEqual(dict(module.edge_patterns(3)[1]),
                         {((1, 2), (1,)): 2, ((2,), (2,)): 1, ((2, 2), ()): 1})

    def test_translation_scaling_and_within_block_reordering_preserve_normalized_variance(self):
        for values in ([1, 3, 2], [2, 2, 2, 1, 3], [1, 2, 3, 4, 5, 6, 7]):
            before = copy.deepcopy(values)
            split = (len(values) + 1) // 2
            expected = module.locus_moments(values)["association_variance"]
            for changed in ([value + 100 for value in values], [7 * value for value in values],
                            values[:split][::-1] + values[split:][::-1]):
                self.assertEqual(module.locus_moments(changed)["association_variance"], expected)
            self.assertEqual(values, before)

    def test_equal_locus_denominator_retains_every_invariant(self):
        rows = [("f1r", "f1r.1", [1, 2, 3]), ("f1r", "f1r.2", [1, 3, 2]),
                ("f1v", "f1v.1", [4, 4, 4])]
        result = module.summarize(rows)
        self.assertEqual(result["loci"], 3)
        self.assertEqual(result["accepted_effect_denominator"], 3)
        self.assertEqual(result["exact_zero_variance_loci"], 2)
        self.assertEqual(result["invariant_identifiers"],
                         [{"page_id": page, "locus_key": key} for page, key, _ in rows[1:]])
        fraction = result["exact_ideal_mean_variance"]
        actual = Fraction(int(fraction["numerator"], 16), int(fraction["denominator"], 16))
        self.assertEqual(actual, module.locus_moments(rows[0][2])["association_variance"] / 9)
        self.assertEqual(module.mean_variance([Fraction(1, 4), Fraction(), Fraction(1)]), Fraction(5, 36))
        self.assertEqual(result["exact_half_centered_ensemble_mean"], module.fraction_record(Fraction()))

    def test_large_exact_aggregate_serializes_without_global_decimal_context_changes(self):
        value = Fraction(10 ** 9000 + 1, 10 ** 9001 + 3)
        expected = module.encoded(module.aggregate_fraction_record(value))
        with localcontext() as context:
            context.prec = 1
            context.rounding = ROUND_FLOOR
            result = module.aggregate_fraction_record(value)
            self.assertEqual(context.prec, 1)
            self.assertEqual(context.rounding, ROUND_FLOOR)
        self.assertEqual(module.encoded(result), expected)
        self.assertEqual(Fraction(int(result["numerator"], 16), int(result["denominator"], 16)), value)
        self.assertGreater(len(result["numerator"]), 4300)

    def test_invalid_inputs_and_duplicate_identities_fail(self):
        for values in ([], [1, 2], [1, 0, 3], [1, True, 3], [1, 2.5, 3]):
            with self.assertRaises(ValueError):
                module.locus_moments(values)
        for values, exponents in (((1,), (1, 1)), ((True,), (1,)), ((1,), (True,)),
                                  ((1,), (0,)), ((1,), (5,)), ((1, 2), (2, 3))):
            with self.assertRaises(ValueError):
                module.block_moment(values, exponents)
        for rows in ([], [("f1r", "f1r.1", [1, 2, 3])] * 2):
            with self.assertRaises(ValueError):
                module.summarize(rows)
        for variances in ([], [Fraction(-1)]):
            with self.assertRaises(ValueError):
                module.mean_variance(variances)
        for size in (2, True, 2.5):
            with self.assertRaises(ValueError):
                module.edge_patterns(size)

    def test_changed_pins_and_duplicate_treatments_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "input.txt"
            path.write_bytes(b"synthetic input")
            pins = {"input.txt": hashlib.sha256(path.read_bytes()).hexdigest()}
            with patch.multiple(module, ROOT=root, INPUT_PINS=pins):
                self.assertEqual(module.verify_inputs(), {})
                path.write_bytes(b"changed synthetic input")
                with self.assertRaisesRegex(ValueError, "pinned input changed"):
                    module.verify_inputs()
        rows = [{"source_id": "fixture", "spacing": "split"}]
        self.assertEqual(len(module.treatment_map({"treatments": rows}, {("fixture", "split")})), 1)
        for changed in (rows * 2, [], [{"source_id": "different", "spacing": "split"}]):
            with self.assertRaisesRegex(ValueError, "inventory changed"):
                module.treatment_map({"treatments": changed}, {("fixture", "split")})

    def test_direct_early_and_late_aliases_preserve_all_synthetic_input_classes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            native = root / "data/native.txt"
            native.write_text("synthetic native input")
            catalog = root / module.CATALOG_NAME
            catalog.write_text(json.dumps({"sources": [{"path": "data/native.txt"}]}))
            names = ("parent.json", "half.json", "invariance.json", "plan.md", "helper.py")
            pins = {}
            for name in names:
                (root / name).write_text("synthetic pinned input")
                pins[name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
            implementation = root / "implementation.py"
            implementation.write_text("synthetic implementation")
            check = root / "check.json"
            check.write_bytes(module.encoded({"synthetic": True}))
            protected = [root / name for name in pins] + [native, catalog, implementation, check]
            before = {path: path.read_bytes() for path in protected}
            with patch.multiple(module, ROOT=root, INPUT_PINS=pins, IMPLEMENTATION_PATH=implementation):
                for path in protected:
                    with patch("sys.argv", ["audit", "--output", str(path), "--check", str(check)]):
                        with patch.object(module, "report") as build:
                            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                                module.main()
                            self.assertEqual(error.exception.code, 1)
                            build.assert_not_called()
                    for alias_kind in ("symlink", "hardlink"):
                        for late in (False, True):
                            output = root / f"alias-{path.name}-{alias_kind}-{late}"

                            def create_alias():
                                if alias_kind == "symlink":
                                    output.symlink_to(path)
                                else:
                                    output.hardlink_to(path)
                                return {"synthetic": True}

                            if not late:
                                create_alias()
                            with patch("sys.argv", ["audit", "--output", str(output), "--check", str(check)]):
                                with patch.object(module, "report", side_effect=create_alias if late else None,
                                                  return_value={"synthetic": True}) as build:
                                    with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                                        module.main()
                                    self.assertEqual(error.exception.code, 1)
                                    self.assertEqual(build.call_count, int(late))
                            self.assertEqual({target: target.read_bytes() for target in protected}, before)

    def test_normal_output_check_drift_and_finite_serialization(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / module.CATALOG_NAME).write_text('{"sources": []}')
            output, check = root / "output.json", root / "check.json"
            expected = {"synthetic": True}
            check.write_bytes(module.encoded(expected))
            with patch.multiple(module, ROOT=root, INPUT_PINS={}, IMPLEMENTATION_PATH=root / "script.py"):
                with patch.object(module, "report", return_value=expected):
                    for exists in (False, True):
                        if exists:
                            output.write_bytes(b"replaceable output")
                        with patch("sys.argv", ["audit", "--output", str(output), "--check", str(check)]):
                            with contextlib.redirect_stdout(io.StringIO()):
                                module.main()
                        self.assertEqual(output.read_bytes(), check.read_bytes())
                    check.write_bytes(b"changed report")
                    before = output.read_bytes()
                    with patch("sys.argv", ["audit", "--output", str(output), "--check", str(check)]):
                        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                            module.main()
                        self.assertEqual(error.exception.code, 1)
                    self.assertEqual(output.read_bytes(), before)
            with self.assertRaises(ValueError):
                module.encoded({"invalid": float("nan")})


if __name__ == "__main__":
    unittest.main()
