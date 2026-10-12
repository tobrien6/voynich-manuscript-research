from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_transliterations import ROOT
from scripts.verify_residual_paragraph_pilot import verify_residual_pilot


class ResidualParagraphPilotTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'research/transliteration/residual_paragraph_image_pilot.json').read_text())

    def test_complete_selected_contexts_verify_offline(self):
        self.assertEqual(verify_residual_pilot(self.record), (3, 5))

    def test_missing_or_reordered_context_cannot_hide_a_disagreement(self):
        for mode in ('missing', 'reordered'):
            altered = deepcopy(self.record)
            if mode == 'missing':
                altered['records'][2]['contexts'].pop()
            else:
                altered['records'][2]['contexts'].reverse()
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'context coverage'):
                verify_residual_pilot(altered)

    def test_changed_source_annotations_or_page_selection_fail(self):
        altered = deepcopy(self.record)
        altered['records'][0]['source_page_annotations'][0]['loci'][0]['paragraph_start'] = False
        with self.assertRaisesRegex(ValueError, 'page annotations differ'):
            verify_residual_pilot(altered)
        altered = deepcopy(self.record)
        altered['records'].reverse()
        with self.assertRaisesRegex(ValueError, 'fixed selection'):
            verify_residual_pilot(altered)

    def test_altered_input_or_image_provenance_is_rejected(self):
        altered = deepcopy(self.record)
        altered['generic_p_audit_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'audit fingerprint differs'):
            verify_residual_pilot(altered)
        altered = deepcopy(self.record)
        altered['records'][0]['image']['image_oid'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'image references differ'):
            verify_residual_pilot(altered)

    def test_unsupported_visual_confirmation_or_changed_local_bytes_fail(self):
        altered = deepcopy(self.record)
        altered['records'][0]['contexts'][0]['paragraph_disposition'] = 'confirmed'
        with self.assertRaisesRegex(ValueError, 'uncertainty declarations'):
            verify_residual_pilot(altered)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'f19v.jpg').write_bytes(b'incorrect local image')
            with self.assertRaisesRegex(ValueError, 'local image fingerprint differs'):
                verify_residual_pilot(self.record, path)


if __name__ == '__main__':
    unittest.main()
