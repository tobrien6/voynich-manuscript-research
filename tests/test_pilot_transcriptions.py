import copy
import unittest

from scripts.ivtff import parse_ivtff
from scripts.audit_pilot_transcriptions import build_report


def source(ident, text):
    return ({'id': ident, 'sha256': 'synthetic', 'url': 'https://example.org/' + ident},
            parse_ivtff('#=IVTFF Eva- 2.0 M\n' + text))


def fixture(target='1r', sides='1r', combined='False'):
    inventory = {'records': [{
        'target': target, 'canvas_uri': 'canvas:1', 'yale_label': sides,
        'image_id': '1', 'catalog_section': {'part': 'synthetic'},
        'inspection_status': 'synthetic', 'inspected_on': '2026-10-11',
    }]}
    canvases = [{'canvas_uri': 'canvas:1', 'yale_label': sides,
                 'image_oid': '1', 'catalog_image_url': 'https://example.org/1',
                 'explicit_folio_sides': sides, 'has_multiple_explicit_sides': combined}]
    return inventory, canvases


class PilotTranscriptionTests(unittest.TestCase):
    def test_exact_link_retains_all_kinds_absent_loci_and_source_disagreements(self):
        sources = [source('ZL3b', '<f1r>\n<f1r.1,@P0> a\n<f1r.2,@L0> b\n<f1r.3,!P0> c\n'),
                   source('IT2a', '<f1r>\n<f1r.1,+P0> a\n')]
        report = build_report(*fixture(), sources)
        entry = report['entries'][0]
        self.assertEqual(entry['status'], 'exact_page_metadata_link')
        self.assertEqual(report['summary']['shared_present_loci_in_exact_links'], 1)
        self.assertEqual(entry['editions'][0]['exact_page']['present_loci_by_kind'],
                         {'L0': 1, 'P0': 1})
        self.assertEqual(entry['editions'][0]['exact_page']['explicitly_nonexistent_locus_identifiers'],
                         ['f1r.3,!P0'])
        self.assertEqual(entry['exact_page_comparison']['present_only_in_ZL3b'], ['f1r.2'])
        self.assertEqual(len(entry['exact_page_comparison']['shared_with_different_kind_or_locator']), 1)

    def test_panel_candidates_are_never_promoted_or_prefix_matched_to_other_sides(self):
        text = '<f67r1>\n<f67r1.1,@P0> a\n<f67r2>\n<f67r2.1,@P0> b\n<f67v1>\n<f67v1.1,@P0> c\n'
        report = build_report(*fixture('67r', '67r'), [source('ZL3b', text), source('IT2a', text)])
        entry = report['entries'][0]
        self.assertEqual(entry['status'], 'blocked')
        self.assertEqual(report['summary']['shared_present_loci_in_exact_links'], 0)
        self.assertEqual([p['page_id'] for p in entry['editions'][0]['unmapped_panel_identifier_candidates']],
                         ['f67r1', 'f67r2'])
        self.assertFalse(entry['editions'][0]['exact_page']['header_present'])

    def test_combined_canvas_blocks_even_with_exact_page_and_special_header(self):
        text = '<f85v>\n<f85v.1,@P0> a\n<fRos>\n<fRos.1,@L0> b\n'
        report = build_report(*fixture('85v', '85v;86r', 'True'),
                              [source('ZL3b', text), source('IT2a', text)])
        self.assertEqual(report['entries'][0]['status'], 'blocked')
        self.assertEqual(report['entries'][0]['selected_canvas']['explicit_label_sides'], ['85v', '86r'])
        self.assertIn('shared_canvas_requires_documented_region_mapping', report['entries'][0]['blockers'])
        self.assertEqual(report['special_page_headers_without_assigned_pilot_mapping'][0]['page']['page_id'],
                         'fRos')

    def test_empty_page_header_is_not_an_available_text_page(self):
        report = build_report(*fixture(), [source('ZL3b', '<f1r>\n'), source('IT2a', '<f1r>\n')])
        self.assertEqual(report['entries'][0]['status'], 'blocked')

    def test_rejects_duplicate_targets_and_inconsistent_canvas_metadata(self):
        sources = [source('ZL3b', '<f1r>\n'), source('IT2a', '<f1r>\n')]
        inventory, canvases = fixture()
        inventory['records'].append(copy.deepcopy(inventory['records'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate pilot target'):
            build_report(inventory, canvases, sources)
        inventory, canvases = fixture()
        canvases[0]['image_oid'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'image ID mismatch'):
            build_report(inventory, canvases, sources)
        inventory, canvases = fixture()
        canvases[0]['explicit_folio_sides'] = '2r'
        with self.assertRaisesRegex(ValueError, 'target absent'):
            build_report(inventory, canvases, sources)


if __name__ == '__main__':
    unittest.main()
