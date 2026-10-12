"""Separate joint covariance check using injective subset DP and direct edges."""
from collections import Counter
from fractions import Fraction
import argparse
import hashlib
import json
import math
from pathlib import Path

try:
    from .eva_token_adapter import build
except ImportError:
    from eva_token_adapter import build

ROOT=Path(__file__).resolve().parents[1]
POLICIES=['ascii_letters','bench_sequences','bench_and_minim_sequences']
UPPER=[(i,j) for i in range(3) for j in range(i,3)]


def decode(value):
    if isinstance(value,list):return Fraction(int(value[0]),int(value[1]))
    base=16 if value.get('encoding')=='base16-integer-strings' else 10
    return Fraction(int(value['numerator'],base),int(value['denominator'],base))


def block(pairs,powers):
    k=len(powers);states=[0]*(2**k);states[0]=1
    for x,y in pairs:
        previous=states;states=previous.copy()
        weights=[x**a*y**b for a,b in powers]
        for mask,value in enumerate(previous):
            for j,w in enumerate(weights):
                if not mask&(1<<j):states[mask|(1<<j)]+=value*w
    return Fraction(states[-1],math.prod(len(pairs)-j for j in range(k)))


def joint(left,right,scope):
    n=len(left);a=[n*x-sum(left) for x in left];b=[n*x-sum(right) for x in right]
    cut=n if scope=='unrestricted' else (n+1)//2;occurrences=(list(zip(a[:cut],b[:cut])),list(zip(a[cut:],b[cut:])))
    cache={}
    def expected(first,second):
        terms={}
        for p in first:
            u,v=terms.get(p,(0,0));terms[p]=(u+1,v)
        for p in second:
            u,v=terms.get(p,(0,0));terms[p]=(u,v+1)
        value=Fraction(1)
        for j,occ in enumerate(occurrences):
            powers=tuple(sorted(power for p,power in terms.items() if (p<cut)==(j==0)))
            identity=j,powers
            if identity not in cache:cache[identity]=block(occ,powers)
            value*=cache[identity]
        return value
    edges=list(zip(range(n-1),range(1,n)))
    ea=sum((expected(edge,()) for edge in edges),Fraction())
    eb=sum((expected((),edge) for edge in edges),Fraction())
    product=sum((expected(first,second) for first in edges for second in edges),Fraction())
    qa,qb=sum(x*x for x in a),sum(x*x for x in b)
    scale_a=Fraction(n,(n-1)*qa) if qa else Fraction();scale_b=Fraction(n,(n-1)*qb) if qb else Fraction()
    return scale_a*ea,scale_b*eb,scale_a*scale_b*(product-ea*eb)


def count(token,patterns):
    position=0;pieces=[]
    while position<len(token):
        options=[p for p in patterns if token[position:position+len(p)]==p]
        piece=max(options,key=len) if options else token[position]
        pieces.append(piece);position+=len(piece)
    assert ''.join(pieces)==token
    return len(pieces)


def association(values):
    n=len(values);mean=Fraction(sum(values),n);d=[x-mean for x in values];q=sum(x*x for x in d)
    return Fraction(n,n-1)*sum(a*b for a,b in zip(d,d[1:]))/q if q else Fraction()


