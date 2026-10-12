import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.audit_evaluation_freeze import ROOT, artifact_records, audit, record, relative_path
from scripts.validate_evaluation_split import load_split_json


class EvaluationFreezeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='synthetic-freeze-test-')
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.git('init', '--quiet')
        self.input_path = 'input.txt'
        self.split_path = 'split.json'
        self.rules = ['rules [literal].md', 'rule-support.txt']
        self.preprocessing = ['preprocessing.md']
        self.input_bytes = (ROOT / 'research/evaluation/examples/synthetic-input.txt').read_bytes()
        (self.repo / self.input_path).write_bytes(self.input_bytes)
        self.split = load_split_json((ROOT / 'research/evaluation/examples/synthetic-split.json').read_text())
        self.split['fit_started_at'] = None
        self.write_split()
        for path in self.rules + self.preprocessing:
            (self.repo / path).write_text('Synthetic fixture only; no manuscript data.\n')
        self.freeze = self.commit('Synthetic freeze')
        self.receipt = self.make_receipt()

    def git(self, *arguments):
        return subprocess.run([
            'git', '-C', str(self.repo), '-c', 'core.hooksPath=/dev/null',
            '-c', 'core.fsmonitor=false', '-c', 'core.autocrlf=false', '-c', 'commit.gpgSign=false',
            '-c', 'user.name=Synthetic test', '-c', 'user.email=synthetic@example.invalid', *arguments],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode().strip()

    def commit(self, message):
        self.git('add', '--all')
        self.git('commit', '--quiet', '-m', message)
        return self.git('rev-parse', 'HEAD')

    def write_split(self):
        (self.repo / self.split_path).write_text(json.dumps(self.split, indent=2) + '\n')

    def make_receipt(self, commit=None):
        return record(self.repo, commit or self.freeze, self.split_path, self.input_path,
                      self.rules, self.preprocessing)

    def test_freeze_and_unchanged_later_commit_reproduce(self):
        result = audit(self.receipt, self.repo)
        self.assertEqual(result['artifact_count'], 5)
        self.assertEqual(result['candidate_version'], self.split['candidate_version'])
        self.assertIsNone(result['run_commit'])
        (self.repo / 'synthetic-run-note.md').write_text('Synthetic later run; no fitting claim.\n')
        later = self.commit('Synthetic run record')
        self.assertEqual(audit(self.receipt, self.repo, later)['run_commit'], later)

    def test_changed_rules_and_preprocessing_fail_without_a_version_change(self):
        for path in self.rules + self.preprocessing:
            original = (self.repo / path).read_bytes()
            (self.repo / path).write_bytes(original + b'Changed rule.\n')
            with self.assertRaisesRegex(ValueError, 'working bytes differ'):
                audit(self.receipt, self.repo)
            (self.repo / path).write_bytes(original)

    def test_changed_run_commit_is_detected_even_when_working_bytes_are_restored(self):
        path = self.rules[0]
        original = (self.repo / path).read_bytes()
        (self.repo / path).write_bytes(original + b'Changed rule.\n')
        changed = self.commit('Synthetic changed run')
        (self.repo / path).write_bytes(original)
        with self.assertRaisesRegex(ValueError, 'run-commit bytes differ'):
            audit(self.receipt, self.repo, changed)

    def test_unrelated_or_same_commit_is_not_a_later_run(self):
        with self.assertRaisesRegex(ValueError, 'strict descendant'):
            audit(self.receipt, self.repo, self.freeze)
        self.git('checkout', '--quiet', '--orphan', 'unrelated')
        unrelated = self.commit('Synthetic unrelated history')
        with self.assertRaisesRegex(ValueError, 'not a descendant'):
            audit(self.receipt, self.repo, unrelated)

    def test_wrong_declared_hash_and_candidate_identity_fail(self):
        wrong = copy.deepcopy(self.receipt)
        wrong['artifacts']['rules'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'declared hash differs'):
            audit(wrong, self.repo)
        wrong = copy.deepcopy(self.receipt)
        wrong['candidate_version'] = 'other-version'
        with self.assertRaisesRegex(ValueError, 'candidate_version differs'):
            audit(wrong, self.repo)

    def test_changed_input_pin_and_already_started_fitting_fail(self):
        (self.repo / self.input_path).write_bytes(self.input_bytes + b'Changed input.\n')
        changed = self.commit('Synthetic changed input')
        with self.assertRaisesRegex(ValueError, 'Input bytes differ'):
            self.make_receipt(changed)
        (self.repo / self.input_path).write_bytes(self.input_bytes)
        self.split['fit_started_at'] = '2000-01-03T00:00:00Z'
        self.write_split()
        fitted = self.commit('Synthetic fitting declaration')
        with self.assertRaisesRegex(ValueError, 'fitting not yet started'):
            self.make_receipt(fitted)

    def test_unresolved_evaluation_exposure_fails_in_the_committed_split(self):
        self.split['units'][-1]['prior_exposure']['state'] = 'unknown'
        self.write_split()
        changed = self.commit('Synthetic unresolved exposure')
        with self.assertRaisesRegex(ValueError, 'remains unresolved'):
            self.make_receipt(changed)

    def test_symlink_artifacts_and_missing_files_are_rejected(self):
        path = self.preprocessing[0]
        (self.repo / path).unlink()
        (self.repo / path).symlink_to(self.rules[0])
        with self.assertRaisesRegex(ValueError, 'symlink'):
            audit(self.receipt, self.repo)
        linked = self.commit('Synthetic symlink artifact')
        with self.assertRaisesRegex(ValueError, 'tracked regular file'):
            self.make_receipt(linked)
        (self.repo / path).unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            audit(self.receipt, self.repo)

    def test_literal_paths_are_required_and_all_rule_files_are_checked(self):
        for path in ['/outside', '../outside', 'a/../rules', 'a//rules', './rules', '.git/config', 'a\\rules']:
            with self.assertRaises(ValueError):
                relative_path(path)
        wrong = copy.deepcopy(self.receipt)
        wrong['artifacts']['rules'] = []
        with self.assertRaisesRegex(ValueError, 'nonempty'):
            artifact_records(wrong)
        wrong['artifacts']['rules'] = [self.receipt['artifacts']['rules'][0]] * 2
        with self.assertRaisesRegex(ValueError, 'duplicate artifact path'):
            artifact_records(wrong)

    def test_duplicate_declarations_and_symbolic_commit_names_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate object member'):
            load_split_json('{"freeze_commit":"a","freeze_commit":"b"}')
        wrong = copy.deepcopy(self.receipt)
        wrong['freeze_commit'] = 'HEAD'
        with self.assertRaisesRegex(ValueError, 'full lowercase'):
            audit(wrong, self.repo)

    def test_replacement_refs_do_not_substitute_a_different_freeze_tree(self):
        original = (self.repo / self.rules[0]).read_bytes()
        (self.repo / self.rules[0]).write_bytes(original + b'Changed rule.\n')
        replacement = self.commit('Synthetic replacement tree')
        self.git('replace', self.freeze, replacement)
        with self.assertRaisesRegex(ValueError, 'working bytes differ'):
            self.make_receipt()
        (self.repo / self.rules[0]).write_bytes(original)
        self.assertEqual(audit(self.receipt, self.repo)['freeze_commit'], self.freeze)

    def test_legacy_grafts_cannot_change_declared_history(self):
        graft_path = self.repo / '.git/info/grafts'
        graft_path.write_text(self.freeze + '\n')
        with self.assertRaisesRegex(ValueError, 'legacy Git grafts'):
            audit(self.receipt, self.repo)

    def test_cli_records_checks_and_refuses_to_overwrite_an_artifact_or_receipt(self):
        script = ROOT / 'scripts/audit_evaluation_freeze.py'
        target = self.repo / 'receipt.json'
        command = [sys.executable, str(script), '--repo', str(self.repo), 'record',
                   '--commit', self.freeze, '--split', self.split_path, '--input', self.input_path,
                   '--rules', *self.rules, '--preprocessing', *self.preprocessing, '--output', str(target)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(script), '--repo', str(self.repo),
                                 'check', str(target)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['artifact_count'], 5)
        original = target.read_bytes()
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('already exists', result.stderr)
        self.assertEqual(target.read_bytes(), original)
        result = subprocess.run(command[:-1] + [str(self.repo / self.input_path)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('must not overwrite', result.stderr)
        self.assertEqual((self.repo / self.input_path).read_bytes(), self.input_bytes)

    def test_cli_rejects_ambiguous_receipts_without_a_traceback(self):
        path = self.repo / 'ambiguous-receipt.json'
        path.write_text(json.dumps(self.receipt).replace('"schema_version": 1',
                                                       '"schema_version": 2, "schema_version": 1'))
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/audit_evaluation_freeze.py'),
                                 '--repo', str(self.repo), 'check', str(path)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('duplicate object member', result.stderr)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
