"""Exploratory equal-representation counts at fixed original-slot distances."""

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

try:
    from .audit_transliterations import load_sources
    from .repetition_moments import conditional_moments
    from .token_baselines import paired_sources, retain, tokenize
except ImportError:
    from audit_transliterations import load_sources
    from repetition_moments import conditional_moments
    from token_baselines import paired_sources, retain, tokenize


ROOT = Path(__file__).resolve().parents[1]
DISTANCES = (1, 2, 3, 4)
PLAN = 'research/transliteration/REPETITION_DISTANCE_PLAN.md'
ENGINES = ('scripts/repetition_distances.py', 'scripts/repetition_moments.py',
           'scripts/token_baselines.py', 'scripts/audit_transliterations.py',
           'scripts/ivtff.py')


def distance_graphs(slots, distances=DISTANCES):
    """Keep original coordinates; only a pair's endpoints must be retained."""
    if not isinstance(slots, (list, tuple)) or any(
            value is not None and (not isinstance(value, str) or not value) for value in slots):
        raise ValueError('slots must be a sequence of nonempty token strings or null exclusions')
    if (not isinstance(distances, (list, tuple)) or not distances or
            any(type(d) is not int or d < 1 for d in distances) or
            len(set(distances)) != len(distances)):
        raise ValueError('distances must be distinct positive integers')
    positions = [i for i, value in enumerate(slots) if value is not None]
    indices = {position: index for index, position in enumerate(positions)}
    values = [slots[position] for position in positions]
    graphs, spanning = [], []
    for distance in distances:
        pairs = [(position, position + distance) for position in positions
                 if position + distance in indices]
        graphs.append([(indices[left], indices[right]) for left, right in pairs])
        spanning.append(sum(any(value is None for value in slots[left + 1:right])
                            for left, right in pairs))
    return values, graphs, spanning


def distance_moments(slots, distances=DISTANCES):
    """Exact joint moments under one uniform permutation of a locus's bag."""
    values, graphs, spanning = distance_graphs(slots, distances)
    moments = [conditional_moments(values, edges) for edges in graphs]
    covariance = [[Fraction(0) for _ in distances] for _ in distances]
    for i in range(len(distances)):
        covariance[i][i] = moments[i]['variance']
        for j in range(i):
            # Different distances cannot share an undirected edge.
            union = conditional_moments(values, graphs[i] + graphs[j])
            covariance[i][j] = covariance[j][i] = (
                union['variance'] - moments[i]['variance'] - moments[j]['variance']) / 2
    return {
        'eligible_pairs': [len(edges) for edges in graphs],
        'pairs_spanning_excluded_interior_slots': spanning,
        'observed_equal_pairs': [sum(values[a] == values[b] for a, b in edges) for edges in graphs],
        'expected': [moment['expected'] for moment in moments],
        'covariance': covariance,
    }


def summarize(rows, distances=DISTANCES):
    """Sum joint moments for the explicitly independent-locus control."""
    distance_graphs([], distances)
    rows = list(rows)
    keys = [key for key, _ in rows]
    if any(not isinstance(key, str) or not key for key in keys) or len(set(keys)) != len(keys):
        raise ValueError('supply distinct nonempty locus keys')
    rows.sort(key=lambda row: row[0])
    count = len(distances)
    observed, eligible, contributing, spanning = ([0] * count for _ in range(4))
    expected = [Fraction(0) for _ in distances]
    covariance = [[Fraction(0) for _ in distances] for _ in distances]
    for _, slots in rows:
        result = distance_moments(slots, distances)
        for i in range(count):
            observed[i] += result['observed_equal_pairs'][i]
            eligible[i] += result['eligible_pairs'][i]
            contributing[i] += bool(result['eligible_pairs'][i])
            spanning[i] += result['pairs_spanning_excluded_interior_slots'][i]
            expected[i] += result['expected'][i]
            for j in range(count):
                covariance[i][j] += result['covariance'][i][j]
    diagnostics = []
    for i, distance in enumerate(distances):
        variance = covariance[i][i]
        sd = math.sqrt(float(variance))
        diagnostics.append({
            'slot_distance': distance, 'eligible_pairs': eligible[i],
            'contributing_loci': contributing[i],
            'pairs_spanning_excluded_interior_slots': spanning[i],
            'observed_equal_pairs': observed[i],
            'observed_rate': round(observed[i] / eligible[i], 8) if eligible[i] else None,
            'conditional_expected_pairs_fraction': str(expected[i]),
            'conditional_expected_pairs': round(float(expected[i]), 8),
            'conditional_expected_rate': round(float(expected[i]) / eligible[i], 8) if eligible[i] else None,
            'conditional_variance': round(float(variance), 8),
            'conditional_standard_deviation': round(sd, 8),
            'observed_minus_expected_in_sd': round(float(observed[i] - expected[i]) / sd, 8) if variance else None,
            'zero_conditional_variance': not bool(variance),
        })
    digest = hashlib.sha256(json.dumps(rows, ensure_ascii=True, separators=(',', ':')).encode('ascii')).hexdigest()
    return {
        'selected_loci': len(rows), 'apparent_token_slots': sum(len(slots) for _, slots in rows),
        'retained_tokens': sum(value is not None for _, slots in rows for value in slots),
        'preprocessed_loci_sha256': digest,
        'preprocessed_digest_encoding': 'ASCII compact JSON of sorted [locus_key, original_slots] rows; null exclusions',
        'distances': diagnostics,
        'covariance_distance_order': list(distances),
        'conditional_covariance_matrix': [[round(float(value), 8) for value in row] for row in covariance],
        'conditional_covariance_fractions': [[str(value) for value in row] for row in covariance],
    }


