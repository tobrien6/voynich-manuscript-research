from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from unittest.mock import patch

from scripts.positional_prediction_demo import decode, encode, main, make_report, score, train


class PositionalPredictionControlTests(unittest.TestCase):
    def test_inverse_recovers_every_source_type_and_rejects_invalid_carriers(self):
        for chars in product('ab', repeat=4):
            word = ''.join(chars)
            for representation in ('literal', 'alternating_case'):
                self.assertEqual(decode(encode(word, representation), representation), word)
        for word in ['aaaa', 'AaAa', 'aAa', 'aAcA', 'aAAa']:
            with self.assertRaises(ValueError):
                decode(word, 'alternating_case')

    def test_parity_exclusions_have_exact_balanced_low_order_marginals(self):
        report = make_report()
        self.assertEqual(len(report['population']), 16)
        for fold in report['source_fold_marginals']:
            self.assertEqual(fold['types'], 8)
            self.assertEqual(fold['source_position_counts'], [{'a': 4, 'b': 4}] * 4)
            self.assertEqual(fold['source_adjacent_pair_counts'], [{'aa': 2, 'ab': 2, 'ba': 2, 'bb': 2}] * 3)
        partitions = [{row['source_word'] for row in report['population'] if row['fold'] == f} for f in range(2)]
        self.assertFalse(partitions[0] & partitions[1])
        self.assertEqual(len(partitions[0] | partitions[1]), 16)

    def test_every_score_matches_the_predeclared_exact_count_oracle(self):
        for result in make_report()['results']:
            for row in result['fold_model_records']:
                noninitial = row['treatment'] == 'matched_noninitial'
                expected = Fraction(1, 2)
                if result['representation'] == 'alternating_case':
                    if row['model'] == 'unigram':
                        expected = Fraction(1, 3) if noninitial else Fraction(1, 4)
                    elif row['model'] == 'bigram' and row['treatment'] == 'first_unigram_backoff':
                        expected = Fraction(3, 8)
                denominator = 24 if noninitial else 32
                self.assertEqual(row['training_types'], 8)
                self.assertEqual(row['heldout_types'], 8)
                self.assertEqual(row['scored_characters'], denominator)
                self.assertEqual(row['correct_characters'], expected * denominator)
                self.assertEqual(row['accuracy_exact'], {'numerator': expected.numerator, 'denominator': expected.denominator})
                self.assertEqual(row['tied_maximum_decisions'], denominator)
                self.assertEqual(row['unigram_backoff_decisions'],
                                 8 if row['model'] == 'bigram' and row['treatment'] == 'first_unigram_backoff' else 0)
            for summary in result['summaries']:
                matching = [row for row in result['fold_model_records']
                            if row['model'] == summary['model'] and row['treatment'] == summary['treatment']]
                self.assertEqual(summary['pooled_scored_characters'], sum(row['scored_characters'] for row in matching))
                self.assertEqual(summary['pooled_correct_characters'], sum(row['correct_characters'] for row in matching))
                self.assertEqual(summary['mean_fold_accuracy_exact'], matching[0]['accuracy_exact'])
                self.assertEqual(summary['pooled_accuracy_exact'], matching[0]['accuracy_exact'])

    def test_count_tables_reset_at_words_and_beginning_is_a_separate_context(self):
        uni, bi, beginning, positions = train(['ab', 'cd'])
        self.assertEqual(uni, Counter('abcd'))
        self.assertEqual(bi, {'a': Counter('b'), 'c': Counter('d')})
        self.assertEqual(beginning, Counter('ac'))
        self.assertEqual(positions, {0: Counter('ac'), 1: Counter('bd')})

    def test_position_baseline_never_reads_the_previous_test_character(self):
        counts = train(['aa', 'ba'])
        # At second position, a previous unseen x still has a direct positional prediction.
        position = score(['xa'], counts, 'matched_noninitial', 'position_only')
        bigram = score(['xa'], counts, 'matched_noninitial', 'bigram')
        self.assertEqual(position['unigram_backoff_decisions'], 0)
        self.assertEqual(bigram['unigram_backoff_decisions'], 1)
        self.assertEqual(position['correct_characters'], 1)

    def test_cli_preserves_existing_outputs_and_aliases(self):
        with tempfile.TemporaryDirectory() as folder:
            original = Path(folder) / 'original.json'; original.write_bytes(b'preserve bytes\n')
            symbolic = Path(folder) / 'symbolic.json'; symbolic.symlink_to(original)
            hard = Path(folder) / 'hard.json'; hard.hardlink_to(original)
            for target in [original, symbolic, hard]:
                with patch('sys.argv', ['demo', '--output', str(target)]), redirect_stderr(StringIO()), self.assertRaises(SystemExit) as failure:
                    main()
                self.assertEqual(failure.exception.code, 1)
                self.assertEqual(original.read_bytes(), b'preserve bytes\n')


if __name__ == '__main__':
    unittest.main()
