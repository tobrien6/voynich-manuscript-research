"""Planned exploratory y-removal lookup diagnostic; never held-out validation."""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

try:
    from .audit_transliterations import ROOT, load_sources
    from .audit_transcription_images import make_report, page_reference
    from .ivtff import TAG, without_free_comments
    from .locus_positions import prepare_rows
    from .prefix_strata import paragraph_start, select_locations
    from .section_strata import selected_records
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from audit_transcription_images import make_report, page_reference
    from ivtff import TAG, without_free_comments
    from locus_positions import prepare_rows
    from prefix_strata import paragraph_start, select_locations
    from section_strata import selected_records
    from token_baselines import paired_sources


BASE = 'research/hypotheses/y-layout-prefix-v1'
SEED = 'y-layout-prefix-v1-2026-10-11'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def key_digest(values):
    return sha(('\n'.join(sorted(values)) + '\n').encode('ascii'))


def page_families(page):
    reference = page_reference(page)
    if not reference['folio_sides']:
        raise ValueError(f'unsupported coarse page reference: {page}')
    return set(side[:-1] for side in reference['folio_sides'])


def selection(sources):
    paired = paired_sources(sources)
    shared_p0, regular = select_locations(paired)
    records = [selected_records(document, regular) for _, document in paired]
    indexed = [{locus.key: locus for locus in loci} for loci in records]
    starts = {key for key in regular if any(paragraph_start(index[key]) for index in indexed)}
    selected = regular - starts
    if not selected:
        raise ValueError('no jointly non-start regular P0 locations')
    return paired, selected, {
        'shared_present_p0_count': len(shared_p0), 'shared_regular_p0_count': len(regular),
        'excluded_nonregular_keys': sorted(shared_p0 - regular),
        'excluded_source_paragraph_start_keys': sorted(starts),
        'selected_location_count': len(selected), 'sorted_selected_keys_sha256': key_digest(selected),
    }


def repetition_body(locus):
    body = TAG.sub('', without_free_comments(locus.text)).replace('<%>', '').replace('<$>', '')
    body = ''.join(body.split())
    return body if body.count('.') >= 2 and not any(c in body for c in '?[]') else None


