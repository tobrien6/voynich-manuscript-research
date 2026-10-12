"""Audit row versus comparison-opportunity weights on every frozen default case."""

import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path

try:
    from .replay_self_citation import ROOT, digest
    from .trace_self_citation_rows import canonical, row_ledger, trace_events
except ImportError:
    from replay_self_citation import ROOT, digest
    from trace_self_citation_rows import canonical, row_ledger, trace_events

SOURCE = ROOT / 'research/literature/self-citation-prefix-seeds.json'
SOURCE_SHA256 = '8a770fcd41340960b985e5e035c1b135f91137b2d0aa4acffdd6c075fc2d47a0'
PLAN = ROOT / 'research/literature/SELF_CITATION_PREFIX_WEIGHT_PLAN.md'
FAMILY = [(start, boundary, prefix) for start in (False, True)
          for boundary in ('first', 'last') for prefix in ('q', 'y')]


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON object key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def fraction(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def as_fraction(value):
    return Fraction(int(value['numerator']), int(value['denominator']))


def sign(value):
    return 'negative' if value < 0 else 'positive' if value > 0 else 'zero'


def measure(rows, boundary, prefix):
    if boundary not in ('first', 'last') or prefix not in ('q', 'y'):
        raise ValueError('require a declared boundary/prefix cell')
    eligible = [row for row in rows if len(row) >= 2]
    count = len(eligible)
    if not count:
        raise ValueError('frozen cell has no eligible rows; family is incomplete')
    weights, differences, edge_count, weighted_edges, other_count = [], [], 0, 0, 0
    for row in eligible:
        weight = len(row) - 1
        edge = int(row[0 if boundary == 'first' else -1].startswith(prefix))
        others = sum(token.startswith(prefix) for token in row) - edge
        weights.append(weight)
        differences.append(Fraction(edge) - Fraction(others, weight))
        edge_count += edge
        weighted_edges += weight * edge
        other_count += others
    opportunities = sum(weights)
    total = sum(differences, Fraction())
    equal = total / count
    weighted_total = weighted_edges - other_count
    weighted = Fraction(weighted_total, opportunities)
    mean_weight = Fraction(opportunities, count)
    covariance = Fraction(weighted_total, count) - mean_weight * equal
    change = weighted - equal
    if change != covariance / mean_weight:
        raise ValueError('exact weighting decomposition failed')
    return {'population_rows': len(rows), 'eligible_rows': count,
            'total_comparison_opportunities': opportunities,
            'boundary_positive_rows': edge_count,
            'weighted_boundary_positive_opportunities': weighted_edges,
            'other_prefix_occurrences': other_count,
            'equal_row_sum_difference_exact': fraction(total),
            'equal_row_mean_difference_exact': fraction(equal),
            'equal_row_other_prefix_rate_exact': fraction(Fraction(edge_count, count) - equal),
            'opportunity_weighted_mean_difference_exact': fraction(weighted),
            'mean_weight_exact': fraction(mean_weight),
            'population_covariance_weight_contrast_exact': fraction(covariance),
            'weighted_minus_equal_exact': fraction(change),
            'equal_row_sign': sign(equal), 'opportunity_weighted_sign': sign(weighted),
            'sign_transition': sign(equal) + '->' + sign(weighted)}


def read_case(raw_work, case):
    if case['accepted_case'] is not True or case['paired_complete_bytes_equal'] is not True or case['error'] is not None:
        raise ValueError('default case is not accepted')
    folder = raw_work / f"seed-{case['seed']:02d}"
    outputs = []
    for mode in ('original', 'observed'):
        sub = folder / mode
        output = (sub / 'output/generated.txt').read_bytes()
        if digest(output) != case['output_sha256'][mode]:
            raise ValueError('native output differs from frozen case')
        if digest((sub / 'conf.properties').read_bytes()) != case['effective_configuration_sha256']:
            raise ValueError('configuration differs from frozen case')
        process = case['processes'][mode]
        if process['exit_code'] != 0 or process['timed_out'] is not False:
            raise ValueError('default process failed or timed out')
        for stream in ('stdout', 'stderr'):
            log = (sub / f'process.{stream}.txt').read_bytes()
            if len(log) != process[stream + '_bytes'] or digest(log) != process[stream + '_sha256']:
                raise ValueError('process log differs from frozen case')
        outputs.append(output)
    if outputs[0] != outputs[1]:
        raise ValueError('complete default output pair differs')
    raw = outputs[1]
    events, _ = trace_events((folder / 'observed/process.stderr.txt').read_bytes(), 1, 1200)
    ledger = row_ledger(raw, events, 1, 1200)
    stored = strict_json((folder / 'observed/row-ledger.json').read_bytes())
    if (canonical(stored) != canonical(ledger) or digest(canonical(ledger)) != case['canonical_ledger_sha256']
            or digest(canonical(events)) != case['canonical_events_sha256']):
        raise ValueError('row ledger/events differ from frozen case')
    cohorts = {False: [], True: []}
    excluded = [{'generated_row_index': 0, 'reason': 'initialization input'}]
    for row in ledger[1:]:
        flag = row['model_paragraph_initial']
        if type(flag) is not bool:
            raise ValueError('generated row flag is not an observed Boolean')
        tokens = raw[row['start_byte']:row['end_byte_exclusive_without_line_ending']].decode('ascii').split(' ')
        cohorts[flag].append(tokens)
        if len(tokens) < 2:
            excluded.append({'generated_row_index': row['generated_row_index'], 'reason': 'fewer than two native tokens'})
    old = case['measurements']
    if old['initialized_rows'] != 1 or canonical(excluded) != canonical(old['excluded_rows']):
        raise ValueError('default exclusions changed')
    index = {(c['model_paragraph_initial'], c['boundary'], c['prefix']): c for c in old['cells']}
    if len(old['cells']) != 8 or set(index) != set(FAMILY):
        raise ValueError('default eight-cell family changed')
    cells = []
    fields = {'population_rows': 'population_rows', 'eligible_rows': 'eligible_rows',
              'boundary_positive_rows': 'boundary_positive_rows',
              'sum_difference_exact': 'equal_row_sum_difference_exact',
              'mean_difference_exact': 'equal_row_mean_difference_exact',
              'mean_other_prefix_rate_exact': 'equal_row_other_prefix_rate_exact'}
    for start, boundary, prefix in FAMILY:
        measured = measure(cohorts[start], boundary, prefix)
        parent = index[start, boundary, prefix]
        if any(canonical(parent[key]) != canonical(measured[new]) for key, new in fields.items()):
            raise ValueError('equal-row measurement differs from frozen census')
        cells.append({'model_paragraph_initial': start, 'boundary': boundary, 'prefix': prefix, **measured})
    return {'seed': case['seed'], 'all_frozen_case_fingerprints_verified': True,
            **{k: case[k] for k in ('effective_configuration_sha256', 'output_sha256',
                                    'canonical_events_sha256', 'canonical_ledger_sha256')},
            'initialized_rows': 1, 'excluded_rows': excluded, 'cells': cells}


def summarize(cases):
    summaries = []
    for start, boundary, prefix in FAMILY:
        cells = [next(c for c in case['cells'] if
                      (c['model_paragraph_initial'], c['boundary'], c['prefix']) == (start, boundary, prefix))
                 for case in cases]
        if len(cells) != 20:
            raise ValueError('complete twenty-seed family required')
        equal = [as_fraction(c['equal_row_mean_difference_exact']) for c in cells]
        weighted = [as_fraction(c['opportunity_weighted_mean_difference_exact']) for c in cells]
        changes = [right - left for left, right in zip(equal, weighted)]
        summaries.append({'model_paragraph_initial': start, 'boundary': boundary, 'prefix': prefix,
                          'defined_seeds': 20,
                          'equal_row_mean_across_seeds_exact': fraction(sum(equal) / 20),
                          'opportunity_weighted_mean_across_seeds_exact': fraction(sum(weighted) / 20),
                          'mean_change_across_seeds_exact': fraction(sum(changes) / 20),
                          'minimum_change_exact': fraction(min(changes)),
                          'maximum_change_exact': fraction(max(changes)),
                          'change_sign_counts': dict(sorted(Counter(map(sign, changes)).items())),
                          'seed_sign_transitions': dict(sorted(Counter(c['sign_transition'] for c in cells).items())),
                          'minimum_eligible_rows': min(c['eligible_rows'] for c in cells),
                          'maximum_eligible_rows': max(c['eligible_rows'] for c in cells),
                          'minimum_total_opportunities': min(c['total_comparison_opportunities'] for c in cells),
                          'maximum_total_opportunities': max(c['total_comparison_opportunities'] for c in cells)})
    return summaries


def audit(raw_work):
    raw = SOURCE.read_bytes()
    if digest(raw) != SOURCE_SHA256:
        raise ValueError('frozen default census identity changed')
    source = strict_json(raw)
    observer_path = ROOT / 'research/literature/self-citation-row-trace.json'
    observer_raw = observer_path.read_bytes()
    observer = strict_json(observer_raw)
    helpers = ['replay_self_citation.py', 'trace_self_citation_rows.py', 'census_self_citation_prefixes.py']
    pins = {f'scripts/{name}': digest((ROOT / 'scripts' / name).read_bytes()) for name in helpers}
    if (source['seed_schedule'] != list(range(1, 21)) or
            [c['seed'] for c in source['cases']] != list(range(1, 21)) or
            source['all_planned_cases_accepted'] is not True or
            source['requested_rows_per_case_including_initialization'] != 1200 or
            source['census_producer_sha256'] != pins['scripts/census_self_citation_prefixes.py'] or
            source['shared_replay_helper_sha256'] != pins['scripts/replay_self_citation.py'] or
            source['row_observer_report_sha256'] != digest(observer_raw) or
            observer['observer_sha256'] != pins['scripts/trace_self_citation_rows.py'] or
            source['base_repeatability_report_sha256'] != digest((ROOT / 'research/literature/self-citation-repeatability.json').read_bytes())):
        raise ValueError('default family/helper provenance changed')
    cases = [read_case(raw_work, case) for case in source['cases']]
    return {'schema_version': 1, 'method': 'native-prefix-row-versus-comparison-opportunity-weights-v1',
            'plan_sha256': digest(PLAN.read_bytes()), 'producer_sha256': digest(Path(__file__).read_bytes()),
            'inputs': {'default_census_sha256': digest(raw), 'source_commit': source['source_commit'],
                       'helper_sha256': pins, 'raw_generated_text_redistributed': False},
            'rules': {'same_eligible_rows_in_both_measures': True, 'opportunity_weight': 'native token count minus one',
                      'covariance_divisor': 'eligible row count', 'seed_summary_weight': 'equal per seed',
                      'directional_prediction': None, 'success_threshold': None},
            'seed_schedule': source['seed_schedule'], 'all_planned_cases_accepted': True,
            'cases': cases, 'summaries': summarize(cases),
            'scope': 'exposed software-descriptor sensitivity only; no generator change, manuscript fit or translation'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-work', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output and (args.output.exists() or args.output.is_symlink()):
            raise ValueError('output exists; choose a new record')
        result = audit(args.raw_work.resolve())
        if args.check and canonical(strict_json(args.check.read_bytes())) != canonical(result):
            raise ValueError('weighting report differs from complete pinned replay')
        if args.output:
            with args.output.open('xb') as file:
                file.write((json.dumps(result, indent=2) + '\n').encode())
    except (OSError, ValueError, KeyError, UnicodeError) as error:
        parser.exit(1, f'Prefix weighting audit failed: {error}\n')
    print('Verified all 20 frozen cases and 160 weighting cells; no manuscript comparison.')


if __name__ == '__main__':
    main()
