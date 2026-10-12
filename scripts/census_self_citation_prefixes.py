#!/usr/bin/env python3
"""Descriptive fixed-seed prefix census with unchanged/observed output pairs."""

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import shutil
import subprocess

try:
    from .replay_self_citation import ROOT, SUPPLIED_HASH, configuration, digest, process_environment, run_process, source_inventory
    from .trace_self_citation_rows import BASE, MAIN, canonical, control_contract, instrument, row_ledger, trace_events
    from .prefix_conditional_bounds import fraction_record, locus_moments
except ImportError:
    from replay_self_citation import ROOT, SUPPLIED_HASH, configuration, digest, process_environment, run_process, source_inventory
    from trace_self_citation_rows import BASE, MAIN, canonical, control_contract, instrument, row_ledger, trace_events
    from prefix_conditional_bounds import fraction_record, locus_moments


TRACE = ROOT / 'research/literature/self-citation-row-trace.json'


def measurements(raw, ledger):
    """All eight cells, equal native-row weights; initialization never contributes."""
    if [row['generated_row_index'] for row in ledger] != list(range(len(ledger))):
        raise ValueError('ledger row identity/order changed')
    cohorts = {False: [], True: []}
    excluded = []
    initialized = 0
    for row in ledger:
        body = raw[row['start_byte']:row['end_byte_exclusive_without_line_ending']]
        if digest(body) != row['row_sha256']:
            raise ValueError('ledger row hash differs from output bytes')
        tokens = body.decode('ascii').split(' ')
        if len(tokens) != row['space_delimited_token_count'] or any(not token or not token.isalpha() for token in tokens):
            raise ValueError('native row token contract changed')
        if row['initialized_input_row']:
            initialized += 1
            excluded.append({'generated_row_index': row['generated_row_index'], 'reason': 'initialization input'})
            continue
        flag = row['model_paragraph_initial']
        if type(flag) is not bool:
            raise ValueError('generated row requires an observed boolean call flag')
        cohorts[flag].append((row['generated_row_index'], tokens))
        if len(tokens) < 2:
            excluded.append({'generated_row_index': row['generated_row_index'], 'reason': 'fewer than two native tokens'})
    cells = []
    for start in [False, True]:
        population = cohorts[start]
        eligible = [(index, tokens) for index, tokens in population if len(tokens) >= 2]
        for boundary in ['first', 'last']:
            for prefix in ['q', 'y']:
                total, others, positives = Fraction(0), Fraction(0), 0
                for _, tokens in eligible:
                    value, _ = locus_moments(tokens, boundary, prefix)
                    indicators = [int(token.startswith(prefix)) for token in tokens]
                    edge = indicators[0 if boundary == 'first' else -1]
                    total += value
                    positives += edge
                    others += Fraction(sum(indicators) - edge, len(tokens) - 1)
                count = len(eligible)
                mean = total / count if count else None
                cells.append({'model_paragraph_initial': start, 'boundary': boundary, 'prefix': prefix,
                              'population_rows': len(population), 'eligible_rows': count,
                              'boundary_positive_rows': positives, 'sum_difference_exact': fraction_record(total) if count else None,
                              'mean_difference_exact': fraction_record(mean) if mean is not None else None,
                              'mean_difference_rounded': round(float(mean), 8) if mean is not None else None,
                              'mean_other_prefix_rate_exact': fraction_record(others / count) if count else None})
    return {'initialized_rows': initialized, 'excluded_rows': excluded, 'cells': cells}


