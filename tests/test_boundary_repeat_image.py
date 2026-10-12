from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.audit_transliterations import ROOT
from scripts.paragraph_token_corpus import strict_json
from scripts.verify_boundary_repeat_image import jpeg_dimensions, source_facts, verify_record


class BoundaryRepeatImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = strict_json((ROOT / 'research/transliteration/boundary_repeat_image_check.json').read_bytes())
        cls.facts = source_facts()

    def checked(self, record):
        with patch('scripts.verify_boundary_repeat_image.source_facts', return_value=self.facts):
            return verify_record(record)

    def test_complete_source_replay_retains_actual_endpoints_and_drawing_context(self):
        self.assertEqual(verify_record(self.record), self.facts)
        self.assertEqual(self.facts['member_keys'], ['f82r.' + str(n) for n in range(1, 10)])
        self.assertTrue(all(v['left_endpoint'] == v['right_endpoint'] == 'qokaiin'
                            for v in self.facts['endpoint_variants']))
        self.assertTrue(all(row['drawing_interruption_count'] == 1 for v in self.facts['endpoint_variants']
                            for row in v['selected_row_metadata']))

    def test_native_endpoint_row_type_raw_text_and_missing_variant_tampering_rejected(self):
        for mode in ('endpoint', 'row_type', 'raw_text', 'missing_variant'):
            record = deepcopy(self.record)
            if mode == 'endpoint': record['endpoint_variants'][0]['left_endpoint'] = 'Changed'
            elif mode == 'row_type': record['endpoint_variants'][0]['selected_row_metadata'][0]['drawing_interruption_count'] = True
            elif mode == 'raw_text': record['selected_native_source_text'][0]['text'] += '.changed'
            else: record['endpoint_variants'].pop()
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'native endpoints'):
                self.checked(record)

    def test_image_source_pin_and_required_original_byte_pin_tampering_rejected(self):
        record = deepcopy(self.record)
        record['inputs_sha256']['data/transliterations.json'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'input fingerprints'): self.checked(record)
        record = deepcopy(self.record)
        record['retrieval']['file_sha256'].pop('f82r.jpg')
        with self.assertRaisesRegex(ValueError, 'primary retrieval'): self.checked(record)
        record = deepcopy(self.record)
        record['image_index_record']['image_oid'] = '1006223'
        with self.assertRaisesRegex(ValueError, 'image identity'): self.checked(record)
        record = deepcopy(self.record)
        record['plan_history']['original_before_image_inspection_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'plan provenance'): self.checked(record)

    def test_region_url_bounds_dimensions_and_boolean_coordinates_rejected(self):
        for mode in ('url', 'bounds', 'dimensions', 'coordinate_type'):
            record = deepcopy(self.record)
            region = record['inspected_regions'][0]
            if mode == 'url': region['url'] += '?changed'
            elif mode == 'bounds': region['region_xywh'][0] = 3000
            elif mode == 'dimensions': region['decoded_dimensions'][0] += 1
            else: region['region_xywh'][0] = True
            with self.subTest(mode=mode), self.assertRaises(ValueError): self.checked(record)

    def test_unblinded_local_plan_and_unresolved_glyph_declarations_are_required(self):
        for key, value in (('plan_remotely_published_before_inspection', True),
                           ('independent_blind_or_human_review', True),
                           ('image_inspected_in_this_chat', 1)):
            record = deepcopy(self.record)
            record['exposure'][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'exposure'):
                self.checked(record)
        record = deepcopy(self.record)
        record['observations']['glyph_equivalence_disposition'] = 'confirmed'
        with self.assertRaisesRegex(ValueError, 'uncertainty'): self.checked(record)

    def test_jpeg_dimension_reader_has_no_pixel_edit_and_rejects_bad_inputs(self):
        raw = b'\xff\xd8\xff\xc0\x00\x0b\x08\x00\x96\x01\x68\x01\x01\x11\x00'
        self.assertEqual(jpeg_dimensions(raw), [360, 150])
        for bad in (b'', b'not JPEG', b'\xff\xd8\xff', raw[:9]):
            with self.subTest(raw=bad), self.assertRaises(ValueError): jpeg_dimensions(bad)


if __name__ == '__main__':
    unittest.main()
