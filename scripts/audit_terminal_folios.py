"""Audit terminal source/image labels without inferring a historical folio alias.

Source record counts are not physical writing-row counts. No images are fetched.
"""

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re

try:
    from .audit_pilot_transcriptions import page_summary
    from .audit_transliterations import ROOT, load_sources
    from .check_folio_aliases import lookup, read_index
    from .ivtff import without_free_comments
except ImportError:
    from audit_pilot_transcriptions import page_summary
    from audit_transliterations import ROOT, load_sources
    from check_folio_aliases import lookup, read_index
    from ivtff import without_free_comments


SOURCE_IDS = ('ZL3b', 'IT2a', 'GC2a', 'RF1b-full', 'RF1b-basic')
TARGETS = (('116r', 'f116r'), ('116v', 'f116v'), ('[Back flyleaf recto]', None))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_page(document, page):
    summary = page_summary(document, page)
    if not summary['header_present']:
        state = 'header_absent'
        require(not summary['present_loci'], 'records exist without their page header')
    elif not summary['present_loci']:
        state = 'header_without_present_loci'
    else:
        state = 'present_loci'
    records = [locus for locus in document.loci if locus.page == page and locus.present]
    require(len({locus.key for locus in records}) == len(records), 'duplicate terminal locus key')
    result = {
        **summary, 'presence_state': state,
        'present_generic_p_loci': sum(locus.kind.startswith('P') for locus in records),
        'present_p0_p1_loci': sum(locus.kind in {'P0', 'P1'} for locus in records),
        'record_metadata': [{'locus_identifier': locus.identifier,
                             'source_line_number': locus.line_number,
                             'kind': locus.kind, 'locator': locus.locator}
                            for locus in records],
    }
    if page == 'f116v':
        result['native_payload_records'] = [{
            'locus_identifier': locus.identifier,
            'native_payload_outside_free_comments': without_free_comments(locus.text),
            'free_comments_present': locus.text != without_free_comments(locus.text),
            'effective_source_variables': locus.variables,
        } for locus in records]
    return result


def build_report(sources, canvas_rows, alias):
    require(Counter(source['id'] for source, _ in sources) == Counter(SOURCE_IDS),
            'require exactly the five declared source editions')
    by_id = {source['id']: (source, document) for source, document in sources}
    require(alias.get('source_scheme') == 'yale_legacy_ms408_catalog' and
            alias.get('source_label') == '117v' and alias.get('status') == 'unresolved' and
            alias.get('mapping_allowed') is False and alias.get('target') is None,
            'legacy alias changed; this unresolved-intake protocol requires a new review')
    entries = []
    for label, page in TARGETS:
        matches = [row for row in canvas_rows if row['yale_label'] == label]
        require(len(matches) == 1, 'terminal image label is absent or nonunique')
        row = matches[0]
        expected_class = 'exact_single_side_label' if page else 'non_numbered_view'
        require(row['label_class'] == expected_class and
                row['has_partial_marker'] == 'False' and
                row['has_multiple_explicit_sides'] == 'False',
                'terminal label changed to a partial, combined, or unsupported view')
        require(row['explicit_folio_sides'] == (label if page else ''),
                'terminal explicit-side metadata differs')
        editions = []
        if page is not None:
            for identifier in SOURCE_IDS:
                source, document = by_id[identifier]
                editions.append({'source_id': identifier, 'sha256': source['sha256'],
                                 **source_page(document, page)})
        entries.append({
            'yale_label': label, 'source_page_id': page,
            'image': {field: row[field] for field in (
                'canvas_uri', 'image_oid', 'catalog_image_url', 'full_image_url',
                'image_service_url', 'image_width', 'image_height')},
            'editions': editions,
            'image_text_alignment': 'not_verified',
            'unnumbered_flyleaf_has_no_assigned_native_page': page is None,
        })
    return {
        'schema_version': 1, 'method': 'terminal-folio source intake v1',
        'scope': 'Exact source/image labels only; no row alignment, historical alias, script interpretation, or translation is verified.',
        'sources': [{field: by_id[identifier][0][field]
                     for field in ('id', 'url', 'path', 'sha256', 'alphabet')}
                    for identifier in SOURCE_IDS],
        'entries': entries,
        'legacy_117v_lookup': alias,
        'f117v_source_controls': [{
            'source_id': identifier, **source_page(by_id[identifier][1], 'f117v')}
            for identifier in SOURCE_IDS],
        'limits': [
            'Absent source headers describe edition coverage, not physically missing manuscript pages.',
            'One stored Lx locus is not a complete transcription of all visible writing rows.',
            'RF full/basic are related derived exports, not independent manuscript replications.',
            'The unnumbered flyleaf is not assigned a 117 folio label.',
        ],
    }


