from dataclasses import replace
import copy
import json
from types import SimpleNamespace
import unittest

from scripts import build_f68r3_review as packet
from scripts.ivtff import Locus
from scripts import verify_f68r3_review as review


def fixture():
    loci = tuple(Locus(packet.PAGE, number, packet.LOCATORS[number], packet.KINDS[number],
                       None, 'synthetic,uncertain.[a:o].text', number + 100, {}) for number in range(1, 23))
    return [({'id': identity, 'sha256': '0' * 64, 'alphabet': identity, 'url': 'https://example.org/synthetic',
              'path': 'synthetic'}, SimpleNamespace(pages={packet.PAGE: {}}, loci=loci)) for identity in ('ZL3b', 'IT2a')]


class F68r3PacketTests(unittest.TestCase):
    def test_all_nonparagraph_records_and_empty_p0_scope_are_preserved(self):
        result = packet.collect(fixture())
        self.assertEqual(result['locations'], 22)
        self.assertEqual([r['locus_key'] for r in result['records'] if r['selected_anchor_attempt']], packet.ANCHORS)
        for page in result['page_audit']:
            self.assertEqual(page['present_p0_locations'], [])
            self.assertEqual(page['present_by_kind'], {'Cc': 2, 'La': 1, 'Ls': 11, 'Ri': 8})
        self.assertTrue(all(r['image_glyph_verification'] == 'pending' for r in result['records']))

    def test_missing_extra_duplicate_reordered_or_nonexistent_records_fail(self):
        original = fixture()[0][1].loci
        for changed in (original[:-1], original + (original[-1],), tuple(reversed(original)),
                        (replace(original[0], locator='!'),) + original[1:]):
            sources = fixture(); sources[0][1].loci = changed
            with self.assertRaises(ValueError):
                packet.collect(sources)

    def test_page_header_editions_kind_and_locator_requirements_are_explicit(self):
        with self.assertRaises(ValueError):
            packet.collect(fixture()[:1])
        with self.assertRaises(ValueError):
            packet.collect(fixture() + fixture()[:1])
        sources = fixture(); sources[0][1].pages = {}
        with self.assertRaises(ValueError):
            packet.collect(sources)
        for kwargs in ({'kind': 'P0'}, {'locator': '+'}):
            sources = fixture()
            sources[0][1].loci = (replace(sources[0][1].loci[0], **kwargs),) + sources[0][1].loci[1:]
            with self.assertRaises(ValueError):
                packet.collect(sources)

    def test_native_annotations_and_edition_disagreement_are_retained(self):
        sources = fixture()
        raw = '<!09:30>extended{ct}.unknown?.uncertain,[a:o]'
        sources[0][1].loci = (replace(sources[0][1].loci[0], text=raw),) + sources[0][1].loci[1:]
        result = packet.collect(sources)
        self.assertEqual(result['records'][0]['readings'][0]['native_text'], raw)
        self.assertFalse(result['records'][0]['native_record_text_identical'])
        self.assertEqual(result['different_native_record_text'], 1)

    def review_fixture(self):
        return (json.loads(review.REVIEW.read_bytes()), json.loads(review.PACKET.read_bytes()),
                json.loads(review.PARENT.read_bytes()))

    def test_real_metadata_keeps_both_attempts_and_all_other_records_pending(self):
        record, native, parent = self.review_fixture()
        review.validate_metadata(record, native, parent)
        self.assertFalse(record['usable_as_verified_corpus_join'])
        self.assertEqual(len(record['unreviewed_locus_keys']), 20)

    def test_dropped_attempts_records_source_identity_and_promotion_fail(self):
        original, native, parent = self.review_fixture()
        changes = []
        changed = copy.deepcopy(original); changed['attempts'].pop(); changes.append(changed)
        changed = copy.deepcopy(original); changed['unreviewed_locus_keys'].pop(); changes.append(changed)
        changed = copy.deepcopy(original); changed['usable_as_verified_corpus_join'] = True; changes.append(changed)
        changed = copy.deepcopy(original); changed['attempts'][1]['source_native_text_identical'] = False; changes.append(changed)
        changed = copy.deepcopy(original); changed['attempts'][0]['glyph_alignment_status'] = 'verified'; changes.append(changed)
        for changed in changes:
            with self.assertRaises(ValueError):
                review.validate_metadata(changed, native, parent)

    def test_changed_request_geometry_dimensions_urls_and_asset_coverage_fail(self):
        original, native, parent = self.review_fixture()
        changes = []
        changed = copy.deepcopy(original); changed['assets'].pop(); changes.append(changed)
        changed = copy.deepcopy(original); changed['assets'][3]['native_region'][0] = 7993; changes.append(changed)
        changed = copy.deepcopy(original); changed['assets'][4]['pixel_dimensions'][0] += 1; changes.append(changed)
        changed = copy.deepcopy(original); changed['assets'][5]['url'] = 'https://example.org/substituted'; changes.append(changed)
        for changed in changes:
            with self.assertRaises(ValueError):
                review.validate_metadata(changed, native, parent)

    def test_png_header_dimensions_and_malformed_render_headers(self):
        header = b'\x89PNG\r\n\x1a\n' + (13).to_bytes(4, 'big') + b'IHDR'
        good = header + (1237).to_bytes(4, 'big') + (1600).to_bytes(4, 'big') + b'\x00' * 9
        self.assertEqual(review.recorded_dimensions(good), (1237, 1600))
        for bad in (header, good[:16] + b'\x00' * 4 + good[20:]):
            with self.assertRaises(ValueError):
                review.recorded_dimensions(bad)


if __name__ == '__main__':
    unittest.main()
