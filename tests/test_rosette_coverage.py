import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_rosette_coverage as module
from scripts.audit_historical_interlinear import parse_historical
from scripts.ivtff import parse_ivtff


class RosetteCoverageTests(unittest.TestCase):
    def test_native_records_and_shared_unit_keys_are_distinct_counts(self):
        records, _ = parse_historical(
            b'<f85v2> {}\n## <f85v2.B1> {}\n'
            b'<f85v2.B1.1;U> a=\n<f85v2.B1.1;V> b=\n'
            b'## <f85v2.b1> {}\n<f85v2.b1.1a;U> c=\n')
        result = module.historical_page(records, 'f85v2')
        self.assertEqual(result['native_records'], 3)
        self.assertEqual(result['distinct_unit_line_keys'], 2)
        self.assertEqual(result['records_by_transcriber'], {'H': 0, 'U': 2, 'V': 1})
        pair = next(p for p in result['within_source_key_overlap'] if p['left_code'] == 'U')
        self.assertEqual(pair['shared_unit_line_keys'], 1)
        self.assertEqual(pair['left_only_unit_line_keys'], 1)
        self.assertEqual(result['ordered_record_refs'][-1],
                         {'locator': 'f85v2.b1.1a;U', 'physical_line': 6})
        for page in ('fRos', 'f86r4'):
            self.assertEqual(module.historical_page(records, page)['native_records'], 0)

    def test_header_absence_empty_header_and_nonexistent_locus_stay_distinct(self):
        doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n<fRos>\n'
                          '<fRos.1,@L0> a\n<fRos.2,!Cc> b\n<f85v2>\n')
        page = module.page_summary(doc, 'fRos')
        self.assertEqual(page['present_loci'], 1)
        self.assertEqual(page['present_loci_by_kind'], {'L0': 1})
        self.assertEqual(page['explicitly_nonexistent_locus_identifiers'], ['fRos.2,!Cc'])
        empty = module.page_summary(doc, 'f85v2')
        self.assertTrue(empty['header_present'])
        self.assertEqual(empty['present_loci'], 0)
        self.assertFalse(module.page_summary(doc, 'f86r4')['header_present'])

    def test_composite_context_cannot_be_changed_to_an_isolated_leaf(self):
        inventory = {'manifest_sha256': 'a', 'records': [{
            'target': '85v', 'canvas_uri': 'canvas:rosette',
            'yale_label': '85v and 86r (foldout)', 'image_id': '1006231'}]}
        row = {'canvas_uri': 'canvas:rosette', 'yale_label': '85v and 86r (foldout)',
               'image_oid': '1006231', 'explicit_folio_sides': '85v;86r',
               'has_multiple_explicit_sides': 'True', 'catalog_image_url': 'https://example.org/'}
        result = module.canvas_context(inventory, [row], {'manifest_sha256': 'a'})
        self.assertEqual(result['explicit_folio_sides'], ['85v', '86r'])
        for bad in ({**row, 'explicit_folio_sides': '85v'},
                    {**row, 'has_multiple_explicit_sides': 'False'},
                    {**row, 'canvas_uri': 'other-canvas'}):
            with self.assertRaises(ValueError):
                module.canvas_context(inventory, [bad], {'manifest_sha256': 'a'})
        with self.assertRaises(ValueError):
            module.canvas_context(inventory, [row], {'manifest_sha256': 'changed'})
        duplicate = copy.deepcopy(inventory)
        duplicate['records'] *= 2
        with self.assertRaises(ValueError):
            module.canvas_context(duplicate, [row], {'manifest_sha256': 'a'})

    def test_cli_rejects_receipt_drift_without_replacing_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            check, output = Path(folder) / 'check.json', Path(folder) / 'output.json'
            check.write_text('{}')
            output.write_text('preserve this')
            with patch.object(module, 'report', return_value={'schema_version': 1}), \
                    patch('sys.argv', ['audit', '--check', str(check), '--output', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                module.main()
            self.assertEqual(caught.exception.code, 1)
            self.assertEqual(output.read_text(), 'preserve this')

    def test_output_guards_preserve_catalog_archive_source_and_hardlink(self):
        root = module.ROOT
        source = root / 'data/raw/ZL3b-n.txt'
        paths = [root / 'data/transliterations.json',
                 root / 'data/historical/text16e6.zip', source,
                 root / 'scripts/audit_rosette_coverage.py']
        with tempfile.TemporaryDirectory() as folder:
            linked = Path(folder) / 'linked-source.json'
            linked.hardlink_to(source)
            paths.append(linked)
            for path in paths:
                before = path.read_bytes()
                with self.subTest(path=path.name), \
                        patch('sys.argv', ['audit', '--output', str(path)]), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                    module.main()
                self.assertEqual(caught.exception.code, 1)
                self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
