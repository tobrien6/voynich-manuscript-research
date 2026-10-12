import unittest

from scripts.trace_self_citation_rows import ANCHOR, OBSERVER, instrument, row_ledger, trace_events


class SelfCitationTraceTests(unittest.TestCase):
    def test_observer_is_one_insertion_and_refuses_missing_or_duplicate_anchors(self):
        synthetic = b'// synthetic surrounding bytes\n' + ANCHOR + b'\n'
        self.assertEqual(instrument(synthetic).replace(OBSERVER, b''), synthetic)
        for raw in [b'no anchor', ANCHOR + b'\n' + ANCHOR]:
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                instrument(raw)

    def test_trace_coverage_order_and_literal_flags_are_required(self):
        valid = b'VMS_ROW_TRACE_V1\t1\tfalse\ttrue\t0\t0\nVMS_ROW_TRACE_V1\t2\ttrue\tfalse\t1\t1\n'
        events, diagnostics = trace_events(valid, 1, 3)
        self.assertEqual(diagnostics, 0)
        self.assertTrue(events[1]['model_paragraph_initial'])
        for raw in [valid.splitlines(keepends=True)[0], valid + valid, b'\n'.join(reversed(valid.splitlines()))]:
            with self.assertRaisesRegex(ValueError, 'coverage/order'):
                trace_events(raw, 1, 3)
        with self.assertRaisesRegex(ValueError, 'malformed'):
            trace_events(valid.replace(b'false', b'unknown', 1), 1, 3)
        with self.assertRaisesRegex(ValueError, 'nonnegative'):
            trace_events(valid.replace(b'\t0\t0', b'\t-1\t0', 1), 1, 3)

    def test_ledger_offsets_preserve_native_rows_and_initialization_is_unannotated(self):
        raw = b'# synthetic header\r\n\r\nalpha beta\r\ngamma delta\r\n'
        events, _ = trace_events(b'VMS_ROW_TRACE_V1\t1\tfalse\ttrue\t0\t0\n', 1, 2)
        ledger = row_ledger(raw, events, 1, 2)
        self.assertTrue(ledger[0]['initialized_input_row'])
        self.assertIsNone(ledger[0]['model_paragraph_initial'])
        self.assertIsNone(ledger[0]['model_paragraph_final'])
        self.assertEqual(ledger[0]['native_file_line_number'], 3)
        self.assertEqual(raw[ledger[1]['start_byte']:ledger[1]['end_byte_exclusive_without_line_ending']], b'gamma delta')
        self.assertEqual(ledger[1]['space_delimited_token_count'], 2)
        self.assertTrue(ledger[1]['model_paragraph_final'])

    def test_unsupported_spacing_and_missing_rows_are_not_repaired(self):
        events, _ = trace_events(b'VMS_ROW_TRACE_V1\t1\tfalse\ttrue\t0\t0\n', 1, 2)
        with self.assertRaisesRegex(ValueError, 'unsupported notation/spacing'):
            row_ledger(b'alpha beta\ngamma  delta\n', events, 1, 2)
        with self.assertRaisesRegex(ValueError, 'row count differs'):
            row_ledger(b'alpha beta\n', events, 1, 2)
        with self.assertRaisesRegex(ValueError, 'complete ordered'):
            row_ledger(b'alpha beta\ngamma delta\n', [], 1, 2)


if __name__ == '__main__':
    unittest.main()
