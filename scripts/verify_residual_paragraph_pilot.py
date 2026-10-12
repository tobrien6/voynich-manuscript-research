"""Check residual image-pilot source provenance; visual judgments need review."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

try:
    from .annotation_agreement import annotations
    from .audit_transliterations import ROOT, load_sources
    from .paragraph_context_audit import context_report
    from .token_baselines import paired_sources
except ImportError:
    from annotation_agreement import annotations
    from audit_transliterations import ROOT, load_sources
    from paragraph_context_audit import context_report
    from token_baselines import paired_sources


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_residual_pilot(record, image_dir=None):
    if record['schema_version'] != 1 or record['method'] != 'three-page residual paragraph-end image pilot v1':
        raise ValueError('unsupported residual pilot format')
    paired = paired_sources(load_sources())
    audit_path = ROOT / 'research/transliteration/generic_p_context.json'
    index_path = ROOT / 'research/image-index/canvases.csv'
    if record['generic_p_audit_sha256'] != fingerprint(audit_path):
        raise ValueError('generic-P audit fingerprint differs')
    if record['image_index_sha256'] != fingerprint(index_path):
        raise ValueError('image index fingerprint differs')
    audit = context_report(paired)
    if audit != json.loads(audit_path.read_text()):
        raise ValueError('generic-P audit differs from pinned sources')
    if record['sources'] != audit['sources']:
        raise ValueError('pilot source identities differ')
    residual = [context for context in audit['shared_p0_end_disagreement_contexts']
                if context['following_centered_locus_is_separate_paragraph_in'] is None]
    pages = {context['current']['page'] for context in residual}
    if any(not re.fullmatch(r'f[0-9]+[rv][1-6]?', page) for page in pages):
        raise ValueError('numeric folio selection cannot order this page set')
    selected = sorted(pages, key=lambda page: (int(re.search(r'[0-9]+', page)[0]), page))[:3]
    if [row['page'] for row in record['records']] != selected:
        raise ValueError('residual pilot pages differ from fixed selection')
    with index_path.open() as stream:
        canvases = list(csv.DictReader(stream))
    count = 0
    for row in record['records']:
        page = row['page']
        expected_contexts = [context for context in residual if context['current']['page'] == page]
        if [context['source_context'] for context in row['contexts']] != expected_contexts:
            raise ValueError(f'{page}: residual context coverage or annotations differ')
        expected_page_sources = []
        for source, document in paired:
            loci = [locus for locus in document.loci if locus.page == page and locus.present
                    and locus.kind.startswith('P')]
            expected_page_sources.append({
                'source_id': source['id'], 'present_generic_p_locus_count': len(loci),
                'loci': [{**annotations(locus), 'key': locus.key, 'kind': locus.kind} for locus in loci],
            })
        if row['source_page_annotations'] != expected_page_sources:
            raise ValueError(f'{page}: complete generic-P page annotations differ')
        matches = [canvas for canvas in canvases if canvas['yale_label'] == page[1:]]
        if len(matches) != 1 or matches[0]['label_class'] != 'exact_single_side_label':
            raise ValueError(f'{page}: exact standalone image is not unique')
        canvas = matches[0]
        expected_image = {key: canvas[key] for key in (
            'canvas_uri', 'image_oid', 'catalog_image_url', 'full_image_url',
            'image_service_url', 'yale_label')}
        if row['image'] != expected_image:
            raise ValueError(f'{page}: image references differ')
        inspection = row['inspection']
        if (inspection['url'] != canvas['image_service_url'] + '/full/!2200,2200/0/default.jpg'
                or inspection['local_filename'] != page + '.jpg'
                or not re.fullmatch(r'[0-9a-f]{64}', inspection['sha256'])):
            raise ValueError(f'{page}: inspected image provenance differs')
        if (not row['direct_observations'] or not row['review_status']
                or not row['exposure']['inspected_in_this_chat']
                or type(row['observed_horizontal_row_count']) is not int
                or row['observed_horizontal_row_count'] < 1):
            raise ValueError(f'{page}: required observation declarations are absent')
        for context in row['contexts']:
            if (not context['direct_observation'] or not context['reason']
                    or context['source_row_association']['status'] != 'provisional'
                    or not context['source_row_association']['basis']
                    or context['paragraph_disposition'] != 'unresolved'):
                raise ValueError(f'{page}: required uncertainty declarations differ')
            count += 1
        if image_dir is not None and fingerprint(image_dir / inspection['local_filename']) != inspection['sha256']:
            raise ValueError(f'{page}: local image fingerprint differs')
    return len(selected), count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path,
                        default=ROOT / 'research/transliteration/residual_paragraph_image_pilot.json')
    parser.add_argument('--image-dir', type=Path)
    args = parser.parse_args()
    try:
        pages, contexts = verify_residual_pilot(json.loads(args.record.read_text()), args.image_dir)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'residual pilot verification failed: {error}\n')
    print(f'Verified {pages} selected pages and all {contexts} residual source contexts.')
    if args.image_dir is not None:
        print('All local image bytes match their recorded fingerprints.')
    print('Image judgments, row associations, and paragraph divisions require separate review.')


if __name__ == '__main__':
    main()
