from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.verify_initial_prefix_review import (
    REVIEW, SELECTION, bitmap_dimensions, check_local_images,
    reference_sources, verify_review,
)


class InitialPrefixReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selection_bytes = SELECTION.read_bytes()
        cls.selection = json.loads(cls.selection_bytes)
        cls.review = json.loads(REVIEW.read_text())
        cls.references = reference_sources()

    def check(self, review, selection_bytes=None):
        with patch('scripts.verify_initial_prefix_review.selection_report', return_value=self.selection), \
                patch('scripts.verify_initial_prefix_review.reference_sources', return_value=self.references):
            verify_review(review, self.selection,
                          self.selection_bytes if selection_bytes is None else selection_bytes)

    def test_pinned_record_reproduces_reference_choice_and_retains_later_ambiguity(self):
        verify_review(self.review, self.selection, self.selection_bytes)
        candidates, references = self.references
        self.assertEqual([ref['locus_key'] for ref in references], ['f78r.43', 'f78r.4'])
        self.assertEqual(len(candidates['l']), 1)
        self.assertEqual(len(candidates['q']), 11)
        zl = references[0]['sources'][0]
        self.assertIn('[a:o]', zl['original_locus_text'])
        self.assertFalse(zl['whole_locus_adapter_eligible'])
        self.assertEqual(zl['first_token'], 'lchedy')

    def test_corrections_and_verified_alignment_claims_are_rejected(self):
        for change in ('correction', 'case_alignment', 'reference_alignment'):
            altered = deepcopy(self.review)
            if change == 'correction':
                altered['may_apply_as_source_correction'] = True
            elif change == 'case_alignment':
                altered['cases'][0]['row_alignment_status'] = 'verified'
            else:
                altered['same_page_comparison']['references'][0]['row_alignment_status'] = 'verified'
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.check(altered)

    def test_missing_duplicate_or_rebound_selected_cases_fail(self):
        for change in ('missing', 'duplicate', 'metadata', 'byte_binding'):
            altered = deepcopy(self.review)
            if change == 'missing':
                altered['cases'].pop()
            elif change == 'duplicate':
                altered['cases'].append(deepcopy(altered['cases'][0]))
            elif change == 'metadata':
                altered['cases'][0]['selection_case']['variants'][0]['first_token'] = 'wrong'
            else:
                altered['selection_report_sha256'] = '0' * 64
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.check(altered)

    def test_reference_substitution_or_erasing_later_uncertainty_fails(self):
        for change in ('candidate', 'source_text', 'eligibility', 'line_number'):
            altered = deepcopy(self.review)
            comparison = altered['same_page_comparison']
            if change == 'candidate':
                comparison['candidate_locus_keys_by_literal_prefix']['q'].reverse()
            elif change == 'source_text':
                comparison['references'][0]['sources'][0]['original_locus_text'] = 'lchedy.a'
            elif change == 'eligibility':
                comparison['references'][0]['sources'][0]['whole_locus_adapter_eligible'] = True
            else:
                comparison['references'][0]['sources'][0]['source_line_number'] += 1
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.check(altered)

    def test_wrong_region_service_dimensions_or_bounds_fail(self):
        for change in ('service', 'dimensions', 'bounds'):
            altered = deepcopy(self.review)
            image = altered['same_page_comparison']['references'][0]['inspected_images'][0]
            if change == 'service':
                image['url'] = image['url'].replace('/1006214/', '/1006109/')
            elif change == 'dimensions':
                image['pixel_width'] += 1
            else:
                image['region_xywh_full_image_pixels'][0] = 10000
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.check(altered)

    def test_unresolved_status_cannot_retain_a_preferred_representation(self):
        altered = deepcopy(self.review)
        altered['cases'][1]['interpretation_status'] = 'unresolved'
        with self.assertRaises(ValueError):
            self.check(altered)

    def test_bitmap_header_sizes_and_truncation(self):
        gif = b'GIF89a\x80\x02\x08\x04'
        self.assertEqual(bitmap_dimensions(gif), (640, 1032))
        jpeg = b'\xff\xd8\xff\xc0\x00\x0b\x08\x00\x03\x00\x05\x01\x01\x11\x00'
        self.assertEqual(bitmap_dimensions(jpeg), (5, 3))
        for bad in (b'not a bitmap', b'\xff\xd8\xff', jpeg[:-1]):
            with self.subTest(data=bad), self.assertRaises(ValueError):
                bitmap_dimensions(bad)

    def test_optional_local_bindings_check_bytes_sizes_and_identity(self):
        altered = deepcopy(self.review)
        data = b'GIF89a\x80\x02\x08\x04'
        altered['notation_reference']['sha256'] = hashlib.sha256(data).hexdigest()
        url = altered['notation_reference']['url']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'reference.gif'
            path.write_bytes(data)
            binding = url + '=' + str(path)
            self.assertEqual(check_local_images(altered, [binding]), 1)
            with self.assertRaises(ValueError):
                check_local_images(altered, [binding, binding])
            with self.assertRaises(ValueError):
                check_local_images(altered, ['https://example.test/unrecorded=' + str(path)])
            altered['notation_reference']['pixel_width'] += 1
            with self.assertRaises(ValueError):
                check_local_images(altered, [binding])
            altered['notation_reference']['pixel_width'] -= 1
            path.write_bytes(data + b'changed')
            with self.assertRaises(ValueError):
                check_local_images(altered, [binding])


if __name__ == '__main__':
    unittest.main()
