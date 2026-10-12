from itertools import permutations, product
import unittest
from unittest.mock import patch

from scripts.ivtff import parse_ivtff
from scripts.token_baselines import Token, adjacency, baselines, expected_repeats, paired_sources, retain, summarize, tokenize


class TokenPolicyTests(unittest.TestCase):
    def test_comparator_catalog_growth_does_not_change_the_declared_pair(self):
        eva = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> a.a.b\n')
        v101 = parse_ivtff('#=IVTFF v101 2.0 M\n<f1r>\n<f1r.1,@P0> a!b\n')
        sources = [({'id': 'GC2a', 'sha256': 'synthetic'}, v101),
                   ({'id': 'IT2a', 'sha256': 'synthetic'}, eva),
                   ({'id': 'ZL3b', 'sha256': 'synthetic'}, eva)]
        with patch('scripts.token_baselines.load_sources', return_value=sources):
            report = baselines(repetitions=1, seed=1)
        self.assertEqual([source['id'] for source in report['sources']], ['ZL3b', 'IT2a'])
        self.assertEqual(report['selection']['count'], 1)
        for invalid in (sources[:2], sources + [sources[2]]):
            with self.assertRaisesRegex(ValueError, 'exactly one pinned'):
                paired_sources(invalid)

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

    def test_joining_uncertain_spaces_does_not_repair_invalid_boundaries(self):
        separators = ('.', ',', '<->', '<~>')
        invalid = [separator + 'a' for separator in separators]
        invalid += ['a' + separator for separator in separators]
        invalid += ['a' + left + right + 'b' for left, right in product(separators, repeat=2)]
        invalid += ['a, <!comment> .b', '<%>,a', 'a,<$>', 'a,<@H=2>b,']
        for text, policy in product(invalid, ('split', 'join')):
            with self.subTest(text=text, policy=policy), self.assertRaises(ValueError):
                tokenize(text, policy)

    def test_valid_uncertain_gaps_survive_comments_and_layout_under_both_policies(self):
        text = '<%>a <! , . > , b . c<@H=2><$>'
        self.assertEqual([token.value for token in tokenize(text, 'split')], ['a', 'b', 'c'])
        self.assertEqual([token.value for token in tokenize(text, 'join')], ['ab', 'c'])


if __name__ == '__main__':
    unittest.main()
