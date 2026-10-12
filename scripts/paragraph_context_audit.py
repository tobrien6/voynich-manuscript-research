"""Extend annotation comparisons to generic P loci and immediate source context."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

try:
    from .annotation_agreement import FIELDS, MARKER_COUNTS, annotations, index_loci, summarize
    from .audit_transliterations import load_sources
    from .token_baselines import paired_sources
except ImportError:
    from annotation_agreement import FIELDS, MARKER_COUNTS, annotations, index_loci, summarize
    from audit_transliterations import load_sources
    from token_baselines import paired_sources


def snapshot(locus):
    return None if locus is None else {**annotations(locus), 'key': locus.key, 'kind': locus.kind}


def next_paragraph_loci(document):
    pages = defaultdict(list)
    for locus in document.loci:
        if locus.present and locus.kind.startswith('P'):
            pages[locus.page].append(locus)
    following = {}
    for loci in pages.values():
        for index, locus in enumerate(loci):
            following[locus.key] = loci[index + 1] if index + 1 < len(loci) else None
    return following


def separate_centered_locus_source(current, following, source_ids):
    """Identify only the exact marker context fixed before this audit."""
    left, right = following['left'], following['right']
    if (left is None or right is None or left['key'] != right['key']
            or left['kind'] != 'Pc' or right['kind'] != 'Pc'
            or left['end_marker_count'] != 1 or right['end_marker_count'] != 1):
        return None
    for separate, joined, identifier in [('left', 'right', source_ids[0]),
                                          ('right', 'left', source_ids[1])]:
        if (current[separate]['end_marker_count'] == 1
                and current[joined]['end_marker_count'] == 0
                and following[separate]['start_marker_count'] == 1
                and following[joined]['start_marker_count'] == 0):
            return identifier
    return None


def context_report(sources):
    paired = paired_sources(sources)
    source_ids = [source['id'] for source, _ in paired]
    indexes = [index_loci(document) for _, document in paired]
    generic = [{key for key, locus in indexed.items()
                if locus.present and locus.kind.startswith('P')} for indexed in indexes]
    shared = set.intersection(*generic)
    if not shared:
        raise ValueError('no shared present generic-P loci')
    rows = []
    for key in sorted(shared):
        left, right = [snapshot(indexed[key]) for indexed in indexes]
        rows.append({'key': key, 'page': indexes[0][key].page, 'left': left, 'right': right,
                     'discordant_fields': [field for field in FIELDS + MARKER_COUNTS + ('kind',)
                                           if left[field] != right[field]]})
    kinds = sorted({row[side]['kind'] for row in rows for side in ('left', 'right')})
    kind_pairs = Counter((row['left']['kind'], row['right']['kind']) for row in rows)
    next_loci = [next_paragraph_loci(document) for _, document in paired]
    p0_contexts = []
    for row in rows:
        if (row['left']['kind'] == row['right']['kind'] == 'P0'
                and row['left']['paragraph_end'] != row['right']['paragraph_end']):
            following = {side: snapshot(indexed[row['key']])
                         for side, indexed in zip(('left', 'right'), next_loci)}
            p0_contexts.append({
                'current': row, 'next_present_generic_p_on_same_page': following,
                'following_centered_locus_is_separate_paragraph_in':
                    separate_centered_locus_source(row, following, source_ids),
            })
    matches = Counter(context['following_centered_locus_is_separate_paragraph_in']
                      for context in p0_contexts)
    return {
        'schema_version': 1, 'method': 'paired generic-P annotation context audit v1',
        'source_order': {'left': source_ids[0], 'right': source_ids[1]},
        'sources': [{field: source[field] for field in ('id', 'url', 'path', 'sha256', 'alphabet')}
                    for source, _ in paired],
        'selection': {
            'generic_type': 'P', 'rule': 'intersection of present generic-P locus keys in both sources',
            'source_present_generic_p_counts': {identifier: len(keys)
                                                for identifier, keys in zip(source_ids, generic)},
            'source_present_generic_p_kind_counts': {
                identifier: dict(sorted(Counter(indexed[key].kind for key in keys).items()))
                for identifier, indexed, keys in zip(source_ids, indexes, generic)},
            'present_generic_p_keys_excluded_by_intersection': {
                identifier: sorted(keys - shared) for identifier, keys in zip(source_ids, generic)},
        },
        'shared_generic_p_annotations': summarize(rows),
        'subtype_pairs': [{'left': left, 'right': right, 'count': kind_pairs[left, right]}
                          for left in kinds for right in kinds],
        'annotation_disagreements_by_subtype_pair': [
            {'left': left, 'right': right, 'denominator': kind_pairs[left, right],
             'paragraph_start_disagreement_count': sum(
                 row['left']['paragraph_start'] != row['right']['paragraph_start']
                 for row in rows if row['left']['kind'] == left and row['right']['kind'] == right),
             'paragraph_end_disagreement_count': sum(
                 row['left']['paragraph_end'] != row['right']['paragraph_end']
                 for row in rows if row['left']['kind'] == left and row['right']['kind'] == right)}
            for left in kinds for right in kinds],
        'discordant_loci': [row for row in rows if row['discordant_fields']],
        'shared_p0_end_disagreement_contexts': p0_contexts,
        'centered_locus_context_summary': {
            'p0_end_disagreement_denominator': len(p0_contexts),
            'matching_context_count_by_source_marking_separate_centered_locus':
                {identifier: matches[identifier] for identifier in source_ids},
            'other_context_count': matches[None],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        report = context_report(load_sources())
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed paragraph context audit differs from recomputed report')
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
        if args.output:
            args.output.write_text(rendered)
        elif not args.check:
            print(rendered, end='')
    except (ValueError, OSError) as error:
        parser.exit(1, f'paragraph context audit failed: {error}\n')
    if args.check:
        print('Pinned sources and committed generic-P context audit verified.')


if __name__ == '__main__':
    main()
