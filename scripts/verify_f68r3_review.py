"""Verify the fixed f68r3 packet/request identities; never certify visual judgments."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

try:
    from .build_f68r3_review import ROOT, PLAN, build
    from .verify_initial_prefix_review import bitmap_dimensions
except ImportError:
    from build_f68r3_review import ROOT, PLAN, build
    from verify_initial_prefix_review import bitmap_dimensions


BASE = ROOT / 'research/panel-regions'
PACKET = BASE / 'f68r3-native-review.json'
REVIEW = BASE / 'f68r3-image-review.json'
PARENT = BASE / 'f68r-proposal.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def recorded_dimensions(raw):
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):
        require(len(raw) >= 33 and int.from_bytes(raw[8:12], 'big') == 13 and raw[12:16] == b'IHDR',
                'invalid recorded PNG dimension header')
        size = (int.from_bytes(raw[16:20], 'big'), int.from_bytes(raw[20:24], 'big'))
        require(min(size) > 0, 'invalid recorded PNG dimensions')
        return size
    return bitmap_dimensions(raw)


def validate_metadata(record, packet, parent):
    require(record['schema_version'] == 1 and record['method'] == 'fixed f68r3 first-last radial inspection v1',
            'unsupported review contract')
    require(record['usable_as_verified_corpus_join'] is False and record['apply_to_statistics'] is False and
            record['blind'] is False and record['glyph_alignment_status'] == 'pending' and
            record['independent_review_status'] == 'pending', 'unverified review scope was promoted')
    for name in ('image_oid', 'canvas_uri', 'dependency_group'):
        require(record[name] == packet[name] == parent[name], 'carrier/dependency identity changed')
    require(record['native_image_dimensions'] == [parent['original_image_width'], parent['original_image_height']],
            'native image dimensions changed')
    width, height = record['native_image_dimensions']
    require([item['locus_key'] for item in record['attempts']] == packet['anchor_attempts'] == ['f68r3.2', 'f68r3.9'],
            'fixed first/last anchor coverage changed')
    other = [row['locus_key'] for row in packet['records'] if not row['selected_anchor_attempt']]
    require(record['unreviewed_locus_keys'] == other and record['source_packet_coverage'] ==
            {'locations': 22, 'anchor_attempts': 2, 'other_locations_glyph_unreviewed': 20, 'present_p0_locations': 0},
            'complete source packet or unreviewed coverage changed')
    roles = ['specification', 'service_metadata', 'overview', 'right_drawing', 'first_anchor', 'last_anchor']
    require([asset['role'] for asset in record['assets']] == roles, 'planned assets missing, duplicated or substituted')
    for asset in record['assets']:
        filename = asset['local_filename']
        require(re.fullmatch(r'[A-Za-z0-9.-]+', filename) is not None and filename not in ('.', '..'), 'unsafe local asset name')
        require(re.fullmatch('[0-9a-f]{64}', asset['sha256']) is not None and
                type(asset['bytes']) is int and asset['bytes'] > 0 and asset['http_status'] == 200,
                'invalid successful asset receipt')
        if asset['role'] == 'specification':
            require(asset['url'] == parent['naming_reference']['url'] and
                    asset['sha256'] == parent['naming_reference']['sha256'] == record['specification']['sha256'],
                    'specification identity changed')
        elif asset['role'] == 'service_metadata':
            require(asset['url'] == 'https://collections.library.yale.edu/iiif/2/1006196/info.json', 'service metadata URL changed')
        else:
            require(asset['rotation_degrees'] == 0, 'unrecorded image rotation')
            prefix = 'https://collections.library.yale.edu/iiif/2/1006196/'
            rect = asset['native_region']
            if asset['role'] == 'overview':
                require(rect is None and asset['url'] == prefix + 'full/!2400,2400/0/default.jpg' and
                        asset['pixel_dimensions'] == [2400, 1149] and asset['sha256'] == parent['inspection_image_sha256'],
                        'whole-carrier overview identity changed')
            else:
                require(isinstance(rect, list) and len(rect) == 4 and all(type(value) is int for value in rect), 'invalid native rectangle')
                x, y, w, h = rect
                require(x >= 0 and y >= 0 and w > 0 and h > 0 and x + w <= width and y + h <= height,
                        'inspection window exceeds the native image')
                require(asset['url'] == prefix + ','.join(map(str, rect)) + '/full/0/default.jpg' and
                        asset['pixel_dimensions'] == [w, h], 'native request/dimension mismatch')
    for attempt, role in zip(record['attempts'], ['first_anchor', 'last_anchor'], strict=True):
        original = next(row for row in packet['records'] if row['locus_key'] == attempt['locus_key'])
        require(attempt['asset_role'] == role and attempt['native_kind'] == original['native_kind'] == 'Ri' and
                attempt['source_native_text_identical'] is original['native_record_text_identical'] and
                attempt['association_status'] in ('provisional_compatible', 'unlocated', 'contradicted') and
                attempt['glyph_alignment_status'] == 'pending' and attempt['word_boundary_status'] == 'unresolved',
                'anchor source identity or provisional scope changed')
    require(record['failed_requests'] == [], 'this saved successful request set changed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-directory', type=Path)
    args = parser.parse_args()
    try:
        packet_raw, review_raw = PACKET.read_bytes(), REVIEW.read_bytes()
        packet, record = json.loads(packet_raw), json.loads(review_raw)
        require(packet == build(), 'complete source packet no longer reproduces')
        require(hashlib.sha256(packet_raw).hexdigest() == record['source_packet_sha256'] and
                hashlib.sha256((ROOT / PLAN).read_bytes()).hexdigest() == record['plan_sha256'], 'packet/plan pin changed')
        require(record['source_packet_path'] == PACKET.relative_to(ROOT).as_posix(), 'source packet path changed')
        for field, name in (('plan_commit', PLAN), ('source_packet_commit', PACKET.relative_to(ROOT).as_posix())):
            commit = record[field]
            require(re.fullmatch('[0-9a-f]{40}', commit) is not None, 'invalid freeze commit')
            require(subprocess.check_output(['git', 'show', commit + ':' + name], cwd=ROOT) == (ROOT / name).read_bytes(),
                    'registered source/plan bytes differ from public freeze')
        validate_metadata(record, packet, json.loads(PARENT.read_bytes()))
        if args.local_directory:
            for asset in record['assets'] + record['specification']['local_page_renders']:
                name = asset['local_filename']
                require(re.fullmatch(r'[A-Za-z0-9.-]+', name) is not None and name not in ('.', '..'), 'unsafe local asset name')
                raw = (args.local_directory / name).read_bytes()
                require(len(raw) == asset['bytes'] and hashlib.sha256(raw).hexdigest() == asset['sha256'], 'local asset bytes differ')
                if 'pixel_dimensions' in asset:
                    require(list(recorded_dimensions(raw)) == asset['pixel_dimensions'], 'local bitmap dimensions differ')
                elif asset.get('role') == 'service_metadata':
                    metadata = json.loads(raw)
                    require([metadata['width'], metadata['height']] == record['native_image_dimensions'], 'native service dimensions differ')
        print('Complete native packet, fixed attempts, public freeze and image metadata verify; visual/glyph judgments remain provisional.')
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'f68r3 review verification failed: {error}\n')


if __name__ == '__main__':
    main()
