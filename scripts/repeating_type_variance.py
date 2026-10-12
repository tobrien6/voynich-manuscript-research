"""Exact conditional type-count variance with signed finite-bag covariances."""

import argparse
from collections import Counter, defaultdict
from decimal import Context, Decimal, localcontext, MAX_EMAX, MIN_EMIN, ROUND_HALF_EVEN
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
import hashlib
import math
from pathlib import Path

try:
    from . import repeating_types as parent
except ImportError:
    import repeating_types as parent


ROOT = parent.ROOT
PLAN = 'research/transliteration/REPEATING_TYPE_VARIANCE_PLAN.md'
MEAN_REPORT = 'research/transliteration/repeating_types.json'
ENGINE = 'scripts/repeating_type_variance.py'
PRECISION = 50


@lru_cache(maxsize=8192)
def _joint_count(components, ca, cb):
    other = sum(components) - ca - cb
    states = {(0, 0, 0): 1}
    processed = 0
    for length in components:
        reset = Counter()
        for (a, b, last), ways in states.items():
            reset[a, b, 0] += ways
        states = reset
        for _ in range(length):
            following = Counter()
            for (a, b, last), ways in states.items():
                if processed - a - b < other:
                    following[a, b, 0] += ways
                if a < ca and last != 1:
                    following[a + 1, b, 1] += ways
                if b < cb and last != 2:
                    following[a, b + 1, 2] += ways
            states = following
            processed += 1
    return sum(ways for (a, b, last), ways in states.items() if a == ca and b == cb)


def joint_no_repeat_probability(components, ca, cb):
    """Uniform marked A/B placements; only AA and BB adjacency are forbidden."""
    parent.independent_set_count(components, 0)  # Validate retained-run sizes.
    m = sum(components)
    if any(type(count) is not int or count < 0 for count in (ca, cb)) or ca + cb > m:
        raise ValueError('marked counts must be nonnegative integers within retained positions')
    if ca <= 1:
        return parent.no_repeat_probability(components, cb)
    if cb <= 1:
        return parent.no_repeat_probability(components, ca)
    if not parent.no_repeat_probability(components, ca) or not parent.no_repeat_probability(components, cb):
        return Fraction()
    counts = sorted((ca, cb))
    numerator = _joint_count(tuple(sorted(components)), *counts)
    return Fraction(numerator, math.comb(m, ca) * math.comb(m - ca, cb))


def diagnostics(variance, centered):
    if variance < 0 or (variance == 0 and centered != 0):
        raise ValueError('invalid variance or observed ordering under a constant control')
    context = Context(prec=PRECISION, rounding=ROUND_HALF_EVEN, Emax=MAX_EMAX, Emin=MIN_EMIN)
    with localcontext(context):
        decimal_variance = Decimal(variance.numerator) / Decimal(variance.denominator)
        sd = decimal_variance.sqrt()
        contrast = (Decimal(centered.numerator) / Decimal(centered.denominator) / sd) if variance else None
    def finite_float(value):
        if value is None:
            return None
        converted = float(value)
        return converted if math.isfinite(converted) and (converted != 0 or value == 0) else None
    return {
        'zero_conditional_variance': not bool(variance),
        'conditional_variance_approx': finite_float(decimal_variance),
        'conditional_variance_decimal': str(decimal_variance),
        'conditional_standard_deviation': finite_float(sd),
        'conditional_standard_deviation_decimal': str(sd),
        'observed_minus_expected_in_sd': finite_float(contrast),
        'observed_minus_expected_in_sd_decimal': str(contrast) if contrast is not None else None,
        'decimal_diagnostic_precision': PRECISION,
    }


