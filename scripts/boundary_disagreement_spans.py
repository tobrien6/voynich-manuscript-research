"""Extract encoded disagreement spans between consecutive shared boundaries."""

import argparse
from collections import Counter
import hashlib
from pathlib import Path

try:
    from .audit_eva_token_coverage import encoded, indexed, load_json
    from .audit_transliterations import ROOT
    from .eva_token_adapter import build as build_adapter
    from .paragraph_token_corpus import protect_outputs
    from .token_boundary_concordance import build as build_parent, key_set, representation
except ImportError:
    from audit_eva_token_coverage import encoded, indexed, load_json
    from audit_transliterations import ROOT
    from eva_token_adapter import build as build_adapter
    from paragraph_token_corpus import protect_outputs
    from token_boundary_concordance import build as build_parent, key_set, representation


PARENT = Path('research/transliteration/token_boundary_concordance.json')
SOURCES = ('ZL3b', 'IT2a')
POLICIES = ('split', 'join')
HELPERS = ('boundary_disagreement_spans.py', 'token_boundary_concordance.py',
           'audit_eva_token_coverage.py', 'audit_transliterations.py',
           'eva_token_adapter.py', 'token_baselines.py', 'ivtff.py')


def spans(left_tokens, right_tokens):
    left_chain, left_offsets = representation(left_tokens)
    right_chain, right_offsets = representation(right_tokens)
    if left_chain != right_chain:
        raise ValueError('different encoded chains cannot supply aligned spans')
    left, right = set(left_offsets), set(right_offsets)
    anchors = sorted({0, len(left_chain)} | (left & right))
    result = []
    for start, end in zip(anchors, anchors[1:]):
        a = sorted(offset for offset in left if start < offset < end)
        b = sorted(offset for offset in right if start < offset < end)
        if a == b:
            continue
        # Every common internal boundary is already an anchor, so these cuts
        # are exclusive to one source. Endpoints belong to both partitions.
        if set(a) & set(b):
            raise ValueError('shared internal cut escaped the anchor partition')
        left_edges, right_edges = [start, *a, end], [start, *b, end]
        left_parts = [left_chain[x:y] for x, y in zip(left_edges, left_edges[1:])]
        right_parts = [left_chain[x:y] for x, y in zip(right_edges, right_edges[1:])]
        result.append({
            'start_ascii_offset': start, 'end_ascii_offset_exclusive': end,
            'span_ascii': left_chain[start:end], 'span_ascii_length': end - start,
            'left_original_token_parts': left_parts, 'right_original_token_parts': right_parts,
            'left_only_internal_ascii_offsets': a, 'right_only_internal_ascii_offsets': b,
            'left_minus_right_native_token_count': len(left_parts) - len(right_parts),
            'category': ('left_only_internal_cuts' if a and not b else
                         'right_only_internal_cuts' if b and not a else 'both_sources_internal_cuts'),
        })
    # No unmatched offset may be lost or repeated across emitted spans.
    if ({x for row in result for x in row['left_only_internal_ascii_offsets']} != left - right or
            {x for row in result for x in row['right_only_internal_ascii_offsets']} != right - left):
        raise ValueError('span partition lost an encoded boundary difference')
    if sum(row['left_minus_right_native_token_count'] for row in result) != len(left_tokens) - len(right_tokens):
        raise ValueError('span token deltas do not account for source count difference')
    return result


