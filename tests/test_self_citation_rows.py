import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.audit_self_citation_rows import analyze, digest, ledger_bytes


class SelfCitationRowTests(unittest.TestCase):
    def test_initialization_is_excluded_and_physical_lines_are_preserved(self):
        summary, rows = analyze(b'#header\n\na b\nc d e\n', 'a b z')
        self.assertEqual([row['physical_file_line_1_based'] for row in rows], [3, 4])
        self.assertEqual([row['origin'] for row in rows], ['initialization', 'generated'])
        self.assertEqual(summary['group_occurrences_including_initialization'], 5)
        self.assertEqual(summary['newly_generated_group_occurrences'], 3)
        self.assertEqual(summary['newly_generated_rows'], 1)
        self.assertFalse(summary['stored_initial_row_equals_initial_input'])
        self.assertEqual(summary['initial_input']['group_occurrences'], 3)

    def test_single_initialization_row_is_not_a_generated_sample(self):
        summary, rows = analyze(b'a b', 'a b')
        self.assertEqual(summary['newly_generated_rows'], 0)
        self.assertIsNone(summary['generated_row_notation_character_range'])
        self.assertTrue(summary['stored_initial_row_equals_initial_input'])
        self.assertFalse(summary['final_line_terminator'])

    def test_empty_slots_non_ascii_and_unsupported_notation_are_rejected(self):
        for raw in (b'a  b\n', b' a\n', b'a \n', b'a\tb\n', b'\xc3\xa9\n', b'a.b\n', b'A\n', b'#only\n'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                analyze(raw, 'a')

    def test_line_ending_differences_remain_in_whole_file_fingerprint(self):
        lf, rows_lf = analyze(b'#h\na b\nc\n', 'a b')
        crlf, rows_crlf = analyze(b'#h\r\na b\r\nc\r\n', 'a b')
        self.assertEqual(rows_lf, rows_crlf)
        self.assertNotEqual(lf['sha256'], crlf['sha256'])
        self.assertEqual(crlf['line_ending'], 'CRLF')
        for raw in (b'a\r\nb\n', b'a\rb\n'):
            with self.assertRaises(ValueError):
                analyze(raw, 'a')

    def test_ledger_is_stable_and_contains_hashes_instead_of_row_text(self):
        summary, rows = analyze(b'alpha beta\ngamma\n', 'alpha beta')
        raw = ledger_bytes(rows)
        self.assertNotIn(b'alpha', raw)
        self.assertIn(digest(b'alpha beta').encode(), raw)
        self.assertEqual(raw, ledger_bytes(rows))

    def test_existing_input_or_duplicate_output_path_is_preserved(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/audit_self_citation_rows.py'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generated, config, ledger = root / 'generated.txt', root / 'conf.properties', root / 'ledger.csv'
            generated.write_bytes(b'a b\nc\n')
            config.write_bytes(b'text.initial_line=a b\n')
            for target in (generated, config, ledger):
                result = subprocess.run([sys.executable, str(script), str(generated), '--configuration', str(config),
                                         '--new-record', str(target), '--new-ledger', str(ledger)], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(generated.read_bytes(), b'a b\nc\n')
                self.assertEqual(config.read_bytes(), b'text.initial_line=a b\n')
                self.assertFalse(ledger.exists())

    def test_committed_ledger_retains_all_rows_and_the_initialization_denominator(self):
        root = Path(__file__).resolve().parents[1]
        record = json.loads((root / 'research/literature/self-citation-java17-replay.json').read_text())
        ledger = (root / record['row_accounting']['ledger_path']).read_bytes()
        rows = list(csv.DictReader(ledger.decode('ascii').splitlines()))
        self.assertEqual(digest(ledger), record['row_accounting']['ledger_sha256'])
        self.assertEqual([int(row['data_row_1_based']) for row in rows], list(range(1, 1201)))
        self.assertEqual([int(row['physical_file_line_1_based']) for row in rows], list(range(36, 1236)))
        self.assertEqual(rows[0]['origin'], 'initialization')
        self.assertTrue(all(row['origin'] == 'generated' for row in rows[1:]))
        self.assertEqual(sum(int(row['group_occurrences']) for row in rows), 10832)
        self.assertEqual(sum(int(row['group_occurrences']) for row in rows[1:]), 10823)
        self.assertEqual(record['row_accounting']['initial_input']['group_occurrences'], 11)
        self.assertEqual(int(rows[0]['group_occurrences']), 9)
        self.assertFalse(record['row_accounting']['stored_initial_row_equals_initial_input'])


if __name__ == '__main__':
    unittest.main()
