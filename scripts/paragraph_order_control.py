"""Exact boundary-repeat moments under anchored whole-locus order permutations."""

import argparse
from fractions import Fraction
from itertools import combinations
from math import factorial
from pathlib import Path

try:
    from .audit_eva_token_coverage import encoded, IDENTITY_FIELDS
    from .audit_transliterations import ROOT
    from .paragraph_boundary_repetition import build as build_parent, rational, fraction, summary
    from .paragraph_token_corpus import build as build_corpus, digest, protect_outputs, strict_json
except ImportError:
    from audit_eva_token_coverage import encoded, IDENTITY_FIELDS
    from audit_transliterations import ROOT
    from paragraph_boundary_repetition import build as build_parent, rational, fraction, summary
    from paragraph_token_corpus import build as build_corpus, digest, protect_outputs, strict_json


PLAN = Path('research/transliteration/PARAGRAPH_ORDER_PLAN.md')
PARENT = Path('research/transliteration/paragraph_boundary_repetition.json')
COVERAGE = Path('research/transliteration/paragraph_corpus_coverage.json')
VERSION = 'anchored-whole-locus-order-repeat-v1'


def constraints_probability(size, edges):
    """Count fixed-anchor orders satisfying directed adjacency requirements."""
    if type(size) is not int or size < 1:
        raise ValueError('a paragraph must have at least one locus identity')
    requirements = set()
    for edge in edges:
        if len(edge) != 2 or any(type(i) is not int or not 0 <= i < size for i in edge):
            raise ValueError('edge identities must be original locus indices')
        requirements.add(tuple(edge))
    successor, predecessor = {}, {}
    for left, right in sorted(requirements):
        if left == right or right == 0 or left == size - 1:
            return Fraction()
        if left in successor or right in predecessor:
            return Fraction()
        successor[left], predecessor[right] = right, left
    chains, seen = [], set()
    for start in range(size):
        if start in predecessor:
            continue
        chain, node = [], start
        while node is not None:
            chain.append(node)
            seen.add(node)
            node = successor.get(node)
        chains.append(chain)
    if len(seen) != size:  # A directed cycle has no chain root.
        return Fraction()
    first = next(chain for chain in chains if 0 in chain)
    last = next(chain for chain in chains if size - 1 in chain)
    orders = factorial(max(size - 2, 0))
    if first == last:
        return Fraction(1, orders) if len(first) == size else Fraction()
    return Fraction(factorial(len(chains) - 2), orders)


def order_moments(rows):
    if not rows or any(not row for row in rows):
        raise ValueError('whole-locus control requires all original loci nonempty')
    size = len(rows)
    edges = [(left, right) for left in range(size) for right in range(size)
             if left != right and rows[left][-1] == rows[right][0]]
    probabilities = [constraints_probability(size, [edge]) for edge in edges]
    mean = sum(probabilities, Fraction())
    variance = sum((p * (1 - p) for p in probabilities), Fraction())
    covariances = []
    for a, b in combinations(range(len(edges)), 2):
        joint = (constraints_probability(size, [edges[a], edges[b]])
                 if probabilities[a] and probabilities[b] else Fraction())
        covariance = joint - probabilities[a] * probabilities[b]
        variance += 2 * covariance
        covariances.append({'left_edge_index': a, 'right_edge_index': b,
                            'joint_probability': rational(joint),
                            'covariance': rational(covariance)})
    observed = sum(rows[i][-1] == rows[i + 1][0] for i in range(size - 1))
    return {
        **summary(observed, mean, variance, size - 1),
        'locus_count': size, 'permuted_interior_locus_count': max(size - 2, 0),
        'possible_interior_orders': factorial(max(size - 2, 0)),
        'invariant_repeat_count': variance == 0,
        'endpoint_match_edges': [{'left_locus_index': edge[0], 'right_locus_index': edge[1],
                                 'probability': rational(p)} for edge, p in zip(edges, probabilities)],
        'edge_pair_covariances': covariances,
    }


