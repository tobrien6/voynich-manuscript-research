"""Exploratory token baselines on paired, uncertainty-aware IVTFF sources."""

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random
import re
import string

try:
    from .audit_transliterations import load_sources
    from .ivtff import TAG, without_free_comments
except ImportError:
    from audit_transliterations import load_sources
    from ivtff import TAG, without_free_comments


@dataclass(frozen=True)
class Token:
    value: str
    units: int
    alternative: bool = False
    unreadable: bool = False


def _literal(text):
    """Count notation units, retaining ligatures and high-ASCII identities."""
    parts, units, unreadable = [], 0, False
    index = 0
    while index < len(text):
        char = text[index]
        if char in string.ascii_letters + "'":
            parts.append(char)
            units += 1
            index += 1
        elif char == '?':
            parts.append(char)
            units += 1
            unreadable = True
            index += 1
        elif char == '@':
            match = re.match(r'@([0-9]{3});', text[index:])
            if not match or not 128 <= int(match[1]) <= 255:
                raise ValueError('invalid high-ASCII code')
            parts.append(match[0])
            units += 1
            index += len(match[0])
        elif char == '{':
            end = text.find('}', index + 1)
            if end < 0 or '{' in text[index + 1:end]:
                raise ValueError('unclosed or nested ligature')
            content = text[index + 1:end]
            if not content:
                raise ValueError('empty ligature')
            encoded, length, unknown = _literal(content)
            parts.append('{' + encoded + '}')
            units += length
            unreadable |= unknown
            index = end + 1
        else:
            raise ValueError(f'unsupported character inside token: {char!r}')
    return ''.join(parts), units, unreadable


def tokenize(text, uncertain_spaces):
    """Preserve all apparent token slots; choosing alternatives happens explicitly.

    The first reading in a bracket is selected, but flagged so the caller can
    exclude the entire token. Illegible and empty selections remain visible slots.
    Whitespace is formatting, never a word separator.
    """
    if uncertain_spaces not in {'split', 'join'}:
        raise ValueError('uncertain_spaces must be split or join')
    text = without_free_comments(text)
    tokens, parts, units, alternative, unreadable = [], [], 0, False, False
    has_content = False
    separator_pending = False
    index = 0

    def finish():
        nonlocal parts, units, alternative, unreadable, has_content
        if not has_content:
            raise ValueError('empty token between or beside separators')
        tokens.append(Token(''.join(parts), units, alternative, unreadable))
        parts, units, alternative, unreadable, has_content = [], 0, False, False, False

    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char == '<':
            end = text.find('>', index + 1)
            if end < 0:
                raise ValueError('unclosed inline annotation')
            code = text[index:end + 1]
            if code in {'<->', '<~>'}:
                if separator_pending:
                    raise ValueError('consecutive word separators')
                finish()
                separator_pending = True
            elif code not in {'<%>', '<$>'} and not TAG.fullmatch(code):
                raise ValueError(f'unsupported inline annotation: {code}')
            index = end + 1
            continue
        if char in '.,':
            # Validate source boundaries before applying the uncertain-space
            # policy. Joining a comma cannot repair an empty or doubled gap.
            if separator_pending or not has_content:
                raise ValueError('empty or consecutive word separator')
            if char == '.' or uncertain_spaces == 'split':
                finish()
            separator_pending = True
            index += 1
            continue
        if char == '[':
            end = text.find(']', index + 1)
            if end < 0 or '[' in text[index + 1:end]:
                raise ValueError('unclosed or nested alternative')
            choices = text[index + 1:end].split(':')
            if len(choices) < 2:
                raise ValueError('alternative requires colon-separated choices')
            # Validate every option, including unselected ones. Branching word
            # segmentation is outside this reader's supported text grammar.
            for choice in choices:
                _literal(choice)
            encoded, length, unknown = _literal(choices[0])
            alternative = True
            index = end + 1
        elif char == '{':
            end = text.find('}', index + 1)
            if end < 0:
                raise ValueError('unclosed ligature')
            encoded, length, unknown = _literal(text[index:end + 1])
            index = end + 1
        elif char == '@':
            encoded, length, unknown = _literal(text[index:index + 5])
            index += 5
        else:
            encoded, length, unknown = _literal(char)
            index += 1
        parts.append(encoded)
        units += length
        unreadable |= unknown
        has_content = True
        separator_pending = False
    if separator_pending:
        raise ValueError('trailing word separator')
    if has_content:
        finish()
    return tokens


def retain(token, alternatives):
    return bool(token.value) and not token.unreadable and (alternatives == 'first' or not token.alternative)


def adjacency(slots):
    """Map retained tokens to edges without bridging excluded-token gaps."""
    positions = [(index, token.value) for index, token in enumerate(slots) if token is not None]
    values = [value for _, value in positions]
    edges = [(index - 1, index) for index in range(1, len(positions))
             if positions[index][0] == positions[index - 1][0] + 1]
    return values, edges


