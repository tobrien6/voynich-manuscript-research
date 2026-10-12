"""Frozen exploratory lookup comparison with matched other-prefix controls."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from pathlib import Path
import subprocess

try:
    from . import y_layout_prefix as parent
    from .audit_eva_token_coverage import encoded, load_json
except ImportError:
    import y_layout_prefix as parent
    from audit_eva_token_coverage import encoded, load_json


ROOT = Path(__file__).resolve().parents[1]
BASE = Path(parent.BASE)
PROTOCOL = ROOT / BASE / 'matched-control-protocol.json'
PARENT = ROOT / BASE / 'results.json'
ROLES = ('first', 'other')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def frequency_bin(count):
    require(type(count) is int and count >= 0, 'frequency must be a nonnegative integer')
    return count.bit_length()


def scorable(value):
    return (isinstance(value, str) and len(value) >= 2 and parent.ascii_token(value)
            and 'a' <= value[0] <= 'z')


def lookup(value, vocabulary):
    require(scorable(value), 'require two ASCII letters and a lower-case initial')
    before, after = value in vocabulary, value[1:] in vocabulary
    return before, after, int(after) - int(before)


def exact(value):
    return None if value is None else {
        'numerator': value.numerator, 'denominator': value.denominator,
        'decimal': round(float(value), 8)}


def cells(scores):
    counted = Counter((before, after) for before, after, _ in scores)
    return {'occurrences': len(scores), 'both_match': counted[True, True],
            'neither_matches': counted[False, False], 'original_only': counted[True, False],
            'stripped_only': counted[False, True]}


def fit_counts(rows, page_units):
    return Counter(token.value for locus, slots in rows
                   if page_units[locus.page]['partition'] == 'dictionary_development'
                   for token in slots[1:] if token is not None and parent.ascii_token(token.value))


def treatment(rows, page_units, frame, frequencies):
    """Score every fixed-frame occurrence; retain all matching strata and coverage."""
    vocabulary = set(frequencies)
    require(all(type(n) is int and n > 0 for n in frequencies.values()), 'invalid development frequencies')
    groups = defaultdict(lambda: {'targets': [], 'controls': [], 'prefixes': Counter()})
    for locus, slots in rows:
        unit = page_units[locus.page]['unit_id']
        if unit not in frame:
            continue
        for index, token in enumerate(slots):
            if token is None or not scorable(token.value):
                continue
            value = token.value
            role = 'first' if index == 0 else 'other'
            key = (unit, role, len(value), frequency_bin(frequencies.get(value, 0)))
            group = groups[key]
            score = lookup(value, vocabulary)
            if value.startswith('y'):
                group['targets'].append(score)
            else:
                group['controls'].append(score)
                group['prefixes'][value[0]] += 1
    totals = {(unit, role): {'all': [], 'matched': [], 'unmatched': [],
                            'control_sum': Fraction(0), 'pool_controls': 0, 'pair_uses': 0}
              for unit in frame for role in ROLES}
    strata = []
    for (unit, role, length, bucket), group in sorted(groups.items()):
        targets, controls = group['targets'], group['controls']
        # Frequency zero means absent, positive means present. Matching this
        # state cancels the original-membership term in every residual.
        require(all(before == (bucket > 0) for before, _, _ in targets + controls),
                'frequency support differs from vocabulary membership')
        control_mean = Fraction(sum(score[2] for score in controls), len(controls)) if controls else None
        target_mean = Fraction(sum(score[2] for score in targets), len(targets)) if targets else None
        adjusted = target_mean - control_mean if targets and controls else None
        item = totals[unit, role]
        item['all'].extend(targets)
        item['matched' if controls else 'unmatched'].extend(targets)
        if targets and controls:
            item['control_sum'] += len(targets) * control_mean
            item['pool_controls'] += len(controls)
            item['pair_uses'] += len(targets) * len(controls)
        strata.append({'unit_id': unit, 'position': role, 'ascii_length': length,
                       'frequency_bin': bucket, 'targets': cells(targets), 'controls': cells(controls),
                       'control_prefix_occurrences': dict(sorted(group['prefixes'].items())),
                       'matched_targets': len(targets) if controls else 0,
                       'mean_target_gain': exact(target_mean), 'mean_control_gain': exact(control_mean),
                       'mean_adjusted_gain': exact(adjusted)})
    units, gains = [], {}
    for unit in frame:
        roles, means = {}, []
        for role in ROLES:
            item = totals[unit, role]
            count = len(item['matched'])
            y_mean = Fraction(sum(score[2] for score in item['matched']), count) if count else None
            control_mean = item['control_sum'] / count if count else None
            adjusted = y_mean - control_mean if count else None
            roles[role] = {'all_targets': cells(item['all']), 'matched_targets': cells(item['matched']),
                           'unmatched_targets': cells(item['unmatched']),
                           'distinct_pool_control_occurrences': item['pool_controls'],
                           'target_control_pair_uses': item['pair_uses'],
                           'mean_matched_target_gain': exact(y_mean),
                           'mean_assigned_control_gain': exact(control_mean),
                           'mean_adjusted_gain': exact(adjusted)}
            means.append((y_mean, control_mean, adjusted))
        missing = [role for role in ROLES if not roles[role]['matched_targets']['occurrences']]
        if not missing:
            gains[unit] = means
        units.append({'unit_id': unit, 'positions': roles, 'missing_matched_classes': missing})
    return {'strata': strata, 'units': units}, gains


def summarize(results, gain_maps, frame):
    require(len(results) == len(gain_maps) == 8, 'require all eight variants')
    common = sorted(set(frame).intersection(*(set(gains) for gains in gain_maps)))
    adjusted_selectivities = []
    for result, gains in zip(results, gain_maps):
        means = {(role, kind): sum((gains[unit][index][kind] for unit in common), Fraction(0)) / len(common)
                 if common else None for index, role in enumerate(ROLES) for kind in range(3)}
        summary = {}
        for kind, name in enumerate(('matched_target', 'assigned_control', 'adjusted')):
            first, other = means['first', kind], means['other', kind]
            summary[name] = {'first_mean': exact(first), 'other_mean': exact(other),
                             'first_minus_other': exact(first - other) if common else None}
        result['equal_unit_summary'] = summary
        for unit in result['units']:
            unit['included_in_all_variant_joint_summary'] = unit['unit_id'] in common
        if common:
            adjusted_selectivities.append(means['first', 2] - means['other', 2])
    decision = ('indeterminate_matching_coverage' if not common else
                'positive_adjusted_selectivity_in_all_variants' if all(x > 0 for x in adjusted_selectivities)
                else 'mixed_or_nonpositive_adjusted_selectivity')
    return {'joint_unit_ids': common, 'joint_unit_count': len(common),
            'excluded_frame_units': sorted(set(frame) - set(common)), 'decision': decision,
            'variants': results}


def verified_inputs(protocol):
    require(type(protocol.get('schema_version')) is int and protocol['schema_version'] == 1,
            'unsupported protocol schema')
    require(protocol['analysis_id'] == 'y-prefix-matched-other-prefix-v1' and
            protocol['target_prefix'] == 'y' and protocol['exact_ascii_length_match'] is True and
            protocol['position_classes'] == list(ROLES) and
            protocol['frequency_bin'] == '0 if count is zero else count.bit_length()', 'unsupported matching rule')
    for path, expected in protocol['input_sha256'].items():
        require(digest((ROOT / path).read_bytes()) == expected, 'protocol input drift: ' + path)
    for name, expected in protocol['dependency_sha256'].items():
        require(Path(name).name == name and digest((ROOT / 'scripts' / name).read_bytes()) == expected,
                'protocol dependency drift: ' + name)
    original = load_json(PARENT.read_bytes())
    partition_path = ROOT / BASE / 'partition.json'
    partition = load_json(partition_path.read_bytes())
    prepared = parent.prepare_partition()
    require(encoded(partition) == encoded(prepared), 'parent partition differs from pinned reconstruction')
    sources, _, pins = parent.load_pins()
    actual = parent.analyze(sources, partition)
    actual['partition_sha256'] = digest(partition_path.read_bytes())
    actual['input_pins'] = pins
    actual['implementation_sha256'] = digest(Path(parent.__file__).read_bytes())
    execution = original['execution']
    committed = parent.verify_registration(execution['pre_run_commit'], partition_path, execution['fit_started_at'])
    actual['execution'] = {'pre_run_commit': execution['pre_run_commit'], 'registration_committed_at': committed,
                           'fit_started_at': execution['fit_started_at'],
                           'timestamp_claim_is_not_independent_certification': True}
    require(encoded(actual) == encoded(original), 'complete parent report differs from replay')
    require(original['selection']['common_evaluation_unit_ids'] == protocol['evaluation_unit_frame'], 'parent frame drift')
    require(original['selection']['common_eligible_locations'] == protocol['parent_common_eligible_loci'] and
            original['selection']['sorted_common_eligible_keys_sha256'] == protocol['parent_cohort_sha256'],
            'parent common locus cohort drift')
    return sources, partition, original


def report(protocol):
    sources, partition, original = verified_inputs(protocol)
    paired, selected, _ = parent.selection(sources)
    page_units = {page: unit for unit in partition['units'] for page in unit['selected_source_pages']}
    variants, eligible_sets = [], []
    for source, document in paired:
        loci = parent.selected_records(document, selected)
        for spacing in ('split', 'join'):
            for alternative in ('exclude', 'first'):
                rows = parent.prepare_rows(loci, spacing, alternative)
                eligible_sets.append({locus.key for locus, slots in rows if slots and slots[0] is not None
                                      and parent.ascii_token(slots[0].value)
                                      and sum(token is not None for token in slots) >= 2})
                variants.append((source, spacing, alternative, rows))
    common = set.intersection(*eligible_sets)
    require(len(common) == protocol['parent_common_eligible_loci'] and
            parent.key_digest(common) == protocol['parent_cohort_sha256'], 'control common locus cohort drift')
    frame = protocol['evaluation_unit_frame']
    results, gain_maps = [], []
    for (source, spacing, alternative, all_rows), baseline in zip(variants, original['variants']):
        metadata = {'source_id': source['id'], 'uncertain_spaces': spacing, 'alternatives': alternative}
        require(metadata == {key: baseline[key] for key in metadata}, 'variant ordering drift')
        rows = [(locus, slots) for locus, slots in all_rows if locus.key in common]
        frequencies = fit_counts(rows, page_units)
        vocabulary = baseline['vocabulary']
        require(len(frequencies) == vocabulary['distinct_strings'] and sum(frequencies.values()) ==
                vocabulary['development_internal_tokens'] and parent.key_digest(frequencies) ==
                vocabulary['sorted_strings_sha256'], 'development vocabulary drift')
        result, gains = treatment(rows, page_units, frame, frequencies)
        parent_units = {unit['unit_id']: unit for unit in baseline['evaluation_units']}
        for unit in result['units']:
            for role, old_role in (('first', 'first_slot'), ('other', 'other_slots')):
                old, current = parent_units[unit['unit_id']][old_role], unit['positions'][role]['all_targets']
                require(current['occurrences'] == old['candidate_tokens'] and all(current[key] == old[key]
                        for key in ('both_match', 'neither_matches', 'original_only', 'stripped_only')),
                        'control frame does not reconstruct every parent target lookup cell')
        result.update(metadata, source_sha256=source['sha256'], vocabulary=vocabulary,
                      development_frequency_sha256=digest(encoded(sorted(frequencies.items()))),
                      original_full_frame_y_summary=baseline['common_unit_summary'])
        results.append(result)
        gain_maps.append(gains)
    require([{key: item[key] for key in ('source_id', 'uncertain_spaces', 'alternatives')} for item in results]
            == protocol['variant_order'], 'protocol variant ordering drift')
    return {'schema_version': 1, 'analysis_id': protocol['analysis_id'],
            'analysis_status': protocol['analysis_status'], 'valid_candidate_holdout': False,
            'previously_unseen': False, 'original_unit_frame': frame,
            'parent_cohort_sha256': protocol['parent_cohort_sha256'],
            'parent_result_sha256': digest(PARENT.read_bytes()),
            'protocol_sha256': digest(encoded(protocol)), 'input_sha256': protocol['input_sha256'],
            'dependency_sha256': protocol['dependency_sha256'],
            **summarize(results, gain_maps, frame)}


def registration(commit, protocol_path, started):
    require(isinstance(commit, str) and len(commit) == 40 and all(c in '0123456789abcdef' for c in commit),
            'require exact pre-measurement Git commit')
    paths = {BASE / 'MATCHED_CONTROL_PLAN.md': ROOT / BASE / 'MATCHED_CONTROL_PLAN.md',
             BASE / 'MATCHED_CONTROL_EXPOSURE.md': ROOT / BASE / 'MATCHED_CONTROL_EXPOSURE.md',
             BASE / 'matched-control-protocol.json': protocol_path,
             Path('scripts/y_prefix_matched_controls.py'): Path(__file__)}
    for relative, path in paths.items():
        old = subprocess.check_output(['git', 'show', commit + ':' + str(relative)], cwd=ROOT)
        require(old == path.read_bytes(), 'control registration file drift: ' + str(relative))
    timestamp = subprocess.check_output(['git', 'show', '-s', '--format=%cI', commit], cwd=ROOT).decode().strip()
    moment = datetime.fromisoformat(started)
    require(moment.tzinfo is not None and moment > datetime.fromisoformat(timestamp),
            'control measurement must begin after registration')
    return timestamp


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, default=PROTOCOL)
    parser.add_argument('--registered-commit')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args(argv)
    try:
        protocol = load_json(args.protocol.read_bytes())
        prepared = {'input_pins': {path: {'path': path} for path in protocol['input_sha256']}}
        prepared['input_pins']['protocol'] = {'path': str(args.protocol.resolve())}
        if args.output:
            parent.protect_output(args.output, prepared, ROOT / BASE / 'partition.json')
        expected = load_json(args.check.read_bytes()) if args.check else None
        commit = args.registered_commit or (expected['execution']['registered_commit'] if expected else None)
        started = expected['execution']['measurement_started_at'] if expected else datetime.now(timezone.utc).isoformat()
        committed = registration(commit, args.protocol, started)
        result = report(protocol)
        result['implementation_sha256'] = digest(Path(__file__).read_bytes())
        result['execution'] = {'registered_commit': commit, 'registration_committed_at': committed,
                               'measurement_started_at': started, 'timestamps_are_declared_not_independently_certified': True}
        if args.check:
            require(encoded(result) == encoded(expected), 'complete matched-control report differs from replay')
        else:
            parent.protect_output(args.output, prepared, ROOT / BASE / 'partition.json')
            args.output.write_bytes(encoded(result))
        print('PASS: parent replay, matched strata, coverage and complete control report verified')
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'matched-control diagnostic failed: {error}\n')


if __name__ == '__main__':
    main()
