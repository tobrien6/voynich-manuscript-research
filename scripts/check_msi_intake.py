"""Check a selected public MSI source record and optional local file identities.

This offline check does not authenticate the collection, certify visual
observations or reconstruct the multispectral processing pipeline.
"""

import argparse
import csv
import hashlib
import io
from pathlib import Path
import re

try:
    from .audit_eva_token_coverage import encoded
    from .paragraph_token_corpus import strict_json
    from .verify_boundary_repeat_image import jpeg_dimensions
except ImportError:
    from audit_eva_token_coverage import encoded
    from paragraph_token_corpus import strict_json
    from verify_boundary_repeat_image import jpeg_dimensions


ROOT = Path(__file__).resolve().parents[1]
PLAN = 'research/image-index/MULTISPECTRAL_INTAKE_PLAN.md'
RECORD = 'research/image-index/multispectral-intake.json'
INDEX = 'research/image-index/canvases.csv'
AUDIT = 'research/image-index/audit.json'
ALIASES = 'research/folio-aliases/decisions.json'
PINS = (PLAN, INDEX, AUDIT, ALIASES)
COLLECTION = '1mNQGKQDSCR4M_c2M2JrsU5soghvYwMig'
PROCESSED = '1BFwNZTgLqvgnIU8rmXQCdW6kIuC4baS7'
RGB = '1to9QOXNrSfIUITnogjkZSTy8zN553OGi'
TARGETS = {'1r': '1_J_2ukEJwknW7a2p8NnseypSwTyM28_I',
           '116v': '1Q3cUXX9mIs94FLPZPhLne-XbYrt25DNx'}
RGB_116V = '17hqCyh3kaBU_7Twa0N2VKRZjqfmddFVL'
PSC_116V = '1UBQfNp3pm8KfGjGCcAOCV1QXF_qQdjyE'
LISTING_SHA256 = '7907c36e2169813f66a6d3cf6128416443f19adb8d2be82817c24b6a81662fe2'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, expected):
    require(isinstance(value, dict) and set(value) == set(expected), 'unknown or missing record fields')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fingerprint(value):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value), 'invalid SHA-256')


def positive(value):
    require(type(value) is int and value > 0, 'positive integer required')


def exif_orientation(payload):
    if not payload.startswith(b'Exif\0\0'):
        return None
    raw = payload[6:]
    require(len(raw) >= 8 and raw[:2] in (b'II', b'MM'), 'invalid EXIF TIFF header')
    order = 'little' if raw[:2] == b'II' else 'big'
    def integer(offset, count):
        require(offset >= 0 and offset + count <= len(raw), 'truncated EXIF directory')
        return int.from_bytes(raw[offset:offset+count], order)
    require(integer(2, 2) == 42, 'invalid EXIF TIFF signature')
    start = integer(4, 4); count = integer(start, 2)
    require(start + 2 + 12*count + 4 <= len(raw), 'truncated EXIF entry table')
    values = []
    for index in range(count):
        offset = start + 2 + 12*index
        if integer(offset, 2) == 0x112:
            require(integer(offset+2, 2) == 3 and integer(offset+4, 4) == 1,
                    'orientation must be one EXIF SHORT')
            value = integer(offset+8, 2)
            require(1 <= value <= 8, 'invalid EXIF orientation')
            values.append(value)
    require(len(values) <= 1, 'duplicate EXIF orientation tags')
    return values[0] if values else None


def jpeg_metadata(raw):
    """Hash original bytes; inspect headers without modifying/decoding pixels."""
    require(raw.startswith(b'\xff\xd8') and raw.endswith(b'\xff\xd9'), 'require complete JPEG framing')
    dimensions = jpeg_dimensions(raw)
    position = 2; retained = bytearray(raw[:2]); orientations = []; icc = {}
    chunks_expected = None
    while position < len(raw):
        start = position
        require(raw[position] == 0xff, 'invalid pre-scan JPEG marker')
        while position < len(raw) and raw[position] == 0xff:
            position += 1
        require(position < len(raw), 'truncated JPEG marker')
        marker = raw[position];position += 1
        require(marker not in (0, 0xd8, 0xd9), 'unexpected pre-scan JPEG marker')
        if marker == 0xda:
            retained.extend(raw[start:]);break
        require(position + 2 <= len(raw), 'truncated JPEG length')
        length = int.from_bytes(raw[position:position+2], 'big')
        require(length >= 2 and position + length <= len(raw), 'truncated JPEG segment')
        payload = raw[position+2:position+length]
        is_exif = marker == 0xe1 and payload.startswith(b'Exif\0\0')
        if is_exif:
            orientations.append(exif_orientation(payload))
        else:
            retained.extend(raw[start:position+length])
        if marker == 0xe2 and payload.startswith(b'ICC_PROFILE\0'):
            require(len(payload) >= 14, 'truncated ICC header')
            number, total = payload[12], payload[13]
            require(1 <= number <= total and number not in icc, 'invalid ICC chunk order/count')
            require(chunks_expected in (None, total), 'inconsistent ICC chunk totals')
            chunks_expected = total;icc[number] = payload[14:]
        position += length
    else:
        raise ValueError('JPEG has no start of scan')
    require(len(orientations) <= 1, 'multiple EXIF segments need explicit adjudication')
    if icc:
        require(set(icc) == set(range(1, chunks_expected+1)), 'missing ICC chunks')
    return {'byte_count': len(raw), 'sha256': sha(raw), 'header_dimensions': dimensions,
            'exif_orientation': orientations[0] if orientations else None,
            'icc_profile_sha256': sha(b''.join(icc[i] for i in sorted(icc))) if icc else None,
            'jpeg_without_exif_sha256': sha(bytes(retained))}


