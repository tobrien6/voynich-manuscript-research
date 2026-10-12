from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_transliterations import ROOT
from scripts.verify_paragraph_image_pilot import verify_pilot


class ParagraphImagePilotTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'research/transliteration/paragraph_image_pilot.json').read_text())

    def test_selected_records_and_contexts_verify_offline(self):
        self.assertEqual(verify_pilot(self.record), 3)

    def test_changed_selection_image_or_context_is_rejected(self):
        for field in ('selection', 'image', 'context'):
            altered = deepcopy(self.record)
            if field == 'selection':
                altered['records'].reverse()
            elif field == 'image':
                altered['records'][0]['image']['image_oid'] = 'wrong'
            else:
                altered['records'][0]['source_contexts'][0]['adjacent_context'][1]['paragraph_end'] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify_pilot(altered)

    def test_fingerprint_change_and_unsupported_adjudication_are_rejected(self):
        altered = deepcopy(self.record)
        altered['annotation_audit_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'audit fingerprint differs'):
            verify_pilot(altered)
        altered = deepcopy(self.record)
        altered['records'][0]['paragraph_disposition'] = 'confirmed'
        with self.assertRaisesRegex(ValueError, 'uncertainty declaration differs'):
            verify_pilot(altered)

    def test_local_image_mismatch_cannot_verify(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'f9r.jpg').write_bytes(b'incorrect local image')
            with self.assertRaisesRegex(ValueError, 'local image fingerprint differs'):
                verify_pilot(self.record, path)


if __name__ == '__main__':
    unittest.main()
