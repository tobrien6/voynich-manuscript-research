from fractions import Fraction
import unittest

from scripts import verify_exact_slot_length_prediction as m


class IndependentExactSlotTests(unittest.TestCase):
    def test_separate_weighted_formula_matches_hand_cases_and_backoffs(self):
        rows = [{'key': 'a', 'values': [1, 2, 1, 2], 'label': 'A'},
                {'key': 'b', 'values': [2, 3, 1, 2], 'label': 'A'}]
        tables = m.train_tables(rows)
        self.assertEqual(m.probabilities(tables, ('A', 4, 1), 1, 2)[0][2:], (Fraction(2, 9), Fraction(11, 36)))
        self.assertEqual(m.probabilities(tables, ('A', 4, 1), 2, 2)[0][2:], (Fraction(2, 9), Fraction(5, 36)))
        self.assertEqual(m.probabilities(tables, ('A', 7, 5), 1, 2)[0][2:], (Fraction(3, 14), Fraction(3, 14)))
        for y in range(1, 11):
            first = m.probabilities(tables, ('A', 4, 1), 1, y)[0]
            second = m.probabilities(tables, ('A', 4, 1), 2, y)[0]
            self.assertEqual((first[3] + second[3]) / 2, first[2])
        constant = m.train_tables([{'values': [1, 2, 1, 2], 'label': 'A'}, {'values': [1, 3, 2, 2], 'label': 'A'}])
        for x in range(1, 11):
            for y in range(1, 11):
                probabilities, support = m.probabilities(constant, ('A', 4, 1), x, y)
                self.assertEqual(probabilities[2], probabilities[3])
                self.assertTrue(support[3])

    def test_union_find_keeps_transitive_full_canvas_dependencies(self):
        rows = [{'explicit_folio_sides': '88r', 'canvas_uri': 'c1'},
                {'explicit_folio_sides': '88v;89r', 'canvas_uri': 'c2'},
                {'explicit_folio_sides': '89v;90r', 'canvas_uri': 'c3'},
                {'explicit_folio_sides': '90v', 'canvas_uri': 'c4'},
                {'explicit_folio_sides': '', 'canvas_uri': 'unlabelled'}]
        groups, indexed = m.union_groups(rows)
        self.assertEqual(groups, [{'group_id': 'yale-leaves:88+89+90', 'folio_ids': ['88', '89', '90']}])
        self.assertEqual(indexed, {'88': ['c1', 'c2'], '89': ['c2', 'c3'], '90': ['c3', 'c4']})

    def test_complete_independent_exclusions_and_typed_scalar_guards(self):
        def record(**changes):
            return {'locus_type': 'P0', 'eligible': True, 'exclusion_reasons': [],
                    'drawing_interruption_count': 0, 'token_count': 5, **changes}
        mappings = {identity: {'keep': record(), 'short': record(token_count=4),
                              'draw': record(drawing_interruption_count=1),
                              'ambiguous': record(eligible=False, exclusion_reasons=['unreadable']),
                              'absent': record(eligible=False, exclusion_reasons=['nonexistent_locus'])}
                    for identity in m.VARIANTS}
        result = m.cohort(mappings)
        self.assertEqual(result['retained_locus_keys'], ['keep'])
        self.assertEqual(result['excluded_loci'], 3)
        self.assertEqual(result['shared_present_P0_loci'], 4)
        self.assertEqual(result['eligible_in_all_adapters'], 3)
        for item, suffix in zip(result['exclusions'], ('unreadable', 'drawing_interruption', 'fewer_than_five_tokens')):
            self.assertEqual(item['reasons'], sorted(s+'/'+p+':'+suffix for s, p in m.VARIANTS))
        for changed in ({'n': False}, {'n': 0.0}, {}, {'n': 0, 'extra': True}):
            with self.assertRaises(ValueError):
                m.compare({'n': 0}, changed)


if __name__ == '__main__':
    unittest.main()
