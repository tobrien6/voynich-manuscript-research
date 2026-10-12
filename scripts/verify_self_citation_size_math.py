"""Separate literal/rational verification of the exact-size scientific fields.

Uses the earlier independent scanner and moment expansion, and an independently
written support/weight/range calculation. Run complete producer replay as well.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

try:
    from . import verify_self_citation_interior_math as independent
except ImportError:
    import verify_self_citation_interior_math as independent

ROOT=Path(__file__).resolve().parents[1]
VARIANTS=[(s,p) for s in ('ZL3b','IT2a') for p in ('split','join')]
FIELDS=['uncentered_mean','unrestricted_expectation','half_expectation','unrestricted','half']


def profile_values(profile):
    return [independent.unpack(profile[field]) for field in FIELDS[:3]]+[independent.unpack(profile['scores'][scope]) for scope in FIELDS[3:]]


def check_cells(rows,cells,sizes,policies):
    assert [c['original_group_count'] for c in cells]==sizes
    output={}
    for cell in cells:
        k=cell['original_group_count'];native=[(key,tokens) for key,tokens in rows if len(tokens)==k]
        assert cell['rows']==len(native)
        independent.check(native,cell['policies'],policies)
        output[k]={'n':len(native),'means':{p['policy_id']:profile_values(p) for p in cell['policies']}}
    return output


def standard(cells,counts):
    total=sum(counts.values())
    defined=total>0 and all(cells[k]['n']>0 for k in counts)
    means={}
    for pid in ('ascii_letters','bench_sequences','bench_and_minim_sequences'):
        # Multiply by integer target frequencies, then divide once by the total.
        means[pid]=[sum((n*cells[k]['means'][pid][column] for k,n in counts.items()),Fraction(0))/total for column in range(5)] if defined else [None]*5
    return means


def check_standard(cells,counts,saved):
    total=sum(counts.values());missing=[k for k in sorted(counts) if cells[k]['n']==0]
    assert saved['target_rows']==total
    assert saved['all_required_sizes_supported'] is (total>0 and not missing)
    assert [(w['original_group_count'],w['rows'],independent.unpack(w['weight'])) for w in saved['weights']]==[(k,n,Fraction(n,total)) for k,n in sorted(counts.items())]
    assert [(w['original_group_count'],w['target_rows'],independent.unpack(w['target_weight'])) for w in saved['missing_required_sizes']]==[(k,counts[k],Fraction(counts[k],total)) for k in missing]
    expected=standard(cells,counts)
    assert [p['policy_id'] for p in saved['policies']]==list(expected)
    for p in saved['policies']:assert profile_values(p)==expected[p['policy_id']]
    return expected


def verify(runs,report_path):
    if not __debug__:raise ValueError('verification requires assertions; run without optimization')
    report=json.loads(report_path.read_text())
    raw=(ROOT/'research/literature/self-citation-size-pins.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='7bb5faefbe8b6a7d2b2c3a6f678b973319175def3d4e4fabcc83d8b44b2276c0'
    pins=json.loads(raw);assert pins==report['input_pins']
    for name,expected in pins.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected
    old=json.loads((ROOT/'research/literature/self-citation-interior.json').read_text())
    policies=json.loads((ROOT/'research/baselines/eva-unit-protocol.json').read_text())['policies']
    sources={}
    for spacing in ('split','join'):
        packet=independent.build(spacing,source_ids=('ZL3b','IT2a'),kinds=('P0',))
        for sid in ('ZL3b','IT2a'):
            index={r['locus_key']:r['tokens'] for r in packet['records'] if r['source_id']==sid}
            sources[sid,spacing]=[(key,index[key]) for key in old['selection']['selected_keys']]
    native_models=[];model_counts=[]
    assert [m['seed'] for m in report['models']]==list(range(1,32))
    for saved,previous in zip(report['models'],old['cases']):
        raw=(runs/f"seed-{saved['seed']:02d}"/'observed/output/generated.txt').read_bytes()
        assert hashlib.sha256(raw).hexdigest()==previous['generation_receipt']['output_sha256']['observed']
        native=[line for line in raw.splitlines() if line.strip() and not line.lstrip().startswith(b'#')]
        assert all(re.fullmatch(rb'[A-Za-z]+(?: [A-Za-z]+)*',line) for line in native)
        rows=[(str(i),line.decode('ascii').split(' ')) for i,line in enumerate(native) if i>0 and len(line.split(b' '))>=5]
        assert len(rows)==saved['eligibility']['eligible_rows']
        counts=Counter(len(tokens) for _,tokens in rows);native_models.append(rows);model_counts.append(counts)
    sizes=sorted(set.union(*(set(Counter(len(t) for _,t in rows)) for rows in sources.values()),*(set(counts) for counts in model_counts)))
    assert sizes==report['original_group_count_grid']
    support=set.intersection(*(set(counts) for counts in model_counts))
    maps={variant:dict(rows) for variant,rows in sources.items()};selected=[];excluded=[]
    missing={k:[s+1 for s,counts in enumerate(model_counts) if counts[k]==0] for k in sizes}
    for key in old['selection']['selected_keys']:
        reasons=[]
        for sid,spacing in VARIANTS:
            k=len(maps[sid,spacing][key])
            if k not in support:reasons.append({'source_id':sid,'spacing':spacing,'original_group_count':k,'missing_model_seeds':missing[k]})
        if reasons:excluded.append({'locus_key':key,'reasons':reasons})
        else:selected.append(key)
    selection=report['selection']
    assert selected==selection['selected_keys'] and excluded==selection['excluded_keys']
    assert independent.digest(selected)==selection['selected_keys_sha256']
    assert sorted(support)==selection['common_generator_sizes']
    assert independent.unpack(selection['coverage'])==Fraction(len(selected),len(old['selection']['selected_keys']))
    assert [{'original_group_count':k,'missing_model_seeds':missing[k]} for k in sizes]==selection['size_support']
    models=[check_cells(rows,saved['cells'],sizes,policies) for rows,saved in zip(native_models,report['models'])]
    for cells,counts,previous in zip(models,model_counts,old['cases']):
        rebuilt=standard(cells,counts)
        for profile in previous['policies']:assert profile_values(profile)==rebuilt[profile['policy_id']]
    counts_verified=len(models)*len(sizes)*3
    weighted_profiles=0
    for family in ('primary','supported_common'):
        saved=report[family];targets={};source_counts={}
        assert [(t['source_id'],t['spacing']) for t in saved['targets']]==VARIANTS
        assert [c['seed'] for c in saved['cases']]==list(range(1,32))
        for target in saved['targets']:
            variant=(target['source_id'],target['spacing'])
            rows=[(key,tokens) for key,tokens in sources[variant] if family=='primary' or key in set(selected)]
            cells=check_cells(rows,target['cells'],sizes,policies);counts_verified+=len(sizes)*3
            source_counts[variant]=Counter(len(tokens) for _,tokens in rows)
            targets[variant]=check_standard(cells,source_counts[variant],target);weighted_profiles+=3
            if family=='primary':
                previous=old['targets'][VARIANTS.index(variant)]
                for profile in previous['policies']:assert profile_values(profile)==targets[variant][profile['policy_id']]
        model_values=[]
        for cells,case in zip(models,saved['cases']):
            assert [(v['source_id'],v['spacing']) for v in case['standardized']]==VARIANTS
            values={}
            for value in case['standardized']:
                variant=(value['source_id'],value['spacing'])
                values[variant]=check_standard(cells,source_counts[variant],value);weighted_profiles+=3
            model_values.append(values)
        assert len(saved['comparisons'])==24
        assert {(c['source_id'],c['spacing'],c['policy_id'],c['scope']) for c in saved['comparisons']}=={
            (s,p,policy['id'],scope) for s,p in VARIANTS for policy in policies for scope in ('unrestricted','half')}
        memberships=[]
        for c in saved['comparisons']:
            variant=(c['source_id'],c['spacing']);pid=c['policy_id'];column=3 if c['scope']=='unrestricted' else 4
            point=targets[variant][pid][column];points=[m[variant][pid][column] for m in model_values]
            defined=point is not None and all(p is not None for p in points)
            lo,hi=(min(points),max(points)) if defined else (None,None)
            inside=lo<=point<=hi if defined else None;gap=max(lo-point,point-hi,Fraction(0)) if defined else None
            for field,value in [('target',point),('seed_minimum',lo),('seed_maximum',hi),('outside_range_gap',gap)]:assert independent.unpack(c[field])==value
            assert c['all_fixed_seed_values_defined'] is defined and c['within_fixed_seed_range'] is inside
            memberships.append(inside)
        assert saved['comparison_ranges_defined'] is all(value is not None for value in memberships)
        assert saved['all_target_points_within_fixed_seed_ranges'] is (all(memberships) if all(v is not None for v in memberships) else None)
    checks=report['parent_exact_reassembly_checks']
    assert len(checks)==35 and all(check['exact_parent_reassembly'] is True for check in checks)
    return {'count_vectors_including_empty_cells':counts_verified,'standardized_policy_profiles':weighted_profiles,
            'weighted_mean_fields':weighted_profiles*5,'range_comparisons':48,'common_keys':len(selected)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--runs',required=True,type=Path)
    parser.add_argument('--report',type=Path,default=ROOT/'research/literature/self-citation-size-conditioned.json')
    args=parser.parse_args()
    try:result=verify(args.runs,args.report)
    except (AssertionError,ValueError,OSError,KeyError,TypeError) as error:parser.exit(1,f'Independent exact-size verification failed: {error}\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
