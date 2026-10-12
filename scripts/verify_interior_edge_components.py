"""Independent literal-count and ordered-distinct-pair component verification."""
import argparse
from collections import Counter
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

try:
    from .eva_token_adapter import build
except ImportError:
    from eva_token_adapter import build

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'research/transliteration/interior-edge-component-pins.json'
MANIFEST_SHA = '923773ef90fdfefdeb52dce5934bf12ff1ec3b8b9704504eaf7b8fb50e5e32e6'
POLICIES = ['ascii_letters', 'bench_sequences', 'bench_and_minim_sequences']
VARIANTS = [(s, p) for s in ('ZL3b', 'IT2a') for p in ('split', 'join')]
FIELDS = ['raw', 'unrestricted_expectation', 'half_expectation']


def read_report(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def exact(value):
    if isinstance(value, list):
        assert len(value) == 2 and all(type(v) is str for v in value)
        result = Fraction(int(value[0]), int(value[1]))
        assert value == [str(result.numerator), str(result.denominator)]
        return result
    assert value['encoding'] == 'base16-integer-strings'
    result = Fraction(int(value['numerator'], 16), int(value['denominator'], 16))
    assert value['numerator'] == format(result.numerator, 'x')
    assert value['denominator'] == format(result.denominator, 'x')
    with localcontext(Context(prec=60, rounding=ROUND_HALF_EVEN)):
        assert value['decimal_60_significant_digits_approx'] == str(Decimal(result.numerator) / Decimal(result.denominator))
    return result


def count(token, patterns):
    remaining = token
    total = 0
    while remaining:
        prefix = next((p for p in sorted(patterns, key=lambda p: (-len(p), p)) if remaining.startswith(p)), remaining[0])
        remaining = remaining[len(prefix):]
        total += 1
    return total


def direct_pairs(left, right, same_block):
    products = [x * y for i, x in enumerate(left) for j, y in enumerate(right) if not same_block or i != j]
    return sum(products, Fraction()) / len(products) if products else Fraction()


def literal_components(values):
    n = len(values)
    assert n >= 3 and all(type(x) is int and x > 0 for x in values)
    mean = Fraction(sum(values), n)
    z = [Fraction(x) - mean for x in values]
    squared = sum(x * x for x in z)
    scale = Fraction(n, n - 1) / squared if squared else Fraction()
    cut = (n + 1) // 2
    blocks = z[:cut], z[cut:]
    full = direct_pairs(z, z, True)
    block_products = [direct_pairs(blocks[0], blocks[0], True),
                      direct_pairs(blocks[0], blocks[1], False),
                      direct_pairs(blocks[1], blocks[1], True)]
    result = {field: [Fraction()] * 3 for field in FIELDS}
    for position in range(n - 1):
        region = 0 if position + 1 < cut else (1 if position + 1 == cut else 2)
        result['raw'][region] += scale * z[position] * z[position + 1]
        result['unrestricted_expectation'][region] += scale * full
        result['half_expectation'][region] += scale * block_products[region]
    return result


def independent_selection(mappings):
    common = set.intersection(*[set(records) for records in mappings.values()])
    common = {key for key in common if all(records[key]['locus_type'] == 'P0'
              and 'nonexistent_locus' not in records[key]['exclusion_reasons'] for records in mappings.values())}
    retained, excluded = [], []
    reason_counts = Counter()
    after_adapter = after_drawing = 0
    for key in sorted(common):
        valid = all(records[key]['eligible'] for records in mappings.values())
        after_adapter += valid
        after_drawing += valid and all(records[key]['drawing_interruption_count'] == 0 for records in mappings.values())
        reasons = []
        for (sid, spacing), records in mappings.items():
            record = records[key]
            reasons.extend(sid + '/' + spacing + ':' + reason for reason in record['exclusion_reasons'])
            if valid:
                if record['drawing_interruption_count']:
                    reasons.append(sid + '/' + spacing + ':drawing_interruption')
                if record['token_count'] < 5:
                    reasons.append(sid + '/' + spacing + ':fewer_than_five_tokens')
        reasons = sorted(set(reasons))
        if reasons:
            excluded.append({'locus_key': key, 'reasons': reasons})
            reason_counts.update(reasons)
        else:
            retained.append(key)
    return {'shared_present_P0_loci': len(common), 'eligible_in_all_adapters': after_adapter,
            'eligible_after_drawing_exclusion': after_drawing, 'eligible_after_minimum_token_exclusion': len(retained),
            'excluded_loci': len(excluded), 'reason_counts_may_overlap': dict(sorted(reason_counts.items())),
            'exclusions': excluded, 'retained_locus_keys': retained,
            'retained_locus_keys_sha256': hashlib.sha256(json.dumps(retained, separators=(',', ':')).encode()).hexdigest()}


def verify(report_path, progress=None):
    if not __debug__:
        raise ValueError('verification requires assertions without optimization')
    report = read_report(report_path)
    raw = (ROOT / MANIFEST).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == MANIFEST_SHA
    pins = json.loads(raw)
    assert pins == report['input_pins'] and report['pin_manifest_sha256'] == MANIFEST_SHA
    assert report['implementation_sha256'] == hashlib.sha256((ROOT / 'scripts/interior_edge_components.py').read_bytes()).hexdigest()
    for name, digest in pins.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
    previous = json.loads((ROOT / 'research/transliteration/interior_unit_controls.json').read_text())
    joint = json.loads((ROOT / 'research/transliteration/interior_unit_covariance.json').read_text())
    original = json.loads((ROOT / 'research/transliteration/interior_length_order.json').read_text())
    settings = json.loads((ROOT / 'research/baselines/eva-unit-protocol.json').read_text())['policies']
    assert [p['id'] for p in settings] == POLICIES
    mappings = {(s, p): {r['locus_key']: r for r in build(p, source_ids=(s,), kinds=('P0',))['records']}
                for s, p in VARIANTS}
    selection = independent_selection(mappings)
    assert selection == original['selection']
    keys = selection['retained_locus_keys']
    assert report['selection'] == previous['selection'] == {
        'loci': len(keys), 'cohort_sha256': selection['retained_locus_keys_sha256']}
    assert report['components'] == ['early', 'bridge', 'late']
    assert [(t['source_id'], t['spacing']) for t in report['treatments']] == VARIANTS
    assert report['component_tails_computed'] == report['new_permutation_draws'] == 0
    checked = aggregate_count = difference_count = 0
    for treatment, old, accepted in zip(report['treatments'], previous['treatments'], joint['treatments']):
        identity = treatment['source_id'], treatment['spacing']
        assert treatment['source_sha256'] == old['source_sha256']
        assert [p['policy_id'] for p in treatment['unit_policies']] == POLICIES
        aggregates = []
        for pi, (saved, old_policy, policy) in enumerate(zip(treatment['unit_policies'], old['unit_policies'], settings)):
            rows = [(mappings[identity][key]['page_id'], key,
                     [count(token, policy['patterns']) for token in mappings[identity][key]['tokens'][1:-1]]) for key in keys]
            digest = hashlib.sha256(json.dumps(rows, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
            assert digest == saved['length_corpus_sha256'] == old_policy['length_corpus_sha256']
            assert saved['loci'] == saved['accepted_effect_denominator'] == len(keys)
            assert len(saved['per_locus']) == len(keys)
            totals = {field: [Fraction()] * 3 for field in FIELDS}
            for (page, key, vector), entry, old_entry in zip(rows, saved['per_locus'], accepted['per_locus']):
                assert (page, key) == (entry['page_id'], entry['locus_key']) == (old_entry['page_id'], old_entry['locus_key'])
                assert entry['interior_size'] == len(vector) and entry['early_size'] == (len(vector) + 1) // 2
                assert entry['edge_counts'] == [entry['early_size'] - 1, 1, len(vector) - entry['early_size'] - 1]
                direct = literal_components(vector)
                for field in FIELDS:
                    assert direct[field] == [exact(v) for v in entry[field]]
                    totals[field] = [a + b for a, b in zip(totals[field], direct[field])]
                    checked += 3
                for scope in ('unrestricted', 'half'):
                    assert sum(direct[scope + '_expectation']) == exact(old_entry[scope]['uncentered_means'][pi])
            means = {field: [v / len(keys) for v in values] for field, values in totals.items()}
            for scope in ('unrestricted', 'half'):
                means[scope + '_centered'] = [a - b for a, b in zip(means['raw'], means[scope + '_expectation'])]
                assert sum(means[scope + '_centered']) == exact(accepted[scope]['exact_observed_centered_means'][pi])
                assert saved['attributed_parent_total_tails'][scope] == {field: old_policy[scope][field]
                    for field in ('two_sided_tail_count', 'exploratory_two_sided_tail')}
            means['half_minus_unrestricted_expectation'] = [b - a for a, b in zip(
                means['unrestricted_expectation'], means['half_expectation'])]
            assert set(saved['aggregate']) == set(means)
            for field, values in means.items():
                assert values == [exact(v) for v in saved['aggregate'][field]]
                aggregate_count += 3
            if pi:
                assert set(saved['grouped_minus_ascii_centered']) == {'unrestricted', 'half'}
                for scope in ('unrestricted', 'half'):
                    difference = [a - b for a, b in zip(means[scope + '_centered'], aggregates[0][scope + '_centered'])]
                    assert difference == [exact(v) for v in saved['grouped_minus_ascii_centered'][scope]]
                    assert sum(difference) == exact(accepted[scope]['paired_changes'][pi - 1]['observed_change_exact'])
                    difference_count += 3
            else:
                assert saved['grouped_minus_ascii_centered'] is None
            aggregates.append(means)
        if progress:
            progress(identity[0] + '/' + identity[1] + ': independent count vectors and ordered-pair components verified')
    return {'loci': len(keys), 'exclusions': len(selection['exclusions']), 'literal_count_vectors': 12,
            'per_locus_component_values': checked, 'aggregate_component_values': aggregate_count,
            'paired_component_differences': difference_count}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT / 'research/transliteration/interior_edge_components.json.gz')
    args = parser.parse_args()
    try:
        result = verify(args.report, progress=lambda message: print(message, flush=True))
    except (AssertionError, ValueError, OSError, EOFError, KeyError, TypeError) as error:
        parser.exit(1, f'Independent edge component verification failed: {error}\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
