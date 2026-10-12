"""Independently verify literal count vectors, rational moments and finite ranges.

Uses the established native packet reader for source ingestion, without importing
production interior scoring, centering or segmentation helpers. Run the full
producer replay as well to check receipts and every other report field.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

try:
    from .eva_token_adapter import build
except ImportError:
    from eva_token_adapter import build

ROOT = Path(__file__).resolve().parents[1]
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def parse_decimal_integer(text):
    # Small decimal chunks avoid changing the process-wide integer conversion guard.
    if not isinstance(text,str) or not re.fullmatch(r'-?[0-9]+',text):
        raise ValueError('decimal integer string required')
    negative=text.startswith('-');digits=text[1:] if negative else text
    value=0
    for offset in range(0,len(digits),18):
        chunk=digits[offset:offset+18]
        value=value*10**len(chunk)+int(chunk)
    return -value if negative else value
def unpack(value):return Fraction(parse_decimal_integer(value['numerator']),parse_decimal_integer(value['denominator'])) if value is not None else None
def count_units(token,patterns):
    # Candidate comparison at each offset, independent of production ordered_patterns/segment.
    offset=0;pieces=[]
    while offset<len(token):
        matches=[pattern for pattern in patterns if token[offset:offset+len(pattern)]==pattern]
        piece=max(matches,key=len) if matches else token[offset]
        pieces.append(piece);offset+=len(piece)
    assert ''.join(pieces)==token
    return pieces

def exact(values):
    n=len(values);total=sum(values);squares=sum(x*x for x in values)
    # Expanded products provide a second form of the covariance computation.
    denominator=n*n*squares-n*total*total
    numerator=sum(n*n*a*b-n*total*(a+b)+total*total for a,b in zip(values,values[1:]))
    if denominator==0:return (Fraction(0),)*5
    raw=Fraction(n*numerator,(n-1)*denominator)
    full=Fraction(-1,n-1)
    k=(n+1)//2;a=values[:k];b=values[k:]
    means=[Fraction(n*sum(block)-len(block)*total,len(block)) for block in (a,b)]
    internal=Fraction(0)
    for block,mean in zip((a,b),means):
        size=len(block)
        transformed_square=sum((n*x-total)**2 for x in block)
        internal += size*mean*mean-Fraction(transformed_square,size)
    half=Fraction(n,(n-1)*denominator)*(internal+means[0]*means[1])
    return raw,full,half,raw-full,raw-half

def check(rows,profiles,policies):
    assert len(profiles)==len(policies)==3
    assert [p['policy_id'] for p in profiles]==[p['id'] for p in policies]
    output={}
    for policy,saved in zip(policies,profiles):
        vectors=[];totals=[Fraction(0)]*5;hits=Counter({p:0 for p in policy['patterns']});uppercase=Counter()
        for key,tokens in rows:
            values=[]
            for token in tokens[1:-1]:
                pieces=count_units(token,policy['patterns']);values.append(len(pieces))
                hits.update(p for p in pieces if len(p)>1)
                uppercase.update(p for p in pieces if len(p)==1 and p.isupper())
            vectors.append(('encoded-unit',key,values))
            totals=[a+b for a,b in zip(totals,exact(values))]
        assert digest(vectors)==saved['vector_sha256']
        assert len(rows)==saved['rows']
        assert sum(len(v) for _,_,v in vectors)==saved['interior_groups']
        assert sum(len(v)-1 for _,_,v in vectors)==saved['interior_pairs']
        assert sum(len(set(v))==1 for _,_,v in vectors)==saved['constant_interiors']
        assert {str(k):v for k,v in sorted(Counter(len(t) for _,t in rows).items())}==saved['original_group_count_histogram']
        assert dict(hits)==saved['scope_audit']['pattern_hits']
        assert dict(uppercase)==saved['scope_audit']['uppercase_single_letter_fallback_counts']
        values=[x/len(rows) for x in totals] if rows else [None]*5
        for name,value in zip(('uncentered_mean','unrestricted_expectation','half_expectation'),values):assert unpack(saved[name])==value
        for scope,value in zip(('unrestricted','half'),values[3:]):
            assert unpack(saved['scores'][scope])==value
            output[policy['id'],scope]=value
    return output
def verify(runs, report_path):
    if not __debug__:
        raise ValueError('verification requires Python assertions; run without optimization')
    report=json.loads(report_path.read_text())
    pin_bytes=(ROOT/'research/literature/self-citation-interior-pins.json').read_bytes()
    assert hashlib.sha256(pin_bytes).hexdigest()=='8d1b9e97d61ce0052b6e0d15e764f5e46007652ef81fa05d22f1f347d10a9d6e'
    pins=json.loads(pin_bytes)
    assert pins==report['input_pins']
    for name,expected in pins.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected
    parent=json.loads((ROOT/'research/literature/self-citation-prefix-profile.json').read_text())
    policies=json.loads((ROOT/'research/baselines/eva-unit-protocol.json').read_text())['policies']
    assert len(report['targets'])==4 and {(t['source_id'],t['spacing']) for t in report['targets']}=={(s,p) for s in ('ZL3b','IT2a') for p in ('split','join')}
    assert [c['seed'] for c in report['cases']]==list(range(1,32))
    assert all(type(c['seed']) is int for c in report['cases'])
    assert len(report['comparisons'])==24
    assert {(c['source_id'],c['spacing'],c['policy_id'],c['scope']) for c in report['comparisons']}=={
        (s,p,policy['id'],scope) for s in ('ZL3b','IT2a') for p in ('split','join') for policy in policies for scope in ('unrestricted','half')}
    maps={}
    for spacing in ('split','join'):
        payload=build(spacing,source_ids=('ZL3b','IT2a'),kinds=('P0',))
        for sid in ('ZL3b','IT2a'):
            maps[sid,spacing]={r['locus_key']:r['tokens'] for r in payload['records'] if r['source_id']==sid}
    selected=[];excluded=[]
    for key in parent['target']['selected_keys']:
        reasons=[f'{sid}/{spacing}:fewer_than_five_tokens' for sid in ('ZL3b','IT2a') for spacing in ('split','join') if len(maps[sid,spacing][key])<5]
        if reasons:excluded.append({'locus_key':key,'reasons':reasons})
        else:selected.append(key)
    assert selected==report['selection']['selected_keys']
    assert digest(selected)==report['selection']['selected_keys_sha256']
    assert [(r['locus_key'],sorted(r['reasons'])) for r in excluded]==[(r['locus_key'],sorted(r['reasons'])) for r in report['selection']['additional_minimum_size_exclusions']]
    targets={(t['source_id'],t['spacing']):check([(key,maps[t['source_id'],t['spacing']][key]) for key in selected],t['policies'],policies) for t in report['targets']}
    seeds=[]
    for parent_case,saved in zip(parent['cases'],report['cases']):
        assert saved['generation_receipt']==parent_case
        raw=(runs/f"seed-{saved['seed']:02d}"/'observed/output/generated.txt').read_bytes()
        assert hashlib.sha256(raw).hexdigest()==parent_case['output_sha256']['observed']
        native=[line for line in raw.splitlines() if line.strip() and not line.lstrip().startswith(b'#')]
        assert all(re.fullmatch(rb'[A-Za-z]+(?: [A-Za-z]+)*',line) for line in native)
        rows=[];excluded=[];hist=Counter()
        for index,body in enumerate(native):
            tokens=body.decode('ascii').split(' ')
            if index==0:excluded.append({'row_index':index,'reason':'initialized_input','groups':len(tokens)})
            else:
                hist[len(tokens)]+=1
                if len(tokens)<5:excluded.append({'row_index':index,'reason':'fewer_than_five_groups','groups':len(tokens)})
                else:rows.append((str(index),tokens))
        audit={'native_rows':len(native),'initialized_rows':1,'newly_generated_rows':len(native)-1,'eligible_rows':len(rows),
               'excluded_rows':excluded,'generated_group_count_histogram':{str(k):v for k,v in sorted(hist.items())}}
        assert audit==saved['eligibility']
        seeds.append(check(rows,saved['policies'],policies))
    for saved in report['comparisons']:
        identity=(saved['policy_id'],saved['scope']);values=[p[identity] for p in seeds]
        point=targets[saved['source_id'],saved['spacing']][identity]
        defined=point is not None and all(value is not None for value in values)
        lo,hi=(min(values),max(values)) if defined else (None,None)
        gap=max(lo-point,point-hi,Fraction(0)) if defined else None
        for name,value in [('target',point),('seed_minimum',lo),('seed_maximum',hi),('outside_range_gap',gap)]:assert unpack(saved[name])==value
        assert saved['all_fixed_seed_values_defined'] is defined
        assert saved['within_fixed_seed_range'] is (lo<=point<=hi if defined else None)
    vectors=len(policies)*(len(targets)+len(seeds))
    return {'count_vectors':vectors,'exact_means':5*vectors,'eligibility_audits':len(seeds),'range_comparisons':len(report['comparisons'])}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',required=True,type=Path)
    parser.add_argument('--report',type=Path,default=ROOT/'research/literature/self-citation-interior.json')
    args=parser.parse_args()
    try:
        result=verify(args.runs,args.report)
    except (AssertionError,ValueError,OSError,KeyError,TypeError) as error:
        parser.exit(1,f'Independent interior arithmetic verification failed: {error}\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    main()
