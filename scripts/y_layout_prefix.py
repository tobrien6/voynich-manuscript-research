"""Planned exploratory y-removal lookup diagnostic; never held-out validation."""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

try:
    from .audit_transliterations import ROOT, load_sources
    from .audit_transcription_images import make_report, page_reference
    from .ivtff import TAG, without_free_comments
    from .locus_positions import prepare_rows
    from .prefix_strata import paragraph_start, select_locations
    from .section_strata import selected_records
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from audit_transcription_images import make_report, page_reference
    from ivtff import TAG, without_free_comments
    from locus_positions import prepare_rows
    from prefix_strata import paragraph_start, select_locations
    from section_strata import selected_records
    from token_baselines import paired_sources


BASE = 'research/hypotheses/y-layout-prefix-v1'
SEED = 'y-layout-prefix-v1-2026-10-11'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def key_digest(values):
    return sha(('\n'.join(sorted(values)) + '\n').encode('ascii'))


def page_families(page):
    reference = page_reference(page)
    if not reference['folio_sides']:
        raise ValueError(f'unsupported coarse page reference: {page}')
    return set(side[:-1] for side in reference['folio_sides'])


def selection(sources):
    paired = paired_sources(sources)
    shared_p0, regular = select_locations(paired)
    records = [selected_records(document, regular) for _, document in paired]
    indexed = [{locus.key: locus for locus in loci} for loci in records]
    starts = {key for key in regular if any(paragraph_start(index[key]) for index in indexed)}
    selected = regular - starts
    if not selected:
        raise ValueError('no jointly non-start regular P0 locations')
    return paired, selected, {
        'shared_present_p0_count': len(shared_p0), 'shared_regular_p0_count': len(regular),
        'excluded_nonregular_keys': sorted(shared_p0 - regular),
        'excluded_source_paragraph_start_keys': sorted(starts),
        'selected_location_count': len(selected), 'sorted_selected_keys_sha256': key_digest(selected),
    }


def repetition_body(locus):
    body = TAG.sub('', without_free_comments(locus.text)).replace('<%>', '').replace('<$>', '')
    body = ''.join(body.split())
    return body if body.count('.') >= 2 and not any(c in body for c in '?[]') else None


def build_partition(sources, image_report):
    """Construct dependencies and a deterministic partition without fitting a vocabulary."""
    paired, selected, selected_audit = selection(sources)
    parents = {}

    def find(number):
        parents.setdefault(number, number)
        if parents[number] != number:
            parents[number] = find(parents[number])
        return parents[number]

    def connect(numbers):
        numbers = sorted(set(numbers), key=int)
        for number in numbers:
            parents[find(number)] = find(numbers[0])

    for component in image_report['dependency_components']:
        connect(component['folio_ids'])
    repeated_edges = []
    for source, document in paired:
        bodies = defaultdict(set)
        for locus in document.loci:
            if locus.present and locus.kind == 'P0':
                body = repetition_body(locus)
                if body is not None:
                    bodies[body].update(page_families(locus.page))
        for body, families in sorted(bodies.items()):
            if len(families) > 1:
                connect(families)
                repeated_edges.append({'source_id': source['id'], 'body_sha256': sha(body.encode('ascii')),
                                       'numeric_families': sorted(families, key=int)})
    selected_pages = sorted({locus.page for _, document in paired for locus in document.loci
                             if locus.key in selected and locus.present and locus.kind == 'P0'})
    active_families = {family for page in selected_pages for family in page_families(page)}
    members = defaultdict(set)
    for family in list(parents):
        members[find(family)].add(family)
    for family in active_families:
        members[find(family)].add(family)
    active_groups = [sorted(group, key=int) for group in members.values() if group & active_families]
    if len(active_groups) < 2:
        raise ValueError('need at least two dependency units for the diagnostic partition')
    rank = lambda group: sha((SEED + '\n' + '\n'.join(group)).encode('ascii'))
    active_groups.sort(key=rank)
    evaluation_count = max(1, len(active_groups) // 5)
    units = []
    for index, group in enumerate(active_groups):
        group_set = set(group)
        pages = [page for page in selected_pages if page_families(page) & group_set]
        units.append({
            'unit_id': 'numeric-families:' + '+'.join(group), 'numeric_source_families': group,
            'partition': 'diagnostic_evaluation' if index < evaluation_count else 'dictionary_development',
            'rank_sha256': rank(group), 'selected_source_pages': pages,
            'canvas_ids': sorted({canvas for family in group for canvas in
                                 image_report['indexed_canvas_ids_by_leaf'].get(family, [])}),
        })
    return {
        'schema_version': 1, 'candidate_version': 'y-layout-prefix-v1',
        'status': 'exploratory_dictionary_partition', 'seed': SEED,
        'prior_exposure': 'Full-corpus results motivated this candidate; all units used for candidate development.',
        'valid_candidate_holdout': False, 'previously_unseen': False, 'image_region_alignment_reviewed': False,
        'sources': [{'id': source['id'], 'sha256': source['sha256']} for source, _ in paired],
        'selection': selected_audit, 'exact_string_dependency_edges': repeated_edges,
        'units': units,
    }


def load_pins():
    sources = paired_sources(load_sources())
    paths = {'source_catalog': 'data/transliterations.json',
             'image_report': 'research/folio-alignment/transcription-image-coverage.json',
             'canvas_index': 'research/image-index/canvases.csv',
             'image_index_audit': 'research/image-index/audit.json', 'plan': BASE + '/PLAN.md'}
    raw = {name: (ROOT / path).read_bytes() for name, path in paths.items()}
    report = json.loads(raw['image_report'])
    audit = json.loads(raw['image_index_audit'])
    identity = {field: audit[field] for field in
                ('manifest_url', 'manifest_sha256', 'access_date', 'access_timezone')}
    identity['canvases_csv_sha256'] = sha(raw['canvas_index'])
    rows = list(csv.DictReader(io.StringIO(raw['canvas_index'].decode('utf-8'))))
    # The accepted audit consumes the index builder's Booleans; its CSV stores
    # these as exact True/False strings. Restore that documented serialization.
    for row in rows:
        for field in ('has_partial_marker', 'has_multiple_explicit_sides'):
            if row[field] not in {'True', 'False'}:
                raise ValueError(f'invalid canvas-index Boolean: {field}')
            row[field] = row[field] == 'True'
    rebuilt = json.loads(json.dumps(make_report(sources, rows, identity)))
    if rebuilt != report:
        raise ValueError('accepted image-reference report differs from current pinned metadata')
    return sources, report, {name: {'path': paths[name], 'sha256': sha(data)} for name, data in raw.items()}


def prepare_partition():
    sources, images, pins = load_pins()
    partition = build_partition(sources, images)
    partition['input_pins'] = pins
    return partition


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', type=Path, help='Write the pre-fit diagnostic partition only')
    args = parser.parse_args()
    if not args.prepare:
        parser.error('the pre-fit preparation phase requires --prepare')
    try:
        partition = prepare_partition()
        args.prepare.write_text(json.dumps(partition, indent=2) + '\n')
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'y-layout preparation failed: {error}\n')
    print('Prepared exploratory dependency partition; no vocabulary fit or scoring performed.')


if __name__ == '__main__':
    main()
