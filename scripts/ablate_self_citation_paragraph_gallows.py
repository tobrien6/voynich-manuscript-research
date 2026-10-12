#!/usr/bin/env python3
"""Change only the paragraph augmentation predicate and retain all paired seeds."""

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import shutil
import subprocess

try:
    from .replay_self_citation import ROOT, configuration, digest, process_environment, run_process, source_inventory
    from .trace_self_citation_rows import BASE, MAIN, canonical, control_contract, instrument, row_ledger, trace_events
    from .census_self_citation_prefixes import measurements
    from .prefix_conditional_bounds import fraction_record
except ImportError:
    from replay_self_citation import ROOT, configuration, digest, process_environment, run_process, source_inventory
    from trace_self_citation_rows import BASE, MAIN, canonical, control_contract, instrument, row_ledger, trace_events
    from census_self_citation_prefixes import measurements
    from prefix_conditional_bounds import fraction_record


DEFAULT = ROOT / 'research/literature/self-citation-prefix-seeds.json'
TARGET = 'source/src/main/java/de/voynich/text/morph/AbstractBaseGroupMorpher.java'
PREDICATE = b'isParagraphInitial && rand < Constants.PARAGRAPH_STARTS_WITH_GALLOW_PROPABILITY'
ZERO = b'isParagraphInitial && rand < 0'


def ablate(raw):
    if raw.count(PREDICATE) != 1:
        raise ValueError('require exactly one paragraph augmentation predicate')
    patched = raw.replace(PREDICATE, ZERO)
    if patched.replace(ZERO, PREDICATE) != raw:
        raise ValueError('ablation changed bytes outside the declared predicate')
    return patched


def as_fraction(record):
    return Fraction(int(record['numerator']), int(record['denominator'])) if record is not None else None


def paired_cells(default, observed):
    def identity(cell):
        return cell['model_paragraph_initial'], cell['boundary'], cell['prefix']
    index = {identity(cell): cell for cell in default['cells']}
    if len(index) != 8 or len(observed['cells']) != 8 or {identity(cell) for cell in observed['cells']} != set(index):
        raise ValueError('paired comparison does not preserve the complete eight-cell family')
    result = []
    for cell in observed['cells']:
        original = index[identity(cell)]
        old, new = as_fraction(original['mean_difference_exact']), as_fraction(cell['mean_difference_exact'])
        delta = new - old if old is not None and new is not None else None
        result.append({'model_paragraph_initial': cell['model_paragraph_initial'], 'boundary': cell['boundary'],
                       'prefix': cell['prefix'], 'default_eligible_rows': original['eligible_rows'],
                       'ablated_eligible_rows': cell['eligible_rows'], 'default_mean_exact': original['mean_difference_exact'],
                       'ablated_mean_exact': cell['mean_difference_exact'],
                       'ablated_minus_default_exact': fraction_record(delta) if delta is not None else None,
                       'ablated_minus_default_rounded': round(float(delta), 8) if delta is not None else None})
    return result


def response_summary(cases):
    result = []
    for start in [False, True]:
        for boundary in ['first', 'last']:
            for prefix in ['q', 'y']:
                values, missing = [], []
                for case in cases:
                    cells = case['paired_cells'] or []
                    matches = [cell for cell in cells if (cell['model_paragraph_initial'], cell['boundary'], cell['prefix']) ==
                               (start, boundary, prefix)]
                    value = as_fraction(matches[0]['ablated_minus_default_exact']) if len(matches) == 1 else None
                    if value is None:
                        missing.append(case['seed'])
                    else:
                        values.append(value)
                mean = sum(values, Fraction(0)) / len(values) if values else None
                primary = start and boundary == 'first'
                complete = not missing and len(values) == 20
                result.append({'model_paragraph_initial': start, 'boundary': boundary, 'prefix': prefix,
                               'defined_seeds': len(values), 'missing_seeds': missing,
                               'negative_seed_differences': sum(value < 0 for value in values),
                               'zero_seed_differences': sum(value == 0 for value in values),
                               'positive_seed_differences': sum(value > 0 for value in values),
                               'minimum_difference_rounded': round(float(min(values)), 8) if values else None,
                               'maximum_difference_rounded': round(float(max(values)), 8) if values else None,
                               'mean_difference_exact': fraction_record(mean) if mean is not None else None,
                               'primary_directional_prediction': primary,
                               'primary_outcome': ('positive' if mean > 0 else 'nonpositive') if primary and complete else
                                                  ('unresolved' if primary else 'descriptive')})
    return result


