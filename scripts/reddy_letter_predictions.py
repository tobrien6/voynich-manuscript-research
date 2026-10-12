#!/usr/bin/env python3
"""Explicit type-fold letter prediction choices on one pinned local input."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_HASH = '723cb2746da37c8272005f71298917abfed60412b23597b2b8aecb95dc7a0ee4'
INPUT_BYTES = 95465
PLAN = ROOT / 'research/literature/REDDY_LETTER_PREDICTION_PLAN.md'
FOLDS = ROOT / 'research/literature/reddy-letter-folds.json'
TREATMENTS = ['first_unigram_backoff', 'first_beginning_context', 'matched_noninitial']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rational(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)} if value is not None else None


def input_types(path):
    raw = path.read_bytes()
    if len(raw) != INPUT_BYTES or sha(raw) != INPUT_HASH:
        raise ValueError('input differs from the pinned author-associated B bytes')
    tokens = raw.decode('utf-8').split()
    words = set(tokens)
    if len(tokens) != 17597 or len(words) != 3920 or len(set(''.join(words))) != 35:
        raise ValueError('native input population differs from the recovered audit')
    return words


def type_folds(words, count=10):
    words = set(words)
    if not words or any(not isinstance(word, str) or not word for word in words) or type(count) is not int or count < 2:
        raise ValueError('require nonempty word types and at least two folds')
    identities = [(sha(word.encode('utf-8')), word) for word in words]
    if len({identity for identity, _ in identities}) != len(identities):
        raise ValueError('distinct word hash collision')
    return [(word, index % count) for index, (_, word) in enumerate(sorted(identities))]


def fold_manifest(words):
    assignment = type_folds(words)
    return {'schema_version': 1, 'method': 'native UTF-8 SHA-256 sorted round-robin word-type folds v1',
            'input_sha256': INPUT_HASH, 'input_bytes': INPUT_BYTES, 'type_count': len(assignment), 'fold_count': 10,
            'plan_sha256': sha(PLAN.read_bytes()), 'producer_sha256': sha(Path(__file__).read_bytes()),
            'types': [{'word_utf8_sha256': sha(word.encode('utf-8')), 'native_character_count': len(word), 'fold': fold}
                      for word, fold in assignment],
            'scope': 'training exclusion by native types; no untouched physical folio claim; raw words not redistributed'}


def train(words, beginning=False):
    unigram, bigram = Counter(), defaultdict(Counter)
    for word in words:
        unigram.update(word)
        for index, character in enumerate(word):
            if index:
                bigram[word[index - 1]][character] += 1
            elif beginning:
                bigram[None][character] += 1
    if not unigram:
        raise ValueError('training has no native characters')
    return unigram, dict(bigram)


def winner(counts):
    if not counts:
        raise ValueError('cannot choose a character from an empty count table')
    highest = max(counts.values())
    tied = sorted(character for character, count in counts.items() if count == highest)
    return tied[0], len(tied) > 1


def score(words, unigram, bigram, treatment, model):
    if treatment not in TREATMENTS or model not in {'unigram', 'bigram'}:
        raise ValueError('unsupported frozen model/treatment')
    global_guess, global_tie = winner(unigram)
    correct, scored, ties, backoffs, zero_scored = 0, 0, 0, 0, 0
    for word in words:
        positions = range(1, len(word)) if treatment == 'matched_noninitial' else range(len(word))
        if not positions:
            zero_scored += 1
        for index in positions:
            guess, tied = global_guess, global_tie
            if model == 'bigram':
                context = word[index - 1] if index else None
                table = bigram.get(context) if index or treatment == 'first_beginning_context' else None
                if table:
                    guess, tied = winner(table)
                else:
                    backoffs += 1
            correct += guess == word[index]
            scored += 1
            ties += tied
    accuracy = Fraction(correct, scored) if scored else None
    return {'heldout_types': len(words), 'zero_scored_types': zero_scored, 'scored_characters': scored,
            'correct_characters': correct, 'tied_maximum_decisions': ties, 'unigram_backoff_decisions': backoffs,
            'accuracy_exact': rational(accuracy), 'accuracy_percent_rounded': round(float(accuracy) * 100, 8) if accuracy is not None else None}


def evaluate(words, manifest):
    if manifest != fold_manifest(words):
        raise ValueError('fold/plan/producer manifest differs from its frozen recomputation')
    assignment = type_folds(words)
    results = []
    for treatment in TREATMENTS:
        folds = []
        for heldout in range(10):
            test = [word for word, fold in assignment if fold == heldout]
            training = [word for word, fold in assignment if fold != heldout]
            if set(test) & set(training) or len(test) + len(training) != len(words):
                raise ValueError('word-type training/test partition leaked or lost a type')
            unigram, bigram = train(training, beginning=treatment == 'first_beginning_context')
            folds.append({'fold': heldout, 'training_types': len(training),
                          'unigram': score(test, unigram, bigram, treatment, 'unigram'),
                          'bigram': score(test, unigram, bigram, treatment, 'bigram')})
        models = []
        for model in ['unigram', 'bigram']:
            values = [fold[model] for fold in folds]
            undefined = [fold['fold'] for fold in folds if fold[model]['accuracy_exact'] is None]
            accuracies = [Fraction(value['correct_characters'], value['scored_characters']) for value in values if value['scored_characters']]
            mean = sum(accuracies, Fraction(0)) / 10 if not undefined else None
            total, correct = sum(value['scored_characters'] for value in values), sum(value['correct_characters'] for value in values)
            pooled = Fraction(correct, total) if total else None
            published = Fraction(1465, 10000) if model == 'unigram' else Fraction(4002, 10000)
            models.append({'model': model, 'undefined_fold_indices': undefined,
                           'mean_fold_accuracy_exact': rational(mean),
                           'mean_fold_accuracy_percent_rounded': round(float(mean) * 100, 8) if mean is not None else None,
                           'pooled_correct_characters': correct, 'pooled_scored_characters': total,
                           'pooled_accuracy_exact': rational(pooled),
                           'pooled_accuracy_percent_rounded': round(float(pooled) * 100, 8) if pooled is not None else None,
                           'published_accuracy_percent': float(published) * 100,
                           'mean_fold_minus_published_percentage_points': round(float(mean - published) * 100, 8) if mean is not None else None})
        results.append({'treatment': treatment, 'folds': folds, 'models': models})
    return {'schema_version': 1, 'method': 'explicit native-type letter prediction boundary choices v1',
            'input_sha256': INPUT_HASH, 'fold_manifest_sha256': sha((json.dumps(manifest, indent=2) + '\n').encode()),
            'plan_sha256': sha(PLAN.read_bytes()), 'producer_sha256': sha(Path(__file__).read_bytes()),
            'word_types': len(words), 'results': results,
            'scope': 'exposed later author-associated input; explicit operationalization not authenticated historical replication or decoding'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['folds', 'evaluate'])
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--folds', type=Path, default=FOLDS)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError('output record exists; choose a new record')
        words = input_types(args.input)
        result = fold_manifest(words) if args.mode == 'folds' else evaluate(words, json.loads(args.folds.read_text()))
        with args.output.open('x', encoding='utf-8') as output:
            output.write(json.dumps(result, indent=2) + '\n')
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'Letter prediction failed: {error}\n')
    print(f'Wrote {args.mode} record to {args.output}.')


if __name__ == '__main__':
    main()
