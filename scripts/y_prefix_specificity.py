"""Exploratory prefix controls and matched vocabulary-opportunity accounting."""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import subprocess

try:
    from . import y_layout_prefix as source
except ImportError:
    import y_layout_prefix as source


BASE = 'research/hypotheses/y-prefix-specificity-v1'
PREFIXES = ('y', 'q', 'o')
FREQUENCIES = ('0', '1', '2+')
LENGTHS = ('2-4', '5-7', '8+')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def eligible_prefix(value, prefix):
    return len(value) >= 2 and value.startswith(prefix) and source.ascii_token(value)


def frequency_bin(count):
    if type(count) is not int or count < 0:
        raise ValueError('frequency must be a nonnegative integer')
    return '0' if count == 0 else '1' if count == 1 else '2+'


def length_bin(length):
    if type(length) is not int or length < 2:
        raise ValueError('candidate representation length must be at least two')
    return '2-4' if length <= 4 else '5-7' if length <= 7 else '8+'


def lookup_summary(values, counts, prefix):
    if any(not eligible_prefix(value, prefix) for value in values):
        raise ValueError('unsupported prefix-control candidate')
    cells = Counter((counts[value] > 0, counts[value[1:]] > 0) for value in values)
    total = len(values)
    gain = Fraction(cells[False, True] - cells[True, False], total) if total else None
    return {
        'candidate_tokens': total, 'original_matches': cells[True, True] + cells[True, False],
        'stripped_matches': cells[True, True] + cells[False, True],
        'both_match': cells[True, True], 'neither_matches': cells[False, False],
        'original_only': cells[True, False], 'stripped_only': cells[False, True],
        'mean_match_gain': round(float(gain), 8) if gain is not None else None,
    }, gain


def mean(values):
    return sum(values, Fraction(0)) / len(values) if values else None


def rendered_means(first, other):
    a, b = mean(first), mean(other)
    return {name: round(float(value), 8) if value is not None else None for name, value in (
        ('first_gain', a), ('other_gain', b),
        ('first_minus_other_gain', a - b if a is not None and b is not None else None))}


def common_keys(maps):
    return sorted(set.intersection(*(set(mapping) for mapping in maps)))


def collect_variant(rows, partition, counts):
    units = {unit['unit_id']: unit for unit in partition['units']}
    by_page = {page: unit for unit in partition['units'] for page in unit['selected_source_pages']}
    evaluation = {uid: {prefix: [[], []] for prefix in PREFIXES}
                  for uid, unit in units.items() if unit['partition'] == 'diagnostic_evaluation'}
    for locus, slots in rows:
        unit = by_page[locus.page]
        if unit['partition'] != 'diagnostic_evaluation':
            continue
        for position, token in enumerate(slots):
            if token is None:
                continue
            for prefix in PREFIXES:
                if eligible_prefix(token.value, prefix):
                    evaluation[unit['unit_id']][prefix][int(position != 0)].append(token.value)
    output, prefix_gains, cell_gains = [], {}, {}
    for uid in sorted(evaluation):
        prefixes, cells = [], []
        for prefix in PREFIXES:
            first, a = lookup_summary(evaluation[uid][prefix][0], counts, prefix)
            other, b = lookup_summary(evaluation[uid][prefix][1], counts, prefix)
            prefixes.append({'prefix': prefix, 'first_slot': first, 'other_slots': other})
            if a is not None and b is not None:
                prefix_gains[uid, prefix] = (a, b)
        y_first, y_other = evaluation[uid]['y']
        for frequency in FREQUENCIES:
            for length in LENGTHS:
                classes = [[value for value in values
                            if frequency_bin(counts[value]) == frequency and length_bin(len(value)) == length]
                           for values in (y_first, y_other)]
                first, a = lookup_summary(classes[0], counts, 'y')
                other, b = lookup_summary(classes[1], counts, 'y')
                cells.append({'frequency_bin': frequency, 'length_bin': length,
                              'first_slot': first, 'other_slots': other})
                if a is not None and b is not None:
                    cell_gains[uid, frequency, length] = (a, b)
        output.append({'unit_id': uid, 'prefixes': prefixes, 'y_opportunity_cells': cells})
    return output, prefix_gains, cell_gains


