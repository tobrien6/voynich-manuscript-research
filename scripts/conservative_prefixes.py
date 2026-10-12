"""Prefix contrasts on one cohort eligible under every declared adapter policy."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import string

try:
    from .audit_transliterations import load_sources
    from .eva_token_adapter import build
    from .locus_positions import summarize_position
    from .prefix_strata import LOCATORS, PREFIX_FEATURES, paragraph_start
    from .token_baselines import Token, paired_sources
except ImportError:
    from audit_transliterations import load_sources
    from eva_token_adapter import build
    from locus_positions import summarize_position
    from prefix_strata import LOCATORS, PREFIX_FEATURES, paragraph_start
    from token_baselines import Token, paired_sources


def common_cohort(payloads, expected_hashes, candidate_keys):
    records, policy_counts, seen_modes = {}, [], set()
    for payload in payloads:
        if (payload['schema_version'] != 1 or payload['adapter_version'] != 'plain-eva-v1'
                or payload['analysis_unit'] != 'transcription_locus'):
            raise ValueError('adapter contract/version changed')
        mode = payload['processing']['uncertain_space_policy']
        if mode not in {'split', 'join'} or mode in seen_modes:
            raise ValueError('need exactly one split and one join adapter output')
        seen_modes.add(mode)
        if (payload['processing']['selected_locus_types'] != ['P0'] or
                payload['processing']['ambiguity_policy'] != 'exclude entire selected locus with explicit reasons'):
            raise ValueError('adapter processing policy changed')
        sources = payload['sources']
        if (len(sources) != len(expected_hashes) or
                {source['id']: source['sha256'] for source in sources} != expected_hashes):
            raise ValueError('adapter source provenance changed')
        for record in payload['records']:
            identity = (record['source_id'], mode, record['locus_key'])
            if record['source_id'] not in expected_hashes or identity in records:
                raise ValueError('unknown source or duplicate adapter locus')
            records[identity] = record
    if seen_modes != {'split', 'join'}:
        raise ValueError('need both spacing policies')
    selected, excluded = set(), []
    counters = {(source, mode): Counter() for source in expected_hashes for mode in ['split', 'join']}
    for key in sorted(candidate_keys):
        reasons = []
        for source in expected_hashes:
            for mode in ['split', 'join']:
                identity = (source, mode, key)
                if identity not in records:
                    raise ValueError(f'missing candidate adapter record: {identity}')
                record = records[identity]
                if record['locus_type'] != 'P0':
                    raise ValueError('candidate locus type changed')
                counter = counters[(source, mode)]
                counter['candidate_records'] += 1
                problems = []
                if not record['eligible']:
                    problems.extend(record['exclusion_reasons'])
                    if not problems:
                        raise ValueError('excluded adapter record lacks reasons')
                    counter['excluded_by_adapter'] += 1
                else:
                    tokens = record['tokens']
                    if not isinstance(tokens, list) or record['token_count'] != len(tokens):
                        raise ValueError('eligible adapter token count changed')
                    if any(not isinstance(token, str) or not token or
                           any(char not in string.ascii_letters for char in token) for token in tokens):
                        raise ValueError('eligible adapter token is not plain Eva ASCII letters')
                    if len(tokens) < 2:
                        problems.append('fewer_than_two_tokens')
                        counter['fewer_than_two_tokens'] += 1
                if record['locator'] not in LOCATORS:
                    problems.append('nonregular_locator')
                    counter['nonregular_locator'] += 1
                if problems:
                    reasons.append({'source_id': source, 'spacing': mode, 'reasons': problems})
                else:
                    counter['eligible_regular_at_least_two'] += 1
        if reasons:
            excluded.append({'locus_key': key, 'source_policy_failures': reasons})
        else:
            selected.add(key)
    for (source, mode), counter in counters.items():
        policy_counts.append({'source_id': source, 'spacing': mode,
                              'counts_reasons_may_overlap': dict(sorted(counter.items()))})
    return selected, records, excluded, policy_counts


def conservative_report(repetitions=199, seed=20261011):
    if repetitions < 1:
        raise ValueError('repetitions must be positive')
    sources = paired_sources(load_sources())
    expected = {source['id']: source['sha256'] for source, _ in sources}
    candidates = set.intersection(*[
        {locus.key for locus in document.loci if locus.present and locus.kind == 'P0'}
        for _, document in sources])
    payloads = [build(mode, source_ids=tuple(expected), kinds=('P0',)) for mode in ['split', 'join']]
    selected, records, excluded, counts = common_cohort(payloads, expected, candidates)
    if not selected:
        raise ValueError('empty conservative common cohort')
    labels = sorted({locus.variables.get('L', 'unset') for _, document in sources
                     for locus in document.loci if locus.key in selected})
    report = {
        'schema_version': 1, 'method': 'exploratory plain-eva-v1 common-cohort prefix controls v1',
        'adapter_version': 'plain-eva-v1',
        'selection': {
            'candidate_shared_present_p0_count': len(candidates), 'selected_count': len(selected),
            'selected_locus_keys': sorted(selected),
            'sorted_selected_locus_keys_sha256': hashlib.sha256(
                ('\n'.join(sorted(selected)) + '\n').encode()).hexdigest(),
            'source_currier_labels_including_unset': labels,
            'excluded_loci': excluded, 'source_policy_counts': counts,
        },
        'sources': [],
    }
    for source, document in sources:
        loci = [locus for locus in document.loci if locus.key in selected and locus.present and locus.kind == 'P0']
        variants = []
        for mode in ['split', 'join']:
            rows = [(locus, [Token(text, len(text)) for text in records[(source['id'], mode, locus.key)]['tokens']])
                    for locus in loci]
            cohorts = []
            for label in labels:
                for starts_paragraph in [False, True]:
                    cohort = [(locus, slots) for locus, slots in rows
                              if locus.variables.get('L', 'unset') == label and
                              paragraph_start(locus) == starts_paragraph]
                    positions = []
                    for boundary in ['first', 'last']:
                        position = summarize_position(cohort, boundary, repetitions, seed)
                        position['features'] = [feature for feature in position['features']
                                                if feature['feature'] in PREFIX_FEATURES]
                        if len(position['features']) != 2:
                            raise ValueError('prefix feature interface changed')
                        positions.append(position)
                    cohorts.append({'source_currier_label': label,
                                    'source_paragraph_start': starts_paragraph,
                                    'selected_loci': len(cohort), 'positions': positions})
            variants.append({'spacing': mode, 'cohorts': cohorts})
        report['sources'].append({'id': source['id'], 'sha256': source['sha256'], 'variants': variants})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repetitions', type=int, default=199)
    parser.add_argument('--seed', type=int, default=20261011)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        report = conservative_report(args.repetitions, args.seed)
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed conservative cohort differs from recomputed report')
    except (ValueError, OSError) as error:
        parser.exit(1, f'conservative prefix analysis failed: {error}\n')
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(rendered)
    elif not args.check:
        print(rendered, end='')
    if args.check:
        print('Adapter contract, pinned inputs and conservative prefix cohort verified.')


if __name__ == '__main__':
    main()
