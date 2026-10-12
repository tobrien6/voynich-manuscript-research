from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.paragraph_token_corpus import strict_json
from scripts.check_msi_intake import (
    ROOT, RECORD, LISTING_SHA256, sha, jpeg_metadata, exif_orientation,
    verify, check_metadata, check_actual_decoding, main,
)


def segment(marker, payload):
    return bytes((0xff, marker)) + struct.pack('>H', len(payload)+2) + payload


def synthetic_header(orientation=1, order='<', icc=True):
    tiff = (b'II' if order == '<' else b'MM') + struct.pack(order+'HIH', 42, 8, 1)
    tiff += struct.pack(order+'HHI', 0x112, 3, 1) + struct.pack(order+'H', orientation) + b'\0\0'
    tiff += struct.pack(order+'I', 0)
    raw = b'\xff\xd8' + segment(0xe0, b'\0'*92) + segment(0xe1, b'Exif\0\0'+tiff)
    if icc:
        # Deliberately reversed chunk order; the profile has a separate identity.
        raw += segment(0xe2, b'ICC_PROFILE\0'+bytes((2,2))+b'profile')
        raw += segment(0xe2, b'ICC_PROFILE\0'+bytes((1,2))+b'test-')
    raw += segment(0xc0, b'\x08'+struct.pack('>HH', 12, 9)+b'\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00')
    return raw + segment(0xda, b'\x03\x01\x00\x02\x00\x03\x00\x00\x3f\x00') + b'\x01\x02\xff\xd9'


class MSIIntakeTests(unittest.TestCase):
    def setUp(self):
        self.record = strict_json((ROOT/RECORD).read_bytes())

    def test_valid_record_binds_finite_selection_without_certifying_glyphs(self):
        result = verify(self.record)
        self.assertEqual(result, {'selected_msi_files':6,'yale_reference_files':2,
            'processed_folder_names':10,'local_bytes_checked':False,
            'local_pixels_decoded':False,'glyph_or_alias_verified':False})
        self.assertEqual(sha(encoded(self.record['listing'])), LISTING_SHA256)
        self.assertEqual(len(self.record['selected_images']), 6)

    def test_orientation_reads_both_tiff_byte_orders_and_preserves_original_hashes(self):
        for order in ('<','>'):
            one=synthetic_header(1,order);three=synthetic_header(3,order)
            first=jpeg_metadata(one);second=jpeg_metadata(three)
            self.assertEqual(first['header_dimensions'], [9,12])
            self.assertEqual(first['exif_orientation'], 1)
            self.assertEqual(second['exif_orientation'], 3)
            self.assertNotEqual(first['sha256'], second['sha256'])
            self.assertEqual(first['jpeg_without_exif_sha256'], second['jpeg_without_exif_sha256'])
            self.assertEqual(first['icc_profile_sha256'], sha(b'test-profile'))
            self.assertEqual(one,synthetic_header(1,order))
        self.assertEqual([i for i,(a,b) in enumerate(zip(synthetic_header(1),synthetic_header(3))) if a!=b],[126])

    def test_truncated_headers_bad_orientation_and_duplicate_profiles_fail(self):
        good=synthetic_header()
        for raw in (b'<html>download confirmation</html>',good[:-1],good[:30]+b'\xff\xd9',
                    synthetic_header(0),synthetic_header(9)):
            with self.assertRaises(ValueError):jpeg_metadata(raw)
        duplicate=good.replace(b'ICC_PROFILE\0\x02\x02',b'ICC_PROFILE\0\x01\x02')
        with self.assertRaisesRegex(ValueError,'ICC'):jpeg_metadata(duplicate)
        bad_tiff=b'Exif\0\0II'+b'\x00'*6
        with self.assertRaises(ValueError):exif_orientation(bad_tiff)

    def test_source_listing_and_selected_source_label_url_changes_fail(self):
        paths=[('listing','rgb_files',0,'name'), ('selected_images',0,'source_side'),
               ('selected_images',0,'parent_id'), ('selected_images',0,'download_url'),
               ('selected_images',0,'local_filename'), ('yale_references',0,'side')]
        for path in paths:
            changed=deepcopy(self.record);target=changed
            for key in path[:-1]:target=target[key]
            target[path[-1]]='changed'
            with self.assertRaises(ValueError):verify(changed)
        changed=deepcopy(self.record);changed['listing']['rgb_files'].append(changed['listing']['rgb_files'][0])
        with self.assertRaises(ValueError):verify(changed)

    def test_unknown_fields_scalar_types_and_changed_exposure_fail(self):
        edits=[lambda r:r.update(frontend_configuration='placeholder'),
               lambda r:r.update(schema_version=True),
               lambda r:r['selected_images'][0]['metadata'].update(byte_count=True),
               lambda r:r['selected_images'][0]['metadata'].update(exif_orientation=True),
               lambda r:r['selected_images'][0]['decoded'].update(dimensions=[True,8176]),
               lambda r:r['selected_images'][0]['decoded'].update(mode='L'),
               lambda r:r['exposure'].update(independent_qualified_review=True),
               lambda r:r['exposure'].update(alias_registry_changed=0),
               lambda r:r['release']['readme'].update(page_count=True)]
        for edit in edits:
            changed=deepcopy(self.record);edit(changed)
            with self.assertRaises(ValueError):verify(changed)

    def test_cache_wrong_bytes_and_undocumented_input_changes_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            cache=Path(directory);first=self.record['selected_images'][0]
            path=cache/first['local_filename'];original=synthetic_header();path.write_bytes(original)
            with self.assertRaisesRegex(ValueError,'local MSI bytes'):verify(self.record,cache)
            self.assertEqual(path.read_bytes(),original)
        changed=deepcopy(self.record);changed['inputs_sha256'][next(iter(changed['inputs_sha256']))]='0'*64
        with self.assertRaisesRegex(ValueError,'pins'):verify(changed)

    def test_full_decode_requires_cache_and_rejects_changed_decoded_pixels(self):
        with self.assertRaisesRegex(ValueError,'local source cache'):verify(self.record,decode=True)
        expected=self.record['selected_images'][0]['decoded']
        altered={**expected,'stored_rgb_sha256':'0'*64}
        with patch('scripts.check_msi_intake.decoded_observation',return_value=altered), \
                self.assertRaisesRegex(ValueError,'decoded RGB content'):check_actual_decoding(b'synthetic',expected)
        another_version={**expected,'decoder':'Pillow later-test-version'}
        with patch('scripts.check_msi_intake.decoded_observation',return_value=another_version):
            check_actual_decoding(b'synthetic',expected)

    def test_cli_strict_json_types_and_read_only_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'record.json';path.write_bytes(encoded(self.record))
            def cli():
                with patch('sys.argv',['msi.py','--record',str(path)]),redirect_stdout(io.StringIO()):main()
            cli();valid=path.read_bytes();self.assertEqual(valid,encoded(self.record))
            boolean=deepcopy(self.record);boolean['schema_version']=True
            decimal=deepcopy(self.record);decimal['schema_version']=1.0
            for raw in (encoded(boolean),encoded(decimal),b'{"x":1,"x":2}',b'{"x":NaN}'):
                path.write_bytes(raw)
                with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):cli()
                self.assertEqual(path.read_bytes(),raw)


if __name__=='__main__':unittest.main()
