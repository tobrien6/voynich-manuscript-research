"""Native endpoint-string edit costs under anchored whole-locus order controls."""

import argparse
from fractions import Fraction
import math
from pathlib import Path

try:
    from .anchored_path_moments import weighted_moments
    from .audit_eva_token_coverage import encoded, IDENTITY_FIELDS
    from .audit_transliterations import ROOT
    from .paragraph_token_corpus import build as build_corpus, coverage, digest, protect_outputs, strict_json
except ImportError:
    from anchored_path_moments import weighted_moments
    from audit_eva_token_coverage import encoded, IDENTITY_FIELDS
    from audit_transliterations import ROOT
    from paragraph_token_corpus import build as build_corpus, coverage, digest, protect_outputs, strict_json


PLAN = Path('research/transliteration/ENDPOINT_EDIT_DISTANCE_PLAN.md')
COVERAGE = Path('research/transliteration/paragraph_corpus_coverage.json')
VERSION = 'anchored-native-endpoint-edit-distance-v1'


def rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def levenshtein(left, right):
    if not isinstance(left, str) or not isinstance(right, str):
        raise ValueError('edit inputs must be strings')
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def normalized_distance(left, right):
    denominator = max(len(left), len(right))
    return Fraction(levenshtein(left, right), denominator) if denominator else Fraction()


def summary(observed, mean, variance, boundaries):
    if variance < 0 or (variance == 0 and observed != mean):
        raise ValueError('cost moments contradict the observed allowed path')
    centered = observed - mean
    sd = math.sqrt(float(variance))
    return {
        'boundary_count': boundaries,
        'observed_cost_sum': rational(observed), 'conditional_mean_cost_sum': rational(mean),
        'conditional_variance_cost_sum': rational(variance), 'centered_cost_sum': rational(centered),
        'observed_mean_cost': float(observed / boundaries) if boundaries else None,
        'conditional_expected_mean_cost': float(mean / boundaries) if boundaries else None,
        'centered_mean_cost': float(centered / boundaries) if boundaries else None,
        'conditional_sd_cost_sum': sd,
        'sd_scaled_contrast': float(centered) / sd if sd else None,
    }


def analyze(corpus):
    common = [p for p in corpus['paragraphs'] if p['common_eligible']]
    if any(not row['tokens'] for p in common for v in p['variants'] for row in v['loci']):
        raise ValueError('nonempty endpoint cohort changed; no silent filtering is permitted')
    totals = {(s['id'], policy): {'observed': Fraction(), 'mean': Fraction(), 'variance': Fraction(),
                                 'boundaries': 0, 'invariant': 0}
              for s in corpus['sources'] for policy in corpus['processing']['uncertain_space_policies']}
    paragraphs = []
    for paragraph in common:
        variants = []
        for variant in paragraph['variants']:
            rows = variant['loci']
            weights = [[None if a == b else normalized_distance(rows[a]['tokens'][-1], rows[b]['tokens'][0])
                        for b in range(len(rows))] for a in range(len(rows))]
            result = weighted_moments(weights)
            key = variant['source_id'], variant['uncertain_spaces']
            total = totals[key]
            total['observed'] += result['observed']
            total['mean'] += result['mean']
            total['variance'] += result['variance']
            total['boundaries'] += len(rows) - 1
            total['invariant'] += result['invariant']
            variants.append({
                'source_id': key[0], 'uncertain_spaces': key[1],
                'loci': [{**{name: row[name] for name in IDENTITY_FIELDS},
                          'token_count': row['token_count'],
                          'drawing_interruption_count': row['drawing_interruption_count'],
                          'uncertain_space_count': row['uncertain_space_count']}
                         for row in rows],
                'cost_matrix': [[rational(w) if w is not None else None for w in row] for row in weights],
                'adjacency_probability_matrix': [[rational(p) if p is not None else None for p in row]
                                                  for row in result['probabilities']],
                **summary(result['observed'], result['mean'], result['variance'], len(rows) - 1),
                'diagonal_variance': rational(result['diagonal_variance']),
                'twice_covariance_sum': rational(result['twice_covariance']),
                **{field: result[field] for field in ('nonzero_weight_possible_edges', 'joint_events_evaluated',
                                                      'zero_joint_events', 'positive_joint_events',
                                                      'possible_interior_orders', 'invariant')},
            })
        paragraphs.append({**{name: paragraph[name] for name in ('common_unit_id', 'page_id', 'member_keys',
                                                                'source_unit_ids')},
                           'variants': variants})
    return {
        'cohort': corpus['cohort'],
        'variants': [{
            'source_id': key[0], 'uncertain_spaces': key[1],
            **summary(t['observed'], t['mean'], t['variance'], t['boundaries']),
            'invariant_paragraphs': t['invariant'], 'varying_paragraphs': len(common) - t['invariant'],
        } for key, t in totals.items()],
        'paragraphs': paragraphs,
    }


def build(root=ROOT):
    corpus = build_corpus(root)
    raw = (root / COVERAGE).read_bytes()
    if encoded(strict_json(raw)) != encoded(coverage(corpus)):
        raise ValueError('parent coverage differs from complete pinned-source corpus replay')
    return {
        'schema_version': 1, 'producer_version': VERSION,
        'analysis_unit': 'native_endpoint_string_cost_across_encoded_loci_within_common_paragraph',
        'sources': corpus['sources'],
        'inputs': {'canonical_corpus_sha256': digest(encoded(corpus)), 'corpus_inputs': corpus['inputs'],
                   'coverage_path': str(COVERAGE), 'coverage_sha256': digest(raw),
                   'plan_path': str(PLAN), 'plan_sha256': digest((root / PLAN).read_bytes()),
                   'implementation_sha256': {name: digest((Path(__file__).parent / name).read_bytes())
                                              for name in ('paragraph_endpoint_distance.py', 'anchored_path_moments.py')}},
        'method': {'distance': 'unit insertion/deletion/substitution Levenshtein over native case-preserved ASCII',
                   'normalization': 'divide by maximum endpoint-string length',
                   'statistic': 'equal-boundary sum/mean normalized cost',
                   'control': 'uniform interior whole-locus identity orders; first/last loci fixed',
                   'moments': 'exact rational single/joint directed-chain adjacency probabilities',
                   'representation': 'native transcription strings; no glyph/phonetic/semantic mapping',
                   'tail_or_decision_criterion': None},
        **analyze(corpus),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    inputs = [ROOT / PLAN, ROOT / COVERAGE, *([args.check] if args.check else [])]
    try:
        protect_outputs([args.output] if args.output else [], inputs, root=ROOT)
        report = build(root=ROOT)
        if args.check and encoded(strict_json(args.check.read_bytes())) != encoded(report):
            raise ValueError('endpoint-distance report differs from complete pinned producer replay')
        if args.output:
            raw = encoded(report)
            protect_outputs([args.output], inputs, root=ROOT)
            args.output.write_bytes(raw)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'endpoint distance failed: {error}\n')
    print(f"Verified {report['cohort']['common_eligible_units']} whole units; all original boundaries retained.")


if __name__ == '__main__':
    main()
