import copy
from fractions import Fraction
from itertools import permutations
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import greedy_wrap_control as accepted_wrap
from scripts import interior_half_controls as accepted_half
from scripts import interior_length_order as accepted_full
from scripts import wrap_interior_symmetry as subject


class WrappingSymmetryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings, cls.raws = subject.load_settings()
        cls.laws = {item['id']: subject.law(item) for item in cls.settings['laws']}

    def test_all_fixed_classes_match_sequential_accepted_wrapper_and_exact_scores(self):
        for case in self.settings['cases']:
            with self.subTest(case=case['id']):
                probabilities = self.laws[case['law_id']]
                certificate = subject.certify_case(case, probabilities, 1)
                for order in certificate['orders']:
                    middle = order['interior']
                    row = [case['first'], *middle, case['last']]
                    independent = Fraction(0)
                    for incoming, p in probabilities.items():
                        rows, _ = accepted_wrap.wrap(row + [incoming], case['capacity'], 1)
                        if rows and rows[0] == row:
                            weight = p
                            for value in row[1:]:
                                weight *= probabilities[value]
                            independent += weight
                    self.assertEqual(str(independent), order['event_weight_given_first'])
                    if len(row) >= 5:
                        self.assertEqual(order['full_centered'], str(accepted_full.exact_score(middle)))
                        self.assertEqual(order['half_centered'], str(accepted_half.exact_centered_score(middle)))

    def test_unequal_iid_law_event_weight_is_separate_from_conditional_probability(self):
        case = next(x for x in self.settings['cases'] if x['id'] == 'unequal-law-24')
        result = subject.certify_case(case, self.laws[case['law_id']], 1)
        self.assertEqual(result['per_order_event_weight_given_first'], '1/1024')
        self.assertEqual(result['class_event_weight_given_first'], '3/128')
        self.assertEqual(result['conditional_order_probability'], '1/24')
        self.assertEqual(result['mean_full_centered'], '0')
        self.assertEqual(result['mean_half_centered'], '0')

    def test_repeated_orders_constant_short_and_impossible_conditions_are_retained(self):
        results = {c['id']: subject.certify_case(c, self.laws[c['law_id']], 1)
                   for c in self.settings['cases']}
        self.assertEqual(len(results['repeated-selective-18']['orders']), 3)
        self.assertEqual(results['constant-18']['orders'][0]['full_centered'], '0')
        short = results['short-two-8']
        self.assertEqual(short['status'], 'completed_short')
        self.assertEqual(short['conditional_order_probability'], '1')
        self.assertIsNone(short['mean_full_centered'])
        for key in ('no-closing-overflow-30', 'over-capacity-18'):
            self.assertEqual(results[key]['per_order_event_weight_given_first'], '0')
            self.assertIsNone(results[key]['conditional_order_probability'])
            self.assertIsNone(results[key]['mean_full_centered'])
            self.assertEqual(results[key]['orders'], [])

    def test_domain_guards_singletons_negative_geometry_and_invalid_laws(self):
        probabilities = self.laws['uniform-two']
        with self.assertRaisesRegex(ValueError, 'at least two'):
            subject.row_event_weight([2], probabilities, 8, 1)
        for capacity, separator in ((2, 1), (8, -1), (True, 1)):
            with self.subTest(capacity=capacity, separator=separator), self.assertRaises(ValueError):
                subject.row_event_weight([2, 3], probabilities, capacity, separator)
        for probabilities in (['1/2', '0'], ['1/2', '1/3']):
            with self.subTest(probabilities=probabilities), self.assertRaises(ValueError):
                subject.law({'support': [2, 3], 'probabilities': probabilities})
        with self.assertRaises(ValueError):
            subject.scores([2, 3])

    def test_zero_separator_equality_and_whole_stream_carry_tail(self):
        # Boundary implementation check, separate from the eight published fixtures.
        p = self.laws['uniform-two']
        weights = [subject.row_event_weight([2, *middle, 2], p, 12, 0)
                   for middle in sorted(set(permutations([2, 3, 3])))]
        self.assertEqual(len(set(weights)), 1)
        self.assertGreater(weights[0], 0)
        fixture = self.settings['stream_fixture']
        result = subject.certify_stream(fixture, self.laws[fixture['law_id']], 1)
        self.assertEqual(result['joint_unique_orders'], 9)
        self.assertEqual(result['original_unclosed_tail']['occupied_width'], 18)
        self.assertEqual(result['original_equal_row_full_centered'], '-1/8')
        self.assertEqual(result['original_equal_row_half_centered'], '-3/16')
        for item in result['orders']:
            rows, tail = accepted_wrap.wrap(item['stream'], 18, 1)
            self.assertEqual(rows, [r['lengths'] for r in item['completed_rows']])
            self.assertEqual(tail, [2, 2, 2, 3, 5])
            self.assertEqual(len(rows), 2)

    def test_frozen_protocol_drift_is_rejected_without_touching_real_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for path, raw in self.raws.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            (root / subject.PLAN).write_bytes(b'changed fixture plan')
            with patch.object(subject, 'ROOT', root), patch.object(subject.subprocess, 'check_output',
                    side_effect=lambda args, **kwargs: self.raws[Path(args[-1].split(':', 1)[1])]):
                with self.assertRaisesRegex(ValueError, 'frozen protocol'):
                    subject.load_settings()

    def test_archival_references_do_not_require_unchanged_live_documentation(self):
        real_root = subject.ROOT
        original_git = subject.subprocess.check_output
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for path, raw in self.raws.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            live = root / 'research/transliteration/INTERIOR_HALVES.md'
            live.parent.mkdir(parents=True)
            live.write_bytes(b'Later documentary supplement; historical definition unchanged')
            with patch.object(subject, 'ROOT', root), patch.object(subject.subprocess, 'check_output',
                    side_effect=lambda args, **kwargs: original_git(args, cwd=real_root)):
                settings, _ = subject.load_settings()
            self.assertEqual(settings, self.settings)

    def test_exclusive_output_rejects_existing_and_late_hardlink_aliases(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            original, output = root / 'copied-input.txt', root / 'result.json'
            original.write_bytes(b'unchanged synthetic fixture')
            os.link(original, output)
            with self.assertRaisesRegex(ValueError, 'new unlinked'):
                subject.write_report(output)
            output.unlink()
            def late_alias():
                os.link(original, output)
                return {'fixture': True}
            with patch.object(subject, 'build_report', side_effect=late_alias):
                with self.assertRaisesRegex(ValueError, 'new unlinked'):
                    subject.write_report(output)
            self.assertEqual(original.read_bytes(), b'unchanged synthetic fixture')
            with self.assertRaisesRegex(ValueError, 'protected output'):
                subject.protect_output(subject.ROOT / 'data/raw/new-symmetry-fixture.json')

    def test_complete_report_has_all_declared_attempts_and_deterministic_bytes(self):
        before = copy.deepcopy(self.settings)
        first, second = subject.build_report(), subject.build_report()
        self.assertEqual(subject.encoded(first), subject.encoded(second))
        self.assertEqual([x['id'] for x in first['cases']], [x['id'] for x in before['cases']])
        self.assertEqual(first['protocol_commit'], subject.PROTOCOL_COMMIT)
        self.assertEqual(self.settings, before)


if __name__ == '__main__':
    unittest.main()
