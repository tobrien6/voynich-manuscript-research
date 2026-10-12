"""Freeze source-only within-locus repeat agreements/disagreements for image review."""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re

try:
    from .audit_transliterations import load_sources
    from .token_baselines import paired_sources, retain, tokenize
    from .validate_evaluation_split import load_split_json
except ImportError:
    from audit_transliterations import load_sources
    from token_baselines import paired_sources, retain, tokenize
    from validate_evaluation_split import load_split_json


ROOT = Path(__file__).resolve().parents[1]
PLAN = 'research/transliteration/IMMEDIATE_REPEAT_IMAGE_PLAN.md'
PARENT = 'research/transliteration/repeating_types.json'
INDEX = 'research/image-index/canvases.csv'
ENGINES = ('scripts/select_immediate_repeat_images.py', 'scripts/token_baselines.py',
           'scripts/audit_transliterations.py', 'scripts/ivtff.py',
           'scripts/validate_evaluation_split.py')
VARIANTS = tuple((source, spacing, alternatives) for source in ('ZL3b', 'IT2a')
                 for spacing in ('split', 'join') for alternatives in ('exclude', 'first'))
GROUPS = ('paired_agreement', 'ZL_only', 'IT_only')
PAGE = re.compile(r'f([1-9][0-9]*)([rv])')
REGULAR = frozenset({'@', '+', '*'})


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def key_digest(keys):
    return digest(('\n'.join(sorted(keys)) + '\n').encode())


def key_order(key):
    page, number = key.rsplit('.', 1)
    match = PAGE.fullmatch(page)
    if not match or not number.isdigit() or int(number) < 1:
        raise ValueError('require ordinary numbered-side locus for image selection')
    return int(match[1]), match[2] == 'v', int(number)


def events(slots):
    if not isinstance(slots, (list, tuple)) or any(
            v is not None and (not isinstance(v, str) or not v) for v in slots):
        raise ValueError('require nonempty representations or excluded null slots')
    return [[i, i + 1, slots[i]] for i in range(len(slots) - 1)
            if slots[i] is not None and slots[i] == slots[i + 1]]


def classification(event_rows):
    """Exactly one event/type per positive treatment, stable across its policies."""
    if len(event_rows) != 8:
        raise ValueError('require eight declared event lists in variant order')
    zl, it = event_rows[:4], event_rows[4:]
    def one(rows):
        return all(len(row) == 1 for row in rows) and len({row[0][2] for row in rows}) == 1
    if one(event_rows):
        return 'paired_agreement'
    if one(zl) and all(not row for row in it):
        return 'ZL_only'
    if one(it) and all(not row for row in zl):
        return 'IT_only'
    return None


