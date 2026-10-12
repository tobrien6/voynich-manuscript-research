"""Audit encoded paragraph-marker pairing and exact locus membership."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

try:
    from .annotation_agreement import annotations, index_loci, selection_digest
    from .audit_transliterations import ROOT, load_sources
    from .ivtff import without_free_comments
    from .token_baselines import paired_sources
except ImportError:
    from annotation_agreement import annotations, index_loci, selection_digest
    from audit_transliterations import ROOT, load_sources
    from ivtff import without_free_comments
    from token_baselines import paired_sources


START, END = '<%>', '<$>'
MARKERS = re.compile(r'<[%$]>')
STATUSES = (
    'same_ordered_unit_members', 'different_ordered_unit_members',
    'grouped_only_left', 'grouped_only_right', 'ungrouped_both',
    'ineligible_page_annotations',
)


def envelope(locus):
    return None if locus is None else {
        'key': locus.key, 'locus_id': locus.identifier, 'kind': locus.kind,
        'present': locus.present, 'file_line_number': locus.line_number,
    }


def page_units(source_id, page, loci):
    events = [(locus, MARKERS.findall(without_free_comments(locus.text))) for locus in loci]
    anomalies, opened = [], None
    for locus, marks in events:
        if marks.count(START) > 1 or marks.count(END) > 1:
            anomalies.append({**envelope(locus), 'reason': 'repeated_marker_in_locus'})
        if START in marks and END in marks and marks.index(END) < marks.index(START):
            anomalies.append({**envelope(locus), 'reason': 'end_before_start_in_locus'})
        for mark in marks:
            if mark == START:
                if opened is not None:
                    anomalies.append({**envelope(locus), 'reason': 'start_while_unit_open'})
                else:
                    opened = locus
            elif opened is None:
                anomalies.append({**envelope(locus), 'reason': 'end_without_open_unit'})
            else:
                opened = None
    if opened is not None:
        anomalies.append({**envelope(opened), 'reason': 'unit_open_at_page_end'})
    starts = sum(marks.count(START) for _, marks in events)
    ends = sum(marks.count(END) for _, marks in events)
    units, assigned, members = [], set(), None
    if not anomalies:
        for locus, marks in events:
            if START in marks:
                members = []
            if members is not None:
                members.append(locus.key)
            if END in marks:
                unit = {
                    'id': f'{source_id}:{members[0]}-{members[-1]}', 'page': page,
                    'start_key': members[0], 'end_key': members[-1],
                    'member_count': len(members), 'member_keys': members,
                    'ordered_member_keys_sha256': hashlib.sha256(
                        ('\n'.join(members) + '\n').encode()).hexdigest(),
                }
                units.append(unit)
                assigned.update(members)
                members = None
    return {
        'page': page, 'present_generic_p_loci': len(loci),
        'status': 'anomalous' if anomalies else ('balanced' if starts else 'unmarked'),
        'start_marker_count': starts, 'end_marker_count': ends,
        'anomalies_reasons_may_overlap': anomalies, 'units': units,
        'unassigned_locus_keys': [locus.key for locus in loci if locus.key not in assigned],
    }


def source_units(source, document):
    index_loci(document)
    pages = defaultdict(list)
    outside = []
    nonexistent = []
    for locus in document.loci:
        if locus.kind.startswith('P'):
            if locus.present:
                pages[locus.page].append(locus)
            else:
                nonexistent.append(envelope(locus))
        elif locus.present:
            observed = annotations(locus)
            if observed['start_marker_count'] or observed['end_marker_count']:
                outside.append({**envelope(locus),
                                'start_marker_count': observed['start_marker_count'],
                                'end_marker_count': observed['end_marker_count']})
    records = [page_units(source['id'], page, loci) for page, loci in pages.items()]
    counts = Counter(row['status'] for row in records)
    present = sum(row['present_generic_p_loci'] for row in records)
    assigned = sum(unit['member_count'] for row in records for unit in row['units'])
    unassigned = sum(len(row['unassigned_locus_keys']) for row in records)
    if assigned + unassigned != present:
        raise ValueError('paragraph membership does not account for all present P loci')
    return {
        **{field: source[field] for field in ('id', 'url', 'path', 'sha256', 'alphabet')},
        'summary': {
            'generic_p_page_count': len(records), 'present_generic_p_loci': present,
            'page_marker_status_counts': {status: counts[status]
                                         for status in ('balanced', 'unmarked', 'anomalous')},
            'complete_unit_count': sum(len(row['units']) for row in records),
            'assigned_locus_count': assigned, 'unassigned_locus_count': unassigned,
        },
        'pages': records,
        'nonexistent_generic_p_records': nonexistent,
        'paragraph_marks_on_present_non_p_loci': outside,
    }


def membership_report(sources):
    paired = paired_sources(sources)
    indexed = [index_loci(document) for _, document in paired]
    generic = [{key for key, locus in index.items()
                if locus.present and locus.kind.startswith('P')} for index in indexed]
    shared = set.intersection(*generic)
    if not shared:
        raise ValueError('no shared present generic-P loci')
    summaries = [source_units(source, document) for source, document in paired]
    by_key, units, signatures, page_status = [], [], [], []
    for summary in summaries:
        source_units_by_id = {unit['id']: unit for page in summary['pages'] for unit in page['units']}
        signature_units = {tuple(unit['member_keys']): unit for unit in source_units_by_id.values()}
        assigned = {key: unit['id'] for unit in source_units_by_id.values() for key in unit['member_keys']}
        if (len(signature_units) != len(source_units_by_id)
                or len(assigned) != summary['summary']['assigned_locus_count']):
            raise ValueError('duplicate paragraph unit or overlapping membership')
        by_key.append(assigned)
        units.append(source_units_by_id)
        signatures.append(signature_units)
        page_status.append({page['page']: page['status'] for page in summary['pages']})
    status_keys = {status: [] for status in STATUSES}
    different_with_unpaired, different_without_unpaired = [], []
    for key in sorted(shared):
        page = indexed[0][key].page
        left_id, right_id = [assigned.get(key) for assigned in by_key]
        if any(status[page] == 'anomalous' for status in page_status):
            status = 'ineligible_page_annotations'
        elif left_id is None and right_id is None:
            status = 'ungrouped_both'
        elif left_id is None:
            status = 'grouped_only_right'
        elif right_id is None:
            status = 'grouped_only_left'
        else:
            left = units[0][left_id]['member_keys']
            right = units[1][right_id]['member_keys']
            if left == right:
                status = 'same_ordered_unit_members'
            else:
                status = 'different_ordered_unit_members'
                has_unpaired = bool((set(left) | set(right)) - shared)
                (different_with_unpaired if has_unpaired else different_without_unpaired).append(key)
        status_keys[status].append(key)
    exact = set(signatures[0]) & set(signatures[1])
    matched = [{
        'left_unit_id': signatures[0][members]['id'],
        'right_unit_id': signatures[1][members]['id'],
        'member_count': len(members),
        'ordered_member_keys_sha256': signatures[0][members]['ordered_member_keys_sha256'],
    } for members in sorted(exact)]
    excluded = {}
    for side, (source, _) in enumerate(paired):
        excluded[source['id']] = [
            {'selected_source_record': envelope(indexed[side][key]),
             'other_source_record': envelope(indexed[1 - side].get(key))}
            for key in sorted(generic[side] - shared)
        ]
    return {
        'schema_version': 1, 'method': 'paired encoded paragraph membership audit v1',
        'source_order': {'left': paired[0][0]['id'], 'right': paired[1][0]['id']},
        'selection': {
            'generic_type': 'P', 'shared_present_generic_p_count': len(shared),
            'sorted_shared_locus_keys_sha256': selection_digest(shared),
            'generic_p_records_excluded_by_intersection': excluded,
        },
        'sources': summaries,
        'shared_locus_membership': {
            'denominator': len(shared),
            'status_counts': {status: len(keys) for status, keys in status_keys.items()},
            'status_locus_keys': status_keys,
            'different_membership_with_unpaired_unit_members': different_with_unpaired,
            'different_membership_without_unpaired_unit_members': different_without_unpaired,
        },
        'exact_unit_comparison': {
            'matching_complete_unit_count': len(exact), 'matches': matched,
            'unmatched_unit_ids': {
                summary['id']: [unit['id'] for unit in units[side].values()
                                if tuple(unit['member_keys']) not in exact]
                for side, summary in enumerate(summaries)
            },
        },
    }


def validate_output_path(path):
    resolved = path.resolve()
    raw = (ROOT / 'data/raw').resolve()
    scripts = (ROOT / 'scripts').resolve()
    protected = {
        (ROOT / 'data/transliterations.json').resolve(), Path(__file__).resolve(),
        (ROOT / 'research/transliteration/PARAGRAPH_MEMBERSHIP_PLAN.md').resolve(),
    }
    catalog = json.loads((ROOT / 'data/transliterations.json').read_text())
    protected.update((ROOT / source['path']).resolve() for source in catalog['sources'])
    if (resolved in protected or resolved == raw or raw in resolved.parents
            or resolved == scripts or scripts in resolved.parents):
        raise ValueError('output would overwrite a source, source catalog, script, or plan')
    if path.exists():
        protected.update(candidate for folder in (raw, scripts)
                         for candidate in folder.rglob('*') if candidate.is_file())
        if any(path.samefile(source) for source in protected if source.exists()):
            raise ValueError('output aliases a source, source catalog, script, or plan')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    destination = parser.add_mutually_exclusive_group()
    destination.add_argument('--output', type=Path)
    destination.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            validate_output_path(args.output)
        report = membership_report(load_sources())
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed paragraph membership differs from recomputed report')
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
        if args.output:
            args.output.write_text(rendered)
        elif not args.check:
            print(rendered, end='')
    except (ValueError, OSError) as error:
        parser.exit(1, f'paragraph membership audit failed: {error}\n')
    if args.check:
        print('Pinned sources and committed paragraph membership audit verified.')


if __name__ == '__main__':
    main()
