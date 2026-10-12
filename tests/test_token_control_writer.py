import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import write_token_control as writer


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'research/token-controls/synthetic-corpus.json'


class TokenControlWriterTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='synthetic-token-writer-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'scripts').mkdir()
        for name in ('write_token_control.py', 'shuffle_token_lines.py'):
            shutil.copyfile(ROOT / 'scripts' / name, self.root / 'scripts' / name)
        self.corpus = self.root / 'synthetic-corpus.json'
        self.original = FIXTURE.read_bytes()
        self.corpus.write_bytes(self.original)
        self.script = self.root / 'scripts/write_token_control.py'

    def run_cli(self, output, scope='line', extra=(), module=False):
        invocation = ['-m', 'scripts.write_token_control'] if module else [str(self.script)]
        return subprocess.run([sys.executable, '-B', *invocation, str(self.corpus),
                               '--scope', scope, '--seed', '1729', '--trial', '0',
                               '--output', str(output), *extra], cwd=ROOT,
                              capture_output=True, text=True)

    def test_actual_cli_refuses_direct_resolved_symlink_and_hardlink_aliases_of_all_inputs(self):
        protected = [self.corpus, self.script, self.root / 'scripts/shuffle_token_lines.py']
        before = {path: path.read_bytes() for path in protected}
        for index, source in enumerate(protected):
            symbolic = self.root / f'symbolic-{index}.json'
            symbolic.symlink_to(source)
            hardlink = self.root / f'hardlink-{index}.json'
            os.link(source, hardlink)
            resolved = source.parent / 'unused' / '..' / source.name
            for output in (source, resolved, symbolic, hardlink):
                with self.subTest(source=source.name, output=output.name):
                    result = self.run_cli(output)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn('aliases its original corpus, writer, or shuffle producer', result.stderr)
                    self.assertEqual({path: path.read_bytes() for path in protected}, before)

    def test_both_scopes_and_entry_points_reproduce_committed_control_bytes(self):
        digest = hashlib.sha256(self.original).hexdigest()
        for scope, fixture in [('line', 'example-line-control.json'),
                               ('folio-side', 'example-folio-side-control.json')]:
            expected = (ROOT / 'research/token-controls' / fixture).read_bytes()
            for module in (False, True):
                with self.subTest(scope=scope, module=module):
                    output = self.root / f'{scope}-{module}.json'
                    result = self.run_cli(output, scope, ('--expected-sha256', digest), module)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(output.read_bytes(), expected)
                    self.assertEqual(self.corpus.read_bytes(), self.original)

    def test_ordinary_existing_output_is_replaced_without_mutating_corpus(self):
        output = self.root / 'existing-unrelated.json'
        output.write_bytes(b'Old unrelated output.\n')
        result = self.run_cli(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.read_bytes(), (ROOT / 'research/token-controls/example-line-control.json').read_bytes())
        self.assertEqual(self.corpus.read_bytes(), self.original)

    def test_hash_mismatch_and_invalid_corpus_leave_input_and_existing_output_unchanged(self):
        output = self.root / 'unrelated-output.json'
        sentinel = b'Unrelated existing output.\n'
        output.write_bytes(sentinel)
        mismatch = self.run_cli(output, extra=('--expected-sha256', '0' * 64))
        self.assertEqual(mismatch.returncode, 1)
        self.assertIn('input bytes do not match', mismatch.stderr)
        self.assertEqual(output.read_bytes(), sentinel)
        self.assertEqual(self.corpus.read_bytes(), self.original)
        invalid = json.loads(self.original)
        invalid['control'] = {'synthetic': True}
        self.corpus.write_text(json.dumps(invalid))
        original_invalid = self.corpus.read_bytes()
        failed = self.run_cli(output)
        self.assertEqual(failed.returncode, 1)
        self.assertIn('original corpus', failed.stderr)
        self.assertEqual(output.read_bytes(), sentinel)
        self.assertEqual(self.corpus.read_bytes(), original_invalid)

    def test_alias_created_during_calculation_is_rechecked_before_writing(self):
        output = self.root / 'late-alias.json'
        result = writer.generator.make_control(self.original, 'line', 1729, 0)
        def create_alias(*unused):
            os.link(self.corpus, output)
            return result
        with patch.object(writer.generator, 'make_control', side_effect=create_alias), \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as failed:
            writer.main([str(self.corpus), '--scope', 'line', '--seed', '1729',
                         '--trial', '0', '--output', str(output)])
        self.assertEqual(failed.exception.code, 1)
        self.assertEqual(self.corpus.read_bytes(), self.original)
        self.assertEqual(output.read_bytes(), self.original)


if __name__ == '__main__':
    unittest.main()
