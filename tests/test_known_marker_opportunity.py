from collections import Counter
from fractions import Fraction
import itertools
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import known_marker_opportunity as demo


class MarkerOpportunityTests(unittest.TestCase):
    def test_exhaustive_two_row_two_slot_round_trips(self):
        count = 0
        for values in itertools.product(sorted(demo.VOCABULARY), repeat=4):
            rows = [list(values[:2]), list(values[2:])]
            encoded = demo.encode(rows)
            self.assertEqual(demo.decode(encoded), rows)
            self.assertEqual([row[1] for row in encoded], [row[1] for row in rows])
            count += 1
        self.assertEqual(count, 1296)

    def test_one_marker_is_removed_even_from_natural_source_y(self):
        rows = [['ya', 'yc'], ['yc', 'ya']]
        self.assertEqual(demo.encode(rows), [['yya', 'yc'], ['yyc', 'ya']])
        self.assertEqual(demo.decode(demo.encode(rows)), rows)

    def test_invalid_source_and_encoded_rows_are_rejected(self):
        for invalid in ([], 'ab', [[]], [['not-in-vocabulary']], [['a', None]]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                demo.encode(invalid)
        for invalid in ([], 'ya', [[]], [['a', 'ya']], [['y', 'z']], [['ywrong', 'z']], [['yb', 'wrong']]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                demo.decode(invalid)

    def test_known_development_only_counts_and_unchanged_other_slots(self):
        development, diagnostic = demo.fixture()
        encoded_development, encoded_diagnostic = demo.encode(development), demo.encode(diagnostic)
        result = demo.score(encoded_development, encoded_diagnostic)
        self.assertEqual(result['development_dictionary_counts'], {'a': 1, 'b': 1, 'c': 1, 'ya': 2, 'z': 1})
        self.assertNotIn('yc', result['development_dictionary_counts'])
        self.assertNotIn('yz', result['development_dictionary_counts'])
        self.assertEqual([row[1:] for row in diagnostic], [row[1:] for row in encoded_diagnostic])
        self.assertEqual(result['development_internal_tokens'], 6)

    def test_scores_match_independent_membership_and_two_cell_calculation(self):
        development, diagnostic = demo.fixture()
        encoded_development, encoded_diagnostic = demo.encode(development), demo.encode(diagnostic)
        result = demo.score(encoded_development, encoded_diagnostic)
        counts = Counter(token for row in encoded_development for token in row[1:])
        membership = set(counts)
        first = [row[0] for row in encoded_diagnostic]
        other = [token for row in encoded_diagnostic for token in row[1:] if token.startswith('y')]
        def avg_gain(values):
            return Fraction(sum(int(value[1:] in membership)-int(value in membership) for value in values), len(values))
        self.assertEqual((avg_gain(first), avg_gain(other)), (Fraction(4, 5), Fraction(1, 5)))
        self.assertEqual(result['unstandardized_same_unit']['first_minus_other_gain'], {'numerator': 3, 'denominator': 5})
        matched = [[avg_gain([v for v in values if counts[v] == 0]), avg_gain([v for v in values if counts[v] >= 2])]
                   for values in (first, other)]
        self.assertEqual(matched, [[1, 0], [1, 0]])
        self.assertEqual(result['matched_equal_cells_within_same_unit']['first_gain'], {'numerator': 1, 'denominator': 2})
        self.assertEqual(result['matched_equal_cells_within_same_unit']['other_gain'], {'numerator': 1, 'denominator': 2})
        self.assertEqual(result['matched_equal_cells_within_same_unit']['first_minus_other_gain'], {'numerator': 0, 'denominator': 1})
        self.assertEqual(result['matched_minus_unstandardized_selectivity'], {'numerator': -3, 'denominator': 5})

    def test_fixed_opportunity_memberships_and_empty_cells(self):
        development, diagnostic = demo.fixture()
        result = demo.score(demo.encode(development), demo.encode(diagnostic))
        self.assertEqual(result['common_cell_ids'], [{'frequency_bin': '0', 'length_bin': '2-4'},
                                                    {'frequency_bin': '2+', 'length_bin': '2-4'}])
        cells = result['all_y_opportunity_cells']
        self.assertEqual(len(cells), 9)
        present = [c for c in cells if c['first_slot']['candidate_tokens']]
        self.assertEqual([(c['first_slot']['candidate_tokens'], c['other_slots']['candidate_tokens']) for c in present], [(4, 1), (1, 4)])
        for c in cells:
            if not c['first_slot']['candidate_tokens']:
                self.assertIsNone(c['first_slot']['mean_match_gain'])
                self.assertIsNone(c['other_slots']['mean_match_gain'])

    def test_all_four_lookup_cells_remain_available(self):
        summary, gain = demo.controls.lookup_summary(['ya', 'yb', 'yc', 'yd'], Counter({'a': 1, 'yb': 1, 'c': 1, 'yc': 1}), 'y')
        self.assertEqual(gain, 0)
        self.assertEqual([summary[key] for key in ('stripped_only', 'original_only', 'both_match', 'neither_matches')], [1, 1, 1, 1])

    def test_input_pin_drift_and_output_aliases_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            plan = root / demo.PLAN
            plan.parent.mkdir(parents=True)
            plan.write_bytes(b'fixed plan')
            record = {'analysis_id': 'known-marker-opportunity-v1', 'pins': {'plan': {'path': demo.PLAN, 'sha256': demo.sha(plan.read_bytes())}}}
            (root / demo.INPUTS).write_text(json.dumps(record))
            catalog = root / 'data/transliterations.json'
            catalog.parent.mkdir()
            catalog.write_text(json.dumps({'sources': []}))
            with patch.object(demo, 'ROOT', root), patch.object(demo.controls.source, 'ROOT', root):
                self.assertEqual(demo.verify_inputs(), record)
                for kind in ('direct', 'symlink', 'hardlink'):
                    alias = root / ('alias-' + kind)
                    if kind == 'direct': alias = plan
                    elif kind == 'symlink': alias.symlink_to(plan)
                    else: os.link(plan, alias)
                    with self.subTest(kind=kind), self.assertRaises(ValueError):
                        demo.protect_output(alias, record)
                demo.protect_output(root / 'safe.json', record)
                plan.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, 'pin changed'):
                    demo.verify_inputs()


if __name__ == '__main__':
    unittest.main()
