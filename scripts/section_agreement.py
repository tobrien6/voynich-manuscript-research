"""Sensitivity of catalog-section prefixes to source paragraph-start agreement."""

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .audit_transliterations import ROOT, load_sources
    from .prefix_strata import paragraph_start, select_locations
    from .section_strata import page_assignment, section_report, selected_records, summarize_sections
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from prefix_strata import paragraph_start, select_locations
    from section_strata import page_assignment, section_report, selected_records, summarize_sections
    from token_baselines import paired_sources


def digest(keys):
    return hashlib.sha256(('\n'.join(sorted(keys)) + '\n').encode()).hexdigest()


def agreement_report(sources, baseline, repetitions=199, seed=20261011):
    """Verify the complete baseline before comparing a declared paired filter."""
    sources = paired_sources(sources)
    if section_report(repetitions, seed, sources=sources) != baseline:
        raise ValueError('section baseline differs from recomputed report')
    _, keys = select_locations(sources)
    selected = [selected_records(document, keys) for _, document in sources]
    indexed = [{locus.key: locus for locus in loci} for loci in selected]
    removed = sorted(key for key in keys
                     if paragraph_start(indexed[0][key]) != paragraph_start(indexed[1][key]))
    retained = keys - set(removed)
    assignments = {locus.page: page_assignment(locus.page) for locus in selected[0]}
    report = {
        'schema_version': 1, 'method': 'catalog-section paragraph-start agreement sensitivity v1',
        'selection': {
            'original_selected_location_count': len(keys), 'agreement_selected_location_count': len(retained),
            'sorted_original_locus_keys_sha256': digest(keys),
            'sorted_agreement_locus_keys_sha256': digest(retained),
            'removed_paragraph_start_disagreements': [
                {'key': key, 'ZL3b_paragraph_start': paragraph_start(indexed[0][key]),
                 'IT2a_paragraph_start': paragraph_start(indexed[1][key])} for key in removed],
            'image_boundaries_adjudicated': False, 'token_eligibility_fixed_across_variants': False,
        },
        'sources': [],
    }
    for source_index, ((source, _), loci) in enumerate(zip(sources, selected)):
        agreed = [locus for locus in loci if locus.key in retained]
        variants = []
        for original_variant in baseline['sources'][source_index]['variants']:
            spacing, alternatives = original_variant['uncertain_spaces'], original_variant['alternatives']
            cohorts = summarize_sections(agreed, assignments, spacing, alternatives, repetitions, seed)
            for before, after in zip(original_variant['cohorts'], cohorts):
                if (before['catalog_part'], before['source_paragraph_start']) != (
                        after['catalog_part'], after['source_paragraph_start']):
                    raise ValueError('cohort interface changed')
                before_position = before['first_position']
                after_position = after['first_position']
                comparisons = []
                for old, new in zip(before_position['features'], after_position['features']):
                    if old['feature'] != new['feature']:
                        raise ValueError('feature interface changed')
                    old_effect, new_effect = old['paired_difference'], new['paired_difference']
                    comparisons.append({
                        'feature': old['feature'], 'before': old_effect, 'after': new_effect,
                        'after_minus_before': round(new_effect - old_effect, 8)
                        if old_effect is not None and new_effect is not None else None,
                    })
                after['before_selected_loci'] = before['selected_loci']
                after['removed_selected_loci'] = before['selected_loci'] - after['selected_loci']
                after['before_eligible_loci'] = before_position['eligible_loci']
                after['removed_eligible_loci'] = before_position['eligible_loci'] - after_position['eligible_loci']
                after['feature_comparisons'] = comparisons
            variants.append({'uncertain_spaces': spacing, 'alternatives': alternatives, 'cohorts': cohorts})
        report['sources'].append({'id': source['id'], 'sha256': source['sha256'], 'variants': variants})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, default=ROOT / 'research/transliteration/section_strata.json')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        baseline_bytes = args.baseline.read_bytes()
        report = agreement_report(load_sources(), json.loads(baseline_bytes))
        report['baseline_report_sha256'] = hashlib.sha256(baseline_bytes).hexdigest()
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed section agreement differs from recomputed report')
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
        if args.output:
            args.output.write_text(rendered)
        elif not args.check:
            print(rendered, end='')
    except (ValueError, OSError) as error:
        parser.exit(1, f'section agreement failed: {error}\n')
    if args.check:
        print('Pinned inputs, section baseline, and paragraph-agreement report verified.')


if __name__ == '__main__':
    main()
