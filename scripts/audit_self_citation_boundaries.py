"""Audit the exposed seed-19 row trace against pinned boundary bookkeeping."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = 'research/literature/SELF_CITATION_BOUNDARY_PLAN.md'
REPORT = 'research/literature/self-citation-boundary-state.json'
TRACE = 'research/literature/self-citation-row-trace.json'
REPLAY = 'research/literature/self-citation-repeatability.json'
REVISION = '9e98c9122a0f490905e8b66f3911fc7ce095fd26'
PINS = {
    TRACE: '66ee19b89c3acba54112cc8a012cc3767ef0c2752a69cfd9a84e76d55e11fc91',
    REPLAY: 'a31bd822bc93546274a49db3a0fa144907c8aebf6864abf4f2230bd02d6c337e',
    'scripts/trace_self_citation_rows.py': 'a078447279d7557d243fdce925a66749747d5c665cb69c97923a69328cf4b778',
    'scripts/replay_self_citation.py': '4579f7caaf75ec124a8ffcbfd53b2e173f1ea117bdf7a7ee24761e53d2ee225f',
}
SOURCE_PINS = {
    'source/src/main/java/de/voynich/text/SelfCitationTextGenerator.java': '7afa236373a997d2e2ccef9a8e7ee799c5766b63ddf161bab8b72ce0f3bbf1e9',
    'source/src/main/java/de/voynich/text/StatisticHelper.java': 'e40bffd4518c3555771fb3d502908d1ff7af5e516648d080111c384512cc9918',
    'source/src/main/java/de/voynich/text/util/Config.java': 'f6cfdbe3dfa14def6f67b9197bdd18c3eb340fb3d7972da04bf315749e23adb7',
    'source/src/main/java/de/voynich/text/util/random/PseudoRandomNumberGenerator.java': '62c756d5f8490d7ee70d6ac508ca765f6dc023cfb604d40f5632e7eabd8857e9',
    'executable/conf.properties': '00944114753a7019e920199ed2d076065e30aed5e8402057b710d78ad0e1e800',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_pins(root, pins):
    result = {}
    for path, expected in pins.items():
        raw = (root / path).read_bytes()
        if digest(raw) != expected:
            raise ValueError(f'pinned input changed: {path}')
        result[path] = raw
    return result


def reconstruct(rows, initial_count, page_length):
    """Walk only boundary state, using observed final flags at eligible draws."""
    if (not isinstance(rows, list) or type(initial_count) is not int or
            type(page_length) is not int or not 0 < initial_count < page_length or
            len(rows) <= initial_count):
        raise ValueError('require initialized input, generated rows and a larger page length')
    context = ['model_paragraph_initial', 'model_paragraph_final',
               'source_lines_in_page_pre_call', 'source_lines_in_paragraph_pre_call']
    for index, row in enumerate(rows):
        if (not isinstance(row, dict) or type(row.get('generated_row_index')) is not int or
                row['generated_row_index'] != index or
                type(row.get('initialized_input_row')) is not bool or
                row['initialized_input_row'] != (index < initial_count)):
            raise ValueError('require complete ordered typed row indices and input origins')
        if index < initial_count:
            if any(key not in row or row[key] is not None for key in context):
                raise ValueError('initialized rows must have unknown call metadata')
        elif (any(type(row.get(key)) is not bool for key in context[:2]) or
              any(type(row.get(key)) is not int or row[key] < 0 for key in context[2:])):
            raise ValueError('generated call flags/counters have invalid types or values')

    page_counter = paragraph_counter = initial_count
    page_index = page_start = segment_start = 0
    segments, pages, page_segments = [], [], []
    causes = Counter({key: 0 for key in ['page_length', 'terminal', 'page_length_and_terminal', 'threshold_branch']})
    eligible_count = saturated_count = 0
    for index in range(initial_count, len(rows)):
        row = rows[index]
        initial = paragraph_counter == 0
        next_page, next_paragraph = page_counter + 1, paragraph_counter + 1
        page_full, terminal = next_page == page_length, index == len(rows) - 1
        forced = page_full or terminal
        eligible = (not forced and next_page < page_length - 2 and
                    next_paragraph > 3 and index < len(rows) - 2)
        eligible_count += eligible
        saturated = eligible and next_paragraph >= 10
        saturated_count += saturated
        final = row['model_paragraph_final']
        if (row['model_paragraph_initial'] != initial or
                (forced and not final) or (saturated and not final) or
                (not forced and final and not eligible)):
            raise ValueError(f'call flags disagree with source transition at row {index}')
        page_counter = 0 if forced else next_page
        paragraph_counter = 0 if final else next_paragraph
        if (row['source_lines_in_page_pre_call'] != page_counter or
                row['source_lines_in_paragraph_pre_call'] != paragraph_counter):
            raise ValueError(f'call counters disagree with source transition at row {index}')
        if final:
            cause = ('page_length_and_terminal' if page_full and terminal else
                     'page_length' if page_full else 'terminal' if terminal else 'threshold_branch')
            causes[cause] += 1
            segment_index = len(segments)
            segments.append({
                'segment_index': segment_index, 'source_page_block_index': page_index,
                'start_row_index': segment_start, 'end_row_index_inclusive': index,
                'row_count': index - segment_start + 1,
                'initialized_row_count': max(0, min(initial_count, index + 1) - segment_start),
                'first_row_initial_call_flag': rows[segment_start]['model_paragraph_initial'],
                'closure_condition': cause,
            })
            page_segments.append(segment_index)
            segment_start = index + 1
        if forced:
            pages.append({
                'source_page_block_index': page_index, 'start_row_index': page_start,
                'end_row_index_inclusive': index, 'row_count': index - page_start + 1,
                'page_length_reached': page_full, 'terminal_output_row': terminal,
                'segment_indices': page_segments,
            })
            page_index += 1
            page_start = index + 1
            page_segments = []
    if segment_start != len(rows) or page_start != len(rows):
        raise ValueError('terminal row must close every segment/page block')

    def distribution(records):
        return [{'row_count': length, 'count': count}
                for length, count in sorted(Counter(row['row_count'] for row in records).items())]

    return {
        'counts': {
            'output_rows': len(rows), 'initialized_rows': initial_count,
            'verified_generated_transitions': len(rows) - initial_count,
            'initial_call_flags': sum(row['model_paragraph_initial'] is True for row in rows),
            'final_call_flags': sum(row['model_paragraph_final'] is True for row in rows),
            'algorithmic_segments': len(segments), 'source_page_blocks': len(pages),
            'eligible_threshold_branch_calls': eligible_count,
            'eligible_threshold_branch_nonclosures': eligible_count - causes['threshold_branch'],
            'saturated_threshold_closures': saturated_count,
            'closure_conditions': dict(causes),
        },
        'segment_row_count_distribution': distribution(segments),
        'page_block_row_count_distribution': distribution(pages),
        'segments': segments, 'page_blocks': pages,
    }


def make_report(root=ROOT):
    raw = read_pins(root, PINS)
    trace, replay = json.loads(raw[TRACE]), json.loads(raw[REPLAY])
    if (trace.get('accepted_output_preserving_trace') is not True or
            trace.get('source_inputs_unchanged_after_runs') is not True or
            trace.get('source_commit') != REVISION or replay.get('source_commit') != REVISION):
        raise ValueError('require accepted unchanged-source control and trace')
    inventory = {row['path']: row['sha256'] for row in replay['source_inventory']}
    if any(inventory.get(path) != expected for path, expected in SOURCE_PINS.items()):
        raise ValueError('source evidence differs from the accepted replay inventory')
    rows = trace['ledger']
    if len(rows) != 1200 or trace['counts']['initialized_rows'] != 1:
        raise ValueError('fixed trace population differs')
    derived = reconstruct(rows, initial_count=1, page_length=29)
    return {
        'schema_version': 1, 'method': 'pinned source boundary-state audit v1',
        'input_pins': PINS, 'source_commit': REVISION, 'source_evidence_pins': SOURCE_PINS,
        'plan_sha256': digest((root / PLAN).read_bytes()),
        'producer_sha256': digest(Path(__file__).read_bytes()),
        'parameters': {'total_output_rows': 1200, 'initialized_rows': 1, 'lines_per_page': 29},
        **derived,
        'units': 'source-program rows, closed algorithmic segments and counter-reset page blocks',
        'exposure': 'complete accepted trace/source/output already inspected; descriptive software audit',
        'scope': 'no new Java run, random value recovery, prefix statistic, manuscript unit equivalence, model fit or translation',
    }


def write_new(path, raw):
    """Exclusive creation also rejects existing symlinks and hardlink aliases."""
    with path.open('xb') as output:
        output.write(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group()
    options.add_argument('--check', action='store_true')
    options.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        report = make_report()
        raw = (json.dumps(report, indent=2) + '\n').encode('utf-8')
        if args.check:
            if (ROOT / REPORT).read_bytes() != raw:
                raise ValueError('committed boundary-state report differs from complete regeneration')
        else:
            write_new(args.output or ROOT / REPORT, raw)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Boundary audit failed: {error}\n')
    print('Boundary-state report checked.' if args.check else 'Boundary-state report created.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
