"""Trace native separator notation at every fixed-cohort source-only cut."""

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import re
import string
import subprocess

try:
    from .audit_eva_token_coverage import encoded, indexed, load_json
    from .audit_transliterations import ROOT, load_sources
    from .eva_token_adapter import build as build_adapter
    from .ivtff import TAG
    from .paragraph_token_corpus import protect_outputs
    from .token_boundary_concordance import build as build_parent, key_set
except ImportError:
    from audit_eva_token_coverage import encoded, indexed, load_json
    from audit_transliterations import ROOT, load_sources
    from eva_token_adapter import build as build_adapter
    from ivtff import TAG
    from paragraph_token_corpus import protect_outputs
    from token_boundary_concordance import build as build_parent, key_set


PLAN = Path('research/transliteration/BOUNDARY_SEPARATOR_PLAN.json')
PARENT = Path('research/transliteration/token_boundary_concordance.json')
INPUTS = (str(PARENT), 'data/transliterations.json', *(f'scripts/{name}.py' for name in (
    'audit_eva_token_coverage', 'audit_transliterations', 'eva_token_adapter',
    'ivtff', 'paragraph_token_corpus', 'token_baselines', 'token_boundary_concordance')))
MARKERS = ('.', ',', '<->', '<~>')
SOURCES = ('ZL3b', 'IT2a')
POLICIES = ('split', 'join')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def trace(text):
    """Read only the accepted plain-letter grammar; preserve raw marker ranges."""
    require(isinstance(text, str), 'need literal source text')
    letters, letter_positions, events = [], [], []
    pending, index = False, 0
    while index < len(text):
        start, char = index, text[index]
        if char in string.ascii_letters:
            letters.append(char)
            letter_positions.append(index)
            pending, index = False, index + 1
            continue
        if char.isspace():
            index += 1
            continue
        if char == '<':
            end = text.find('>', index + 1)
            require(end >= 0, 'unclosed native annotation')
            marker = text[index:end + 1]
            index = end + 1
            if marker.startswith('<!') or marker in ('<%>', '<$>') or TAG.fullmatch(marker):
                continue
            require(marker in ('<->', '<~>'), 'unsupported native annotation')
        else:
            require(char in '.,', 'non-plain native notation')
            marker, index = char, index + 1
        require(letters and not pending, 'leading or consecutive native separators')
        events.append({'ascii_offset': len(letters), 'native_marker': marker,
                       'raw_locus_start': start, 'raw_locus_end_exclusive': index})
        pending = True
    require(letters and not pending, 'empty text or trailing native separator')
    return {'chain': ''.join(letters), 'letter_raw_positions': letter_positions,
            'events': events, 'raw_locus_sha256': sha(text.encode('ascii'))}


def tokens(traced, policy):
    require(policy in POLICIES, 'unknown comma policy')
    cuts = [event['ascii_offset'] for event in traced['events']
            if policy == 'split' or event['native_marker'] != ',']
    anchors = [0, *cuts, len(traced['chain'])]
    return [traced['chain'][start:end] for start, end in zip(anchors, anchors[1:])]


def endpoint(traced, offset):
    """A missing source separator remains explicit; ignored annotations add no cut."""
    require(0 < offset < len(traced['chain']), 'require an internal encoded offset')
    matches = [event for event in traced['events'] if event['ascii_offset'] == offset]
    require(len(matches) <= 1, 'duplicate native separator at encoded offset')
    event = matches[0] if matches else None
    return {'native_marker': event['native_marker'] if event else None,
            'raw_locus_separator_range': ([event['raw_locus_start'], event['raw_locus_end_exclusive']]
                                          if event else None),
            'neighbor_letter_raw_positions': [traced['letter_raw_positions'][offset - 1],
                                              traced['letter_raw_positions'][offset]],
            'cut_by_policy': {'split': event is not None,
                              'join': event is not None and event['native_marker'] != ','}}


def differences(left, right):
    require(left['chain'] == right['chain'], 'different chains must not be aligned')
    offsets = sorted({event['ascii_offset'] for row in (left, right) for event in row['events']})
    rows = []
    for offset in offsets:
        a, b = endpoint(left, offset), endpoint(right, offset)
        policies = [policy for policy in POLICIES if a['cut_by_policy'][policy] != b['cut_by_policy'][policy]]
        if policies:
            rows.append({'ascii_offset': offset, 'left': a, 'right': b,
                         'disagreement_policies': policies})
    return rows


def pinned_inputs(root=ROOT):
    raw = (root / PLAN).read_bytes()
    plan = load_json(raw)
    require(type(plan['schema_version']) is int and plan['schema_version'] == 1
            and plan['analysis_id'] == 'modern-boundary-separator-provenance-v1',
            'unsupported separator plan')
    commit = plan['base_commit']
    require(isinstance(commit, str) and re.fullmatch('[0-9a-f]{40}', commit), 'need an exact plan base commit')
    require(plan['sources'] == list(SOURCES) and set(plan['markers']) == set(MARKERS), 'source/marker plan changed')
    require(set(plan['input_sha256']) == set(INPUTS) and plan['parent_report'] == str(PARENT)
            and set(plan['source_file_sha256']) == set(SOURCES), 'frozen input set changed')
    for path, expected in plan['input_sha256'].items():
        current = (root / path).read_bytes()
        require(sha(current) == expected, 'frozen separator input changed: ' + path)
        require(subprocess.check_output(['git', 'show', commit + ':' + path], cwd=root) == current,
                'frozen input Git blob differs: ' + path)
    parent = load_json((root / plan['parent_report']).read_bytes())
    require(encoded(parent) == encoded(build_parent(root=root)), 'complete accepted concordance replay differs')
    return raw, plan, parent


