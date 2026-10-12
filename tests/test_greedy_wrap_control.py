"""Independently enumerate fitting paths and exact calibration values."""

from collections import defaultdict
from fractions import Fraction
from itertools import product
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import greedy_wrap_control as WRAP


def enumerate_paths(first, support, capacity, separator):
    transitions, reward, counts = defaultdict(Fraction), Fraction(0), defaultdict(Fraction)
    probability = Fraction(1, len(support))

    def visit(row, weight):
        nonlocal reward
        for incoming in support:
            path_weight = weight * probability
            candidate = row + [incoming]
            if sum(candidate) + separator * (len(candidate)-1) <= capacity:
                visit(candidate, path_weight)
            else:
                transitions[incoming] += path_weight
                # Use the actual path, independently of the occupancy-state formula.
                reward += path_weight * (Fraction(row[0]) - Fraction(sum(row[1:]), len(row)-1))
                counts[len(row)] += path_weight

    visit([first], Fraction(1))
    return [transitions[value] for value in support], reward, dict(sorted(counts.items()))


class WrappingTests(unittest.TestCase):
    def test_small_path_enumeration_matches_kernel_and_equal_row_rewards(self):
        for support, capacity in [([2, 3], 7), ([2, 3], 8), ([2, 3], 9), ([2, 3, 4, 5, 6], 13)]:
            kernel, rewards, laws = WRAP.row_kernel(support, capacity)
            for index, first in enumerate(support):
                with self.subTest(support=support, capacity=capacity, first=first):
                    transition, reward, counts = enumerate_paths(first, support, capacity, 1)
                    self.assertEqual(kernel[index], transition)
                    self.assertEqual(rewards[index], reward)
                    self.assertEqual(laws[index], counts)

    def test_known_positive_stationary_calibration_is_exact(self):
        result = WRAP.exact([2, 3], 8)
        self.assertEqual(result["transition_kernel_exact"], [["3/8", "5/8"], ["1/2", "1/2"]])
        self.assertEqual(result["stationary_first_length_probabilities_exact"], ["4/9", "5/9"])
        self.assertEqual(result["conditional_equal_row_contrasts_exact"], ["-1/2", "1/2"])
        self.assertEqual(result["stationary_equal_row_contrast_exact"], "1/18")

    def test_known_zero_case_is_retained(self):
        result = WRAP.exact([2, 3], 7)
        self.assertEqual(result["stationary_equal_row_contrast_exact"], "0")
        self.assertEqual(result["stationary_row_token_count_probabilities_exact"], {"2": "1"})

    def test_same_rejected_token_is_carried_and_full_unclosed_tail_is_excluded(self):
        stream = [2, 2, 3, 2, 3, 3]
        rows, trailing = WRAP.wrap(stream, 7)
        self.assertEqual(rows, [[2, 2], [3, 2]])
        self.assertEqual(trailing, [3, 3])  # Exactly fits, but no overflow closed it.
        self.assertEqual([x for row in rows for x in row] + trailing, stream)

    def test_fixed_count_iid_expectation_is_zero_by_complete_enumeration(self):
        for size in [3, 4, 5]:
            rows = [list(row) for row in product([2, 3], repeat=size)]
            self.assertEqual(WRAP.measure(rows)["observed_equal_row_contrast"], 0)

    def test_negative_finite_contrast_and_equal_row_weighting_are_not_hidden(self):
        result = WRAP.measure([[2, 3], [2, 3, 3]])
        self.assertEqual(result["observed_equal_row_contrast"], -1)
        # Row [3,2] has +1; row [2,3,3] has -1. Each row has one vote.
        self.assertEqual(WRAP.measure([[3, 2], [2, 3, 3]])["observed_equal_row_contrast"], 0)

    def test_recurrent_classes_and_stationary_support_are_checked(self):
        with self.assertRaisesRegex(ValueError, "Multiple recurrent classes"):
            WRAP.stationary([[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]])
        with self.assertRaisesRegex(ValueError, "self-transition"):
            WRAP.stationary([[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]])
        law, graph = WRAP.stationary([[Fraction(0), Fraction(1)], [Fraction(0), Fraction(1)]])
        self.assertEqual(law, [0, 1])
        self.assertEqual(graph["closed_classes_indices"], [[1]])
        self.assertEqual(graph["stationary_support_indices"], [1])

    def test_unsupported_lengths_singleton_settings_and_overlong_inputs_fail(self):
        for support, capacity in [([2, 2], 8), ([0, 3], 8), ([2, 3], 6), ([True, 3], 8)]:
            with self.assertRaises(ValueError):
                WRAP.row_kernel(support, capacity)
        for stream in [[9], [0], [True]]:
            with self.assertRaises(ValueError):
                WRAP.wrap(stream, 8)
        with self.assertRaises(ValueError):
            WRAP.measure([[2]])

    def test_changed_mechanism_labels_or_omitted_declared_case_fail(self):
        settings = json.loads(WRAP.PARAMETERS.read_bytes())
        for field in ["mechanism", "case", "calibration"]:
            altered = deepcopy(settings)
            if field == "mechanism":
                altered["final_row"] = "include"
            elif field == "case":
                altered["cases"].pop()
            else:
                altered["finite_check"]["capacity"] = 7
            with self.subTest(field=field), self.assertRaises(ValueError):
                WRAP.build(altered)

    def test_cli_rejects_hardlink_to_temporary_input_copy_without_modifying_it(self):
        original = WRAP.PARAMETERS.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "parameters-copy.json"
            output = Path(folder) / "output-alias.json"
            source.write_bytes(original)
            os.link(source, output)
            result = subprocess.run([sys.executable, str(WRAP.ROOT / "scripts/greedy_wrap_control.py"),
                                     "--parameters", str(source), "--output", str(output)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("aliases an input", result.stderr)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
