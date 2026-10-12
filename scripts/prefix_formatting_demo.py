"""Demonstrate prefix/length effects of a known reversible synthetic row marker."""

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

try:
    from .locus_positions import contrast, conditional_variance
    from .shuffle_token_lines import ALGORITHM, HashDraws
except ImportError:
    from locus_positions import contrast, conditional_variance
    from shuffle_token_lines import ALGORITHM, HashDraws


ROOT = Path(__file__).resolve().parents[1]
PLAN = Path('research/representation/PREFIX_FORMATTING_PLAN.md')
IMPLEMENTATIONS = ('scripts/prefix_formatting_demo.py', 'scripts/locus_positions.py',
                   'scripts/shuffle_token_lines.py')
VOCABULARY = tuple(''.join(word) for word in itertools.product('abcd', repeat=3))


def encoded(value):
    return json.dumps(value, ensure_ascii=True, separators=(',', ':')).encode('ascii')


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def rational(value):
    value = Fraction(value)
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def source_rows(count, width, seed):
    if (type(count) is not int or count < 1 or type(width) is not int or width < 2
            or type(seed) is not int or seed < 0):
        raise ValueError('require positive row count, at least two slots, and a nonnegative integer seed')
    key = hashlib.sha256(f'prefix-formatting-demo-v1:{seed}'.encode('ascii')).digest()
    draws = HashDraws(key)
    return [[VOCABULARY[draws.below(len(VOCABULARY))] for _ in range(width)] for _ in range(count)]


def encode_rows(rows):
    if not rows or any(not row or any(token not in VOCABULARY for token in row) for row in rows):
        raise ValueError('source must contain nonempty rows of declared vocabulary tokens')
    return [['y' + row[0], *row[1:]] for row in rows]


def decode_rows(rows):
    if not rows or any(not row or not isinstance(row[0], str) or not row[0].startswith('y') for row in rows):
        raise ValueError('encoded rows require exactly one declared first-slot marker')
    recovered = [[row[0][1:], *row[1:]] for row in rows]
    if any(token not in VOCABULARY for row in recovered for token in row):
        raise ValueError('decoded token is outside the source vocabulary')
    return recovered


def boundary_metrics(rows, boundary, feature):
    edge = 0 if boundary == 'first' else -1 if boundary == 'last' else None
    if edge is None or feature not in {'literal_y_prefix', 'ascii_token_length'} or not rows:
        raise ValueError('require rows and a declared boundary/feature')
    deltas, variances = [], []
    for row in rows:
        values = [int(token.startswith('y')) if feature == 'literal_y_prefix' else len(token) for token in row]
        m = len(values)
        if m < 2:
            raise ValueError('boundary contrasts require at least two slots')
        delta = Fraction(values[edge]) - Fraction(sum(values) - values[edge], m - 1)
        variance = Fraction(m * sum(value * value for value in values) - sum(values) ** 2, (m - 1) ** 2)
        if (abs(contrast(values, edge) - float(delta)) > 1e-12 or
                abs(conditional_variance(values) - float(variance)) > 1e-12):
            raise ValueError('exact synthetic moments disagree with the accepted measurement functions')
        deltas.append(delta)
        variances.append(variance)
    return {'boundary': boundary, 'feature': feature, 'rows': len(rows),
            'equal_row_mean_contrast': rational(sum(deltas, Fraction(0)) / len(rows)),
            'conditional_variance_of_equal_row_mean': rational(sum(variances, Fraction(0)) / len(rows) ** 2)}


def extreme_tail(count, width):
    if type(count) is not int or count < 1 or type(width) is not int or width < 2:
        raise ValueError('require positive row count and at least two slots')
    # Only the all-first placement reaches +1; with two slots, all-last also
    # reaches absolute contrast 1. Wider rows have a smaller negative extreme.
    return Fraction(2 if width == 2 else 1, width ** count)


def lookup_counts(rows, dictionary):
    result = []
    for position in ('first', 'other'):
        tokens = [token for row in rows for token in (row[:1] if position == 'first' else row[1:])]
        original = sum(token in dictionary for token in tokens)
        trimmed = sum((token[1:] if token.startswith('y') else token) in dictionary for token in tokens)
        result.append({'position': position, 'slots': len(tokens), 'raw_matches': original,
                       'matches_after_one_leading_y_removed': trimmed,
                       'match_gain': rational(Fraction(trimmed - original, len(tokens)))})
    return result