def expected_repeats(values, edges):
    count = len(values)
    if count < 2:
        return 0.0
    frequencies = Counter(values)
    same_pair_probability = sum(n * (n - 1) for n in frequencies.values()) / (count * (count - 1))
    return len(edges) * same_pair_probability


def summarize(loci, spacing, alternatives, repetitions, seed):
    frequencies, lengths, exclusions = Counter(), Counter(), Counter()
    groups = []
    slots_total, eligible_pairs, observed_repeats, expectation = 0, 0, 0, 0.0
    for locus in loci:
        try:
            tokens = tokenize(locus.text, spacing)
        except ValueError as error:
            raise ValueError(f'{locus.identifier}: {error}') from error
        slots_total += len(tokens)
        slots = []
        for token in tokens:
            kept = retain(token, alternatives)
            slots.append(token if kept else None)
            if kept:
                frequencies[token.value] += 1
                lengths[token.units] += 1
            else:
                exclusions['total'] += 1
                exclusions['unreadable'] += token.unreadable
                exclusions['alternative'] += token.alternative and alternatives == 'exclude'
                exclusions['empty_first_option'] += not bool(token.value)
        values, edges = adjacency(slots)
        eligible_pairs += len(edges)
        observed_repeats += sum(values[a] == values[b] for a, b in edges)
        expectation += expected_repeats(values, edges)
        if edges:
            groups.append((values, edges))
    rng = random.Random(seed)
    null_counts = []
    for _ in range(repetitions):
        count = 0
        for values, edges in groups:
            shuffled = values.copy()
            rng.shuffle(shuffled)
            count += sum(shuffled[a] == shuffled[b] for a, b in edges)
        null_counts.append(count)
    retained = sum(frequencies.values())
    return {
        'uncertain_spaces': spacing, 'alternatives': alternatives,
        'selected_loci': len(loci), 'apparent_token_slots': slots_total,
        'retained_tokens': retained, 'distinct_representations': len(frequencies),
        'excluded_token_reasons_may_overlap': dict(sorted(exclusions.items())),
        'mean_notation_units': round(sum(k * n for k, n in lengths.items()) / retained, 8) if retained else None,
        'notation_unit_length_counts': dict(sorted(lengths.items())),
        'most_common_representations': [{'text': value, 'count': count} for value, count in
                                       sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))[:20]],
        'adjacent_repetition': {
            'eligible_pairs': eligible_pairs, 'observed_equal_pairs': observed_repeats,
            'observed_rate': round(observed_repeats / eligible_pairs, 8) if eligible_pairs else None,
            'exact_conditional_expected_pairs': round(expectation, 8),
            'expected_rate': round(expectation / eligible_pairs, 8) if eligible_pairs else None,
            'shuffle_repetitions': repetitions, 'seed': seed,
            'null_equal_pair_counts': null_counts,
            'exploratory_upper_tail': ((1 + sum(n >= observed_repeats for n in null_counts)) /
                                       (repetitions + 1)) if eligible_pairs else None,
        },
    }


def paired_sources(sources):
    """Keep the declared ZL/IT analysis stable as the source catalog grows."""
    paired = []
    for identifier in ('ZL3b', 'IT2a'):
        matches = [(source, document) for source, document in sources
                   if source['id'] == identifier]
        if len(matches) != 1:
            raise ValueError(f'Expected exactly one pinned {identifier} source')
        paired.append(matches[0])
    return paired


def baselines(repetitions=199, seed=20261011):
    if repetitions < 1:
        raise ValueError('repetitions must be positive')
    sources = paired_sources(load_sources())
    sets = [{locus.key for locus in doc.loci if locus.present and locus.kind == 'P0'} for _, doc in sources]
    common = set.intersection(*sets)
    if not common:
        raise ValueError('no common P0 locations')
    selection_hash = hashlib.sha256(('\n'.join(sorted(common)) + '\n').encode()).hexdigest()
    report = {
        'schema_version': 1, 'method': 'paired exploratory token baselines v1',
        'selection': {'kind': 'P0', 'rule': 'intersection of present P0 loci in the paired ZL3b and IT2a sources',
                      'count': len(common), 'sorted_locus_keys_sha256': selection_hash},
        'sources': [],
    }
    for source, doc in sources:
        selected = [locus for locus in doc.loci if locus.key in common and locus.present and locus.kind == 'P0']
        variants = []
        for spacing in ['split', 'join']:
            for alternatives in ['exclude', 'first']:
                variant = summarize(selected, spacing, alternatives, repetitions, seed)
                # JSON object keys are always strings, including length bins.
                variant['notation_unit_length_counts'] = {
                    str(key): value for key, value in variant['notation_unit_length_counts'].items()}
                variants.append(variant)
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
        report = baselines(args.repetitions, args.seed)
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError('committed baseline differs from recomputed report')
    except (ValueError, OSError) as error:
        parser.exit(1, f'baseline failed: {error}\n')
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(rendered)
    elif not args.check:
        print(rendered, end='')
    if args.check:
        print('Pinned inputs and committed exploratory baselines verified.')


if __name__ == '__main__':
    main()
