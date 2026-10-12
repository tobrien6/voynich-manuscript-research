"""Frozen finite-grid paragraph-argument ablation; no manuscript fit test."""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

try:
    from . import self_citation_prefix_profile as shared
except ImportError:
    import self_citation_prefix_profile as shared


ROOT = shared.ROOT
PLAN_COMMIT = 'f0ad3f1919a9e49eb7181fbfbed9a02c2d1aeac1'
PROTOCOL = ROOT / 'research/literature/self-citation-context-protocol.json'
PROTOCOL_SHA256 = 'f9d475ec26dfd3a6d40fd4991ca384cf2fba04ebd843536c129e7b77f6379dd0'
RUNTIME_EXECUTABLE_SHA256 = {
    'java': 'f671624e7f4fdc15a5913be61b36b5410f58ffc18d9ccda082b7e0ff58591596',
    'javac': 'ad9bfde64121361606c4051e208638c4a979b1eaaa875c2df1ef3585a702788d',
}
SETTINGS = [('original', False, False), ('chooser_off', True, False),
            ('morpher_off', False, True), ('both_off', True, True)]
CHOOSER = (b'config.sourceGroupChooser.chooseSourceGroup(lineArrays, paragraphInitialLineArrays, '
           b'glyphGroupList, config.statistics, isParagraphInitial, isLineInitial, initialLineCount)')
MORPHER = (b'config.groupMorpher.morphGroup(sourceGroups, lastGeneratedGroup, '
           b'isParagraphInitial, isLineInitial)')
IDS = ('paragraph_initial', 'boundary', 'prefix')
require, digest, canonical = shared.require, shared.digest, shared.canonical
packed, unpack = shared.packed, shared.unpack


def ablate_source(raw, suppress_chooser, suppress_morpher):
    require(type(suppress_chooser) is bool and type(suppress_morpher) is bool,
            'suppression flags must be explicit booleans')
    for anchor, suppress in ((CHOOSER, suppress_chooser), (MORPHER, suppress_morpher)):
        require(raw.count(anchor) == 1, 'require one exact anchor for each component call')
        if suppress:
            replacement = anchor.replace(b'isParagraphInitial', b'false')
            require(replacement != anchor, 'component anchor has no paragraph argument')
            raw = raw.replace(anchor, replacement)
    return raw


def measured_profile(raw, ledger):
    measured, short = [], []
    for row in ledger:
        if row['initialized_input_row']:
            continue
        if row['space_delimited_token_count'] < 2:
            short.append(row)
            continue
        body = raw[row['start_byte']:row['end_byte_exclusive_without_line_ending']]
        require(digest(body) == row['row_sha256'], 'row bytes differ from their native ledger')
        groups = body.decode('ascii').split(' ')
        require(len(groups) == row['space_delimited_token_count'], 'ledger group count changed')
        measured.append((row['generated_row_index'], groups, row['model_paragraph_initial']))
    return shared.profile(measured), short


def summarize(values):
    defined = all(value is not None for value in values)
    return {'defined_seed_count': sum(value is not None for value in values),
            'all_seeds_defined': defined,
            'summary': {'mean': packed(sum(values, Fraction()) / len(values)),
                        'minimum': packed(min(values)), 'maximum': packed(max(values)),
                        'negative': sum(value < 0 for value in values),
                        'zero': sum(value == 0 for value in values),
                        'positive': sum(value > 0 for value in values)} if defined else None,
            'seed_values': [packed(value) for value in values]}