def build(root=ROOT):
    plan_raw, plan, parent = pinned_inputs(root)
    selected = parent['selection']['common_eligible']['native_locus_keys']
    matrices = {policy: indexed(build_adapter(policy, source_ids=SOURCES, kinds=('P0',), root=root))
                for policy in POLICIES}
    documents = {source['id']: (source, document) for source, document in load_sources(root)}
    traced, identities = {source: {} for source in SOURCES}, {source: {} for source in SOURCES}
    source_totals = {}
    for source in SOURCES:
        metadata, document = documents[source]
        require(metadata['sha256'] == plan['source_file_sha256'][source], 'native source pin changed')
        require(subprocess.check_output(['git', 'show', plan['base_commit'] + ':' + metadata['path']], cwd=root)
                == (root / metadata['path']).read_bytes(), 'native source Git blob differs')
        loci = {locus.key: locus for locus in document.loci}
        require(len(loci) == len(document.loci), 'duplicate native source keys')
        counts = Counter({marker: 0 for marker in MARKERS})
        for key in selected:
            locus, reference = loci[key], matrices['split'][source][key]
            require(locus.present and locus.kind == 'P0' and reference['eligible'], 'selected native record changed')
            row = trace(locus.text)
            for policy in POLICIES:
                require(tokens(row, policy) == matrices[policy][source][key]['tokens'],
                        'native punctuation replay differs: ' + source + '/' + policy + '/' + key)
            local = Counter(event['native_marker'] for event in row['events'])
            require(local[','] == reference['uncertain_space_count'] and
                    local['<->'] + local['<~>'] == reference['drawing_interruption_count'],
                    'whole-locus annotation count differs')
            counts.update(local)
            traced[source][key] = row
            identities[source][key] = {'locus_identifier': locus.identifier,
                                        'source_file_first_line': locus.line_number,
                                        'raw_locus_text_sha256': row['raw_locus_sha256']}
        source_totals[source] = dict(counts)
    records, aligned, different = [], [], []
    totals = {policy: {source: Counter({marker: 0 for marker in MARKERS}) for source in SOURCES}
              for policy in POLICIES}
    keys_by_policy = {policy: set() for policy in POLICIES}
    for key in selected:
        a, b = (traced[source][key] for source in SOURCES)
        if a['chain'] != b['chain']:
            different.append(key)
            continue
        aligned.append(key)
        offsets = differences(a, b)
        if not offsets:
            continue
        records.append({'native_locus_key': key, 'chain_ascii_length': len(a['chain']),
                        'chain_ascii_sha256': sha(a['chain'].encode('ascii')),
                        'ZL3b': identities['ZL3b'][key], 'IT2a': identities['IT2a'][key],
                        'offset_records': offsets})
        for row in offsets:
            for policy in row['disagreement_policies']:
                keys_by_policy[policy].add(key)
                for side, source in (('left', 'ZL3b'), ('right', 'IT2a')):
                    if row[side]['cut_by_policy'][policy]:
                        totals[policy][source][row[side]['native_marker']] += 1
    for policy in POLICIES:
        comparison = parent['cross_source'][policy]
        expected = comparison['boundary_disagreements_on_identical_chains']
        require(keys_by_policy[policy] == {row['native_locus_key'] for row in expected}, 'disagreement key set differs')
        for side, source in (('left', 'ZL3b'), ('right', 'IT2a')):
            require(sum(totals[policy][source].values()) == sum(len(row['only_' + side + '_boundary_offsets'])
                                                             for row in expected), 'exclusive cut total differs')
    return {'schema_version': 1, 'analysis_id': plan['analysis_id'],
            'plan_sha256': sha(plan_raw), 'input_sha256': plan['input_sha256'],
            'producer_sha256': sha(Path(__file__).read_bytes()), 'base_commit': plan['base_commit'],
            'sources': parent['sources'], 'selected': key_set(selected),
            'same_chain': key_set(aligned), 'different_chain_unaligned': key_set(different),
            'source_internal_validation': {'native_records': len(selected) * len(SOURCES),
                                           'source_policy_token_arrays': len(selected) * len(SOURCES) * len(POLICIES),
                                           'marker_counts': source_totals},
            'disagreement_native_loci': {policy: key_set(keys_by_policy[policy]) for policy in POLICIES},
            'exclusive_cut_marker_counts': {policy: {source: dict(counter) for source, counter in by_source.items()}
                                            for policy, by_source in totals.items()},
            'union_disagreement_locus_count': len(records),
            'union_disagreement_offset_count': sum(len(row['offset_records']) for row in records),
            'records': records, 'raw_coordinates': plan['raw_coordinates'],
            'verified_glyph_regions': False, 'source_corrections_applied': False,
            'limits': plan['limits'], 'exposure': plan['exposure']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        reads = [ROOT / PLAN, *(ROOT / path for path in INPUTS), *([args.check] if args.check else [])]
        protect_outputs([args.output] if args.output else [], reads, root=ROOT)
        report = build()
        rendered = encoded(report)
        if args.check:
            require(args.check.read_bytes() == rendered, 'complete separator report differs')
        if args.output:
            protect_outputs([args.output], reads, root=ROOT)
            args.output.write_bytes(rendered)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'separator provenance failed: {error}\n')
    print('Verified all common source/policy token arrays and complete encoded-separator report.')


if __name__ == '__main__':
    main()
