"""Exact expected distinct self-repeating representations under locus shuffles."""

import argparse
from collections import Counter
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path

try:
    from .audit_transliterations import load_sources
    from .repetition_moments import conditional_moments
    from .token_baselines import paired_sources, retain, tokenize
    from .validate_evaluation_split import load_split_json
except ImportError:
    from audit_transliterations import load_sources
    from repetition_moments import conditional_moments
    from token_baselines import paired_sources, retain, tokenize
    from validate_evaluation_split import load_split_json


ROOT = Path(__file__).resolve().parents[1]
PLAN = 'research/transliteration/REPEATING_TYPES_PLAN.md'
BASELINE = 'research/transliteration/token_baselines.json'
ENGINES = ('scripts/repeating_types.py', 'scripts/repetition_moments.py',
           'scripts/token_baselines.py', 'scripts/audit_transliterations.py',
           'scripts/ivtff.py', 'scripts/validate_evaluation_split.py')


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')


def fraction_text(value):
    """Format exact integers without changing Python's integer-string limits.

    Decimal construction from an integer is exact, independent of precision.
    No decimal arithmetic or rounding enters the rational calculation.
    """
    numerator = format(Decimal(value.numerator), 'f')
    return numerator if value.denominator == 1 else numerator + '/' + format(Decimal(value.denominator), 'f')


