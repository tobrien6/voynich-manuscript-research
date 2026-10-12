"""Fixed, exposed-data prefix diagnostic; encoded loci and model rows differ.

The numerical helpers do not execute Java or infer glyph/paragraph equivalence.
The local producer verifies a pinned observer before using its instrumentation.
"""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import types

try:
    from .audit_transliterations import ROOT, load_sources
    from .conservative_prefixes import common_cohort
    from .eva_token_adapter import build
    from .prefix_strata import paragraph_start
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from conservative_prefixes import common_cohort
    from eva_token_adapter import build
    from prefix_strata import paragraph_start
    from token_baselines import paired_sources


SOURCE_IDS = ('ZL3b', 'IT2a')
SPACING = ('split', 'join')
PREFIXES = ('q', 'y')
BOUNDARIES = ('first', 'last')
PLAN_COMMIT = '586d4b50e155880cd5fb9c7f554c22b16b3dd046'
AMENDMENT_COMMIT = '7c54f11344e8d1a26c8cdf4a41e2437fe8ca546b'
PROTOCOL_SHA256 = '8fb75078e4d013c951b481c50d7e4a8b082ae8e604e0310ee5834c24bca66c3c'
PROTOCOL = ROOT / 'research/literature/self-citation-prefix-protocol.json'
PROFILE_IDENTITIES = {(initial, boundary, prefix) for initial in (False, True)
                      for boundary in BOUNDARIES for prefix in PREFIXES}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packed(value):
    return ({'numerator': value.numerator, 'denominator': value.denominator,
             'mean': float(value)} if value is not None else None)


def unpack(value):
    return Fraction(value['numerator'], value['denominator']) if value is not None else None


def prefix_contrast(groups, boundary, prefix):
    require(boundary in BOUNDARIES and prefix in PREFIXES, 'undeclared boundary or prefix')
    require(len(groups) >= 2 and all(isinstance(group, str) and re.fullmatch('[A-Za-z]+', group)
                                  for group in groups), 'need at least two plain ASCII groups')
    values = [int(group.startswith(prefix)) for group in groups]
    edge = values[0 if boundary == 'first' else -1]
    return Fraction(edge * len(values) - sum(values), len(values) - 1)


def profile(rows):
    """Rows are (identity, group strings, context flag); keep both empty contexts."""
    require(len({row[0] for row in rows}) == len(rows), 'duplicate measured row identity')
    require(all(type(row[2]) is bool for row in rows), 'measured context must be an explicit boolean')
    output = []
    for initial in (False, True):
        cohort = [groups for _, groups, context in rows if context == initial]
        for boundary in BOUNDARIES:
            for prefix in PREFIXES:
                value = sum((prefix_contrast(groups, boundary, prefix) for groups in cohort), Fraction())
                output.append({'paragraph_initial': initial, 'boundary': boundary, 'prefix': prefix,
                               'rows': len(cohort), 'group_occurrences': sum(map(len, cohort)),
                               'contrast': packed(value / len(cohort)) if cohort else None})
    return output


def select_target(sources, payloads):
    require(Counter(source['id'] for source, _ in sources) == Counter(SOURCE_IDS),
            'require exactly both declared native sources')
    expected = {source['id']: source['sha256'] for source, _ in sources}
    indexes = {}
    for source, document in sources:
        loci = [locus for locus in document.loci if locus.present and locus.kind == 'P0']
        indexes[source['id']] = {locus.key: locus for locus in loci}
        require(len(indexes[source['id']]) == len(loci), 'duplicate native P0 key')
    candidates = set.intersection(*(set(indexes[source]) for source in SOURCE_IDS))
    common, records, excluded, counts = common_cohort(payloads, expected, candidates)
    selected, additional = [], []
    for key in sorted(common):
        reasons = []
        labels = {source: indexes[source][key].variables.get('L', 'unset') for source in SOURCE_IDS}
        if any(label != 'B' for label in labels.values()):
            reasons.append('not_native_B_in_both_sources')
        for source in SOURCE_IDS:
            for spacing in SPACING:
                drawing = records[(source, spacing, key)].get('drawing_interruption_count')
                require(type(drawing) is int and drawing >= 0, 'drawing count missing or invalid')
                if drawing:
                    reasons.append(f'{source}/{spacing}:drawing_interruption')
        if reasons:
            additional.append({'locus_key': key, 'source_L_labels': labels, 'reasons': reasons})
        else:
            selected.append(key)
    require(selected, 'empty frozen B cohort')
    variants = []
    for source in SOURCE_IDS:
        for spacing in SPACING:
            rows = [(key, records[(source, spacing, key)]['tokens'], paragraph_start(indexes[source][key]))
                    for key in selected]
            variants.append({'source_id': source, 'spacing': spacing, 'profile': profile(rows),
                             'row_context_digest': digest(canonical(rows))})
    return {'candidate_shared_P0': len(candidates), 'accepted_common_cohort': len(common),
            'selected_keys': selected, 'selected_keys_sha256': digest(canonical(selected)),
            'common_cohort_exclusions': excluded, 'additional_exclusions': additional,
            'source_policy_counts': counts, 'variants': variants,
            'sources': [{field: source[field] for field in ('id', 'path', 'url', 'sha256', 'alphabet')}
                        for source, _ in sources]}