def verify(report_path):
    if not __debug__:raise ValueError('verification requires assertions without optimization')
    result=json.loads(report_path.read_text());raw=(ROOT/'research/transliteration/interior-covariance-pins.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='0dfd611f66f54be079ff4eb0069b2ff943e05b4de655de7a88d8b75d529782c9'
    pins=json.loads(raw);assert pins==result['input_pins']
    for name,expected in pins.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected
    parent=json.loads((ROOT/'research/transliteration/interior_unit_controls.json').read_text())
    original=json.loads((ROOT/'research/transliteration/interior_length_order.json').read_text())
    settings=json.loads((ROOT/'research/baselines/eva-unit-protocol.json').read_text())['policies']
    keys=original['selection']['retained_locus_keys'];checked=0
    expected_variants=[(s,p) for s in ('ZL3b','IT2a') for p in ('split','join')]
    assert [(t['source_id'],t['spacing']) for t in result['treatments']]==expected_variants
    for treatment,old in zip(result['treatments'],parent['treatments']):
        sid,spacing=treatment['source_id'],treatment['spacing']
        payload=build(spacing,source_ids=(sid,),kinds=('P0',));records={r['locus_key']:r for r in payload['records']}
        rows=[[(records[key]['page_id'],key,[count(token,policy['patterns']) for token in records[key]['tokens'][1:-1]]) for key in keys] for policy in settings]
        for pid,vector in zip(POLICIES,rows):
            digest=hashlib.sha256(json.dumps(vector,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
            assert digest==treatment['policy_vector_sha256'][pid]
        totals={s:[[Fraction()]*3 for _ in range(3)] for s in ('unrestricted','half')};effects={s:[Fraction()]*3 for s in totals}
        zero_half={pid:[] for pid in POLICIES}
        assert len(treatment['per_locus'])==len(keys)
        for row,saved in zip(zip(*rows),treatment['per_locus']):
            page,key,_=row[0];assert (page,key)==(saved['page_id'],saved['locus_key']);vectors=[v[2] for v in row]
            for scope in totals:
                means=[Fraction()]*3;covariances=[]
                for i,j in UPPER:
                    left,right,cov=joint(vectors[i],vectors[j],scope);covariances.append(cov)
                    totals[scope][i][j]+=cov
                    if i!=j:totals[scope][j][i]+=cov
                    if i==j:means[i]=left
                assert covariances==[decode(v) for v in saved[scope]['covariance_upper']]
                assert means==[decode(v) for v in saved[scope]['uncentered_means']]
                if scope=='half':
                    for policy,position in zip(POLICIES,(0,3,5)):
                        if covariances[position]==0:zero_half[policy].append({'page_id':page,'locus_key':key})
                for i in range(3):effects[scope][i]+=association(vectors[i])-means[i]
                checked+=6
        n=len(keys)
        assert zero_half==treatment['exact_half_zero_variance_identifiers']
        assert n==treatment['loci']==treatment['accepted_effect_denominator']
        for scope,total in totals.items():
            matrix=[[value/n**2 for value in row] for row in total];saved=treatment[scope]
            assert matrix==[[decode(v) for v in row] for row in saved['exact_ideal_mean_covariance']]
            assert [math.sqrt(float(matrix[i][i])) for i in range(3)]==saved['ideal_standard_deviations_approx']
            ideal_correlation=[[float(matrix[i][j])/math.sqrt(float(matrix[i][i])*float(matrix[j][j])) if matrix[i][i] and matrix[j][j] else None for j in range(3)] for i in range(3)]
            assert ideal_correlation==saved['ideal_correlations_approx']
            points=[v/n for v in effects[scope]];assert points==[decode(v) for v in saved['exact_observed_centered_means']]
            arrays=[p[scope]['control_statistics'] for p in old['unit_policies']];means=[math.fsum(a)/len(a) for a in arrays]
            covariance=[[math.fsum((a-means[i])*(b-means[j]) for a,b in zip(arrays[i],arrays[j]))/len(arrays[i]) for j in range(3)] for i in range(3)]
            assert covariance==saved['existing_controls']['population_covariance']
            assert means==saved['existing_controls']['means'] and len(arrays[0])==saved['existing_controls']['repetitions']==999
            empirical_correlation=[[covariance[i][j]/math.sqrt(covariance[i][i]*covariance[j][j]) if covariance[i][i] and covariance[j][j] else None for j in range(3)] for i in range(3)]
            assert empirical_correlation==saved['existing_controls']['population_correlations']
            for i,pair in enumerate(saved['paired_changes'],1):
                variance=matrix[0][0]+matrix[i][i]-2*matrix[0][i]
                assert variance==decode(pair['ideal_variance_exact'])
                assert points[i]-points[0]==decode(pair['observed_change_exact'])
                sd=math.sqrt(float(variance))
                assert pair['ideal_standard_deviation_approx']==sd
                assert pair['observed_over_ideal_sd_approx']==(float(points[i]-points[0])/sd if sd else None)
                difference=[b-a for a,b in zip(arrays[0],arrays[i])];mean=math.fsum(difference)/len(difference)
                empirical=math.fsum((v-mean)**2 for v in difference)/len(difference)
                assert empirical==pair['existing_control_population_variance']
                assert pair['empirical_to_ideal_sd_ratio_approx']==(math.sqrt(empirical/float(variance)) if variance else None)
                accepted=old['unit_policies'][i]['paired_change_from_ascii'][scope]
                assert pair['accepted_two_sided_tail_count']==accepted['two_sided_tail_count']
                assert pair['accepted_exploratory_two_sided_tail']==accepted['exploratory_two_sided_tail']
        print(f'{sid}/{spacing}: independent literal vectors and all joint entries verified',flush=True)
    return {'unique_per_locus_covariance_entries':checked,'aggregate_covariance_entries':72,'paired_variances':16}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path,default=ROOT/'research/transliteration/interior_unit_covariance.json');args=parser.parse_args()
    try:result=verify(args.report)
    except (AssertionError,ValueError,OSError,KeyError,TypeError) as error:parser.exit(1,f'Independent covariance verification failed: {error}\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
