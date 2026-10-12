"""Fixed-model event-role accounting on the exposed grouped symbol reference."""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction as F
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import string

try:
    from . import paired_symbol_entropy as parent
    from .audit_transcription_images import dependency_components, page_reference
    from .validate_evaluation_split import load_split_json
except ImportError:
    import paired_symbol_entropy as parent
    from audit_transcription_images import dependency_components, page_reference
    from validate_evaluation_split import load_split_json

ROOT = Path(__file__).resolve().parents[1]
INPUTS = 'research/baselines/symbol-event-accounting-inputs.json'
PLAN = 'research/baselines/SYMBOL_EVENT_ACCOUNTING_PLAN.md'
PINS = {INPUTS:'aa3e11cc271d88ef19c83d2bfae5871e482d647ccfae1cb198cc2d5263019598',
        PLAN:'5677de8bb29006641fada5c80b046df8ccb689cac32eaf5f9c247bcb58c2e185'}
ROLES = ('initial_unit','second_unit','later_unit','termination')
BOS, EOS = '<BOS>', '<EOS>'
TOL = 1e-10


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compact(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()


def encoded(value):
    return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def packed(raw):
    buffer=io.BytesIO()
    with gzip.GzipFile(fileobj=buffer,filename='',mode='wb',mtime=0) as archive:
        archive.write(raw)
    return buffer.getvalue()


def unpack(raw):
    require(raw[:3]==b'\x1f\x8b\x08' and raw[3]==0 and raw[4:8]==b'\0'*4,
            'gzip must have no optional metadata, filename or timestamp')
    return gzip.decompress(raw)


def validate_inputs(root=ROOT):
    for path,pin in PINS.items():
        require(sha((root/path).read_bytes())==pin,'fixed accounting plan changed: '+path)
    manifest=load_split_json((root/INPUTS).read_text(encoding='utf-8'))
    require(manifest['role_order']==list(ROLES) and manifest['parent_loss_tolerance_bits']==TOL,
            'accounting rule changed')
    for path,pin in manifest['input_pins'].items():
        require(sha((root/path).read_bytes())==pin,'reference input/helper changed: '+path)
    return manifest


def load_reference(path,manifest):
    raw=path.read_bytes()
    require(sha(raw)==manifest['reference_report_sha256'],'numeric reference report bytes changed')
    reference=load_split_json(raw.decode('utf-8'))
    require(reference['schema_version']==1 and reference['method']=='grouped-symbol-prediction-v1'
            and reference['implementation_sha256']==manifest['reference_producer_sha256']
            and reference['input_pins']==manifest['input_pins'],'reference specification changed')
    return reference


def segment(token,patterns):
    require(isinstance(token,str) and token and token.isascii() and token.isalpha(),'literal ASCII token required')
    ordered=sorted(patterns,key=lambda p:(-len(p),p))
    output=[];offset=0
    while offset<len(token):
        piece=next((p for p in ordered if token.startswith(p,offset)),token[offset])
        output.append(piece);offset+=len(piece)
    require(''.join(output)==token,'unit reconstruction changed')
    return output


def events(units):
    require(isinstance(units,list) and units and all(isinstance(u,str) and u and u not in (BOS,EOS)
            for u in units),'nonempty units without reserved labels required')
    values=[BOS,BOS,*units,EOS]
    result=[]
    for index in range(len(units)+1):
        role=('termination' if index==len(units) else 'initial_unit' if index==0
              else 'second_unit' if index==1 else 'later_unit')
        result.append((*values[index:index+3],role))
    return result


def fit(rows,alphabet):
    require(rows and len(alphabet)==len(set(alphabet)) and EOS in alphabet and BOS not in alphabet,
            'nonempty training population and unique target alphabet required')
    triples=Counter(e[:3] for row in rows for units in row['segments'] for e in events(units))
    targets,pairs,first_totals,second_totals=Counter(),Counter(),Counter(),Counter()
    for (w,x,y),n in triples.items():
        require(y in alphabet,'target outside fixed alphabet')
        targets[y]+=n;pairs[x,y]+=n;first_totals[x]+=n;second_totals[w,x]+=n
    return dict(alphabet=tuple(alphabet),targets=targets,pairs=pairs,triples=triples,
                first_totals=first_totals,second_totals=second_totals,total=sum(targets.values()))


def counts_record(model):
    return {'alphabet':list(model['alphabet']),
            'target_counts':[[y,n] for y,n in sorted(model['targets'].items())],
            'first_counts':[[x,y,n] for (x,y),n in sorted(model['pairs'].items())],
            'second_counts':[[w,x,y,n] for (w,x,y),n in sorted(model['triples'].items())]}


def probabilities(model,w,x,y):
    require(y in model['alphabet'],'target outside alphabet')
    q0=F(2*model['targets'][y]+1,2*model['total']+len(model['alphabet']))
    q1=(model['pairs'][x,y]+16*q0)/(model['first_totals'][x]+16)
    q2=(model['triples'][w,x,y]+16*q1)/(model['second_totals'][w,x]+16)
    return q0,q1,q2


def close(actual,expected,label):
    require(isinstance(actual,(int,float)) and isinstance(expected,(int,float))
            and math.isfinite(actual) and math.isfinite(expected) and abs(actual-expected)<=TOL,
            'reference/identity discrepancy: '+label)
    return abs(actual-expected)


def role_record(role,losses,gains):
    count=len(gains)
    totals=[math.fsum(values) for values in losses]
    direct=math.fsum(gains)
    close(direct,totals[1]-totals[2],'role gain/loss identity')
    return {'role':role,'targets':count,'loss_bits_order0_order1_order2':totals,
            'gain12_bits':direct,'mean_gain12_bits_per_target':direct/count if count else None}


def score_row(row,model,fold,cache):
    all_losses=[[],[],[]]
    role_losses={r:[[],[],[]] for r in ROLES};role_gains={r:[] for r in ROLES}
    unseen1=unseen2=0
    for units in row['segments']:
        for w,x,y,role in events(units):
            key=w,x,y
            if key not in cache:
                cache[key]=tuple(-math.log2(float(q)) for q in probabilities(model,w,x,y))
            values=cache[key]
            for j,value in enumerate(values):
                all_losses[j].append(value);role_losses[role][j].append(value)
            role_gains[role].append(values[1]-values[2])
            unseen1+=x not in model['first_totals'];unseen2+=(w,x) not in model['second_totals']
    roles=[role_record(r,role_losses[r],role_gains[r]) for r in ROLES]
    totals=[math.fsum(values) for values in all_losses]
    tokens=len(row['segments']);units=sum(len(u) for u in row['segments']);targets=units+tokens
    require(roles[0]['targets']==roles[3]['targets']==tokens
            and sum(r['targets'] for r in roles[:3])==units and sum(r['targets'] for r in roles)==targets,
            'event class target accounting changed')
    for j in range(3):close(math.fsum(r['loss_bits_order0_order1_order2'][j] for r in roles),totals[j],'row role sums')
    return {'locus_key':row['key'],'page_id':row['page'],'group_id':row['group'],'fold':fold,
            'tokens':tokens,'units':units,'targets':targets,'loss_bits_order0_order1_order2':totals,
            'gain01_bits_per_target':(totals[0]-totals[1])/targets,
            'gain12_bits_per_target':(totals[1]-totals[2])/targets,
            'unseen_order1_context_targets':unseen1,'unseen_order2_context_targets':unseen2,'roles':roles}


def verify_row(actual,expected):
    error=0
    for key,value in expected.items():
        if key=='loss_bits_order0_order1_order2':
            for a,b in zip(actual[key],value):error=max(error,close(a,b,'locus loss'))
        elif key in ('gain01_bits_per_target','gain12_bits_per_target'):
            close(actual[key],value,key)
        else:require(type(actual[key]) is type(value) and actual[key]==value,'reference locus field changed: '+key)
    return error


def aggregate(scores):
    require(scores,'nonempty original scoring population required')
    count=sum(s['targets'] for s in scores)
    require(count>0,'positive original target denominator required')
    totals=[math.fsum(s['loss_bits_order0_order1_order2'][j] for s in scores) for j in range(3)]
    output={'loci':len(scores),'tokens':sum(s['tokens'] for s in scores),'units':sum(s['units'] for s in scores),
            'targets':count,'loss_bits_order0_order1_order2':totals}
    for name,a,b in [('01',0,1),('12',1,2)]:
        output['pooled_gain'+name+'_bits_per_target']=(totals[a]-totals[b])/count
        output['locus_macro_gain'+name+'_bits_per_target']=math.fsum(s['gain'+name+'_bits_per_target'] for s in scores)/len(scores)
    for order in [1,2]:
        key=f'unseen_order{order}_context_targets';output[key]=sum(s[key] for s in scores)
    roles=[]
    for index,role in enumerate(ROLES):
        parts=[s['roles'][index] for s in scores]
        require(all(p['role']==role for p in parts),'role ledger order changed')
        n=sum(p['targets'] for p in parts)
        losses=[math.fsum(p['loss_bits_order0_order1_order2'][j] for p in parts) for j in range(3)]
        gain=math.fsum(p['gain12_bits'] for p in parts)
        close(gain,losses[1]-losses[2],'aggregate role gain/loss identity')
        roles.append({'role':role,'targets':n,'loss_bits_order0_order1_order2':losses,'gain12_bits':gain,
                      'mean_gain12_bits_per_target':gain/n if n else None,
                      'pooled_contribution12_bits_per_target':gain/count})
    require(sum(r['targets'] for r in roles)==count and roles[0]['targets']==roles[3]['targets']==output['tokens']
            and sum(r['targets'] for r in roles[:3])==output['units'],'aggregate event population changed')
    for j in range(3):close(math.fsum(r['loss_bits_order0_order1_order2'][j] for r in roles),totals[j],'aggregate loss role sum')
    close(math.fsum(r['pooled_contribution12_bits_per_target'] for r in roles),
          output['pooled_gain12_bits_per_target'],'pooled contribution sum')
    return {**output,'roles':roles}


def verify_aggregate(actual,expected):
    for field,value in expected.items():
        if field=='loss_bits_order0_order1_order2':
            for a,b in zip(actual[field],value):close(a,b,'population loss')
        elif type(value) is float:close(actual[field],value,field)
        else:require(type(actual[field]) is type(value) and actual[field]==value,'reference aggregate changed: '+field)


def add_group_contributions(summary,groups):
    require(groups and all(g['targets']>0 for g in groups),'all original nonempty groups required')
    for index,role in enumerate(ROLES):
        require(summary['roles'][index]['role']==role and all(g['roles'][index]['role']==role for g in groups),
                'group role order changed')
        summary['roles'][index]['equal_group_contribution12_bits_per_target']=math.fsum(
            g['roles'][index]['gain12_bits']/g['targets'] for g in groups)/len(groups)
        summary['roles'][index]['groups_with_no_role_targets']=sum(g['roles'][index]['targets']==0 for g in groups)
    close(math.fsum(r['equal_group_contribution12_bits_per_target'] for r in summary['roles']),
          math.fsum(g['pooled_gain12_bits_per_target'] for g in groups)/len(groups),'equal-group role sum')


def derive_groups(keys,mapping,root,reference):
    image=load_split_json((root/'research/folio-alignment/transcription-image-coverage.json').read_text())
    canvases=list(csv.DictReader(io.StringIO((root/'research/image-index/canvases.csv').read_text())))
    components=dependency_components(canvases)
    require(components==image['dependency_components'],'full component graph changed')
    members={c['group_id']:c['folio_ids'] for c in components}
    by_leaf,by_side=defaultdict(set),defaultdict(set)
    leaf_group={leaf:g for g,leaves in members.items() for leaf in leaves}
    for canvas in canvases:
        for side in filter(None,canvas['explicit_folio_sides'].split(';')):
            by_leaf[side[:-1]].add(canvas['canvas_uri']);by_side[side].add(canvas['canvas_uri'])
    require({k:sorted(v) for k,v in by_leaf.items()}==image['indexed_canvas_ids_by_leaf'],'canvas membership changed')
    pages={p['page_id']:p for p in image['pages']}
    require(len(pages)==len(image['pages']),'duplicate image page')
    groups=defaultdict(list);page_groups={}
    for key in keys:
        page=mapping[key]['page_id'];sides=page_reference(page)['folio_sides']
        candidates={leaf_group.get(s[:-1]) for s in sides}
        require(sides and all(by_side[s] for s in sides) and len(candidates)==1 and None not in candidates,
                'selected page has no complete supported component')
        group=next(iter(candidates))
        require(pages[page]['side_reference_status']=='side_references_matched' and pages[page]['dependency_group']==group,
                'selected source page differs from image receipt')
        groups[group].append(key);page_groups[page]=group
    assignments={g:int.from_bytes(hashlib.sha256(compact(['grouped-symbol-prediction-v1',20261012,g])).digest(),'big')%5 for g in groups}
    manifest=[{'group_id':g,'fold':assignments[g],'folio_ids':members[g],
               'source_page_ids':sorted({mapping[k]['page_id'] for k in groups[g]}),'locus_keys':sorted(groups[g]),
               'canvas_ids':sorted({uri for leaf in members[g] for uri in by_leaf[leaf]})} for g in sorted(groups)]
    require(len(groups)==91 and manifest==reference['folds']['group_assignments']
            and sha(compact(manifest))==reference['folds']['manifest_sha256'],'original full fold manifest changed')
    return assignments,page_groups,manifest


def evaluate(rows,assignments,alphabet,expected):
    require(set(assignments)=={r['group'] for r in rows} and set(assignments.values())==set(range(5)),
            'complete original groups/folds required')
    saved={s['locus_key']:s for s in expected['loci']}
    require(len(saved)==len(expected['loci'])==len(rows) and set(saved)=={r['key'] for r in rows},'original locus coverage changed')
    scores=[];folds=[];maximum=0
    for fold,original in enumerate(expected['folds']):
        require(original['fold']==fold,'reference fold order changed')
        train=[r for r in rows if assignments[r['group']]!=fold];test=[r for r in rows if assignments[r['group']]==fold]
        train_groups=sorted({r['group'] for r in train});test_groups=sorted({r['group'] for r in test})
        require(train and test and not set(train_groups)&set(test_groups)
                and train_groups==original['training_group_ids'] and test_groups==original['scoring_group_ids'],
                'original fit/scoring group exclusion changed')
        model=fit(train,alphabet);counts=counts_record(model)
        require(sha(compact(counts))==original['fitted_counts_sha256']
                and counts['target_counts']==original['training_target_counts']
                and len(train)==original['training_loci'] and model['total']==original['training_targets']
                and len(model['first_totals'])==original['observed_order1_contexts']
                and len(model['second_totals'])==original['observed_order2_contexts'],'original fitted-count tables changed')
        cache={};scored=[score_row(r,model,fold,cache) for r in test]
        for score in scored:maximum=max(maximum,verify_row(score,saved[score['locus_key']]))
        summary=aggregate(scored)
        verify_aggregate(summary,{k:original[k] for k in summary if k!='roles'})
        folds.append({'fold':fold,'fitted_counts_sha256':original['fitted_counts_sha256'],
                      'training_group_ids':train_groups,'scoring_group_ids':test_groups,**summary})
        scores.extend(scored)
    require(Counter(s['locus_key'] for s in scores)==Counter(r['key'] for r in rows),'score coverage changed')
    by_group=defaultdict(list)
    for score in scores:by_group[score['group_id']].append(score)
    groups=[{'group_id':g,'fold':assignments[g],**aggregate(v)} for g,v in sorted(by_group.items())]
    require(len(groups)==len(expected['groups']),'reference group count changed')
    for actual,original in zip(groups,expected['groups']):
        verify_aggregate(actual,{k:original[k] for k in actual if k!='roles'})
    summary=aggregate(scores);summary['groups']=len(groups)
    for name in ['01','12']:
        summary['group_macro_gain'+name+'_bits_per_target']=math.fsum(g['pooled_gain'+name+'_bits_per_target'] for g in groups)/len(groups)
    summary['positive_order2_fold_count']=sum(f['pooled_gain12_bits_per_target']>0 for f in folds)
    summary['fixed_second_order_preference']=(summary['pooled_gain12_bits_per_target']>=.02
        and summary['group_macro_gain12_bits_per_target']>0 and summary['positive_order2_fold_count']==5)
    verify_aggregate(summary,expected['summary'])
    add_group_contributions(summary,groups)
    return {'reference_summary_unchanged':expected['summary'],'summary':summary,'folds':folds,'groups':groups,
            'loci':sorted(scores,key=lambda s:s['locus_key']),'maximum_original_locus_loss_difference_bits':maximum}


def build_report(reference_path,root=ROOT):
    manifest=validate_inputs(root);reference=load_reference(reference_path,manifest)
    old_parent=load_split_json((root/'research/representation/paired_symbol_entropy.json').read_text())
    require(parent.make_report(root)==old_parent,'entire paired-entropy receipt changed')
    plan,policies,_=parent.load_plan(root)
    maps,keys,selection=parent.prepare(parent.load_sources(root),plan)
    require(len(keys)==2485 and sha(compact(selection))==reference['selection']['parent_selection_sha256'],
            'reference source/cohort identity changed')
    assignments,page_groups,groups=derive_groups(keys,maps['ZL3b','split'],root,reference)
    require(len(reference['treatments'])==12,'all twelve original treatments required')
    results=[];index=0
    for sid in parent.SOURCE_IDS:
        for spacing in parent.SPACING:
            for policy in policies:
                original=reference['treatments'][index];index+=1
                require((original['source_id'],original['spacing'],original['unit_policy'])==(sid,spacing,policy['id']),
                        'reference treatment identity/order changed')
                alphabet=sorted(set(string.ascii_letters)|set(policy['patterns'])|{EOS})
                require(alphabet==original['target_alphabet'],'original target alphabet changed')
                rows=[]
                for key in keys:
                    row=maps[sid,spacing][key]
                    rows.append({'key':key,'page':row['page_id'],'group':page_groups[row['page_id']],
                                 'segments':[segment(token,policy['patterns']) for token in row['tokens']]})
                require(sha(compact(rows))==original['segmented_rows_sha256'],'original segmented rows changed')
                results.append({'source_id':sid,'spacing':spacing,'unit_policy':policy['id'],
                                'segmented_rows_sha256':original['segmented_rows_sha256'],
                                **evaluate(rows,assignments,alphabet,original)})
    require(validate_inputs(root)==manifest and sha(reference_path.read_bytes())==manifest['reference_report_sha256'],
            'fixed inputs changed during accounting')
    return {'schema_version':1,'analysis_id':manifest['analysis_id'],'analysis_status':manifest['analysis_status'],
            'reference_report_sha256':manifest['reference_report_sha256'],
            'reference_producer_sha256':manifest['reference_producer_sha256'],
            'reference_accepted_at_plan':manifest['reference_accepted_at_plan'],'input_pins':{**PINS,**manifest['input_pins']},
            'implementation_sha256':sha(Path(__file__).read_bytes()),'role_order':list(ROLES),
            'source_selection':reference['selection'],'group_assignments':groups,
            'parent_comparison_absolute_tolerance_bits':TOL,
            'prior_exposure':True,'valid_candidate_holdout':False,'new_model_or_decision':False,
            'treatments':results,'limitations':['Role contributions are score-sum terms, not causal fractions explained.',
                'Notation-unit positions and token termination do not identify physical glyphs or words.',
                'Original coarse image groups, related editions and corpus exposure remain dependent.',
                'No glyph function, language, decipherment or translation is established.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-report',type=Path,required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output',type=Path);mode.add_argument('--check',type=Path)
    args=parser.parse_args()
    try:
        if args.output:require(not args.output.exists() and not args.output.is_symlink(),'output must be a new file')
        result=build_report(args.reference_report,ROOT);raw=encoded(result);payload=packed(raw)
        require(unpack(payload)==raw,'lossless compressed report round-trip failed')
        if args.check:
            original=args.check.read_bytes();load_split_json(unpack(original).decode())
            require(unpack(original)==raw and original==payload,'complete compressed report differs from replay')
        else:
            validate_inputs(ROOT)
            require(sha(args.reference_report.read_bytes())==result['reference_report_sha256']
                    and sha(Path(__file__).read_bytes())==result['implementation_sha256'],'producer/reference changed before writing')
            with args.output.open('xb') as destination:destination.write(payload)
        print('Complete accounting verified.' if args.check else 'New complete accounting created.')
        print('Uncompressed JSON SHA-256:',sha(raw))
    except (OSError,ValueError,KeyError,TypeError,EOFError) as error:
        parser.exit(1,f'event accounting failed: {error}\n')


if __name__=='__main__':main()
