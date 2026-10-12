"""Audit exact pilot image/page links without assigning foldout panels or aliases."""

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys

try:
    from .audit_transliterations import load_sources
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import load_sources
    from token_baselines import paired_sources


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    'inventory': 'research/pilot/inventory.json',
    'canvas_index': 'research/image-index/canvases.csv',
    'index_audit': 'research/image-index/audit.json',
    'source_catalog': 'data/transliterations.json',
}
SIDE = re.compile(r'[1-9][0-9]*[rv]')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def page_summary(document, page):
    loci = [locus for locus in document.loci if locus.page == page]
    present = [locus for locus in loci if locus.present]
    return {
        'page_id': page,
        'header_present': page in document.pages,
        'present_loci': len(present),
        'present_loci_by_kind': dict(sorted(Counter(locus.kind for locus in present).items())),
        'present_locus_identifiers': [locus.identifier for locus in present],
        'explicitly_nonexistent_locus_identifiers': [locus.identifier for locus in loci
                                                   if not locus.present],
    }


def build_report(inventory, canvases, sources):
    """Compare identifiers only; even exact links leave glyph/region review pending."""
    sources = paired_sources(sources)
    index = {}
    for row in canvases:
        uri = row['canvas_uri']
        require(uri not in index, 'duplicate canvas URI')
        require(row['has_multiple_explicit_sides'] in {'True', 'False'},
                'invalid combined-view flag')
        index[uri] = row
    seen, entries = set(), []
    for record in inventory['records']:
        target = record['target']
        require(isinstance(target, str) and SIDE.fullmatch(target), 'invalid pilot target')
        require(target not in seen, 'duplicate pilot target')
        seen.add(target)
        row = index.get(record['canvas_uri'])
        require(row is not None, 'pilot canvas absent from index')
        require(row['yale_label'] == record['yale_label'], 'pilot/index label mismatch')
        require(row['image_oid'] == record['image_id'], 'pilot/index image ID mismatch')
        sides = row['explicit_folio_sides'].split(';')
        require(target in sides, 'pilot target absent from explicit canvas labels')
        require(all(SIDE.fullmatch(side) for side in sides), 'invalid explicit canvas side')
        require((len(sides) > 1) == (row['has_multiple_explicit_sides'] == 'True'),
                'combined-view flag disagrees with explicit sides')
        exact_id = 'f' + target
        editions = []
        blockers = []
        if len(sides) > 1:
            blockers.append('shared_canvas_requires_documented_region_mapping')
        for source, document in sources:
            exact = page_summary(document, exact_id)
            # These identifiers are lexical candidates, never accepted mappings.
            panel_pattern = re.compile(re.escape(exact_id) + r'[1-6]')
            candidates = [page_summary(document, page) for page in document.pages
                          if panel_pattern.fullmatch(page)]
            if not exact['header_present']:
                blockers.append(source['id'] + ':exact_page_header_absent')
            elif not exact['present_loci']:
                blockers.append(source['id'] + ':no_present_exact_page_loci')
            if candidates:
                blockers.append(source['id'] + ':panel_identifiers_require_review')
            editions.append({'id': source['id'], 'exact_page': exact,
                             'unmapped_panel_identifier_candidates': candidates})
        left, right = [
            {locus.key: locus for locus in document.loci
             if locus.page == exact_id and locus.present}
            for _, document in sources
        ]
        shared = sorted(left.keys() & right.keys())
        entries.append({
            'target': target,
            'catalog_section': record['catalog_section'],
            'selected_canvas': {
                'canvas_uri': row['canvas_uri'], 'yale_label': row['yale_label'],
                'image_oid': row['image_oid'],
                'catalog_image_url': row['catalog_image_url'],
                'explicit_label_sides': sides,
                'combined_view': len(sides) > 1,
            },
            'status': 'blocked' if blockers else 'exact_page_metadata_link',
            'blockers': blockers,
            'image_exposure': {
                'inspection_status': record['inspection_status'],
                'inspected_on': record['inspected_on'],
                'source_record': 'research/pilot/inventory.json',
            },
            'editions': editions,
            'exact_page_comparison': {
                'shared_present_locus_keys': shared,
                'present_only_in_ZL3b': sorted(left.keys() - right.keys()),
                'present_only_in_IT2a': sorted(right.keys() - left.keys()),
                'shared_with_different_kind_or_locator': [
                    {'key': key, 'ZL3b': left[key].identifier, 'IT2a': right[key].identifier}
                    for key in shared if (left[key].kind, left[key].locator)
                    != (right[key].kind, right[key].locator)
                ],
            },
        })
    linked = [entry for entry in entries if entry['status'] == 'exact_page_metadata_link']
    return {
        'schema_version': 1,
        'method': 'pilot exact-page metadata readiness v1',
        'scope': 'No panel/region mapping, glyph adjudication, alias, split, or decipherment.',
        'sources': [{'id': source['id'], 'sha256': source['sha256'], 'url': source['url']}
                    for source, _ in sources],
        'summary': {
            'target_count': len(entries),
            'exact_page_metadata_link_count': len(linked),
            'blocked_target_count': len(entries) - len(linked),
            'shared_present_loci_in_exact_links': sum(
                len(entry['exact_page_comparison']['shared_present_locus_keys']) for entry in linked),
        },
        'special_page_headers_without_assigned_pilot_mapping': [
            {'id': source['id'], 'page': page_summary(document, 'fRos')}
            for source, document in sources
        ],
        'entries': entries,
    }


def audit(root=ROOT):
    raw = {name: (root / path).read_bytes() for name, path in INPUTS.items()}
    inventory = json.loads(raw['inventory'])
    index_audit = json.loads(raw['index_audit'])
    require(inventory['manifest_sha256'] == index_audit['manifest_sha256'],
            'inventory and image index refer to different manifests')
    require(inventory['manifest_url'] == index_audit['manifest_url'],
            'inventory and image index refer to different manifest URLs')
    rows = list(csv.DictReader(io.StringIO(raw['canvas_index'].decode('utf-8'))))
    require(len(rows) == index_audit['canvas_count'] == inventory['manifest_canvas_count'],
            'canvas count disagrees with declared manifest inventory')
    report = build_report(inventory, rows, load_sources(root))
    report['inputs'] = {name: {'path': path, 'sha256': hashlib.sha256(raw[name]).hexdigest()}
                        for name, path in INPUTS.items()}
    report['manifest'] = {'url': inventory['manifest_url'],
                          'sha256': inventory['manifest_sha256']}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    parser.add_argument('--require-complete', action='store_true',
                        help='Exit 2 if any pilot target has a mapping blocker')
    args = parser.parse_args()
    try:
        report = audit()
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed pilot readiness differs from recomputed report')
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
        if args.output:
            args.output.write_text(rendered, encoding='utf-8')
        elif not args.check:
            print(rendered, end='')
        if args.check:
            print('Pinned sources and pilot metadata readiness verified.')
        blocked = report['summary']['blocked_target_count']
        if args.require_complete and blocked:
            print(f'Incomplete pilot: {blocked} targets retain mapping blockers.', file=sys.stderr)
            return 2
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'pilot readiness failed: {error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
