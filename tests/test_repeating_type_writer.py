import contextlib
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

from scripts import repeating_types as producer
from scripts import write_repeating_types as writer
try:
    from .test_repeating_types import synthetic_root
except ImportError:
    from test_repeating_types import synthetic_root


def fixture(path):
    root = synthetic_root(path)
    shutil.copyfile(Path(writer.__file__), root / 'scripts/write_repeating_types.py')
    return root


def link(target, output, kind):
    if kind == 'symlink':
        output.symlink_to(target)
    else:
        os.link(target, output)


class RepeatingTypeWriterTests(unittest.TestCase):
    def test_copied_cli_matches_complete_original_bytes_and_checks_typed_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = fixture(Path(directory))
            with patch.object(producer, 'ROOT', root):
                expected = producer.encoded(producer.report())
            command = [sys.executable, str(root / 'scripts/write_repeating_types.py')]
            output = root / 'mean.json'
            wrote = subprocess.run([*command, '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(wrote.returncode, 0, wrote.stderr)
            self.assertEqual(output.read_bytes(), expected)
            checked = subprocess.run([*command, '--check', str(output)], capture_output=True, text=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            original = output.read_bytes()
            # The schema version is integer1, not a bool accepted by dict equality.
            cache = json.loads(original)
            cache['schema_version'] = True
            output.write_text(json.dumps(cache))
            bad = subprocess.run([*command, '--check', str(output)], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            self.assertIn('complete producer replay', bad.stderr)
            output.write_text('{"schema_version":1,"schema_version":1}')
            duplicate = subprocess.run([*command, '--check', str(output)], capture_output=True, text=True)
            self.assertEqual(duplicate.returncode, 1)

    def test_every_declared_input_rejects_entry_aliases_before_calculation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = fixture(Path(directory))
            with patch.object(producer, 'ROOT', root):
                targets = set(p for p in writer.protected_inputs() if p.is_relative_to(root))
                for kind in ('direct', 'symlink', 'hardlink'):
                    for target in targets:
                        with self.subTest(kind=kind, target=target.relative_to(root)):
                            before = target.read_bytes()
                            output = target if kind == 'direct' else root / 'alias.json'
                            if kind != 'direct':
                                link(target, output, kind)
                            with patch.object(producer, 'report') as calculate, \
                                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                                writer.main(['--output', str(output)])
                            self.assertEqual(error.exception.code, 1)
                            calculate.assert_not_called()
                            self.assertEqual(target.read_bytes(), before)
                            if kind != 'direct':
                                output.unlink()

    def test_construction_and_serialization_aliases_preserve_temporary_targets(self):
        for stage in ('construction', 'serialization'):
            for kind in ('symlink', 'hardlink'):
                for name in (producer.PLAN, 'data/raw/ZL3b.txt', 'scripts/repeating_types.py',
                             'scripts/write_repeating_types.py'):
                    with self.subTest(stage=stage, kind=kind, name=name), tempfile.TemporaryDirectory() as directory:
                        root = fixture(Path(directory))
                        target, output = root / name, root / 'mean.json'
                        before = target.read_bytes()
                        real_report, real_encoded = producer.report, producer.encoded
                        def calculate():
                            result = real_report()
                            if stage == 'construction':
                                link(target, output, kind)
                            return result
                        def serialize(value):
                            payload = real_encoded(value)
                            if stage == 'serialization' and isinstance(value, dict) and 'method' in value:
                                link(target, output, kind)
                            return payload
                        with patch.object(producer, 'ROOT', root), \
                                patch.object(producer, 'report', side_effect=calculate), \
                                patch.object(producer, 'encoded', side_effect=serialize), \
                                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                            writer.main(['--output', str(output)])
                        self.assertEqual(error.exception.code, 1)
                        self.assertEqual(target.read_bytes(), before)
                        self.assertEqual(output.read_bytes(), before)

    def test_entry_and_current_catalog_paths_remain_protected(self):
        for declaration in ('removed_original', 'new_declared'):
            with self.subTest(declaration=declaration), tempfile.TemporaryDirectory() as directory:
                root = fixture(Path(directory))
                target = root / ('data/raw/ZL3b.txt' if declaration == 'removed_original' else 'new-raw.txt')
                if declaration == 'new_declared':
                    target.write_bytes(b'new temporary input')
                before, output = target.read_bytes(), root / 'mean.json'
                real_encoded = producer.encoded
                def serialize(value):
                    payload = real_encoded(value)
                    if isinstance(value, dict) and 'method' in value:
                        sources = [] if declaration == 'removed_original' else [{'path': 'new-raw.txt'}]
                        (root / 'data/transliterations.json').write_text(json.dumps({'sources': sources}))
                        output.hardlink_to(target)
                    return payload
                with patch.object(producer, 'ROOT', root), patch.object(producer, 'encoded', side_effect=serialize), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    writer.main(['--output', str(output)])
                self.assertEqual(error.exception.code, 1)
                self.assertEqual(target.read_bytes(), before)

    def test_copied_cli_rejects_writer_alias_and_source_pin_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = fixture(Path(directory))
            script = root / 'scripts/write_repeating_types.py'
            before = script.read_bytes()
            alias = root / 'writer-alias.json'
            alias.hardlink_to(script)
            command = [sys.executable, str(script)]
            rejected = subprocess.run([*command, '--output', str(alias)], capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 1)
            self.assertEqual(script.read_bytes(), before)
            raw = root / 'data/raw/ZL3b.txt'
            raw.write_bytes(raw.read_bytes() + b'\n')
            output = root / 'failed.json'
            failed = subprocess.run([*command, '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(failed.returncode, 1)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
