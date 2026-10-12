"""Exploratory first-slot q/y contrasts by catalog range and paragraph mark."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

try:
    from .audit_transliterations import load_sources
    from .locus_positions import prepare_rows, summarize_position
    from .prefix_strata import LOCATORS, PREFIX_FEATURES, paragraph_start, select_locations
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import load_sources
    from locus_positions import prepare_rows, summarize_position
    from prefix_strata import LOCATORS, PREFIX_FEATURES, paragraph_start, select_locations
    from token_baselines import paired_sources


# S002 reports folio-side endpoints; both sides of each numeric interval belong
# to that range. This classifies source names without aligning image regions.
CATALOG_URL = 'https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM'
RANGES = (('I', 1, 66), ('II', 67, 73), ('III', 75, 84),
          ('IV', 85, 86), ('V', 87, 102), ('VI', 103, 117))
GROUPS = tuple(part for part, _, _ in RANGES) + ('unassigned',)


def page_assignment(page):
    """Retain the exact name; never invent a foldout or historical folio alias."""
    if page == 'fRos':
        return {'source_page': page, 'catalog_part': 'unassigned',
                'source_folio_number': None, 'reason': 'non_numeric_page_name'}
    match = re.fullmatch(r'f([1-9][0-9]*)[rv][1-6]?', page)
    if not match:
        raise ValueError(f'unsupported source page name: {page}')
    number = int(match[1])
    part = next((part for part, first, last in RANGES if first <= number <= last), 'unassigned')
    return {'source_page': page, 'catalog_part': part, 'source_folio_number': number,
            'reason': 'numeric_catalog_range' if part != 'unassigned' else 'outside_catalog_ranges'}


def selected_records(document, keys):
    records = [locus for locus in document.loci if locus.present and locus.kind == 'P0'
               and locus.key in keys]
    counts = Counter(locus.key for locus in records)
    if set(counts) != keys or any(count != 1 for count in counts.values()):
        raise ValueError('analysis requires exactly one present P0 record per selected source location')
    return records


def section_report(repetitions=199, seed=20261011):
    if repetitions < 1:
        raise ValueError('repetitions must be positive')
    sources = paired_sources(load_sources())
    common_p0, selected_keys = select_locations(sources)
    if not selected_keys:
        raise ValueError('no paired regular P0 locations')
    selected = [selected_records(document, selected_keys) for _, document in sources]
    assignments = {locus.page: page_assignment(locus.page) for locus in selected[0]}
    paragraphs = [{locus.key: paragraph_start(locus) for locus in loci} for loci in selected]
    report = {
        'schema_version': 1, 'method': 'exploratory first-slot catalog-section prefix strata v1',
        'catalog_grouping': {
            'source_id': 'S002', 'url': CATALOG_URL, 'inspected_date': '2026-10-11',
            'numeric_ranges': [{'part': part, 'first_folio_number': first, 'last_folio_number': last}
                               for part, first, last in RANGES],
            'page_assignments': [assignments[page] for page in sorted(assignments)],
            'image_region_alignment_verified': False,
        },
        'selection': {
            'kind': 'P0', 'permitted_locators_in_both_sources': sorted(LOCATORS),
            'shared_present_p0_count': len(common_p0), 'selected_location_count': len(selected_keys),
            'excluded_nonregular_locations': sorted(common_p0 - selected_keys),
            'sorted_selected_locus_keys_sha256': hashlib.sha256(
                ('\n'.join(sorted(selected_keys)) + '\n').encode()).hexdigest(),
            'source_paragraph_disagreement_locations': sorted(
                key for key in selected_keys if paragraphs[0][key] != paragraphs[1][key]),
        },
        'sources': [],
    }
    for (source, _), loci in zip(sources, selected):
        variants = []
        for spacing in ['split', 'join']:
            for alternatives in ['exclude', 'first']:
                rows = prepare_rows(loci, spacing, alternatives)
                cohorts = []
                for part in GROUPS:
                    for starts_paragraph in [False, True]:
                        cohort = [(locus, slots) for locus, slots in rows
                                  if assignments[locus.page]['catalog_part'] == part and
                                  paragraph_start(locus) == starts_paragraph]
                        summary = summarize_position(cohort, 'first', repetitions, seed)
                        summary['features'] = [feature for feature in summary['features']
                                               if feature['feature'] in PREFIX_FEATURES]
                        if len(summary['features']) != 2:
                            raise ValueError('prefix feature interface changed')
                        cohorts.append({
                            'catalog_part': part, 'source_paragraph_start': starts_paragraph,
                            'selected_loci': len(cohort),
                            'source_page_locus_counts': dict(sorted(Counter(
                                locus.page for locus, _ in cohort).items())),
                            'first_position': summary,
                        })
                if sum(cohort['selected_loci'] for cohort in cohorts) != len(loci):
                    raise ValueError('catalog/paragraph cohorts do not partition the selection')
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
        report = section_report(args.repetitions, args.seed)
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed section report differs from recomputed report')
    except (ValueError, OSError) as error:
        parser.exit(1, f'catalog section analysis failed: {error}\n')
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(rendered)
    elif not args.check:
        print(rendered, end='')
    if args.check:
        print('Pinned inputs and committed catalog section strata verified.')


if __name__ == '__main__':
    main()
