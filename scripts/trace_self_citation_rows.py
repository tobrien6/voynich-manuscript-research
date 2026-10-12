#!/usr/bin/env python3
"""Observe generation-call flags only when instrumented output preserves the control bytes."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

try:
    from .replay_self_citation import (ROOT, REVISION, SUPPLIED_HASH, REMOVED_ENV, configuration,
                                     digest, process_environment, run_process, source_inventory)
except ImportError:
    from replay_self_citation import (ROOT, REVISION, SUPPLIED_HASH, REMOVED_ENV, configuration,
                                    digest, process_environment, run_process, source_inventory)


MAIN = 'source/src/main/java/de/voynich/text/SelfCitationTextGenerator.java'
ANCHOR = b'            generatedText.add(generateLine(isParagraphInitial, isParagraphFinal, initialLineCount));'
OBSERVER = (b'            System.err.println("VMS_ROW_TRACE_V1\\t" + i + "\\t" + isParagraphInitial'
            b' + "\\t" + isParagraphFinal + "\\t" + config.statistics.linesInPage'
            b' + "\\t" + config.statistics.linesInParagraph);\n')
BASE = ROOT / 'research/literature/self-citation-repeatability.json'


def control_contract(baseline):
    expected = {'build_flags': ['--release', '8', '-encoding', 'UTF-8', '-proc:none'],
                'jvm_flags': ['-Dfile.encoding=UTF-8', '-Duser.timezone=UTC', '-Duser.language=en', '-Duser.country=US'],
                'subprocess_locale': {'TZ': 'UTC', 'LANG': 'en_US.UTF-8', 'LC_ALL': 'en_US.UTF-8'}}
    if (not isinstance(baseline, dict) or type(baseline.get('schema_version')) is not int or
            baseline['schema_version'] != 1 or baseline.get('source_commit') != REVISION or
            baseline.get('method') != 'pinned self-citation source-build repeatability v1' or
            any(baseline.get(key) != value for key, value in expected.items())):
        raise ValueError('unmodified control version/build/runtime contract changed')
    helper_hash = digest((ROOT / 'scripts/replay_self_citation.py').read_bytes())
    if baseline.get('runner_sha256') != helper_hash:
        raise ValueError('shared replay helper differs from the control producer')
    try:
        release = [case for case in baseline['cases'] if case['case'] == 'release-19']
        if (len(release) != 1 or release[0]['seed'] != 19 or
                release[0]['requested_rows_including_initialization'] != 1200 or
                len(release[0]['runs']) != 2 or
                any(run['output']['sha256'] != SUPPLIED_HASH or run['completed_expected_rows'] is not True
                    for run in release[0]['runs'])):
            raise ValueError('unmodified release outcome contract changed')
    except (KeyError, TypeError) as error:
        raise ValueError('unmodified release outcome contract changed') from error
    return release[0], helper_hash


def instrument(raw):
    if raw.count(ANCHOR) != 1:
        raise ValueError('require exactly one pinned generation-call insertion anchor')
    return raw.replace(ANCHOR, OBSERVER + ANCHOR)


def trace_events(raw, initial_count, total_count):
    events, other_lines = [], 0
    for line in raw.decode('utf-8').splitlines():
        if not line.startswith('VMS_ROW_TRACE_V1\t'):
            other_lines += 1
            continue
        fields = line.split('\t')
        if len(fields) != 6 or fields[2] not in {'true', 'false'} or fields[3] not in {'true', 'false'}:
            raise ValueError('malformed versioned row-trace event')
        try:
            index, page, paragraph = (int(fields[i]) for i in [1, 4, 5])
        except ValueError as error:
            raise ValueError('trace index/counters must be integers') from error
        if min(index, page, paragraph) < 0:
            raise ValueError('trace index/counters must be nonnegative')
        events.append({'generated_row_index': index, 'model_paragraph_initial': fields[2] == 'true',
                       'model_paragraph_final': fields[3] == 'true',
                       'source_lines_in_page_pre_call': page, 'source_lines_in_paragraph_pre_call': paragraph})
    if [event['generated_row_index'] for event in events] != list(range(initial_count, total_count)):
        raise ValueError('trace coverage/order differs from every expected newly generated row')
    return events, other_lines


def row_ledger(raw, events, initial_count, total_count):
    if [event['generated_row_index'] for event in events] != list(range(initial_count, total_count)):
        raise ValueError('ledger requires complete ordered unique events')
    by_index = {event['generated_row_index']: event for event in events}
    ledger, offset = [], 0
    for file_line, line in enumerate(raw.splitlines(keepends=True), start=1):
        body = line.rstrip(b'\r\n')
        if body.strip() and not body.lstrip().startswith(b'#'):
            if not re.fullmatch(rb'[a-z]+(?: [a-z]+)*', body):
                raise ValueError('generated output row has unsupported notation/spacing; no repair is performed')
            index = len(ledger)
            initialized = index < initial_count
            context = (by_index.get(index) if not initialized else
                       {'generated_row_index': index, 'model_paragraph_initial': None,
                        'model_paragraph_final': None, 'source_lines_in_page_pre_call': None,
                        'source_lines_in_paragraph_pre_call': None})
            if context is None:
                raise ValueError('generated row lacks its observed call event')
            ledger.append({**context, 'initialized_input_row': initialized, 'native_file_line_number': file_line,
                           'start_byte': offset, 'end_byte_exclusive_without_line_ending': offset + len(body),
                           'row_sha256': digest(body), 'space_delimited_token_count': len(body.split(b' '))})
        offset += len(line)
    if len(ledger) != total_count:
        raise ValueError('native output row count differs from the fixed case')
    return ledger


def canonical(raw):
    return (json.dumps(raw, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def observe(reference, java_home, work):
    paths, inventory, base_config, supplied = source_inventory(reference)
    base_bytes = BASE.read_bytes()
    baseline = json.loads(base_bytes)
    release, helper_hash = control_contract(baseline)
    settings = configuration(base_config, {'save.path': './output/', 'save.filename': 'generated.txt'})
    if digest(settings) != release['effective_configuration_sha256']:
        raise ValueError('instrumented effective configuration differs from the unmodified control')
    work.mkdir(parents=True, exist_ok=False)
    source_root, classes, empty = work / 'sources', work / 'classes', work / 'empty-classpath'
    shutil.copytree(reference / 'source/src/main/java', source_root)
    classes.mkdir()
    empty.mkdir()
    main = source_root / 'de/voynich/text/SelfCitationTextGenerator.java'
    original, observed = main.read_bytes(), instrument(main.read_bytes())
    main.write_bytes(observed)
    for path in paths:
        copied = (source_root / path.removeprefix('source/src/main/java/')).read_bytes()
        expected = observed if path == MAIN else (reference / path).read_bytes()
        if copied != expected:
            raise ValueError('observer changed source outside the single declared insertion')
    environment = process_environment(os.environ)
    java, javac = java_home / 'bin/java', java_home / 'bin/javac'
    for name, executable in [('java', java), ('javac', javac)]:
        result = subprocess.run([str(executable), '-version'], capture_output=True, env=environment,
                                check=True, timeout=15)
        if (digest(executable.read_bytes()) != baseline['runtime'][name]['executable_sha256'] or
                (result.stdout + result.stderr).decode().strip() != baseline['runtime'][name]['version_output']):
            raise ValueError('runtime/compiler differs from the unmodified control')
    build = run_process([str(javac), *baseline['build_flags'], '--class-path', str(empty), '-d', str(classes),
                         *[str(source_root / path.removeprefix('source/src/main/java/')) for path in paths]],
                        work, environment, work / 'build')
    class_records = [{'path': str(path.relative_to(classes)), 'bytes': path.stat().st_size,
                      'sha256': digest(path.read_bytes())} for path in sorted(classes.rglob('*.class'))]
    previous_classes = {row['path']: row['sha256'] for row in baseline['class_inventory']}
    changed_classes = [row['path'] for row in class_records if previous_classes.get(row['path']) != row['sha256']]
    runs, ledgers, traces, outputs = [], [], [], []
    for repeat in [1, 2]:
        folder = work / f'run-{repeat}'
        folder.mkdir()
        (folder / 'output').mkdir()
        (folder / 'conf.properties').write_bytes(settings)
        process = (run_process([str(java), *baseline['jvm_flags'], '-cp', str(classes),
                                'de.voynich.text.SelfCitationTextGenerator'], folder, environment, folder / 'process')
                   if build['exit_code'] == 0 else {'exit_code': None, 'timed_out': False, 'not_run': 'build failed'})
        path = folder / 'output/generated.txt'
        output = path.read_bytes() if path.exists() else None
        events, ledger, error, other = None, None, None, None
        if process['exit_code'] == 0 and not process['timed_out'] and output == supplied:
            try:
                events, other = trace_events((folder / 'process.stderr.txt').read_bytes(), 1, 1200)
                ledger = row_ledger(output, events, 1, 1200)
            except ValueError as problem:
                error = str(problem)
        else:
            error = 'process did not finish with byte-identical control output'
        valid = error is None and ledger is not None
        if valid:
            (folder / 'row-ledger.json').write_bytes(canonical(ledger))
        runs.append({'repeat': repeat, 'process': process, 'output_sha256': digest(output) if output is not None else None,
                     'matches_complete_unmodified_and_supplied_bytes': output == supplied if output is not None else False,
                     'accepted_trace': valid, 'trace_error': error, 'non_event_stderr_line_count': other,
                     'canonical_events_sha256': digest(canonical(events)) if events is not None else None,
                     'canonical_ledger_sha256': digest(canonical(ledger)) if ledger is not None else None})
        outputs.append(output)
        ledgers.append(ledger)
        traces.append(events)
        print(f'trace-19 repeat {repeat}: accepted_trace={valid}', flush=True)
    unchanged = source_inventory(reference)[1] == inventory
    ledger = ledgers[0]
    accepted = (all(run['accepted_trace'] for run in runs) and ledgers[0] == ledgers[1] and
                traces[0] == traces[1] and outputs[0] == outputs[1] == supplied and unchanged)
    return {'schema_version': 1, 'method': 'output-preserving self-citation call trace v1',
            'plan_sha256': digest((ROOT / 'research/literature/SELF_CITATION_TRACE_PLAN.md').read_bytes()),
            'observer_sha256': digest(Path(__file__).read_bytes()), 'source_commit': REVISION,
            'shared_replay_helper_sha256': helper_hash,
            'base_repeatability_report_sha256': digest(base_bytes), 'effective_configuration_sha256': digest(settings),
            'original_main_source_sha256': digest(original), 'instrumented_main_source_sha256': digest(observed),
            'build': build, 'class_inventory': class_records, 'changed_compiled_classes': changed_classes,
            'source_inputs_unchanged_after_runs': unchanged, 'runs': runs,
            'accepted_output_preserving_trace': accepted,
            'ledger': ledger,
            'counts': {'output_rows': len(ledger), 'initialized_rows': sum(row['initialized_input_row'] for row in ledger),
                       'observed_generation_calls': sum(not row['initialized_input_row'] for row in ledger),
                       'model_paragraph_initial_calls': sum(row['model_paragraph_initial'] is True for row in ledger),
                       'model_paragraph_final_calls': sum(row['model_paragraph_final'] is True for row in ledger)} if ledger else None,
            'units': 'native generated rows; flags/counters observed before generateLine; initialized flags unknown',
            'scope': 'metadata bridge only; no manuscript locus/glyph equivalence, mechanism statistic, evaluation split or translation'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for argument in ['reference', 'java-home', 'work', 'output']:
        parser.add_argument(f'--{argument}', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('output record exists; choose a new record')
        report = observe(args.reference.resolve(), args.java_home.resolve(), args.work.resolve())
        with args.output.open('x', encoding='utf-8') as output:
            output.write(json.dumps(report, indent=2) + '\n')
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Row observation failed: {error}\n')
    print(f'Artifacts retained in {args.work}; record saved to {args.output}.')
    return not report['accepted_output_preserving_trace']


if __name__ == '__main__':
    raise SystemExit(main())
