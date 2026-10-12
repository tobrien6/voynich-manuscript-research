from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.audit_terminal_folios import ROOT, SOURCE_IDS, audit, build_report, source_page, verify_observations
from scripts.ivtff import parse_ivtff


HEADER = '#=IVTFF Eva- 2.0 M\n'


def documents():
    document = parse_ivtff(HEADER + '<f116r>\n<f116r.1,@P0> q.a\n'
                           '<f116v>\n<f116v.1,@Lx> oror.sheey<!comment>\n')
    return [({'id': identifier, 'sha256': 'synthetic', 'url': 'https://example.test/source',
              'path': 'synthetic.txt', 'alphabet': 'Eva-'}, document)
            for identifier in SOURCE_IDS]


def canvas(label, index):
    numbered = label in {'116r', '116v'}
    return {'yale_label': label, 'label_class': 'exact_single_side_label' if numbered else 'non_numbered_view',
            'has_partial_marker': 'False', 'has_multiple_explicit_sides': 'False',
            'explicit_folio_sides': label if numbered else '',
            'canvas_uri': 'https://example.test/canvas/' + str(index),
            'image_oid': str(index), 'catalog_image_url': 'https://example.test/catalog/' + str(index),
            'full_image_url': 'https://example.test/image/' + str(index),
            'image_service_url': 'https://example.test/service/' + str(index),
            'image_width': '1000', 'image_height': '2000'}


def canvases():
    return [canvas(label, index) for index, label in enumerate(
        ('116r', '116v', '[Back flyleaf recto]'))]


ALIAS = {'source_scheme': 'yale_legacy_ms408_catalog', 'source_label': '117v',
         'status': 'unresolved', 'mapping_allowed': False, 'target': None}


class TerminalFolioTests(unittest.TestCase):
    def test_missing_header_empty_header_and_present_locus_are_distinct(self):
        missing = parse_ivtff(HEADER + '<f116r>\n')
        empty = parse_ivtff(HEADER + '<f116v>\n')
        present = documents()[0][1]
        self.assertEqual(source_page(missing, 'f116v')['presence_state'], 'header_absent')
        self.assertEqual(source_page(empty, 'f116v')['presence_state'], 'header_without_present_loci')
        self.assertEqual(source_page(present, 'f116v')['presence_state'], 'present_loci')

    def test_nonexistent_locus_is_preserved_without_becoming_present_text(self):
        doc = parse_ivtff(HEADER + '<f116v>\n<f116v.1,!Lx> oror.sheey\n')
        result = source_page(doc, 'f116v')
        self.assertEqual(result['presence_state'], 'header_without_present_loci')
        self.assertEqual(result['explicitly_nonexistent_locus_identifiers'], ['f116v.1,!Lx'])
        self.assertEqual(result['native_payload_records'], [])

    def test_lx_payload_stays_apart_from_paragraphs_and_free_comments(self):
        result = source_page(documents()[0][1], 'f116v')
        self.assertEqual(result['present_generic_p_loci'], 0)
        self.assertEqual(result['present_p0_p1_loci'], 0)
        self.assertEqual(result['present_loci_by_kind'], {'Lx': 1})
        record = result['native_payload_records'][0]
        self.assertEqual(record['native_payload_outside_free_comments'], 'oror.sheey')
        self.assertTrue(record['free_comments_present'])

    def test_flyleaf_never_acquires_a_native_page_or_edition(self):
        report = build_report(documents(), canvases(), ALIAS)
        flyleaf = report['entries'][2]
        self.assertIsNone(flyleaf['source_page_id'])
        self.assertEqual(flyleaf['editions'], [])
        self.assertTrue(flyleaf['unnumbered_flyleaf_has_no_assigned_native_page'])

    def test_changed_removed_or_verified_alias_requires_new_review(self):
        for update in ({'mapping_allowed': True}, {'target': {}}, {'status': 'unregistered'},
                       {'status': 'verified'}, {'source_label': 'f117v'}):
            alias = {**ALIAS, **update}
            with self.subTest(update=update), self.assertRaises(ValueError):
                build_report(documents(), canvases(), alias)

    def test_missing_duplicate_partial_or_compound_terminal_image_fails(self):
        for mode in ('missing', 'duplicate', 'partial', 'combined', 'numbered_flyleaf'):
            rows = canvases()
            if mode == 'missing':
                rows.pop()
            elif mode == 'duplicate':
                rows.append(deepcopy(rows[0]))
            elif mode == 'partial':
                rows[0]['has_partial_marker'] = 'True'
            elif mode == 'combined':
                rows[1]['has_multiple_explicit_sides'] = 'True'
            else:
                rows[2]['explicit_folio_sides'] = '117r'
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                build_report(documents(), rows, ALIAS)

    def test_missing_or_duplicate_source_file_cannot_inflate_the_five_edition_audit(self):
        for sources in (documents()[:-1], documents() + documents()[:1]):
            with self.assertRaises(ValueError):
                build_report(sources, canvases(), ALIAS)

    def test_pinned_intake_preserves_terminal_asymmetry_and_absent_control(self):
        result = audit()
        recto, verso, flyleaf = result['entries']
        self.assertEqual([entry['present_loci'] for entry in recto['editions']], [50] * 5)
        self.assertEqual([entry['header_present'] for entry in verso['editions']],
                         [True, False, False, True, True])
        self.assertEqual([entry['present_loci_by_kind'] for entry in verso['editions']],
                         [{'Lx': 1}, {}, {}, {'Lx': 1}, {'Lx': 1}])
        self.assertFalse(result['legacy_117v_lookup']['mapping_allowed'])
        self.assertTrue(all(not entry['header_present'] for entry in result['f117v_source_controls']))

    def test_observation_binding_and_region_metadata_do_not_authorize_an_alias(self):
        report_path = ROOT / 'research/source-audit/terminal-folio-intake.json'
        raw = report_path.read_bytes()
        report = json.loads(raw)
        observations = json.loads((ROOT / 'research/source-audit/terminal-folio-observations.json').read_text())
        verify_observations(observations, report, raw)
        for change in ('alias', 'new_reading', 'missing', 'page', 'binding', 'region'):
            altered = deepcopy(observations)
            if change == 'alias':
                altered['historical_alias_verified'] = True
            elif change == 'new_reading':
                altered['new_voynich_glyph_reading_or_translation'] = True
            elif change == 'missing':
                altered['records'].pop()
            elif change == 'page':
                altered['records'][2]['source_page_id'] = 'f117r'
            elif change == 'binding':
                altered['intake_report_sha256'] = '0' * 64
            else:
                altered['records'][1]['inspected_images'][1]['url'] = 'https://example.test/wrong-region'
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_observations(altered, report, raw)


if __name__ == '__main__':
    unittest.main()
