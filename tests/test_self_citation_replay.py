import unittest
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

from scripts.replay_self_citation import (
    REMOVED_ENV, configuration, matches_runtime_version, process_environment,
    properties, run_process, text_projection,
)


class SelfCitationReplayTests(unittest.TestCase):
    def test_compiler_and_vm_options_are_removed_without_mutating_inherited_environment(self):
        inherited = {name: 'synthetic fixture value' for name in REMOVED_ENV}
        inherited.update(PATH='synthetic path', TZ='synthetic timezone')
        before = dict(inherited)
        result = process_environment(inherited)
        self.assertIn('JDK_JAVAC_OPTIONS', REMOVED_ENV)
        self.assertTrue(set(REMOVED_ENV).isdisjoint(result))
        self.assertEqual(result['PATH'], 'synthetic path')
        self.assertEqual(result['TZ'], 'UTC')
        self.assertEqual(result['LANG'], 'en_US.UTF-8')
        self.assertEqual(result['LC_ALL'], 'en_US.UTF-8')
        self.assertEqual(inherited, before)

    def test_runtime_guard_requires_the_exact_declared_version_token(self):
        for name, output in [('java', 'openjdk version "22.0.2" 2024-07-16\nbuild details'),
                             ('java', 'java version "22.0.2"'), ('javac', 'javac 22.0.2')]:
            self.assertTrue(matches_runtime_version(name, output), output)
        for name, output in [('java', 'openjdk version "22.0.20"'),
                             ('java', 'openjdk version "22.0.2-ea"'),
                             ('java', 'openjdk version "23.0.1"\nbuild mentions 22.0.2'),
                             ('javac', 'javac 22.0.20'),
                             ('javac', 'javac 23.0.1\ncompatible with 22.0.2'), ('java', '')]:
            self.assertFalse(matches_runtime_version(name, output), output)

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