def finite_ranges(target, simulations, seeds):
    require(seeds and len(seeds) == len(set(seeds)) and
            all(type(seed) is int and seed > 0 for seed in seeds), 'seed list must be nonempty and unique')
    require([case['seed'] for case in simulations] == list(seeds), 'missing/duplicate/unordered seed case')
    require(all(case['accepted'] is True for case in simulations), 'failed case blocks complete planned comparison')
    require({(item['source_id'], item['spacing']) for item in target['variants']} ==
            {(source, spacing) for source in SOURCE_IDS for spacing in SPACING} and
            len(target['variants']) == 4, 'require every planned source/spacing target')
    for item in [*target['variants'], *simulations]:
        require(len(item['profile']) == 8 and
                {tuple(row[key] for key in ('paragraph_initial', 'boundary', 'prefix'))
                 for row in item['profile']} == PROFILE_IDENTITIES,
                'require exactly the eight planned profile statistics')
        require(all(type(row['rows']) is int and row['rows'] >= 0 and
                    (row['contrast'] is None) == (row['rows'] == 0) for row in item['profile']),
                'undefined contrasts must preserve an empty-stratum denominator')
    comparisons = []
    for variant in target['variants']:
        for position in variant['profile']:
            identity = tuple(position[key] for key in ('paragraph_initial', 'boundary', 'prefix'))
            values = []
            for case in simulations:
                matches = [item for item in case['profile']
                           if tuple(item[key] for key in ('paragraph_initial', 'boundary', 'prefix')) == identity]
                require(len(matches) == 1, 'model profile is missing or duplicates a planned statistic')
                values.append(unpack(matches[0]['contrast']))
            point = unpack(position['contrast'])
            complete = point is not None and all(value is not None for value in values)
            low, high = (min(values), max(values)) if complete else (None, None)
            inside = low <= point <= high if complete else None
            gap = (max(low - point, point - high, Fraction()) if complete else None)
            comparisons.append({'source_id': variant['source_id'], 'spacing': variant['spacing'],
                                **{key: position[key] for key in ('paragraph_initial', 'boundary', 'prefix', 'rows')},
                                'target': position['contrast'], 'seed_minimum': packed(low),
                                'seed_maximum': packed(high), 'within_fixed_seed_range': inside,
                                'outside_range_gap': packed(gap), 'all_seed_contrasts_defined': complete})
    return comparisons