def build_partition(sources, image_report):
    """Construct dependencies and a deterministic partition without fitting a vocabulary."""
    paired, selected, selected_audit = selection(sources)
    parents = {}

    def find(number):
        parents.setdefault(number, number)
        if parents[number] != number:
            parents[number] = find(parents[number])
        return parents[number]

    def connect(numbers):
        numbers = sorted(set(numbers), key=int)
        for number in numbers:
            parents[find(number)] = find(numbers[0])

    for component in image_report['dependency_components']:
        connect(component['folio_ids'])
    repeated_edges = []
    for source, document in paired:
        bodies = defaultdict(set)
        for locus in document.loci:
            if locus.present and locus.kind == 'P0':
                body = repetition_body(locus)
                if body is not None:
                    bodies[body].update(page_families(locus.page))
        for body, families in sorted(bodies.items()):
            if len(families) > 1:
                connect(families)
                repeated_edges.append({'source_id': source['id'], 'body_sha256': sha(body.encode('ascii')),
                                       'numeric_families': sorted(families, key=int)})
    selected_pages = sorted({locus.page for _, document in paired for locus in document.loci
                             if locus.key in selected and locus.present and locus.kind == 'P0'})
    active_families = {family for page in selected_pages for family in page_families(page)}
    members = defaultdict(set)
    for family in list(parents):
        members[find(family)].add(family)
    for family in active_families:
        members[find(family)].add(family)
    active_groups = [sorted(group, key=int) for group in members.values() if group & active_families]
    if len(active_groups) < 2:
        raise ValueError('need at least two dependency units for the diagnostic partition')
    rank = lambda group: sha((SEED + '\n' + '\n'.join(group)).encode('ascii'))
    active_groups.sort(key=rank)
    evaluation_count = max(1, len(active_groups) // 5)
    units = []
    for index, group in enumerate(active_groups):
        group_set = set(group)
        pages = [page for page in selected_pages if page_families(page) & group_set]
        units.append({
            'unit_id': 'numeric-families:' + '+'.join(group), 'numeric_source_families': group,
            'partition': 'diagnostic_evaluation' if index < evaluation_count else 'dictionary_development',
            'rank_sha256': rank(group), 'selected_source_pages': pages,
            'canvas_ids': sorted({canvas for family in group for canvas in
                                 image_report['indexed_canvas_ids_by_leaf'].get(family, [])}),
        })
    return {
        'schema_version': 1, 'candidate_version': 'y-layout-prefix-v1',
        'status': 'exploratory_dictionary_partition', 'seed': SEED,
        'prior_exposure': 'Full-corpus results motivated this candidate; all units used for candidate development.',
        'valid_candidate_holdout': False, 'previously_unseen': False, 'image_region_alignment_reviewed': False,
        'sources': [{'id': source['id'], 'sha256': source['sha256']} for source, _ in paired],
        'selection': selected_audit, 'exact_string_dependency_edges': repeated_edges,
        'units': units,
    }


def load_pins():
    sources = paired_sources(load_sources())
    paths = {'source_catalog': 'data/transliterations.json',
             'image_report': 'research/folio-alignment/transcription-image-coverage.json',
             'canvas_index': 'research/image-index/canvases.csv',
             'image_index_audit': 'research/image-index/audit.json', 'plan': BASE + '/PLAN.md'}
    raw = {name: (ROOT / path).read_bytes() for name, path in paths.items()}
    report = json.loads(raw['image_report'])
    audit = json.loads(raw['image_index_audit'])
    identity = {field: audit[field] for field in
                ('manifest_url', 'manifest_sha256', 'access_date', 'access_timezone')}
    identity['canvases_csv_sha256'] = sha(raw['canvas_index'])
    rows = list(csv.DictReader(io.StringIO(raw['canvas_index'].decode('utf-8'))))
    # The accepted audit consumes the index builder's Booleans; its CSV stores
    # these as exact True/False strings. Restore that documented serialization.
    for row in rows:
        for field in ('has_partial_marker', 'has_multiple_explicit_sides'):
            if row[field] not in {'True', 'False'}:
                raise ValueError(f'invalid canvas-index Boolean: {field}')
            row[field] = row[field] == 'True'
    rebuilt = json.loads(json.dumps(make_report(sources, rows, identity)))
    if rebuilt != report:
        raise ValueError('accepted image-reference report differs from current pinned metadata')
    return sources, report, {name: {'path': paths[name], 'sha256': sha(data)} for name, data in raw.items()}


def prepare_partition():
    sources, images, pins = load_pins()
    partition = build_partition(sources, images)
    partition['input_pins'] = pins
    return partition


def ascii_token(value):
    return bool(re.fullmatch(r'[A-Za-z]+', value))


def scorable(value):
    return len(value) >= 2 and value.startswith('y') and ascii_token(value)


def match_gain(value, vocabulary):
    if not scorable(value):
        raise ValueError('score requires a lower-case y prefix and at least two ASCII letters')
    before, after = value in vocabulary, value[1:] in vocabulary
    return before, after, int(after) - int(before)


def case_summary(values, vocabulary):
    cells = Counter((before, after) for before, after, _ in
                    (match_gain(value, vocabulary) for value in values))
    count = len(values)
    gain = Fraction(cells[False, True] - cells[True, False], count) if count else None
    return {
        'candidate_tokens': count,
        'original_matches': cells[True, True] + cells[True, False],
        'stripped_matches': cells[True, True] + cells[False, True],
        'both_match': cells[True, True], 'neither_matches': cells[False, False],
        'original_only': cells[True, False], 'stripped_only': cells[False, True],
        'mean_match_gain': round(float(gain), 8) if gain is not None else None,
    }, gain


def fit_vocabulary(rows, page_units):
    values = [token.value for locus, slots in rows
              if page_units[locus.page]['partition'] == 'dictionary_development'
              for token in slots[1:] if token is not None and ascii_token(token.value)]
    return set(values), len(values)


def fixed_decision(gains):
    if not gains:
        return 'indeterminate'
    if len(gains) != 8:
        raise ValueError('decision requires all eight declared sensitivity variants')
    first, other = gains[0]
    primary_passes = first > 0 and first - other >= Fraction(1, 20)
    sensitivities_pass = all(a > 0 and a - b > 0 for a, b in gains[1:])
    return 'survives_v1_diagnostic' if primary_passes and sensitivities_pass else 'fails_v1_diagnostic'


def analyze(sources, partition):
    paired, selected, _ = selection(sources)
    core = {key: value for key, value in partition.items() if key != 'input_pins'}
    # Sources/selection/dependency/partition drift is checked by the CLI against
    # a freshly rebuilt partition; this pure function checks page assignment.
    page_units = {}
    for unit in core['units']:
        for page in unit['selected_source_pages']:
            if page in page_units:
                raise ValueError('source page belongs to multiple diagnostic units')
            page_units[page] = unit
    variants = []
    eligible_sets = []
    for source, document in paired:
        loci = selected_records(document, selected)
        if any(locus.page not in page_units for locus in loci):
            raise ValueError('selected source page has no diagnostic unit')
        for spacing in ('split', 'join'):
            for alternatives in ('exclude', 'first'):
                rows = prepare_rows(loci, spacing, alternatives)
                eligible = {locus.key for locus, slots in rows if slots and slots[0] is not None
                            and ascii_token(slots[0].value)
                            and sum(token is not None for token in slots) >= 2}
                eligible_sets.append(eligible)
                variants.append(({'source_id': source['id'], 'source_sha256': source['sha256'],
                                  'uncertain_spaces': spacing, 'alternatives': alternatives}, rows))
    common = set.intersection(*eligible_sets)
    evaluation_units = [unit for unit in core['units'] if unit['partition'] == 'diagnostic_evaluation']
    outputs, gain_maps = [], []
    for (metadata, all_rows), eligible in zip(variants, eligible_sets):
        rows = [(locus, slots) for locus, slots in all_rows if locus.key in common]
        vocabulary, development_token_count = fit_vocabulary(rows, page_units)
        cases = {unit['unit_id']: [[], []] for unit in evaluation_units}
        for locus, slots in rows:
            unit = page_units[locus.page]
            if unit['partition'] != 'diagnostic_evaluation':
                continue
            first, other = cases[unit['unit_id']]
            if scorable(slots[0].value):
                first.append(slots[0].value)
            other.extend(token.value for token in slots[1:] if token is not None and scorable(token.value))
        summaries, gains = [], {}
        for unit in evaluation_units:
            uid = unit['unit_id']
            first, a = case_summary(cases[uid][0], vocabulary)
            other, b = case_summary(cases[uid][1], vocabulary)
            summaries.append({'unit_id': uid, 'first_slot': first, 'other_slots': other})
            if a is not None and b is not None:
                gains[uid] = (a, b)
        gain_maps.append(gains)
        outputs.append({
            **metadata,
            'own_eligible_locus_count': len(eligible),
            'excluded_from_common_locus_cohort': sorted(selected - common),
            'vocabulary': {'distinct_strings': len(vocabulary), 'development_internal_tokens': development_token_count,
                           'sorted_strings_sha256': key_digest(vocabulary)},
            'evaluation_units': summaries,
        })
    common_units = sorted(set.intersection(*(set(gains) for gains in gain_maps)))
    averages = []
    for output, gains in zip(outputs, gain_maps):
        if common_units:
            a = sum((gains[uid][0] for uid in common_units), Fraction(0)) / len(common_units)
            b = sum((gains[uid][1] for uid in common_units), Fraction(0)) / len(common_units)
            averages.append((a, b))
            summary = {'mean_unit_first_slot_gain': round(float(a), 8),
                       'mean_unit_other_slot_gain': round(float(b), 8),
                       'mean_unit_first_minus_other_gain': round(float(a - b), 8)}
        else:
            summary = {field: None for field in ('mean_unit_first_slot_gain', 'mean_unit_other_slot_gain',
                                                'mean_unit_first_minus_other_gain')}
        output['common_unit_summary'] = summary
        output['excluded_evaluation_units_missing_candidate_class'] = sorted(
            unit['unit_id'] for unit in evaluation_units if unit['unit_id'] not in gains)
    return {
        'schema_version': 1, 'candidate_version': 'y-layout-prefix-v1',
        'analysis_status': 'exploratory; previously used candidate-development data',
        'valid_candidate_holdout': False, 'previously_unseen': False,
        'selection': {'selected_locations': len(selected), 'common_eligible_locations': len(common),
                      'sorted_common_eligible_keys_sha256': key_digest(common),
                      'diagnostic_evaluation_unit_count': len(evaluation_units),
                      'common_evaluation_unit_ids': common_units, 'common_evaluation_unit_count': len(common_units)},
        'decision': fixed_decision(averages),
        'decision_rule': 'primary first gain > 0 and first-minus-other >= 1/20; all seven sensitivities positive for both gains',
        'variants': outputs,
    }


def verify_registration(commit, partition_path, fit_started_at):
    if not commit or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('require the exact 40-character pre-fit Git commit')
    for relative, current in ((BASE + '/PLAN.md', ROOT / BASE / 'PLAN.md'),
                              (BASE + '/partition.json', partition_path)):
        recorded = subprocess.check_output(['git', 'show', commit + ':' + relative], cwd=ROOT)
        if recorded != current.read_bytes():
            raise ValueError('current rules/partition differ from the pre-fit commit')
    committed = subprocess.check_output(['git', 'show', '-s', '--format=%cI', commit], cwd=ROOT).decode().strip()
    fitted = datetime.fromisoformat(fit_started_at)
    if fitted.tzinfo is None or fitted <= datetime.fromisoformat(committed):
        raise ValueError('dictionary fitting must start after the recorded pre-fit commit')
    return committed


def protect_output(path, prepared, partition_path, *, preparing=False):
    """Keep both write modes from replacing explicit or implicit source inputs."""
    protected = {(ROOT / pin['path']).resolve() for pin in prepared['input_pins'].values()}
    catalog_path = ROOT / 'data/transliterations.json'
    protected.add(catalog_path.resolve())
    catalog = json.loads(catalog_path.read_bytes())
    protected.update((ROOT / source['path']).resolve() for source in catalog['sources'])
    protected.add((ROOT / BASE / 'PLAN.md').resolve())
    protected.add(Path(__file__).resolve())
    # Initial preparation may create a partition. Once present, both the
    # selected and standard registered paths must be preserved, including when
    # --partition names a separate copy of the historical record.
    for partition in (partition_path, ROOT / BASE / 'partition.json'):
        if not preparing or partition.exists():
            protected.add(partition.resolve())
    resolved = path.resolve()
    if resolved in protected or (path.exists() and any(
            candidate.exists() and path.samefile(candidate) for candidate in protected)):
        raise ValueError('output must not replace a pinned input, raw source, producer, plan or existing partition')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', type=Path, help='Write the pre-fit diagnostic partition only')
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    parser.add_argument('--partition', type=Path, default=ROOT / BASE / 'partition.json')
    parser.add_argument('--pre-run-commit', help='Exact commit containing the pre-fit plan and partition')
    args = parser.parse_args()
    try:
        prepared = prepare_partition()
        if args.prepare:
            protect_output(args.prepare, prepared, args.partition, preparing=True)
            args.prepare.write_text(json.dumps(prepared, indent=2) + '\n')
            print('Prepared exploratory dependency partition; no vocabulary fit or scoring performed.')
            return
        if args.output:
            protect_output(args.output, prepared, args.partition)
        partition = json.loads(args.partition.read_bytes())
        if partition != prepared:
            raise ValueError('committed diagnostic partition differs from current pinned inputs')
        expected = json.loads(args.check.read_bytes()) if args.check else None
        commit = args.pre_run_commit or (expected['execution']['pre_run_commit'] if expected else None)
        fitted = expected['execution']['fit_started_at'] if expected else datetime.now(timezone.utc).isoformat()
        committed = verify_registration(commit, args.partition, fitted)
        sources, _, _ = load_pins()
        report = analyze(sources, partition)
        report['partition_sha256'] = sha(args.partition.read_bytes())
        report['input_pins'] = prepared['input_pins']
        report['implementation_sha256'] = sha(Path(__file__).read_bytes())
        report['execution'] = {'pre_run_commit': commit, 'registration_committed_at': committed,
                               'fit_started_at': fitted, 'timestamp_claim_is_not_independent_certification': True}
        if expected is not None and report != expected:
            raise ValueError('committed y-layout report differs from complete replay')
        if args.output:
            # Recheck after fitting as well: an existing output can acquire an
            # input alias while the analysis runs. The next operation writes.
            protect_output(args.output, prepared, args.partition)
            args.output.write_text(json.dumps(report, indent=2) + '\n')
            print('Recorded exploratory diagnostic:', report['decision'])
        else:
            print('Pinned rules, partition, vocabulary fits, and complete diagnostic report verified.')
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'y-layout diagnostic failed: {error}\n')


if __name__ == '__main__':
    main()