def decoded_observation(raw):
    """Optional full decoding, without EXIF rotation or any image enhancement."""
    try:
        from PIL import Image
    except ImportError as error:
        raise ValueError('full pixel verification requires Pillow') from error
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        require(image.mode == 'RGB', 'selected image is not decoded RGB')
        return {'format': image.format, 'mode': image.mode, 'dimensions': [image.width, image.height],
                'stored_rgb_sha256': sha(image.tobytes()), 'decoder': 'Pillow '+Image.__version__}


def verify(record, cache=None, root=ROOT, decode=False):
    require(not decode or cache is not None, 'pixel decoding requires the local source cache')
    keys(record, ('schema_version', 'method', 'recorded_on', 'inputs_sha256', 'release',
                  'listing', 'selected_images', 'yale_references', 'duplicate_check',
                  'observations', 'exposure', 'verification_limits'))
    require(type(record['schema_version']) is int and record['schema_version'] == 1,
            'unsupported schema')
    require(record['method'] == 'selected-public-voynich-msi-intake-v1', 'unsupported method')
    require(record['recorded_on'] == '2026-10-12', 'source inspection date differs')
    require(encoded(record['inputs_sha256']) == encoded({p: sha((root/p).read_bytes()) for p in PINS}),
            'source index, alias registry or plan pins changed')
    release = record['release']
    keys(release, ('article_url', 'article_date', 'readme_date', 'readme', 'capture_year', 'credit',
                   'manuscript_citation', 'access_and_reuse', 'reported_processing'))
    require(release['article_url'] == 'https://manuscriptroadtrip.wordpress.com/2024/09/08/multispectral-imaging-and-the-voynich-manuscript/'
            and release['article_date'] == '2024-09-08' and release['readme_date'] == '2024-09-09'
            and type(release['capture_year']) is int and release['capture_year'] == 2014, 'release identity differs')
    keys(release['readme'], ('file_id', 'filename', 'sha256', 'byte_count', 'page_count'))
    require(release['readme']['file_id'] == '1nzKNlV2BqCEz3VvheAFZ_4IULFwLExng'
            and release['readme']['filename'] == 'READ ME.pdf'
            and type(release['readme']['page_count']) is int and release['readme']['page_count'] == 1,
            'Read Me identity differs')
    fingerprint(release['readme']['sha256']);positive(release['readme']['byte_count'])
    for field in ('credit', 'manuscript_citation', 'access_and_reuse', 'reported_processing'):
        require(isinstance(release[field], str) and release[field], 'source statement missing')
    listing = record['listing']
    keys(listing, ('root_id', 'top_folders', 'processed_folio_folders', 'rgb_files', 'selected_folder_files'))
    require(listing['root_id'] == COLLECTION, 'wrong public collection')
    require(sha(encoded(listing)) == LISTING_SHA256, 'manually extracted visible listing identity changed')
    require([len(listing[k]) for k in ('top_folders', 'processed_folio_folders', 'rgb_files', 'selected_folder_files')]
            == [4, 10, 6, 10], 'declared listing scope changed')
    all_rows = [row for key in ('top_folders', 'processed_folio_folders', 'rgb_files', 'selected_folder_files') for row in listing[key]]
    for row in all_rows:
        keys(row, ('file_id', 'name', 'parent_id'))
        require(isinstance(row['file_id'], str) and re.fullmatch('[A-Za-z0-9_-]{20,}', row['file_id']), 'invalid public item ID')
        require(isinstance(row['name'], str) and row['name'] and len(row['name']) < 250
                and '/' not in row['name'] and '\\' not in row['name'] and '@' not in row['name'], 'invalid research item name')
    for category in ('top_folders', 'processed_folio_folders', 'rgb_files', 'selected_folder_files'):
        require(len({row['file_id'] for row in listing[category]}) == len(listing[category]), 'duplicate listing ID')
    require(all(row['parent_id'] == COLLECTION for row in listing['top_folders']), 'top folder parent differs')
    require(all(row['parent_id'] == PROCESSED for row in listing['processed_folio_folders']), 'processed folder parent differs')
    require(all(row['parent_id'] == RGB for row in listing['rgb_files']), 'RGB folder parent differs')
    require(all(row['parent_id'] in TARGETS.values() for row in listing['selected_folder_files']), 'selected folder parent differs')
    expected = {row['file_id']: row for row in listing['selected_folder_files'] if row['name'].endswith('.jpg')}
    rgb = next((row for row in listing['rgb_files'] if row['file_id'] == RGB_116V), None)
    require(rgb is not None, 'RGB reference missing');expected[RGB_116V] = rgb
    require(len(expected) == 6 and len(record['selected_images']) == 6
            and {row['file_id'] for row in record['selected_images']} == set(expected), 'fixed JPEG selection changed')
    for image in record['selected_images']:
        keys(image, ('file_id', 'name', 'parent_id', 'source_side', 'local_filename', 'view_url', 'download_url', 'metadata', 'decoded'))
        require(encoded({k:image[k] for k in ('file_id', 'name', 'parent_id')}) == encoded(expected[image['file_id']]),
                'selected image source name/parent differs')
        side = '116v' if image['parent_id'] == RGB else next(k for k,v in TARGETS.items() if v == image['parent_id'])
        require(image['source_side'] == side and image['local_filename'] == 'msi-'+image['file_id']+'.jpg', 'source label or local file differs')
        require(image['view_url'] == 'https://drive.google.com/file/d/'+image['file_id']+'/view'
                and image['download_url'] == 'https://drive.google.com/uc?export=download&id='+image['file_id'], 'public image URL differs')
        check_metadata(image['metadata'])
        check_decoded(image['decoded'], image['metadata']['header_dimensions'])
        if cache is not None:
            raw=(cache/image['local_filename']).read_bytes()
            require(encoded(jpeg_metadata(raw)) == encoded(image['metadata']), 'local MSI bytes/headers differ')
            if decode:check_actual_decoding(raw, image['decoded'])
    with (root/INDEX).open(newline='') as stream:
        indexed = {row['yale_label']: row for row in csv.DictReader(stream) if row['yale_label'] in TARGETS}
    audit = strict_json((root/AUDIT).read_bytes())
    require([row['side'] for row in record['yale_references']] == ['1r', '116v'], 'Yale reference selection differs')
    for reference in record['yale_references']:
        keys(reference, ('side', 'index_row', 'local_filename', 'metadata', 'manifest_sha256', 'decoded'))
        row = indexed[reference['side']]
        require(encoded(reference['index_row']) == encoded(row)
                and reference['local_filename'] == 'yale-'+reference['side']+'.jpg', 'Yale reference index identity differs')
        require(reference['manifest_sha256'] == audit['manifest_sha256'], 'manifest identity differs')
        check_metadata(reference['metadata'])
        check_decoded(reference['decoded'], reference['metadata']['header_dimensions'])
        require(reference['metadata']['header_dimensions'] == [int(row['image_width']), int(row['image_height'])], 'Yale dimensions differ')
        if cache is not None:
            raw=(cache/reference['local_filename']).read_bytes()
            require(encoded(jpeg_metadata(raw)) == encoded(reference['metadata']), 'local Yale bytes/headers differ')
            if decode:check_actual_decoding(raw, reference['decoded'])
    duplicate = record['duplicate_check']
    keys(duplicate, ('file_ids', 'byte_different_count', 'byte_different_offsets', 'same_jpeg_without_exif', 'decoded_raw_rgb_sha256', 'decoder'))
    require(duplicate['file_ids'] == [PSC_116V, RGB_116V]
            and type(duplicate['byte_different_count']) is int and duplicate['byte_different_count'] == 1
            and duplicate['byte_different_offsets'] == [126]
            and type(duplicate['same_jpeg_without_exif']) is bool and duplicate['same_jpeg_without_exif'], 'PSC copy comparison differs')
    fingerprint(duplicate['decoded_raw_rgb_sha256'])
    require(isinstance(duplicate['decoder'], str) and duplicate['decoder'], 'decoder identity missing')
    metadata = {row['file_id']:row['metadata'] for row in record['selected_images']}
    require(metadata[PSC_116V]['exif_orientation'] == 3 and metadata[RGB_116V]['exif_orientation'] == 1
            and metadata[PSC_116V]['jpeg_without_exif_sha256'] == metadata[RGB_116V]['jpeg_without_exif_sha256'], 'orientation/encoded pixel identity differs')
    pixels={row['file_id']:row['decoded']['stored_rgb_sha256'] for row in record['selected_images']}
    require(pixels[PSC_116V] == pixels[RGB_116V] == duplicate['decoded_raw_rgb_sha256'], 'recorded raw pixel identity differs')
    observations = record['observations']
    keys(observations, ('1r', '116v', 'disposition'))
    for side in TARGETS:
        require(isinstance(observations[side], str) and observations[side], 'visual observation missing')
    require(observations['disposition'] == 'supplementary views; glyph readings and legacy alias unresolved', 'unsupported interpretation')
    flags = {'plan_remotely_published_before_selected_pixels': True, 'article_and_ordinary_images_previously_exposed': True,
             'single_nonblind_assistant_review': True, 'independent_qualified_review': False,
             'pixel_registration_or_new_enhancement': False, 'raw_band_archive_retrieved': False,
             'alias_registry_changed': False, 'new_transcription_or_translation': False}
    require(encoded(record['exposure']) == encoded(flags), 'exposure or interpretation limits changed')
    require(isinstance(record['verification_limits'], str) and record['verification_limits'], 'checker limits missing')
    if cache is not None:
        raw=(cache/'README.pdf').read_bytes()
        require(raw.startswith(b'%PDF') and len(raw) == release['readme']['byte_count'] and sha(raw) == release['readme']['sha256'], 'Read Me bytes differ')
        raw=(cache/'live-manifest.json').read_bytes();require(sha(raw) == audit['manifest_sha256'], 'local manifest differs')
        manifest = strict_json(raw)
        for reference in record['yale_references']:
            row=reference['index_row'];canvas=next(c for c in manifest['items'] if c['id'] == row['canvas_uri'])
            require(canvas['label'] == {'none':[reference['side']]} and [canvas['width'],canvas['height']] == reference['metadata']['header_dimensions'], 'live canvas differs')
        first=(cache/('msi-'+PSC_116V+'.jpg')).read_bytes();second=(cache/('msi-'+RGB_116V+'.jpg')).read_bytes()
        require(len(first) == len(second) and [i for i,(a,b) in enumerate(zip(first,second)) if a!=b] == duplicate['byte_different_offsets'], 'actual duplicate-byte comparison differs')
    return {'selected_msi_files': 6, 'yale_reference_files': 2, 'processed_folder_names': 10,
            'local_bytes_checked': cache is not None, 'local_pixels_decoded': decode, 'glyph_or_alias_verified': False}


