"""Verify frozen image-pair records and local fingerprints; never judge pixels."""

import argparse
import json
from pathlib import Path
import re
import subprocess

try:
    from . import select_y_lookup_images as selector
    from .verify_initial_prefix_review import bitmap_dimensions
except ImportError:
    import select_y_lookup_images as selector
    from verify_initial_prefix_review import bitmap_dimensions


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_record(record, selection, root, local_directory=None):
    require(record['analysis_id'] == selection['analysis_id'] == 'y-lookup-image-v1', 'wrong image study')
    for name in ('independent_human_adjudication', 'image_alignment_verified', 'source_corrections_applied',
                 'valid_candidate_holdout', 'previously_unseen'):
        require(record.get(name) is False, 'unsupported verified/correction/exposure flag')
    pairs = selection['selection']['selected_pairs']
    expected = [(pair['locus_key'], pair['chosen_reference']['locus_key'], pair['chosen_reference']['original_slot_zero_based']) for pair in pairs]
    actual = [(case['target_key'], case['reference_key'], case['reference_slot_zero_based']) for case in record['cases']]
    require(actual == expected, 'missing, replaced, reordered or changed pair')
    for case in record['cases']:
        require(type(case['reference_slot_zero_based']) is int
                and case['target_page'] == case['target_key'].rsplit('.', 1)[0]
                and case['reference_page'] == case['reference_key'].rsplit('.', 1)[0],
                'wrong typed slot or source page identity')
        require(case['alignment_status'] in ('single_observer_provisional', 'unresolved'), 'unsupported alignment status')
        require(case['comparison_status'] in ('provisional_broad_correspondence', 'unresolved'), 'unsupported comparison status')
        if case['alignment_status'] == 'unresolved':
            require(case['comparison_status'] == 'unresolved', 'fine comparison despite unresolved alignment')
        require(all(isinstance(case.get(field), str) and case[field].strip() for field in
                    ('target_row_evidence', 'reference_row_evidence', 'target_visible', 'reference_visible', 'comparison', 'alternatives')),
                'missing observation or uncertainty')
        require(bool(case['remaining_uncertainties']), 'missing remaining uncertainties')
    images = selection['selection']['images_by_page']
    resources = record['retrieved_resources']
    require(len({item['name'] for item in resources}) == len(resources), 'duplicate resource name')
    expected_names = {page + '-' + suffix for page in images for suffix in ('whole.jpg', 'info.json', 'context.jpg', 'token.jpg')}
    require(expected_names | {'basic-eva.gif'} == {item['name'] for item in resources}, 'missing or added inspected resource')
    for item in resources:
        require(item['status'] == 'retrieved' and re.fullmatch('[0-9a-f]{64}', item['sha256']), 'invalid resource identity')
        name = item['name']
        if name == 'basic-eva.gif':
            require(item['url'] == 'https://voynich.nu/img/extra/eva01.gif', 'wrong notation reference')
        else:
            page, suffix = name.split('-', 1)
            source = images[page]
            service = source['image_service_url']
            if suffix == 'info.json':
                require(item['url'] == service + '/info.json', 'wrong service metadata')
            elif suffix == 'whole.jpg':
                require(item['url'] == service + '/full/!1600,1600/0/default.jpg', 'wrong whole-page overview')
                w, h = item['pixel_dimensions']
                require(max(w, h) == 1600 and abs(w / h - int(source['image_width']) / int(source['image_height'])) < .001,
                        'wrong overview dimensions')
            else:
                box = item['native_region_xywh']
                require(len(box) == 4 and all(type(x) is int for x in box), 'invalid native region')
                x, y, w, h = box
                require(x >= 0 and y >= 0 and w > 0 and h > 0 and x + w <= int(source['image_width'])
                        and y + h <= int(source['image_height']), 'native region outside source image')
                require(item['url'] == service + '/' + ','.join(map(str, box)) + '/full/0/default.jpg', 'wrong native region URL')
                require(item['pixel_dimensions'] == [w, h], 'native region dimensions changed')
        if local_directory:
            raw = (local_directory / name).read_bytes()
            require(selector.sha(raw) == item['sha256'] and len(raw) == item['bytes'], 'local inspected bytes changed')
            if name.endswith('info.json'):
                metadata = json.loads(raw)
                source = images[name.split('-', 1)[0]]
                require((metadata['width'], metadata['height']) == (int(source['image_width']), int(source['image_height'])),
                        'service native dimensions differ')
            else:
                require(list(bitmap_dimensions(raw)) == item['pixel_dimensions'], 'local bitmap dimensions changed')
    require(all(item['status'] in ('first_request_failed', 'request_failed') and type(item['http_status']) is int
                for item in record['failed_requests']), 'unrecorded request failure status')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-directory', type=Path)
    args = parser.parse_args()
    try:
        root = selector.parent.ROOT
        base = root / selector.BASE
        selection_raw = (base / 'selection.json').read_bytes()
        selection = json.loads(selection_raw)
        require(selection == selector.selection_report(), 'frozen selector no longer reproduces')
        record = json.loads((base / 'image-review.json').read_bytes())
        require(selector.sha(selection_raw) == record['selection_sha256'], 'selection bytes changed')
        require(selector.sha((base / 'PLAN.md').read_bytes()) == record['plan_sha256'], 'image plan bytes changed')
        for field, paths in (('plan_commit', ('PLAN.md', 'inputs.json')),
                             ('selection_commit', ('selection.json', 'PLAN.md', 'inputs.json'))):
            commit = record[field]
            require(re.fullmatch('[0-9a-f]{40}', commit), 'invalid freeze commit')
            for path in paths:
                old = subprocess.check_output(['git', 'show', commit + ':' + selector.BASE + '/' + path], cwd=root)
                require(old == (base / path).read_bytes(), 'registered image input differs from committed bytes')
        require(subprocess.run(['git', 'merge-base', '--is-ancestor', record['plan_commit'], record['selection_commit']],
                               cwd=root, capture_output=True).returncode == 0, 'plan not in frozen selection ancestry')
        verify_record(record, selection, root, args.local_directory)
        print('Frozen pairs, provisional observations, URL bounds and identities verified; visual correctness is not certified.')
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'image-pair record failed: {error}\n')


if __name__ == '__main__':
    main()
