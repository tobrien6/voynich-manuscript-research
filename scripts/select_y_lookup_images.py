"""Freeze image pairs for positive y-removal lookups without inspecting pixels."""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

try:
    from . import y_layout_prefix as parent
    from .select_initial_prefix_images import key_order, PAGE
    from .ivtff import without_free_comments
except ImportError:
    import y_layout_prefix as parent
    from select_initial_prefix_images import key_order, PAGE
    from ivtff import without_free_comments


BASE = 'research/hypotheses/y-lookup-image-v1'
VARIANTS = tuple((s, spacing, alternatives) for s in ('ZL3b', 'IT2a')
                 for spacing in ('split', 'join') for alternatives in ('exclude', 'first'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def drawing(locus):
    return any(mark in without_free_comments(locus.text) for mark in ('<->', '<~>'))


def unique_images(rows):
    by_page = {}
    for row in rows:
        if (row['label_class'] == 'exact_single_side_label' and row['has_partial_marker'] == 'False'
                and row['has_multiple_explicit_sides'] == 'False' and PAGE.fullmatch('f' + row['yale_label'])):
            by_page.setdefault('f' + row['yale_label'], []).append(row)
    fields = ('yale_label', 'canvas_uri', 'image_oid', 'catalog_image_url', 'full_image_url',
              'image_service_url', 'image_width', 'image_height')
    return {page: {field: values[0][field] for field in fields}
            for page, values in by_page.items() if len(values) == 1}


def select_pairs(variant_rows, partition, canvas_rows, allowed_target_units):
    if len(variant_rows) != 8 or {metadata for metadata, _ in variant_rows} != set(VARIANTS):
        raise ValueError('require the eight declared source/policy treatments')
    row_maps = [{locus.key: (locus, slots) for locus, slots in rows} for _, rows in variant_rows]
    if any(len(mapping) != len(rows) for mapping, (_, rows) in zip(row_maps, variant_rows)):
        raise ValueError('duplicate source location')
    common = set.intersection(*[{key for key, (_, slots) in mapping.items() if slots and slots[0] is not None
                                and parent.ascii_token(slots[0].value)
                                and sum(token is not None for token in slots) >= 2} for mapping in row_maps])
    units = {page: unit for unit in partition['units'] for page in unit['selected_source_pages']}
    if any(mapping[key][0].page not in units for mapping in row_maps for key in common):
        raise ValueError('eligible source page lacks a dependency unit')
    images = unique_images(canvas_rows)
    vocabularies, references = [], []
    for mapping in row_maps:
        rows = [mapping[key] for key in common]
        vocabulary, _ = parent.fit_vocabulary(rows, units)
        vocabularies.append(vocabulary)
        references.append({(locus.key, index, token.value) for locus, slots in rows
                           if units[locus.page]['partition'] == 'dictionary_development'
                           for index, token in enumerate(slots) if index > 0 and token is not None
                           and parent.ascii_token(token.value)})
    stable_references = set.intersection(*references)
    reference_pools, candidates, excluded = {}, [], []
    evaluation_keys = sorted(key for key in common if units[row_maps[0][key][0].page]['partition'] == 'diagnostic_evaluation')
    for key in evaluation_keys:
        records = [mapping[key] for mapping in row_maps]
        page = records[0][0].page
        uid = units[page]['unit_id']
        values = {slots[0].value for _, slots in records}
        reasons = []
        if uid not in allowed_target_units:
            reasons.append('unit_not_scorable_in_parent_all_treatments')
        if len(values) != 1:
            reasons.append('first_form_differs_across_treatments')
        value = next(iter(values)) if len(values) == 1 else None
        if value is None or not parent.scorable(value):
            reasons.append('no_shared_scorable_y_first_form')
        elif not all(parent.match_gain(value, vocabulary)[2] == 1 for vocabulary in vocabularies):
            reasons.append('not_a_positive_lookup_gain_in_every_treatment')
        if any(drawing(locus) for locus, _ in records):
            reasons.append('target_inline_drawing_interruption')
        if page not in images:
            reasons.append('target_no_unique_exact_single_side_canvas')
        if reasons:
            excluded.append({'locus_key': key, 'unit_id': uid, 'reasons': reasons})
            continue
        remainder = value[1:]
        if remainder not in reference_pools:
            possible = sorted(item for item in stable_references if item[2] == remainder)
            eligible, unavailable = [], []
            for ref_key, slot, _ in possible:
                ref_records = [mapping[ref_key][0] for mapping in row_maps]
                ref_page = ref_records[0].page
                ref_reasons = []
                if any(drawing(locus) for locus in ref_records):
                    ref_reasons.append('reference_inline_drawing_interruption')
                if ref_page not in images:
                    ref_reasons.append('reference_no_unique_exact_single_side_canvas')
                item = {'locus_key': ref_key, 'original_slot_zero_based': slot,
                        'unit_id': units[ref_page]['unit_id']}
                if ref_reasons:
                    unavailable.append({**item, 'reasons': ref_reasons})
                else:
                    eligible.append(item)
            eligible.sort(key=lambda item: (*key_order(item['locus_key']), item['original_slot_zero_based']))
            reference_pools[remainder] = {'eligible_occurrences': eligible, 'excluded_stable_occurrences': unavailable}
        eligible = reference_pools[remainder]['eligible_occurrences']
        if not eligible:
            excluded.append({'locus_key': key, 'unit_id': uid, 'reasons': ['no_qualifying_development_reference'],
                             'reference_form': remainder})
            continue
        candidates.append({'locus_key': key, 'unit_id': uid, 'original_first_form': value,
                           'reference_form': remainder, 'chosen_reference': eligible[0]})
    candidates.sort(key=lambda item: key_order(item['locus_key']))
    chosen, seen = [], set()
    for item in candidates:
        if item['unit_id'] not in seen:
            chosen.append(dict(item))
            seen.add(item['unit_id'])
        if len(chosen) == 2:
            break
    assert {item['locus_key'] for item in candidates + excluded} == set(evaluation_keys)
    return {
        'common_eligible_locations': len(common), 'sorted_common_eligible_keys_sha256': parent.key_digest(common),
        'diagnostic_eligible_locus_count': len(evaluation_keys), 'candidate_count': len(candidates),
        'candidates': candidates, 'excluded_diagnostic_loci': excluded,
        'reference_pools': reference_pools, 'selected_pairs': chosen, 'unfilled_target_units': 2 - len(chosen),
        'stable_development_reference_occurrences': len(stable_references),
        'reference_occurrence_intersection_excludes_source_policy_disagreement': True,
        'images_by_page': {page: images[page] for pair in chosen for page in (
            pair['locus_key'].rsplit('.', 1)[0], pair['chosen_reference']['locus_key'].rsplit('.', 1)[0])},
    }


def verify_inputs():
    record = json.loads((parent.ROOT / BASE / 'inputs.json').read_bytes())
    if record['analysis_id'] != 'y-lookup-image-v1' or record['maximum_target_units'] != 2:
        raise ValueError('image-pair declarations changed')
    for item in record['pins'].values():
        path = parent.ROOT / item['path']
        if not path.resolve().is_relative_to(parent.ROOT.resolve()) or sha(path.read_bytes()) != item['sha256']:
            raise ValueError('image-pair input pin changed')
    return record


def selection_report():
    record = verify_inputs()
    sources, _, _ = parent.load_pins()
    partition = json.loads((parent.ROOT / parent.BASE / 'partition.json').read_bytes())
    if partition != parent.prepare_partition():
        raise ValueError('parent partition changed')
    baseline = json.loads((parent.ROOT / parent.BASE / 'results.json').read_bytes())
    original = parent.analyze(sources, partition)
    if original != {key: baseline[key] for key in original}:
        raise ValueError('parent scientific report changed')
    paired, selected, _ = parent.selection(sources)
    variants = [((metadata['id'], spacing, alternatives), parent.prepare_rows(parent.selected_records(document, selected), spacing, alternatives))
                for metadata, document in paired for spacing in ('split', 'join') for alternatives in ('exclude', 'first')]
    canvas_rows = list(csv.DictReader(io.StringIO((parent.ROOT / 'research/image-index/canvases.csv').read_text())))
    chosen = select_pairs(variants, partition, canvas_rows, set(baseline['selection']['common_evaluation_unit_ids']))
    if (chosen['common_eligible_locations'] != baseline['selection']['common_eligible_locations'] or
            chosen['sorted_common_eligible_keys_sha256'] != baseline['selection']['sorted_common_eligible_keys_sha256']):
        raise ValueError('image-pair eligible cohort differs from parent')
    native_sources = {metadata['id']: document for metadata, document in paired}

    def contexts(key, slot):
        by_source = {}
        for identifier, document in native_sources.items():
            loci = [locus for locus in document.loci if locus.page == key.rsplit('.', 1)[0]]
            position = next(i for i, locus in enumerate(loci) if locus.key == key)

            def native(locus):
                return {'identifier': locus.identifier, 'file_line': locus.line_number, 'text': locus.text}

            by_source[identifier] = {'locus': native(loci[position]),
                                     'preceding': native(loci[position - 1]) if position else None,
                                     'following': native(loci[position + 1]) if position + 1 < len(loci) else None,
                                     'original_slot_zero_based': slot}
        return by_source

    for pair in chosen['selected_pairs']:
        pair['target_native_context'] = contexts(pair['locus_key'], 0)
        reference = pair['chosen_reference']
        pair['reference_native_context'] = contexts(reference['locus_key'], reference['original_slot_zero_based'])
    return {'schema_version': 1, 'analysis_id': 'y-lookup-image-v1', 'status': 'selection_only_before_pixels',
            'input_pins': record['pins'], 'selection': chosen,
            'implementation_sha256': {name: sha((parent.ROOT / name).read_bytes()) for name in (
                'scripts/select_y_lookup_images.py', 'scripts/select_initial_prefix_images.py', 'scripts/ivtff.py',
                'scripts/locus_positions.py', 'scripts/token_baselines.py', 'scripts/audit_transliterations.py')},
            'image_alignment_verified': False, 'source_corrections_applied': False,
            'valid_candidate_holdout': False, 'previously_unseen': False}


def protect_output(output, record):
    parent.protect_output(output, parent.prepare_partition(), parent.ROOT / parent.BASE / 'partition.json')
    protected = [parent.ROOT / item['path'] for item in record['pins'].values()]
    protected += [parent.ROOT / BASE / 'inputs.json', parent.ROOT / BASE / 'PLAN.md', Path(__file__)]
    if any(output.resolve() == path.resolve() or (output.exists() and path.exists() and output.samefile(path)) for path in protected):
        raise ValueError('selection output cannot replace fixed inputs or producer')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        record = verify_inputs()
        if args.output:
            protect_output(args.output, record)
        report = selection_report()
        if args.check and report != json.loads(args.check.read_bytes()):
            raise ValueError('complete frozen selection differs')
        if args.output:
            protect_output(args.output, record)
            args.output.write_text(json.dumps(report, indent=2) + '\n')
        print('Fixed image pairs and full selection accounting verified; no pixel reading performed.')
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'y-lookup image selection failed: {error}\n')


if __name__ == '__main__':
    main()
