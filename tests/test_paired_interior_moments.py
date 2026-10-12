from fractions import Fraction
import itertools
import unittest

from scripts import paired_interior_moments as m


def raw(values):
    n=len(values);average=Fraction(sum(values),n);d=[v-average for v in values];q=sum(v*v for v in d)
    return Fraction(n,n-1)*sum(a*b for a,b in zip(d,d[1:]))/q if q else Fraction()


def ensemble(left,right,scope):
    n=len(left);cut=n if scope=='unrestricted' else (n+1)//2
    orders=[a+tuple(v+cut for v in b) for a in itertools.permutations(range(cut)) for b in itertools.permutations(range(n-cut))]
    pairs=[(raw([left[j] for j in order]),raw([right[j] for j in order])) for order in orders]
    a=sum((v[0] for v in pairs),Fraction())/len(pairs);b=sum((v[1] for v in pairs),Fraction())/len(pairs)
    covariance=sum(((x-a)*(y-b) for x,y in pairs),Fraction())/len(pairs)
    return {'left_mean':a,'right_mean':b,'covariance':covariance}


class PairedMomentTests(unittest.TestCase):
    def test_partition_counts_and_signed_block_moments_against_injective_assignments(self):
        self.assertEqual([len(m.partitions(n)) for n in range(5)],[1,1,2,5,15])
        pairs=[(-2,3),(1,-1),(0,4),(3,2)]
        patterns=[(),((1,1),),((1,0),(0,1)),((1,1),(1,1)),((1,0),(1,0),(0,1)),((1,0),(1,0),(0,1),(0,1))]
        for pattern in patterns:
            assignments=list(itertools.permutations(range(len(pairs)),len(pattern)))
            values=[]
            for assigned in assignments:
                product=1
                for j,(u,v) in zip(assigned,pattern):product*=pairs[j][0]**u*pairs[j][1]**v
                values.append(product)
            with self.subTest(pattern=pattern):self.assertEqual(m.block_product(pairs,pattern),Fraction(sum(values),len(values)))

    def test_all_small_trinary_pairs_against_complete_occurrence_permutations(self):
        vectors=list(itertools.product((1,2,3),repeat=3))
        for left in vectors:
            for right in vectors:
                for scope in ('unrestricted','half'):
                    with self.subTest(left=left,right=right,scope=scope):self.assertEqual(m.joint_moment(left,right,scope),ensemble(left,right,scope))

    def test_shared_disjoint_crossing_and_repeated_edges_on_larger_fixtures(self):
        fixtures=[([1,2,3,4],[4,1,2,2]),([1,3,2,1,1],[2,2,1,3,1]),([1,2,1,3,2,4],[3,1,2,2,4,1]),([1,1,3,3],[2,4,2,4])]
        for left,right in fixtures:
            for scope in ('unrestricted','half'):
                with self.subTest(left=left,scope=scope):self.assertEqual(m.joint_moment(left,right,scope),ensemble(left,right,scope))

    def test_affine_statistics_constant_transitions_and_zero_paired_variance(self):
        left=[1,3,2,4,1]
        for right in ([2*v+7 for v in left],[10-v for v in left]):
            for scope in ('unrestricted','half'):
                result=m.joint_moment(left,right,scope);variance=m.joint_moment(left,left,scope)['covariance']
                self.assertEqual(result['left_mean'],result['right_mean']);self.assertEqual(result['covariance'],variance)
                means,matrix=m.policy_matrix([left,right,[3]*5],scope)
                self.assertEqual(m.paired_variance(matrix,1),0);self.assertEqual(m.paired_variance(matrix,2),variance)
        for scope in ('unrestricted','half'):
            self.assertEqual(m.joint_moment([2]*5,left,scope)['covariance'],0)

    def test_symmetry_psd_and_input_immutability(self):
        vectors=[[1,2,4,2,3],[2,1,3,1,2],[1,1,2,3,4]];before=[list(v) for v in vectors]
        for scope in ('unrestricted','half'):
            means,matrix=m.policy_matrix(vectors,scope);self.assertTrue(m.validate_psd(matrix))
            for i in range(3):
                for j in range(3):self.assertEqual(matrix[i][j],m.joint_moment(vectors[j],vectors[i],scope)['covariance'])
        self.assertEqual(vectors,before)
        for invalid in ([[1,2,0],[2,1,0],[0,0,1]],[[1,0,0],[0,1,2],[0,2,1]]):
            with self.assertRaises(ValueError):m.validate_psd(invalid)

    def test_invalid_dimensions_counts_powers_and_scopes_fail(self):
        for left,right,scope in (([1,2],[1,2],'half'),([1,2,3],[1,2],'half'),([1,True,3],[1,2,3],'half'),([1,0,3],[1,2,3],'half'),([1,2,3],[1,2,3],'other')):
            with self.assertRaises(ValueError):m.joint_moment(left,right,scope)
        for pattern in (((1,0),)*5,((True,0),),((0,0),),((-1,1),)):
            with self.assertRaises(ValueError):m.block_product([(1,2)]*4,pattern)
        self.assertEqual(m.block_product([],()),1)


if __name__=='__main__':unittest.main()
