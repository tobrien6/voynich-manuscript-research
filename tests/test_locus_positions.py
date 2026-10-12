from itertools import permutations
import unittest
from unittest.mock import patch

from scripts.ivtff import parse_ivtff
from scripts.locus_positions import conditional_variance, contrast, position_report, prepare_rows, summarize_position


class PositionControlsTests(unittest.TestCase):
    def test_additional_alphabets_do_not_enter_the_paired_eva_analysis(self):
        eva = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> q.a\n')
        v101 = parse_ivtff('#=IVTFF v101 2.0 M\n<f1r>\n<f1r.1,@P0> a!b\n')
        sources = [({'id': 'GC2a', 'sha256': 'synthetic'}, v101),
                   ({'id': 'ZL3b', 'sha256': 'synthetic'}, eva),
                   ({'id': 'IT2a', 'sha256': 'synthetic'}, eva)]
        with patch('scripts.locus_positions.load_sources', return_value=sources):
            result = position_report(repetitions=1, seed=1)
        self.assertEqual([source['id'] for source in result['sources']], ['ZL3b', 'IT2a'])
        self.assertEqual(result['selection']['count'], 1)

    def test_exact_null_variance_matches_exhaustive_permutations(self):
        for values in [[1, 0, 0], [1, 2, 3], [2, 2], [0, 1, 2, 2]]:
            for edge in [0, -1]:
                null = [contrast(list(p), edge) for p in permutations(values)]
                mean = sum(null) / len(null)
                variance = sum((value - mean) ** 2 for value in null) / len(null)
                self.assertAlmostEqual(mean, 0)
                self.assertAlmostEqual(conditional_variance(values), variance)

    def test_an_excluded_first_token_is_not_replaced_by_the_next(self):
        doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> ?.q.a\n')
        rows = prepare_rows(doc.loci, 'split', 'exclude')
        first = summarize_position(rows, 'first', 9, 1)
        last = summarize_position(rows, 'last', 9, 1)
        self.assertEqual(first['eligible_loci'], 0)
        self.assertIsNone(first['features'][0]['paired_difference'])
        self.assertEqual(last['eligible_loci'], 1)
        self.assertEqual(last['features'][0]['paired_difference'], -1)

    def test_every_locus_has_equal_weight_even_with_different_lengths(self):
        doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n'
                          '<f1r.1,@P0> q.a\n<f1r.2,+P0> a.q.q.q\n')
        result = summarize_position(prepare_rows(doc.loci, 'split', 'exclude'), 'first', 9, 1)
        q = result['features'][0]
        self.assertEqual(q['mean_boundary_feature'], .5)
        self.assertEqual(q['mean_locus_other_feature'], .5)
        self.assertEqual(q['paired_difference'], 0)

    def test_lone_retained_tokens_do_not_form_position_contrasts(self):
        doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> q.?\n')
        result = summarize_position(prepare_rows(doc.loci, 'split', 'exclude'), 'first', 9, 1)
        self.assertEqual(result['eligible_loci'], 0)
        self.assertEqual(result['ineligible_reasons_may_overlap']['fewer_than_two_retained'], 1)


if __name__ == '__main__':
    unittest.main()
