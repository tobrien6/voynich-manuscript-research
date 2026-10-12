#!/usr/bin/env python3
"""Run the fixed source-build repeatability cases without downloading anything."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REVISION = '9e98c9122a0f490905e8b66f3911fc7ce095fd26'
CONFIG_HASH = '00944114753a7019e920199ed2d076065e30aed5e8402057b710d78ad0e1e800'
SUPPLIED_HASH = 'a9f8237c9d7428ed148718d5aef2563a220b0df3fbc137eea197751af8ce2956'
CASES = [('short-19', 60, 19), ('short-20', 60, 20), ('release-19', 1200, 19)]
REMOVED_ENV = ['JAVA_TOOL_OPTIONS', '_JAVA_OPTIONS', 'JDK_JAVA_OPTIONS', 'CLASSPATH',
               'GH_TOKEN', 'GITHUB_TOKEN']


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def properties(raw):
    """Read only the simple ASCII key=value subset present in this pinned file."""
    result = {}
    for line in raw.decode('ascii').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(('#', '!')):
            continue
        if '\\' in line or '=' not in line:
            raise ValueError('unsupported property escape/continuation or declaration')
        key, value = line.split('=', 1)
        key, value = key.strip(), value.strip()
        if not re.fullmatch(r'[A-Za-z0-9_.]+', key) or key in result:
            raise ValueError('invalid or duplicate property key')
        result[key] = value
    return result


def configuration(raw, overrides):
    original = properties(raw)
    if set(overrides) - set(original):
        raise ValueError('override names a missing property')
    lines = []
    for line in raw.decode('ascii').splitlines():
        key = line.split('=', 1)[0].strip()
        lines.append(f'{key}={overrides[key]}' if key in overrides else line)
    rendered = ('\n'.join(lines) + '\n').encode('ascii')
    if properties(rendered) != {**original, **overrides}:
        raise ValueError('configuration changed properties beyond the declared overrides')
    return rendered


def text_projection(raw):
    rows = [line for line in raw.decode('utf-8').splitlines()
            if line.strip() and not line.lstrip().startswith('#')]
    projected = ('\n'.join(rows) + '\n').encode('utf-8') if rows else b''
    return projected, {'bytes': len(raw), 'sha256': digest(raw), 'text_rows': len(rows),
                       'projected_sha256': digest(projected),
                       'first_row_sha256': digest(rows[0].encode('utf-8')) if rows else None}


def source_inventory(reference):
    def git(*args):
        return subprocess.run(['git', '--no-replace-objects', '-C', str(reference), *args],
                              capture_output=True, check=True).stdout

    if git('rev-parse', 'HEAD').decode().strip() != REVISION:
        raise ValueError('reference checkout differs from the pinned release commit')
    if git('status', '--porcelain', '--untracked-files=all'):
        raise ValueError('reference checkout must be unchanged and free of untracked files')
    paths = git('ls-tree', '-r', '--name-only', REVISION, 'source/src/main/java').decode().splitlines()
    paths = sorted(path for path in paths if path.endswith('.java'))
    if len(paths) != 35:
        raise ValueError('pinned source inventory changed')
    records = []
    for path in paths + ['executable/conf.properties', 'executable/generate/vms_generated.txt']:
        working = (reference / path).read_bytes()
        if working != git('show', f'{REVISION}:{path}'):
            raise ValueError(f'{path}: working bytes differ from the release blob')
        records.append({'path': path, 'bytes': len(working), 'sha256': digest(working)})
    config = (reference / 'executable/conf.properties').read_bytes()
    supplied = (reference / 'executable/generate/vms_generated.txt').read_bytes()
    if digest(config) != CONFIG_HASH or digest(supplied) != SUPPLIED_HASH or len(supplied) != 62795:
        raise ValueError('configuration or supplied-output pin changed')
    settings = properties(config)
    if (settings['method.random'] != 'pseudo' or settings['save.gephi.nodes'] != 'false' or
            settings['save.properties_in_seperate_file'] != 'false'):
        raise ValueError('fixed random/output policies changed')
    return paths, records, config, supplied


def run_process(command, cwd, environment, log_prefix):
    try:
        result = subprocess.run(command, cwd=cwd, env=environment, capture_output=True, timeout=120)
        stdout, stderr, code, timed_out = result.stdout, result.stderr, result.returncode, False
    except subprocess.TimeoutExpired as error:
        stdout, stderr, code, timed_out = error.stdout or b'', error.stderr or b'', None, True
    log_prefix.with_suffix('.stdout.txt').write_bytes(stdout)
    log_prefix.with_suffix('.stderr.txt').write_bytes(stderr)
    return {'exit_code': code, 'timed_out': timed_out, 'stdout_bytes': len(stdout),
            'stdout_sha256': digest(stdout), 'stderr_bytes': len(stderr), 'stderr_sha256': digest(stderr)}


def replay(reference, java_home, work):
    paths, inventory, base_config, supplied = source_inventory(reference)
    work.mkdir(parents=True, exist_ok=False)
    classes, empty_classpath = work / 'classes', work / 'empty-classpath'
    classes.mkdir()
    empty_classpath.mkdir()
    environment = {key: value for key, value in os.environ.items() if key not in REMOVED_ENV}
    environment.update({'TZ': 'UTC', 'LANG': 'en_US.UTF-8', 'LC_ALL': 'en_US.UTF-8'})
    java, javac = java_home / 'bin/java', java_home / 'bin/javac'
    versions = {}
    for name, executable in [('java', java), ('javac', javac)]:
        result = subprocess.run([str(executable), '-version'], capture_output=True, env=environment,
                                check=True, timeout=15)
        version = (result.stdout + result.stderr).decode('utf-8').strip()
        if '22.0.2' not in version:
            raise ValueError('this recorded plan targets Java 22.0.2; use a new plan for another runtime')
        versions[name] = {'version_output': version, 'executable_sha256': digest(executable.read_bytes())}
    build_flags = ['--release', '8', '-encoding', 'UTF-8', '-proc:none']
    build = run_process([str(javac), *build_flags, '--class-path', str(empty_classpath),
                         '-d', str(classes), *[str(reference / path) for path in paths]],
                        work, environment, work / 'build')
    class_records = [{'path': str(path.relative_to(classes)), 'bytes': path.stat().st_size,
                      'sha256': digest(path.read_bytes())} for path in sorted(classes.rglob('*.class'))]
    class_digest = digest(('\n'.join(f'{row["path"]}\t{row["sha256"]}' for row in class_records) + '\n').encode())
    jvm_flags = ['-Dfile.encoding=UTF-8', '-Duser.timezone=UTC', '-Duser.language=en', '-Duser.country=US']
    supplied_projection, supplied_record = text_projection(supplied)
    cases, all_successful = [], build['exit_code'] == 0 and not build['timed_out']
    projected_by_case = {}
    for name, line_count, seed in CASES:
        overrides = {'save.path': './output/', 'save.filename': 'generated.txt'}
        if name.startswith('short-'):
            overrides.update({'text.lines_to_create': str(line_count), 'method.random.pseudo.seed': str(seed)})
        config = configuration(base_config, overrides)
        settings = properties(config)
        initial_hash = digest(settings.pop('text.initial_line').encode('ascii'))
        runs, raw_outputs, projections = [], [], []
        for repeat in [1, 2]:
            directory = work / name / f'run-{repeat}'
            directory.mkdir(parents=True)
            (directory / 'output').mkdir()
            (directory / 'conf.properties').write_bytes(config)
            result = (run_process([str(java), *jvm_flags, '-cp', str(classes),
                                   'de.voynich.text.SelfCitationTextGenerator'], directory,
                                  environment, directory / 'process') if build['exit_code'] == 0 else
                      {'exit_code': None, 'timed_out': False, 'not_run': 'source build failed'})
            output = directory / 'output/generated.txt'
            raw = output.read_bytes() if output.exists() else None
            projection, metrics = text_projection(raw) if raw is not None else (None, None)
            successful = (result['exit_code'] == 0 and not result['timed_out'] and
                          metrics is not None and metrics['text_rows'] == line_count)
            all_successful = all_successful and successful
            runs.append({'repeat': repeat, 'process': result, 'output': metrics,
                         'completed_expected_rows': successful,
                         'matches_supplied_full_bytes': raw == supplied if raw is not None else None,
                         'matches_supplied_projected_bytes': projection == supplied_projection if projection is not None else None})
            raw_outputs.append(raw)
            projections.append(projection)
            print(f'{name} repeat {repeat}: completed_expected_rows={successful}', flush=True)
        same_raw = all(raw is not None for raw in raw_outputs) and raw_outputs[0] == raw_outputs[1]
        same_text = all(raw is not None for raw in projections) and projections[0] == projections[1]
        all_successful = all_successful and same_text
        projected_by_case[name] = projections[0]
        cases.append({'case': name, 'requested_rows_including_initialization': line_count, 'seed': seed,
                      'declared_overrides': overrides, 'effective_configuration_sha256': digest(config),
                      'effective_properties_excluding_initial_text': settings,
                      'initialization_text_sha256': initial_hash, 'runs': runs,
                      'repeats_full_bytes_equal': same_raw, 'repeats_projected_bytes_equal': same_text})
    short19, short20 = projected_by_case['short-19'], projected_by_case['short-20']
    return {'schema_version': 1, 'method': 'pinned self-citation source-build repeatability v1',
            'plan_sha256': digest((ROOT / 'research/literature/SELF_CITATION_REPLAY_PLAN.md').read_bytes()),
            'runner_sha256': digest(Path(__file__).read_bytes()), 'source_commit': REVISION,
            'source_inventory': inventory, 'build': build, 'build_flags': build_flags,
            'class_inventory': class_records, 'sorted_class_inventory_sha256': class_digest,
            'runtime': versions, 'platform': {'system': platform.system(), 'release': platform.release(),
                                            'machine': platform.machine()},
            'jvm_flags': jvm_flags, 'subprocess_locale': {'TZ': 'UTC', 'LANG': 'en_US.UTF-8', 'LC_ALL': 'en_US.UTF-8'},
            'suppressed_environment_names': REMOVED_ENV,
            'supplied_output': supplied_record, 'cases': cases,
            'short_seed_change_changes_projected_bytes': short19 != short20 if short19 is not None and short20 is not None else None,
            'all_runs_complete_and_within_case_text_repeatable': all_successful,
            'scope': 'software replay; initialized manuscript text is input; no manuscript mechanism test or translation'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True, help='unchanged local pinned release checkout')
    parser.add_argument('--java-home', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True, help='new directory retaining builds/configurations/logs/output')
    parser.add_argument('--output', type=Path, required=True, help='new JSON record, containing no generated text')
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('output record exists; choose a new run record')
        result = replay(args.reference.resolve(), args.java_home.resolve(), args.work.resolve())
        with args.output.open('x', encoding='utf-8') as output:
            output.write(json.dumps(result, indent=2) + '\n')
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Replay failed: {error}\n')
    print(f'Artifacts retained in {args.work}; record saved to {args.output}.')
    return not result['all_runs_complete_and_within_case_text_repeatable']


if __name__ == '__main__':
    raise SystemExit(main())
