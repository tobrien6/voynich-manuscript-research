"""Retain all four fixed unmatched-page comparisons without accepting aliases."""

import argparse
from collections import Counter, defaultdict
import hashlib
from pathlib import Path
import zipfile

try:
    from . import audit_historical_record_projections as parent
except ImportError:
    import audit_historical_record_projections as parent

ROOT = parent.ROOT
PLAN = Path('research/historical/f101-candidate-plan.json')
HUMAN_PLAN = Path('research/historical/F101_CANDIDATE_PLAN.md')
PARENT = Path('research/historical/record-projections.json')
HISTORICAL = ('f101r1', 'f101v2')
MODERN = ('f101r', 'f101v')
FROZEN = (str(PARENT), str(parent.PLAN), str(parent.PARENT),
          *('scripts/' + name for name in parent.HELPERS),
          'scripts/paragraph_token_corpus.py')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_plan(root):
    raw = (root / PLAN).read_bytes()
    plan = parent.load_json(raw)
    require(type(plan['schema_version']) is int and plan['schema_version'] == 1
            and plan['plan_id'] == 'fixed-f101-native-record-candidates-v1'
            and plan['accepted_parent_merge'] == 'ed787c56848b893add21c4a51b219fe9f5f08501'
            and plan['historical_page_ids'] == list(HISTORICAL)
            and plan['modern_page_ids'] == list(MODERN)
            and plan['candidate_pairs'] == [[a, b] for a in HISTORICAL for b in MODERN]
            and plan['accepted_page_aliases'] == []
            and plan['apply_to_statistics'] is False
            and plan['untouched_evaluation'] is False
            and set(plan['frozen_sha256']) == set(FROZEN), 'fixed candidate plan changed')
    for name, checksum in plan['frozen_sha256'].items():
        require(sha((root / name).read_bytes()) == checksum, 'frozen dependency changed: ' + name)
    return plan, raw


def compare_pair(left, right):
    a, b = [s for s, _ in left if s], [s for s, _ in right if s]
    comparable = bool(a and b)
    groups_a, groups_b = defaultdict(list), defaultdict(list)
    for rows, groups in ((left, groups_a), (right, groups_b)):
        for stream, descriptor in rows:
            if stream:
                groups[stream].append(descriptor)
    hashes, groups = {}, []
    for stream in set(groups_a) | set(groups_b):
        checksum = sha(stream.encode('ascii'))
        require(checksum not in hashes or hashes[checksum] == stream,
                'distinct exact projection strings have a digest collision')
        hashes[checksum] = stream
        x, y = groups_a.get(stream, []), groups_b.get(stream, [])
        status = ('one_to_one_lossy_projection' if len(x) == len(y) == 1 else
                  'ambiguous_shared_projection' if x and y else
                  'historical_only_projection' if x else 'modern_only_projection')
        groups.append({'projection_sha256': checksum, 'projected_lowercase_symbols': len(stream),
                       'status': status, 'historical_H_records': x, 'modern_IT2a_present_records': y})
    shared = [g for g in groups if g['historical_H_records'] and g['modern_IT2a_present_records']]
    return {
        'accepted_page_alias': False, 'usable_as_verified_locus_crosswalk': False,
        'comparable_nonempty': comparable,
        'nonempty_record_projection_order_equal': a == b if comparable else None,
        'nonempty_record_projection_bags_equal': Counter(a) == Counter(b) if comparable else None,
        'joined_lowercase_streams_equal': ''.join(a) == ''.join(b) if comparable else None,
        'lowercase_symbol_frequencies_equal': Counter(''.join(a)) == Counter(''.join(b)) if comparable else None,
        'shared_projection_groups': len(shared),
        'one_to_one_lossy_projection_groups': sum(g['status'] == 'one_to_one_lossy_projection' for g in shared),
        'ambiguous_shared_projection_groups': sum(g['status'] == 'ambiguous_shared_projection' for g in shared),
        'shared_projection_group_records': {
            'historical_H': sum(len(g['historical_H_records']) for g in shared),
            'modern_IT2a_present': sum(len(g['modern_IT2a_present_records']) for g in shared)},
        'projection_groups': sorted(groups, key=lambda g: g['projection_sha256']),
    }


