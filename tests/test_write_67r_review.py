"""Exercise real copied CLIs and late changes only in synthetic temporary trees."""

from contextlib import redirect_stderr, redirect_stdout
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

from scripts import write_67r_review as writer


ROOT = Path(__file__).resolve().parents[1]


def fixture(directory):
    root = Path(directory)
    (root / 'scripts').mkdir()
    (root / 'data/raw').mkdir(parents=True)
    (root / 'research/panel-regions').mkdir(parents=True)
    for relative in writer.ENGINES:
        shutil.copyfile(ROOT / relative, root / relative)
    sources = []
    for sid, alphabet, body in (('ZL3b', 'Eva-', 'a.b.c'), ('IT2a', 'EvaT', 'd.e.f')):
        lines = [f'#=IVTFF {alphabet} 2.0 A', '<f67r1>']
        lines += [f'<f67r1.{n},@P0> {body}' for n in range(1, 5)]
        lines += ['<f67r2>']
        lines += [f'<f67r2.{n},+P0> {"a.b.c" if n == 72 else body}' for n in range(72, 75)]
        raw = ('\n'.join(lines) + '\n').encode('ascii')
        path = f'data/raw/{sid}.txt'
        (root / path).write_bytes(raw)
        sources.append({'id': sid, 'path': path, 'url': f'https://example.invalid/{sid}',
                        'alphabet': alphabet, 'bytes': len(raw),
                        'sha256': hashlib.sha256(raw).hexdigest(),
                        'credit': 'Synthetic fixture, not manuscript evidence'})
    (root / writer.CONTEXT[0]).write_text(json.dumps({'sources': sources}), encoding='utf-8')
    (root / writer.CONTEXT[1]).write_text('Synthetic provisional proposal\n', encoding='utf-8')
    report = writer.producer.build(root=root)
    (root / writer.CONTEXT[2]).write_bytes(writer.rendered(report))
    return root, report


def cli(root, *arguments, legacy=False, package=False):
    script = 'build_67r_review' if legacy else 'write_67r_review'
    command = ([sys.executable, '-m', f'scripts.{script}'] if package
               else [sys.executable, str(root / 'scripts' / f'{script}.py')])
    return subprocess.run([*command, *map(str, arguments)], cwd=root,
                          capture_output=True, text=True)


def inventory(root):
    return {str(path.relative_to(root)): path.read_bytes()
            for folder in ('data', 'research', 'scripts')
            for path in (root / folder).rglob('*')
            if path.is_file() and '__pycache__' not in path.parts}


