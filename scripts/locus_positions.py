"""Exploratory locus-edge effects with conditional within-locus controls."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random

try:
    from .audit_transliterations import load_sources
    from .ivtff import without_free_comments
    from .token_baselines import paired_sources, retain, tokenize
except ImportError:
    from audit_transliterations import load_sources
    from ivtff import without_free_comments
    from token_baselines import paired_sources, retain, tokenize


FEATURES = ('literal_q_prefix', 'literal_y_prefix', 'notation_units')


def features(token):
    return (int(token.value.startswith('q')), int(token.value.startswith('y')), token.units)


def contrast(values, edge):
    """Boundary value minus mean of all other retained values."""
    if len(values) < 2:
        raise ValueError('a contrast needs at least two retained tokens')
    return values[edge] - (sum(values) - values[edge]) / (len(values) - 1)


def conditional_variance(values):
    """Exact variance of the contrast when the boundary token is uniform."""
    count = len(values)
    if count < 2:
        raise ValueError('a variance needs at least two retained tokens')
    mean = sum(values) / count
    population_variance = sum((value - mean) ** 2 for value in values) / count
    return (count / (count - 1)) ** 2 * population_variance


def prepare_rows(loci, spacing, alternatives):
    rows = []
    for locus in loci:
        try:
            tokens = tokenize(locus.text, spacing)
        except ValueError as error:
            raise ValueError(f'{locus.identifier}: {error}') from error
        slots = [token if retain(token, alternatives) else None for token in tokens]
        rows.append((locus, slots))
    return rows


def summarize_position(rows, boundary, repetitions, seed):
    if boundary not in {'first', 'last'}:
        raise ValueError('boundary must be first or last')
    if repetitions < 1:
        raise ValueError('repetitions must be positive')
    eligible, unavailable, insufficient = [], 0, 0
    for locus, slots in rows:
        retained = [token for token in slots if token is not None]
        available = bool(slots) and slots[0 if boundary == 'first' else -1] is not None
        unavailable += not available
        insufficient += len(retained) < 2
        if available and len(retained) >= 2:
            eligible.append((locus, [features(token) for token in retained]))
    edge = 0 if boundary == 'first' else -1
    count = len(eligible)
    observed, means_edge, means_other, variances = [0.0] * 3, [0.0] * 3, [0.0] * 3, [0.0] * 3
    for _, vectors in eligible:
        for index in range(3):
            values = [vector[index] for vector in vectors]
            observed[index] += contrast(values, edge)
            means_edge[index] += values[edge]
            means_other[index] += (sum(values) - values[edge]) / (len(values) - 1)
            variances[index] += conditional_variance(values)
    if count:
        observed = [value / count for value in observed]
        means_edge = [value / count for value in means_edge]
        means_other = [value / count for value in means_other]
        variances = [value / count ** 2 for value in variances]
    rng = random.Random(seed)
    nulls = [[] for _ in FEATURES]
    if count:
        for _ in range(repetitions):
            totals = [0.0] * 3
            for _, vectors in eligible:
                shuffled = vectors.copy()
                rng.shuffle(shuffled)
                for index in range(3):
                    totals[index] += contrast([vector[index] for vector in shuffled], edge)
            for index in range(3):
                nulls[index].append(totals[index] / count)
    output = []
    for index, name in enumerate(FEATURES):
        output.append({
            'feature': name,
            'mean_boundary_feature': round(means_edge[index], 8) if count else None,
            'mean_locus_other_feature': round(means_other[index], 8) if count else None,
            'paired_difference': round(observed[index], 8) if count else None,
            'exact_null_expectation': 0.0 if count else None,
            'exact_null_standard_deviation': round(math.sqrt(variances[index]), 8) if count else None,
            'shuffle_differences': [round(value, 8) for value in nulls[index]],
            'exploratory_two_sided_tail': (
                (1 + sum(abs(value) >= abs(observed[index]) - 1e-12 for value in nulls[index])) /
                (repetitions + 1)) if count else None,
        })
    return {
        'boundary': boundary, 'eligible_loci': count,
        'ineligible_reasons_may_overlap': {'boundary_unavailable': unavailable,
                                         'fewer_than_two_retained': insufficient},
        'eligible_source_paragraph_starts': sum('<%>' in without_free_comments(locus.text)
                                               for locus, _ in eligible),
        'eligible_source_currier_labels': dict(sorted(Counter(
            locus.variables.get('L', 'unset') for locus, _ in eligible).items())),
        'eligible_source_locators': dict(sorted(Counter(locus.locator for locus, _ in eligible).items())),
        'shuffle_repetitions': repetitions, 'seed': seed, 'features': output,
    }


def position_report(repetitions=199, seed=20261011):
    if repetitions < 1:
        raise ValueError('repetitions must be positive')
    sources = paired_sources(load_sources())
    common = set.intersection(*[
        {locus.key for locus in doc.loci if locus.present and locus.kind == 'P0'}
        for _, doc in sources])
    if not common:
        raise ValueError('no common P0 locations')
    report = {
        'schema_version': 1, 'method': 'exploratory equal-locus-weight position effects v1',
        'selection': {'kind': 'P0', 'count': len(common),
                      'sorted_locus_keys_sha256': hashlib.sha256(
                          ('\n'.join(sorted(common)) + '\n').encode()).hexdigest()},
        'sources': [],
    }
    for source, document in sources:
        selected = [locus for locus in document.loci if locus.present and
                    locus.kind == 'P0' and locus.key in common]
        variants = []
        for spacing in ['split', 'join']:
            for alternatives in ['exclude', 'first']:
                rows = prepare_rows(selected, spacing, alternatives)
                variants.append({
                    'uncertain_spaces': spacing, 'alternatives': alternatives,
                    'positions': [summarize_position(rows, boundary, repetitions, seed)
                                  for boundary in ['first', 'last']],
                })
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
        report = position_report(args.repetitions, args.seed)
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed position report differs from recomputed report')
    except (ValueError, OSError) as error:
        parser.exit(1, f'position analysis failed: {error}\n')
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(rendered)
    elif not args.check:
        print(rendered, end='')
    if args.check:
        print('Pinned inputs and committed position report verified.')


if __name__ == '__main__':
    main()
