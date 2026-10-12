from fractions import Fraction
import itertools
import unittest

from scripts import verify_self_citation_interior_math as independent


class IndependentInteriorMathTests(unittest.TestCase):
    def test_literal_case_and_longest_match_inside_original_tokens(self):
        patterns=['ch','cth','iin','in']
        self.assertEqual(independent.count_units('cthchChiin',patterns),['cth','ch','C','h','iin'])
        self.assertEqual(independent.count_units('iiin',patterns),['i','iin'])
        self.assertEqual(independent.count_units('cthh',patterns),['cth','h'])

    def test_expanded_moments_match_exhaustive_full_and_half_ensembles(self):
        def association(values):
            n=len(values);mean=Fraction(sum(values),n)
            centered=[value-mean for value in values]
            squared=sum(x*x for x in centered)
            return Fraction(n,n-1)*sum(a*b for a,b in zip(centered,centered[1:]))/squared if squared else Fraction(0)
        for values in ([1,2,3],[1,3,2,1,1],[2,2,2],[1,1,3,3],[1,1,2]):
            cut=(len(values)+1)//2
            full=list(itertools.permutations(values))
            half=[a+b for a in itertools.permutations(values[:cut]) for b in itertools.permutations(values[cut:])]
            raw=association(values)
            full_mean=sum(map(association,full),Fraction(0))/len(full)
            half_mean=sum(map(association,half),Fraction(0))/len(half)
            with self.subTest(values=values):
                self.assertEqual(independent.exact(values),(raw,full_mean,half_mean,raw-full_mean,raw-half_mean))

    def test_truncated_policy_profiles_fail_instead_of_reporting_partial_verification(self):
        with self.assertRaises(AssertionError):
            independent.check([],[],[{'id':'ascii_letters','patterns':[]}])


if __name__=='__main__':
    unittest.main()
