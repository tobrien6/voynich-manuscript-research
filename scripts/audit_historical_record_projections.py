"""Compare lossy native record projections without creating a locus crosswalk."""

import argparse
from collections import Counter, defaultdict
import hashlib
from pathlib import Path
import zipfile

try:
    from .audit_historical_modern_pages import load_inputs
    from .audit_historical_lowercase_projection import project_body, build_report as parent_report
    from .audit_eva_token_coverage import encoded, load_json
    from .paragraph_token_corpus import protect_outputs
except ImportError:
    from audit_historical_modern_pages import load_inputs
    from audit_historical_lowercase_projection import project_body, build_report as parent_report
    from audit_eva_token_coverage import encoded, load_json
    from paragraph_token_corpus import protect_outputs

ROOT = Path(__file__).resolve().parents[1]
PARENT = Path('research/historical/lowercase-projection.json')
PLAN = Path('research/historical/RECORD_PROJECTION_PLAN.md')
HELPERS = ('audit_historical_record_projections.py', 'audit_historical_lowercase_projection.py',
           'audit_historical_modern_pages.py', 'audit_historical_interlinear.py',
           'ivtff.py', 'inspect_ivtff.py', 'audit_eva_token_coverage.py')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def projection_records(records, historical):
    grouped = defaultdict(list)
    seen = set()
    for record in records:
        if historical and record.transcriber != 'H':
            continue
        if not historical:
            if record.transcriber is not None:
                raise ValueError('modern input requires a single-source export')
            if not record.present:
                continue
        locator = record.locator if historical else record.identifier
        if locator in seen:
            raise ValueError('duplicate selected native locator')
        seen.add(locator)
        stream, _, _, _ = project_body(record.body if historical else record.text, historical)
        descriptor = {'native_locator': locator,
                      'source_file_line': record.physical_line if historical else record.line_number,
                      'native_unit' if historical else 'locus_kind': record.unit if historical else record.kind,
                      'source_order_index_zero_based_on_page': len(grouped[record.page])}
        grouped[record.page].append((stream, descriptor))
    if not grouped:
        raise ValueError('both sources require selected native records')
    return grouped


def side_profile(rows):
    nonempty = [stream for stream, _ in rows if stream]
    joined = ''.join(nonempty)
    return {'selected_native_records': len(rows), 'nonempty_projected_records': len(nonempty),
            'empty_projection_records': [descriptor for stream, descriptor in rows if not stream],
            'ordered_nonempty_projection_digests_sha256': digest(encoded([digest(s.encode('ascii')) for s in nonempty])),
            'projected_lowercase_symbols': len(joined), 'joined_stream_sha256': digest(joined.encode('ascii')),
            'projected_symbol_frequencies': dict(sorted(Counter(joined).items()))}