def load_observer(directory, protocol):
    for artifact in protocol['observer_snapshot']['artifacts']:
        path = directory / Path(artifact['path']).name
        require(digest(path.read_bytes()) == artifact['sha256'], 'pinned observer/helper bytes changed')
    namespace = '_pinned_sc_profile_' + digest(canonical(protocol['observer_snapshot']))[:16]
    package = types.ModuleType(namespace)
    package.__path__ = [str(directory)]
    sys.modules[package.__name__] = package
    spec = importlib.util.spec_from_file_location(package.__name__ + '.trace_self_citation_rows',
                                                directory / 'trace_self_citation_rows.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def process(command, cwd, environment, log):
    try:
        result = subprocess.run(command, cwd=cwd, env=environment, capture_output=True, timeout=60)
        stdout, stderr, code, timeout = result.stdout, result.stderr, result.returncode, False
    except subprocess.TimeoutExpired as error:
        stdout, stderr, code, timeout = error.stdout or b'', error.stderr or b'', None, True
    log.with_suffix('.stdout').write_bytes(stdout)
    log.with_suffix('.stderr').write_bytes(stderr)
    return {'returncode': code, 'timed_out': timeout, 'stdout_bytes': len(stdout), 'stderr_bytes': len(stderr),
            'stdout_sha256': digest(stdout), 'stderr_sha256': digest(stderr)}


def produce(reference, observer_dir, work, manifest_path):
    for protected in (reference, observer_dir):
        require(not work.resolve().is_relative_to(protected.resolve()), 'work cannot be inside an input tree')
    require(not work.exists() and not work.is_symlink(), 'work directory must be new')
    protocol_bytes = PROTOCOL.read_bytes()
    require(digest(protocol_bytes) == PROTOCOL_SHA256, 'amended frozen protocol bytes changed')
    protocol = json.loads(protocol_bytes)
    require(protocol['seeds'] == list(range(1, 32)) and protocol['prefixes'] == list(PREFIXES) and
            protocol['boundaries'] == list(BOUNDARIES) and protocol['source_ids'] == list(SOURCE_IDS) and
            protocol['spacing_policies'] == list(SPACING), 'frozen protocol constants changed')
    sources = paired_sources(load_sources())
    payloads = [build(spacing, source_ids=SOURCE_IDS, kinds=('P0',)) for spacing in SPACING]
    target = select_target(sources, payloads)
    observer = load_observer(observer_dir, protocol)
    manifest_bytes = manifest_path.read_bytes()
    require(digest(manifest_bytes) == protocol['source_manifest_sha256'], 'frozen author-source manifest changed')
    inventory = json.loads(manifest_bytes)
    require(len(inventory) == 39 and len({row['path'] for row in inventory}) == 39, 'source inventory changed')
    for row in inventory:
        relative = Path(row['path'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe source path')
        raw = (reference / relative).read_bytes()
        require(len(raw) == row['bytes'] and digest(raw) == row['sha256'] and
                hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob_sha1'],
                'pinned source/config/reference blob changed')
    config = (reference / protocol['configuration_path']).read_bytes()
    require(digest(config) == protocol['configuration_sha256'], 'executable configuration changed')
    environment = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC'}
    versions = {}
    for name in ('java', 'javac'):
        result = subprocess.run(['/usr/bin/' + name, '-version'], env=environment, capture_output=True,
                                check=True, timeout=10)
        versions[name] = (result.stdout + result.stderr).decode().strip()
        pattern = (r'openjdk version "17\.0\.16"(?:\s|$)' if name == 'java'
                   else r'javac 17\.0\.16(?:\s|$)')
        require(re.match(pattern, versions[name].splitlines()[0]) is not None,
                'planned Java runtime/compiler changed')
    require('Zulu17.60+17-CA' in versions['java'], 'planned Java vendor/build changed')
    work.mkdir(parents=True, exist_ok=False)
    (work / 'empty-classpath').mkdir()
    java_paths = sorted(Path(row['path']) for row in inventory if row['path'].endswith('.java'))
    require(len(java_paths) == 35, 'Java source count changed')
    builds, class_dirs, class_inventories = {}, {}, {}
    for mode in ('control', 'observed'):
        source_root = work / mode / 'sources'
        shutil.copytree(reference / 'source/src/main/java', source_root)
        main = source_root / 'de/voynich/text/SelfCitationTextGenerator.java'
        if mode == 'observed':
            main.write_bytes(observer.instrument(main.read_bytes()))
        for relative in java_paths:
            original = (reference / relative).read_bytes()
            expected = observer.instrument(original) if mode == 'observed' and str(relative) == observer.MAIN else original
            require((source_root / relative.relative_to('source/src/main/java')).read_bytes() == expected,
                    'source copy differs outside the declared observer insertion')
        classes = work / mode / 'classes'
        classes.mkdir()
        flags = ['-J-Xmx256m', '--release', '8', '-encoding', 'UTF-8', '-proc:none', '--class-path',
                 str(work / 'empty-classpath'), '-d', str(classes)]
        builds[mode] = process(['/usr/bin/javac', *flags,
                               *[str(source_root / path.relative_to('source/src/main/java')) for path in java_paths]],
                              work, environment, work / (mode + '-build'))
        class_dirs[mode] = classes
        class_inventories[mode] = [{'path': path.relative_to(classes).as_posix(), 'sha256': digest(path.read_bytes())}
                                  for path in sorted(classes.rglob('*.class'))]
    total = len(target['selected_keys']) + 1
    cases = []
    for seed in protocol['seeds']:
        effective = observer.configuration(config, {'text.lines_to_create': str(total),
                                                    'method.random.pseudo.seed': str(seed),
                                                    'save.path': './output/', 'save.filename': 'generated.txt'})
        processes, outputs, contexts, ledger, error = {}, {}, None, None, None
        for mode in ('control', 'observed'):
            directory = work / f'seed-{seed:02d}' / mode
            directory.mkdir(parents=True)
            (directory / 'output').mkdir()
            (directory / 'conf.properties').write_bytes(effective)
            processes[mode] = (process(['/usr/bin/java', '-Xmx256m', '-Dfile.encoding=UTF-8',
                                        '-Duser.language=en', '-Duser.country=US', '-Duser.timezone=UTC',
                                        '-cp', str(class_dirs[mode]), 'de.voynich.text.SelfCitationTextGenerator'],
                                       directory, environment, directory / 'process')
                               if builds[mode]['returncode'] == 0 else
                               {'returncode': None, 'timed_out': False, 'not_run': 'build failed'})
            path = directory / 'output/generated.txt'
            outputs[mode] = path.read_bytes() if path.exists() else None
        try:
            require(all(p['returncode'] == 0 and not p['timed_out'] for p in processes.values()),
                    'process did not complete successfully')
            require(outputs['control'] is not None and outputs['control'] == outputs['observed'],
                    'observed output differs from complete control bytes')
            events, other = observer.trace_events((work / f'seed-{seed:02d}/observed/process.stderr').read_bytes(), 1, total)
            ledger = observer.row_ledger(outputs['observed'], events, 1, total)
            measured, excluded = [], []
            for item in ledger:
                if item['initialized_input_row']:
                    continue
                if item['space_delimited_token_count'] < 2:
                    excluded.append(item)
                    continue
                row = outputs['observed'][item['start_byte']:item['end_byte_exclusive_without_line_ending']]
                groups = row.decode('ascii').split(' ')
                measured.append((item['generated_row_index'], groups, item['model_paragraph_initial']))
            contexts = profile(measured)
            (work / f'seed-{seed:02d}/observed/ledger.json').write_bytes(observer.canonical(ledger))
        except (ValueError, UnicodeError) as problem:
            error = str(problem)
            excluded, other = None, None
        case = {'seed': seed, 'accepted': error is None, 'error': error, 'processes': processes,
                'effective_configuration_sha256': digest(effective), 'total_output_rows': total,
                'output_sha256': {mode: digest(raw) if raw is not None else None for mode, raw in outputs.items()},
                'complete_control_observed_bytes_equal': outputs['control'] is not None and outputs['control'] == outputs['observed'],
                'profile': contexts, 'excluded_short_rows': excluded, 'non_event_stderr_lines': other,
                'row_ledger_sha256': digest(observer.canonical(ledger)) if ledger is not None else None}
        cases.append(case)
        (work / 'case-receipts.json').write_bytes(canonical(cases))
        print(f'Seed {seed}: accepted={case["accepted"]}', flush=True)
    complete = all(case['accepted'] for case in cases)
    comparisons = finite_ranges(target, cases, protocol['seeds']) if complete else None
    dependencies = ['scripts/audit_transliterations.py', 'scripts/ivtff.py', 'scripts/token_baselines.py',
                    'scripts/eva_token_adapter.py', 'scripts/conservative_prefixes.py', 'scripts/prefix_strata.py']
    return {'schema_version': 1, 'method': 'fixed self-citation prefix profile diagnostic v1',
            'protocol_sha256': digest(protocol_bytes), 'plan_commit': PLAN_COMMIT,
            'pre_measurement_amendment_commit': AMENDMENT_COMMIT,
            'producer_sha256': digest(Path(__file__).read_bytes()), 'helper_fingerprints':
                [{'path': path, 'sha256': digest((ROOT / path).read_bytes())} for path in dependencies],
            'source_commit': protocol['source_commit'], 'source_inventory': inventory,
            'source_manifest_sha256': digest(manifest_path.read_bytes()),
            'observer_snapshot': protocol['observer_snapshot'], 'runtime': versions,
            'minimal_environment': environment, 'builds': builds, 'class_inventories': class_inventories,
            'target': target, 'cases': cases, 'planned_execution_complete': complete,
            'comparison_reporting_complete': complete, 'comparisons': comparisons,
            'all_comparison_ranges_defined': (all(item['all_seed_contrasts_defined'] for item in comparisons)
                                               if comparisons else False),
            'all_target_points_within_finite_seed_ranges':
                (all(item['within_fixed_seed_range'] for item in comparisons)
                 if comparisons and all(item['within_fixed_seed_range'] is not None for item in comparisons) else None),
            'scope': protocol['evaluation_claim'], 'mechanism_or_translation_validated': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('reference', 'observer-dir', 'work', 'source-manifest', 'new-report'):
        parser.add_argument('--' + option, type=Path, required=True)
    args = parser.parse_args()
    try:
        require(not args.new_report.exists() and not args.new_report.is_symlink(), 'report path must be new')
        require(all(not args.new_report.resolve().is_relative_to(path.resolve())
                    for path in (args.reference, args.observer_dir)), 'report cannot be inside an input tree')
        report = produce(args.reference.resolve(), args.observer_dir.resolve(), args.work.resolve(), args.source_manifest)
        with args.new_report.open('xb') as destination:
            destination.write((json.dumps(report, indent=2) + '\n').encode())
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Fixed profile diagnostic failed: {error}\n')
    print('Complete planned execution/reporting:', report['planned_execution_complete'])
    return not report['planned_execution_complete']


if __name__ == '__main__':
    raise SystemExit(main())
