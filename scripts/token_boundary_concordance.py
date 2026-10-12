"""Descriptive encoded-chain and token-boundary agreement on one native cohort."""

import argparse
import hashlib
from pathlib import Path
import string

try:
    from .audit_eva_token_coverage import (
        encoded, indexed, load_json, selection_manifest, summarize_outputs,
    )
    from .audit_transliterations import ROOT
    from .eva_token_adapter import build as build_adapter
    from .paragraph_token_corpus import protect_outputs
except ImportError:
    from audit_eva_token_coverage import (
        encoded, indexed, load_json, selection_manifest, summarize_outputs,
    )
    from audit_transliterations import ROOT
    from eva_token_adapter import build as build_adapter
    from paragraph_token_corpus import protect_outputs


SOURCES = ('ZL3b', 'IT2a')
POLICIES = ('split', 'join')
CATEGORIES = ('same_chain_same_boundaries', 'same_chain_different_boundaries',
              'different_chains')
HELPERS = ('token_boundary_concordance.py', 'audit_eva_token_coverage.py',
           'eva_token_adapter.py', 'audit_transliterations.py', 'ivtff.py',
           'token_baselines.py')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def key_set(keys):
    ordered = sorted(keys)
    return {'native_locus_count': len(ordered), 'native_locus_keys': ordered,
            'sorted_native_keys_sha256': digest((''.join(key + '\n' for key in ordered)).encode())}


def representation(tokens):
    """Return literal ASCII chain and offsets between nonempty encoded tokens."""
    if (not isinstance(tokens, list) or not tokens or
            any(not isinstance(token, str) or not token or
                any(char not in string.ascii_letters for char in token) for token in tokens)):
        raise ValueError('need at least one nonempty native ASCII-letter token')
    offsets, position = [], 0
    for token in tokens[:-1]:
        position += len(token)
        offsets.append(position)
    return ''.join(tokens), offsets


def compare(left, right):
    left_chain, left_offsets = representation(left)
    right_chain, right_offsets = representation(right)
    if left_chain != right_chain:
        # Character coordinates are not aligned when the chains differ.
        return {'category': 'different_chains', 'aligned_boundary_difference': None}
    only_left = sorted(set(left_offsets) - set(right_offsets))
    only_right = sorted(set(right_offsets) - set(left_offsets))
    return {
        'category': ('same_chain_different_boundaries' if only_left or only_right
                     else 'same_chain_same_boundaries'),
        'aligned_boundary_difference': {
            'chain_ascii_length': len(left_chain), 'chain_ascii_sha256': digest(left_chain.encode('ascii')),
            'left_token_count': len(left), 'right_token_count': len(right),
            'left_boundary_offsets': left_offsets, 'right_boundary_offsets': right_offsets,
            'only_left_boundary_offsets': only_left, 'only_right_boundary_offsets': only_right,
        },
    }


def contrast(keys, matrices, left, right):
    groups = {category: [] for category in CATEGORIES}
    details = []
    for key in sorted(keys):
        a, b = matrices[left[1]][left[0]][key], matrices[right[1]][right[0]][key]
        result = compare(a['tokens'], b['tokens'])
        groups[result['category']].append(key)
        if result['category'] == 'same_chain_different_boundaries':
            delta = {name: value for name, value in result['aligned_boundary_difference'].items()
                     if name not in ('left_boundary_offsets', 'right_boundary_offsets')}
            details.append({'native_locus_key': key, **delta,
                            'left_identifier': a['locus_identifier'], 'right_identifier': b['locus_identifier'],
                            'left_source_file_line': a['source_line_number'],
                            'right_source_file_line': b['source_line_number'],
                            'left_drawing_interruption_count': a['drawing_interruption_count'],
                            'right_drawing_interruption_count': b['drawing_interruption_count']})
    return {'left': {'source_id': left[0], 'spacing': left[1]},
            'right': {'source_id': right[0], 'spacing': right[1]},
            'category_key_sets': {name: key_set(group) for name, group in groups.items()},
            'boundary_disagreement_loci_with_drawing_interruptions_in_either': sum(
                row['left_drawing_interruption_count'] > 0 or row['right_drawing_interruption_count'] > 0
                for row in details),
            'boundary_disagreements_on_identical_chains': details}