def select_cases(maps, canvas_rows, shared_keys):
    shared_keys = set(shared_keys)
    if set(maps) != set(VARIANTS) or any(set(mapping) != shared_keys for mapping in maps.values()):
        raise ValueError('require exactly eight complete shared-locus maps')
    images = defaultdict(list)
    for row in canvas_rows:
        if (row['label_class'] == 'exact_single_side_label' and
                row['has_partial_marker'] == 'False' and
                row['has_multiple_explicit_sides'] == 'False' and
                PAGE.fullmatch('f' + row['yale_label'])):
            images['f' + row['yale_label']].append(row)
    excluded, groups, other, repeated, zero = defaultdict(list), {g: [] for g in GROUPS}, [], [], []
    totals = [Counter() for _ in VARIANTS]
    rows = [[] for _ in VARIANTS]
    for key in sorted(shared_keys):
        records = [maps[v][key] for v in VARIANTS]
        page = key.rsplit('.', 1)[0]
        if any(record['locus_key'] != key or record['page'] != page for record in records):
            raise ValueError('native lookup identity mismatch')
        event_rows = [events(record['slots']) for record in records]
        for n, (record, event_row) in enumerate(zip(records, event_rows)):
            totals[n].update(event[2] for event in event_row)
            rows[n].append([key, record['slots']])
        if any(event_rows):
            repeated.append({'locus_key': key, 'events_in_variant_order': event_rows})
        else:
            zero.append(key)
        reasons = set()
        if not PAGE.fullmatch(page):
            reasons.add('unsupported_panel_page')
        if len(images[page]) != 1:
            reasons.add('no_unique_exact_canvas')
        for variant, record in zip(VARIANTS, records):
            label = '/'.join(variant)
            if record['locator'] not in REGULAR:
                reasons.add(label + ':nonregular_locator')
            if len(record['slots']) < 2:
                reasons.add(label + ':fewer_than_two_tokens')
            if any(value is None for value in record['slots']):
                reasons.add(label + ':excluded_token')
        if reasons:
            for reason in sorted(reasons):
                excluded[reason].append(key)
            continue
        group = classification(event_rows)
        if group:
            groups[group].append(key)
        else:
            other.append(key)
    for group in GROUPS:
        groups[group].sort(key=key_order)
    excluded_union = set().union(*(set(keys) for keys in excluded.values())) if excluded else set()
    covered = excluded_union | set(other) | {key for keys in groups.values() for key in keys}
    if covered != shared_keys or len(repeated) + len(zero) != len(shared_keys):
        raise ValueError('incomplete locus accounting')
    return {
        'count': len(shared_keys), 'sorted_locus_keys_sha256': key_digest(shared_keys),
        'variants': [{'source_id': v[0], 'uncertain_spaces': v[1], 'alternatives': v[2],
                      'observed_equal_pair_events': sum(totals[i].values()),
                      'observed_distinct_repeating_types': len(totals[i]),
                      'preprocessed_loci_sha256': digest(json.dumps(rows[i], ensure_ascii=True,
                                                                  separators=(',', ':')).encode('ascii'))}
                     for i, v in enumerate(VARIANTS)],
        'loci_with_any_repeat': repeated, 'zero_repeat_locus_keys': zero,
        'candidate_keys': groups,
        'selected_locus_keys': {group: keys[0] if keys else None for group, keys in groups.items()},
        'unfilled_groups': [group for group, keys in groups.items() if not keys],
        'excluded_union_count': len(excluded_union),
        'exclusions_may_overlap': dict(sorted(excluded.items())),
        'other_eligible_pattern_locus_keys': other,
    }, images


def native(locus):
    return {'locus_key': locus.key, 'locus_identifier': locus.identifier,
            'page': locus.page, 'source_file_line': locus.line_number,
            'locator': locus.locator, 'kind': locus.kind, 'present': locus.present,
            'native_text': locus.text, 'variables': dict(locus.variables)}


