"""Replay source/image metadata for the local sole-repeat image check, not its visual judgments."""

import argparse
import csv
import hashlib
from pathlib import Path
import re

try:
    from .audit_eva_token_coverage import encoded
    from .audit_transliterations import ROOT, load_sources
    from .paragraph_boundary_repetition import build as build_parent
    from .paragraph_token_corpus import build as build_corpus, strict_json
    from .token_baselines import paired_sources
except ImportError:
    from audit_eva_token_coverage import encoded
    from audit_transliterations import ROOT, load_sources
    from paragraph_boundary_repetition import build as build_parent
    from paragraph_token_corpus import build as build_corpus, strict_json
    from token_baselines import paired_sources


PINS = (
    'research/transliteration/BOUNDARY_REPEAT_IMAGE_PLAN.md',
    'research/transliteration/paragraph_boundary_repetition.json',
    'research/transliteration/paragraph_corpus_coverage.json',
    'data/transliterations.json', 'research/image-index/canvases.csv',
)


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jpeg_dimensions(raw):
    """Read dimensions from a JPEG start-of-frame marker; do not edit pixels."""
    if raw[:2] != b'\xff\xd8':
        raise ValueError('image is not a JPEG')
    position = 2
    while position < len(raw):
        if raw[position] != 255:
            raise ValueError('invalid JPEG marker sequence')
        while position < len(raw) and raw[position] == 255:
            position += 1
        if position >= len(raw):
            break
        marker = raw[position]
        position += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        if position + 2 > len(raw):
            break
        length = int.from_bytes(raw[position:position + 2], 'big')
        if length < 2 or position + length > len(raw):
            raise ValueError('truncated JPEG marker segment')
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            if length < 7:
                raise ValueError('truncated JPEG start-of-frame segment')
            dimensions = [int.from_bytes(raw[position + 5:position + 7], 'big'),
                          int.from_bytes(raw[position + 3:position + 5], 'big')]
            if not all(dimensions):
                raise ValueError('JPEG dimensions must be nonzero')
            return dimensions
        position += length
    raise ValueError('JPEG has no supported start-of-frame dimensions')


def source_facts(root=ROOT):
    parent = build_parent(root)
    parent_raw = (root / PINS[1]).read_bytes()
    if encoded(parent) != encoded(strict_json(parent_raw)):
        raise ValueError('parent boundary report differs from complete source replay')
    hits = []
    for paragraph in parent['paragraphs']:
        for variant in paragraph['variants']:
            for boundary in variant['boundaries']:
                if boundary['observed_repeat']:
                    i = boundary['boundary_index']
                    hits.append((variant['source_id'], variant['uncertain_spaces'],
                                 paragraph['member_keys'][i], paragraph['member_keys'][i + 1]))
    if len(hits) != 4 or {(a, b) for _, _, a, b in hits} != {('f82r.3', 'f82r.4')}:
        raise ValueError('sole-repeat selection changed; do not silently select another case')
    corpus = build_corpus(root)
    unit = next(p for p in corpus['paragraphs'] if p['common_eligible'] and
                'f82r.3' in p['member_keys'] and 'f82r.4' in p['member_keys'])
    variants = []
    for variant in unit['variants']:
        rows = {row['locus_key']: row for row in variant['loci']}
        left, right = rows['f82r.3'], rows['f82r.4']
        variants.append({
            'source_id': variant['source_id'], 'uncertain_spaces': variant['uncertain_spaces'],
            'left_endpoint': left['tokens'][-1], 'right_endpoint': right['tokens'][0],
            'same_within_variant': left['tokens'][-1] == right['tokens'][0],
            'selected_row_metadata': [{k: value for k, value in row.items() if k != 'tokens'}
                                      for row in (left, right)],
        })
    native = [{'source_id': source['id'], 'key': locus.key, 'text': locus.text,
               'source_line_number': locus.line_number}
              for source, document in paired_sources(load_sources(root)) for locus in document.loci
              if locus.present and locus.key in ('f82r.3', 'f82r.4')]
    with (root / PINS[-1]).open(newline='') as stream:
        images = [row for row in csv.DictReader(stream) if row['yale_label'] == '82r']
    if len(images) != 1 or images[0]['label_class'] != 'exact_single_side_label':
        raise ValueError('indexed 82r image is no longer uniquely labeled')
    return {'common_unit_id': unit['common_unit_id'], 'member_keys': unit['member_keys'],
            'sources': corpus['sources'], 'endpoint_variants': variants,
            'selected_native_source_text': native, 'image_index_record': images[0]}