def construct(outputs):
    coverage = summarize_outputs(outputs)
    if (tuple(source['id'] for source in coverage['sources']) != SOURCES or
            coverage['selected_locus_types'] != ['P0']):
        raise ValueError('requires ordered ZL3b/IT2a sources and only P0 loci')
    manifest = selection_manifest(outputs)
    reference = manifest['shared_cohort_key_sets']['eligible_in_every_source_and_policy']
    selected = set(manifest['key_sets'][reference['sorted_native_keys_sha256']])
    matrices = {policy: indexed(outputs[policy]) for policy in POLICIES}
    present = [{key for key, row in matrices['split'][source].items()
                if row['locator'] != '!' and row['locus_type'] == 'P0'} for source in SOURCES]
    candidates = set.intersection(*present)
    if not selected or not selected <= candidates:
        raise ValueError('empty or invalid common eligible cohort')
    excluded = []
    for key in sorted(candidates - selected):
        failures = []
        for source in SOURCES:
            for policy in POLICIES:
                row = matrices[policy][source][key]
                if not row['eligible']:
                    failures.append({'source_id': source, 'spacing': policy,
                                     'reasons': row['exclusion_reasons']})
        excluded.append({'native_locus_key': key, 'source_policy_failures': failures})
    # Comma treatment must preserve every selected source's literal chain.
    for source in SOURCES:
        for key in selected:
            if (representation(matrices['split'][source][key]['tokens'])[0] !=
                    representation(matrices['join'][source][key]['tokens'])[0]):
                raise ValueError('spacing policies unexpectedly change a literal encoded chain')
    cross_source = {policy: contrast(selected, matrices, (SOURCES[0], policy), (SOURCES[1], policy))
                    for policy in POLICIES}
    within_source = {source: contrast(selected, matrices, (source, 'split'), (source, 'join'))
                     for source in SOURCES}
    persistent = set.intersection(*[
        set(cross_source[policy]['category_key_sets']['same_chain_different_boundaries']['native_locus_keys'])
        for policy in POLICIES])
    variants = []
    for source in SOURCES:
        for policy in POLICIES:
            rows = [matrices[policy][source][key] for key in sorted(selected)]
            variants.append({
                'source_id': source, 'spacing': policy, 'native_locus_count': len(rows),
                'token_count': sum(row['token_count'] for row in rows),
                'one_token_loci': key_set(row['locus_key'] for row in rows if row['token_count'] == 1),
                'loci_with_uncertain_spaces': sum(row['uncertain_space_count'] > 0 for row in rows),
                'uncertain_space_count': sum(row['uncertain_space_count'] for row in rows),
                'loci_with_drawing_interruptions': sum(row['drawing_interruption_count'] > 0 for row in rows),
                'drawing_interruption_count': sum(row['drawing_interruption_count'] for row in rows),
            })
    metadata_differences = []
    for key in sorted(selected):
        a, b = (matrices['split'][source][key] for source in SOURCES)
        if a['locator'] != b['locator']:
            metadata_differences.append({'native_locus_key': key,
                                        'ZL3b_identifier': a['locus_identifier'],
                                        'IT2a_identifier': b['locus_identifier']})
    return {
        'schema_version': 1, 'method': 'exploratory literal-chain boundary concordance v1',
        'analysis_unit': 'paired native transcription locus key',
        'processing': {'adapter_version': 'plain-eva-v1', 'selected_locus_types': ['P0'],
                       'cohort_rule': 'eligible in both editions under both comma policies; at least one token',
                       'case': 'preserved', 'drawing_interruptions': 'adapter separators retained and counted',
                       'boundary_unit': 'cumulative ASCII-letter offset in an identical concatenated chain',
                       'different_chain_rule': 'no alignment or boundary-offset comparison',
                       'locator_rule': 'all present P0 locators; differing locators retained explicitly'},
        'sources': coverage['sources'], 'adapter_coverage': coverage,
        'selection': {'candidate_shared_present_p0': key_set(candidates), 'common_eligible': key_set(selected),
                      'excluded_candidate_loci': excluded,
                      'present_p0_only_in_ZL3b': key_set(present[0] - present[1]),
                      'present_p0_only_in_IT2a': key_set(present[1] - present[0])},
        'variants': variants, 'cross_source': cross_source, 'within_source_spacing': within_source,
        'cross_source_boundary_disagreements_under_both_policies': key_set(persistent),
        'cross_source_locator_differences': metadata_differences,
        'limitations': ['exposed-data description; no inferential test or untouched evaluation',
                        'same native key is not verified image-region or physical-line equivalence',
                        'ASCII chain agreement is not glyph, language, phonetic-word, or source-accuracy agreement',
                        'drawing interruption separators are not necessarily manuscript word spaces',
                        'eligibility depends on both editions; excluded loci may systematically differ'],
    }


def build(root=ROOT):
    outputs = {policy: build_adapter(policy, source_ids=SOURCES, kinds=('P0',), root=root)
               for policy in POLICIES}
    report = construct(outputs)
    report['input_sha256'] = {'data/transliterations.json': digest((root / 'data/transliterations.json').read_bytes())}
    report['implementation_sha256'] = {'scripts/' + name: digest((ROOT / 'scripts' / name).read_bytes())
                                       for name in HELPERS}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        protect_outputs([args.output] if args.output else [], root=ROOT)
        report = build()
        if args.check and encoded(load_json(args.check.read_bytes())) != encoded(report):
            raise ValueError('committed concordance report differs from complete pinned replay')
        if args.output:
            args.output.write_bytes(encoded(report))
        elif not args.check:
            print(encoded(report).decode(), end='')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'boundary concordance failed: {error}\n')
    if args.output or args.check:
        print(f"Verified {report['selection']['common_eligible']['native_locus_count']} common eligible P0 loci.")


if __name__ == '__main__':
    main()