def factorial_grid(cases, seeds):
    require(seeds and len(set(seeds)) == len(seeds) and
            all(type(seed) is int and seed > 0 for seed in seeds), 'invalid seed bank')
    require([(case['seed'], case['setting']) for case in cases] ==
            [(seed, setting) for seed in seeds for setting, _, _ in SETTINGS],
            'missing, duplicate or unordered setting/seed cell')
    require(all(case['accepted'] is True for case in cases), 'failed cell blocks the complete grid')
    lookup = {}
    for case in cases:
        rows = case['profile']
        require(len(rows) == 8 and {tuple(row[key] for key in IDS) for row in rows} ==
                shared.PROFILE_IDENTITIES, 'require all eight distinct profiles per cell')
        for row in rows:
            require(type(row['paragraph_initial']) is bool and type(row['rows']) is int and
                    row['rows'] >= 0 and type(row['group_occurrences']) is int and
                    (row['group_occurrences'] >= 2 * row['rows'] if row['rows'] else
                     row['group_occurrences'] == 0) and
                    (row['contrast'] is None) == (row['rows'] == 0), 'invalid profile denominator')
            if row['contrast'] is not None:
                value = row['contrast']
                require(type(value['numerator']) is int and type(value['denominator']) is int and
                        value['denominator'] > 0 and -1 <= unpack(value) <= 1,
                        'invalid exact binary contrast')
            lookup[(case['seed'], case['setting'], tuple(row[key] for key in IDS))] = unpack(row['contrast'])
        for initial in (False, True):
            require(len({(row['rows'], row['group_occurrences']) for row in rows
                         if row['paragraph_initial'] == initial}) == 1, 'context denominators disagree')
    profiles, deltas, interactions = [], [], []
    for identity in sorted(shared.PROFILE_IDENTITIES):
        fields = dict(zip(IDS, identity))
        by_setting = {setting: [lookup[(seed, setting, identity)] for seed in seeds]
                      for setting, _, _ in SETTINGS}
        for setting, _, _ in SETTINGS:
            profiles.append({'setting': setting, **fields, **summarize(by_setting[setting])})
        for setting, _, _ in SETTINGS[1:]:
            values = [value - original if value is not None and original is not None else None
                      for value, original in zip(by_setting[setting], by_setting['original'], strict=True)]
            deltas.append({'setting_minus_original': setting, **fields, **summarize(values)})
        values = [both - chooser - morpher + original if all(value is not None for value in
                  (both, chooser, morpher, original)) else None for both, chooser, morpher, original in
                  zip(by_setting['both_off'], by_setting['chooser_off'], by_setting['morpher_off'],
                      by_setting['original'], strict=True)]
        interactions.append({**fields, **summarize(values)})
    identity = (True, 'first', 'y')
    predicted = []
    for changed, control in [('morpher_off', 'original'), ('both_off', 'chooser_off')]:
        values = [lookup[(seed, changed, identity)] - lookup[(seed, control, identity)]
                  if lookup[(seed, changed, identity)] is not None and
                  lookup[(seed, control, identity)] is not None else None for seed in seeds]
        predicted.append({'changed': changed, 'control': control, **summarize(values)})
    criterion = (all(unpack(item['summary']['mean']) > 0 for item in predicted)
                 if all(item['all_seeds_defined'] for item in predicted) else None)
    return {'seeds': list(seeds), 'profiles': profiles, 'original_relative_differences': deltas,
            'two_factor_interactions': interactions, 'prediction_differences': predicted,
            'directional_prediction_satisfied': criterion,
            'all_profile_and_difference_strata_defined': all(item['all_seeds_defined'] for item in
                                                             profiles + deltas + interactions)}


def check_pair(runs, outputs, profiles, short_rows, parent=None):
    require(len(runs) == len(outputs) == len(profiles) == len(short_rows) == 2,
            'require exactly two retained runs')
    require(all(run['accepted_trace'] is True for run in runs), 'repeat process/trace did not pass')
    require(outputs[0] is not None and outputs[0] == outputs[1], 'complete repeat output bytes differ')
    for field in ('canonical_events_sha256', 'canonical_ledger_sha256'):
        require(runs[0][field] == runs[1][field], 'repeat event/ledger identities differ')
    require(profiles[0] == profiles[1] and short_rows[0] == short_rows[1], 'repeat measurements differ')
    if parent is not None:
        require(digest(outputs[0]) == parent['output_sha256']['observed'] and
                runs[0]['canonical_ledger_sha256'] == parent['row_ledger_sha256'] and
                profiles[0] == parent['profile'] and short_rows[0] == parent['excluded_short_rows'],
                'original cell differs from the accepted parent receipt')


