"""Select reproducible, conservative q/y-prefix disagreements for image review.

This performs source selection only. It neither locates glyphs in images nor
adjudicates either transcription. See INITIAL_PREFIX_IMAGE_PLAN.md.
"""

import argparse
from collections import defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re

try:
    from .audit_transliterations import ROOT, load_sources
    from .eva_token_adapter import adapt
    from .token_baselines import paired_sources
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from eva_token_adapter import adapt
    from token_baselines import paired_sources


VARIANTS = tuple((source, spacing) for source in ('ZL3b', 'IT2a')
                 for spacing in ('split', 'join'))
PAGE = re.compile(r'f([1-9][0-9]*)([rv])')
REGULAR = frozenset({'@', '+', '*'})


def key_order(key):
    page, number = key.rsplit('.', 1)
    match = PAGE.fullmatch(page)
    if not match or not number.isdigit():
        raise ValueError(f'not an ordinary numbered-side locus: {key}')
    return int(match[1]), match[2] == 'v', int(number)


def digest(keys):
    return hashlib.sha256(('\n'.join(keys) + '\n').encode()).hexdigest()


def select_cases(maps, canvas_rows, shared_keys, maximum=3):
    if maximum < 1 or set(maps) != set(VARIANTS):
        raise ValueError('require a positive maximum and exactly the four declared variants')
    images = defaultdict(list)
    for row in canvas_rows:
        if (row['label_class'] == 'exact_single_side_label' and
                row['has_partial_marker'] == 'False' and
                row['has_multiple_explicit_sides'] == 'False' and
                PAGE.fullmatch('f' + row['yale_label'])):
            images['f' + row['yale_label']].append(row)
    excluded = defaultdict(list)
    candidates = []
    for key in sorted(shared_keys):
        if any(key not in maps[variant] for variant in VARIANTS):
            raise ValueError(f'missing declared shared location: {key}')
        records = [maps[variant][key] for variant in VARIANTS]
        if any(record['locus_key'] != key for record in records):
            raise ValueError(f'record identity differs from lookup key: {key}')
        pages = {record['page_id'] for record in records}
        if len(pages) != 1 or key.rsplit('.', 1)[0] not in pages:
            raise ValueError(f'paired page identities differ: {key}')
        reasons = []
        for variant, record in zip(VARIANTS, records):
            label = '/'.join(variant)
            if not record['eligible']:
                reasons.append(label + ':whole_locus_excluded')
            elif record['token_count'] < 2:
                reasons.append(label + ':fewer_than_two_tokens')
            if record['locator'] not in REGULAR:
                reasons.append(label + ':nonregular_locator')
        if reasons:
            for reason in reasons:
                excluded[reason].append(key)
            continue
        page = records[0]['page_id']
        if len(images[page]) != 1:
            excluded['no_unique_exact_canvas'].append(key)
            continue
        masks = []
        for spacing in ('split', 'join'):
            first = [maps[source, spacing][key]['tokens'][0]
                     for source in ('ZL3b', 'IT2a')]
            masks.append([prefix for prefix in ('q', 'y')
                          if first[0].startswith(prefix) != first[1].startswith(prefix)])
        if masks[0] != masks[1]:
            excluded['spacing_dependent_disagreement'].append(key)
            continue
        if not masks[0]:
            excluded['prefix_features_agree'].append(key)
            continue
        # Fail rather than choosing a lexical order if the declared numeric
        # sorting rule is unsupported by a candidate identifier.
        key_order(key)
        image = images[page][0]
        candidates.append({
            'locus_key': key, 'page_id': page, 'discordant_features': masks[0],
            'variants': [{
                'source_id': source, 'uncertain_spaces': spacing,
                'locus_identifier': maps[source, spacing][key]['locus_identifier'],
                'source_line_number': maps[source, spacing][key]['source_line_number'],
                'first_token': maps[source, spacing][key]['tokens'][0],
                'token_count': maps[source, spacing][key]['token_count'],
            } for source, spacing in VARIANTS],
            'image': {name: image[name] for name in (
                'yale_label', 'canvas_uri', 'image_oid', 'catalog_image_url',
                'full_image_url', 'image_service_url', 'image_width', 'image_height')},
        })
    candidates.sort(key=lambda case: key_order(case['locus_key']))
    selected, seen_pages = [], set()
    for case in candidates:
        if case['page_id'] not in seen_pages:
            selected.append(case['locus_key'])
            seen_pages.add(case['page_id'])
        if len(selected) == maximum:
            break
    excluded_union = set().union(*map(set, excluded.values())) if excluded else set()
    assert excluded_union | {case['locus_key'] for case in candidates} == set(shared_keys)
    return {
        'shared_present_p0_count': len(shared_keys),
        'sorted_shared_keys_sha256': digest(sorted(shared_keys)),
        'exclusions_may_overlap': {reason: {'count': len(keys), 'locus_keys': keys}
                                  for reason, keys in sorted(excluded.items())},
        'excluded_union_count': len(excluded_union),
        'candidate_count': len(candidates), 'candidates': candidates,
        'maximum_distinct_sides': maximum, 'selected_locus_keys': selected,
        'selected_keys_sha256': digest(selected),
        'unfilled_review_slots': maximum - len(selected),
    }


def selection_report(root=ROOT):
    sources = paired_sources(load_sources(root))
    common = set.intersection(*[
        {locus.key for locus in document.loci if locus.present and locus.kind == 'P0'}
        for _, document in sources])
    maps = {}
    for source, document in sources:
        for spacing in ('split', 'join'):
            records = adapt(source, document, spacing, ('P0',))
            mapping = {record['locus_key']: record for record in records}
            if len(mapping) != len(records):
                raise ValueError('duplicate adapter locus key')
            maps[source['id'], spacing] = mapping
    index_path = root / 'research/image-index/canvases.csv'
    index = index_path.read_bytes()
    canvas_rows = list(csv.DictReader(io.StringIO(index.decode('utf-8'))))
    return {
        'schema_version': 1, 'method': 'initial-prefix image selection v1',
        'adapter_version': 'plain-eva-v1', 'analysis_unit': 'transcription_locus',
        'sources': [{name: source[name] for name in ('id', 'sha256', 'url', 'path')}
                    for source, _ in sources],
        'canvas_index_path': 'research/image-index/canvases.csv',
        'canvas_index_sha256': hashlib.sha256(index).hexdigest(),
        'implementation_sha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                                  for name in (
                                      'scripts/select_initial_prefix_images.py',
                                      'scripts/eva_token_adapter.py', 'scripts/ivtff.py',
                                      'scripts/token_baselines.py', 'scripts/audit_transliterations.py')},
        'selection': select_cases(maps, canvas_rows, common),
        'image_alignment_verified': False, 'source_corrections_applied': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        report = selection_report()
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed image-review selection differs from recomputation')
        if args.output:
            args.output.write_text(json.dumps(report, indent=2) + '\n')
    except (ValueError, OSError) as error:
        parser.exit(1, f'initial-prefix selection failed: {error}\n')
    if args.check:
        print('Pinned sources and committed image-review selection verified.')
    elif not args.output:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