def summarize(rows):
    rows = list(rows)
    base = parent.summarize(rows)
    global_q, local_records = {}, []
    for _, slots in rows:
        values, edges, components = parent.adjacency_graph(slots)
        if not edges:
            continue
        counts = {value: count for value, count in Counter(values).items() if count >= 2}
        local_q = {value: parent.no_repeat_probability(components, count) for value, count in counts.items()}
        for value, q in local_q.items():
            global_q[value] = global_q.get(value, Fraction(1)) * q
        local_records.append((components, counts, local_q))
    possible_pairs, corrections = set(), defaultdict(lambda: Fraction(1))
    for components, counts, local_q in local_records:
        for a, b in combinations(sorted(counts), 2):
            possible_pairs.add((a, b))
            if not global_q[a] or not global_q[b]:
                continue  # Exact forced-repeat indicators have zero covariance.
            joint = joint_no_repeat_probability(components, counts[a], counts[b])
            corrections[a, b] *= joint / (local_q[a] * local_q[b])
    covariance = [global_q[a] * global_q[b] * (correction - 1)
                  for (a, b), correction in corrections.items()]
    marginal = sum((q * (1 - q) for q in global_q.values()), Fraction())
    covariance_sum = sum(covariance, Fraction())
    variance = marginal + 2 * covariance_sum
    mean = sum((1 - q for q in global_q.values()), Fraction())
    if parent.fraction_text(mean) != base['conditional_expected_repeating_types_fraction']:
        raise ValueError('global indicator means differ from parent producer')
    centered = base['observed_distinct_repeating_types'] - mean
    return {
        **base,
        'marginal_variance_sum_fraction': parent.fraction_text(marginal),
        'type_pair_covariance_sum_fraction': parent.fraction_text(covariance_sum),
        'covariance_adjustment_fraction': parent.fraction_text(2 * covariance_sum),
        'conditional_variance_fraction': parent.fraction_text(variance),
        'forced_repeating_types': sum(q == 0 for q in global_q.values()),
        'type_pairs_with_shared_opportunity': len(possible_pairs),
        'variable_indicator_shared_pairs': len(corrections),
        'forced_indicator_shared_pairs': len(possible_pairs) - len(corrections),
        'positive_covariance_pairs': sum(value > 0 for value in covariance),
        'negative_covariance_pairs': sum(value < 0 for value in covariance),
        'zero_covariance_variable_pairs': sum(value == 0 for value in covariance),
        **diagnostics(variance, centered),
    }


def report():
    raw = (ROOT / MEAN_REPORT).read_bytes()
    expected = parent.report()
    if parent.encoded(parent.load_split_json(raw.decode('utf-8'))) != parent.encoded(expected):
        raise ValueError('accepted type-mean report differs from complete parent replay')
    sources = parent.paired_sources(parent.load_sources(root=ROOT))
    common = set.intersection(*[{locus.key for locus in document.loci if locus.present and locus.kind == 'P0'}
                               for _, document in sources])
    result = {
        'schema_version': 1, 'method': 'exact globally deduplicated repeating-type variance v1',
        'mean_report_sha256': hashlib.sha256(raw).hexdigest(),
        'parent_inputs': {key: expected[key] for key in ('source_catalog_sha256', 'plan_sha256',
                                                      'baseline_sha256', 'engine_sha256')},
        'plan_sha256': hashlib.sha256((ROOT / PLAN).read_bytes()).hexdigest(),
        'engine_sha256': hashlib.sha256((ROOT / ENGINE).read_bytes()).hexdigest(),
        'selection': expected['selection'], 'control': expected['control'],
        'limits': ['Conditional SD scaling supplies no normal tail, confidence or mechanism probability.',
                   'Global deduplication and finite bags couple type indicators; signed covariance retained.',
                   'Exposed representations and loci are not adjudicated words, glyphs or independent physical lines.'],
        'sources': [],
    }
    for source, document in sources:
        selected = sorted((locus for locus in document.loci if locus.key in common
                           and locus.present and locus.kind == 'P0'), key=lambda locus: locus.key)
        reference = next(row for row in expected['sources'] if row['id'] == source['id'])
        variants = []
        for spacing in ('split', 'join'):
            for alternatives in ('exclude', 'first'):
                rows = [[locus.key, [token.value if parent.retain(token, alternatives) else None
                                     for token in parent.tokenize(locus.text, spacing)]] for locus in selected]
                base = parent.summarize(rows)
                prior = next(row for row in reference['variants'] if
                             (row['uncertain_spaces'], row['alternatives']) == (spacing, alternatives))
                if parent.encoded(base) != parent.encoded({key: prior[key] for key in base}):
                    raise ValueError('reconstructed slots or parent type diagnostics differ')
                variants.append({'uncertain_spaces': spacing, 'alternatives': alternatives, **summarize(rows)})
        result['sources'].append({'id': source['id'], 'url': source['url'], 'sha256': source['sha256'], 'variants': variants})
    return result


def protect_output(output):
    parent.protect_output(output)
    for path in (ROOT / PLAN, ROOT / MEAN_REPORT, ROOT / ENGINE):
        if output.resolve() == path.resolve() or (output.exists() and path.exists() and output.samefile(path)):
            raise ValueError('output aliases the accepted mean, variance plan or producer')


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
            if parent.encoded(parent.load_split_json(args.check.read_text())) != parent.encoded(result):
                raise ValueError('variance report differs from complete producer replay')
            print('Accepted mean report and exact covariance-aware type variance verified.')
        elif args.output:
            rendered = parent.encoded(result)
            protect_output(args.output)
            args.output.write_bytes(rendered)
        else:
            print(parent.encoded(result).decode('utf-8'), end='')
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(1, f'type variance failed: {error}\n')


if __name__ == '__main__':
    main()
