"""Exact recurrence moments across consecutive encoded paragraph locus boundaries."""

import argparse
from collections import Counter
from fractions import Fraction
import math
from pathlib import Path

try:
    from .audit_eva_token_coverage import encoded, IDENTITY_FIELDS
    from .audit_transliterations import ROOT
    from .paragraph_token_corpus import (
        build as build_corpus, coverage, digest, protect_outputs, strict_json,
    )
except ImportError:
    from audit_eva_token_coverage import encoded, IDENTITY_FIELDS
    from audit_transliterations import ROOT
    from paragraph_token_corpus import (
        build as build_corpus, coverage, digest, protect_outputs, strict_json,
    )


PLAN = Path('research/transliteration/PARAGRAPH_BOUNDARY_PLAN.md')
COVERAGE = Path('research/transliteration/paragraph_corpus_coverage.json')
VERSION = 'encoded-paragraph-boundary-repeat-v1'


def rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def probability(left, right):
    if not left or not right:
        raise ValueError('boundary endpoints must be nonempty loci')
    a, b = Counter(left), Counter(right)
    return Fraction(sum(count * b[token] for token, count in a.items()),
                    len(left) * len(right))


def joint_probability(left, middle, right):
    if not left or not middle or not right:
        raise ValueError('adjacent boundaries must have three nonempty loci')
    a, m, b = Counter(left), Counter(middle), Counter(right)
    diagonal = sum(a[token] * count * b[token] for token, count in m.items())
    if len(middle) == 1:
        return Fraction(diagonal, len(left) * len(right))
    left_overlap = sum(a[token] * count for token, count in m.items())
    right_overlap = sum(b[token] * count for token, count in m.items())
    return Fraction(left_overlap * right_overlap - diagonal,
                    len(left) * len(right) * len(middle) * (len(middle) - 1))


def summary(observed, mean, variance, boundary_count):
    if variance < 0:
        raise ValueError('conditional variance is negative')
    centered = Fraction(observed) - mean
    if variance == 0 and centered != 0:
        raise ValueError('observed ordering contradicts a zero-variance control')
    sd = math.sqrt(float(variance))
    return {
        'eligible_boundaries': boundary_count, 'observed_repeats': observed,
        'conditional_mean': rational(mean), 'conditional_variance': rational(variance),
        'centered_repeat_count': rational(centered),
        'conditional_mean_decimal': float(mean), 'conditional_sd': sd,
        'sd_scaled_contrast': float(centered) / sd if sd else None,
    }


def moments(rows, selected):
    if len(selected) != len(set(selected)) or any(
            type(i) is not int or not 0 <= i < len(rows) - 1 for i in selected):
        raise ValueError('boundary indices must be unique original consecutive locus pairs')
    probabilities = {i: probability(rows[i], rows[i + 1]) for i in selected}
    boundaries = [{
        'boundary_index': i,
        'observed_repeat': int(rows[i][-1] == rows[i + 1][0]),
        'repeat_probability': rational(p), 'variance': rational(p * (1 - p)),
    } for i, p in sorted(probabilities.items())]
    adjacent = []
    variance = sum((p * (1 - p) for p in probabilities.values()), Fraction())
    for i in sorted(probabilities):
        if i + 1 in probabilities:
            joint = joint_probability(rows[i], rows[i + 1], rows[i + 2])
            covariance = joint - probabilities[i] * probabilities[i + 1]
            variance += 2 * covariance
            adjacent.append({'left_boundary_index': i, 'right_boundary_index': i + 1,
                             'joint_repeat_probability': rational(joint),
                             'covariance': rational(covariance)})
    mean = sum(probabilities.values(), Fraction())
    observed = sum(row['observed_repeat'] for row in boundaries)
    return {**summary(observed, mean, variance, len(selected)),
            'boundaries': boundaries, 'adjacent_boundary_covariances': adjacent}


def fraction(field):
    return Fraction(field['numerator'], field['denominator'])


