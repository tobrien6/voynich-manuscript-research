"""Exploratory q/y locus-boundary contrasts stratified by source metadata."""

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .audit_transliterations import load_sources
    from .ivtff import without_free_comments
    from .locus_positions import prepare_rows, summarize_position
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import load_sources
    from ivtff import without_free_comments
    from locus_positions import prepare_rows, summarize_position
    from token_baselines import paired_sources


LOCATORS = frozenset({'@', '+', '*'})
PREFIX_FEATURES = frozenset({'literal_q_prefix', 'literal_y_prefix'})


def select_locations(sources):
    present_p0 = [{locus.key for locus in document.loci if locus.present and locus.kind == 'P0'}
                  for _, document in sources]
    regular = [{locus.key for locus in document.loci if locus.present and
                locus.kind == 'P0' and locus.locator in LOCATORS} for _, document in sources]
    return set.intersection(*present_p0), set.intersection(*regular)


def paragraph_start(locus):
    return '<%>' in without_free_comments(locus.text)


def stratified_report(repetitions=199, seed=20261011):
    if repetitions < 1:
        raise ValueError('repetitions must be positive')
    sources = paired_sources(load_sources())
    common_p0, common_regular = select_locations(sources)
    if not common_regular:
        raise ValueError('no paired regular P0 locations')
    labels = sorted({locus.variables.get('L', 'unset') for _, document in sources
                     for locus in document.loci if locus.key in common_regular and locus.present})
    report = {
        'schema_version': 1, 'method': 'exploratory prefix-position source strata v1',
        'selection': {
            'kind': 'P0', 'permitted_locators_in_both_sources': sorted(LOCATORS),
            'shared_present_p0_count': len(common_p0), 'selected_location_count': len(common_regular),
            'excluded_nonregular_locations': sorted(common_p0 - common_regular),
            'sorted_selected_locus_keys_sha256': hashlib.sha256(
                ('\n'.join(sorted(common_regular)) + '\n').encode()).hexdigest(),
            'source_currier_labels_including_unset': labels,
        },
        'sources': [],
    }
    for source, document in sources:
        selected = [locus for locus in document.loci if locus.present and locus.kind == 'P0'
                    and locus.key in common_regular]
        variants = []
        for spacing in ['split', 'join']:
            for alternatives in ['exclude', 'first']:
                rows = prepare_rows(selected, spacing, alternatives)
                cohorts = []
                for label in labels:
                    for starts_paragraph in [False, True]:
                        cohort = [(locus, slots) for locus, slots in rows
                                  if locus.variables.get('L', 'unset') == label and
                                  paragraph_start(locus) == starts_paragraph]
                        positions = []
                        for boundary in ['first', 'last']:
                            summary = summarize_position(cohort, boundary, repetitions, seed)
                            # Select the two features fixed in PREFIX_STRATA_PLAN;
                            # the shared routine's notation-length output is not
                            # part of this prefix-only analysis.
                            summary['features'] = [feature for feature in summary['features']
                                                   if feature['feature'] in PREFIX_FEATURES]
                            if len(summary['features']) != 2:
                                raise ValueError('prefix feature interface changed')
                            positions.append(summary)
                        cohorts.append({'source_currier_label': label,
                                        'source_paragraph_start': starts_paragraph,
                                        'selected_loci': len(cohort), 'positions': positions})
                variants.append({'uncertain_spaces': spacing, 'alternatives': alternatives,
                                 'cohorts': cohorts})
        report['sources'].append({'id': source['id'], 'sha256': source['sha256'], 'variants': variants})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repetitions', type=int, default=199)
    parser.add_argument('--seed', type=int, default=20261011)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        report = stratified_report(args.repetitions, args.seed)
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed stratified report differs from recomputed report')
    except (ValueError, OSError) as error:
        parser.exit(1, f'prefix stratification failed: {error}\n')
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(rendered)
    elif not args.check:
        print(rendered, end='')
    if args.check:
        print('Pinned inputs and committed prefix strata verified.')


if __name__ == '__main__':
    main()
