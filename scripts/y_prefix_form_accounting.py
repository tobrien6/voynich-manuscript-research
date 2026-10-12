"""Exact literal-form accounting of the fixed exploratory y-prefix lookup gains."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

try:
    from . import y_layout_prefix as parent
    from .validate_evaluation_split import load_split_json
except ImportError:
    import y_layout_prefix as parent
    from validate_evaluation_split import load_split_json


ROOT = parent.ROOT
BASE = parent.BASE
INPUTS = BASE + '/form-accounting-inputs.json'
INPUTS_SHA256 = '3e9f400e1727f50e242d51f0fbcbe044346f1c13cfd2606159c801a3b90a6f64'
METHOD = 'y-prefix-literal-form-accounting-v1'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def score(value, vocabulary):
    require(isinstance(vocabulary, (set, frozenset)), 'require a fixed vocabulary set')
    require(isinstance(value, str) and parent.scorable(value), 'require a scorable literal y-prefixed form')
    before, after = value in vocabulary, value[1:] in vocabulary
    return before, after, int(after) - int(before)


def cells(values, vocabulary):
    counts = Counter(values)
    output = dict(candidate_tokens=len(values), original_matches=0, stripped_matches=0,
                  both_match=0, neither_matches=0, original_only=0, stripped_only=0)
    for value, count in counts.items():
        before, after, _ = score(value, vocabulary)
        output['original_matches'] += count * int(before)
        output['stripped_matches'] += count * int(after)
        category = ('both_match' if before and after else 'original_only' if before
                    else 'stripped_only' if after else 'neither_matches')
        output[category] += count
    mean = Fraction(output['stripped_only'] - output['original_only'], len(values)) if values else None
    output['mean_match_gain'] = round(float(mean), 8) if mean is not None else None
    return output, mean


def account_forms(cases, vocabulary, common_units):
    require(isinstance(cases, dict) and cases, 'require diagnostic unit cases')
    require(all(isinstance(uid, str) and uid for uid in cases), 'require nonempty unit identities')
    require(isinstance(common_units, (list, tuple)) and common_units
            and len(set(common_units)) == len(common_units)
            and set(common_units) <= set(cases), 'require distinct common unit identities present in cases')
    counters, ledger = {}, []
    for uid in sorted(cases):
        classes = cases[uid]
        require(isinstance(uid, str) and uid and isinstance(classes, (tuple, list)) and len(classes) == 2,
                'require unit identity and two candidate classes')
        for values in classes:
            require(isinstance(values, (tuple, list)), 'candidate class must be a token sequence')
            for value in values:
                score(value, vocabulary)
        first, other = classes
        a, gain_a = cells(first, vocabulary)
        b, gain_b = cells(other, vocabulary)
        if uid in common_units:
            require(gain_a is not None and gain_b is not None, 'common unit has an empty candidate class')
        counters[uid] = (Counter(first), Counter(other))
        ledger.append({'unit_id': uid, 'included_in_common_summary': uid in common_units,
                       'missing_classes_in_this_variant': [name for name, values in zip(['first', 'other'], classes) if not values],
                       'first_slot': a, 'other_slots': b,
                       'first_frequencies': dict(sorted(counters[uid][0].items())),
                       'other_frequencies': dict(sorted(counters[uid][1].items()))})
    forms = sorted({value for uid in common_units for counts in counters[uid] for value in counts})
    count = len(common_units)
    terms, first_gain, other_gain = [], Fraction(), Fraction()
    for value in forms:
        before, after, gain = score(value, vocabulary)
        first_weight = sum((Fraction(counters[uid][0][value], sum(counters[uid][0].values()))
                            for uid in common_units), Fraction()) / count
        other_weight = sum((Fraction(counters[uid][1][value], sum(counters[uid][1].values()))
                            for uid in common_units), Fraction()) / count
        difference = first_weight - other_weight
        first_gain += first_weight * gain
        other_gain += other_weight * gain
        terms.append({'form': value, 'stripped_form': value[1:],
                      'original_matches': before, 'stripped_matches': after, 'lookup_gain': gain,
                      'pooled_first_occurrences': sum(counters[uid][0][value] for uid in common_units),
                      'pooled_other_occurrences': sum(counters[uid][1][value] for uid in common_units),
                      'unit_weighted_first_frequency': rational(first_weight),
                      'unit_weighted_other_frequency': rational(other_weight),
                      'frequency_difference': rational(difference),
                      'selectivity_contribution': rational(difference * gain)})
    def unpack(item, field):
        return Fraction(**item[field])
    weight_a = sum((unpack(term, 'unit_weighted_first_frequency') for term in terms), Fraction())
    weight_b = sum((unpack(term, 'unit_weighted_other_frequency') for term in terms), Fraction())
    contribution = sum((unpack(term, 'selectivity_contribution') for term in terms), Fraction())
    direct_a = sum((cells(cases[uid][0], vocabulary)[1] for uid in common_units), Fraction()) / count
    direct_b = sum((cells(cases[uid][1], vocabulary)[1] for uid in common_units), Fraction()) / count
    require(weight_a == weight_b == 1 and first_gain == direct_a and other_gain == direct_b
            and contribution == direct_a - direct_b, 'exact form/unit accounting identity failed')
    pooled_first = [value for uid in common_units for value in cases[uid][0]]
    pooled_other = [value for uid in common_units for value in cases[uid][1]]
    return {'common_unit_count': count, 'literal_form_count': len(terms),
            'exact_first_gain': rational(first_gain), 'exact_other_gain': rational(other_gain),
            'exact_selective_gain': rational(contribution),
            'rounded_parent_summary': {'mean_unit_first_slot_gain': round(float(first_gain), 8),
                'mean_unit_other_slot_gain': round(float(other_gain), 8),
                'mean_unit_first_minus_other_gain': round(float(contribution), 8)},
            'exact_class_weight_sums': {'first': rational(weight_a), 'other': rational(weight_b)},
            'pooled_first_cells': cells(pooled_first, vocabulary)[0],
            'pooled_other_cells': cells(pooled_other, vocabulary)[0],
            'all_diagnostic_unit_frequencies': ledger, 'forms': terms}


def validate_pins(manifest, root=ROOT):
    entries = list(manifest['parent_files'].values()) + manifest['helper_files']
    for entry in entries:
        path = Path(entry['path'])
        require(not path.is_absolute() and '..' not in path.parts and '.git' not in path.parts,
                'pinned paths must be repository-relative')
        require(sha((root / path).read_bytes()) == entry['sha256'],
                f'pinned input or helper changed: {entry["path"]}')


def load_manifest(root=ROOT):
    raw = (root / INPUTS).read_bytes()
    require(sha(raw) == INPUTS_SHA256, 'accounting input manifest changed; review/version instead of replacing pins')
    manifest = load_split_json(raw.decode('utf-8'))
    require(manifest['schema_version'] == 1 and manifest['method'] == METHOD, 'unknown accounting manifest')
    validate_pins(manifest, root)
    return manifest


def load_parent(manifest, root=ROOT):
    validate_pins(manifest, root)
    paths = manifest['parent_files']
    expected = load_split_json((root / paths['report']['path']).read_text(encoding='utf-8'))
    partition_path = root / paths['partition']['path']
    partition = load_split_json(partition_path.read_text(encoding='utf-8'))
    prepared = parent.prepare_partition()
    require(partition == prepared, 'parent source/selection/dependency partition changed')
    execution = expected['execution']
    committed = parent.verify_registration(execution['pre_run_commit'], partition_path, execution['fit_started_at'])
    sources, _, _ = parent.load_pins()
    replay = parent.analyze(sources, partition)
    replay.update(partition_sha256=sha(partition_path.read_bytes()), input_pins=prepared['input_pins'],
                  implementation_sha256=paths['producer']['sha256'],
                  execution={'pre_run_commit': execution['pre_run_commit'], 'registration_committed_at': committed,
                             'fit_started_at': execution['fit_started_at'],
                             'timestamp_claim_is_not_independent_certification': True})
    require(replay == expected, 'complete pinned parent report no longer replays')
    return expected, partition, sources


def verify_variant(metadata, cases, vocabulary, development_count, expected):
    for field, value in metadata.items():
        require(expected[field] == value, f'parent variant identity changed: {field}')
    require(expected['vocabulary'] == {'distinct_strings': len(vocabulary),
            'development_internal_tokens': development_count, 'sorted_strings_sha256': parent.key_digest(vocabulary)},
            'parent vocabulary identity changed')
    actual = [{'unit_id': uid, 'first_slot': cells(values[0], vocabulary)[0],
               'other_slots': cells(values[1], vocabulary)[0]} for uid, values in cases.items()]
    require(actual == expected['evaluation_units'], 'parent unit identities or lookup cells changed')
    present = {uid for uid, values in cases.items() if values[0] and values[1]}
    require(sorted(set(cases) - present) == expected['excluded_evaluation_units_missing_candidate_class'],
            'parent missing-class exclusions changed')
    return present


def collect_variants(sources, partition, expected):
    paired, selected, _ = parent.selection(sources)
    page_units = {}
    for unit in partition['units']:
        for page in unit['selected_source_pages']:
            require(page not in page_units, 'parent source page assigned to multiple units')
            page_units[page] = unit
    variants, eligible_sets = [], []
    for source, document in paired:
        loci = parent.selected_records(document, selected)
        require(all(locus.page in page_units for locus in loci), 'parent selected page is unassigned')
        for spacing in ('split', 'join'):
            for alternatives in ('exclude', 'first'):
                rows = parent.prepare_rows(loci, spacing, alternatives)
                eligible = {locus.key for locus, slots in rows if slots and slots[0] is not None
                            and parent.ascii_token(slots[0].value)
                            and sum(token is not None for token in slots) >= 2}
                eligible_sets.append(eligible)
                metadata = {'source_id': source['id'], 'source_sha256': source['sha256'],
                            'uncertain_spaces': spacing, 'alternatives': alternatives,
                            'own_eligible_locus_count': len(eligible)}
                variants.append((metadata, rows))
    common = set.intersection(*eligible_sets)
    require(len(selected) == expected['selection']['selected_locations']
            and len(common) == expected['selection']['common_eligible_locations']
            and parent.key_digest(common) == expected['selection']['sorted_common_eligible_keys_sha256'],
            'parent common locus cohort changed')
    evaluation = [unit for unit in partition['units'] if unit['partition'] == 'diagnostic_evaluation']
    require(len(evaluation) == expected['selection']['diagnostic_evaluation_unit_count'],
            'parent diagnostic unit count changed')
    captured, unit_sets = [], []
    require(len(variants) == len(expected['variants']) == 8, 'require all eight parent variants')
    for (metadata, all_rows), original in zip(variants, expected['variants']):
        rows = [(locus, slots) for locus, slots in all_rows if locus.key in common]
        vocabulary, development_count = parent.fit_vocabulary(rows, page_units)
        cases = {unit['unit_id']: [[], []] for unit in evaluation}
        for locus, slots in rows:
            unit = page_units[locus.page]
            if unit['partition'] != 'diagnostic_evaluation':
                continue
            first, other = cases[unit['unit_id']]
            if parent.scorable(slots[0].value):
                first.append(slots[0].value)
            other.extend(token.value for token in slots[1:] if token is not None and parent.scorable(token.value))
        metadata['excluded_from_common_locus_cohort'] = sorted(selected - common)
        unit_sets.append(verify_variant(metadata, cases, vocabulary, development_count, original))
        captured.append((metadata, cases, vocabulary, original))
    common_units = sorted(set.intersection(*unit_sets))
    require(common_units == expected['selection']['common_evaluation_unit_ids']
            and len(common_units) == expected['selection']['common_evaluation_unit_count'],
            'parent common evaluation units changed')
    return captured, common_units


def report(manifest, root=ROOT):
    expected, partition, sources = load_parent(manifest, root)
    captured, common_units = collect_variants(sources, partition, expected)
    variants = []
    for metadata, cases, vocabulary, original in captured:
        result = account_forms(cases, vocabulary, common_units)
        require(result['rounded_parent_summary'] == original['common_unit_summary'],
                'exact form accounting differs from parent summary')
        variants.append({**metadata, 'vocabulary': original['vocabulary'], **result})
    return {'schema_version': 1, 'method': METHOD,
            'analysis_status': 'exact accounting follow-up on previously exposed diagnostic data',
            'valid_candidate_holdout': False, 'previously_unseen': False,
            'input_manifest_sha256': INPUTS_SHA256,
            'implementation_sha256': sha(Path(__file__).read_bytes()),
            'parent_input_pins': expected['input_pins'], 'parent_source_pins': partition['sources'],
            'parent_selection': expected['selection'], 'parent_decision_unchanged': expected['decision'],
            'score_rule': 'I(literal form without its first y in fixed vocabulary) - I(original in vocabulary)',
            'weight_rule': 'Equal common-unit weight; within-unit class occurrence frequencies',
            'other_slot_scope': 'All retained scorable non-first slots, including final slots',
            'development_vocabulary_scope': 'All retained ASCII non-first development slots, including final slots, on the common locus cohort',
            'variants': variants,
            'limitations': ['Form contributions are deterministic accounting terms, not causal effects or explained fractions.',
                'Exact-form matching at identical weights yields zero by construction; it is not a mechanism falsification.',
                'Parent exposures, vocabulary selection, related sources and policies remain dependent.',
                'No glyph meaning, validated reading, language, decipherment or translation is established.']}


def protect_output(output, manifest, root=ROOT, check_path=None):
    entries = list(manifest['parent_files'].values()) + manifest['helper_files']
    paths = {root / entry['path'] for entry in entries}
    paths.update({root / INPUTS, Path(__file__), root / 'data/transliterations.json'})
    parent_report = load_split_json((root / manifest['parent_files']['report']['path']).read_text(encoding='utf-8'))
    paths.update(root / item['path'] for item in parent_report['input_pins'].values())
    catalog = load_split_json((root / 'data/transliterations.json').read_text(encoding='utf-8'))
    paths.update(root / item['path'] for item in catalog['sources'])
    if check_path is not None:
        paths.add(check_path)
    folders = [root / 'data/raw', root / 'scripts', root / 'research/image-index']
    if output.exists():
        paths.update(path for folder in folders for path in folder.rglob('*') if path.is_file())
    resolved = output.resolve()
    require(not any(resolved.is_relative_to(folder.resolve()) for folder in folders)
            and not any(resolved == path.resolve() or
                        (output.exists() and path.exists() and output.samefile(path)) for path in paths),
            'accounting output must not overwrite pinned inputs, helpers, scripts, raw data or check report')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        manifest = load_manifest(root=ROOT)
        if args.output:
            protect_output(args.output, manifest, root=ROOT, check_path=args.check)
        result = report(manifest, root=ROOT)
        if args.check:
            require(result == load_split_json(args.check.read_text(encoding='utf-8')), 'form-accounting report differs from full replay')
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
        if args.output:
            validate_pins(manifest, root=ROOT)
            protect_output(args.output, manifest, root=ROOT, check_path=args.check)
            args.output.write_text(rendered, encoding='utf-8')
        elif not args.check:
            print(rendered, end='')
        if args.check:
            print('Complete parent and exact literal-form accounting report replay verified.')
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'form accounting failed: {error}\n')


if __name__ == '__main__':
    main()