def audit(root=ROOT):
    paths = {
        'source_catalog': 'data/transliterations.json',
        'canvas_index': 'research/image-index/canvases.csv',
        'index_audit': 'research/image-index/audit.json',
        'folio_aliases': 'research/folio-aliases/decisions.json',
    }
    raw = {name: (root / path).read_bytes() for name, path in paths.items()}
    registry = json.loads(raw['folio_aliases'])
    manifest_sha256 = json.loads(raw['index_audit'])['manifest_sha256']
    alias = lookup(registry, 'yale_legacy_ms408_catalog', '117v',
                   index=read_index(raw['canvas_index']), manifest_sha256=manifest_sha256)
    rows = list(csv.DictReader(io.StringIO(raw['canvas_index'].decode('utf-8'))))
    report = build_report(load_sources(root), rows, alias)
    report['inputs'] = {name: {'path': path, 'sha256': hashlib.sha256(raw[name]).hexdigest()}
                        for name, path in paths.items()}
    report['manifest_sha256'] = manifest_sha256
    return report


def verify_observations(record, report, report_bytes):
    """Validate metadata declarations, never visual row counts or glyph readings."""
    require(record.get('schema_version') == 1 and
            record.get('historical_alias_verified') is False and
            record.get('new_voynich_glyph_reading_or_translation') is False,
            'terminal observation must retain the unverified alias and reading scope')
    require(record.get('intake_report_sha256') == hashlib.sha256(report_bytes).hexdigest(),
            'observations bound to a different intake report')
    require([item['yale_label'] for item in record['records']] ==
            [entry['yale_label'] for entry in report['entries']],
            'observations omit, duplicate or change terminal views')
    anchor_review = record.get('terminal_native_locus_review_performed', False)
    require(type(anchor_review) is bool, 'native-locus review flag must be boolean')
    for item, entry in zip(record['records'], report['entries']):
        require(item['source_page_id'] == entry['source_page_id'] and
                item['image_metadata'] == entry['image'], 'observation image/page metadata differ')
        require(item.get('observation_status') == 'single_observer' and
                isinstance(item.get('direct_observations'), list) and item['direct_observations'] and
                all(isinstance(text, str) and text for text in item['direct_observations']),
                'missing observations or unsupported verification status')
        target = entry['image']
        images = item['inspected_images']
        require(len(images) >= (2 if entry['source_page_id'] else 1),
                'missing whole-image or detail-region inspection')
        require('region_xywh_full_image_pixels' not in images[0], 'whole-image context must come first')
        for image in images:
            require(isinstance(image.get('sha256'), str) and
                    re.fullmatch('[0-9a-f]{64}', image['sha256']), 'invalid inspection fingerprint')
            region = image.get('region_xywh_full_image_pixels')
            if region is None:
                require(image['url'] == target['full_image_url'] and
                        (image['pixel_width'], image['pixel_height']) ==
                        (int(target['image_width']), int(target['image_height'])),
                        'whole-image URL or dimensions differ from the index')
            else:
                require(isinstance(region, list) and len(region) == 4 and
                        all(type(value) is int for value in region), 'invalid native region')
                x, y, width, height = region
                require(x >= 0 and y >= 0 and width > 0 and height > 0 and
                        x + width <= int(target['image_width']) and
                        y + height <= int(target['image_height']), 'region exceeds indexed image')
                require((image['pixel_width'], image['pixel_height']) == (width, height),
                        'region dimensions do not match its native coordinates')
                require(image['url'] == target['image_service_url'] + '/' +
                        ','.join(map(str, region)) + '/full/0/default.jpg',
                        'region URL does not match its coordinates and image service')
        anchor = item.get('native_locus_review_anchor')
        require((anchor is not None) == (anchor_review and entry['source_page_id'] == 'f116v'),
                'native-locus review must retain exactly the terminal verso anchor')
        if anchor is not None:
            verify_native_anchor(anchor, entry, report['sources'], images)


