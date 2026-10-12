"""A fixed synthetic counterexample for substitution-score normalization."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'research/literature/substitution-normalization-control.json'
TOY_COUNTS = {'A': 1, 'B': 1, 'C': 99, 'XC': 99}


def entropy(counts):
    total = sum(counts.values())
    if total <= 0:
        raise ValueError('entropy requires positive mass')
    return -math.fsum((count / total) * math.log2(count / total) for count in counts.values())


def measure(counts, source, target):
    if not counts or any(not isinstance(word, str) or not word or type(count) is not int or count <= 0
                         for word, count in counts.items()):
        raise ValueError('require nonempty words and positive integer occurrence counts')
    if not isinstance(source, str) or not isinstance(target, str) or len(source) != 1 or len(target) != 1 or source == target:
        raise ValueError('require two distinct single notation characters')
    selected = {word: count for word, count in counts.items() if source in word or target in word}
    selected_mass = sum(selected.values())
    if not selected_mass:
        raise ValueError('selected subset has no occurrence mass')
    total = sum(counts.values())
    groups = defaultdict(dict)
    for word, count in selected.items():
        groups[word.replace(source, target)][word] = count
    collision_groups = {word: members for word, members in groups.items() if len(members) > 1}
    # A singleton class contributes exactly zero and is not evaluated by cancellation.
    information = math.fsum(math.fsum([sum(members.values()) * math.log2(sum(members.values()))]
                                     + [-count * math.log2(count) for count in members.values()])
                            for members in collision_groups.values())
    transformed = Counter()
    for word, count in counts.items():
        transformed[word.replace(source, target)] += count
    subset_transformed = {word: sum(members.values()) for word, members in groups.items()}
    weight = Fraction(selected_mass, total)
    return {'source': source, 'target': target, 'all_occurrences': total,
            'selected_occurrences': selected_mass,
            'selected_mass_fraction': {'numerator': str(weight.numerator), 'denominator': str(weight.denominator)},
            'all_types_before': len(counts), 'all_types_after': len(transformed),
            'selected_types_before': len(selected), 'selected_types_after': len(groups),
            'collision_classes': [{'mapped_synthetic_word': word,
                                   'original_synthetic_counts': [{'word': original, 'occurrences': count}
                                                                 for original, count in sorted(members.items())]}
                                  for word, members in sorted(collision_groups.items())],
            'subset_entropy_before_bits': entropy(selected), 'subset_entropy_after_bits': entropy(subset_transformed),
            'whole_entropy_before_bits': entropy(counts), 'whole_entropy_after_bits': entropy(transformed),
            'subset_entropy_decrease_bits': information / selected_mass,
            'whole_entropy_decrease_bits': information / total}


def report():
    results = [measure(TOY_COUNTS, 'A', target) for target in ['B', 'C']]
    for result in results:
        for key, value in list(result.items()):
            if isinstance(value, float):
                result[key] = round(value, 12)
    return {'schema_version': 1, 'method': 'fixed synthetic substitution-normalization control v1',
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_observation': {'repository': 'sravanareddy/deciphervoynich',
                                   'commit': '643b881b2937bae8193814d8ff5d6e99a48bf7c5',
                                   'path': 'basic_stats.py', 'function': 'CorpusStats.get_bestsub',
                                   'sha256': '12102b9c290838ebe0c60580f62cb449759cb71d13949dbcf5c23c82d1aa4ccc',
                                   'basis': 'prior static source inspection, not author execution or runtime file verification'},
            'synthetic_word_counts': [{'word': word, 'occurrences': count} for word, count in sorted(TOY_COUNTS.items())],
            'declared_candidates': ['B', 'C'], 'results': results,
            'largest_subset_decrease_target': max(results, key=lambda result: result['subset_entropy_decrease_bits'])['target'],
            'largest_whole_decrease_target': max(results, key=lambda result: result['whole_entropy_decrease_bits'])['target'],
            'scope': 'constructed counterexample over two candidates; no manuscript input or historical BESTSUB result evaluated'}


def load(raw):
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('non-finite JSON number')
    return json.loads(raw, object_pairs_hook=object_pairs, parse_constant=invalid)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.output and (args.output.exists() or args.output.is_symlink()):
            raise ValueError('output exists; choose a new record')
        result = report()
        if args.check:
            if result != load(REPORT.read_bytes()):
                raise ValueError('synthetic report differs from reconstruction')
            print('Synthetic substitution-normalization report matches.')
        else:
            with args.output.open('x', encoding='utf-8') as output:
                output.write(json.dumps(result, indent=2) + '\n')
            print('Wrote synthetic substitution-normalization report.')
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Substitution control failed: {error}\n')


if __name__ == '__main__':
    main()
