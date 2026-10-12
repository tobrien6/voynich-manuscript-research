import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_reddy_sources import annotated, compare_pages, population, read_selected, subset_check
from scripts.audit_reddy_sources import MANIFEST, ROOT
from scripts.audit_reddy_sources import write_new


class ReddyIntakeTests(unittest.TestCase):
    def test_headers_and_symbols_remain_literal_and_blanks_are_accounted(self):
        rows, pages, blanks = annotated(b'<f1r P1 1 H> A* B\n\n<f1r P1 2 H> A A\n<f2v P 1 C> 9\n')
        self.assertEqual(blanks, 1)
        self.assertEqual(rows[0]['header'], ('f1r', 'P1', '1', 'H'))
        self.assertEqual(rows[1]['native_file_line'], 3)
        self.assertEqual(pages[0]['tokens'], ['A*', 'B', 'A', 'A'])
        stats = population(pages[0]['tokens'])
        self.assertEqual((stats['token_occurrences'], stats['token_types']), (4, 3))
        self.assertEqual(stats['notation_character_types'], 3)

    def test_malformed_duplicate_and_returning_page_records_fail(self):
        examples = [b'not a header A B\n', b'<f1r P 1> A\n', b'<f1r P 1 H> \n',
                    b'<f1r P 1 H> A\n<f1r P 1 H> B\n',
                    b'<f1r P 1 H> A\n<f2r P 1 H> B\n<f1r P 2 H> C\n', b'\n']
        for raw in examples:
            with self.assertRaises(ValueError):
                annotated(raw)

    def test_page_comparison_retains_missing_extra_and_blank_lines(self):
        _, pages, _ = annotated(b'<f1r P 1 H> A B\n<f2r P 1 H> 9\n')
        self.assertTrue(compare_pages(pages, b'A  B\n9\n')['all_pages_match'])
        for raw in [b'B A\n9\n', b'A B\n', b'A B\n\n9\n']:
            self.assertFalse(compare_pages(pages, raw)['all_pages_match'])
        result = compare_pages(pages, b'A B\n\n9\n')
        self.assertEqual(result['paged_blank_lines'], 1)
        self.assertEqual(len(result['page_comparisons']), 3)

    def test_subset_membership_preserves_header_tokens_and_order(self):
        full = annotated(b'<f1r P 1 H> A B\n<f2r P 1 H> C\n')
        b = annotated(b'<f2r P 1 H> C\n')
        self.assertTrue(subset_check(*full[:2], *b[:2])['all_records_and_pages_match'])
        changed = annotated(b'<f2r P 1 H> D\n')
        self.assertFalse(subset_check(*full[:2], *changed[:2])['all_records_and_pages_match'])
        missing = annotated(b'<f3r P 1 H> C\n')
        self.assertEqual(subset_check(*full[:2], *missing[:2])['records_missing_from_full'], [['f3r', 'P', '1', 'H']])
        reversed_rows = list(reversed(full[0]))
        self.assertFalse(subset_check(*full[:2], reversed_rows, list(reversed(full[1])))['record_order_preserved'])

    def test_source_snapshot_pin_or_local_byte_drift_fails_before_parsing(self):
        manifest = json.loads((ROOT / MANIFEST).read_bytes())
        changed = copy.deepcopy(manifest); changed['source_commit'] = '0' * 40
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaisesRegex(ValueError, 'snapshot differs'):
                read_selected(root, changed)
            path = root / 'README.md'; path.write_bytes(b'synthetic changed bytes')
            with self.assertRaisesRegex(ValueError, 'identity differs'):
                read_selected(root, manifest)

    def test_output_is_exclusive_and_preserves_existing_file_and_aliases(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'source'; source.write_bytes(b'synthetic')
            symbolic = root / 'symbolic'; symbolic.symlink_to(source)
            hard = root / 'hard'; hard.hardlink_to(source)
            for path in [source, symbolic, hard]:
                with self.assertRaises(FileExistsError):
                    write_new(path, b'changed')
                self.assertEqual(source.read_bytes(), b'synthetic')
            result = root / 'new.json'; write_new(result, b'{}\n')
            self.assertEqual(result.read_bytes(), b'{}\n')


if __name__ == '__main__':
    unittest.main()
