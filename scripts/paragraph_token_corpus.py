"""Build and replay conservative tokens for exact common encoded paragraphs."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

try:
    from .audit_eva_token_coverage import encoded, load_json, IDENTITY_FIELDS
    from .audit_transliterations import ROOT, load_sources
    from .eva_token_adapter import adapt
    from .paragraph_membership import membership_report
    from .token_baselines import paired_sources
    from .write_eva_token_cache import protect_output as protect_source_output
except ImportError:
    from audit_eva_token_coverage import encoded, load_json, IDENTITY_FIELDS
    from audit_transliterations import ROOT, load_sources
    from eva_token_adapter import adapt
    from paragraph_membership import membership_report
    from token_baselines import paired_sources
    from write_eva_token_cache import protect_output as protect_source_output


POLICIES = ('split', 'join')
PRODUCER = 'common-encoded-paragraph-eva-v1'
MEMBERSHIP_PATH = Path('research/transliteration/paragraph_membership.json')
PLAN_PATH = Path('research/transliteration/PARAGRAPH_CORPUS_PLAN.md')
HELPERS = (
    'paragraph_token_corpus.py', 'paragraph_membership.py', 'annotation_agreement.py',
    'eva_token_adapter.py', 'token_baselines.py', 'ivtff.py',
    'audit_transliterations.py', 'audit_eva_token_coverage.py',
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    value = load_json(raw)
    encoded(value)  # Reject NaN/Infinity and retain numeric/Boolean type distinctions.
    return value


def construct(sources, membership, inputs):
    paired = paired_sources(sources)
    if encoded(membership) != encoded(membership_report(paired)):
        raise ValueError('membership report differs from a complete pinned-source replay')
    unit_maps = {
        source['id']: {unit['id']: unit for page in source['pages'] for unit in page['units']}
        for source in membership['sources']
    }
    kinds = sorted({locus.kind for _, document in paired for locus in document.loci
                    if locus.present and locus.kind.startswith('P')})
    adapted = {}
    for source, document in paired:
        for policy in POLICIES:
            records = adapt(source, document, policy, kinds=kinds)
            mapping = {record['locus_key']: record for record in records}
            if len(mapping) != len(records):
                raise ValueError('adapter records have duplicate locus keys')
            adapted[source['id'], policy] = mapping
    paragraphs = []
    for match in membership['exact_unit_comparison']['matches']:
        left_id, right_id = match['left_unit_id'], match['right_unit_id']
        left = unit_maps[paired[0][0]['id']][left_id]
        right = unit_maps[paired[1][0]['id']][right_id]
        keys = left['member_keys']
        if keys != right['member_keys'] or left['ordered_member_keys_sha256'] != right['ordered_member_keys_sha256']:
            raise ValueError('exact unit match has inconsistent ordered membership')
        variants = []
        for source, _ in paired:
            for policy in POLICIES:
                rows = [adapted[source['id'], policy][key] for key in keys]
                local = all(row['eligible'] for row in rows)
                failures = [{'locus_key': row['locus_key'],
                             'exclusion_reasons': row['exclusion_reasons']}
                            for row in rows if not row['eligible']]
                variants.append({'source_id': source['id'], 'uncertain_spaces': policy,
                                 'locally_eligible': local, 'failed_loci': failures,
                                 'loci': [{**{field: row[field] for field in IDENTITY_FIELDS},
                                           'adapter_eligible': row['eligible'],
                                           'exclusion_reasons': row['exclusion_reasons'],
                                           'uncertain_space_count': row['uncertain_space_count'],
                                           'drawing_interruption_count': row['drawing_interruption_count'],
                                           'tokens': row['tokens'], 'token_count': row['token_count']}
                                          for row in rows]})
        common = all(variant['locally_eligible'] for variant in variants)
        for variant in variants:
            if not common:
                for row in variant['loci']:
                    row['tokens'] = None
                    row['token_count'] = None
            variant['common_corpus_token_count'] = (
                sum(row['token_count'] for row in variant['loci']) if common else None)
        paragraphs.append({
            'common_unit_id': 'paragraph:' + left['ordered_member_keys_sha256'],
            'page_id': left['page'], 'member_keys': keys,
            'ordered_member_keys_sha256': left['ordered_member_keys_sha256'],
            'source_unit_ids': {paired[0][0]['id']: left_id, paired[1][0]['id']: right_id},
            'common_eligible': common, 'variants': variants,
        })
    if len({row['common_unit_id'] for row in paragraphs}) != len(paragraphs):
        raise ValueError('candidate paragraph identity is duplicated')
    common = [row for row in paragraphs if row['common_eligible']]
    return {
        'schema_version': 1, 'producer_version': PRODUCER,
        'analysis_unit': 'source_defined_encoded_paragraph', 'inputs': inputs,
        'sources': [{key: source[key] for key in ('id', 'url', 'path', 'sha256', 'alphabet')}
                    for source, _ in paired],
        'processing': {
            'uncertain_space_policies': list(POLICIES), 'selected_locus_types': kinds,
            'token_representation': 'native Eva ASCII letters; case preserved',
            'eligibility': 'every member adapter-eligible in both sources and both policies',
            'excluded_candidate_tokens': 'null for all loci and all variants',
            'row_boundaries': 'retain original loci and locators; no concatenation across loci',
            'minimum_token_count_filter': None,
        },
        'cohort': {
            'candidate_units': len(paragraphs), 'common_eligible_units': len(common),
            'excluded_candidate_units': len(paragraphs) - len(common),
            'candidate_member_loci': sum(len(row['member_keys']) for row in paragraphs),
            'common_eligible_member_loci': sum(len(row['member_keys']) for row in common),
            'ordered_common_unit_ids_sha256': digest(
                ('\n'.join(row['common_unit_id'] for row in common) + '\n').encode()),
        },
        'paragraphs': paragraphs,
    }


def build(root=ROOT):
    membership_raw = (root / MEMBERSHIP_PATH).read_bytes()
    membership = strict_json(membership_raw)
    implementation = {f'scripts/{name}': digest((Path(__file__).parent / name).read_bytes())
                      for name in HELPERS}
    inputs = {
        'membership_report_path': str(MEMBERSHIP_PATH),
        'membership_report_sha256': digest(membership_raw),
        'source_catalog_path': 'data/transliterations.json',
        'source_catalog_sha256': digest((root / 'data/transliterations.json').read_bytes()),
        'selection_plan_path': str(PLAN_PATH),
        'selection_plan_sha256': digest((root / PLAN_PATH).read_bytes()),
        'implementation_sha256': implementation,
    }
    return construct(load_sources(root), membership, inputs)


def coverage(corpus):
    variants = []
    for source in corpus['sources']:
        for policy in POLICIES:
            selected = [next(variant for variant in paragraph['variants']
                             if variant['source_id'] == source['id'] and variant['uncertain_spaces'] == policy)
                        for paragraph in corpus['paragraphs']]
            reasons = Counter()
            for variant in selected:
                reasons.update({reason for row in variant['failed_loci'] for reason in row['exclusion_reasons']})
            variants.append({
                'source_id': source['id'], 'uncertain_spaces': policy,
                'candidate_units': len(selected),
                'locally_eligible_units': sum(variant['locally_eligible'] for variant in selected),
                'locally_excluded_units': sum(not variant['locally_eligible'] for variant in selected),
                'common_corpus_native_tokens': sum(variant['common_corpus_token_count'] or 0 for variant in selected),
                'local_unit_exclusion_reasons_may_overlap': dict(sorted(reasons.items())),
            })
    ledger = [{
        **{key: paragraph[key] for key in ('common_unit_id', 'page_id', 'member_keys',
                                         'ordered_member_keys_sha256', 'source_unit_ids', 'common_eligible')},
        'variants': [{key: variant[key] for key in ('source_id', 'uncertain_spaces',
                                                  'locally_eligible', 'failed_loci',
                                                  'common_corpus_token_count')}
                     for variant in paragraph['variants']],
    } for paragraph in corpus['paragraphs']]
    return {
        'schema_version': 1, 'method': 'exact common encoded paragraph token coverage v1',
        'producer_version': PRODUCER, 'inputs': corpus['inputs'], 'sources': corpus['sources'],
        'processing': corpus['processing'], 'cohort': corpus['cohort'],
        'canonical_corpus_sha256': digest(encoded(corpus)),
        'variants': variants, 'unit_ledger': ledger,
    }


def verify_corpus(raw, root=ROOT):
    actual = strict_json(raw)
    expected = build(root)
    if encoded(actual) != encoded(expected):
        raise ValueError('cached paragraph corpus differs from the complete pinned producer')
    return expected


def protect_outputs(outputs, read_inputs=(), root=ROOT):
    scripts = Path(__file__).parent.resolve()
    protected = [root / MEMBERSHIP_PATH, root / PLAN_PATH,
                 root / 'research/transliteration/PARAGRAPH_MEMBERSHIP_PLAN.md', *read_inputs]
    for index, output in enumerate(outputs):
        protect_source_output(output, root=root)
        resolved = output.resolve()
        if resolved == scripts or scripts in resolved.parents:
            raise ValueError('paragraph output must not overwrite implementation files')
        critical = protected + [path for path in scripts.rglob('*') if path.is_file()]
        if any(resolved == path.resolve() or
               (output.exists() and path.exists() and output.samefile(path)) for path in critical):
            raise ValueError('paragraph output aliases an input, implementation, plan, or verification target')
        for previous in outputs[:index]:
            if resolved == previous.resolve() or (output.exists() and previous.exists() and output.samefile(previous)):
                raise ValueError('coverage and corpus output paths must be distinct')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    summary_mode = parser.add_mutually_exclusive_group()
    summary_mode.add_argument('--output', type=Path, help='write token-free coverage JSON')
    summary_mode.add_argument('--check', type=Path, help='replay token-free coverage JSON')
    corpus_mode = parser.add_mutually_exclusive_group()
    corpus_mode.add_argument('--corpus-output', type=Path, help='write full native-token corpus locally')
    corpus_mode.add_argument('--check-corpus', type=Path, help='verify complete corpus against fresh producer')
    args = parser.parse_args()
    try:
        outputs = [path for path in (args.output, args.corpus_output) if path]
        reads = [path for path in (args.check, args.check_corpus) if path]
        protect_outputs(outputs, reads, root=ROOT)
        corpus = build(root=ROOT)
        report = coverage(corpus)
        if args.check and encoded(strict_json(args.check.read_bytes())) != encoded(report):
            raise ValueError('committed paragraph coverage differs from the complete pinned producer')
        if args.check_corpus and encoded(strict_json(args.check_corpus.read_bytes())) != encoded(corpus):
            raise ValueError('cached paragraph corpus differs from the complete pinned producer')
        # All input and verification checks precede any output write.
        if args.output:
            args.output.write_bytes(encoded(report))
        if args.corpus_output:
            args.corpus_output.write_bytes(encoded(corpus))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'paragraph corpus failed: {error}\n')
    print(f"Verified {report['cohort']['candidate_units']} candidate units; "
          f"{report['cohort']['common_eligible_units']} common eligible under all four variants.")
    if args.check_corpus:
        print('Complete cached corpus matches fresh producer output.')


if __name__ == '__main__':
    main()
