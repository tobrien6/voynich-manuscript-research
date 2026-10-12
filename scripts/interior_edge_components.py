"""Exact early/bridge/late bookkeeping of accepted interior-order statistics."""
import argparse
from fractions import Fraction
from pathlib import Path
import platform

try:
    from . import interior_unit_covariance as parent
except ImportError:
    import interior_unit_covariance as parent

ROOT = Path(__file__).resolve().parents[1]
PLAN = 'research/transliteration/INTERIOR_EDGE_COMPONENTS_PLAN.md'
PINS = 'research/transliteration/interior-edge-component-pins.json'
JOINT = 'research/transliteration/interior_unit_covariance.json'
PIN_SHA256 = '923773ef90fdfefdeb52dce5934bf12ff1ec3b8b9704504eaf7b8fb50e5e32e6'
COMPONENTS = ['early', 'bridge', 'late']
FIELDS = ['raw', 'unrestricted_expectation', 'half_expectation']


def components(values):
    if (not isinstance(values, (list, tuple)) or len(values) < 3
            or any(type(x) is not int or x < 1 for x in values)):
        raise ValueError('at least three positive integer counts required')
    m = len(values)
    cut = (m + 1) // 2
    d = [m * x - sum(values) for x in values]
    squared = sum(x * x for x in d)
    scale = Fraction(m, (m - 1) * squared) if squared else Fraction()
    early, late = d[:cut], d[cut:]
    edges = [cut - 1, 1, m - cut - 1]
    raw = [scale * sum(a * b for a, b in zip(early, early[1:])),
           scale * early[-1] * late[0],
           scale * sum(a * b for a, b in zip(late, late[1:]))]
    full = [scale * count * Fraction(-squared, m * (m - 1)) for count in edges]
    halves = [scale * Fraction(sum(block) ** 2 - sum(x * x for x in block), len(block))
              for block in (early, late)]
    half = [halves[0], scale * Fraction(sum(early) * sum(late), len(early) * len(late)), halves[1]]
    return {'interior_size': m, 'early_size': cut, 'edge_counts': edges,
            'raw': raw, 'unrestricted_expectation': full, 'half_expectation': half}


def centered(record, scope):
    if scope not in parent.SCOPES:
        raise ValueError('unrestricted or half scope required')
    return [a - b for a, b in zip(record['raw'], record[scope + '_expectation'])]


def average(records):
    if not records:
        raise ValueError('nonempty equal-locus denominator required')
    result = {field: [sum((r[field][i] for r in records), Fraction()) / len(records)
                      for i in range(3)] for field in FIELDS}
    for scope in parent.SCOPES:
        result[scope + '_centered'] = centered(result, scope)
    result['half_minus_unrestricted_expectation'] = [b - a for a, b in zip(
        result['unrestricted_expectation'], result['half_expectation'])]
    return result


def difference(grouped, ascii_result):
    return {scope: [g - a for g, a in zip(grouped[scope + '_centered'], ascii_result[scope + '_centered'])]
            for scope in parent.SCOPES}


def load_inputs():
    raw = (ROOT / PINS).read_bytes()
    if parent.sha(raw) != PIN_SHA256:
        raise ValueError('frozen component manifest changed')
    pins = parent.unit.load_split_json(raw.decode())
    for name, expected in pins.items():
        if parent.sha((ROOT / name).read_bytes()) != expected:
            raise ValueError('frozen component input changed: ' + name)
    previous = parent.unit.load_split_json((ROOT / parent.UNIT).read_text())
    joint = parent.unit.load_split_json((ROOT / JOINT).read_text())
    return previous, joint, pins


