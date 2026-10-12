from fractions import Fraction
import unittest

from scripts.census_self_citation_prefixes import measurements, summaries
from scripts.trace_self_citation_rows import row_ledger, trace_events


class GeneratedPrefixCensusTests(unittest.TestCase):
    def test_initialization_and_single_token_rows_cannot_affect_contrasts(self):
        raw = b'q q\nq a\na a q\nq\n'
        events, _ = trace_events(b'VMS_ROW_TRACE_V1\t1\tfalse\tfalse\t2\t2\n'
                                 b'VMS_ROW_TRACE_V1\t2\tfalse\tfalse\t3\t3\n'
                                 b'VMS_ROW_TRACE_V1\t3\ttrue\ttrue\t0\t0\n', 1, 4)
        result = measurements(raw, row_ledger(raw, events, 1, 4))
        self.assertEqual(result['initialized_rows'], 1)
        self.assertEqual([row['generated_row_index'] for row in result['excluded_rows']], [0, 3])
        first = next(cell for cell in result['cells'] if not cell['model_paragraph_initial'] and
                     cell['boundary'] == 'first' and cell['prefix'] == 'q')
        mean = first['mean_difference_exact']
        self.assertEqual(Fraction(int(mean['numerator']), int(mean['denominator'])), Fraction(1, 4))
        self.assertEqual(first['eligible_rows'], 2)
        self.assertTrue(all(cell['eligible_rows'] == 2 for cell in result['cells'] if not cell['model_paragraph_initial']))
        self.assertTrue(all(cell['mean_difference_exact'] is None for cell in result['cells'] if cell['model_paragraph_initial']))

    def test_summary_keeps_every_sign_and_undefined_seed(self):
        cell = {'model_paragraph_initial': False, 'boundary': 'first', 'prefix': 'q',
                'mean_difference_exact': {'numerator': '-1', 'denominator': '4'}}
        cases = [{'seed': 1, 'measurements': {'cells': [cell]}}, {'seed': 2, 'measurements': None}]
        result = summaries(cases)
        first = result[0]
        self.assertEqual(first['negative_seeds'], 1)
        self.assertEqual(first['missing_seeds'], [2])
        self.assertEqual(len(result), 8)
        self.assertTrue(all(row['missing_seeds'] == [1, 2] for row in result[1:]))

    def test_changed_row_identity_or_bytes_fail_before_measurement(self):
        raw = b'a q\nq a\n'
        events, _ = trace_events(b'VMS_ROW_TRACE_V1\t1\tfalse\ttrue\t0\t0\n', 1, 2)
        ledger = row_ledger(raw, events, 1, 2)
        with self.assertRaisesRegex(ValueError, 'row hash differs'):
            measurements(b'q a\nq a\n', ledger)
        ledger[1]['generated_row_index'] = 3
        with self.assertRaisesRegex(ValueError, 'identity/order'):
            measurements(raw, ledger)


if __name__ == '__main__':
    unittest.main()