def verify_record(record, image_dir=None, root=ROOT):
    if type(record.get('schema_version')) is not int or record['schema_version'] != 1 or \
            record['method'] != 'sole encoded boundary-repeat source image check v1':
        raise ValueError('unsupported image-check format')
    expected_pins = {name: fingerprint(root / name) for name in PINS}
    if encoded(record['inputs_sha256']) != encoded(expected_pins):
        raise ValueError('image-check input fingerprints differ')
    history = record['plan_history']
    if history['original_before_image_inspection_sha256'] != \
            'b2c4dc17d13aa549549c1ea13af031728eb67536e99156ec1d85ae224ae383a7' or \
            history['current_public_document_sha256'] != expected_pins[PINS[0]] or \
            not history['post_inspection_revision_scope']:
        raise ValueError('original/current local plan provenance differs')
    expected = source_facts(root)
    actual = {key: record[key] for key in ('sources', 'endpoint_variants',
                                         'selected_native_source_text', 'image_index_record')}
    actual.update({key: record['selection'][key] for key in ('common_unit_id', 'member_keys')})
    if encoded(actual) != encoded(expected):
        raise ValueError('selected unit, native endpoints, row metadata, or image identity differs')
    if [record['selection']['left_key'], record['selection']['right_key']] != ['f82r.3', 'f82r.4']:
        raise ValueError('selected repeat identifiers differ')
    image = expected['image_index_record']
    dimensions = [int(image['image_width']), int(image['image_height'])]
    retrieval = record['retrieval']
    if set(retrieval['file_sha256']) != {'f82r.jpg', 'live-manifest.json', 'info.json'} or \
            any(not isinstance(sha, str) or not re.fullmatch('[0-9a-f]{64}', sha)
                for sha in retrieval['file_sha256'].values()):
        raise ValueError('required primary retrieval fingerprints differ')
    if retrieval['live_canvas_id'] != image['canvas_uri'] or retrieval['live_label'] != {'none': ['82r']} or \
            retrieval['image_url'] != image['full_image_url'] or retrieval['decoded_jpeg_dimensions'] != dimensions:
        raise ValueError('retrieved image identity or dimensions differ')
    for key in ('live_canvas_dimensions', 'image_info_dimensions'):
        if encoded(retrieval[key]) != encoded(dict(zip(('width', 'height'), dimensions))):
            raise ValueError('retrieved metadata dimensions differ')
    if [region['id'] for region in record['inspected_regions']] != ['top-context', 'right-endpoint', 'left-endpoint']:
        raise ValueError('required contextual and endpoint regions differ')
    for region in record['inspected_regions']:
        box = region['region_xywh']
        if len(box) != 4 or any(type(n) is not int for n in box):
            raise ValueError('region coordinates must be integer pixel values')
        x, y, width, height = box
        if min(x, y) < 0 or min(width, height) <= 0 or x + width > dimensions[0] or y + height > dimensions[1]:
            raise ValueError('review region is outside the original image')
        url = image['image_service_url'] + '/' + ','.join(map(str, box)) + '/full/0/default.jpg'
        if region['url'] != url or region['local_filename'] != region['id'] + '.jpg' or \
                encoded(region['decoded_dimensions']) != encoded([width, height]) or \
                not re.fullmatch('[0-9a-f]{64}', region['sha256']):
            raise ValueError('region URL, dimensions, filename or fingerprint differs')
        if image_dir is not None:
            raw = (image_dir / region['local_filename']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != region['sha256'] or jpeg_dimensions(raw) != [width, height]:
                raise ValueError('local review-region bytes or dimensions differ')
    if image_dir is not None:
        for filename, sha in retrieval['file_sha256'].items():
            if Path(filename).name != filename or fingerprint(image_dir / filename) != sha:
                raise ValueError('local retrieval input bytes differ')
        if jpeg_dimensions((image_dir / 'f82r.jpg').read_bytes()) != dimensions:
            raise ValueError('local original-image dimensions differ')
    exposure = record['exposure']
    expected_flags = {'plan_saved_locally_before_image_inspection': True,
                      'plan_remotely_published_before_inspection': False,
                      'known_native_reading_before_image_inspection': True,
                      'known_statistical_result_before_selection': True,
                      'image_inspected_in_this_chat': True,
                      'independent_blind_or_human_review': False,
                      'region_displays_native_size': True}
    if any(type(exposure[key]) is not bool or exposure[key] != value for key, value in expected_flags.items()):
        raise ValueError('required local/unblinded exposure declarations differ')
    observation = record['observations']
    if observation['source_row_association']['status'] != 'provisional' or \
            not observation['source_row_association']['basis'] or not observation['endpoint_shape_comparison']['direct_observation'] or \
            observation['endpoint_shape_comparison']['status'] != 'provisional_similarity' or \
            observation['glyph_equivalence_disposition'] != 'unresolved pending independent qualified review' or \
            observation['source_correction'] != 'none':
        raise ValueError('required observation/uncertainty declarations differ')
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path,
                        default=ROOT / 'research/transliteration/boundary_repeat_image_check.json')
    parser.add_argument('--image-dir', type=Path)
    args = parser.parse_args()
    try:
        verify_record(strict_json(args.record.read_bytes()), args.image_dir)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'boundary image metadata failed: {error}\n')
    print('Verified selected unit, all four native endpoint/row records, image references and pixel-region metadata.')
    if args.image_dir:
        print('Original image, retrieval inputs and all local review-region bytes match their pins.')
    print('Visual judgments and glyph equivalence require independent review; this verifier does not certify them.')


if __name__ == '__main__':
    main()
