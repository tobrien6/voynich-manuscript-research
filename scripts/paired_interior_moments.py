"""Exact bivariate adjacent-association moments under shared permutations."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from math import factorial,prod


@lru_cache(maxsize=5)
def partitions(size):
    if type(size) is not int or not 0<=size<=4:
        raise ValueError('set-partition degree must be0..4')
    if size==0:return ((),)
    result=[]
    for partition in partitions(size-1):
        result.append(partition+((size-1,),))
        for j,block in enumerate(partition):
            result.append(partition[:j]+(block+(size-1,),)+partition[j+1:])
    return tuple(result)


def block_product(pairs,exponents):
    """Distinct-occurrence bivariate product by partition inclusion-exclusion."""
    if any(len(pair)!=2 or any(type(v) is not int for v in pair) for pair in pairs):
        raise ValueError('paired signed integer occurrence values required')
    if (any(len(p)!=2 or any(type(v) is not int or v<0 for v in p) or sum(p)<1 for p in exponents)
            or sum(sum(p) for p in exponents)>4 or len(exponents)>len(pairs)):
        raise ValueError('positive position degrees must total at most4 and fit the block')
    sums={};total=0
    for partition in partitions(len(exponents)):
        coefficient=prod((-1)**(len(block)-1)*factorial(len(block)-1) for block in partition)
        term=coefficient
        for block in partition:
            powers=tuple(sum(exponents[j][axis] for j in block) for axis in (0,1))
            if powers not in sums:sums[powers]=sum(a**powers[0]*b**powers[1] for a,b in pairs)
            term*=sums[powers]
        total+=term
    return Fraction(total,prod(range(len(pairs)-len(exponents)+1,len(pairs)+1)))


@lru_cache(maxsize=128)
def edge_patterns(size,scope):
    if type(size) is not int or size<3 or scope not in ('unrestricted','half'):
        raise ValueError('at least3 positions and a declared scope required')
    cut=size if scope=='unrestricted' else (size+1)//2
    def signature(first,second=()):
        factors={}
        for position in first:
            factors.setdefault(position,[0,0])[0]+=1
        for position in second:
            factors.setdefault(position,[0,0])[1]+=1
        return tuple(tuple(sorted(tuple(powers) for position,powers in factors.items() if (position<cut)==(block==0)))
                     for block in (0,1))
    edges=[(j,j+1) for j in range(size-1)]
    means=Counter(signature(edge) for edge in edges)
    cross=Counter(signature(a,b) for a in edges for b in edges)
    return tuple(sorted(means.items())),tuple(sorted(cross.items()))


def joint_moment(left,right,scope):
    if (not isinstance(left,(tuple,list)) or not isinstance(right,(tuple,list)) or len(left)!=len(right)
            or len(left)<3 or any(type(v) is not int or v<1 for v in list(left)+list(right))):
        raise ValueError('equal-sized positive integer count vectors with at least3 positions required')
    size=len(left);total_left,total_right=sum(left),sum(right)
    a=[size*v-total_left for v in left];b=[size*v-total_right for v in right]
    da,db=sum(v*v for v in a),sum(v*v for v in b)
    cut=size if scope=='unrestricted' else (size+1)//2
    blocks=(list(zip(a[:cut],b[:cut])),list(zip(a[cut:],b[cut:])))
    cache={}
    def moment(signature,swap=False):
        answer=Fraction(1)
        for j,powers in enumerate(signature):
            if swap:powers=tuple(sorted((v,u) for u,v in powers))
            key=j,powers
            if key not in cache:cache[key]=block_product(blocks[j],powers)
            answer*=cache[key]
        return answer
    first,cross=edge_patterns(size,scope)
    ea=sum((n*moment(p) for p,n in first),Fraction())
    eb=sum((n*moment(p,True) for p,n in first),Fraction())
    eab=sum((n*moment(p) for p,n in cross),Fraction())
    scale_a=Fraction(size,(size-1)*da) if da else Fraction()
    scale_b=Fraction(size,(size-1)*db) if db else Fraction()
    return {'left_mean':scale_a*ea,'right_mean':scale_b*eb,
            'covariance':scale_a*scale_b*(eab-ea*eb)}


def validate_psd(matrix):
    if len(matrix)!=3 or any(len(row)!=3 for row in matrix):
        raise ValueError('three-policy covariance matrix required')
    if any(matrix[i][j]!=matrix[j][i] for i in range(3) for j in range(3)):
        raise ValueError('covariance symmetry failed')
    if any(matrix[i][i]<0 for i in range(3)):
        raise ValueError('negative variance')
    if any(matrix[i][i]*matrix[j][j]-matrix[i][j]**2<0 for i in range(3) for j in range(i+1,3)):
        raise ValueError('negative covariance principal minor')
    a,b,c=matrix[0];_,d,e=matrix[1];_,_,f=matrix[2]
    if a*d*f+2*b*c*e-a*e*e-d*c*c-f*b*b<0:
        raise ValueError('negative covariance determinant')
    return True


def policy_matrix(vectors,scope):
    if len(vectors)!=3:raise ValueError('all3 paired count vectors required')
    matrix=[[Fraction() for _ in range(3)] for _ in range(3)];means=[]
    for i in range(3):
        for j in range(i,3):
            value=joint_moment(vectors[i],vectors[j],scope)
            matrix[i][j]=matrix[j][i]=value['covariance']
            if i==j:means.append(value['left_mean'])
    validate_psd(matrix)
    return means,matrix


def paired_variance(matrix,other):
    validate_psd(matrix)
    if type(other) is not int or other not in (1,2):raise ValueError('grouped policy index1or2 required')
    result=matrix[other][other]+matrix[0][0]-2*matrix[other][0]
    if result<0:raise ValueError('negative paired variance')
    return result
