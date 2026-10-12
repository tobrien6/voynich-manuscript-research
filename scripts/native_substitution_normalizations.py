"""Both frozen substitution normalizations on one pinned native B input."""

import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache
import hashlib
from itertools import combinations
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'research/literature/NATIVE_SUBSTITUTION_PLAN.md'
REPORT = ROOT / 'research/literature/native-substitution-normalizations.json'
INPUT_SHA = '723cb2746da37c8272005f71298917abfed60412b23597b2b8aecb95dc7a0ee4'
PINS = {
    'scripts/substitution_entropy_control.py': 'b4be747f08996e6898cadf151344cac6a2c36be9ced8d8c62afd5ac47bd1443f',
    'research/literature/substitution-normalization-control.json': 'a701c04d7e41363d2b38538f15c6d9540e15198402834f19d457f0401e1db82a',
}
PRECISION = 80
GUARD = Decimal('1e-60')
GALLOWS = ['B', 'F', 'P', 'V']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_hash(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8'))


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


@lru_cache(maxsize=None)
def factors(number):
    if type(number) is not int or number < 1:
        raise ValueError('factorization requires a positive integer')
    remaining, divisor, result = number, 2, []
    while divisor * divisor <= remaining:
        power = 0
        while remaining % divisor == 0:
            remaining //= divisor
            power += 1
        if power:
            result.append((divisor, power))
        divisor = 3 if divisor == 2 else divisor + 2
    if remaining > 1:
        result.append((remaining, 1))
    return tuple(result)


def information_vector(frequency_vectors):
    exponents = Counter()
    for frequencies in frequency_vectors:
        if len(frequencies) < 2 or any(type(count) is not int or count < 1 for count in frequencies):
            raise ValueError('require multi-type collision classes with positive counts')
        total = sum(frequencies)
        for prime, power in factors(total):
            exponents[prime] += total * power
        for count in frequencies:
            for prime, power in factors(count):
                exponents[prime] -= count * power
    return tuple(sorted((prime, exponent) for prime, exponent in exponents.items() if exponent))


def signature(vector, denominator):
    if type(denominator) is not int or denominator < 1:
        raise ValueError('score denominator must be a positive integer')
    return tuple((prime, Fraction(exponent, denominator)) for prime, exponent in vector)


def decimal_score(exact_signature):
    with localcontext() as context:
        context.prec = PRECISION
        log_two = Decimal(2).ln()
        result = sum((Decimal(value.numerator) / Decimal(value.denominator) * (Decimal(prime).ln() / log_two)
                      for prime, value in exact_signature), Decimal(0))
        if exact_signature and result <= GUARD:
            raise ValueError('nonzero collision information is not numerically positive')
        return +result


def ranking(source, candidates, metric):
    if not candidates:
        raise ValueError('ranking has no declared candidates')
    evaluated = [(candidate['symbol'], signature(candidate['vector'], candidate['denominator'])) for candidate in candidates]
    scores = {symbol: decimal_score(exact) for symbol, exact in evaluated}
    maximum = max(scores.values())
    leader = min(symbol for symbol, score in scores.items() if score == maximum)
    leader_signature = dict(evaluated)[leader]
    exact_ties = sorted(symbol for symbol, exact in evaluated if exact == leader_signature)
    with localcontext() as context:
        context.prec = PRECISION
        possible = sorted(symbol for symbol, score in scores.items() if abs(maximum - score) <= GUARD)
    unresolved = any(dict(evaluated)[symbol] != leader_signature for symbol in possible)
    status = 'numerically_unresolved' if unresolved else ('resolved_positive' if maximum else 'no_positive_optimum')
    return {'source_symbol': source, 'metric': metric, 'candidate_count': len(candidates),
            'maximum_bits_20dp': format(maximum, '.20f'), 'status': status,
            'possible_maximizers': possible if unresolved else exact_ties,
            'positive_maximizers': None if unresolved else (exact_ties if maximum else [])}


def native_counts(raw):
    if len(raw) != 95465 or sha(raw) != INPUT_SHA:
        raise ValueError('input differs from the exact author-associated B bytes')
    counts = Counter(raw.decode('utf-8').split())
    alphabet = sorted({character for word in counts for character in word})
    if sum(counts.values()) != 17597 or len(counts) != 3920 or len(alphabet) != 35:
        raise ValueError('native source population differs from the recovered audit')
    if any(symbol not in alphabet for symbol in GALLOWS):
        raise ValueError('fixed focus symbol absent from native alphabet')
    return counts, alphabet


def produce(input_path):
    for name, fingerprint in PINS.items():
        if sha((ROOT / name).read_bytes()) != fingerprint:
            raise ValueError('parent measurement dependency drift')
    if __package__:
        from .substitution_entropy_control import measure
    else:
        from substitution_entropy_control import measure
    counts, alphabet = native_counts(input_path.read_bytes())
    pairs = []
    for source, target in combinations(alphabet, 2):
        measured = measure(counts, source, target)
        classes = measured['collision_classes']
        frequency_vectors = sorted(sorted(member['occurrences'] for member in item['original_synthetic_counts']) for item in classes)
        identities = [{'mapped_word_utf8_sha256': sha(item['mapped_synthetic_word'].encode('utf-8')),
                       'original_type_counts': sorted((sha(member['word'].encode('utf-8')), member['occurrences'])
                                                      for member in item['original_synthetic_counts'])} for item in classes]
        vector = information_vector(frequency_vectors)
        subset = decimal_score(signature(vector, measured['selected_occurrences']))
        whole = decimal_score(signature(vector, measured['all_occurrences']))
        pairs.append({'symbols': [source, target], 'symbol_codepoints': [f'U+{ord(symbol):04X}' for symbol in [source, target]],
                      **{key: measured[key] for key in ['all_occurrences', 'selected_occurrences', 'selected_mass_fraction',
                                                       'all_types_before', 'all_types_after', 'selected_types_before', 'selected_types_after']},
                      'collision_frequency_vectors': frequency_vectors,
                      'collision_identity_digest': canonical_hash(sorted(identities, key=lambda item: item['mapped_word_utf8_sha256'])),
                      'information_prime_exponents': [{'prime': prime, 'exponent': exponent} for prime, exponent in vector],
                      'subset_score_bits_decimal_80digits': str(subset), 'whole_score_bits_decimal_80digits': str(whole),
                      'subset_score_bits_20dp': format(subset, '.20f'), 'whole_score_bits_20dp': format(whole, '.20f')})
    if len(pairs) != 595:
        raise ValueError('complete declared pair scope was lost')
    rankings = []
    comparisons = []
    for symbol in alphabet:
        values = {}
        for metric, denominator in [('subset', 'selected_occurrences'), ('whole', 'all_occurrences')]:
            candidates = [{'symbol': pair['symbols'][1] if pair['symbols'][0] == symbol else pair['symbols'][0],
                           'vector': tuple((item['prime'], item['exponent']) for item in pair['information_prime_exponents']),
                           'denominator': pair[denominator]} for pair in pairs if symbol in pair['symbols']]
            if len(candidates) != 34:
                raise ValueError('a source symbol lost a declared candidate')
            values[metric] = ranking(symbol, candidates, metric)
            rankings.append(values[metric])
        left, right = values['subset']['positive_maximizers'], values['whole']['positive_maximizers']
        comparisons.append({'source_symbol': symbol,
                            'different_positive_maximizer_sets': None if left is None or right is None else left != right,
                            'subset_positive_maximizers': left, 'whole_positive_maximizers': right})
    focus = []
    for symbol in GALLOWS:
        comparison = next(value for value in comparisons if value['source_symbol'] == symbol)
        focus.append({**comparison, **{metric + '_positive_set_gallows_only': None if comparison[metric + '_positive_maximizers'] is None
                                      else bool(comparison[metric + '_positive_maximizers']) and all(value in GALLOWS for value in comparison[metric + '_positive_maximizers'])
                                      for metric in ['subset', 'whole']}})
    return {'schema_version': 1, 'method': 'complete native B substitution normalizations v1',
            'input_sha256': INPUT_SHA, 'input_bytes': 95465, 'token_occurrences': sum(counts.values()),
            'native_word_types': len(counts), 'native_alphabet': alphabet,
            'word_frequency_table_digest': canonical_hash(sorted((sha(word.encode('utf-8')), count) for word, count in counts.items())),
            'plan_sha256': sha(PLAN.read_bytes()), 'producer_sha256': sha(Path(__file__).read_bytes()),
            'parent_pins': PINS, 'decimal_precision': PRECISION, 'numerical_guard_bits': str(GUARD),
            'pairs': pairs, 'rankings': rankings, 'normalization_comparisons': comparisons, 'fixed_gallows_focus': focus,
            'scope': 'exposed native notation count comparison; explicit implementation, not authenticated historical replication, physical case assignment or decoding'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--output', type=Path)
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        if args.output and (args.output.exists() or args.output.is_symlink()):
            raise ValueError('output exists; choose a new record')
        result = produce(args.input)
        if args.check:
            if canonical_hash(result) != canonical_hash(load(REPORT.read_bytes())):
                raise ValueError('native score report differs from replay')
            print('All native substitution scores and rankings match the report.')
        else:
            with args.output.open('x', encoding='utf-8') as output:
                output.write(json.dumps(result, indent=2) + '\n')
            print('Wrote complete native substitution score report.')
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Native substitution failed: {error}\n')


if __name__ == '__main__':
    main()
