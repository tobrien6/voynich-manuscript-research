from fractions import Fraction
import itertools
import unittest

from scripts import verify_independent_position_length as m


class PositionOracleTests(unittest.TestCase):
    def test_direct_distinct_pair_expectations_match_complete_local_orders(self):
        for vector in ([1, 3, 2], [2, 4, 1, 2], [2, 3, 4, 2, 5], [1, 2, 2, 5, 4, 3], [3, 3, 3]):
            measured = m.edge_scores(vector)
            cut = (len(vector) + 1) // 2
            for scope, orders in (
                ('unrestricted', itertools.permutations(vector)),
                ('half', (a + b for a, b in itertools.product(
                    itertools.permutations(vector[:cut]), itertools.permutations(vector[cut:]))))):
                samples = [m.edge_scores(order)['raw'] for order in orders]
                expected = [sum((r[i] for r in samples), Fraction()) / len(samples) for i in range(3)]
                self.assertEqual(expected, measured[scope + '_expectation'])

    def test_complete_small_process_probabilities_covariance_and_zero_predictions(self):
        settings = {'base': 2, 'half_step_increment': 3, 'gradient_increment': 1}
        flat = m.process('flat', 3, settings)
        step = m.process('half_step', 3, settings)
        self.assertEqual(flat['outcome_count'], 8)
        self.assertEqual(flat['outcome_weight'], ['1', '8'])
        self.assertEqual(flat['constant_outcomes'], 2)
        self.assertEqual(flat['known_zero_predictions'], {'unrestricted': True, 'half': True})
        self.assertEqual(step['known_zero_predictions'], {'half': True})
        expected_covariance = [[['1', '4'] if i == j else ['0', '1'] for j in range(3)] for i in range(3)]
        self.assertEqual(flat['population_count_covariance'], expected_covariance)
        self.assertEqual(step['population_count_covariance'], expected_covariance)
        self.assertEqual(step['population_count_means'], [['5', '2'], ['5', '2'], ['11', '2']])
        self.assertEqual([r[0] for r in flat['outcomes']], ['000', '001', '010', '011', '100', '101', '110', '111'])

    def test_complete_typed_comparison_refuses_missing_or_scalar_substituted_evidence(self):
        m.compare({'values': [['1', '4']], 'count': 0, 'flag': False},
                  {'flag': False, 'count': 0, 'values': [['1', '4']]})
        for changed in ({'count': False}, {'count': 0.0}, {}, {'count': 0, 'extra': True}):
            with self.assertRaises(ValueError):
                m.compare({'count': 0}, changed)


if __name__ == '__main__':
    unittest.main()