def report(count=256, width=8, seed=20261012, root=ROOT):
    source = source_rows(count, width, seed)
    carrier = encode_rows(source)
    recovered = decode_rows(carrier)
    if recovered != source:
        raise ValueError('complete-message round trip failed')
    dictionary = {token for row in carrier for token in row[1:]}
    total_tokens = count * width
    source_chars = sum(map(len, (token for row in source for token in row)))
    carrier_chars = sum(map(len, (token for row in carrier for token in row)))
    return {
        'schema_version': 1, 'method': 'synthetic reversible first-slot marker v1',
        'scope': 'Known-codec measurement demonstration; no manuscript data or candidate fit',
        'plan_sha256': hashlib.sha256((root / PLAN).read_bytes()).hexdigest(),
        'implementation_sha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in IMPLEMENTATIONS},
        'generator': {'algorithm': ALGORITHM, 'key_recipe': 'SHA-256 of ASCII prefix-formatting-demo-v1:SEED',
                      'seed': seed, 'draw_bound': len(VOCABULARY), 'rows': count, 'slots_per_row': width,
                      'realization_status': 'deterministic once the recorded key is fixed'},
        'codec': {'source_alphabet': 'abcd', 'source_token_width': 3, 'marker': 'y',
                  'marker_position': 'first token only; supplied row boundaries retained'},
        'source_matrix_sha256': digest(source), 'encoded_matrix_sha256': digest(carrier),
        'decoded_matrix_sha256': digest(recovered), 'round_trip_verified': True,
        'token_count_in_each_matrix': total_tokens,
        'source_ascii_characters': source_chars, 'encoded_ascii_characters': carrier_chars,
        'measurements': {name: [boundary_metrics(rows, boundary, feature)
                        for boundary in ('first', 'last')
                        for feature in ('literal_y_prefix', 'ascii_token_length')]
                         for name, rows in (('source', source), ('encoded', carrier))},
        'conditional_control': {'scope': 'independent uniform token assignment within each encoded row',
                                'observed_first_slot_mean': rational(1),
                                'exact_two_sided_tail_for_either_first_slot_feature': rational(extreme_tail(count, width)),
                                'tail_scope': 'one fixed boundary contrast; no manuscript inference'},
        'lookup': {'dictionary_scope': 'encoded non-first slots; reused for every lookup',
                   'dictionary_types': len(dictionary), 'sorted_dictionary_sha256': digest(sorted(dictionary)),
                   'source': lookup_counts(source, dictionary), 'encoded': lookup_counts(carrier, dictionary)},
        'ideal_uniform_source_ensemble': {
            'source_model': 'independent uniform choices from all 64 vocabulary entries',
            'message_support': f'64**{total_tokens}; identical complete-message support under the codec',
            'joint_bits_in_either_representation': 6 * total_tokens,
            'bits_per_source_token': rational(6),
            'joint_bits_per_source_ascii_character': rational(Fraction(6 * total_tokens, source_chars)),
            'joint_bits_per_encoded_ascii_character': rational(Fraction(6 * total_tokens, carrier_chars)),
            'qualification': 'ensemble quantities; not entropy in the known seed or a plug-in entropy estimate'},
    }


def protect_output(output, root=ROOT):
    resolved = output.resolve()
    protected = [root / PLAN, *(root / name for name in IMPLEMENTATIONS)]
    catalog = root / 'data/transliterations.json'
    if catalog.exists():
        protected.extend([catalog, *(root / source['path'] for source in json.loads(catalog.read_text())['sources'])])
    if (resolved.is_relative_to((root / 'data').resolve()) or resolved.is_relative_to((root / 'scripts').resolve())
            or any(resolved == path.resolve() or (output.exists() and path.exists() and output.samefile(path))
                   for path in protected)):
        raise ValueError('demo output must not replace source data, implementation files, or the plan')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output, root=ROOT)
        result = report(root=ROOT)
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError('synthetic report differs from the pinned implementation/plan and replay')
        if args.output:
            args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        elif not args.check:
            print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'prefix formatting demo failed: {error}\n')
    if args.check:
        print('Known codec, exact recovery, prefix/length moments and synthetic report reproduce.')


if __name__ == '__main__':
    main()
