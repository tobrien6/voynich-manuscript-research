from fractions import Fraction
import itertools
import unittest

from scripts import verify_interior_covariance as m


class IndependentJointTests(unittest.TestCase):
    def test_subset_updates_match_explicit_signed_injective_assignment(self):
        pairs=[(-2,3),(1,-1),(0,2),(3,1)]
        for powers in ((),((1,1),),((1,0),(0,1)),((1,1),(1,1)),((1,0),(1,0),(0,1),(0,1))):
            choices=list(itertools.permutations(range(4),len(powers)));total=0
            for choice in choices:
                value=1
                for j,(a,b) in zip(choice,powers):value*=pairs[j][0]**a*pairs[j][1]**b
                total+=value
            self.assertEqual(m.block(pairs,powers),Fraction(total,len(choices)))

    def test_direct_edge_joint_moments_match_complete_uniform_permutations(self):
        left=[1,3,2,1,1];right=[2,1,3,2,1]
        for scope in ('unrestricted','half'):
            cut=5 if scope=='unrestricted' else 3
            orders=[a+tuple(j+cut for j in b) for a in itertools.permutations(range(cut)) for b in itertools.permutations(range(5-cut))]
            values=[(m.association([left[j] for j in order]),m.association([right[j] for j in order])) for order in orders]
            means=[sum((v[i] for v in values),Fraction())/len(values) for i in (0,1)]
            cov=sum(((a-means[0])*(b-means[1]) for a,b in values),Fraction())/len(values)
            self.assertEqual(m.joint(left,right,scope),(*means,cov))

    def test_literal_longest_match_case_and_original_boundaries(self):
        self.assertEqual(m.count('cthchChiin',['cth','ch','iin','in']),5)
        self.assertEqual(m.count('Ch',['ch']),2)
        self.assertEqual(m.count('iiin',['iin','in']),2)


if __name__=='__main__':unittest.main()
