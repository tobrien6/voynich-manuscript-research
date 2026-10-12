"""An analytically constructed marker can have zero matched lookup selectivity."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

try:
    from . import y_prefix_specificity as controls
    from .token_baselines import Token
except ImportError:
    import y_prefix_specificity as controls
    from token_baselines import Token


ROOT = Path(__file__).resolve().parents[1]
PLAN = 'research/representation/KNOWN_MARKER_OPPORTUNITY_PLAN.md'
INPUTS = 'research/representation/known-marker-opportunity-inputs.json'
VOCABULARY = frozenset(('a', 'b', 'c', 'ya', 'yc', 'z'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def valid_source(rows):
    return (isinstance(rows, (list, tuple)) and bool(rows)
            and all(isinstance(row, (list, tuple)) and bool(row)
                    and all(isinstance(token, str) and token in VOCABULARY for token in row) for row in rows))


def encode(rows):
    if not valid_source(rows):
        raise ValueError('source rows must contain declared vocabulary tokens')
    return [['y' + row[0], *row[1:]] for row in rows]


def decode(rows):
    if (not isinstance(rows, (list, tuple)) or not rows or
            any(not isinstance(row, (list, tuple)) or not row or not isinstance(row[0], str)
                or not row[0].startswith('y') for row in rows)):
        raise ValueError('encoded first slots require a marker')
    recovered = [[row[0][1:], *row[1:]] for row in rows]
    if not valid_source(recovered):
        raise ValueError('decoded rows are outside the declared vocabulary')
    return recovered


def rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator} if value is not None else None


def fixture():
    return [['z', 'a', 'b', 'c', 'ya', 'ya', 'z']], [['b', 'ya', 'z'] for _ in range(4)] + [['a', 'yc', 'z']]


def score(development, diagnostic):
    units = {'units': [{'unit_id': 'synthetic-development', 'selected_source_pages': ['toy-development'],
                        'partition': 'dictionary_development'},
                       {'unit_id': 'synthetic-diagnostic', 'selected_source_pages': ['toy-diagnostic'],
                        'partition': 'diagnostic_evaluation'}]}
    rows = [(SimpleNamespace(page=page, key=page + ':' + str(index)), [Token(value, len(value)) for value in row])
            for page, matrix in (('toy-development', development), ('toy-diagnostic', diagnostic))
            for index, row in enumerate(matrix)]
    counts = Counter(value for row in development for value in row[1:])
    page_units = {page: unit for unit in units['units'] for page in unit['selected_source_pages']}
    vocabulary, count = controls.source.fit_vocabulary(rows, page_units)
    if set(counts) != vocabulary or sum(counts.values()) != count:
        raise ValueError('independent development count/set construction disagrees')
    tables, prefix_gains, cell_gains = controls.collect_variant(rows, units, counts)
    a, b = prefix_gains['synthetic-diagnostic', 'y']
    matched = list(cell_gains.values())
    first, other = controls.mean([x for x, _ in matched]), controls.mean([y for _, y in matched])
    raw_exact = {'first_gain': rational(a), 'other_gain': rational(b), 'first_minus_other_gain': rational(a - b)}
    matched_exact = {'first_gain': rational(first), 'other_gain': rational(other),
                     'first_minus_other_gain': rational(first - other) if first is not None else None}
    return {
        'development_dictionary_counts': dict(sorted(counts.items())),
        'dictionary_distinct_strings': len(vocabulary), 'development_internal_tokens': count,
        'diagnostic_y_lookup_cells': tables[0]['prefixes'][0],
        'all_y_opportunity_cells': tables[0]['y_opportunity_cells'],
        'common_cell_ids': [{'frequency_bin': frequency, 'length_bin': length}
                            for _, frequency, length in sorted(cell_gains)],
        'unstandardized_same_unit': raw_exact,
        'matched_equal_cells_within_same_unit': matched_exact,
        'matched_minus_unstandardized_selectivity': rational(first - other - a + b) if first is not None else None,
        'diagnostic_units': 1, 'toy_treatments': 1,
    }


def verify_inputs():
    record = json.loads((ROOT / INPUTS).read_bytes())
    if record['analysis_id'] != 'known-marker-opportunity-v1':
        raise ValueError('wrong constructed-example identity')
    for item in record['pins'].values():
        path = ROOT / item['path']
        if not path.resolve().is_relative_to(ROOT.resolve()) or sha(path.read_bytes()) != item['sha256']:
            raise ValueError('constructed-example input pin changed')
    return record


def make_report():
    record = verify_inputs()
    development, diagnostic = fixture()
    encoded_development, encoded_diagnostic = encode(development), encode(diagnostic)
    recovered_development, recovered_diagnostic = decode(encoded_development), decode(encoded_diagnostic)
    if recovered_development != development or recovered_diagnostic != diagnostic:
        raise ValueError('known codec round trip failed')
    source_rows = development + diagnostic
    encoded_rows = encoded_development + encoded_diagnostic
    return {
        'schema_version': 1, 'analysis_id': 'known-marker-opportunity-v1',
        'scope': 'Analytically constructed synthetic measurement check; no manuscript data enters construction or scoring',
        'analytical_predictions_known_before_implementation': True,
        'manuscript_mechanism_validation': False, 'input_pins': record['pins'],
        'implementation_sha256': sha(Path(__file__).read_bytes()),
        'source_vocabulary': sorted(VOCABULARY),
        'source': {'development': development, 'diagnostic': diagnostic},
        'encoded': {'development': encoded_development, 'diagnostic': encoded_diagnostic},
        'recovered': {'development': recovered_development, 'diagnostic': recovered_diagnostic},
        'round_trip_exact': True, 'markers_inserted': len(encoded_rows),
        'total_rows': len(source_rows), 'total_source_tokens': sum(map(len, source_rows)),
        'total_encoded_tokens': sum(map(len, encoded_rows)),
        'source_ascii_characters': sum(len(token) for row in source_rows for token in row),
        'encoded_ascii_characters': sum(len(token) for row in encoded_rows for token in row),
        'diagnostic_prefix_counts': {
            'source_first_y': sum(row[0].startswith('y') for row in diagnostic),
            'encoded_first_y': sum(row[0].startswith('y') for row in encoded_diagnostic),
            'source_other_y': sum(value.startswith('y') for row in diagnostic for value in row[1:]),
            'encoded_other_y': sum(value.startswith('y') for row in encoded_diagnostic for value in row[1:]),
        },
        'lookup': score(encoded_development, encoded_diagnostic),
    }


def protect_output(output, record):
    controls.source.protect_output(output, {'input_pins': record['pins']}, ROOT / controls.source.BASE / 'partition.json')
    protected = [ROOT / item['path'] for item in record['pins'].values()] + [ROOT / INPUTS, ROOT / PLAN, Path(__file__)]
    if any(output.resolve() == path.resolve() or (output.exists() and path.exists() and output.samefile(path)) for path in protected):
        raise ValueError('constructed-example output cannot replace an input or producer')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        record = verify_inputs()
        if args.output:
            protect_output(args.output, record)
        report = make_report()
        if args.check and report != json.loads(args.check.read_bytes()):
            raise ValueError('complete constructed-example report differs')
        if args.output:
            protect_output(args.output, record)
            args.output.write_text(json.dumps(report, indent=2) + '\n')
        print('Known-codec recovery and all exact lookup/opportunity fields verified; no manuscript mechanism fit.')
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'known-marker example failed: {error}\n')


if __name__ == '__main__':
    main()