def summaries(cases):
    output = []
    for start in [False, True]:
        for boundary in ['first', 'last']:
            for prefix in ['q', 'y']:
                values, missing = [], []
                for case in cases:
                    cells = case['measurements']['cells'] if case['measurements'] is not None else []
                    matched = [cell for cell in cells if (cell['model_paragraph_initial'], cell['boundary'], cell['prefix']) ==
                               (start, boundary, prefix)]
                    if len(matched) != 1 or matched[0]['mean_difference_exact'] is None:
                        missing.append(case['seed'])
                    else:
                        item = matched[0]['mean_difference_exact']
                        values.append(Fraction(int(item['numerator']), int(item['denominator'])))
                output.append({'model_paragraph_initial': start, 'boundary': boundary, 'prefix': prefix,
                               'defined_seeds': len(values), 'missing_seeds': missing,
                               'negative_seeds': sum(value < 0 for value in values),
                               'zero_seeds': sum(value == 0 for value in values),
                               'positive_seeds': sum(value > 0 for value in values),
                               'minimum_rounded': round(float(min(values)), 8) if values else None,
                               'maximum_rounded': round(float(max(values)), 8) if values else None,
                               'mean_across_seed_means_exact': fraction_record(sum(values, Fraction(0)) / len(values)) if values else None})
    return output


