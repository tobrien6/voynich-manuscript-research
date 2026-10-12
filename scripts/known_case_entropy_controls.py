"""Two original generated-case controls for substitution entropy rankings."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'research/literature/known-case-entropy-controls.json'
CASES = [('balanced_rare_case', 2, 1, 99, 99), ('skewed_common_case', 100, 99, 99, 99)]
CANDIDATES = ['a', 'b', 'x']


def generate(a_total, capital_a, b_total, xb_total):
    if any(type(value) is not int for value in [a_total, capital_a, b_total, xb_total]) or \
            min(a_total, b_total, xb_total) < 1 or not 0 <= capital_a <= a_total:
        raise ValueError('require positive base counts and a valid integer capitalization count')
    base = {'a': a_total, 'b': b_total, 'xb': xb_total}
    observed = Counter(base)
    observed['a'] -= capital_a
    observed['a'.upper()] += capital_a
    return base, Counter({word: count for word, count in observed.items() if count})


def entropy(counts):
    total = sum(counts.values())
    if total < 1:
        raise ValueError('entropy requires positive occurrence mass')
    return -math.fsum((count / total) * math.log2(count / total) for count in sorted(counts.values()))


def scores(counts, target):
    source = 'a'.upper()
    selected = {word: count for word, count in counts.items() if source in word or target in word}
    transformed, subset_after = Counter(), Counter()
    for word, count in counts.items():
        transformed[word.replace(source, target)] += count
    for word, count in selected.items():
        subset_after[word.replace(source, target)] += count
    mass, total = sum(selected.values()), sum(counts.values())
    weight = Fraction(mass, total)
    return {'candidate': target, 'affected_occurrences': mass, 'all_occurrences': total,
            'mass_fraction': {'numerator': str(weight.numerator), 'denominator': str(weight.denominator)},
            'subset_decrease_bits': entropy(selected) - entropy(subset_after),
            'whole_decrease_bits': entropy(counts) - entropy(transformed),
            'transformed_synthetic_counts': [{'word': word, 'occurrences': count} for word, count in sorted(transformed.items())]}


def report():
    results = []
    source, gold = 'a'.upper(), 'a'
    if source.lower() != gold:
        raise ValueError('declared ASCII capitalization rule does not invert to its base symbol')
    for name, a_total, capital_a, b_total, xb_total in CASES:
        base, observed = generate(a_total, capital_a, b_total, xb_total)
        measured = [scores(observed, candidate) for candidate in CANDIDATES]
        rankings = []
        for metric in ['subset', 'whole']:
            field = metric + '_decrease_bits'
            maximum = max(value[field] for value in measured)
            chosen = sorted(value['candidate'] for value in measured if value[field] == maximum)
            rankings.append({'metric': metric, 'maximizers': chosen, 'known_case_target_is_maximizer': gold in chosen})
        for value in measured:
            for field in ['subset_decrease_bits', 'whole_decrease_bits']:
                value[field] = round(value[field], 12)
        results.append({'case': name, 'base_synthetic_counts': [{'word': word, 'occurrences': count} for word, count in sorted(base.items())],
                        'capitalized_a_occurrences': capital_a,
                        'observed_synthetic_counts': [{'word': word, 'occurrences': count} for word, count in sorted(observed.items())],
                        'candidate_scores': measured, 'rankings': rankings})
    return {'schema_version': 1, 'method': 'fixed generated ASCII case entropy controls v1',
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'generation_rule': 'capitalize only the declared number of a occurrences; b and xb remain unchanged',
            'source_symbol': source, 'known_case_target': gold, 'candidate_set': CANDIDATES, 'cases': results,
            'scope': 'constructed known-case controls, not language-corpus performance estimates or manuscript case assignments'}


def load(raw):
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('non-finite JSON number')
    return json.loads(raw, object_pairs_hook=object_pairs, parse_constant=invalid)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.output and (args.output.exists() or args.output.is_symlink()):
            raise ValueError('output exists; choose a new record')
        result = report()
        if args.check:
            expected = load(REPORT.read_bytes())
            if json.dumps(result, sort_keys=True) != json.dumps(expected, sort_keys=True):
                raise ValueError('known-case report differs from replay')
            print('Complete generated-case control report matches.')
        else:
            with args.output.open('x', encoding='utf-8') as output:
                output.write(json.dumps(result, indent=2) + '\n')
            print('Wrote complete generated-case control report.')
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Known-case control failed: {error}\n')


if __name__ == '__main__':
    main()
