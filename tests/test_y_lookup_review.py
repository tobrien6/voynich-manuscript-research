import copy
import json
from pathlib import Path
import unittest

from scripts.verify_y_lookup_review import verify_record


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/hypotheses/y-lookup-image-v1'


class LookupImageRecordTests(unittest.TestCase):
    def setUp(self):
        self.selection = json.loads((BASE / 'selection.json').read_bytes())
        self.record = json.loads((BASE / 'image-review.json').read_bytes())

    def test_complete_provisional_record_is_structurally_valid(self):
        verify_record(self.record, self.selection, ROOT)

    def test_unverified_cases_cannot_be_upgraded_by_flags(self):
        for flag in ('independent_human_adjudication', 'image_alignment_verified', 'source_corrections_applied',
                     'valid_candidate_holdout', 'previously_unseen'):
            changed = copy.deepcopy(self.record)
            changed[flag] = True
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, 'unsupported verified'):
                verify_record(changed, self.selection, ROOT)

    def test_missing_pair_or_reference_slot_change_is_rejected(self):
        changed = copy.deepcopy(self.record)
        changed['cases'].pop()
        with self.assertRaisesRegex(ValueError, 'changed pair'):
            verify_record(changed, self.selection, ROOT)
        changed = copy.deepcopy(self.record)
        changed['cases'][0]['reference_slot_zero_based'] = 1
        with self.assertRaisesRegex(ValueError, 'changed pair'):
            verify_record(changed, self.selection, ROOT)

    def test_unresolved_alignment_cannot_support_a_fine_comparison(self):
        changed = copy.deepcopy(self.record)
        changed['cases'][0]['alignment_status'] = 'unresolved'
        with self.assertRaisesRegex(ValueError, 'fine comparison'):
            verify_record(changed, self.selection, ROOT)

    def test_missing_whole_image_or_observation_is_rejected(self):
        changed = copy.deepcopy(self.record)
        changed['retrieved_resources'].pop(0)
        with self.assertRaisesRegex(ValueError, 'resource'):
            verify_record(changed, self.selection, ROOT)
        changed = copy.deepcopy(self.record)
        changed['cases'][0]['alternatives'] = ''
        with self.assertRaisesRegex(ValueError, 'observation'):
            verify_record(changed, self.selection, ROOT)

    def test_region_bounds_and_url_are_consistent_with_native_image(self):
        changed = copy.deepcopy(self.record)
        region = next(item for item in changed['retrieved_resources'] if 'native_region_xywh' in item)
        region['native_region_xywh'][2] = 10000
        with self.assertRaisesRegex(ValueError, 'outside source'):
            verify_record(changed, self.selection, ROOT)
        changed = copy.deepcopy(self.record)
        region = next(item for item in changed['retrieved_resources'] if 'native_region_xywh' in item)
        region['url'] += '?wrong'
        with self.assertRaisesRegex(ValueError, 'region URL'):
            verify_record(changed, self.selection, ROOT)

    def test_record_pages_and_slot_types_cannot_disagree_with_selected_identity(self):
        changed = copy.deepcopy(self.record)
        changed['cases'][0]['target_page'] = 'f18r'
        with self.assertRaisesRegex(ValueError, 'source page identity'):
            verify_record(changed, self.selection, ROOT)
        changed = copy.deepcopy(self.record)
        changed['cases'][0]['reference_slot_zero_based'] = 2.0
        with self.assertRaisesRegex(ValueError, 'typed slot'):
            verify_record(changed, self.selection, ROOT)


if __name__ == '__main__':
    unittest.main()