def census(reference, java_home, work):
    paths, inventory, base_config, supplied = source_inventory(reference)
    base_bytes, trace_bytes = BASE.read_bytes(), TRACE.read_bytes()
    baseline, trace = json.loads(base_bytes), json.loads(trace_bytes)
    release, helper_hash = control_contract(baseline)
    if (trace['schema_version'] != 1 or trace['accepted_output_preserving_trace'] is not True or
            trace['observer_sha256'] != digest((ROOT / 'scripts/trace_self_citation_rows.py').read_bytes()) or
            trace['shared_replay_helper_sha256'] != helper_hash or trace['base_repeatability_report_sha256'] != digest(base_bytes)):
        raise ValueError('accepted row-observer/control identity changed')
    work.mkdir(parents=True, exist_ok=False)
    environment = process_environment(os.environ)
    java, javac = java_home / 'bin/java', java_home / 'bin/javac'
    for name, executable in [('java', java), ('javac', javac)]:
        result = subprocess.run([str(executable), '-version'], env=environment, capture_output=True, check=True, timeout=15)
        if (digest(executable.read_bytes()) != baseline['runtime'][name]['executable_sha256'] or
                (result.stdout + result.stderr).decode().strip() != baseline['runtime'][name]['version_output']):
            raise ValueError('runtime/compiler differs from the fixed control')
    empty = work / 'empty-classpath'
    empty.mkdir()
    builds, classes = {}, {}
    for mode in ['original', 'observed']:
        folder = work / mode
        folder.mkdir()
        sources, target = folder / 'sources', folder / 'classes'
        shutil.copytree(reference / 'source/src/main/java', sources)
        target.mkdir()
        if mode == 'observed':
            main = sources / MAIN.removeprefix('source/src/main/java/')
            main.write_bytes(instrument(main.read_bytes()))
            if digest(main.read_bytes()) != trace['instrumented_main_source_sha256']:
                raise ValueError('instrumented main source differs from accepted observer')
        process = run_process([str(javac), *baseline['build_flags'], '--class-path', str(empty), '-d', str(target),
                               *[str(sources / path.removeprefix('source/src/main/java/')) for path in paths]],
                              folder, environment, folder / 'build')
        class_records = [{'path': str(path.relative_to(target)), 'bytes': path.stat().st_size,
                          'sha256': digest(path.read_bytes())} for path in sorted(target.rglob('*.class'))]
        expected = baseline['class_inventory'] if mode == 'original' else trace['class_inventory']
        if process['exit_code'] == 0 and class_records != expected:
            raise ValueError('compiled classes differ from accepted control/observer')
        builds[mode] = {'process': process, 'class_inventory_sha256': digest(canonical(class_records))}
        classes[mode] = target
    cases = []
    for seed in range(1, 21):
        settings = configuration(base_config, {'save.path': './output/', 'save.filename': 'generated.txt',
                                              'method.random.pseudo.seed': str(seed)})
        outputs, processes = {}, {}
        for mode in ['original', 'observed']:
            folder = work / f'seed-{seed:02d}' / mode
            folder.mkdir(parents=True)
            (folder / 'output').mkdir()
            (folder / 'conf.properties').write_bytes(settings)
            process = (run_process([str(java), *baseline['jvm_flags'], '-cp', str(classes[mode]),
                                    'de.voynich.text.SelfCitationTextGenerator'], folder, environment, folder / 'process')
                       if builds[mode]['process']['exit_code'] == 0 else
                       {'exit_code': None, 'timed_out': False, 'not_run': 'build failed'})
            path = folder / 'output/generated.txt'
            outputs[mode] = path.read_bytes() if path.exists() else None
            processes[mode] = process
        raw = outputs['observed']
        pair_equal = raw is not None and outputs['original'] == raw
        metric, ledger_hash, event_hash, error = None, None, None, None
        good = pair_equal and all(item['exit_code'] == 0 and not item['timed_out'] for item in processes.values())
        if seed == 19:
            good = good and raw == supplied and digest(raw) == SUPPLIED_HASH
        if good:
            try:
                folder = work / f'seed-{seed:02d}' / 'observed'
                events, _ = trace_events((folder / 'process.stderr.txt').read_bytes(), 1, 1200)
                ledger = row_ledger(raw, events, 1, 1200)
                (folder / 'row-ledger.json').write_bytes(canonical(ledger))
                ledger_hash, event_hash = digest(canonical(ledger)), digest(canonical(events))
                metric = measurements(raw, ledger)
            except ValueError as problem:
                error = str(problem)
        else:
            error = 'paired processes/complete output control failed'
        accepted = good and error is None and metric is not None
        cases.append({'seed': seed, 'processes': processes, 'effective_configuration_sha256': digest(settings),
                      'output_sha256': {mode: digest(raw) if raw is not None else None for mode, raw in outputs.items()},
                      'paired_complete_bytes_equal': pair_equal, 'accepted_case': accepted, 'error': error,
                      'canonical_events_sha256': event_hash, 'canonical_ledger_sha256': ledger_hash, 'measurements': metric})
        print(f'seed {seed:02d}: accepted_case={accepted}', flush=True)
    unchanged = source_inventory(reference)[1] == inventory
    return {'schema_version': 1, 'method': 'fixed-seed native generated prefix census v1',
            'plan_sha256': digest((ROOT / 'research/literature/SELF_CITATION_PREFIX_SEED_PLAN.md').read_bytes()),
            'census_producer_sha256': digest(Path(__file__).read_bytes()), 'shared_replay_helper_sha256': helper_hash,
            'row_observer_report_sha256': digest(trace_bytes), 'base_repeatability_report_sha256': digest(base_bytes),
            'source_commit': baseline['source_commit'], 'source_inventory_sha256': digest(canonical(inventory)),
            'runtime': baseline['runtime'], 'builds': builds, 'seed_schedule': list(range(1, 21)),
            'requested_rows_per_case_including_initialization': 1200, 'cases': cases, 'summaries': summaries(cases),
            'source_inputs_unchanged_after_runs': unchanged,
            'all_planned_cases_accepted': unchanged and all(case['accepted_case'] for case in cases),
            'scope': 'deterministic seed sensitivity; native generated-row q/y descriptors; no calibrated probability or manuscript fit'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['reference', 'java-home', 'work', 'output']:
        parser.add_argument(f'--{name}', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('output record exists; choose a new record')
        report = census(args.reference.resolve(), args.java_home.resolve(), args.work.resolve())
        with args.output.open('x', encoding='utf-8') as output:
            output.write(json.dumps(report, indent=2) + '\n')
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Prefix census failed: {error}\n')
    print(f'Artifacts retained in {args.work}; record saved to {args.output}.')
    return not report['all_planned_cases_accepted']


if __name__ == '__main__':
    raise SystemExit(main())
