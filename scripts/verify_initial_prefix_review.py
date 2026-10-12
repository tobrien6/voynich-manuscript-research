"""Verify source/image metadata for the provisional initial-prefix review.

This does not certify row alignment, shape judgments, or source corrections.
Optional local image bindings verify inspected bytes and bitmap dimensions.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re

try:
    from .audit_transliterations import ROOT, load_sources
    from .eva_token_adapter import adapt
    from .select_initial_prefix_images import selection_report
    from .token_baselines import paired_sources, retain, tokenize
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from eva_token_adapter import adapt
    from select_initial_prefix_images import selection_report
    from token_baselines import paired_sources, retain, tokenize


REVIEW = ROOT / 'research/transliteration/initial_prefix_review.json'
SELECTION = ROOT / 'research/transliteration/initial_prefix_selection.json'
STATUSES = {'unresolved', 'single_observer_provisional_preference'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reference_sources():
    sources = paired_sources(load_sources())
    loci = {source['id']: {locus.key: locus for locus in document.loci
                          if locus.page == 'f78r' and locus.present and
                          locus.kind == 'P0' and locus.locator in {'@', '+', '*'}}
            for source, document in sources}
    adapted = {source['id']: {record['locus_key']: record for record in
                             adapt(source, document, 'split', ('P0',))}
               for source, document in sources}
    common = set.intersection(*(set(mapping) for mapping in loci.values()))
    candidates = {'l': [], 'q': []}
    for key in sorted(common, key=lambda value: int(value.rsplit('.', 1)[1])):
        first = []
        for source, _ in sources:
            for spacing in ('split', 'join'):
                tokens = tokenize(loci[source['id']][key].text, spacing)
                if (tokens and retain(tokens[0], 'exclude') and
                        re.fullmatch('[A-Za-z]+', tokens[0].value)):
                    first.append(tokens[0].value)
        if len(first) == 4 and len(set(first)) == 1:
            for prefix in candidates:
                if first[0].startswith(prefix):
                    candidates[prefix].append(key)
    require(all(candidates.values()), 'missing declared l/q reference class')
    references = []
    for prefix in ('l', 'q'):
        key = candidates[prefix][0]
        references.append({
            'reference_prefix': prefix, 'locus_key': key,
            'sources': [{
                'id': source['id'], 'sha256': source['sha256'],
                'locus_identifier': loci[source['id']][key].identifier,
                'source_line_number': loci[source['id']][key].line_number,
                'first_token': tokenize(loci[source['id']][key].text, 'split')[0].value,
                'original_locus_text': loci[source['id']][key].text,
                'whole_locus_adapter_eligible': adapted[source['id']][key]['eligible'],
                'whole_locus_exclusion_reasons': adapted[source['id']][key]['exclusion_reasons'],
            } for source, _ in sources],
        })
    return candidates, references


def images_in(review):
    yield review['notation_reference']
    for case in review['cases']:
        yield from case['inspected_images']
    for reference in review['same_page_comparison']['references']:
        yield from reference['inspected_images']


def check_image(image, target=None):
    require(type(image.get('pixel_width')) is int and image['pixel_width'] > 0 and
            type(image.get('pixel_height')) is int and image['pixel_height'] > 0,
            'invalid image dimensions')
    require(isinstance(image.get('sha256'), str) and
            re.fullmatch('[0-9a-f]{64}', image['sha256']), 'invalid inspection hash')
    if target is None:
        require(image.get('url') == 'https://voynich.nu/img/extra/eva01.gif',
                'unexpected notation reference image')
        return
    region = image.get('region_xywh_full_image_pixels')
    if region is None:
        require(image.get('url') == target['full_image_url'], 'wrong whole-image URL')
        require((image['pixel_width'], image['pixel_height']) ==
                (int(target['image_width']), int(target['image_height'])),
                'whole-image dimensions differ from canvas index')
    else:
        require(isinstance(region, list) and len(region) == 4 and
                all(type(value) is int for value in region), 'invalid region coordinates')
        x, y, width, height = region
        require(x >= 0 and y >= 0 and width > 0 and height > 0 and
                x + width <= int(target['image_width']) and
                y + height <= int(target['image_height']), 'region exceeds indexed image')
        require((width, height) == (image['pixel_width'], image['pixel_height']),
                'native region dimensions differ from coordinates')
        expected = target['image_service_url'] + '/' + ','.join(map(str, region)) + '/full/0/default.jpg'
        require(image.get('url') == expected, 'region URL differs from its coordinates')


def verify_review(review, selection, selection_bytes):
    require(review.get('schema_version') == 2, 'unsupported image-review version')
    require(selection == selection_report(), 'selection differs from pinned-source recomputation')
    require(review.get('selection_report_sha256') == hashlib.sha256(selection_bytes).hexdigest(),
            'review bound to a different selection file')
    require(review.get('may_apply_as_source_correction') is False,
            'this provisional review cannot authorize source corrections')
    selected = selection['selection']['selected_locus_keys']
    require([case['locus_key'] for case in review['cases']] == selected,
            'review omits, duplicates or changes selected cases')
    candidates = {case['locus_key']: case for case in selection['selection']['candidates']}
    check_image(review['notation_reference'])
    for case in review['cases']:
        require(case['selection_case'] == candidates[case['locus_key']],
                'review case source/image metadata differ from selection')
        require(case.get('row_alignment_status') == 'single_observer_provisional',
                'row alignment cannot be asserted as verified by this review')
        require(case.get('interpretation_status') in STATUSES, 'unsupported interpretation status')
        if case['interpretation_status'] == 'unresolved':
            require(case.get('preferred_first_slot_representation') is None,
                    'unresolved case cannot adopt a representation')
        else:
            require(isinstance(case.get('preferred_first_slot_representation'), str) and
                    bool(case['preferred_first_slot_representation']), 'missing provisional preference')
        require(len(case['inspected_images']) >= 3, 'missing whole/context/initial inspections')
        target = case['selection_case']['image']
        require('region_xywh_full_image_pixels' not in case['inspected_images'][0],
                'first inspection must preserve the whole-image context')
        for image in case['inspected_images']:
            check_image(image, target)
    expected_candidates, expected_references = reference_sources()
    comparison = review['same_page_comparison']
    require(comparison['candidate_locus_keys_by_literal_prefix'] == expected_candidates,
            'reference candidate list differs from fixed source rule')
    references = comparison['references']
    require(len(references) == len(expected_references), 'missing or extra comparison reference')
    target = candidates['f78r.21']['image']
    for reference, expected in zip(references, expected_references):
        require({key: reference[key] for key in expected} == expected,
                'selected reference or source uncertainty differs from pinned sources')
        require(reference.get('row_alignment_status') == 'single_observer_provisional',
                'comparison reference cannot assert verified row alignment')
        require(len(reference['inspected_images']) >= 2, 'missing reference context/initial inspection')
        for image in reference['inspected_images']:
            require('region_xywh_full_image_pixels' in image, 'reference must link an explicit region')
            check_image(image, target)
    urls = [image['url'] for image in images_in(review)]
    require(len(urls) == len(set(urls)), 'duplicate image inspection URL')


def bitmap_dimensions(data):
    """Read GIF logical size or JPEG SOF dimensions; do not decode pixels."""
    if data[:6] in (b'GIF87a', b'GIF89a') and len(data) >= 10:
        return int.from_bytes(data[6:8], 'little'), int.from_bytes(data[8:10], 'little')
    require(data.startswith(b'\xff\xd8'), 'expected a recorded GIF or JPEG bitmap')
    index = 2
    frames = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while index < len(data):
        require(data[index] == 0xFF, 'invalid JPEG marker boundary')
        while index < len(data) and data[index] == 0xFF:
            index += 1
        require(index < len(data), 'truncated JPEG marker')
        marker = data[index]
        index += 1
        if marker in {0x01, *range(0xD0, 0xD9)}:
            continue
        require(marker not in {0xD9, 0xDA} and index + 2 <= len(data),
                'JPEG frame dimensions are absent or truncated')
        length = int.from_bytes(data[index:index + 2], 'big')
        require(length >= 2 and index + length <= len(data), 'truncated JPEG segment')
        if marker in frames:
            require(length >= 8, 'short JPEG frame header')
            return (int.from_bytes(data[index + 5:index + 7], 'big'),
                    int.from_bytes(data[index + 3:index + 5], 'big'))
        index += length
    raise ValueError('JPEG frame dimensions not found')


def check_local_images(review, bindings):
    known = {image['url']: image for image in images_in(review)}
    seen = set()
    for binding in bindings:
        url, separator, path = binding.partition('=')
        require(separator and url in known and url not in seen, 'unknown or duplicate local image binding')
        seen.add(url)
        data = Path(path).read_bytes()
        image = known[url]
        require(hashlib.sha256(data).hexdigest() == image['sha256'], 'local inspected image bytes differ')
        require(bitmap_dimensions(data) == (image['pixel_width'], image['pixel_height']),
                'local bitmap dimensions differ from inspection record')
    return len(seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, default=REVIEW)
    parser.add_argument('--selection', type=Path, default=SELECTION)
    parser.add_argument('--image-file', action='append', default=[], metavar='URL=PATH',
                        help='Repeat for optional local inspected-file hash/dimension checks')
    args = parser.parse_args()
    try:
        selection_bytes = args.selection.read_bytes()
        selection = json.loads(selection_bytes)
        review = json.loads(args.review.read_text())
        verify_review(review, selection, selection_bytes)
        checked = check_local_images(review, args.image_file)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'initial-prefix review metadata failed: {error}\n')
    print(f'Source/reference metadata and provisional-only flags verified; {checked} local image files checked. Visual judgments are not certified.')


if __name__ == '__main__':
    main()
