"""Audit paired P0 paragraph marks and effective source metadata without tokens."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

try:
    from .audit_transliterations import load_sources
    from .ivtff import without_free_comments
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import load_sources
    from ivtff import without_free_comments
    from token_baselines import paired_sources


REGULAR_LOCATORS = frozenset({'@', '+', '*'})
FIELDS = ('paragraph_start', 'paragraph_end', 'currier_label', 'locator')
MARKER_COUNTS = ('start_marker_count', 'end_marker_count')


def annotations(locus):
    """Absence of a source mark is not an independently verified non-boundary."""
    text = without_free_comments(locus.text)
    starts, ends = text.count('<%>'), text.count('<$>')
    return {
        'locus_id': locus.identifier,
        'file_line_number': locus.line_number,
        'paragraph_start': bool(starts), 'paragraph_end': bool(ends),
        'start_marker_count': starts, 'end_marker_count': ends,
        'currier_label': locus.variables.get('L'), 'locator': locus.locator,
    }


def index_loci(document):
    indexed = {}
    for locus in document.loci:
        if locus.transcriber is not None or locus.key in indexed:
            raise ValueError('require unique non-interlinear locus keys')
        indexed[locus.key] = locus
    return indexed


def selection_digest(keys):
    return hashlib.sha256(('\n'.join(sorted(keys)) + '\n').encode()).hexdigest()


def summarize(rows):
    comparisons = []
    for field in FIELDS:
        counts = Counter((row['left'][field], row['right'][field]) for row in rows)
        if field in {'paragraph_start', 'paragraph_end'}:
            values = [False, True]
        else:
            values = {value for pair in counts for value in pair}
            if field == 'currier_label':
                values.add(None)
            values = sorted(values, key=lambda value: (value is not None, str(value)))
        agreements = sum(count for (left, right), count in counts.items() if left == right)
        comparisons.append({
            'field': field, 'denominator': len(rows), 'agreement_count': agreements,
            'disagreement_count': len(rows) - agreements,
            'disagreement_fraction': round((len(rows) - agreements) / len(rows), 8)
            if rows else None,
            'cells': [{'left': left, 'right': right, 'count': counts[left, right]}
                      for left in values for right in values],
        })
    return {
        'selected_loci': len(rows),
        'sorted_locus_keys_sha256': selection_digest([row['key'] for row in rows]),
        'source_marker_totals': {
            side: {field: sum(row[side][field] for row in rows) for field in MARKER_COUNTS}
            for side in ('left', 'right')
        },
        'comparisons': comparisons,
        'any_discordant_field_count': sum(bool(row['discordant_fields']) for row in rows),
    }


def annotation_report(sources):
    paired = paired_sources(sources)
    indexes = [index_loci(document) for _, document in paired]
    p0_keys = [{key for key, locus in indexed.items()
                if locus.present and locus.kind == 'P0'} for indexed in indexes]
    common = set.intersection(*p0_keys)
    if not common:
        raise ValueError('no shared present P0 loci')
    regular = {key for key in common
               if all(indexed[key].locator in REGULAR_LOCATORS for indexed in indexes)}
    rows = []
    for key in sorted(common):
        left, right = [annotations(indexed[key]) for indexed in indexes]
        rows.append({
            'key': key, 'page': indexes[0][key].page,
            'in_regular_cohort': key in regular, 'left': left, 'right': right,
            'discordant_fields': [field for field in FIELDS + MARKER_COUNTS
                                  if left[field] != right[field]],
        })
    return {
        'schema_version': 1, 'method': 'paired P0 source annotation agreement v1',
        'source_order': {'left': paired[0][0]['id'], 'right': paired[1][0]['id']},
        'sources': [{field: source[field] for field in ('id', 'url', 'path', 'sha256', 'alphabet')}
                    for source, _ in paired],
        'selection': {
            'kind': 'P0', 'rule': 'intersection of present P0 locus keys in ZL3b and IT2a',
            'source_present_p0_counts': {source['id']: len(keys)
                                        for (source, _), keys in zip(paired, p0_keys)},
            'present_p0_keys_excluded_by_intersection': {
                source['id']: sorted(keys - common)
                for (source, _), keys in zip(paired, p0_keys)
            },
            'regular_locators_required_in_both_sources': sorted(REGULAR_LOCATORS),
            'shared_p0_keys_excluded_by_locator_rule': sorted(common - regular),
        },
        'cohorts': {
            'shared_present_p0': summarize(rows),
            'shared_regular_p0': summarize([row for row in rows if row['in_regular_cohort']]),
        },
        'discordant_loci': [row for row in rows if row['discordant_fields']],
        'repeated_marker_loci': [row for row in rows
                                 if any(row[side][field] > 1 for side in ('left', 'right')
                                        for field in MARKER_COUNTS)],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        report = annotation_report(load_sources())
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed annotation agreement differs from recomputed report')
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
        if args.output:
            args.output.write_text(rendered)
        elif not args.check:
            print(rendered, end='')
    except (ValueError, OSError) as error:
        parser.exit(1, f'annotation agreement failed: {error}\n')
    if args.check:
        print('Pinned sources and committed annotation agreement verified.')


if __name__ == '__main__':
    main()
