"""Verify frozen source selection and provisional image-receipt structure offline."""

import argparse
from datetime import datetime
import hashlib
from pathlib import Path
import re

try:
    from . import select_immediate_repeat_images as selector
    from .validate_evaluation_split import load_split_json
except ImportError:
    import select_immediate_repeat_images as selector
    from validate_evaluation_split import load_split_json


ROOT = Path(__file__).resolve().parents[1]
SELECTION = 'research/transliteration/immediate_repeat_image_selection.json'
REVIEW = 'research/transliteration/immediate_repeat_image_review.json'
FLAGS = ('image_alignment_verified', 'glyph_readings_verified',
         'source_corrections_applied', 'untouched_evaluation')
CASE_FIELDS = {'group', 'locus_key', 'image', 'status', 'source_preference',
               'inspected_files', 'direct_image_observation', 'source_informed_correspondence',
               'neighboring_placements_compared', 'contradictions_and_limits'}


def jpeg_dimensions(raw):
    """Read JPEG SOF dimensions without decoding, resizing or altering pixels."""
    if not raw.startswith(b'\xff\xd8'):
        raise ValueError('receipt image is not a JPEG')
    at = 2
    while at < len(raw):
        if raw[at] != 255:
            break
        while at < len(raw) and raw[at] == 255:
            at += 1
        if at == len(raw):
            break
        marker = raw[at]
        at += 1
        if marker in (0xD9, 0xDA):
            break
        if marker == 1 or 0xD0 <= marker <= 0xD8:
            continue
        length = int.from_bytes(raw[at:at + 2], 'big')
        if length < 2 or at + length > len(raw):
            break
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            body = raw[at + 2:at + length]
            if len(body) < 6:
                break
            width, height = int.from_bytes(body[3:5], 'big'), int.from_bytes(body[1:3], 'big')
            if width > 0 and height > 0:
                return width, height
            break
        at += length
    raise ValueError('JPEG has no valid dimension header')


def verify(review, selection, image_dir=None):
    if (type(review.get('schema_version')) is not int or review['schema_version'] != 1 or
            review.get('selection_path') != SELECTION or
            any(review.get(flag) is not False for flag in FLAGS)):
        raise ValueError('require declared schema, selection and provisional-only flags')
    cases = review.get('cases', [])
    expected = {c['locus_key']: c for c in selection['selected']}
    keys = [c['locus_key'] for c in cases]
    if len(keys) != len(set(keys)) or set(keys) != set(expected):
        raise ValueError('require exactly all fixed selected cases')
    file_count = 0
    for case in cases:
        selected = expected[case['locus_key']]
        if (set(case) != CASE_FIELDS or case['group'] != selected['group'] or
                selector.encoded(case['image']) != selector.encoded(selected['image']) or
                case['status'] != 'provisional' or case['source_preference'] != 'unresolved'):
            raise ValueError('case identity, image or provisional status differs')
        for field in ('direct_image_observation', 'source_informed_correspondence'):
            if not isinstance(case[field], str) or not case[field].strip():
                raise ValueError('require separate nonempty observation and correspondence')
        for field in ('neighboring_placements_compared', 'contradictions_and_limits'):
            if not isinstance(case[field], list) or not case[field] or any(
                    not isinstance(v, str) or not v.strip() for v in case[field]):
                raise ValueError('require neighboring placements and limitations')
        image = case['image']
        native_size = int(image['image_width']), int(image['image_height'])
        service, oid = image['image_service_url'], image['image_oid']
        files = case['inspected_files']
        roles = [f['role'] for f in files]
        if (len(roles) != len(set(roles)) or not {'info', 'overview', 'block', 'detail'} <= set(roles) or
                not set(roles) <= {'info', 'overview', 'block', 'detail', 'wide_detail'}):
            raise ValueError('require unique info, overview, block and detail receipts')
        for item in files:
            role = item['role']
            name = oid + '-' + role.replace('_', '-') + ('.json' if role == 'info' else '.jpg')
            if (item['file_name'] != name or type(item['bytes']) is not int or item['bytes'] < 1 or
                    not isinstance(item['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', item['sha256']) or
                    any(type(item[k]) is not int or item[k] < 1 for k in ('width', 'height'))):
                raise ValueError('invalid receipt filename, size, digest or dimensions')
            if datetime.fromisoformat(item['access_utc']).tzinfo is None:
                raise ValueError('receipt access time needs explicit timezone')
            dimensions = item['width'], item['height']
            if role == 'info':
                url = service + '/info.json'
                if dimensions != native_size or 'native_region' in item:
                    raise ValueError('native info dimensions differ')
            elif role == 'overview':
                url = service + '/full/!1800,1800/0/default.jpg'
                if ('native_region' in item or max(dimensions) != min(1800, max(native_size)) or
                        abs(dimensions[0] * native_size[1] - dimensions[1] * native_size[0]) > max(native_size)):
                    raise ValueError('overview dimensions do not preserve the bounded full page')
            else:
                region = item.get('native_region')
                if (not isinstance(region, list) or len(region) != 4 or
                        any(type(v) is not int for v in region) or
                        min(region[:2]) < 0 or min(region[2:]) < 1 or
                        region[0] + region[2] > native_size[0] or
                        region[1] + region[3] > native_size[1] or dimensions != tuple(region[2:])):
                    raise ValueError('review rectangle is outside native image bounds')
                url = service + '/' + ','.join(map(str, region)) + '/full/0/default.jpg'
            if item['url'] != url:
                raise ValueError('receipt URL differs from source image/rectangle')
            if image_dir is not None:
                raw = (Path(image_dir) / name).read_bytes()
                if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
                    raise ValueError('local inspected bytes differ from receipt')
                if role == 'info':
                    info = load_split_json(raw.decode())
                    actual = info['width'], info['height']
                else:
                    actual = jpeg_dimensions(raw)
                if actual != dimensions:
                    raise ValueError('local image dimensions differ from receipt')
            file_count += 1
    return {'selected_cases': len(cases), 'receipt_count': file_count,
            'local_image_bytes_checked': image_dir is not None,
            'visual_judgments_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, default=ROOT / REVIEW)
    parser.add_argument('--image-dir', type=Path)
    args = parser.parse_args()
    try:
        raw = (ROOT / SELECTION).read_bytes()
        selection = load_split_json(raw.decode())
        review = load_split_json(args.review.read_text())
        if selector.encoded(selection) != selector.encoded(selector.report()):
            raise ValueError('fixed source selection no longer replays')
        if review['selection_sha256'] != hashlib.sha256(raw).hexdigest():
            raise ValueError('review is not tied to the frozen selection bytes')
        result = verify(review, selection, args.image_dir)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'immediate-repeat image verification failed: {error}\n')
    print(selector.encoded(result).decode(), end='')


if __name__ == '__main__':
    main()