def report():
    sources = paired_sources(load_sources(root=ROOT))
    shared = set.intersection(*[{l.key for l in doc.loci if l.present and l.kind == 'P0'}
                               for _, doc in sources])
    if not shared:
        raise ValueError('no shared present P0 loci')
    maps, documents = {}, {}
    for source, document in sources:
        documents[source['id']] = document
        loci = {locus.key: locus for locus in document.loci if locus.key in shared}
        if len(loci) != len(shared):
            raise ValueError('shared source locus mismatch')
        for spacing in ('split', 'join'):
            for alternatives in ('exclude', 'first'):
                maps[source['id'], spacing, alternatives] = {
                    key: {'locus_key': key, 'page': locus.page, 'locator': locus.locator,
                          'slots': [t.value if retain(t, alternatives) else None
                                    for t in tokenize(locus.text, spacing)]}
                    for key, locus in loci.items()}
    index_raw = (ROOT / INDEX).read_bytes()
    audit, images = select_cases(maps, list(csv.DictReader(io.StringIO(index_raw.decode()))), shared)
    parent_raw = (ROOT / PARENT).read_bytes()
    parent = load_split_json(parent_raw.decode())
    if parent['selection'] != {'kind': 'P0', 'count': audit['count'],
                               'sorted_locus_keys_sha256': audit['sorted_locus_keys_sha256']}:
        raise ValueError('accepted repeating-type cohort differs')
    for source, _ in sources:
        matching = [s for s in parent['sources'] if s['id'] == source['id']]
        if len(matching) != 1 or matching[0]['sha256'] != source['sha256']:
            raise ValueError('accepted repeating-type source differs')
    for variant in audit['variants']:
        source = next(s for s in parent['sources'] if s['id'] == variant['source_id'])
        matching = [v for v in source['variants'] if
                    (v['uncertain_spaces'], v['alternatives']) ==
                    (variant['uncertain_spaces'], variant['alternatives'])]
        fields = ('observed_equal_pair_events', 'observed_distinct_repeating_types',
                  'preprocessed_loci_sha256')
        if len(matching) != 1 or any(variant[k] != matching[0][k] for k in fields):
            raise ValueError('accepted repeating-type slots/counts differ')
    selected = []
    for group, key in audit['selected_locus_keys'].items():
        if key is None:
            continue
        page = key.rsplit('.', 1)[0]
        source_records = []
        for source, document in sources:
            page_loci = [l for l in document.loci if l.page == page]
            positions = [i for i, l in enumerate(page_loci) if l.key == key]
            if len(positions) != 1:
                raise ValueError('selected native record is not unique')
            i = positions[0]
            source_records.append({'source_id': source['id'], 'alphabet': document.alphabet,
                                   **native(page_loci[i]),
                                   'preceding_native_record': native(page_loci[i - 1]) if i else None,
                                   'following_native_record': native(page_loci[i + 1]) if i + 1 < len(page_loci) else None})
        image = images[page][0]
        selected.append({'group': group, 'locus_key': key, 'native_source_records': source_records,
                         'variants': [{'source_id': v[0], 'uncertain_spaces': v[1], 'alternatives': v[2],
                                       'slots': maps[v][key]['slots'], 'events': events(maps[v][key]['slots'])}
                                      for v in VARIANTS],
                         'image': {k: image[k] for k in ('yale_label', 'canvas_uri', 'image_oid',
                                   'catalog_image_url', 'full_image_url', 'image_service_url',
                                   'image_width', 'image_height')}})
    return {'schema_version': 1, 'method': 'source-stable within-locus immediate-repeat image selection v1',
            'unit': 'encoded equal adjacent event within native locus; distinct types are separate diagnostics',
            'sources': [{k: source[k] for k in ('id', 'path', 'url', 'sha256')} for source, _ in sources],
            'input_sha256': {PLAN: digest((ROOT / PLAN).read_bytes()), PARENT: digest(parent_raw),
                             INDEX: digest(index_raw), 'data/transliterations.json': digest((ROOT / 'data/transliterations.json').read_bytes()),
                             **{p: digest((ROOT / p).read_bytes()) for p in ENGINES}},
            'audit': audit, 'selected': selected,
            'image_alignment_verified': False, 'source_corrections_applied': False,
            'limits': ['Purposive exposed selection; events and globally distinct types are different units.',
                       'Related editions/policies and shared images are not independent samples.',
                       'Source-only selection does not locate or adjudicate glyphs, words or physical rows.']}


def protect_output(output):
    catalog = ROOT / 'data/transliterations.json'
    inputs = [catalog, ROOT / PLAN, ROOT / PARENT, ROOT / INDEX, *(ROOT / p for p in ENGINES)]
    inputs += [ROOT / source['path'] for source in load_split_json(catalog.read_text())['sources']]
    for path in inputs:
        if output.resolve() == path.resolve() or (output.exists() and path.exists() and output.samefile(path)):
            raise ValueError('output aliases a source, parent, index, plan or engine')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output)
        result = report()
        payload = encoded(result)
        if args.check and payload != encoded(load_split_json(args.check.read_text())):
            raise ValueError('saved immediate-repeat selection differs')
        if args.output:
            protect_output(args.output)
            args.output.write_bytes(payload)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'immediate-repeat selection failed: {error}\n')
    if args.check:
        print('Immediate-repeat candidates, source context and all eight parent counts verified.')


if __name__ == '__main__':
    main()
