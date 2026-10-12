import unittest
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

from scripts.replay_self_citation import configuration, properties, run_process, text_projection


class SelfCitationReplayTests(unittest.TestCase):
    def test_config_overrides_preserve_every_other_effective_property(self):
        raw = b'# synthetic properties only\na=old\nb=unchanged\nc=1\n'
        result = configuration(raw, {'a': 'new', 'c': '2'})
        self.assertEqual(properties(result), {'a': 'new', 'b': 'unchanged', 'c': '2'})
        self.assertIn(b'# synthetic properties only\n', result)

    def test_missing_duplicate_or_unsupported_property_declarations_fail(self):
        with self.assertRaisesRegex(ValueError, 'missing property'):
            configuration(b'a=1\n', {'b': '2'})
        for raw in [b'a=1\na=2\n', b'a=1\\\n', b'a:1\n']:
            with self.assertRaises(ValueError):
                properties(raw)

    def test_text_projection_removes_only_comments_blank_lines_and_line_endings(self):
        raw = b'# metadata\r\n\r\n  # more metadata\r\nalpha  beta \r\n gamma\r\n'
        projected, record = text_projection(raw)
        self.assertEqual(projected, b'alpha  beta \n gamma\n')
        self.assertEqual(record['text_rows'], 2)
        self.assertNotEqual(record['sha256'], record['projected_sha256'])
        self.assertIsNotNone(record['first_row_sha256'])

    def test_empty_projection_and_invalid_utf8_are_explicit(self):
        projected, record = text_projection(b'# comments only\n\n')
        self.assertEqual(projected, b'')
        self.assertEqual(record['text_rows'], 0)
        self.assertIsNone(record['first_row_sha256'])
        with self.assertRaises(UnicodeDecodeError):
            text_projection(b'\xff\n')

    def test_failed_process_retains_logs_and_nonzero_outcome(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / 'process'
            outcome = subprocess.CompletedProcess(['synthetic'], 3, b'partial output', b'failure details')
            with patch('scripts.replay_self_citation.subprocess.run', return_value=outcome):
                result = run_process(['synthetic'], directory, {}, prefix)
            self.assertEqual(result['exit_code'], 3)
            self.assertFalse(result['timed_out'])
            self.assertEqual(prefix.with_suffix('.stdout.txt').read_bytes(), b'partial output')
            self.assertEqual(prefix.with_suffix('.stderr.txt').read_bytes(), b'failure details')

    def test_timeout_retains_partial_logs_and_cannot_look_like_success(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / 'process'
            outcome = subprocess.TimeoutExpired(['synthetic'], 120, output=b'partial', stderr=b'limit reached')
            with patch('scripts.replay_self_citation.subprocess.run', side_effect=outcome):
                result = run_process(['synthetic'], directory, {}, prefix)
            self.assertIsNone(result['exit_code'])
            self.assertTrue(result['timed_out'])
            self.assertEqual(prefix.with_suffix('.stdout.txt').read_bytes(), b'partial')
            self.assertEqual(prefix.with_suffix('.stderr.txt').read_bytes(), b'limit reached')


if __name__ == '__main__':
    unittest.main()