class ChecklistWriterTests(unittest.TestCase):
    def invoke(self, root, *arguments):
        with patch.object(writer.producer, 'ROOT', root), redirect_stdout(io.StringIO()), \
                redirect_stderr(io.StringIO()):
            return writer.main(list(map(str, arguments)))

    def refuse(self, root, *arguments):
        with self.assertRaises(SystemExit) as error:
            self.invoke(root, *arguments)
        self.assertEqual(error.exception.code, 1)

    def test_script_and_package_create_legacy_bytes_and_check_reordered_objects(self):
        with tempfile.TemporaryDirectory() as directory:
            root, report = fixture(directory)
            before = inventory(root)
            legacy = root / 'legacy.json'
            self.assertEqual(cli(root, '--output', legacy, legacy=True).returncode, 0)
            for package in (False, True):
                output = root / f'new-{package}.json'
                process = cli(root, '--new-report', output, package=package)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertEqual(output.read_bytes(), legacy.read_bytes())
                self.assertEqual(json.loads(output.read_bytes()), report)
                output.write_text(json.dumps(report, sort_keys=True), encoding='utf-8')
                self.assertEqual(cli(root, '--check', output, package=package).returncode, 0)
            self.assertEqual(inventory(root), before)

    def test_copied_legacy_overwrites_are_refused_by_companion(self):
        # Preserve the concrete defect without using real source files as targets.
        for kind in ('symbolic', 'hard'):
            for relative in (writer.CONTEXT[1], 'data/raw/ZL3b.txt', writer.ENGINES[0]):
                with self.subTest(kind=kind, relative=relative), tempfile.TemporaryDirectory() as directory:
                    root, _ = fixture(directory)
                    target = root / relative
                    before = target.read_bytes()
                    alias = root / 'alias.json'
                    alias.symlink_to(target) if kind == 'symbolic' else os.link(target, alias)
                    self.assertNotEqual(cli(root, '--new-report', alias).returncode, 0)
                    self.assertEqual(target.read_bytes(), before)
                    legacy = cli(root, '--output', alias, legacy=True)
                    self.assertEqual(legacy.returncode, 0, legacy.stderr)
                    self.assertNotEqual(target.read_bytes(), before)
                    self.assertEqual(json.loads(target.read_bytes())['locations'], 7)

    def test_existing_direct_symbolic_hard_and_dangling_destinations_are_preserved(self):
        for kind in ('direct', 'symbolic', 'hard', 'dangling'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root, _ = fixture(directory)
                original = root / 'existing.json'
                original.write_bytes(b'preserve this existing file\n')
                target = root / 'output.json'
                if kind == 'direct':
                    target = original
                elif kind == 'symbolic':
                    target.symlink_to(original)
                elif kind == 'hard':
                    os.link(original, target)
                else:
                    target.symlink_to(root / 'missing.json')
                with patch.object(writer.producer, 'build', side_effect=AssertionError('calculation ran')):
                    self.refuse(root, '--new-report', target)
                self.assertEqual(original.read_bytes(), b'preserve this existing file\n')
                self.assertFalse((root / 'missing.json').exists())

    def test_every_protected_entry_alias_is_refused_before_calculation(self):
        for relative in (*writer.CONTEXT, *writer.ENGINES, 'data/raw/ZL3b.txt', 'data/raw/IT2a.txt'):
            for kind in ('direct', 'symbolic', 'hard'):
                with self.subTest(relative=relative, kind=kind), tempfile.TemporaryDirectory() as directory:
                    root, _ = fixture(directory)
                    target = root / relative
                    before = inventory(root)
                    output = target if kind == 'direct' else root / 'alias.json'
                    if kind == 'symbolic':
                        output.symlink_to(target)
                    elif kind == 'hard':
                        os.link(target, output)
                    with patch.object(writer.producer, 'build', side_effect=AssertionError('calculation ran')):
                        self.refuse(root, '--new-report', output)
                    self.assertEqual(inventory(root), before)

    def test_late_aliases_after_calculation_and_serialization_preserve_targets(self):
        for phase in ('calculation', 'serialization'):
            for kind in ('symbolic', 'hard'):
                for relative in (*writer.CONTEXT, *writer.ENGINES, 'data/raw/ZL3b.txt'):
                    with self.subTest(phase=phase, kind=kind, relative=relative), \
                            tempfile.TemporaryDirectory() as directory:
                        root, report = fixture(directory)
                        output, target = root / 'new.json', root / relative
                        before = inventory(root)

                        def changed(*args, **kwargs):
                            output.symlink_to(target) if kind == 'symbolic' else os.link(target, output)
                            return report if phase == 'calculation' else original_render(report)

                        original_render = writer.rendered
                        module, name = (writer.producer, 'build') if phase == 'calculation' else (writer, 'rendered')
                        with patch.object(module, name, side_effect=changed):
                            self.refuse(root, '--new-report', output)
                        self.assertEqual(inventory(root), before)

    def test_data_and_scripts_subtrees_include_resolved_parent_links(self):
        for folder in ('data', 'scripts'):
            for late in (False, True):
                with self.subTest(folder=folder, late=late), tempfile.TemporaryDirectory() as directory:
                    root, report = fixture(directory)
                    empty = root / 'empty'
                    empty.mkdir()
                    parent = root / 'parent'
                    parent.symlink_to(empty if late else root / folder, target_is_directory=True)
                    output = parent / 'new.json'

                    def retarget(*args, **kwargs):
                        parent.unlink()
                        parent.symlink_to(root / folder, target_is_directory=True)
                        return report

                    with patch.object(writer.producer, 'build', side_effect=retarget if late else AssertionError('calculation ran')):
                        self.refuse(root, '--new-report', output)
                    self.assertFalse((root / folder / 'new.json').exists())

    def test_entry_source_remains_protected_after_catalog_removal_and_retargeting(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = fixture(directory)
            external = root / 'external'
            external.mkdir()
            target = external / 'retained.txt'
            target.write_bytes((root / 'data/raw/ZL3b.txt').read_bytes())
            catalog_path = root / writer.CONTEXT[0]
            catalog = json.loads(catalog_path.read_text())
            extra = dict(catalog['sources'][0], id='synthetic-extra', path=str(target))
            catalog['sources'].append(extra)
            catalog_path.write_text(json.dumps(catalog))
            empty = root / 'empty'
            empty.mkdir()
            parent = root / 'output-parent'
            parent.symlink_to(empty, target_is_directory=True)
            original_build = writer.producer.build

            def changed(*args, **kwargs):
                report = original_build(*args, **kwargs)
                catalog['sources'].pop()
                catalog_path.write_text(json.dumps(catalog))
                target.unlink()
                parent.unlink()
                parent.symlink_to(external, target_is_directory=True)
                return report

            with patch.object(writer.producer, 'build', side_effect=changed):
                self.refuse(root, '--new-report', parent / target.name)
            self.assertFalse(target.exists())

    def test_current_catalog_additions_protect_new_external_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root, report = fixture(directory)
            output = root / 'new-external-source.txt'
            catalog_path = root / writer.CONTEXT[0]

            def changed(*args, **kwargs):
                catalog = json.loads(catalog_path.read_text())
                catalog['sources'].append({'path': str(output)})
                catalog_path.write_text(json.dumps(catalog))
                return report

            with patch.object(writer, 'rendered', side_effect=lambda value: (changed(), json.dumps(value).encode())[1]):
                self.refuse(root, '--new-report', output)
            self.assertFalse(output.exists())

    def test_actual_relocated_module_paths_are_protected_even_when_absent(self):
        for module in (writer, writer.producer, writer.audit, writer.ivtff, writer.strict_json):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as directory:
                root, _ = fixture(directory)
                relocated = root / 'relocated-module.py'
                with patch.object(module, '__file__', str(relocated)), \
                        patch.object(writer.producer, 'build', side_effect=AssertionError('calculation ran')):
                    self.refuse(root, '--new-report', relocated)
                self.assertFalse(relocated.exists())

    def test_exclusive_open_preserves_a_destination_created_after_final_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = fixture(directory)
            output = root / 'new.json'
            original_open = Path.open

            def appeared(path, mode='r', *args, **kwargs):
                if path == output and mode == 'xb':
                    output.write_bytes(b'created after the final guard\n')
                return original_open(path, mode, *args, **kwargs)

            with patch.object(Path, 'open', new=appeared):
                self.refuse(root, '--new-report', output)
            self.assertEqual(output.read_bytes(), b'created after the final guard\n')

    def test_cache_types_reject_legacy_equal_substitutions(self):
        changes = (
            ('schema_version', True), ('usable_as_verified_corpus_join', 0), ('locations', 7.0),
            ('identical_native_record_text', 1.0), ('different_native_record_text', 6.0),
        )
        with tempfile.TemporaryDirectory() as directory:
            root, report = fixture(directory)
            cache = root / 'cache.json'
            before = inventory(root)
            for key, value in changes:
                with self.subTest(key=key):
                    altered = dict(report, **{key: value})
                    self.assertEqual(altered, report)  # The legacy Python comparison accepts this.
                    cache.write_text(json.dumps(altered))
                    self.assertEqual(cli(root, '--check', cache, legacy=True).returncode, 0)
                    self.assertNotEqual(cli(root, '--check', cache).returncode, 0)
            altered = json.loads(json.dumps(report))
            altered['records'][0]['readings'][0]['source_file_line'] = float(altered['records'][0]['readings'][0]['source_file_line'])
            cache.write_text(json.dumps(altered))
            self.assertEqual(cli(root, '--check', cache, legacy=True).returncode, 0)
            self.assertNotEqual(cli(root, '--check', cache).returncode, 0)
            self.assertEqual(inventory(root), before)

    def test_complete_cache_comparison_rejects_missing_extra_changed_and_reordered_arrays(self):
        with tempfile.TemporaryDirectory() as directory:
            root, report = fixture(directory)
            for kind in ('missing', 'extra', 'changed', 'array-order'):
                with self.subTest(kind=kind):
                    altered = json.loads(json.dumps(report))
                    if kind == 'missing':
                        del altered['records'][0]['readings'][0]['native_text']
                    elif kind == 'extra':
                        altered['unexpected'] = False
                    elif kind == 'changed':
                        altered['records'][0]['readings'][0]['native_text'] = 'changed'
                    else:
                        altered['records'].reverse()
                    cache = root / 'cache.json'
                    cache.write_text(json.dumps(altered))
                    self.refuse(root, '--check', cache)
                    self.assertEqual(json.loads(cache.read_bytes()), altered)

    def test_duplicate_nested_members_and_nonfinite_numbers_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root, report = fixture(directory)
            original = json.dumps(report)
            invalid = [original.replace('"source_id": "ZL3b"', '"source_id": "ZL3b", "source_id": "ZL3b"', 1)]
            invalid += [original.replace('"locations": 7', f'"locations": {value}')
                        for value in ('NaN', 'Infinity', '-Infinity', '1e309')]
            for text in invalid:
                with self.subTest(text=text[:40]):
                    cache = root / 'cache.json'
                    cache.write_text(text)
                    self.refuse(root, '--check', cache)
                    self.assertEqual(cache.read_text(), text)

    def test_source_pin_drift_and_duplicate_catalog_keys_create_no_output(self):
        for defect in ('source', 'catalog'):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as directory:
                root, _ = fixture(directory)
                if defect == 'source':
                    (root / 'data/raw/ZL3b.txt').write_bytes(b'changed synthetic bytes')
                else:
                    catalog = root / writer.CONTEXT[0]
                    text = catalog.read_text()
                    catalog.write_text(text.replace('"path": "data/raw/ZL3b.txt"',
                                                    '"path": "data/raw/ZL3b.txt", "path": "data/raw/ZL3b.txt"', 1))
                output = root / 'new.json'
                process = cli(root, '--new-report', output)
                self.assertNotEqual(process.returncode, 0)
                self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