def experiment(reference, java_home, work):
    paths, inventory, base_config, _ = source_inventory(reference)
    base_bytes, default_bytes = BASE.read_bytes(), DEFAULT.read_bytes()
    baseline, default = json.loads(base_bytes), json.loads(default_bytes)
    _, helper_hash = control_contract(baseline)
    if (default['schema_version'] != 1 or default['method'] != 'fixed-seed native generated prefix census v1' or
            default['seed_schedule'] != list(range(1, 21)) or default['all_planned_cases_accepted'] is not True or
            default['census_producer_sha256'] != digest((ROOT / 'scripts/census_self_citation_prefixes.py').read_bytes()) or
            default['base_repeatability_report_sha256'] != digest(base_bytes) or
            default['shared_replay_helper_sha256'] != helper_hash):
        raise ValueError('frozen default census/producer identity changed')
    defaults = {case['seed']: case for case in default['cases']}
    if len(defaults) != 20 or list(defaults) != list(range(1, 21)):
        raise ValueError('default seed family changed')
    original = (reference / TARGET).read_bytes()
    patched = ablate(original)
    work.mkdir(parents=True, exist_ok=False)
    environment = process_environment(os.environ)
    java, javac = java_home / 'bin/java', java_home / 'bin/javac'
    for name, executable in [('java', java), ('javac', javac)]:
        output = subprocess.run([str(executable), '-version'], capture_output=True, env=environment, check=True, timeout=15)
        if (digest(executable.read_bytes()) != baseline['runtime'][name]['executable_sha256'] or
                (output.stdout + output.stderr).decode().strip() != baseline['runtime'][name]['version_output']):
            raise ValueError('runtime/compiler differs from the frozen default')
    empty = work / 'empty-classpath'
    empty.mkdir()
    classes, builds = {}, {}
    for mode in ['original', 'observed']:
        folder = work / mode
        folder.mkdir()
        sources, target = folder / 'sources', folder / 'classes'
        shutil.copytree(reference / 'source/src/main/java', sources)
        target.mkdir()
        (sources / TARGET.removeprefix('source/src/main/java/')).write_bytes(patched)
        observed_main = instrument((reference / MAIN).read_bytes()) if mode == 'observed' else (reference / MAIN).read_bytes()
        if mode == 'observed':
            (sources / MAIN.removeprefix('source/src/main/java/')).write_bytes(observed_main)
        for path in paths:
            expected = patched if path == TARGET else observed_main if path == MAIN else (reference / path).read_bytes()
            if (sources / path.removeprefix('source/src/main/java/')).read_bytes() != expected:
                raise ValueError('source copy contains an undeclared modification')
        process = run_process([str(javac), *baseline['build_flags'], '--class-path', str(empty), '-d', str(target),
                               *[str(sources / path.removeprefix('source/src/main/java/')) for path in paths]],
                              folder, environment, folder / 'build')
        records = [{'path': str(path.relative_to(target)), 'bytes': path.stat().st_size,
                    'sha256': digest(path.read_bytes())} for path in sorted(target.rglob('*.class'))]
        (folder / 'class-inventory.json').write_bytes(canonical(records))
        builds[mode] = {'process': process, 'class_inventory_sha256': digest(canonical(records))}
        classes[mode] = target
    cases = []
    for seed in range(1, 21):
        config = configuration(base_config, {'save.path': './output/', 'save.filename': 'generated.txt',
                                            'method.random.pseudo.seed': str(seed)})
        if digest(config) != defaults[seed]['effective_configuration_sha256']:
            raise ValueError('ablation configuration differs from the paired default')
        outputs, processes = {}, {}
        for mode in ['original', 'observed']:
            folder = work / f'seed-{seed:02d}' / mode
            folder.mkdir(parents=True)
            (folder / 'output').mkdir()
            (folder / 'conf.properties').write_bytes(config)
            process = (run_process([str(java), *baseline['jvm_flags'], '-cp', str(classes[mode]),
                                    'de.voynich.text.SelfCitationTextGenerator'], folder, environment, folder / 'process')
                       if builds[mode]['process']['exit_code'] == 0 else
                       {'exit_code': None, 'timed_out': False, 'not_run': 'build failed'})
            path = folder / 'output/generated.txt'
            outputs[mode] = path.read_bytes() if path.exists() else None
            processes[mode] = process
        raw = outputs['observed']
        equal = raw is not None and raw == outputs['original']
        metric, paired, error, ledger_hash, event_hash = None, None, None, None, None
        if equal and all(process['exit_code'] == 0 and not process['timed_out'] for process in processes.values()):
            try:
                folder = work / f'seed-{seed:02d}' / 'observed'
                events, _ = trace_events((folder / 'process.stderr.txt').read_bytes(), 1, 1200)
                ledger = row_ledger(raw, events, 1, 1200)
                (folder / 'row-ledger.json').write_bytes(canonical(ledger))
                ledger_hash, event_hash = digest(canonical(ledger)), digest(canonical(events))
                metric = measurements(raw, ledger)
                paired = paired_cells(defaults[seed]['measurements'], metric)
            except ValueError as problem:
                error = str(problem)
        else:
            error = 'ablated process/output-preservation control failed'
        good = error is None and paired is not None
        cases.append({'seed': seed, 'processes': processes, 'accepted_case': good, 'error': error,
                      'effective_configuration_sha256': digest(config),
                      'output_sha256': {mode: digest(raw) if raw is not None else None for mode, raw in outputs.items()},
                      'ablated_observer_preserves_complete_bytes': equal,
                      'canonical_ledger_sha256': ledger_hash, 'canonical_events_sha256': event_hash,
                      'ablated_measurements': metric, 'paired_cells': paired})
        print(f'paragraph-zero seed {seed:02d}: accepted_case={good}', flush=True)
    unchanged = source_inventory(reference)[1] == inventory
    summary = response_summary(cases)
    return {'schema_version': 1, 'method': 'paragraph-only gallows augmentation threshold-zero intervention v1',
            'plan_sha256': digest((ROOT / 'research/literature/SELF_CITATION_GALLOWS_PLAN.md').read_bytes()),
            'producer_sha256': digest(Path(__file__).read_bytes()), 'default_census_sha256': digest(default_bytes),
            'shared_measurement_helper_sha256': digest((ROOT / 'scripts/census_self_citation_prefixes.py').read_bytes()),
            'shared_replay_helper_sha256': helper_hash, 'source_commit': baseline['source_commit'],
            'target_source_path': TARGET, 'original_target_source_sha256': digest(original),
            'ablated_target_source_sha256': digest(patched), 'unchanged_shared_threshold': 94,
            'paragraph_augmentation_threshold': 0, 'builds': builds, 'runtime': baseline['runtime'],
            'seed_schedule': list(range(1, 21)), 'cases': cases, 'summaries': summary,
            'source_inputs_unchanged_after_runs': unchanged,
            'all_planned_cases_accepted': unchanged and all(case['accepted_case'] for case in cases),
            'scope': 'software intervention on exposed model; conditional populations/RNG paths can differ; no manuscript fit or translation'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['reference', 'java-home', 'work', 'output']:
        parser.add_argument(f'--{name}', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('output record exists; choose a new record')
        report = experiment(args.reference.resolve(), args.java_home.resolve(), args.work.resolve())
        with args.output.open('x', encoding='utf-8') as output:
            output.write(json.dumps(report, indent=2) + '\n')
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Paragraph ablation failed: {error}\n')
    print(f'Artifacts retained in {args.work}; record saved to {args.output}.')
    return not report['all_planned_cases_accepted']


if __name__ == '__main__':
    raise SystemExit(main())