def candidate_matrix(old, new):
    require(all(page in old for page in HISTORICAL) and all(page in new for page in MODERN),
            'a fixed selected page is absent')
    return [{'historical_page_id': a, 'modern_page_id': b, **compare_pair(old[a], new[b])}
            for a in HISTORICAL for b in MODERN]


def build(root=ROOT, loaded=None, frozen=None):
    plan, plan_raw = frozen or load_plan(root)
    loaded = loaded or parent.load_inputs(root)
    historical, modern, pins, _ = loaded
    replay = parent.build(root, loaded)
    raw = (root / PARENT).read_bytes()
    require(parent.encoded(parent.load_json(raw)) == parent.encoded(replay),
            'accepted parent differs from complete pinned replay')
    require(replay['summary']['historical_only_page_ids'] == list(HISTORICAL)
            and replay['summary']['modern_only_page_ids'] == list(MODERN)
            and replay['summary']['shared_exact_page_ids'] == 223,
            'fixed pages are not the complete unmatched parent sets')
    old = parent.projection_records(historical, True)
    new = parent.projection_records(modern.loci, False)
    profiles = [{'source_id': source, 'page_id': page, **parent.side_profile(rows[page])}
                for source, pages, rows in [('historical_H', HISTORICAL, old),
                                            ('modern_IT2a_present', MODERN, new)] for page in pages]
    return {
        'schema_version': 1, 'method': 'fixed-f101-unmatched-record-candidates-v1',
        'accepted_page_aliases': [], 'usable_for_statistical_evaluation': False,
        'usable_as_verified_locus_crosswalk': False, 'usable_as_physical_image_mapping': False,
        'untouched_evaluation': False,
        'rules': {'selection': 'all four fixed H/IT2a unmatched page-ID comparisons; no page renaming',
                  'projection': 'accepted source-specific ASCII a-z body projection, with known losses',
                  'empty_projections': 'retain native denominators/descriptors; never positive evidence',
                  'groups': 'exact strings before hashes; complete multiplicities; no positional pairing',
                  'parent': 'original 223 exact-page cohort remains unchanged'},
        'inputs': {'sources': pins, 'parent_report': {'path': str(PARENT), 'sha256': sha(raw)},
                   'machine_plan': {'path': str(PLAN), 'sha256': sha(plan_raw)},
                   'human_plan': {'path': str(HUMAN_PLAN), 'sha256': sha((root / HUMAN_PLAN).read_bytes())},
                   'frozen_sha256': plan['frozen_sha256'],
                   'producer_sha256': sha(Path(__file__).read_bytes())},
        'page_profiles': profiles, 'candidate_pairs': candidate_matrix(old, new),
    }


def protected_inputs(root, loaded):
    return [*loaded[3], *(root / name for name in FROZEN), root / PLAN, root / HUMAN_PLAN,
            root / 'scripts/audit_f101_record_candidates.py', Path(__file__).resolve()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        frozen = load_plan(ROOT)
        loaded = parent.load_inputs(ROOT)
        reads = protected_inputs(ROOT, loaded) + ([args.check] if args.check else [])
        outputs = [args.output] if args.output else []
        parent.protect_outputs(outputs, reads, root=ROOT)
        result = build(ROOT, loaded, frozen)
        serialized = parent.encoded(result)
        if args.check:
            require(parent.encoded(parent.load_json(args.check.read_bytes())) == serialized,
                    'candidate report differs from complete pinned replay')
        if args.output:
            parent.protect_outputs(outputs, reads, root=ROOT)
            args.output.write_bytes(serialized)
        elif not args.check:
            print(serialized.decode(), end='')
    except (ValueError, KeyError, TypeError, OSError, UnicodeError, zipfile.BadZipFile) as error:
        parser.exit(1, f'f101 candidate audit failed: {error}\n')
    if args.check or args.output:
        print('Verified all four fixed candidate pairs; no page alias or crosswalk accepted.')


if __name__ == '__main__':
    main()
