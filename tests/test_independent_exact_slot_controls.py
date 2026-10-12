import copy
import gzip
import json
import unittest

from scripts import verify_exact_slot_predictor_controls as m
from scripts import exact_slot_predictor_controls as runner
from scripts.shuffle_token_lines import HashDraws


class IndependentControlTests(unittest.TestCase):
    def test_separate_byte_stream_matches_rejection_sampler_including_ten_class_draws(self):
        for key in (bytes(32), bytes(range(32)), b'known-key'):
            independent, original = m.ByteStream(key), HashDraws(key)
            bounds = [4, 10, 10, 4] * 256
            self.assertEqual([independent.below(b) for b in bounds], [original.below(b) for b in bounds])
            self.assertEqual(independent.index, original.counter)

    def test_independent_all_process_rows_and_oracles_match_local_invented_cases(self):
        _, _, _, generator, _ = runner.load_inputs()
        templates = [{'key': 'separate-one', 'page': 'f1r', 'group': 'g', 'label': 'A', 'interior_size': 50},
                     {'key': 'separate-two', 'page': 'f1v', 'group': 'h', 'label': 'B', 'interior_size': 31}]
        for case in m.CASES:
            for replicate in (0, 31, 63):
                rows = m.rows_for(templates, case, replicate)
                self.assertEqual(rows, runner.generate(templates, replicate, case, generator))
                expected = runner.alternating_oracle(rows) if case == m.CASES[3] else generator.oracle_score(rows, generator.CASES[case])
                self.assertEqual(m.oracle(rows, case), expected)

    def test_complete_case_summaries_and_typed_comparison_preserve_adverse_values(self):
        rows = []
        for i in range(64):
            contrasts = {c: {'micro_gain_bits_per_transition': -float(i+1),
                             'group_macro_gain_bits_per_transition': float(i-32),
                             'locus_macro_gain_bits_per_transition': 0.,
                             'fixed_diagnostic_preference': False} for c in m.CONTRASTS}
            rows.append({'replicate': i, 'summary': {'contrasts': contrasts}, 'oracle': {'gain_bits_per_transition': 0.}})
        m.compare(m.case_summary(rows), runner.summaries(rows))
        for replacement in ({'n': False}, {'n': 0.0}, {'n': 0, 'extra': True}, {}):
            with self.assertRaises(ValueError):
                m.compare({'n': 0}, replacement)

    def test_original_rule_receipt_uses_existing_losses_without_changing_report(self):
        record = {'summary': {'loss_bits': {'Q0': 3., 'Q1': 2.}, 'transitions': 1},
                  'groups': [{'loss_bits': {'Q0': 3., 'Q1': 2.}, 'transitions': 1}],
                  'folds': [{'loss_bits': {'Q0': 2. if i < 4 else 1., 'Q1': 1. if i < 4 else 2.}} for i in range(5)]}
        records = [dict(copy.deepcopy(record), replicate=i) for i in range(64)]
        report = {'cases': [{'case': 'invented', 'replicates': records}]}
        before = copy.deepcopy(report)
        packed = gzip.compress(json.dumps(report).encode(), mtime=0)
        receipt = m.coarse_receipt(report, packed)
        self.assertEqual(receipt['cases'][0]['original_coarse_criterion_hits'], 64)
        self.assertEqual(receipt['cases'][0]['original_coarse_mean_pooled_gain'], 1.)
        self.assertEqual(receipt['cases'][0]['replicates'][0]['original_coarse_positive_folds'], 4)
        self.assertEqual(report, before)


if __name__ == '__main__':
    unittest.main()