@lru_cache(maxsize=8192)
def _coefficients(components):
    coefficients = [1]
    for length in components:
        factor = [math.comb(length - k + 1, k) for k in range((length + 1) // 2 + 1)]
        coefficients = [sum(coefficients[degree - k] * factor[k]
                            for k in range(max(0, degree - len(coefficients) + 1),
                                           min(degree, len(factor) - 1) + 1))
                        for degree in range(len(coefficients) + len(factor) - 1)]
    return tuple(coefficients)


def independent_set_count(components, count):
    """Size-count independent sets of disjoint paths, using integer arithmetic."""
    if (not isinstance(components, (tuple, list)) or
            any(type(length) is not int or length < 1 for length in components) or
            type(count) is not int or not 0 <= count <= sum(components)):
        raise ValueError('require positive path lengths and an integer subset size within their total')
    coefficients = _coefficients(tuple(sorted(components)))
    return coefficients[count] if count < len(coefficients) else 0


def no_repeat_probability(components, count):
    """A type's occupied retained positions are a uniform size-count subset."""
    numerator = independent_set_count(components, count)
    return Fraction(numerator, math.comb(sum(components), count))


def adjacency_graph(slots):
    if not isinstance(slots, (list, tuple)) or any(
            value is not None and (not isinstance(value, str) or not value) for value in slots):
        raise ValueError('slots must be a sequence of nonempty representations or null exclusions')
    values, edges, components = [], [], []
    run = 0
    for value in slots:
        if value is None:
            if run:
                components.append(run)
                run = 0
        else:
            if run:
                edges.append((len(values) - 1, len(values)))
            values.append(value)
            run += 1
    if run:
        components.append(run)
    return values, edges, components


def summarize(rows):
    rows = list(rows)
    keys = [key for key, _ in rows]
    if any(not isinstance(key, str) or not key for key in keys) or len(set(keys)) != len(keys):
        raise ValueError('supply unique nonempty locus keys')
    rows.sort(key=lambda row: row[0])
    vocabulary, repeats, no_repeat = set(), Counter(), {}
    eligible_pairs = retained = 0
    expected_pairs = Fraction()
    for _, slots in rows:
        values, edges, components = adjacency_graph(slots)
        vocabulary.update(values)
        retained += len(values)
        eligible_pairs += len(edges)
        expected_pairs += conditional_moments(values, edges)['expected']
        repeats.update(values[a] for a, b in edges if values[a] == values[b])
        if edges:
            for value, count in Counter(values).items():
                if count >= 2:
                    q = no_repeat_probability(components, count)
                    no_repeat[value] = no_repeat.get(value, Fraction(1)) * q
    expected_types = sum((1 - q for q in no_repeat.values()), Fraction())
    if expected_types > expected_pairs or not set(repeats) <= set(no_repeat):
        raise ValueError('type count contradicts its pair-event expectation or opportunities')
    digest = hashlib.sha256(json.dumps(rows, ensure_ascii=True, separators=(',', ':')).encode('ascii')).hexdigest()
    return {
        'selected_loci': len(rows), 'apparent_token_slots': sum(len(slots) for _, slots in rows),
        'retained_tokens': retained, 'distinct_representations': len(vocabulary),
        'eligible_adjacent_pairs': eligible_pairs, 'observed_equal_pair_events': sum(repeats.values()),
        'conditional_expected_pair_events_fraction': fraction_text(expected_pairs),
        'conditional_expected_pair_events': round(float(expected_pairs), 8),
        'repetition_capable_types_under_control': len(no_repeat),
        'observed_distinct_repeating_types': len(repeats),
        'conditional_expected_repeating_types_fraction': fraction_text(expected_types),
        'conditional_expected_repeating_types': round(float(expected_types), 8),
        'observed_minus_expected_types_fraction': fraction_text(len(repeats) - expected_types),
        'observed_minus_expected_types': round(float(len(repeats) - expected_types), 8),
        'observed_event_counts_per_repeating_type': {str(k): v for k, v in sorted(Counter(repeats.values()).items())},
        'preprocessed_loci_sha256': digest,
    }


def verify_pair_baseline(result, baseline):
    if encoded(tuple(result['selection'][key] for key in ('kind', 'count', 'sorted_locus_keys_sha256'))) != encoded(
            tuple(baseline['selection'][key] for key in ('kind', 'count', 'sorted_locus_keys_sha256'))):
        raise ValueError('cohort differs from the accepted pair baseline')
    for source in result['sources']:
        matching = [row for row in baseline['sources'] if row['id'] == source['id']]
        if len(matching) != 1 or matching[0]['sha256'] != source['sha256']:
            raise ValueError('source differs from the accepted pair baseline')
        for variant in source['variants']:
            policies = [row for row in matching[0]['variants'] if
                        (row['uncertain_spaces'], row['alternatives']) ==
                        (variant['uncertain_spaces'], variant['alternatives'])]
            if len(policies) != 1:
                raise ValueError('policy differs from the accepted pair baseline')
            reference = policies[0]
            expected = (reference['selected_loci'], reference['apparent_token_slots'],
                        reference['retained_tokens'], reference['distinct_representations'],
                        reference['adjacent_repetition']['eligible_pairs'],
                        reference['adjacent_repetition']['observed_equal_pairs'],
                        reference['adjacent_repetition']['exact_conditional_expected_pairs'])
            actual = tuple(variant[key] for key in ('selected_loci', 'apparent_token_slots',
                           'retained_tokens', 'distinct_representations', 'eligible_adjacent_pairs',
                           'observed_equal_pair_events', 'conditional_expected_pair_events'))
            if encoded(actual) != encoded(expected):
                raise ValueError('pair-event diagnostics differ from the accepted baseline')


def report():
    sources = paired_sources(load_sources(root=ROOT))
    common = set.intersection(*[{locus.key for locus in document.loci if locus.present and locus.kind == 'P0'}
                               for _, document in sources])
    if not common:
        raise ValueError('no common present P0 loci')
    baseline_raw = (ROOT / BASELINE).read_bytes()
    result = {
        'schema_version': 1, 'method': 'distinct repeating representations under fixed-gap locus shuffles v1',
        'source_catalog_sha256': hashlib.sha256((ROOT / 'data/transliterations.json').read_bytes()).hexdigest(),
        'plan_sha256': hashlib.sha256((ROOT / PLAN).read_bytes()).hexdigest(),
        'baseline_sha256': hashlib.sha256(baseline_raw).hexdigest(),
        'engine_sha256': {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in ENGINES},
        'selection': {'kind': 'P0', 'count': len(common),
                      'sorted_locus_keys_sha256': hashlib.sha256(('\n'.join(sorted(common)) + '\n').encode()).hexdigest()},
        'control': 'independent uniform token-bag permutations within original loci; exclusions fixed',
        'preprocessed_digest_encoding': 'ASCII compact JSON of sorted [locus_key, original_slots] rows; null exclusions',
        'limits': ['Exposed exploratory cohort, not a replication of historical inputs or whole-text shuffles.',
                   'Type indicators are dependent; no variance, tail or confidence derived from the expectation.',
                   'Representations and source loci are not adjudicated words, glyphs or physical lines.'],
        'sources': [],
    }
    for source, document in sources:
        selected = sorted((locus for locus in document.loci if locus.key in common
                           and locus.present and locus.kind == 'P0'), key=lambda locus: locus.key)
        variants = []
        for spacing in ('split', 'join'):
            for alternatives in ('exclude', 'first'):
                rows = []
                for locus in selected:
                    tokens = tokenize(locus.text, spacing)
                    rows.append([locus.key, [token.value if retain(token, alternatives) else None for token in tokens]])
                variants.append({'uncertain_spaces': spacing, 'alternatives': alternatives, **summarize(rows)})
        result['sources'].append({'id': source['id'], 'url': source['url'], 'sha256': source['sha256'], 'variants': variants})
    verify_pair_baseline(result, load_split_json(baseline_raw.decode('utf-8')))
    return result


def protect_output(output):
    catalog = ROOT / 'data/transliterations.json'
    inputs = [catalog, ROOT / PLAN, ROOT / BASELINE, *(ROOT / path for path in ENGINES)]
    inputs += [ROOT / source['path'] for source in load_split_json(catalog.read_text())['sources']]
    for path in inputs:
        if output.resolve() == path.resolve() or (output.exists() and path.exists() and output.samefile(path)):
            raise ValueError('output aliases a pinned source, baseline, plan or calculation file')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output)
        result = report()
        if args.check:
            if encoded(load_split_json(args.check.read_text())) != encoded(result):
                raise ValueError('recorded repeating-type report differs from recomputation')
            print('Pinned cohort, pair reference and distinct repeating-type expectations verified.')
        elif args.output:
            protect_output(args.output)
            args.output.write_bytes(encoded(result))
        else:
            print(encoded(result).decode('utf-8'), end='')
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'repeating types failed: {error}\n')


if __name__ == '__main__':
    main()
