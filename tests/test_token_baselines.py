from itertools import permutations
import unittest

from scripts.ivtff import parse_ivtff
from scripts.token_baselines import Token, adjacency, expected_repeats, retain, summarize, tokenize


class TokenPolicyTests(unittest.TestCase):
    def test_spaces_intrusions_comments_and_tags_have_distinct_meanings(self):
        text = '<%><@H=2>a b,c<! , [x:y]><->d<~>e<$>'
        self.assertEqual([t.value for t in tokenize(text, 'split')], ['ab', 'c', 'd', 'e'])
        self.assertEqual([t.value for t in tokenize(text, 'join')], ['abc', 'd', 'e'])

    def test_alternatives_ligatures_and_rare_codes_remain_traceable(self):
        tokens = tokenize('x[{oh}:ch]y.@133;ch.[:y]', 'split')
        self.assertEqual(tokens[0], Token('x{oh}y', 4, alternative=True))
        self.assertEqual(tokens[1], Token('@133;ch', 3))
        self.assertFalse(retain(tokens[0], 'exclude'))
        self.assertTrue(retain(tokens[0], 'first'))
        self.assertFalse(retain(tokens[2], 'first'))

    def test_unknown_first_choice_is_never_filled_in(self):
        tokens = tokenize('a.[?:x].???', 'join')
        self.assertEqual([retain(t, 'first') for t in tokens], [True, False, False])

    def test_dropped_tokens_do_not_create_false_adjacent_repeats(self):
        values, edges = adjacency([Token('a', 1), None, Token('a', 1), Token('b', 1)])
        self.assertEqual(values, ['a', 'a', 'b'])
        self.assertEqual(edges, [(1, 2)])
        self.assertEqual(sum(values[a] == values[b] for a, b in edges), 0)

    def test_exact_expectation_agrees_with_exhaustive_permutations(self):
        values = ['a', 'a', 'b', 'b']
        edges = [(0, 1), (2, 3)]
        counts = [sum(p[a] == p[b] for a, b in edges) for p in permutations(values)]
        self.assertAlmostEqual(expected_repeats(values, edges), sum(counts) / len(counts))

    def test_summary_matches_small_exact_case_and_marks_empty_edges_undefined(self):
        doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> a.a.b\n')
        result = summarize(doc.loci, 'split', 'exclude', 9, 1)['adjacent_repetition']
        self.assertEqual(result['eligible_pairs'], 2)
        self.assertEqual(result['observed_equal_pairs'], 1)
        self.assertAlmostEqual(result['exact_conditional_expected_pairs'], 2 / 3)
        gap = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> a.?.a\n')
        result = summarize(gap.loci, 'split', 'exclude', 9, 1)['adjacent_repetition']
        self.assertEqual(result['eligible_pairs'], 0)
        self.assertIsNone(result['exploratory_upper_tail'])

    def test_unsupported_or_malformed_text_is_rejected(self):
        for text in ['a..b', '.a', 'a,', 'a<-><~>b', 'a[bc]', 'a[x:y', '@127;',
                     '{a{b}}', 'a<!unclosed', '[a.b:ab]', '[x:@999;]']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                tokenize(text, 'split')


if __name__ == '__main__':
    unittest.main()
