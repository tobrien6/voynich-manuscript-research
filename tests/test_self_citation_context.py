import copy
from fractions import Fraction
import unittest

from scripts import ablate_self_citation_context as ablation


def profile(value):
    return [{'paragraph_initial': initial, 'boundary': boundary, 'prefix': prefix,
             'rows': 3, 'group_occurrences': 9, 'contrast': ablation.packed(value)}
            for initial, boundary, prefix in sorted(ablation.shared.PROFILE_IDENTITIES)]


def cells():
    values = {'original': Fraction(1, 10), 'chooser_off': Fraction(2, 10),
              'morpher_off': Fraction(4, 10), 'both_off': Fraction(7, 10)}
    return [{'seed': seed, 'setting': name, 'accepted': True,
             'profile': profile(values[name] + Fraction(seed - 1, 20))}
            for seed in (1, 2) for name, _, _ in ablation.SETTINGS]


class ContextAblationTests(unittest.TestCase):
    def test_exact_call_site_masks_preserve_other_context_uses(self):
        raw = b'head\n' + ablation.CHOOSER + b';\n' + ablation.MORPHER + b';\nif (isParagraphInitial) remember();\n'
        for chooser in (False, True):
            for morpher in (False, True):
                expected = raw
                if chooser:
                    expected = expected.replace(ablation.CHOOSER, ablation.CHOOSER.replace(b'isParagraphInitial', b'false'))
                if morpher:
                    expected = expected.replace(ablation.MORPHER, ablation.MORPHER.replace(b'isParagraphInitial', b'false'))
                self.assertEqual(ablation.ablate_source(raw, chooser, morpher), expected)

    def test_missing_duplicate_anchors_and_nonboolean_masks_are_rejected(self):
        raw = ablation.CHOOSER + b'\n' + ablation.MORPHER
        for broken in (ablation.CHOOSER, raw + ablation.CHOOSER, raw + ablation.MORPHER):
            with self.assertRaises(ValueError):
                ablation.ablate_source(broken, False, False)
        with self.assertRaises(ValueError):
            ablation.ablate_source(raw, 0, False)

    def test_exact_factorial_arithmetic_and_complete_reporting(self):
        grid = ablation.factorial_grid(cells(), [1, 2])
        self.assertEqual((len(grid['profiles']), len(grid['original_relative_differences']),
                          len(grid['two_factor_interactions'])), (32, 24, 8))
        interaction = grid['two_factor_interactions'][0]
        self.assertEqual(ablation.unpack(interaction['summary']['mean']), Fraction(1, 5))
        self.assertEqual(interaction['summary']['positive'], 2)
        self.assertEqual([ablation.unpack(row['summary']['mean']) for row in grid['prediction_differences']],
                         [Fraction(3, 10), Fraction(1, 2)])
        self.assertTrue(grid['directional_prediction_satisfied'])

    def test_empty_stratum_keeps_every_seed_and_invalidates_dependent_prediction(self):
        data = cells()
        for row in data[-1]['profile']:
            if row['paragraph_initial']:
                row.update(rows=0, group_occurrences=0, contrast=None)
        grid = ablation.factorial_grid(data, [1, 2])
        self.assertIsNone(grid['directional_prediction_satisfied'])
        self.assertFalse(grid['all_profile_and_difference_strata_defined'])
        interaction = next(row for row in grid['two_factor_interactions'] if row['paragraph_initial'])
        self.assertEqual(interaction['defined_seed_count'], 1)
        self.assertIsNone(interaction['summary'])
        self.assertEqual(len(interaction['seed_values']), 2)
        self.assertIsNone(interaction['seed_values'][1])

    def test_directional_prediction_fails_for_zero_or_negative_mean(self):
        data = cells()
        for case in data:
            if case['setting'] == 'morpher_off':
                case['profile'] = profile(Fraction(-1, 10))
        self.assertFalse(ablation.factorial_grid(data, [1, 2])['directional_prediction_satisfied'])
        for case in data:
            if case['setting'] == 'morpher_off':
                case['profile'] = copy.deepcopy(next(row['profile'] for row in data
                    if row['seed'] == case['seed'] and row['setting'] == 'original'))
        self.assertFalse(ablation.factorial_grid(data, [1, 2])['directional_prediction_satisfied'])

    def test_missing_unordered_failed_and_duplicate_profile_cells_are_rejected(self):
        data = cells()
        failed = copy.deepcopy(data); failed[0]['accepted'] = False
        duplicate = copy.deepcopy(data); duplicate[0]['profile'][0] = duplicate[0]['profile'][1]
        for changed in (data[:-1], list(reversed(data)), failed, duplicate):
            with self.assertRaises(ValueError):
                ablation.factorial_grid(changed, [1, 2])

    def test_repeat_and_parent_mismatches_block_cell_acceptance(self):
        raw = b'synthetic body\n'
        runs = [{'accepted_trace': True, 'canonical_events_sha256': 'event',
                 'canonical_ledger_sha256': 'ledger'} for _ in range(2)]
        values = [profile(Fraction(1, 3)), profile(Fraction(1, 3))]
        parent = {'output_sha256': {'observed': ablation.digest(raw)}, 'row_ledger_sha256': 'ledger',
                  'profile': values[0], 'excluded_short_rows': []}
        ablation.check_pair(runs, [raw, raw], values, [[], []], parent)
        with self.assertRaises(ValueError):
            ablation.check_pair(runs, [raw, b'changed'], values, [[], []], parent)
        changed = copy.deepcopy(runs); changed[1]['canonical_ledger_sha256'] = 'other'
        with self.assertRaises(ValueError):
            ablation.check_pair(changed, [raw, raw], values, [[], []], parent)
        changed_parent = copy.deepcopy(parent); changed_parent['profile'] = profile(Fraction(1, 2))
        with self.assertRaises(ValueError):
            ablation.check_pair(runs, [raw, raw], values, [[], []], changed_parent)
        changed = copy.deepcopy(runs); changed[0]['accepted_trace'] = False
        with self.assertRaises(ValueError):
            ablation.check_pair(changed, [raw, raw], values, [[], []], parent)


if __name__ == '__main__':
    unittest.main()