def analyze(corpus):
    paragraphs, totals = [], {}
    for source in corpus['sources']:
        for policy in corpus['processing']['uncertain_space_policies']:
            totals[source['id'], policy] = {'observed': 0, 'mean': Fraction(),
                                           'variance': Fraction(), 'boundaries': 0}
    for paragraph in corpus['paragraphs']:
        if not paragraph['common_eligible']:
            continue
        selected, boundary_ledger = [], []
        for i in range(len(paragraph['member_keys']) - 1):
            failures = [{'source_id': v['source_id'], 'uncertain_spaces': v['uncertain_spaces'],
                         'empty_locus_keys': [v['loci'][j]['locus_key'] for j in (i, i + 1)
                                              if not v['loci'][j]['tokens']]}
                        for v in paragraph['variants']
                        if any(not v['loci'][j]['tokens'] for j in (i, i + 1))]
            if not failures:
                selected.append(i)
            boundary_ledger.append({'boundary_index': i,
                                    'left_key': paragraph['member_keys'][i],
                                    'right_key': paragraph['member_keys'][i + 1],
                                    'eligible_in_all_variants': not failures,
                                    'omission_reasons': failures})
        variants = []
        for variant in paragraph['variants']:
            rows = [row['tokens'] for row in variant['loci']]
            result = moments(rows, selected)
            total = totals[variant['source_id'], variant['uncertain_spaces']]
            total['observed'] += result['observed_repeats']
            total['mean'] += fraction(result['conditional_mean'])
            total['variance'] += fraction(result['conditional_variance'])
            total['boundaries'] += result['eligible_boundaries']
            variants.append({
                'source_id': variant['source_id'], 'uncertain_spaces': variant['uncertain_spaces'],
                'loci': [{**{key: row[key] for key in IDENTITY_FIELDS},
                          'token_count': row['token_count'],
                          'uncertain_space_count': row['uncertain_space_count'],
                          'drawing_interruption_count': row['drawing_interruption_count']}
                         for row in variant['loci']],
                **result,
            })
        paragraphs.append({
            **{key: paragraph[key] for key in ('common_unit_id', 'page_id', 'member_keys',
                                             'source_unit_ids')},
            'boundary_ledger': boundary_ledger, 'variants': variants,
        })
    return {
        'cohort': {
            **corpus['cohort'], 'common_paragraphs_with_no_eligible_boundaries': sum(
                not any(b['eligible_in_all_variants'] for b in p['boundary_ledger']) for p in paragraphs),
            'candidate_boundaries_in_common_paragraphs': sum(len(p['boundary_ledger']) for p in paragraphs),
            'eligible_boundaries_in_all_variants': sum(b['eligible_in_all_variants']
                for p in paragraphs for b in p['boundary_ledger']),
        },
        'variants': [{'source_id': source, 'uncertain_spaces': policy,
                      **summary(t['observed'], t['mean'], t['variance'], t['boundaries'])}
                     for (source, policy), t in totals.items()],
        'paragraphs': paragraphs,
    }


def build(root=ROOT):
    corpus = build_corpus(root)
    coverage_raw = (root / COVERAGE).read_bytes()
    if encoded(strict_json(coverage_raw)) != encoded(coverage(corpus)):
        raise ValueError('parent paragraph coverage differs from complete producer replay')
    return {
        'schema_version': 1, 'producer_version': VERSION,
        'analysis_unit': 'consecutive_encoded_locus_boundary_within_common_paragraph',
        'inputs': {'canonical_corpus_sha256': digest(encoded(corpus)),
                   'parent_corpus_inputs': corpus['inputs'],
                   'coverage_path': str(COVERAGE), 'coverage_sha256': digest(coverage_raw),
                   'plan_path': str(PLAN), 'plan_sha256': digest((root / PLAN).read_bytes()),
                   'implementation_sha256': digest(Path(__file__).read_bytes())},
        'sources': corpus['sources'],
        'control': {'scope': 'independent uniform token-occurrence permutation within original loci',
                    'statistic': 'count exact last-left / first-right token equality',
                    'arithmetic': 'exact rational means, variances and adjacent-boundary covariances',
                    'tail_or_decision_criterion': None},
        **analyze(corpus),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        protect_outputs([args.output] if args.output else [],
                        [ROOT / PLAN, ROOT / COVERAGE, *([args.check] if args.check else [])], root=ROOT)
        report = build(root=ROOT)
        if args.check and encoded(strict_json(args.check.read_bytes())) != encoded(report):
            raise ValueError('boundary report differs from complete pinned producer replay')
        if args.output:
            output_bytes = encoded(report)
            protect_outputs([args.output], [ROOT / PLAN, ROOT / COVERAGE], root=ROOT)
            args.output.write_bytes(output_bytes)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'paragraph boundary report failed: {error}\n')
    print(f"Verified {report['cohort']['common_eligible_units']} common paragraphs; "
          f"{report['cohort']['eligible_boundaries_in_all_variants']} encoded boundaries.")


if __name__ == '__main__':
    main()