def compare_records(historical, modern):
    old = projection_records(historical, True)
    new = projection_records(modern.loci, False)
    pages = []
    for page in sorted(set(old) | set(new)):
        left, right = old.get(page, []), new.get(page, [])
        a = [s for s, _ in left if s]
        b = [s for s, _ in right if s]
        comparable = bool(a and b)
        groups = []
        left_groups, right_groups = defaultdict(list), defaultdict(list)
        for stream, descriptor in left:
            if stream:
                left_groups[stream].append(descriptor)
        for stream, descriptor in right:
            if stream:
                right_groups[stream].append(descriptor)
        hashes = {}
        for stream in set(left_groups) | set(right_groups):
            checksum = digest(stream.encode('ascii'))
            if checksum in hashes and hashes[checksum] != stream:
                raise ValueError('distinct exact projection strings have a digest collision')
            hashes[checksum] = stream
            x, y = left_groups.get(stream, []), right_groups.get(stream, [])
            status = ('one_to_one_lossy_projection' if len(x) == len(y) == 1 else
                      'ambiguous_shared_projection' if x and y else
                      'historical_only_projection' if x else 'modern_only_projection')
            groups.append({'projection_sha256': checksum, 'projected_lowercase_symbols': len(stream),
                           'status': status, 'historical_H_records': x, 'modern_IT2a_present_records': y})
        pages.append({
            'page_id': page, 'status': ('shared_exact_page_id' if left and right else
                                      'historical_only_page_id' if left else 'modern_only_page_id'),
            'historical_H': side_profile(left) if left else None,
            'modern_IT2a_present': side_profile(right) if right else None,
            'nonempty_record_projection_order_equal': a == b if comparable else None,
            'nonempty_record_projection_bags_equal': Counter(a) == Counter(b) if comparable else None,
            'joined_lowercase_streams_equal': ''.join(a) == ''.join(b) if comparable else None,
            'lowercase_symbol_frequencies_equal': Counter(''.join(a)) == Counter(''.join(b)) if comparable else None,
            'projection_groups': sorted(groups, key=lambda group: group['projection_sha256']),
        })
    shared = [p for p in pages if p['status'] == 'shared_exact_page_id']
    all_groups = [g for p in shared for g in p['projection_groups']]
    shared_groups = [g for g in all_groups if g['historical_H_records'] and g['modern_IT2a_present_records']]
    summary = {
        'historical_H_native_records': sum(len(rows) for rows in old.values()),
        'modern_IT2a_present_native_records': sum(len(rows) for rows in new.values()),
        'historical_H_record_pages': len(old), 'modern_IT2a_present_record_pages': len(new),
        'shared_exact_page_ids': len(shared),
        'historical_only_page_ids': sorted(set(old) - set(new)),
        'modern_only_page_ids': sorted(set(new) - set(old)),
        'shared_nonempty_projection_groups': len(shared_groups),
        'one_to_one_lossy_projection_groups': sum(g['status'] == 'one_to_one_lossy_projection' for g in shared_groups),
        'ambiguous_shared_projection_groups': sum(g['status'] == 'ambiguous_shared_projection' for g in shared_groups),
        'shared_projection_group_records': {
            'historical_H': sum(len(g['historical_H_records']) for g in shared_groups),
            'modern_IT2a_present': sum(len(g['modern_IT2a_present_records']) for g in shared_groups)},
    }
    for name, predicate in {
        'equal_nonempty_record_order_page_ids': lambda p: p['nonempty_record_projection_order_equal'] is True,
        'equal_nonempty_record_bag_page_ids': lambda p: p['nonempty_record_projection_bags_equal'] is True,
        'equal_bag_different_record_order_page_ids': lambda p: p['nonempty_record_projection_bags_equal'] is True and p['nonempty_record_projection_order_equal'] is False,
        'equal_joined_stream_different_record_bag_page_ids': lambda p: p['joined_lowercase_streams_equal'] is True and p['nonempty_record_projection_bags_equal'] is False,
    }.items():
        summary[name] = [p['page_id'] for p in shared if predicate(p)]
    return {'summary': summary, 'page_profiles': pages,
            'modern_nonexistent_loci_excluded': [l.identifier for l in modern.loci if not l.present]}


def build(root=ROOT, loaded=None):
    historical, modern, pins, _ = loaded or load_inputs(root)
    raw = (root / PARENT).read_bytes()
    if encoded(load_json(raw)) != encoded(parent_report(historical, modern, pins)):
        raise ValueError('parent projection report differs from complete pinned source replay')
    return {'schema_version': 1, 'method': 'exploratory-native-record-lowercase-projection-v1',
            'usable_as_verified_locus_crosswalk': False, 'usable_for_statistical_evaluation': False,
            'rules': {'historical_selection': 'native H including empty/padding projections',
                      'modern_selection': 'IT2a present only; no inferred page aliases',
                      'projection': 'accepted source-specific lowercase a-z body projection',
                      'order_and_bag': 'exact nonempty strings compared before digest serialization',
                      'empty_projection': 'native descriptors retained separately; never matching evidence',
                      'duplicate_group': 'retain every locator without positional pairing',
                      'inference_limit': 'lossy equality does not establish full body, glyph, word or region identity'},
            'inputs': {'sources': pins, 'parent_report': {'path': str(PARENT), 'sha256': digest(raw)},
                       'plan': {'path': str(PLAN), 'sha256': digest((root / PLAN).read_bytes())},
                       'implementation_sha256': {'scripts/' + name: digest((ROOT / 'scripts' / name).read_bytes()) for name in HELPERS}},
            **compare_records(historical, modern)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        loaded = load_inputs(ROOT)
        reads = [*loaded[3], ROOT / PARENT, ROOT / PLAN]
        if args.check:
            reads.append(args.check)
        protect_outputs([args.output] if args.output else [], reads, root=ROOT)
        result = build(ROOT, loaded)
        if args.check and encoded(load_json(args.check.read_bytes())) != encoded(result):
            raise ValueError('record-projection report differs from complete pinned replay')
        if args.output:
            args.output.write_bytes(encoded(result))
        elif not args.check:
            print(encoded(result).decode(), end='')
    except (ValueError, KeyError, OSError, UnicodeError, zipfile.BadZipFile) as error:
        parser.exit(1, f'record projection audit failed: {error}\n')
    if args.check or args.output:
        print(f"Verified {result['summary']['shared_exact_page_ids']} exact shared page IDs; no locus crosswalk created.")


if __name__ == '__main__':
    main()
