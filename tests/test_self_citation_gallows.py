import copy
import unittest

from scripts.ablate_self_citation_paragraph_gallows import PREDICATE, ZERO, ablate, paired_cells, response_summary


def eight_cells(value):
    return {'cells': [{'model_paragraph_initial': start, 'boundary': boundary, 'prefix': prefix,
                       'eligible_rows': 2, 'mean_difference_exact': {'numerator': str(value), 'denominator': '4'}}
                      for start in [False, True] for boundary in ['first', 'last'] for prefix in ['q', 'y']]}


class ParagraphGallowsTests(unittest.TestCase):
    def test_patch_changes_only_paragraph_condition_and_retains_other_threshold_reference(self):
        other = b'rand < Constants.PARAGRAPH_STARTS_WITH_GALLOW_PROPABILITY'
        raw = b'// synthetic surrounding bytes\n' + PREDICATE + b'\n' + other + b'\n'
        changed = ablate(raw)
        self.assertEqual(changed.replace(ZERO, PREDICATE), raw)
        self.assertIn(other, changed)
        for bad in [other, PREDICATE + PREDICATE]:
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                ablate(bad)

    def test_pairing_uses_cell_identity_and_keeps_different_denominators(self):
        default, variant = eight_cells(-1), eight_cells(1)
        variant['cells'].reverse()
        variant['cells'][0]['eligible_rows'] = 3
        result = paired_cells(default, variant)
        self.assertEqual(result[0]['default_eligible_rows'], 2)
        self.assertEqual(result[0]['ablated_eligible_rows'], 3)
        self.assertEqual(result[0]['ablated_minus_default_exact'], {'numerator': '1', 'denominator': '2'})
        with self.assertRaisesRegex(ValueError, 'eight-cell'):
            paired_cells(default, {'cells': variant['cells'][:-1]})

    def test_primary_predictions_require_all_twenty_seeds_and_positive_mean(self):
        paired = paired_cells(eight_cells(-1), eight_cells(1))
        cases = [{'seed': seed, 'paired_cells': copy.deepcopy(paired)} for seed in range(1, 21)]
        self.assertTrue(all(row['primary_outcome'] == 'positive' for row in response_summary(cases)
                            if row['primary_directional_prediction']))
        cases[0]['paired_cells'] = None
        self.assertTrue(all(row['primary_outcome'] == 'unresolved' for row in response_summary(cases)
                            if row['primary_directional_prediction']))
        zero = paired_cells(eight_cells(1), eight_cells(1))
        cases = [{'seed': seed, 'paired_cells': zero} for seed in range(1, 21)]
        self.assertTrue(all(row['primary_outcome'] == 'nonpositive' for row in response_summary(cases)
                            if row['primary_directional_prediction']))


if __name__ == '__main__':
    unittest.main()
