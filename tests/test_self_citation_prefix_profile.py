from copy import deepcopy
from fractions import Fraction
from types import SimpleNamespace
import unittest

from scripts.locus_positions import contrast
from scripts.self_citation_prefix_profile import (finite_ranges, packed, prefix_contrast,
                                                  profile, select_target)


def fixtures():
    sources = []
    for source, pin in [('ZL3b', 'zl'), ('IT2a', 'it')]:
        loci = [SimpleNamespace(key=f'f1r.{number}', kind='P0', present=True,
                                variables={'L': 'A' if number == 2 else 'B'},
                                text=('<%>q.a' if source == 'ZL3b' and number == 1 else 'q.a'))
                for number in range(1, 5)]
        sources.append(({'id': source, 'sha256': pin, 'path': 'synthetic.txt',
                         'url': 'https://example.test/source', 'alphabet': 'Eva-'},
                        SimpleNamespace(loci=loci)))
    payloads = []
    for spacing in ['split', 'join']:
        records = [{'source_id': source, 'locus_key': f'f1r.{number}', 'locus_type': 'P0',
                    'locator': '+', 'eligible': True, 'tokens': ['q', 'a'],
                    'token_count': 2, 'exclusion_reasons': [], 'drawing_interruption_count': 0}
                   for source in ['ZL3b', 'IT2a'] for number in range(1, 5)]
        payloads.append({'schema_version': 1, 'adapter_version': 'plain-eva-v1',
                         'analysis_unit': 'transcription_locus',
                         'processing': {'uncertain_space_policy': spacing, 'selected_locus_types': ['P0'],
                                        'ambiguity_policy': 'exclude entire selected locus with explicit reasons'},
                         'sources': [{'id': 'ZL3b', 'sha256': 'zl'}, {'id': 'IT2a', 'sha256': 'it'}],
                         'records': records})
    payloads[1]['records'][6]['drawing_interruption_count'] = 1  # IT/join f1r.3
    payloads[0]['records'][3].update(eligible=False, tokens=None, token_count=None,
                                   exclusion_reasons=['alternative_reading'])
    return sources, payloads


def comparison_fixture():
    base = profile([('a', ['q', 'a'], False), ('b', ['q', 'a'], True)])
    target = {'variants': [{'source_id': source, 'spacing': spacing, 'profile': deepcopy(base)}
                           for source in ['ZL3b', 'IT2a'] for spacing in ['split', 'join']]}
    cases = [{'seed': seed, 'accepted': True, 'profile': deepcopy(base)} for seed in [1, 2]]
    for variant in target['variants']:
        next(row for row in variant['profile'] if row['paragraph_initial'] and
             row['boundary'] == 'first' and row['prefix'] == 'q')['contrast'] = packed(Fraction(3, 4))
    for case, value in zip(cases, [Fraction(1, 4), Fraction(1, 2)]):
        next(row for row in case['profile'] if row['paragraph_initial'] and
             row['boundary'] == 'first' and row['prefix'] == 'q')['contrast'] = packed(value)
    return target, cases


class SelfCitationProfileTests(unittest.TestCase):
    def test_exact_contrast_matches_the_accepted_definition_and_literal_case(self):
        groups = ['y', 'q', 'a', 'y']
        self.assertEqual(prefix_contrast(groups, 'first', 'y'), Fraction(2, 3))
        self.assertAlmostEqual(float(prefix_contrast(groups, 'first', 'y')), contrast([1, 0, 0, 1], 0))
        self.assertEqual(prefix_contrast(['Q', 'a'], 'first', 'q'), 0)
        for bad in (['q'], ['q', 'a.b'], ['q', '']):
            with self.assertRaises(ValueError):
                prefix_contrast(bad, 'first', 'q')

    def test_unit_weighting_is_equal_and_empty_contexts_remain_undefined(self):
        result = profile([('short', ['q', 'a'], False), ('long', ['a', 'q', 'q', 'q'], False)])
        first_q = next(row for row in result if not row['paragraph_initial'] and
                       row['boundary'] == 'first' and row['prefix'] == 'q')
        self.assertEqual(first_q['contrast'], packed(Fraction()))
        self.assertEqual(first_q['group_occurrences'], 6)
        self.assertTrue(all(row['contrast'] is None for row in result if row['paragraph_initial']))
        for bad in ([('x', ['q', 'a'], False), ('x', ['q', 'a'], True)], [('x', ['q', 'a'], None)]):
            with self.assertRaises(ValueError):
                profile(bad)

    def test_common_selection_uses_both_labels_all_policies_and_native_annotations(self):
        sources, payloads = fixtures()
        result = select_target(sources, payloads)
        self.assertEqual(result['selected_keys'], ['f1r.1'])
        self.assertEqual(result['accepted_common_cohort'], 3)
        self.assertEqual(result['common_cohort_exclusions'][0]['locus_key'], 'f1r.4')
        self.assertEqual([row['locus_key'] for row in result['additional_exclusions']], ['f1r.2', 'f1r.3'])
        for variant in result['variants']:
            populated = [row for row in variant['profile'] if row['rows']]
            self.assertEqual({row['paragraph_initial'] for row in populated}, {variant['source_id'] == 'ZL3b'})

    def test_duplicate_sources_loci_and_missing_drawing_identity_are_rejected(self):
        for change in ('source', 'key', 'drawing'):
            sources, payloads = fixtures()
            if change == 'source':
                sources[1][0]['id'] = 'ZL3b'
            elif change == 'key':
                sources[0][1].loci.append(deepcopy(sources[0][1].loci[0]))
            else:
                payloads[0]['records'][0]['drawing_interruption_count'] = None
            with self.subTest(change=change), self.assertRaises(ValueError):
                select_target(sources, payloads)

    def test_every_planned_point_has_inclusive_ranges_and_exact_outside_gaps(self):
        target, cases = comparison_fixture()
        result = finite_ranges(target, cases, [1, 2])
        self.assertEqual(len(result), 32)
        outside = [row for row in result if row['within_fixed_seed_range'] is False]
        self.assertEqual(len(outside), 4)
        self.assertTrue(all(row['outside_range_gap'] == packed(Fraction(1, 4)) for row in outside))
        self.assertTrue(all(row['outside_range_gap'] == packed(Fraction()) for row in result
                            if row['within_fixed_seed_range']))

    def test_an_undefined_seed_stratum_is_not_dropped_from_its_range(self):
        target, cases = comparison_fixture()
        cases[1]['profile'] = profile([('only-context', ['q', 'a'], False)])
        result = finite_ranges(target, cases, [1, 2])
        self.assertTrue(all(row['within_fixed_seed_range'] is None and row['seed_minimum'] is None
                            for row in result if row['paragraph_initial']))
        self.assertTrue(all(row['within_fixed_seed_range'] is not None
                            for row in result if not row['paragraph_initial']))

    def test_failed_missing_duplicate_seed_or_statistic_blocks_complete_comparison(self):
        for change in ('failed', 'missing', 'duplicate_seed', 'statistic', 'target', 'false_empty'):
            target, cases = comparison_fixture()
            if change == 'failed':
                cases[0]['accepted'] = False
            elif change == 'missing':
                cases.pop()
            elif change == 'duplicate_seed':
                cases[1]['seed'] = 1
            elif change == 'statistic':
                cases[0]['profile'].pop()
            elif change == 'target':
                target['variants'].pop()
            else:
                cases[0]['profile'][0]['contrast'] = None
            with self.subTest(change=change), self.assertRaises(ValueError):
                finite_ranges(target, cases, [1, 2])


if __name__ == '__main__':
    unittest.main()