def control_report(sources, partition, baseline):
    original = source.analyze(sources, partition)
    if original != {key: baseline[key] for key in original}:
        raise ValueError('complete v1 scientific reconstruction differs from the pinned baseline')
    paired, selected, _ = source.selection(sources)
    variants, eligible_sets = [], []
    for metadata, document in paired:
        loci = source.selected_records(document, selected)
        for spacing in ('split', 'join'):
            for alternatives in ('exclude', 'first'):
                rows = source.prepare_rows(loci, spacing, alternatives)
                eligible = {locus.key for locus, slots in rows if slots and slots[0] is not None
                            and source.ascii_token(slots[0].value)
                            and sum(token is not None for token in slots) >= 2}
                eligible_sets.append(eligible)
                variants.append(({'source_id': metadata['id'], 'source_sha256': metadata['sha256'],
                                  'uncertain_spaces': spacing, 'alternatives': alternatives}, rows))
    shared = set.intersection(*eligible_sets)
    page_units = {page: unit for unit in partition['units'] for page in unit['selected_source_pages']}
    outputs, prefix_maps, cell_maps = [], [], []
    for index, (metadata, all_rows) in enumerate(variants):
        rows = [(locus, slots) for locus, slots in all_rows if locus.key in shared]
        counts = Counter(token.value for locus, slots in rows
                         if page_units[locus.page]['partition'] == 'dictionary_development'
                         for token in slots[1:] if token is not None and source.ascii_token(token.value))
        vocabulary, total = source.fit_vocabulary(rows, page_units)
        v1_vocabulary = baseline['variants'][index]['vocabulary']
        current = {'distinct_strings': len(counts), 'development_internal_tokens': sum(counts.values()),
                   'sorted_strings_sha256': source.key_digest(counts)}
        if vocabulary != set(counts) or total != sum(counts.values()) or current != v1_vocabulary:
            raise ValueError('development vocabulary changed from v1')
        units, prefix_gains, cell_gains = collect_variant(rows, partition, counts)
        # Independently computed y cells must reproduce all 18 original units.
        by_id = {unit['unit_id']: unit for unit in units}
        for old in baseline['variants'][index]['evaluation_units']:
            current_y = by_id[old['unit_id']]['prefixes'][0]
            if any(current_y[field] != old[field] for field in ('first_slot', 'other_slots')):
                raise ValueError('v1 y lookup-cell accounting changed')
        outputs.append({**metadata, 'vocabulary': current, 'evaluation_units': units})
        prefix_maps.append(prefix_gains)
        cell_maps.append(cell_gains)
    prefix_units = common_keys([{uid: True for uid, _ in mapping
                                if all((uid, prefix) in mapping for prefix in PREFIXES)}
                               for mapping in prefix_maps])
    cells = common_keys(cell_maps)
    matched_units = sorted({uid for uid, _, _ in cells})
    evaluation_ids = sorted(unit['unit_id'] for unit in partition['units']
                            if unit['partition'] == 'diagnostic_evaluation')
    for output, prefixes, strata, old in zip(outputs, prefix_maps, cell_maps, baseline['variants']):
        for unit in output['evaluation_units']:
            uid = unit['unit_id']
            missing = [{'prefix': item['prefix'], 'role': role}
                       for item in unit['prefixes'] for role in ('first_slot', 'other_slots')
                       if item[role]['candidate_tokens'] == 0]
            unit['comparison_a_eligibility'] = {
                'common_across_all_variants': uid in prefix_units,
                'missing_candidate_classes_in_this_variant': missing,
                'excluded_only_by_other_variants': uid not in prefix_units and not missing,
            }
            for cell in unit['y_opportunity_cells']:
                key = (uid, cell['frequency_bin'], cell['length_bin'])
                missing = [role for role in ('first_slot', 'other_slots') if cell[role]['candidate_tokens'] == 0]
                cell['eligibility'] = {
                    'common_across_all_variants': key in cells,
                    'missing_candidate_classes_in_this_variant': missing,
                    'excluded_only_by_other_variants': key not in cells and not missing,
                }
        comparison_a = []
        selective = {}
        for prefix in PREFIXES:
            gains = [prefixes[uid, prefix] for uid in prefix_units]
            summary = rendered_means([a for a, _ in gains], [b for _, b in gains])
            selective[prefix] = mean([a - b for a, b in gains])
            comparison_a.append({'prefix': prefix, **summary})
        differences = {name: round(float(selective['y'] - selective[prefix]), 8)
                       if selective['y'] is not None else None
                       for name, prefix in (('y_minus_q_selectivity', 'q'), ('y_minus_o_selectivity', 'o'))}
        unit_gains = []
        for uid in matched_units:
            own = [strata[cell] for cell in cells if cell[0] == uid]
            unit_gains.append((mean([a for a, _ in own]), mean([b for _, b in own])))
        matched = rendered_means([a for a, _ in unit_gains], [b for _, b in unit_gains])
        own_raw = [prefixes[uid, 'y'] for uid in matched_units]
        raw = rendered_means([a for a, _ in own_raw], [b for _, b in own_raw])
        delta = (mean([a - b for a, b in unit_gains]) - mean([a - b for a, b in own_raw])) if matched_units else None
        output['comparison_a'] = {'prefixes': comparison_a, **differences}
        output['comparison_b'] = {'matched_cells_equal_weight_within_unit': matched,
                                  'unmatched_y_on_same_units': raw,
                                  'matched_minus_unmatched_selectivity': round(float(delta), 8) if delta is not None else None}
        output['original_v1_y_summary'] = old['common_unit_summary']
    return {
        'schema_version': 1, 'control_version': 'y-prefix-specificity-v1',
        'analysis_status': 'descriptive controls on previously used candidate-development data',
        'valid_candidate_holdout': False, 'previously_unseen': False,
        'common_eligible_locations': len(shared), 'sorted_common_eligible_keys_sha256': source.key_digest(shared),
        'comparison_a_common_unit_ids': prefix_units,
        'comparison_a_excluded_unit_ids': sorted(set(evaluation_ids) - set(prefix_units)),
        'comparison_b_common_cells': [{'unit_id': uid, 'frequency_bin': frequency, 'length_bin': length}
                                      for uid, frequency, length in cells],
        'comparison_b_common_unit_ids': matched_units,
        'comparison_b_excluded_unit_ids': sorted(set(evaluation_ids) - set(matched_units)),
        'variants': outputs,
    }


