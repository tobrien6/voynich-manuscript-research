from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import permutations, product
import unittest

from scripts.prefix_conditional_bounds import bernstein_upper, locus_moments


class PrefixBoundTests(unittest.TestCase):
    def test_binary_moments_match_exhaustive_permutations_exactly(self):
        for tokens in [['q', 'a'], ['q', 'a', 'a'], ['y', 'ya', 'a', 'a']]:
            for boundary in ['first', 'last']:
                for prefix in ['q', 'y']:
                    outcomes = [locus_moments(list(order), boundary, prefix)[0] for order in permutations(tokens)]
                    mean = sum(outcomes, Fraction(0)) / len(outcomes)
                    actual_variance = sum((value - mean) ** 2 for value in outcomes) / len(outcomes)
                    self.assertEqual(mean, 0)
                    self.assertEqual(locus_moments(tokens, boundary, prefix)[1], actual_variance)
                    self.assertTrue(all(abs(value) <= 1 for value in outcomes))

    def test_independent_locus_variances_add_under_the_declared_control(self):
        rows = [['q', 'a'], ['q', 'a', 'a']]
        outcomes = [sum((locus_moments(list(order), 'first', 'q')[0] for order in orders), Fraction(0))
                    for orders in product(*[list(permutations(row)) for row in rows])]
        variance = sum(value ** 2 for value in outcomes) / len(outcomes)
        self.assertEqual(variance, sum((locus_moments(row, 'first', 'q')[1] for row in rows), Fraction(0)))

    def test_bound_is_above_a_known_exact_tail(self):
        # Eight independent rows with [q, a, a]: maximum sum 8 occurs with probability (1/3)^8.
        result = bernstein_upper(Fraction(8), Fraction(4), 96)
        bound = Decimal(result['two_sided_upper_decimal'])
        with localcontext() as context:
            context.prec = 80
            exact_tail = Decimal(1) / Decimal(3) ** 8
        self.assertGreaterEqual(bound, exact_tail)
        self.assertLessEqual(bound, 1)

    def test_bounds_cover_every_attainable_small_joint_tail(self):
        for rows in [
                [['q', 'a'], ['q', 'a', 'a']],
                [['q', 'a', 'a'], ['q', 'q', 'a', 'a']],
                [['q', 'a'], ['q', 'a', 'a'], ['q', 'a', 'a', 'a']]]:
            outcomes = [sum((locus_moments(list(order), 'first', 'q')[0] for order in orders), Fraction(0))
                        for orders in product(*[list(permutations(row)) for row in rows])]
            variance = sum((locus_moments(row, 'first', 'q')[1] for row in rows), Fraction(0))
            for threshold in {abs(value) for value in outcomes}:
                tail = Fraction(sum(abs(value) >= threshold for value in outcomes), len(outcomes))
                result = bernstein_upper(threshold, variance, 96)
                upper = Decimal(result['two_sided_upper_decimal'])
                with localcontext() as context:
                    context.prec = 100
                    exact_tail = Decimal(tail.numerator) / Decimal(tail.denominator)
                self.assertGreaterEqual(upper, exact_tail)
                self.assertGreaterEqual(Decimal(result['family_adjusted_upper_decimal']), upper)
                self.assertLessEqual(Decimal(result['family_adjusted_upper_decimal']), 1)

    def test_numeric_rounding_is_outward_and_large_bounds_do_not_underflow(self):
        result = bernstein_upper(Fraction(50, 3), Fraction(7, 5), 96)
        exponent = Fraction(50, 3) ** 2 / (2 * Fraction(7, 5) + Fraction(2, 3) * Fraction(50, 3))
        with localcontext() as context:
            context.prec = 100
            target = 2 * (-(Decimal(exponent.numerator) / Decimal(exponent.denominator))).exp()
        self.assertGreaterEqual(Decimal(result['two_sided_upper_decimal']), target)
        extreme = bernstein_upper(Fraction(10000), Fraction(1), 96)
        self.assertGreater(Decimal(extreme['two_sided_upper_decimal']), 0)
        self.assertEqual(bernstein_upper(0, 0, 96)['two_sided_upper_decimal'], '1')
        with self.assertRaises(ValueError):
            bernstein_upper(1, 0, 96)


if __name__ == '__main__':
    unittest.main()
