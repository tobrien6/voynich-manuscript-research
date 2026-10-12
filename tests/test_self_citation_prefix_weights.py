from fractions import Fraction
import itertools
import unittest

from scripts.audit_self_citation_prefix_weights import as_fraction, measure, strict_json


class PrefixWeightTests(unittest.TestCase):
    def test_pair_enumeration_and_population_covariance_agree(self):
        # Each opportunity is an explicit boundary/other token pair, an oracle
        # distinct from summing prefix counts in the production calculation.
        for n, m in itertools.product(range(2, 5), repeat=2):
            for bits in itertools.product((False, True), repeat=n + m):
                rows = [[('q' if bit else 'a') for bit in bits[:n]],
                        [('q' if bit else 'a') for bit in bits[n:]]]
                for boundary in ('first', 'last'):
                    edge = 0 if boundary == 'first' else -1
                    contrasts, opportunities = [], []
                    for row in rows:
                        target = row[edge] == 'q'
                        others = row[1:] if boundary == 'first' else row[:-1]
                        pairs = [int(target) - int(token == 'q') for token in others]
                        contrasts.append(Fraction(sum(pairs), len(pairs)))
                        opportunities.extend(pairs)
                    equal = sum(contrasts) / 2
                    weighted = Fraction(sum(opportunities), len(opportunities))
                    weights = [n - 1, m - 1]; mean_weight = Fraction(sum(weights), 2)
                    cov = sum((Fraction(w) - mean_weight) * (d - equal)
                              for w, d in zip(weights, contrasts)) / 2
                    actual = measure(rows, boundary, 'q')
                    self.assertEqual(as_fraction(actual['equal_row_mean_difference_exact']), equal)
                    self.assertEqual(as_fraction(actual['opportunity_weighted_mean_difference_exact']), weighted)
                    self.assertEqual(as_fraction(actual['population_covariance_weight_contrast_exact']), cov)
                    self.assertEqual(weighted - equal, cov / mean_weight)

    def test_length_weighting_can_reverse_sign_on_identical_rows(self):
        rows = [['q', 'a'], ['a', 'q', 'q', *(['a'] * 7)]]
        actual = measure(rows, 'first', 'q')
        self.assertEqual(as_fraction(actual['equal_row_mean_difference_exact']), Fraction(7, 18))
        self.assertEqual(as_fraction(actual['opportunity_weighted_mean_difference_exact']), Fraction(-1, 10))
        self.assertEqual(actual['sign_transition'], 'positive->negative')

    def test_constant_weights_and_zero_contrasts_have_zero_change(self):
        for prefix in ('q', 'y'):
            rows = [[prefix, 'a', 'a'], ['a', prefix, 'a']]
            actual = measure(rows, 'first', prefix)
            self.assertEqual(as_fraction(actual['weighted_minus_equal_exact']), 0)
            self.assertEqual(as_fraction(actual['population_covariance_weight_contrast_exact']), 0)
        actual = measure([['q', 'q'], ['a', 'a', 'a', 'a']], 'last', 'q')
        self.assertEqual(actual['sign_transition'], 'zero->zero')

    def test_short_rows_preserve_population_but_do_not_contribute(self):
        actual = measure([[], ['q'], ['q', 'a']], 'first', 'q')
        self.assertEqual(actual['population_rows'], 3)
        self.assertEqual(actual['eligible_rows'], 1)
        self.assertEqual(actual['total_comparison_opportunities'], 1)
        self.assertEqual(as_fraction(actual['equal_row_mean_difference_exact']), 1)
        for args in [([['q']], 'first', 'q'), ([['q', 'a']], 'middle', 'q'), ([['q', 'a']], 'first', 'o')]:
            with self.assertRaises(ValueError):
                measure(*args)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            strict_json(b'{"flag":true,"flag":1}')


if __name__ == '__main__':
    unittest.main()
