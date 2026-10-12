import unittest
from copy import deepcopy
from fractions import Fraction
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import tempfile
from unittest.mock import patch

from scripts.reddy_letter_predictions import evaluate, fold_manifest, main, score, train, type_folds, winner


class LetterPredictionChoicesTests(unittest.TestCase):
    def test_hash_folds_are_order_independent_balanced_and_type_disjoint(self):
        words = ['a', 'b', 'ab', 'ba', 'aa', 'bb']
        first = type_folds(words, 3)
        self.assertEqual(first, type_folds(list(reversed(words)) + ['a'], 3))
        self.assertEqual([sum(fold == index for _, fold in first) for index in range(3)], [2, 2, 2])
        self.assertEqual(len({word for word, _ in first}), len(words))

    def test_training_never_counts_cross_word_pairs_and_bos_is_not_a_target_character(self):
        unigram, bigram = train(['ab', 'cd'])
        self.assertNotIn('b', bigram)
        self.assertEqual(bigram['a']['b'], 1)
        with_start, contexts = train(['ab', 'cd'], beginning=True)
        self.assertEqual(with_start, unigram)
        self.assertEqual(set(contexts[None]), {'a', 'c'})
        self.assertNotIn(None, unigram)

    def test_ties_choose_lowest_codepoint_and_unseen_context_uses_unigram(self):
        self.assertEqual(winner({'b': 2, 'a': 2}), ('a', True))
        uni, bi = train(['aa', 'ab'])
        result = score(['za'], uni, bi, 'first_unigram_backoff', 'bigram')
        self.assertEqual(result['unigram_backoff_decisions'], 2)
        self.assertEqual(result['correct_characters'], 1)

    def test_bigram_uses_observed_previous_character_and_retains_first_treatment_denominators(self):
        uni, bi = train(['ab', 'ab', 'cc'])
        result = score(['xb'], uni, bi, 'first_unigram_backoff', 'bigram')
        self.assertEqual(result['unigram_backoff_decisions'], 2)
        self.assertEqual(result['correct_characters'], 0)
        skipped = score(['a', 'ab'], uni, bi, 'matched_noninitial', 'bigram')
        self.assertEqual(skipped['scored_characters'], 1)
        self.assertEqual(skipped['zero_scored_types'], 1)
        self.assertEqual(skipped['correct_characters'], 1)

    def test_beginning_context_changes_only_the_first_context_rule(self):
        uni, bi = train(['ba', 'ba', 'ac'], beginning=True)
        beginning = score(['ba'], uni, bi, 'first_beginning_context', 'bigram')
        backoff = score(['ba'], uni, bi, 'first_unigram_backoff', 'bigram')
        self.assertEqual(beginning['scored_characters'], backoff['scored_characters'])
        self.assertGreater(beginning['correct_characters'], backoff['correct_characters'])

    def test_mean_fold_and_pooled_accuracy_keep_distinct_denominators(self):
        words = {'a' * index + 'b' for index in range(20)}
        report = evaluate(words, fold_manifest(words))
        result = report['results'][0]
        values = [fold['unigram'] for fold in result['folds']]
        expected_mean = sum((Fraction(value['correct_characters'], value['scored_characters'])
                             for value in values), Fraction()) / 10
        expected_pooled = Fraction(sum(value['correct_characters'] for value in values),
                                  sum(value['scored_characters'] for value in values))
        model = result['models'][0]
        actual_mean = Fraction(int(model['mean_fold_accuracy_exact']['numerator']),
                               int(model['mean_fold_accuracy_exact']['denominator']))
        actual_pooled = Fraction(int(model['pooled_accuracy_exact']['numerator']),
                                 int(model['pooled_accuracy_exact']['denominator']))
        self.assertEqual(actual_mean, expected_mean)
        self.assertEqual(actual_pooled, expected_pooled)
        self.assertNotEqual(actual_mean, actual_pooled)
        self.assertEqual([fold['training_types'] for fold in result['folds']], [18] * 10)
        self.assertEqual(sum(value['heldout_types'] for value in values), 20)

    def test_evaluation_rejects_changed_fold_or_producer_identity(self):
        words = {'a' * index + 'b' for index in range(20)}
        original = fold_manifest(words)
        for key in ['producer_sha256', 'plan_sha256']:
            changed = deepcopy(original)
            changed[key] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'frozen recomputation'):
                evaluate(words, changed)
        changed = deepcopy(original)
        changed['types'][0]['fold'] = (changed['types'][0]['fold'] + 1) % 10
        with self.assertRaisesRegex(ValueError, 'frozen recomputation'):
            evaluate(words, changed)

    def test_cli_rejects_existing_outputs_and_aliases_before_reading_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            existing = root / 'original.json'
            existing.write_bytes(b'preserve original bytes\n')
            symbolic = root / 'symbolic.json'
            symbolic.symlink_to(existing)
            hard = root / 'hard.json'
            hard.hardlink_to(existing)
            for target in [existing, symbolic, hard]:
                with self.subTest(target=target.name), patch('sys.argv', ['predictor', 'folds',
                        '--input', str(root / 'absent-input'), '--output', str(target)]), \
                        patch('scripts.reddy_letter_predictions.input_types') as read_input, \
                        redirect_stderr(StringIO()), self.assertRaises(SystemExit) as failure:
                    main()
                self.assertEqual(failure.exception.code, 1)
                read_input.assert_not_called()
                self.assertEqual(existing.read_bytes(), b'preserve original bytes\n')


if __name__ == '__main__':
    unittest.main()
