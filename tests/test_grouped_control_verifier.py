from pathlib import Path
import tempfile
import unittest

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

    def test_exact_frozen_producer_and_benchmark_commit_are_available(self):
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

    def test_missing_freeze_commit_is_not_replaced_by_current_code(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'pre-benchmark Git commit is unavailable'):
                verifier.frozen_file(verifier.ENGINE, Path(folder))

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


if __name__ == '__main__':
    unittest.main()
