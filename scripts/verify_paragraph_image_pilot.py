"""Verify image-pilot selection/provenance; does not validate visual judgments."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

try:
    from .annotation_agreement import annotation_report, annotations
    from .audit_transliterations import ROOT, load_sources
    from .token_baselines import paired_sources
except ImportError:
    from annotation_agreement import annotation_report, annotations
    from audit_transliterations import ROOT, load_sources
    from token_baselines import paired_sources


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pilot(record, image_dir=None):
    sources = paired_sources(load_sources())
    audit_path = ROOT / 'research/transliteration/annotation_agreement.json'
    index_path = ROOT / 'research/image-index/canvases.csv'
    if record['annotation_audit_sha256'] != digest(audit_path):
        raise ValueError('annotation audit fingerprint differs')
    if record['image_index_sha256'] != digest(index_path):
        raise ValueError('image index fingerprint differs')
    recomputed = annotation_report(sources)
    if recomputed != json.loads(audit_path.read_text()):
        raise ValueError('annotation audit differs from pinned sources')
    expected_sources = [{key: source[key] for key in ('id', 'url', 'path', 'sha256', 'alphabet')}
                        for source, _ in sources]
    if record['sources'] != expected_sources:
        raise ValueError('pilot source identities differ')
    pages = {row['page'] for row in recomputed['discordant_loci']}
    if any(not re.fullmatch(r'f[0-9]+[rv][1-6]?', page) for page in pages):
        raise ValueError('numeric folio selection rule cannot order this page set')
    selected = sorted(pages, key=lambda page: (int(re.search(r'[0-9]+', page)[0]), page))[:3]
    records = record['records']
    if [row['page'] for row in records] != selected:
        raise ValueError('image pilot pages differ from the fixed selection')
    with index_path.open() as stream:
        index = list(csv.DictReader(stream))
    for row in records:
        page = row['page']
        discordant = [locus['key'] for locus in recomputed['discordant_loci'] if locus['page'] == page]
        if discordant != [row['discordant_key']]:
            raise ValueError(f'{page}: discordant locus coverage differs')
        matches = [canvas for canvas in index if canvas['yale_label'] == page[1:]]
        if len(matches) != 1 or matches[0]['label_class'] != 'exact_single_side_label':
            raise ValueError(f'{page}: standalone canvas is not unique')
        canvas = matches[0]
        expected_image = {key: canvas[key] for key in (
            'canvas_uri', 'image_oid', 'catalog_image_url', 'full_image_url',
            'image_service_url', 'yale_label')}
        if row['image'] != expected_image:
            raise ValueError(f'{page}: image identifiers differ')
        inspection = row['inspection']
        if (inspection['url'] != canvas['image_service_url'] + '/full/!2200,2200/0/default.jpg'
                or inspection['local_filename'] != page + '.jpg'
                or not re.fullmatch(r'[0-9a-f]{64}', inspection['sha256'])):
            raise ValueError(f'{page}: inspection provenance differs')
        contexts = []
        for source, document in sources:
            loci = [locus for locus in document.loci if locus.page == page and locus.present
                    and locus.kind.startswith('P')]
            position = next(i for i, locus in enumerate(loci) if locus.key == row['discordant_key'])
            contexts.append({
                'source_id': source['id'], 'present_generic_p_locus_count': len(loci),
                'source_locators': sorted({locus.locator for locus in loci}),
                'adjacent_context': [{**annotations(locus), 'key': locus.key, 'kind': locus.kind}
                                     for locus in loci[max(0, position - 1):position + 2]],
            })
        if row['source_contexts'] != contexts:
            raise ValueError(f'{page}: source context differs')
        if (not row['direct_observations'] or not row['source_row_association']['basis']
                or row['source_row_association']['status'] != 'provisional'
                or row['paragraph_disposition'] != 'unresolved'
                or not row['reason'] or not row['exposure']['inspected_in_this_chat']):
            raise ValueError(f'{page}: required observation or uncertainty declaration differs')
        if image_dir is not None and digest(image_dir / inspection['local_filename']) != inspection['sha256']:
            raise ValueError(f'{page}: local image fingerprint differs')
    return len(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path,
                        default=ROOT / 'research/transliteration/paragraph_image_pilot.json')
    parser.add_argument('--image-dir', type=Path)
    args = parser.parse_args()
    try:
        count = verify_pilot(json.loads(args.record.read_text()), args.image_dir)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'image pilot verification failed: {error}\n')
    print(f'Verified {count} selected pages, pinned source contexts, and image references.')
    if args.image_dir is not None:
        print('Local image bytes match all recorded fingerprints.')
    print('Visual judgments, row associations, and paragraph divisions require separate review.')


if __name__ == '__main__':
    main()
