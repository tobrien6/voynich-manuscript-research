"""Compare exploratory position contrasts on fixed transcription cohorts."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

try:
    from .audit_transliterations import load_sources
    from .locus_positions import FEATURES, contrast, features, prepare_rows
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import load_sources
    from locus_positions import FEATURES, contrast, features, prepare_rows
    from token_baselines import paired_sources


def key_digest(keys):
    ordered = sorted(keys)
    text = '\n'.join(ordered) + ('\n' if ordered else '')
    return hashlib.sha256(text.encode('ascii')).hexdigest()


def eligible_contrasts(rows, boundary):
    """Keep original boundary eligibility and one equal-weight vector per key."""
    if boundary not in {'first', 'last'}:
        raise ValueError('boundary must be first or last')
    edge = 0 if boundary == 'first' else -1
    result, seen = {}, set()
    for locus, slots in rows:
        if locus.key in seen:
            raise ValueError(f'duplicate selected locus key: {locus.key}')
        seen.add(locus.key)
        retained = [token for token in slots if token is not None]
        if not slots or slots[edge] is None or len(retained) < 2:
            continue
        vectors = [features(token) for token in retained]
        result[locus.key] = tuple(
            contrast([vector[index] for vector in vectors], edge)
            for index in range(len(FEATURES)))
    return result


def mean(values):
    return math.fsum(values) / len(values) if values else None


def rounded(value):
    return round(value, 8) if value is not None else None


def compare_feature(current, primary, common, index):
    """Compare means and per-key differences without changing the cohort."""
    own_mean = mean([current[key][index] for key in sorted(current)])
    common_mean = mean([current[key][index] for key in common])
    differences = [current[key][index] - primary[key][index] for key in common]
    return {
        'feature': FEATURES[index],
        'own_eligible_mean_contrast': rounded(own_mean),
        'common_cohort_mean_contrast': rounded(common_mean),
        'common_minus_own_mean_contrast': rounded(
            common_mean - own_mean if common_mean is not None else None),
        'paired_mean_difference_from_primary': rounded(mean(differences)),
        'paired_mean_absolute_difference_from_primary': rounded(
            mean([abs(value) for value in differences])),
        'paired_loci_differing_from_primary': sum(
            abs(value) > 1e-12 for value in differences),
    }


def cohort_report():
    sources = paired_sources(load_sources())
    selected_by_source = []
    for source, document in sources:
        selected = {}
        for locus in document.loci:
            if not locus.present or locus.kind != 'P0':
                continue
            if locus.key in selected:
                raise ValueError(f'{source["id"]}: duplicate selected locus key: {locus.key}')
            selected[locus.key] = locus
        selected_by_source.append(selected)
    shared = set.intersection(*(set(selected) for selected in selected_by_source))
    if not shared:
        raise ValueError('no common P0 locations')
    variants = []
    for (source, _), selected in zip(sources, selected_by_source):
        loci = [selected[key] for key in sorted(shared)]
        for spacing in ('split', 'join'):
            for alternatives in ('exclude', 'first'):
                variants.append(({
                    'source': source['id'], 'uncertain_spaces': spacing,
                    'alternatives': alternatives,
                }, prepare_rows(loci, spacing, alternatives)))
    report = {
        'schema_version': 1,
        'method': 'descriptive fixed-cohort position sensitivity v1',
        'selection': {
            'kind': 'P0', 'count': len(shared),
            'sorted_locus_keys_sha256': key_digest(shared),
        },
        'sources': [{'id': source['id'], 'sha256': source['sha256']}
                    for source, _ in sources],
        'primary_variant': variants[0][0],
        'differing_locus_absolute_tolerance': 1e-12,
        'boundaries': [],
    }
    for boundary in ('first', 'last'):
        contrasts = [eligible_contrasts(rows, boundary) for _, rows in variants]
        common = sorted(set.intersection(*(set(values) for values in contrasts)))
        common_set = set(common)
        results = []
        for (metadata, rows), values in zip(variants, contrasts):
            results.append({
                **metadata,
                'own_eligible_loci': len(values),
                'eligible_loci_outside_common_cohort': len(values) - len(common),
                'ineligible_locus_keys': sorted(shared - set(values)),
                'common_cohort_source_locators': dict(sorted(Counter(
                    locus.locator for locus, _ in rows if locus.key in common_set).items())),
                'features': [compare_feature(values, contrasts[0], common, index)
                             for index in range(len(FEATURES))],
            })
        report['boundaries'].append({
            'boundary': boundary, 'common_eligible_loci': len(common),
            'sorted_common_locus_keys_sha256': key_digest(common),
            'variants': results,
        })
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        report = cohort_report()
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed cohort report differs from recomputed report')
    except (ValueError, OSError) as error:
        parser.exit(1, f'cohort comparison failed: {error}\n')
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(rendered)
    elif not args.check:
        print(rendered, end='')
    if args.check:
        print('Pinned inputs and committed cohort report verified.')


if __name__ == '__main__':
    main()
