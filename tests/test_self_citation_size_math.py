from fractions import Fraction
import unittest

from scripts import verify_self_citation_size_math as m


class IndependentSizeMathTests(unittest.TestCase):
    def test_frequency_multiplication_matches_known_exact_weighted_scores(self):
        first=m.independent.exact([1,2,3]);second=m.independent.exact([1,2,3,4])
        ids=('ascii_letters','bench_sequences','bench_and_minim_sequences')
        cells={5:{'n':1,'means':{p:list(first) for p in ids}},6:{'n':100,'means':{p:list(second) for p in ids}}}
        result=m.standard(cells,{5:2,6:1})
        for means in result.values():
            self.assertEqual(means[3],Fraction(5,9))
            self.assertEqual(means[4],Fraction(19,60))

    def test_missing_size_returns_undefined_without_renormalizing_remaining_weight(self):
        ids=('ascii_letters','bench_sequences','bench_and_minim_sequences')
        cells={5:{'n':1,'means':{p:[Fraction(1)]*5 for p in ids}},6:{'n':0,'means':{p:[None]*5 for p in ids}}}
        self.assertTrue(all(means==[None]*5 for means in m.standard(cells,{5:99,6:1}).values()))

    def test_empty_source_cohort_does_not_create_zero_scores(self):
        self.assertTrue(all(means==[None]*5 for means in m.standard({},{}).values()))


if __name__=='__main__':
    unittest.main()
