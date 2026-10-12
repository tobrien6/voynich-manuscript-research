"""Exact synthetic letter prediction under a reversible positional carrier."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'research/representation/POSITIONAL_PREDICTION_PLAN.md'
REPORT = ROOT / 'research/representation/positional-prediction-demo.json'
REPRESENTATIONS = ('literal', 'alternating_case')
TREATMENTS = ('first_unigram_backoff', 'first_beginning_context', 'matched_noninitial')
MODELS = ('unigram', 'bigram', 'position_only')


def encode(word, representation):
    if len(word) != 4 or set(word) - {'a', 'b'}:
        raise ValueError('source requires exactly four a/b letters')
    if representation == 'literal':
        return word
    if representation == 'alternating_case':
        return ''.join(c.upper() if i % 2 else c for i, c in enumerate(word))
    raise ValueError('unknown representation')


def decode(word, representation):
    source = word.lower()
    if encode(source, representation) != word:
        raise ValueError('carrier violates the declared case/position convention')
    return source


def choose(counts):
    if not counts:
        raise ValueError('empty training count table')
    maximum = max(counts.values())
    tied = sorted(c for c, count in counts.items() if count == maximum)
    return tied[0], len(tied) > 1


def train(words):
    unigram, beginning = Counter(), Counter()
    bigram, positions = defaultdict(Counter), defaultdict(Counter)
    for word in words:
        unigram.update(word)
        beginning[word[0]] += 1
        for i, target in enumerate(word):
            positions[i][target] += 1
            if i:
                bigram[word[i - 1]][target] += 1
    return unigram, dict(bigram), beginning, dict(positions)


def rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def score(words, counts, treatment, model):
    if treatment not in TREATMENTS or model not in MODELS:
        raise ValueError('unknown treatment/model')
    unigram, bigram, beginning, positions = counts
    correct = scored = ties = backoffs = 0
    for word in words:
        for i in range(1 if treatment == 'matched_noninitial' else 0, len(word)):
            table = unigram
            if model == 'position_only':
                table = positions[i]
            elif model == 'bigram':
                table = (bigram.get(word[i - 1]) if i else
                         beginning if treatment == 'first_beginning_context' else None)
                if not table:
                    table = unigram
                    backoffs += 1
            guess, tied = choose(table)
            correct += guess == word[i]
            ties += tied
            scored += 1
    return {'heldout_types': len(words), 'scored_characters': scored,
            'correct_characters': correct, 'tied_maximum_decisions': ties,
            'unigram_backoff_decisions': backoffs,
            'accuracy_exact': rational(Fraction(correct, scored))}


def make_report():
    sources = [''.join(chars) for chars in product('ab', repeat=4)]
    assignments = {word: word.count('b') % 2 for word in sources}
    population = [{'source_word': word, 'fold': assignments[word],
                   'literal': encode(word, 'literal'),
                   'alternating_case': encode(word, 'alternating_case')} for word in sources]
    marginals = []
    for fold in range(2):
        words = [word for word in sources if assignments[word] == fold]
        marginals.append({'fold': fold, 'types': len(words),
                          'source_position_counts': [dict(sorted(Counter(w[i] for w in words).items()))
                                                     for i in range(4)],
                          'source_adjacent_pair_counts': [dict(sorted(Counter(w[i:i + 2] for w in words).items()))
                                                          for i in range(3)]})
    results = []
    for representation in REPRESENTATIONS:
        folds, fitted = [], []
        for fold in range(2):
            training_source = [w for w in sources if assignments[w] != fold]
            test_source = [w for w in sources if assignments[w] == fold]
            if set(training_source) & set(test_source):
                raise ValueError('source type leaked across a training/test exclusion')
            training = [encode(w, representation) for w in training_source]
            test = [encode(w, representation) for w in test_source]
            if any(decode(encode(w, representation), representation) != w for w in sources):
                raise ValueError('inverse did not recover a source word')
            unigram, bigram, beginning, positions = counts = train(training)
            fitted.append({'fold': fold, 'training_types': len(training),
                           'unigram_counts': dict(sorted(unigram.items())),
                           'internal_bigram_counts': [{'preceding_character': c,
                                                      'target_counts': dict(sorted(table.items()))}
                                                     for c, table in sorted(bigram.items())],
                           'beginning_context_counts': dict(sorted(beginning.items())),
                           'position_counts': [{'position_1based': i + 1,
                                                'target_counts': dict(sorted(table.items()))}
                                               for i, table in sorted(positions.items())]})
            for treatment in TREATMENTS:
                for model in MODELS:
                    folds.append({'fold': fold, 'training_types': len(training),
                                  'treatment': treatment, 'model': model,
                                  **score(test, counts, treatment, model)})
        summaries = []
        for treatment in TREATMENTS:
            for model in MODELS:
                rows = [row for row in folds if row['treatment'] == treatment and row['model'] == model]
                mean = sum((Fraction(row['correct_characters'], row['scored_characters'])
                            for row in rows), Fraction()) / 2
                correct = sum(row['correct_characters'] for row in rows)
                scored = sum(row['scored_characters'] for row in rows)
                summaries.append({'treatment': treatment, 'model': model,
                                  'mean_fold_accuracy_exact': rational(mean),
                                  'pooled_correct_characters': correct, 'pooled_scored_characters': scored,
                                  'pooled_accuracy_exact': rational(Fraction(correct, scored))})
        results.append({'representation': representation, 'fitted_counts': fitted,
                        'fold_model_records': folds, 'summaries': summaries})
    return {'schema_version': 1, 'method': 'exhaustive binary parity-fold positional prediction control v1',
            'plan_sha256': hashlib.sha256(PLAN.read_bytes()).hexdigest(),
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'population': population, 'source_fold_marginals': marginals, 'results': results,
            'scope': 'original synthetic example with analytically exposed expectations; no manuscript fit or historical replication'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check', action='store_true')
    modes.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        raw = (json.dumps(make_report(), indent=2) + '\n').encode('utf-8')
        if args.check:
            if REPORT.read_bytes() != raw:
                raise ValueError('committed report differs from complete regeneration')
        else:
            with args.output.open('xb') as output:
                output.write(raw)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'Positional prediction control failed: {error}\n')
    print('Positional prediction report verified.' if args.check else 'Wrote positional prediction report.')


if __name__ == '__main__':
    main()
