"""Exact original-group-count standardization of archived self-citation rows."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform

try:
    from . import self_citation_interior as parent
except ImportError:
    import self_citation_interior as parent

ROOT = Path(__file__).resolve().parents[1]
METHOD = 'fixed-self-citation-exact-size-standardization-v1'
PLAN = 'research/literature/SELF_CITATION_SIZE_PLAN.md'
PINS = 'research/literature/self-citation-size-pins.json'
PARENT = 'research/literature/self-citation-interior.json'
PIN_SHA256 = '65c9d900f34172c98a5ff38b780fc2612a7fed9c5412a91634859f4d3976e275'
VARIANTS = [(s,p) for s in parent.prefix.SOURCE_IDS for p in parent.prefix.SPACING]
FIELDS = ['uncentered_mean','unrestricted_expectation','half_expectation','unrestricted','half']


def load_inputs():
    raw=(ROOT/PINS).read_bytes()
    if parent.sha(raw)!=PIN_SHA256:
        raise ValueError('frozen size-standardization manifest changed')
    pins=parent.load_split_json(raw.decode())
    for name,expected in pins.items():
        if parent.sha((ROOT/name).read_bytes())!=expected:
            raise ValueError(f'frozen size-standardization input changed: {name}')
    parent.load_inputs()  # All22 parent source/helper pins, including its manifest identity.
    return parent.load_split_json((ROOT/PARENT).read_text()),pins


def histogram(rows):
    if len({key for key,_ in rows})!=len(rows):
        raise ValueError('duplicate original row identity')
    if any(not isinstance(tokens,(list,tuple)) or len(tokens)<5 for _,tokens in rows):
        raise ValueError('only parent-eligible original boundaries allowed')
    return dict(sorted(Counter(len(tokens) for _,tokens in rows).items()))


def values(profile):
    return [parent.unpack(profile[field]) for field in FIELDS[:3]]+[parent.unpack(profile['scores'][scope]) for scope in FIELDS[3:]]


def pack_profile(policy_id,means):
    return {'policy_id':policy_id,**{field:parent.packed(value) for field,value in zip(FIELDS[:3],means[:3])},
            'scores':{scope:parent.packed(value) for scope,value in zip(FIELDS[3:],means[3:])}}


def require_profiles(profiles):
    if [profile['policy_id'] for profile in profiles]!=parent.POLICIES:
        raise ValueError('complete ordered count-policy family required')


def cell_profiles(rows,policies,sizes):
    hist=histogram(rows)
    if sizes!=sorted(set(sizes)) or any(type(k) is not int or k<5 for k in sizes) or not set(hist)<=set(sizes):
        raise ValueError('complete ordered original size grid required')
    return [{'original_group_count':k,'rows':hist.get(k,0),
             'policies':parent.measure([(key,tokens) for key,tokens in rows if len(tokens)==k],policies)} for k in sizes]


def weighted(cells,weights):
    if any(type(k) is not int or k<5 or type(n) is not int or n<=0 for k,n in weights.items()):
        raise ValueError('positive integer original-size weights required')
    index={cell['original_group_count']:cell for cell in cells}
    if len(index)!=len(cells):
        raise ValueError('duplicate exact-size cell')
    for cell in cells:
        require_profiles(cell['policies'])
        if type(cell['rows']) is not int or cell['rows']<0:
            raise ValueError('invalid exact-size denominator')
    total=sum(weights.values())
    missing=[{'original_group_count':k,'target_rows':n,'target_weight':parent.packed(Fraction(n,total))}
             for k,n in sorted(weights.items()) if k not in index or index[k]['rows']==0]
    complete=bool(total) and not missing
    profiles=[]
    for i,pid in enumerate(parent.POLICIES):
        means=[Fraction(0)]*5 if complete else [None]*5
        if complete:
            for k,n in weights.items():
                cell=index[k];score=values(cell['policies'][i])
                if any(value is None for value in score):
                    raise ValueError('nonempty cell has undefined scientific mean')
                means=[a+Fraction(n,total)*b for a,b in zip(means,score)]
        profiles.append(pack_profile(pid,means))
    return {'target_rows':total,'weights':[{'original_group_count':k,'rows':n,'weight':parent.packed(Fraction(n,total))}
                                          for k,n in sorted(weights.items())],
            'all_required_sizes_supported':complete,'missing_required_sizes':missing,'policies':profiles}


def verify_reassembly(cells,expected):
    require_profiles(expected)
    result=weighted(cells,{c['original_group_count']:c['rows'] for c in cells if c['rows']})
    for profile,previous in zip(result['policies'],expected):
        if values(profile)!=values(previous):
            raise ValueError('exact-size decomposition does not reassemble parent means')
    if result['target_rows']!=expected[0]['rows']:
        raise ValueError('exact-size decomposition changes parent denominator')
    return True


def common_support(sources,counts):
    if list(sources)!=VARIANTS or [case['seed'] for case in counts]!=parent.SEEDS or any(type(case['seed']) is not int for case in counts):
        raise ValueError('all ordered variants and fixed31 seeds required')
    if any(type(k) is not int or k<5 or type(n) is not int or n<=0 for case in counts for k,n in case['counts'].items()):
        raise ValueError('positive integer original-size counts required')
    keys=[key for key,_ in sources[VARIANTS[0]]]
    if len(set(keys))!=len(keys) or any([key for key,_ in sources[variant]]!=keys for variant in VARIANTS):
        raise ValueError('identical ordered unique parent source keys required')
    support=set.intersection(*(set(case['counts']) for case in counts))
    union=set.union(*(set(case['counts']) for case in counts))
    missing={k:[case['seed'] for case in counts if case['counts'].get(k,0)==0] for k in union|{len(tokens) for rows in sources.values() for _,tokens in rows}}
    selected=[];excluded=[]
    maps={variant:dict(rows) for variant,rows in sources.items()}
    for key in keys:
        reasons=[]
        for sid,spacing in VARIANTS:
            k=len(maps[sid,spacing][key])
            if k not in support:
                reasons.append({'source_id':sid,'spacing':spacing,'original_group_count':k,'missing_model_seeds':missing[k]})
        if reasons:excluded.append({'locus_key':key,'reasons':reasons})
        else:selected.append(key)
    return {'parent_keys':len(keys),'common_generator_sizes':sorted(support),'selected_keys':selected,
            'selected_keys_sha256':parent.sha(parent.compact(selected)),'excluded_keys':excluded,
            'coverage':parent.packed(Fraction(len(selected),len(keys))) if keys else None,
            'size_support':[{'original_group_count':k,'missing_model_seeds':missing[k]} for k in sorted(missing)]}


def comparisons(targets,cases):
    if [(t['source_id'],t['spacing']) for t in targets]!=VARIANTS or [c['seed'] for c in cases]!=parent.SEEDS or any(type(c['seed']) is not int for c in cases):
        raise ValueError('all ordered source variants and fixed31 seeds required')
    for case in cases:
        if [(t['source_id'],t['spacing']) for t in case['standardized']]!=VARIANTS:
            raise ValueError('all standardized source variants required per seed')
    out=[]
    for j,target in enumerate(targets):
        require_profiles(target['policies'])
        for i,profile in enumerate(target['policies']):
            for scope in parent.SCOPES:
                points=[]
                for case in cases:
                    standard=case['standardized'][j];require_profiles(standard['policies'])
                    points.append(parent.unpack(standard['policies'][i]['scores'][scope]))
                point=parent.unpack(profile['scores'][scope]);defined=point is not None and all(p is not None for p in points)
                lo,hi=(min(points),max(points)) if defined else (None,None)
                out.append({'source_id':target['source_id'],'spacing':target['spacing'],'policy_id':profile['policy_id'],'scope':scope,
                            'target':parent.packed(point),'seed_minimum':parent.packed(lo),'seed_maximum':parent.packed(hi),
                            'all_fixed_seed_values_defined':defined,'within_fixed_seed_range':lo<=point<=hi if defined else None,
                            'outside_range_gap':parent.packed(max(lo-point,point-hi,Fraction(0))) if defined else None})
    defined=all(item['all_fixed_seed_values_defined'] for item in out)
    return {'comparisons':out,'comparison_ranges_defined':defined,
            'all_target_points_within_fixed_seed_ranges':all(item['within_fixed_seed_range'] for item in out) if defined else None}


def report(runs):
    previous,pins=load_inputs()
    if not parent.same_json(parent.report(runs),previous):
        raise ValueError('complete frozen parent report does not replay')
    old,_settings,_,_=parent.load_inputs()
    prepared=parent.verified_runs(runs,old)
    settings=parent.load_split_json((ROOT/parent.SETTINGS).read_text())['policies']
    packets=[parent.prefix.build(spacing,source_ids=parent.prefix.SOURCE_IDS,kinds=('P0',)) for spacing in parent.prefix.SPACING]
    maps={(sid,spacing):{r['locus_key']:r['tokens'] for r in packets[i]['records'] if r['source_id']==sid}
          for i,spacing in enumerate(parent.prefix.SPACING) for sid in parent.prefix.SOURCE_IDS}
    keys=previous['selection']['selected_keys']
    sources={(sid,spacing):[(key,maps[sid,spacing][key]) for key in keys] for sid,spacing in VARIANTS}
    counts=[{'seed':case['seed'],'counts':histogram(rows)} for case,rows,_ in prepared]
    selection=common_support(sources,counts)
    sizes=sorted(set.union(*(set(histogram(rows)) for rows in sources.values()),*(set(case['counts']) for case in counts)))
    full_targets=[];supported_targets=[];reassembly=[]
    selected=set(selection['selected_keys'])
    for j,(sid,spacing) in enumerate(VARIANTS):
        rows=sources[sid,spacing];cells=cell_profiles(rows,settings,sizes)
        reassembly.append({'source_id':sid,'spacing':spacing,'exact_parent_reassembly':verify_reassembly(cells,previous['targets'][j]['policies'])})
        weights=histogram(rows);full=weighted(cells,weights)
        full_targets.append({'source_id':sid,'spacing':spacing,'cells':cells,**full})
        retained=[(key,tokens) for key,tokens in rows if key in selected]
        restricted=cell_profiles(retained,settings,sizes);support=weighted(restricted,histogram(retained))
        supported_targets.append({'source_id':sid,'spacing':spacing,'cells':restricted,**support})
    primary_cases=[];supported_cases=[];model_cases=[]
    for j,(case,rows,audit) in enumerate(prepared):
        cells=cell_profiles(rows,settings,sizes)
        reassembly.append({'seed':case['seed'],'exact_parent_reassembly':verify_reassembly(cells,previous['cases'][j]['policies'])})
        model_cases.append({'seed':case['seed'],'parent_case_index':j,'eligibility':audit,'cells':cells})
        for targets,destination in ((full_targets,primary_cases),(supported_targets,supported_cases)):
            destination.append({'seed':case['seed'],'standardized':[{'source_id':t['source_id'],'spacing':t['spacing'],
                                **weighted(cells,{entry['original_group_count']:entry['rows'] for entry in t['weights']})} for t in targets]})
    return {'schema_version':1,'method':METHOD,'status':'exploratory reused-output exact-size standardization; full prior exposure',
            'python_version':platform.python_version(),'input_pins':pins,'pin_manifest_sha256':PIN_SHA256,
            'implementation_sha256':parent.sha(Path(__file__).read_bytes()),'parent_report_sha256':pins[PARENT],
            'selection':selection,'original_group_count_grid':sizes,'models':model_cases,'parent_exact_reassembly_checks':reassembly,
            'primary':{'targets':full_targets,'cases':primary_cases,**comparisons(full_targets,primary_cases)},
            'supported_common':{'targets':supported_targets,'cases':supported_cases,**comparisons(supported_targets,supported_cases)},
            'new_generation_processes':0,'new_permutation_draws':0,'mechanism_or_translation_validated':False}


def protect_output(output,runs):
    parent.protect_output(output,runs)
    pins=parent.load_split_json((ROOT/PINS).read_text())
    protected=[ROOT/name for name in pins]+[ROOT/PINS,Path(__file__).resolve()]
    if any(output.resolve()==p.resolve() or (output.exists() and p.exists() and output.samefile(p)) for p in protected):
        raise ValueError('output aliases size-standardization inputs, code or plan')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--runs',required=True,type=Path)
    dest=parser.add_mutually_exclusive_group(required=True);dest.add_argument('--new-report',type=Path);dest.add_argument('--check',type=Path)
    args=parser.parse_args()
    try:
        if args.new_report:
            protect_output(args.new_report,args.runs)
            if args.new_report.exists() or args.new_report.is_symlink():raise ValueError('new report destination already exists')
        result=report(args.runs)
        if args.check and not parent.same_json(result,parent.load_split_json(args.check.read_text())):raise ValueError('complete size-conditioned report differs from replay')
        if args.new_report:
            protect_output(args.new_report,args.runs)
            with args.new_report.open('x',encoding='utf-8') as out:out.write(json.dumps(result,indent=2)+'\n')
    except (ValueError,OSError,KeyError,TypeError) as error:parser.exit(1,f'Exact-size comparison failed: {error}\n')
    print('Complete fixed31 exact-size comparison verified.' if args.check else 'Complete fixed31 exact-size comparison saved.')


if __name__=='__main__':
    main()
