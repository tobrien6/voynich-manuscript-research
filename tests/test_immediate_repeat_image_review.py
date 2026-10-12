from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import verify_immediate_repeat_images as module


def jpeg(width, height):
    body = b'\x08' + height.to_bytes(2, 'big') + width.to_bytes(2, 'big') + b'\x01\x01\x11\x00'
    return b'\xff\xd8\xff\xc0' + (len(body) + 2).to_bytes(2, 'big') + body + b'\xff\xd9'


def fixture():
    image = {'image_width': '100', 'image_height': '80', 'image_service_url': 'https://example.test/iiif/1',
             'image_oid': '1', 'yale_label': '1r'}
    selection = {'selected': [{'locus_key': 'f1r.2', 'group': 'paired_agreement', 'image': image}]}
    files, raw_files = [], {}
    for role in ('info', 'overview', 'block', 'detail'):
        width, height = (100, 80) if role in ('info', 'overview') else (30, 20)
        raw = json.dumps({'width': width, 'height': height}).encode() if role == 'info' else jpeg(width, height)
        name = '1-' + role + ('.json' if role == 'info' else '.jpg')
        suffix = '/info.json' if role == 'info' else '/full/!1800,1800/0/default.jpg' if role == 'overview' else '/10,15,30,20/full/0/default.jpg'
        item = {'role': role, 'file_name': name, 'url': image['image_service_url'] + suffix,
                'width': width, 'height': height, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                'access_utc': '2026-10-12T08:00:00+00:00'}
        if role not in ('info', 'overview'):
            item['native_region'] = [10, 15, 30, 20]
        files.append(item)
        raw_files[name] = raw
    case = {'group': 'paired_agreement', 'locus_key': 'f1r.2', 'image': image,
            'status': 'provisional', 'source_preference': 'unresolved', 'inspected_files': files,
            'direct_image_observation': 'Visible marks.', 'source_informed_correspondence': 'Provisional context.',
            'neighboring_placements_compared': ['Before/after rows.'], 'contradictions_and_limits': ['Faint trace.']}
    review = {'schema_version': 1, 'selection_path': module.SELECTION, 'cases': [case],
              **{flag: False for flag in module.FLAGS}}
    return review, selection, raw_files


class RepeatImageReviewTests(unittest.TestCase):
    def test_structure_and_optional_local_receipts(self):
        review, selection, files = fixture()
        self.assertEqual(module.verify(review, selection)['receipt_count'], 4)
        with tempfile.TemporaryDirectory() as directory:
            for name, raw in files.items():
                (Path(directory) / name).write_bytes(raw)
            result = module.verify(review, selection, directory)
            self.assertTrue(result['local_image_bytes_checked'])
            self.assertFalse(result['visual_judgments_verified'])
            (Path(directory) / '1-detail.jpg').write_bytes(b'changed')
            with self.assertRaises(ValueError):
                module.verify(review, selection, directory)

    def test_selected_case_coverage_and_source_identity(self):
        review, selection, _ = fixture()
        for mutation in ('missing', 'duplicate', 'key', 'group', 'image'):
            changed = deepcopy(review)
            if mutation == 'missing':
                changed['cases'] = []
            elif mutation == 'duplicate':
                changed['cases'] *= 2
            elif mutation == 'image':
                changed['cases'][0]['image']['image_oid'] = '2'
            else:
                changed['cases'][0]['locus_key' if mutation == 'key' else 'group'] = 'changed'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                module.verify(changed, selection)

    def test_provisional_flags_and_notes_are_required(self):
        review, selection, _ = fixture()
        for flag in module.FLAGS:
            changed = deepcopy(review)
            changed[flag] = 0
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                module.verify(changed, selection)
        for field, value in [('status', 'verified'), ('source_preference', 'IT2a'),
                             ('direct_image_observation', ''), ('source_informed_correspondence', ''),
                             ('neighboring_placements_compared', []), ('contradictions_and_limits', [])]:
            changed = deepcopy(review)
            changed['cases'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                module.verify(changed, selection)

    def test_window_dimensions_urls_and_types(self):
        review, selection, _ = fixture()
        for field, value in [('native_region', [90, 15, 30, 20]), ('native_region', [True, 15, 30, 20]),
                             ('width', 31), ('url', 'https://wrong.test/detail.jpg'),
                             ('file_name', '../outside.jpg'), ('sha256', 'bad'), ('bytes', True),
                             ('access_utc', '2026-10-12T08:00:00')]:
            changed = deepcopy(review)
            changed['cases'][0]['inspected_files'][-1][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                module.verify(changed, selection)

    def test_all_receipt_roles_required_once(self):
        review, selection, _ = fixture()
        for mutation in ('missing', 'duplicate', 'unknown'):
            changed = deepcopy(review)
            files = changed['cases'][0]['inspected_files']
            if mutation == 'missing':
                files.pop()
            elif mutation == 'duplicate':
                files.append(deepcopy(files[-1]))
            else:
                files[-1]['role'] = 'unknown'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                module.verify(changed, selection)

    def test_jpeg_header_dimensions_and_bad_files(self):
        self.assertEqual(module.jpeg_dimensions(jpeg(25, 10)), (25, 10))
        for raw in (b'no', b'\xff\xd8\xff\xda', jpeg(0, 1), jpeg(1, 1)[:8]):
            with self.assertRaises(ValueError):
                module.jpeg_dimensions(raw)


if __name__ == '__main__':
    unittest.main()