def verify_inputs(reference, inventory):
    require(len(inventory) == len({row['path'] for row in inventory}) == 39, 'source inventory changed')
    for row in inventory:
        relative = Path(row['path'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe source path')
        path = reference / relative
        require(path.is_file() and not path.is_symlink(), 'source must be a regular pinned file')
        raw = path.read_bytes()
        require(len(raw) == row['bytes'] and digest(raw) == row['sha256'] and
                hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob_sha1'],
                'author-source/config/reference identity changed')
    java_paths = sorted(Path(row['path']) for row in inventory if row['path'].endswith('.java'))
    require(len(java_paths) == 35 and
            set(path.relative_to(reference) for path in (reference / 'source/src/main/java').rglob('*.java')) ==
            set(java_paths), 'Java source tree has missing or extra inputs')
    return java_paths


def produce(reference, observer_dir, java_home, work):
    require(not work.exists() and not work.is_symlink(), 'work directory must be new')
    require(all(not work.resolve().is_relative_to(path.resolve()) for path in
                (ROOT, reference, observer_dir, java_home)), 'work must be outside protected input trees')
    protocol_bytes = PROTOCOL.read_bytes()
    require(digest(protocol_bytes) == PROTOCOL_SHA256, 'frozen ablation protocol changed')
    protocol = json.loads(protocol_bytes)
    require(protocol['settings'] == [{'id': name, 'suppress_chooser': chooser, 'suppress_morpher': morpher}
                                     for name, chooser, morpher in SETTINGS] and
            protocol['seeds'] == list(range(1, 32)) and protocol['repeats'] == 2 and
            protocol['total_rows_including_initialization'] == 1684 and protocol['initialized_rows'] == 1,
            'frozen factorial execution grid changed')
    for row in [*protocol['helper_fingerprints'], {'path': protocol['plan_path'], 'sha256': protocol['plan_sha256']}]:
        require(digest((ROOT / row['path']).read_bytes()) == row['sha256'], 'frozen helper or plan changed')
    parent_bytes = (ROOT / protocol['parent_report_path']).read_bytes()
    require(digest(parent_bytes) == protocol['parent_report_sha256'], 'accepted parent report changed')
    parent = json.loads(parent_bytes)
    inventory = parent['source_inventory']
    require(digest((json.dumps(inventory, indent=2) + '\n').encode()) == protocol['source_manifest_sha256'],
            'parent source manifest differs from protocol')
    java_paths = verify_inputs(reference, inventory)
    observer = shared.load_observer(observer_dir, protocol)
    require(digest(shared.PROTOCOL.read_bytes()) == shared.PROTOCOL_SHA256, 'parent protocol changed')
    parent_protocol = json.loads(shared.PROTOCOL.read_bytes())
    base_config = (reference / parent_protocol['configuration_path']).read_bytes()
    require(digest(base_config) == parent_protocol['configuration_sha256'], 'release configuration changed')
    environment = protocol['minimal_environment']
    require(environment == {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC'},
            'minimal environment changed')
    versions = {}
    for name in ('java', 'javac'):
        require(digest((Path('/usr/bin') / name).read_bytes()) == protocol['runtime_launcher_sha256'][name],
                'runtime launcher changed')
        executable = java_home / 'bin' / name
        require(digest(executable.read_bytes()) == RUNTIME_EXECUTABLE_SHA256[name], 'actual runtime executable changed')
        result = subprocess.run([str(executable), '-version'], env=environment, capture_output=True,
                                check=True, timeout=10)
        versions[name] = (result.stdout + result.stderr).decode().strip()
        require(versions[name] == protocol['runtime'][name], 'runtime/compiler build changed')
    require([case['seed'] for case in parent['cases']] == protocol['seeds'] and
            all(case['accepted'] is True and case['total_output_rows'] == 1684 for case in parent['cases']),
            'accepted parent bank changed')
    work.mkdir(parents=True, exist_ok=False)
    empty = work / 'empty-classpath'
    empty.mkdir()
    original = (reference / observer.MAIN).read_bytes()
    builds, class_dirs, class_inventories = {}, {}, {}
    for name, chooser, morpher in [('unobserved', False, False), *SETTINGS]:
        sources = work / name / 'sources'
        shutil.copytree(reference / 'source/src/main/java', sources)
        transformed = original if name == 'unobserved' else observer.instrument(ablate_source(original, chooser, morpher))
        (sources / Path(observer.MAIN).relative_to('source/src/main/java')).write_bytes(transformed)
        for path in java_paths:
            expected = transformed if path.as_posix() == observer.MAIN else (reference / path).read_bytes()
            require((sources / path.relative_to('source/src/main/java')).read_bytes() == expected,
                    'source differs outside the declared observer and call-site substitutions')
        classes = work / name / 'classes'
        classes.mkdir()
        command = [str(java_home / 'bin/javac'), '-J-Xmx256m', '--release', '8', '-encoding', 'UTF-8', '-proc:none',
                   '--class-path', str(empty), '-d', str(classes),
                   *[str(sources / path.relative_to('source/src/main/java')) for path in java_paths]]
        build = shared.process(command, work, environment, work / (name + '-build'))
        records = [{'path': path.relative_to(classes).as_posix(), 'sha256': digest(path.read_bytes())}
                   for path in sorted(classes.rglob('*.class'))]
        control_classes = {row['path']: row['sha256'] for row in class_inventories.get('unobserved', records)}
        changed = [row['path'] for row in records if row['sha256'] != control_classes.get(row['path'])]
        class_ok = (len(records) == 47 and {row['path'] for row in records} == set(control_classes) and
                    changed == ([] if name == 'unobserved' else ['de/voynich/text/SelfCitationTextGenerator.class']))
        parent_classes_match = (records == parent['class_inventories'][
                                'control' if name == 'unobserved' else 'observed']
                                if name in ('unobserved', 'original') else None)
        class_ok = class_ok and parent_classes_match is not False
        build.update({'main_source_sha256': digest(transformed), 'changed_classes': changed,
                      'accepted': build['returncode'] == 0 and not build['timed_out'] and class_ok,
                      'class_inventory_accepted': class_ok, 'accepted_parent_class_inventory_matches': parent_classes_match})
        builds[name], class_dirs[name], class_inventories[name] = build, classes, records
    total, cases = protocol['total_rows_including_initialization'], []
    for seed, parent_case in zip(protocol['seeds'], parent['cases'], strict=True):
        effective = observer.configuration(base_config, {'text.lines_to_create': str(total),
                                          'method.random.pseudo.seed': str(seed),
                                          'save.path': './output/', 'save.filename': 'generated.txt'})
        require(digest(effective) == parent_case['effective_configuration_sha256'], 'effective configuration differs from parent')
        for name, chooser, morpher in SETTINGS:
            runs, outputs, profiles, excluded = [], [], [], []
            for repeat in (1, 2):
                directory = work / f'seed-{seed:02d}' / name / f'repeat-{repeat}'
                directory.mkdir(parents=True)
                (directory / 'output').mkdir()
                (directory / 'conf.properties').write_bytes(effective)
                command = [str(java_home / 'bin/java'), '-Xmx256m', '-Dfile.encoding=UTF-8', '-Duser.language=en',
                           '-Duser.country=US', '-Duser.timezone=UTC', '-cp', str(class_dirs[name]),
                           'de.voynich.text.SelfCitationTextGenerator']
                run = (shared.process(command, directory, environment, directory / 'process')
                       if builds['unobserved']['accepted'] and builds[name]['accepted'] else
                       {'returncode': None, 'timed_out': False, 'not_run': 'build validation failed'})
                output_path = directory / 'output/generated.txt'
                raw = output_path.read_bytes() if output_path.exists() else None
                events = ledger = values = short = None
                other, error = None, None
                try:
                    require(run['returncode'] == 0 and not run['timed_out'] and raw is not None, 'process did not complete')
                    events, other = observer.trace_events((directory / 'process.stderr').read_bytes(), 1, total)
                    ledger = observer.row_ledger(raw, events, 1, total)
                    values, short = measured_profile(raw, ledger)
                    (directory / 'ledger.json').write_bytes(observer.canonical(ledger))
                except (ValueError, UnicodeError) as problem:
                    error = str(problem)
                run.update({'repeat': repeat, 'accepted_trace': error is None, 'validation_error': error,
                            'output_bytes': len(raw) if raw is not None else None,
                            'output_sha256': digest(raw) if raw is not None else None,
                            'canonical_events_sha256': digest(observer.canonical(events)) if events is not None else None,
                            'canonical_ledger_sha256': digest(observer.canonical(ledger)) if ledger is not None else None,
                            'profile_sha256': digest(canonical(values)) if values is not None else None,
                            'non_event_stderr_lines': other})
                runs.append(run); outputs.append(raw); profiles.append(values); excluded.append(short)
            error = None
            try:
                check_pair(runs, outputs, profiles, excluded, parent_case if name == 'original' else None)
            except ValueError as problem:
                error = str(problem)
            case = {'seed': seed, 'setting': name, 'suppress_chooser': chooser, 'suppress_morpher': morpher,
                    'effective_configuration_sha256': digest(effective), 'total_output_rows': total,
                    'runs': runs, 'accepted': error is None, 'error': error,
                    'profile': profiles[0] if error is None else None,
                    'excluded_short_rows': excluded[0] if error is None else None}
            cases.append(case)
            (work / 'case-receipts.json').write_bytes(canonical(cases))
            print(f'Seed {seed} {name}: accepted={case["accepted"]}', flush=True)
    try:
        verify_inputs(reference, inventory)
        unchanged = True
    except ValueError:
        unchanged = False
    complete = all(build['accepted'] for build in builds.values()) and all(case['accepted'] for case in cases) and unchanged
    grid = factorial_grid(cases, protocol['seeds']) if complete else None
    return {'schema_version': 1, 'method': protocol['method'], 'plan_commit': PLAN_COMMIT,
            'protocol_sha256': digest(protocol_bytes), 'producer_sha256': digest(Path(__file__).read_bytes()),
            'parent_report_sha256': digest(parent_bytes), 'source_commit': protocol['source_commit'],
            'source_inventory': inventory, 'source_manifest_sha256': protocol['source_manifest_sha256'],
            'observer_snapshot': protocol['observer_snapshot'], 'helper_fingerprints': protocol['helper_fingerprints'],
            'runtime': versions, 'runtime_launcher_sha256': protocol['runtime_launcher_sha256'],
            'runtime_executable_sha256': RUNTIME_EXECUTABLE_SHA256,
            'minimal_environment': environment, 'builds': builds, 'class_inventories': class_inventories,
            'cases': cases, 'source_inputs_unchanged_after_runs': unchanged,
            'planned_execution_complete': complete, 'grid': grid,
            'directional_prediction_satisfied': grid['directional_prediction_satisfied'] if grid else None,
            'scope': protocol['evaluation_claim'], 'mechanism_or_translation_validated': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('reference', 'observer-dir', 'java-home', 'work', 'new-report'):
        parser.add_argument('--' + option, type=Path, required=True)
    args = parser.parse_args()
    try:
        require(not args.new_report.exists() and not args.new_report.is_symlink(), 'report path must be new')
        require(all(not args.new_report.resolve().is_relative_to(path.resolve()) for path in
                    (ROOT, args.reference, args.observer_dir, args.java_home)), 'report must be outside protected input trees')
        report = produce(args.reference.resolve(), args.observer_dir.resolve(), args.java_home.resolve(), args.work.resolve())
        with args.new_report.open('xb') as stream:
            stream.write((json.dumps(report, indent=2) + '\n').encode())
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Context ablation failed: {error}\n')
    print('Complete planned execution:', report['planned_execution_complete'])
    return not report['planned_execution_complete']


if __name__ == '__main__':
    raise SystemExit(main())
