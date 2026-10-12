from dataclasses import replace
from types import SimpleNamespace
import unittest

from scripts import build_f68r3_review as packet
from scripts.ivtff import Locus


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


if __name__ == '__main__':
    unittest.main()