def summarize(old, converted, joint):
    if ([r['policy_id'] for r in converted] != parent.POLICIES
            or [r['policy_id'] for r in old.get('unit_policies', [])] != parent.POLICIES):
        raise ValueError('complete three-policy family required')
    n = old['unit_policies'][0]['loci']
    identities = [[(p, k, len(x)) for p, k, x in policy['rows']] for policy in converted]
    if (not n or any(len(items) != n or items != identities[0] for items in identities)
            or len({(p, k) for p, k, _ in identities[0]}) != n
            or len(joint['per_locus']) != n):
        raise ValueError('complete unique shared occurrence identities required')
    aggregates, policies = [], []
    for policy_index, (new, saved) in enumerate(zip(converted, old['unit_policies'])):
        records, per_locus = [], []
        for (page, key, values), accepted in zip(new['rows'], joint['per_locus']):
            if (page, key) != (accepted['page_id'], accepted['locus_key']):
                raise ValueError('accepted joint locus order changed')
            record = components(values)
            size, squared, adjacent = parent.unit.original.components(values)
            raw = Fraction(size * adjacent, (size - 1) * squared) if squared else Fraction()
            expected = {'unrestricted': Fraction(-1, size - 1) if squared else Fraction(),
                        'half': parent.unit.half.exact_half_expectation(values)}
            if sum(record['raw']) != raw:
                raise ValueError('raw components do not reassemble accepted association')
            for scope in parent.SCOPES:
                if (sum(record[scope + '_expectation']) != expected[scope]
                        or expected[scope] != Fraction(*map(int, accepted[scope]['uncentered_means'][policy_index]))):
                    raise ValueError('component null means do not reassemble accepted joint means')
            records.append(record)
            per_locus.append({'page_id': page, 'locus_key': key,
                              **{name: record[name] for name in ('interior_size', 'early_size', 'edge_counts')},
                              **{field: [parent.small(v) for v in record[field]] for field in FIELDS}})
        aggregate = average(records)
        for scope in parent.SCOPES:
            total = sum(aggregate[scope + '_centered'])
            if (total != parent.unpack(joint[scope]['exact_observed_centered_means'][policy_index])
                    or abs(float(total) - saved[scope]['observed_centered_association']) > 1e-12):
                raise ValueError('aggregate components do not reassemble accepted effect')
        if abs(float(sum(aggregate['half_minus_unrestricted_expectation']))
               - saved['half_minus_unrestricted_expectation']) > 1e-12:
            raise ValueError('centering shift differs from accepted unit report')
        if policy_index:
            paired = difference(aggregate, aggregates[0])
            for scope in parent.SCOPES:
                if (sum(paired[scope]) != parent.unpack(joint[scope]['paired_changes'][policy_index - 1]['observed_change_exact'])
                        or abs(float(sum(paired[scope])) - saved['paired_change_from_ascii'][scope]['observed_centered_association']) > 1e-12):
                    raise ValueError('paired component differences do not reassemble accepted change')
        else:
            paired = None
        aggregates.append(aggregate)
        policies.append({'policy_id': new['policy_id'], 'length_corpus_sha256': new['length_corpus_sha256'],
                         'loci': n, 'accepted_effect_denominator': n,
                         'aggregate': {field: [parent.large(v) for v in triplet] for field, triplet in aggregate.items()},
                         'grouped_minus_ascii_centered': {scope: [parent.large(v) for v in triplet]
                                                         for scope, triplet in paired.items()} if paired else None,
                         'attributed_parent_total_tails': {scope: {field: saved[scope][field]
                            for field in ('two_sided_tail_count', 'exploratory_two_sided_tail')} for scope in parent.SCOPES},
                         'per_locus': per_locus})
    return {'source_id': old['source_id'], 'spacing': old['spacing'], 'source_sha256': old['source_sha256'],
            'unit_policies': policies}


def report(progress=None):
    previous, joint, pins = load_inputs()
    prepared = parent.prepare(previous)
    if [(t['source_id'], t['spacing']) for t in joint['treatments']] != parent.VARIANTS:
        raise ValueError('complete accepted joint treatment inventory required')
    treatments = []
    for (old, converted), accepted in zip(prepared, joint['treatments']):
        treatments.append(summarize(old, converted, accepted))
        if progress:
            progress(old['source_id'] + '/' + old['spacing'] + ': all component identities verified')
    return {'schema_version': 1, 'method': 'exact-interior-early-bridge-late-components-v1',
            'status': 'descriptive decomposition of previously exposed encoded order effects',
            'python_version': platform.python_version(), 'input_pins': pins,
            'pin_manifest_sha256': PIN_SHA256, 'implementation_sha256': parent.sha(Path(__file__).read_bytes()),
            'components': COMPONENTS, 'selection': previous['selection'],
            'normalization': 'original whole-locus association scale; equal locus weight including zeros',
            'component_tails_computed': 0, 'new_permutation_draws': 0,
            'physical_glyph_policy_selected': False, 'mechanism_or_translation_validated': False,
            'treatments': treatments}


def protect_output(path):
    parent.unit.protect_output(path, root=ROOT)
    pins = parent.unit.load_split_json((ROOT / PINS).read_text())
    protected = [ROOT / name for name in pins] + [ROOT / PINS, Path(__file__).resolve()]
    if any(path.resolve() == item.resolve() or
           (path.exists() and item.exists() and path.samefile(item)) for item in protected):
        raise ValueError('output aliases component inputs, code or plan')


def serialize(value):
    return parent.serialize(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--new-report', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        path = args.new_report or args.check
        protect_output(path)
        if args.new_report and (path.exists() or path.is_symlink()):
            raise ValueError('new report destination already exists')
        result = report(progress=lambda message: print(message, flush=True))
        payload = serialize(result)
        if args.check:
            if not parent.unit.same_report(result, parent.unit.load_split_json(path.read_text())):
                raise ValueError('complete component report differs from replay')
        else:
            protect_output(path)
            with path.open('x', encoding='utf-8') as output:
                output.write(payload)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'Interior edge components failed: {error}\n')
    print('All 12 component families verified.' if args.check else 'All 12 component families saved.')


if __name__ == '__main__':
    main()
