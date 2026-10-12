import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import verify_grouped_predictor_controls as verifier


SOURCE = b'''import math
STRENGTH = 10
def fit(rows):
    return rows
def main():
    print("old CLI")
if __name__ == "__main__":
    main()
'''

GUARD = b'''def protect_output(destination, protected):
    """Reject resolved paths and existing inode aliases of protected inputs."""
    output = destination.resolve()
    if output in protected or (output.exists() and any(
            output.samefile(source) for source in protected if source.exists())):
        raise ValueError("output must not overwrite a pinned input or plan")
'''


class GroupedControlVerifierTests(unittest.TestCase):
    def test_cli_body_revision_is_allowed_but_every_scientific_statement_is_compared(self):
        revised = SOURCE.replace(b'print("old CLI")', b'raise ValueError("new guard")')
        self.assertEqual(verifier.scientific_ast(SOURCE), verifier.scientific_ast(revised))
        for revised in (SOURCE.replace(b'STRENGTH = 10', b'STRENGTH = 11'),
                        SOURCE.replace(b'return rows', b'return rows[::-1]'),
                        SOURCE.replace(b'import math', b'import random'),
                        SOURCE.replace(b'def main():', b'def main(output):'),
                        SOURCE.replace(b'def main():', b'@fit\ndef main():'),
                        SOURCE + b'print("new global effect")\n'):
            self.assertNotEqual(verifier.scientific_ast(SOURCE), verifier.scientific_ast(revised))
        for invalid in (SOURCE + b'def main(): pass\n', SOURCE.replace(b'main', b'cli')):
            with self.assertRaises(ValueError):
                verifier.scientific_ast(invalid)

    def test_whitespace_and_comments_do_not_change_scientific_ast(self):
        self.assertEqual(verifier.scientific_ast(SOURCE), verifier.scientific_ast(b'# comment\n' + SOURCE))

    def test_only_the_exact_reviewed_writer_helper_may_be_added(self):
        self.assertEqual(verifier.scientific_ast(SOURCE), verifier.scientific_ast(GUARD + SOURCE))
        for invalid in (GUARD.replace(b'output.samefile(source)', b'False') + SOURCE,
                        b'@fit\n' + GUARD + SOURCE, GUARD + GUARD + SOURCE):
            with self.assertRaises(ValueError):
                verifier.scientific_ast(invalid)
        # Calling that helper from a scientific function still changes its AST.
        altered = GUARD + SOURCE.replace(b'return rows', b'protect_output(rows, set())\n    return rows')
        self.assertNotEqual(verifier.scientific_ast(SOURCE), verifier.scientific_ast(altered))

    def test_exact_frozen_source_snapshots_match_the_original_report(self):
        frozen = verifier.frozen_file(verifier.ENGINE)
        inputs, hashes = verifier.verified_inputs()
        self.assertEqual(verifier.sha(frozen), inputs['input_pins'][verifier.ENGINE])
        self.assertEqual(set(hashes), set(inputs['input_pins']))
        self.assertEqual(verifier.frozen_file(verifier.PROGRAM), (verifier.ROOT / verifier.PROGRAM).read_bytes())

    def test_changed_frozen_record_fails_before_producer_is_loaded(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = root / verifier.RESULT
            result.parent.mkdir(parents=True)
            result.write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError, 'frozen synthetic result bytes changed'):
                verifier.verified_inputs(root)

    def test_missing_frozen_source_is_not_replaced_by_current_code(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'frozen source snapshot is unavailable'):
                verifier.frozen_file(verifier.ENGINE, Path(folder))

    def test_inert_snapshots_are_preserved_and_need_no_git_history(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = root / verifier.RESULT
            result.parent.mkdir(parents=True)
            result.write_bytes((verifier.ROOT / verifier.RESULT).read_bytes())
            for name, relative in verifier.SNAPSHOTS.items():
                snapshot = root / relative
                snapshot.parent.mkdir(parents=True, exist_ok=True)
                snapshot.write_bytes(verifier.frozen_file(name))
                self.assertEqual(verifier.frozen_file(name, root), verifier.frozen_file(name))
                alias = root / (snapshot.name + '.alias')
                alias.hardlink_to(snapshot)
                with self.assertRaises(ValueError):
                    verifier.protect_output(alias, root)

    def test_receipt_output_cannot_alias_frozen_result_or_producer(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = root / verifier.RESULT
            result.parent.mkdir(parents=True)
            result.write_bytes((verifier.ROOT / verifier.RESULT).read_bytes())
            producer = root / verifier.ENGINE
            producer.parent.mkdir(parents=True)
            producer.write_bytes(b'synthetic producer')
            for source in (result, producer):
                alias = root / ('alias-' + source.name)
                alias.hardlink_to(source)
                with self.assertRaisesRegex(ValueError, 'must not overwrite'):
                    verifier.protect_output(alias, root)
                with self.assertRaises(ValueError):
                    verifier.protect_output(source, root)
            verifier.protect_output(root / 'new-receipt.json', root)

    def test_optional_catalog_sources_are_protected_through_hardlink_aliases(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = root / verifier.RESULT
            result.parent.mkdir(parents=True)
            result.write_bytes((verifier.ROOT / verifier.RESULT).read_bytes())
            source = root / 'native.txt'
            source.write_text('synthetic source')
            catalog = root / 'data/transliterations.json'
            catalog.parent.mkdir()
            catalog.write_text(json.dumps({'sources': [{'path': 'native.txt'}]}))
            for original in (source, catalog):
                alias = root / (original.name + '.alias')
                alias.hardlink_to(original)
                with self.assertRaises(ValueError):
                    verifier.protect_output(alias, root)

    def test_alias_created_during_verification_is_rejected_before_final_write(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = root / verifier.RESULT
            result.parent.mkdir(parents=True)
            result.write_text(json.dumps({'input_pins': {'native.txt': 'synthetic'}}))
            source = root / 'native.txt'
            source.write_text('synthetic input to preserve')
            output = root / 'receipt.json'
            def verify_then_alias(*args):
                output.hardlink_to(source)
                return {'synthetic': True}
            with patch.object(verifier, 'ROOT', root), patch.object(verifier, 'verify', side_effect=verify_then_alias):
                with patch('sys.argv', ['verify', '--output', str(output)]):
                    with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                        verifier.main()
            self.assertEqual(error.exception.code, 1)
            self.assertEqual(source.read_text(), 'synthetic input to preserve')


if __name__ == '__main__':
    unittest.main()