def verify_inputs():
    path = source.ROOT / BASE / 'inputs.json'
    record = json.loads(path.read_bytes())
    if (record['prefixes'] != list(PREFIXES) or record['frequency_bins'] != list(FREQUENCIES)
            or record['length_bins'] != list(LENGTHS) or record['control_version'] != 'y-prefix-specificity-v1'):
        raise ValueError('control plan declarations differ from the implementation')
    for pin in record['pins'].values():
        target = source.ROOT / pin['path']
        if not target.resolve().is_relative_to(source.ROOT.resolve()) or sha(target.read_bytes()) != pin['sha256']:
            raise ValueError('a pre-control input pin changed')
    return record


def protect_output(path, record):
    source.protect_output(path, source.prepare_partition(), source.ROOT / source.BASE / 'partition.json')
    pins = [source.ROOT / pin['path'] for pin in record['pins'].values()]
    pins += [source.ROOT / BASE / 'inputs.json', source.ROOT / BASE / 'PLAN.md', Path(__file__)]
    if path.resolve() in {pin.resolve() for pin in pins} or (path.exists() and any(
            pin.exists() and path.samefile(pin) for pin in pins)):
        raise ValueError('control output aliases a fixed input or registered record')


def registration(commit, started):
    if not commit or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('require the pre-control commit')
    for name in ('PLAN.md', 'inputs.json'):
        relative = BASE + '/' + name
        if subprocess.check_output(['git', 'show', commit + ':' + relative], cwd=source.ROOT) != (source.ROOT / relative).read_bytes():
            raise ValueError('control plan/input record changed after registration')
    committed = subprocess.check_output(['git', 'show', '-s', '--format=%cI', commit], cwd=source.ROOT).decode().strip()
    if datetime.fromisoformat(started) <= datetime.fromisoformat(committed):
        raise ValueError('control execution must follow registration')
    return committed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    parser.add_argument('--pre-control-commit')
    args = parser.parse_args()
    try:
        record = verify_inputs()
        if args.output:
            protect_output(args.output, record)
        expected = json.loads(args.check.read_bytes()) if args.check else None
        commit = args.pre_control_commit or (expected['execution']['pre_control_commit'] if expected else None)
        started = expected['execution']['control_started_at'] if expected else datetime.now(timezone.utc).isoformat()
        committed = registration(commit, started)
        sources, _, _ = source.load_pins()
        partition = json.loads((source.ROOT / source.BASE / 'partition.json').read_bytes())
        if partition != source.prepare_partition():
            raise ValueError('parent diagnostic partition no longer reproduces')
        baseline = json.loads((source.ROOT / source.BASE / 'results.json').read_bytes())
        report = control_report(sources, partition, baseline)
        report['input_pins'] = record['pins']
        report['implementation_sha256'] = sha(Path(__file__).read_bytes())
        report['execution'] = {'pre_control_commit': commit, 'registered_at': committed, 'control_started_at': started,
                               'timestamps_are_not_independent_certification': True}
        if expected is not None and report != expected:
            raise ValueError('complete control report differs from replay')
        if args.output:
            protect_output(args.output, record)
            args.output.write_text(json.dumps(report, indent=2) + '\n')
            print('Recorded all prefix and opportunity controls without a new support/validation claim.')
        else:
            print('Fixed inputs, v1 reconstruction, and complete control report verified.')
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'prefix controls failed: {error}\n')


if __name__ == '__main__':
    main()