def verify_native_anchor(anchor, entry, sources, images):
    """Check the provisional declaration and source contexts, never glyph identity."""
    require(anchor.get('association_status') == 'provisional' and
            anchor.get('usable_as_verified_corpus_join') is False and
            anchor.get('glyph_reading_verified') is False and
            anchor.get('glyph_correction_proposed') is False and
            anchor.get('source_record_is_not_physical_row_number') is True,
            'terminal anchor must retain provisional association and unverified reading scope')
    require(re.fullmatch('[0-9a-f]{40}', anchor.get('plan_commit', '')) is not None,
            'missing committed native-anchor plan identity')
    require(anchor.get('native_locus_key') == 'f116v.1', 'changed terminal native-locus key')
    catalog = {source['id']: source for source in sources}
    expected, absent = [], []
    for edition in entry['editions']:
        if not edition['header_present']:
            require(not edition['record_metadata'], 'absent page has native records')
            absent.append(edition['source_id'])
            continue
        require(len(edition['record_metadata']) == len(edition['native_payload_records']) == 1,
                'terminal native-anchor protocol requires a sole record')
        metadata, payload = edition['record_metadata'][0], edition['native_payload_records'][0]
        require(metadata['locus_identifier'] == payload['locus_identifier'] == 'f116v.1,@Lx' and
                metadata['kind'] == 'Lx', 'terminal native-anchor subtype or identifier changed')
        source = catalog[edition['source_id']]
        expected.append({
            'source_id': edition['source_id'], 'sha256': source['sha256'],
            'alphabet': source['alphabet'], 'url': source['url'],
            'locus_identifier': metadata['locus_identifier'],
            'source_file_line': metadata['source_line_number'],
            'kind': metadata['kind'], 'locator': metadata['locator'],
            'native_payload_outside_free_comments': payload['native_payload_outside_free_comments'],
            'free_comments_present': payload['free_comments_present'],
        })
    require(anchor.get('source_contexts') == expected and
            anchor.get('absent_source_headers') == absent,
            'native-anchor contexts or absent-edition headers differ from the pinned intake')
    require(len(images) == 4 and anchor.get('review_region_image_indices') == [2, 3],
            'native anchor requires the original overview and writing region plus two review windows')
    upper, broad, narrow = [image.get('region_xywh_full_image_pixels') for image in images[1:]]
    require(all(region is not None for region in (upper, broad, narrow)),
            'native anchor requires native-pixel regions')
    for outer, inner in ((upper, broad), (broad, narrow)):
        x, y, width, height = outer
        ix, iy, iw, ih = inner
        require(x <= ix and y <= iy and ix + iw <= x + width and iy + ih <= y + height and
                iw * ih < width * height, 'native review window is not a smaller contained region')
    require(isinstance(anchor.get('physical_position_description'), str) and
            anchor['physical_position_description'], 'missing physical-position description')
    for field in ('direct_observations', 'association_basis', 'unresolved_readings'):
        value = anchor.get(field)
        require(isinstance(value, list) and value and
                all(isinstance(text, str) and text for text in value),
                'missing association evidence or unresolved reading limits')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    parser.add_argument('--observations', type=Path, help='check observation metadata against --check')
    args = parser.parse_args()
    try:
        report = audit()
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed terminal intake differs from recomputation')
        if args.observations:
            require(args.check is not None, 'observation verification requires --check')
            verify_observations(json.loads(args.observations.read_text()), report, args.check.read_bytes())
        if args.output:
            args.output.write_text(json.dumps(report, indent=2) + '\n')
        elif not args.check:
            print(json.dumps(report, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'terminal intake failed: {error}\n')
    if args.check:
        print('Pinned terminal source/image intake verified; no historical alias or physical row count is certified.')
    if args.observations:
        print('Terminal observation metadata and region bounds verified; visual judgments require separate review.')


if __name__ == '__main__':
    main()