def check_metadata(value):
    keys(value, ('byte_count', 'sha256', 'header_dimensions', 'exif_orientation', 'icc_profile_sha256', 'jpeg_without_exif_sha256'))
    positive(value['byte_count']);fingerprint(value['sha256']);fingerprint(value['jpeg_without_exif_sha256'])
    require(isinstance(value['header_dimensions'], list) and len(value['header_dimensions']) == 2, 'image dimensions required')
    for n in value['header_dimensions']:positive(n)
    require(value['exif_orientation'] is None or (type(value['exif_orientation']) is int and 1<=value['exif_orientation']<=8), 'invalid orientation scalar')
    if value['icc_profile_sha256'] is not None:fingerprint(value['icc_profile_sha256'])


def check_decoded(value, dimensions):
    keys(value, ('format', 'mode', 'dimensions', 'stored_rgb_sha256', 'decoder'))
    require(value['format'] == 'JPEG' and value['mode'] == 'RGB'
            and encoded(value['dimensions']) == encoded(dimensions), 'decoded image representation differs')
    fingerprint(value['stored_rgb_sha256'])
    require(isinstance(value['decoder'], str) and value['decoder'].startswith('Pillow '), 'decoder observation missing')


def check_actual_decoding(raw, expected):
    actual=decoded_observation(raw)
    require(encoded({k:v for k,v in actual.items() if k!='decoder'}) == encoded(
            {k:v for k,v in expected.items() if k!='decoder'}), 'decoded RGB content differs')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, default=ROOT/RECORD)
    parser.add_argument('--cache', type=Path)
    parser.add_argument('--decode', action='store_true', help='verify full stored RGB content with Pillow; requires --cache')
    args=parser.parse_args()
    try:
        result=verify(strict_json(args.record.read_bytes()), args.cache, decode=args.decode)
    except (ValueError, OSError, KeyError, StopIteration) as error:
        parser.exit(1, f'MSI intake failed: {error}\n')
    print(encoded(result).decode(), end='')


if __name__ == '__main__':
    main()