def analyze(corpus, parent):
    common = [p for p in corpus['paragraphs'] if p['common_eligible']]
    parent_units = {p['common_unit_id']: p for p in parent['paragraphs']}
    if len(parent_units) != len(parent['paragraphs']) or set(parent_units) != {
            p['common_unit_id'] for p in common}:
        raise ValueError('parent and corpus have different complete unit identities')
    totals = {(s['id'], policy): {'observed': 0, 'mean': Fraction(), 'variance': Fraction(),
                                 'boundaries': 0, 'invariant': 0}
              for s in corpus['sources'] for policy in corpus['processing']['uncertain_space_policies']}
    paragraphs = []
    for paragraph in common:
        previous = parent_units[paragraph['common_unit_id']]
        if previous['member_keys'] != paragraph['member_keys'] or \
                len(previous['boundary_ledger']) != len(paragraph['member_keys']) - 1 or \
                any(not b['eligible_in_all_variants'] for b in previous['boundary_ledger']):
            raise ValueError('parent omits an original boundary; do not silently change the cohort')
        if any(not row['tokens'] for variant in paragraph['variants'] for row in variant['loci']):
            raise ValueError('a retained locus is empty; whole-locus order cohort cannot change')
        prior_variants = {(v['source_id'], v['uncertain_spaces']): v for v in previous['variants']}
        variants = []
        for variant in paragraph['variants']:
            key = variant['source_id'], variant['uncertain_spaces']
            result = order_moments([row['tokens'] for row in variant['loci']])
            if result['observed_repeats'] != prior_variants[key]['observed_repeats']:
                raise ValueError('observed repeat count differs from the verified parent statistic')
            total = totals[key]
            total['observed'] += result['observed_repeats']
            total['mean'] += fraction(result['conditional_mean'])
            total['variance'] += fraction(result['conditional_variance'])
            total['boundaries'] += result['eligible_boundaries']
            total['invariant'] += result['invariant_repeat_count']
            variants.append({
                'source_id': key[0], 'uncertain_spaces': key[1],
                'loci': [{**{field: row[field] for field in IDENTITY_FIELDS},
                          'token_count': row['token_count'],
                          'drawing_interruption_count': row['drawing_interruption_count'],
                          'uncertain_space_count': row['uncertain_space_count']}
                         for row in variant['loci']],
                **result,
            })
        paragraphs.append({
            **{key: paragraph[key] for key in ('common_unit_id', 'page_id', 'member_keys', 'source_unit_ids')},
            'variants': variants,
        })
    return {
        'cohort': corpus['cohort'], 'parent_within_locus_control_summaries': parent['variants'],
        'variants': [{
            'source_id': key[0], 'uncertain_spaces': key[1],
            **summary(total['observed'], total['mean'], total['variance'], total['boundaries']),
            'invariant_paragraphs': total['invariant'],
            'varying_paragraphs': len(common) - total['invariant'],
        } for key, total in totals.items()],
        'paragraphs': paragraphs,
    }


def build(root=ROOT):
    parent_raw = (root / PARENT).read_bytes()
    parent = strict_json(parent_raw)
    if encoded(parent) != encoded(build_parent(root)):
        raise ValueError('parent boundary report differs from complete pinned producer replay')
    corpus = build_corpus(root)
    return {
        'schema_version': 1, 'producer_version': VERSION,
        'analysis_unit': 'anchored_order_of_atomic_loci_within_common_encoded_paragraph',
        'sources': corpus['sources'],
        'inputs': {'canonical_corpus_sha256': digest(encoded(corpus)),
                   'parent_report_path': str(PARENT), 'parent_report_sha256': digest(parent_raw),
                   'parent_inputs': parent['inputs'], 'plan_path': str(PLAN),
                   'plan_sha256': digest((root / PLAN).read_bytes()),
                   'implementation_sha256': digest(Path(__file__).read_bytes())},
        'control': {'scope': 'independent uniform interior whole-locus orders; first/last loci fixed',
                    'preserved': 'every original locus identity, metadata and complete token sequence',
                    'statistic': 'unchanged exact final-left / first-right token equality count',
                    'moments': 'exact rational directed-chain event counts and all edge-pair covariances',
                    'tail_or_decision_criterion': None},
        **analyze(corpus, parent),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        protect_outputs([args.output] if args.output else [],
                        [ROOT / PLAN, ROOT / PARENT, ROOT / COVERAGE,
                         *([args.check] if args.check else [])], root=ROOT)
        report = build(root=ROOT)
        if args.check and encoded(strict_json(args.check.read_bytes())) != encoded(report):
            raise ValueError('paragraph-order report differs from complete pinned producer replay')
        if args.output:
            output_bytes = encoded(report)
            protect_outputs([args.output], [ROOT / PLAN, ROOT / PARENT, ROOT / COVERAGE], root=ROOT)
            args.output.write_bytes(output_bytes)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'paragraph order control failed: {error}\n')
    print(f"Verified {report['cohort']['common_eligible_units']} whole paragraph units; "
          'original locus endpoint roles preserved.')


if __name__ == '__main__':
    main()