def build(root=ROOT):
    parent_raw = (root / PARENT).read_bytes()
    parent = load_json(parent_raw)
    if encoded(parent) != encoded(build_parent(root=root)):
        raise ValueError('accepted parent differs from complete source/implementation replay')
    selected = parent['selection']['common_eligible']['native_locus_keys']
    comparisons = []
    for policy in POLICIES:
        output = build_adapter(policy, source_ids=SOURCES, kinds=('P0',), root=root)
        records = indexed(output)
        shared_chains, different_chains, rows = [], [], []
        locus_counts = Counter()
        for key in selected:
            left, right = (records[source][key] for source in SOURCES)
            a, _ = representation(left['tokens'])
            b, _ = representation(right['tokens'])
            if a != b:
                different_chains.append(key)
                continue
            shared_chains.append(key)
            local = spans(left['tokens'], right['tokens'])
            if not local:
                continue
            locus_counts[key] = len(local)
            for index, span in enumerate(local):
                rows.append({
                    'native_locus_key': key, 'span_index_within_locus_zero_based': index,
                    **span, 'left_source_id': SOURCES[0], 'right_source_id': SOURCES[1],
                    'left_locus_identifier': left['locus_identifier'], 'right_locus_identifier': right['locus_identifier'],
                    'left_source_file_line': left['source_line_number'], 'right_source_file_line': right['source_line_number'],
                    'left_uncertain_space_count_in_locus': left['uncertain_space_count'],
                    'right_uncertain_space_count_in_locus': right['uncertain_space_count'],
                    'left_drawing_interruption_count_in_locus': left['drawing_interruption_count'],
                    'right_drawing_interruption_count_in_locus': right['drawing_interruption_count'],
                    'separator_types_within_span': None, 'verified_glyph_region': None,
                })
        expected = parent['cross_source'][policy]['category_key_sets']
        if (different_chains != expected['different_chains']['native_locus_keys'] or
                sorted(locus_counts) != expected['same_chain_different_boundaries']['native_locus_keys']):
            raise ValueError('span coverage differs from accepted category identities')
        comparisons.append({
            'spacing': policy, 'same_chain_loci': key_set(shared_chains),
            'different_chain_loci_not_aligned': key_set(different_chains),
            'disagreement_loci': key_set(locus_counts), 'span_count': len(rows),
            'span_counts_by_category': dict(sorted(Counter(row['category'] for row in rows).items())),
            'disagreement_loci_by_span_count': {str(count): number for count, number in sorted(Counter(locus_counts.values()).items())},
            'net_left_minus_right_native_tokens_on_same_chains': sum(row['left_minus_right_native_token_count'] for row in rows),
            'span_records': rows,
        })
    return {
        'schema_version': 1, 'method': 'minimal shared-anchor encoded boundary spans v1',
        'analysis_unit': 'encoded interval between shared offsets within one native locus',
        'parent_report_path': str(PARENT), 'parent_report_sha256': hashlib.sha256(parent_raw).hexdigest(),
        'parent_selection': parent['selection']['common_eligible'], 'sources': parent['sources'],
        'implementation_sha256': {'scripts/' + name: hashlib.sha256((ROOT / 'scripts' / name).read_bytes()).hexdigest()
                                  for name in HELPERS},
        'processing': {'adapter_version': 'plain-eva-v1', 'case': 'preserved',
                       'anchor_rule': 'consecutive shared internal ASCII offsets plus common locus endpoints',
                       'different_chain_rule': 'excluded from alignment, with all native keys retained',
                       'part_rule': 'original complete tokens between shared anchors; no partial-token cuts',
                       'separator_scope': 'all adapter separators; locus drawing/comma counts retained, span-specific types unresolved'},
        'comparisons': comparisons,
        'limitations': ['encoded intervals are not pixel masks, manuscript glyphs or linguistic word spans',
                        'locus-level drawing/comma counts do not locate those markers inside a span',
                        'related exposed sources/policies/spans are not independent samples or untouched evaluation'],
        'source_corrections_applied': False, 'usable_as_verified_corpus_join': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        targets = [args.output] if args.output else []
        reads = [ROOT / PARENT, *([args.check] if args.check else [])]
        protect_outputs(targets, reads, root=ROOT)
        report = build()
        rendered = encoded(report)
        if args.check and encoded(load_json(args.check.read_bytes())) != rendered:
            raise ValueError('committed span inventory differs from complete fresh replay')
        if args.output:
            protect_outputs(targets, reads, root=ROOT)
            args.output.write_bytes(rendered)
        elif not args.check:
            print(rendered.decode(), end='')
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f'boundary spans failed: {error}\n')
    if args.output or args.check:
        print('Verified minimal spans on both source/spacing comparisons.')


if __name__ == '__main__':
    main()
