"""Conservative conditional tail bounds for the existing binary-prefix family."""

import argparse
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path

try:
    from .audit_transliterations import ROOT, load_sources
    from .conservative_prefixes import common_cohort
    from .eva_token_adapter import build
    from .prefix_strata import paragraph_start
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from conservative_prefixes import common_cohort
    from eva_token_adapter import build
    from prefix_strata import paragraph_start
    from token_baselines import paired_sources


REFERENCE = ROOT / 'research/transliteration/conservative_prefixes.json'
PREFIXES = {'literal_q_prefix': 'q', 'literal_y_prefix': 'y'}


def locus_moments(tokens, boundary, prefix):
    if boundary not in {'first', 'last'} or prefix not in {'q', 'y'} or len(tokens) < 2:
        raise ValueError('require a declared binary prefix and at least two tokens')
    values = [int(token.startswith(prefix)) for token in tokens]
    count, positives = len(values), sum(values)
    edge = values[0 if boundary == 'first' else -1]
    difference = Fraction(count * edge - positives, count - 1)
    variance = Fraction(positives * (count - positives), (count - 1) ** 2)
    return difference, variance


def fraction_record(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def bernstein_upper(total, variance, family_size):
    """Outward-rounded two-sided Bernstein bound, with |D_i| <= 1.

    Exact fractions precede exponential evaluation. ROUND_FLOOR lowers the
    positive exponent; exp is correctly rounded, then next_plus moves upward.
    Ceiling multiplication prevents decimal rounding below the bound.
    """
    total, variance = abs(Fraction(total)), Fraction(variance)
    if variance < 0 or type(family_size) is not int or family_size < 1:
        raise ValueError('variance must be nonnegative and family size positive')
    if not total:
        return {'exponent_exact': fraction_record(Fraction(0)),
                'two_sided_upper_decimal': '1', 'family_adjusted_upper_decimal': '1'}
    if variance == 0:
        raise ValueError('nonzero observed contrast cannot have zero conditional variance')
    exponent = total ** 2 / (2 * variance + Fraction(2, 3) * total)
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_FLOOR
        downward_exponent = Decimal(exponent.numerator) / Decimal(exponent.denominator)
        upward_exponential = (-downward_exponent).exp().next_plus()
        context.rounding = ROUND_CEILING
        upper = min(Decimal(1), Decimal(2) * upward_exponential)
        adjusted = min(Decimal(1), Decimal(family_size) * upper)
    return {'exponent_exact': fraction_record(exponent),
            'two_sided_upper_decimal': str(upper), 'family_adjusted_upper_decimal': str(adjusted)}


def reference_index(reference):
    index = {}
    for source in reference['sources']:
        for variant in source['variants']:
            for cohort in variant['cohorts']:
                for position in cohort['positions']:
                    for feature in position['features']:
                        identity = (source['id'], variant['spacing'], cohort['source_currier_label'],
                                    cohort['source_paragraph_start'], position['boundary'], feature['feature'])
                        if identity in index:
                            raise ValueError('duplicate reference contrast')
                        index[identity] = (position['eligible_loci'], feature)
    return index


def calculate():
    raw_reference = REFERENCE.read_bytes()
    reference = json.loads(raw_reference)
    if (reference['schema_version'] != 1 or reference['adapter_version'] != 'plain-eva-v1' or
            reference['method'] != 'exploratory plain-eva-v1 common-cohort prefix controls v1'):
        raise ValueError('reference contract changed')
    sources = paired_sources(load_sources())
    expected = {source['id']: source['sha256'] for source, _ in sources}
    if len(reference['sources']) != 2 or {source['id']: source['sha256'] for source in reference['sources']} != expected:
        raise ValueError('reference source pins changed')
    candidates = set.intersection(*[
        {locus.key for locus in document.loci if locus.present and locus.kind == 'P0'}
        for _, document in sources])
    payloads = [build(mode, source_ids=tuple(expected), kinds=('P0',)) for mode in ['split', 'join']]
    selected, records, _, _ = common_cohort(payloads, expected, candidates)
    selection = reference['selection']
    digest = hashlib.sha256(('\n'.join(sorted(selected)) + '\n').encode()).hexdigest()
    if (sorted(selected) != selection['selected_locus_keys'] or len(selected) != selection['selected_count']
            or digest != selection['sorted_selected_locus_keys_sha256']):
        raise ValueError('recomputed cohort differs from existing prefix report')
    labels = sorted({locus.variables.get('L', 'unset') for _, document in sources
                     for locus in document.loci if locus.key in selected})
    if labels != selection['source_currier_labels_including_unset']:
        raise ValueError('reference source-label family changed')
    identities = set(itertools.product(expected, ['split', 'join'], labels, [False, True],
                                       ['first', 'last'], PREFIXES))
    index = reference_index(reference)
    if set(index) != identities:
        raise ValueError('reference does not contain the complete declared contrast family')
    family_size = len(identities)
    output = []
    for source, document in sources:
        loci = [locus for locus in document.loci if locus.key in selected and locus.present and locus.kind == 'P0']
        for spacing, label, start, boundary, feature_name in itertools.product(
                ['split', 'join'], labels, [False, True], ['first', 'last'], PREFIXES):
            cohort = [locus for locus in loci if locus.variables.get('L', 'unset') == label
                      and paragraph_start(locus) == start]
            count = len(cohort)
            total, variance = Fraction(0), Fraction(0)
            for locus in cohort:
                tokens = records[(source['id'], spacing, locus.key)]['tokens']
                delta, row_variance = locus_moments(tokens, boundary, PREFIXES[feature_name])
                total += delta
                variance += row_variance
            identity = (source['id'], spacing, label, start, boundary, feature_name)
            ref_count, ref_feature = index[identity]
            if ref_count != count:
                raise ValueError('reference boundary denominator changed')
            if count:
                mean = float(total / count)
                sd = math.sqrt(float(variance)) / count
                if (abs(mean - ref_feature['paired_difference']) > 5.00001e-9 or
                        abs(sd - ref_feature['exact_null_standard_deviation']) > 5.00001e-9):
                    raise ValueError('exact moments differ beyond reference rounding precision')
            output.append({
                'source_id': source['id'], 'source_sha256': source['sha256'], 'spacing': spacing,
                'source_currier_label': label, 'source_paragraph_start': start,
                'boundary': boundary, 'feature': feature_name, 'loci': count,
                'sum_difference_exact': fraction_record(total) if count else None,
                'variance_sum_exact': fraction_record(variance) if count else None,
                'observed_mean_rounded': round(float(total / count), 8) if count else None,
                'bounds': bernstein_upper(total, variance, family_size) if count else None,
            })
    return {
        'schema_version': 1, 'method': 'exact-moment conditional Bernstein prefix bounds v1',
        'reference_report_sha256': hashlib.sha256(raw_reference).hexdigest(),
        'selected_count': len(selected), 'selected_locus_keys_sha256': digest,
        'family_size_including_nonestimable_cases': family_size,
        'absolute_per_locus_bound': 1, 'decimal_precision': 60,
        'interpretation': 'upper bounds under ideal independent within-locus assignments; exposed-data diagnostics',
        'comparisons': output,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        result = calculate()
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError('committed bound report differs from recomputed result')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'prefix bound calculation failed: {error}\n')
    rendered = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(rendered)
    elif not args.check:
        print(rendered, end='')
    if args.check:
        print('Cohort, reference agreement, exact moments and conditional bounds verified.')


if __name__ == '__main__':
    main()