def distance_report(sources=None):
    sources = paired_sources(load_sources() if sources is None else sources)
    sets = [{locus.key for locus in document.loci if locus.present and locus.kind == 'P0'}
            for _, document in sources]
    common = set.intersection(*sets)
    if not common:
        raise ValueError('no common present P0 loci')
    report = {
        'schema_version': 1, 'method': 'exploratory original-slot recurrence distances v1',
        'plan_sha256': hashlib.sha256((ROOT / PLAN).read_bytes()).hexdigest(),
        'engine_sha256': {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in ENGINES},
        'selection': {'kind': 'P0', 'rule': 'intersection of present P0 loci in pinned ZL3b and IT2a',
                      'count': len(common),
                      'sorted_locus_keys_sha256': hashlib.sha256(('\n'.join(sorted(common)) + '\n').encode()).hexdigest()},
        'control': 'independent uniform permutations within loci; retained representations and excluded slots fixed',
        'limits': ['Exposed exploratory corpus; no untouched evaluation or registered decoding candidate.',
                   'Distances and source treatments share material and are not independent tests.',
                   'Conditional SD is descriptive; no normal tail or generative-mechanism probability.',
                   'Endpoint-eligible pairs can span excluded interior slots; loci are not verified physical lines.'],
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
                    try:
                        tokens = tokenize(locus.text, spacing)
                    except ValueError as error:
                        raise ValueError(f'{locus.identifier}: {error}') from error
                    rows.append([locus.key, [token.value if retain(token, alternatives) else None for token in tokens]])
                variants.append({'uncertain_spaces': spacing, 'alternatives': alternatives, **summarize(rows)})
        report['sources'].append({'id': source['id'], 'url': source['url'],
                                  'sha256': source['sha256'], 'variants': variants})
    return report


def protect_output(output):
    """Reject direct, symlink, and hardlink aliases of calculation inputs."""
    catalog = ROOT / 'data/transliterations.json'
    paths = [catalog, ROOT / PLAN, ROOT / 'research/transliteration/token_baselines.json']
    paths += [ROOT / path for path in ENGINES]
    paths += [ROOT / source['path'] for source in json.loads(catalog.read_text())['sources']]
    for path in paths:
        if output.resolve() == path.resolve() or (output.exists() and path.exists() and output.samefile(path)):
            raise ValueError('output must not overwrite an input, dependency, plan, or accepted baseline')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output)
        report = distance_report()
        if args.check:
            if report != json.loads(args.check.read_text()):
                raise ValueError('recorded distance report differs from recomputation')
            print('Pinned sources, cohort, calculation, and repetition-distance report verified.')
        elif args.output:
            protect_output(args.output)
            args.output.write_text(json.dumps(report, indent=2) + '\n')
        else:
            print(json.dumps(report, indent=2))
    except (OSError, ValueError) as error:
        parser.exit(1, f'repetition distances failed: {error}\n')


if __name__ == '__main__':
    main()
