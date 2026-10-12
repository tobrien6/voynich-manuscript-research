"""Retain the complete native non-paragraph f68r3 packet without assigning glyphs."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

try:
    from .audit_transliterations import ROOT, load_sources
except ImportError:
    from audit_transliterations import ROOT, load_sources


PAGE = 'f68r3'
KEYS = [f'{PAGE}.{number}' for number in range(1, 23)]
KINDS = {number: ('Cc' if number in (1, 22) else 'Ri' if 2 <= number <= 9
                  else 'La' if number == 12 else 'Ls') for number in range(1, 23)}
LOCATORS = {number: ('+' if number in (16, 17, 19) else '=' if number in (14, 20)
                     else '*' if number == 21 else '@') for number in range(1, 23)}
ANCHORS = [f'{PAGE}.2', f'{PAGE}.9']
PLAN = 'research/panel-regions/F68R3_NONPARAGRAPH_PLAN.md'
INPUTS = [PLAN, 'data/transliterations.json', 'research/panel-regions/f68r-proposal.json',
          'research/panel-regions/f68r-p0-review.json', 'research/pilot/native-page-conventions.json']


def collect(sources):
    selected = [(source, document) for source, document in sources if source['id'] in ('ZL3b', 'IT2a')]
    if Counter(source['id'] for source, _ in selected) != Counter(('ZL3b', 'IT2a')):
        raise ValueError('require exactly both pinned editions')
    selected.sort(key=lambda pair: ('ZL3b', 'IT2a').index(pair[0]['id']))
    records, page_audit, by_source = [], [], {}
    for source, document in selected:
        if PAGE not in document.pages:
            raise ValueError('required native page header is absent')
        loci = [locus for locus in document.loci if locus.page == PAGE]
        if [locus.key for locus in loci] != KEYS or any(not locus.present for locus in loci):
            raise ValueError('complete ordered present native key set differs')
        if any(locus.kind != KINDS[locus.number] or locus.locator != LOCATORS[locus.number] for locus in loci):
            raise ValueError('native kind or relative locator differs from frozen scope')
        by_source[source['id']] = loci
        page_audit.append({'source_id': source['id'], 'header_present': True, 'present_locations': len(loci),
                           'present_by_kind': dict(sorted(Counter(locus.kind for locus in loci).items())),
                           'present_p0_locations': [], 'native_locator_counts': dict(sorted(Counter(locus.locator for locus in loci).items()))})
    for index, key in enumerate(KEYS):
        readings = []
        for source, _ in selected:
            locus = by_source[source['id']][index]
            readings.append({'source_id': source['id'], 'locus_identifier': locus.identifier,
                             'source_file_line': locus.line_number, 'native_text': locus.text})
        records.append({'locus_key': key, 'native_kind': KINDS[index + 1], 'native_locator': LOCATORS[index + 1],
                        'selected_anchor_attempt': key in ANCHORS, 'image_glyph_verification': 'pending',
                        'readings': readings, 'native_record_text_identical': readings[0]['native_text'] == readings[1]['native_text']})
    return {'sources': [{'source_id': source['id'], 'sha256': source['sha256'], 'alphabet': source['alphabet'],
                         'url': source['url'], 'path': source['path']} for source, _ in selected],
            'page_audit': page_audit, 'records': records, 'locations': len(records),
            'identical_native_record_text': sum(row['native_record_text_identical'] for row in records),
            'different_native_record_text': sum(not row['native_record_text_identical'] for row in records)}


def build(root=ROOT):
    result = collect(load_sources(root))
    proposal = json.loads((root / 'research/panel-regions/f68r-proposal.json').read_bytes())
    if (proposal['image_oid'] != '1006196' or proposal['yale_label'] != '68r' or
            proposal['dependency_group'] != 'yale-leaves:68'):
        raise ValueError('parent carrier/dependency identity differs')
    return {'schema_version': 1, 'method': 'complete f68r3 non-paragraph review packet v1',
            'plan': PLAN, 'input_pins': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in INPUTS},
            'shared_reader_sha256': hashlib.sha256((root / 'scripts/ivtff.py').read_bytes()).hexdigest(),
            'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'page': PAGE, 'anchor_attempts': ANCHORS, 'selection': 'all native locations plus first/last Ri by source order',
            'canvas_uri': proposal['canvas_uri'], 'image_oid': proposal['image_oid'],
            'dependency_group': proposal['dependency_group'], 'usable_as_verified_corpus_join': False,
            'normalization': 'none; preserve native reader text, annotations, alphabets, kinds and locators',
            'source_file_line_scope': 'physical source-file line; not a physical manuscript line',
            'scope': 'source packet only; source categories/equality do not verify image placement, glyphs or word boundaries',
            **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group(required=True)
    options.add_argument('--new-output', type=Path)
    options.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        result = build()
        raw = (json.dumps(result, indent=2, ensure_ascii=False) + '\n').encode()
        if args.check:
            if args.check.read_bytes() != raw:
                raise ValueError('committed packet differs from complete source reconstruction')
        else:
            with args.new_output.open('xb') as stream:
                stream.write(raw)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'f68r3 packet failed: {error}\n')
    print('Verified all 22 non-paragraph locations, eight radial records and two fixed anchor attempts.')


if __name__ == '__main__':
    main()
