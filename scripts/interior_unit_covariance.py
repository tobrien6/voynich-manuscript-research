"""Exact joint ideal moments for accepted paired interior notation counts."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import re

try:
    from . import interior_unit_controls as unit
    from . import half_control_moments as formatting
    from . import paired_interior_moments as joint
except ImportError:
    import interior_unit_controls as unit
    import half_control_moments as formatting
    import paired_interior_moments as joint

ROOT=Path(__file__).resolve().parents[1]
METHOD='ideal-paired-unit-power-partition-covariance-v1'
PLAN='research/transliteration/INTERIOR_COVARIANCE_PLAN.md'
PINS='research/transliteration/interior-covariance-pins.json'
UNIT='research/transliteration/interior_unit_controls.json'
MOMENTS='research/transliteration/half_control_moments.json'
PIN_SHA256='0dfd611f66f54be079ff4eb0069b2ff943e05b4de655de7a88d8b75d529782c9'
POLICIES=['ascii_letters','bench_sequences','bench_and_minim_sequences']
SCOPES=['unrestricted','half']
UPPER=[(i,j) for i in range(3) for j in range(i,3)]
VARIANTS=[(s,p) for s in unit.original.SOURCE_IDS for p in unit.original.SPACING]


def sha(raw):return hashlib.sha256(raw).hexdigest()


def unpack(value):
    return Fraction(int(value['numerator'],16 if value.get('encoding')=='base16-integer-strings' else 10),
                    int(value['denominator'],16 if value.get('encoding')=='base16-integer-strings' else 10))


def small(value):return [str(value.numerator),str(value.denominator)]


def large(value):return formatting.aggregate_fraction_record(value)


def upper(matrix):return [small(matrix[i][j]) for i,j in UPPER]


def covariance_of_mean(matrices):
    if not matrices:raise ValueError('nonempty equal-locus denominator required')
    result=[[sum((m[i][j] for m in matrices),Fraction())/len(matrices)**2 for j in range(3)] for i in range(3)]
    joint.validate_psd(result)
    return result


def empirical_covariance(arrays):
    if (len(arrays)!=3 or len({len(a) for a in arrays})!=1 or not arrays[0]
            or any(type(v) is not float or not math.isfinite(v) for a in arrays for v in a)):
        raise ValueError('three complete finite float control arrays required')
    n=len(arrays[0]);means=[math.fsum(a)/n for a in arrays]
    matrix=[[math.fsum((x-means[i])*(y-means[j]) for x,y in zip(arrays[i],arrays[j]))/n for j in range(3)] for i in range(3)]
    return means,matrix


def correlation(matrix,i,j):
    return float(matrix[i][j])/math.sqrt(float(matrix[i][i])*float(matrix[j][j])) if matrix[i][i] and matrix[j][j] else None


def paired_diagnostic(observed,variance):
    if variance<0:raise ValueError('negative paired variance')
    return {'observed_change_exact':large(observed),'ideal_variance_exact':large(variance),
            'ideal_standard_deviation_approx':math.sqrt(float(variance)),
            'observed_over_ideal_sd_approx':float(observed)/math.sqrt(float(variance)) if variance else None,
            'variance_status':'positive' if variance else ('zero_variance_zero_difference' if not observed else 'zero_variance_nonzero_difference')}


def load_inputs():
    raw=(ROOT/PINS).read_bytes()
    if sha(raw)!=PIN_SHA256:raise ValueError('frozen covariance pin manifest changed')
    pins=unit.load_split_json(raw.decode())
    for name,expected in pins.items():
        if sha((ROOT/name).read_bytes())!=expected:raise ValueError('frozen covariance input changed: '+name)
    return unit.load_split_json((ROOT/UNIT).read_text()),unit.load_split_json((ROOT/MOMENTS).read_text()),pins


def prepare(previous):
    pinned=unit.pinned_inputs();settings=pinned[unit.SETTINGS]
    sources=unit.load_sources();treatments,accepted,selection=unit.original.prepare(sources)
    if previous['selection']!={'loci':len(accepted),'cohort_sha256':selection['retained_locus_keys_sha256']}:
        raise ValueError('accepted unit cohort changed')
    if [(t['source_id'],t['spacing']) for t in previous['treatments']]!=VARIANTS or set(treatments)!=set(VARIANTS):
        raise ValueError('complete source/spacing family required')
    prepared=[]
    for old in previous['treatments']:
        mapping=treatments[old['source_id'],old['spacing']]
        token_rows=[(mapping[key]['page_id'],key,mapping[key]['tokens']) for key in accepted]
        converted=unit.convert_rows(token_rows,settings['policies'],settings['fallback_examples_not_grouped'])
        if [p['policy_id'] for p in old['unit_policies']]!=POLICIES:raise ValueError('complete count-policy family required')
        for new,saved in zip(converted,old['unit_policies']):
            if any(new[key]!=saved[key] for key in ('length_corpus_sha256','scope_audit','matching_precedence','unit')):
                raise ValueError('count vector, map or source audit changed')
            observed=unit.moments(new['rows'])
            for key,value in observed.items():
                if isinstance(value,dict):
                    if value!=saved[key]:raise ValueError('exact parent expectation changed')
                elif abs(value-saved[key])>1e-12:raise ValueError('parent observed/expected mean changed')
            if saved['loci']!=len(accepted):raise ValueError('parent denominator changed')
            for scope in SCOPES:
                controls=saved[scope]['control_statistics']
                if len(controls)!=previous['controls']['trials'] or previous['controls']['trials']!=999:
                    raise ValueError('all original999 controls required')
        prepared.append((old,converted))
    return prepared


def summarize(previous,converted,old_moments,progress=None):
    rows=[v['rows'] for v in converted];n=len(rows[0])
    if not n or any([(p,k,len(v)) for p,k,v in rows[0]]!=[(p,k,len(v)) for p,k,v in other] for other in rows[1:]):
        raise ValueError('identical nonempty occurrence identities required')
    accepted_moments={(r['page_id'],r['locus_key']):r for r in old_moments['per_locus']}
    if len(accepted_moments)!=n:raise ValueError('all acceptedASCII locus moments required')
    matrices={scope:[] for scope in SCOPES};observed={scope:[Fraction()]*3 for scope in SCOPES}
    zero_half=[[] for _ in POLICIES];per_locus=[]
    for index,triplet in enumerate(zip(*rows)):
        page,key,_=triplet[0];vectors=[row[2] for row in triplet];record={'page_id':page,'locus_key':key}
        for scope in SCOPES:
            means,matrix=joint.policy_matrix(vectors,scope);matrices[scope].append(matrix)
            for i,values in enumerate(vectors):
                size,squared,adjacent=unit.original.components(values)
                raw=Fraction(size*adjacent,(size-1)*squared) if squared else Fraction()
                expected=unit.half.exact_half_expectation(values) if scope=='half' else (Fraction(-1,size-1) if squared else Fraction())
                if means[i]!=expected:raise ValueError('exact mean differs from accepted centering')
                observed[scope][i]+=raw-means[i]
                if scope=='half' and not matrix[i][i]:zero_half[i].append({'page_id':page,'locus_key':key})
            if scope=='half' and (matrix[0][0]!=unpack(accepted_moments[page,key]['association_variance'])
                                  or means[0]!=unpack(accepted_moments[page,key]['association_mean'])):
                raise ValueError('acceptedASCII half locus mean/variance differs')
            record[scope]={'uncentered_means':[small(v) for v in means],'covariance_upper':upper(matrix)}
        per_locus.append(record)
        if progress and (index+1)%500==0:progress(f'{index+1}/{n} joint loci')
    out={}
    for i,saved in enumerate(previous['unit_policies']):
        if zero_half[i]!=saved['exact_half_invariance']['invariant_identifiers']:
            raise ValueError('exact mapped zero-variance identifiers differ from accepted invariant audit')
    for scope in SCOPES:
        aggregate=covariance_of_mean(matrices[scope]);points=[value/n for value in observed[scope]]
        for i,point in enumerate(points):
            if abs(float(point)-previous['unit_policies'][i][scope]['observed_centered_association'])>1e-12:
                raise ValueError('exact observed mean differs from accepted unit report')
        if scope=='half' and aggregate[0][0]!=unpack(old_moments['exact_ideal_mean_variance']):
            raise ValueError('acceptedASCII aggregate half variance differs')
        arrays=[p[scope]['control_statistics'] for p in previous['unit_policies']]
        empirical_means,empirical=empirical_covariance(arrays)
        pairs=[]
        for i in (1,2):
            accepted=previous['unit_policies'][i]['paired_change_from_ascii'][scope]
            actual=[b-a for a,b in zip(arrays[0],arrays[i])]
            if actual!=accepted['control_statistics']:raise ValueError('original paired control array differs')
            variance=joint.paired_variance(aggregate,i);mean=math.fsum(actual)/len(actual)
            empirical_variance=math.fsum((value-mean)**2 for value in actual)/len(actual)
            if abs(empirical_variance-(empirical[i][i]+empirical[0][0]-2*empirical[i][0]))>1e-15:
                raise ValueError('empirical paired variance identity differs')
            pairs.append({'policy_id':POLICIES[i],**paired_diagnostic(points[i]-points[0],variance),
                          'accepted_observed_change_approx':accepted['observed_centered_association'],
                          'accepted_two_sided_tail_count':accepted['two_sided_tail_count'],
                          'accepted_exploratory_two_sided_tail':accepted['exploratory_two_sided_tail'],
                          'existing_control_population_variance':empirical_variance,
                          'empirical_to_ideal_sd_ratio_approx':math.sqrt(empirical_variance/float(variance)) if variance else None})
        out[scope]={'exact_ideal_mean_covariance':[[large(v) for v in row] for row in aggregate],
                    'exact_observed_centered_means':[large(v) for v in points],
                    'ideal_standard_deviations_approx':[math.sqrt(float(aggregate[i][i])) for i in range(3)],
                    'ideal_correlations_approx':[[correlation(aggregate,i,j) for j in range(3)] for i in range(3)],
                    'existing_controls':{'repetitions':len(arrays[0]),'means':empirical_means,'population_covariance':empirical,
                                         'population_correlations':[[correlation(empirical,i,j) for j in range(3)] for i in range(3)]},
                    'paired_changes':pairs}
    return {'source_id':previous['source_id'],'spacing':previous['spacing'],'source_sha256':previous['source_sha256'],
            'loci':n,'accepted_effect_denominator':n,'policy_vector_sha256':{v['policy_id']:v['length_corpus_sha256'] for v in converted},
            'exact_half_zero_variance_identifiers':{pid:ids for pid,ids in zip(POLICIES,zero_half)},
            'ascii_half_variances_match_accepted':True,'per_locus':per_locus,**out}


def report(progress=None):
    previous,moments,pins=load_inputs();prepared=prepare(previous)
    old={(t['source_id'],t['spacing']):t for t in moments['treatments']}
    if set(old)!=set(VARIANTS):raise ValueError('accepted moment treatment inventory changed')
    results=[]
    for saved,converted in prepared:
        sid,spacing=saved['source_id'],saved['spacing']
        callback=(lambda message:progress(f'{sid}/{spacing}: {message}')) if progress else None
        results.append(summarize(saved,converted,old[sid,spacing],callback))
    return {'schema_version':1,'method':METHOD,'status':'exposed-corpus paired operational-count ideal-ensemble audit',
            'python_version':platform.python_version(),'input_pins':pins,'pin_manifest_sha256':PIN_SHA256,
            'implementation_sha256':sha(Path(__file__).read_bytes()),'policies':POLICIES,'scopes':SCOPES,
            'per_locus_fraction_encoding':'two decimal integer strings: numerator,denominator',
            'per_locus_covariance_upper_indices':[list(p) for p in UPPER],
            'aggregate_fraction_encoding':'labelled base16 integer strings plus60-significant-digit approximate decimal',
            'selection':previous['selection'],'ideal_locus_permutations_independent_by_stipulation':True,
            'existing_hash_controls_a_separate_finite_empirical_measure':True,'treatments':results,
            'new_permutation_draws':0,'new_tail_probabilities':0,'physical_glyph_policy_selected':False,'mechanism_or_translation_validated':False}


def protect_output(path):
    unit.protect_output(path)
    pins=unit.load_split_json((ROOT/PINS).read_text());protected=[ROOT/name for name in pins]+[ROOT/PINS,Path(__file__).resolve()]
    if any(path.resolve()==p.resolve() or (path.exists() and p.exists() and path.samefile(p)) for p in protected):
        raise ValueError('output aliases covariance inputs, code or plan')


def serialize(value):
    raw=json.dumps(value,indent=2,allow_nan=False)+'\n'
    # Keep each exact small fraction legible as one pair, without changing JSON values.
    return re.sub(r'\[\n\s*"(-?\d+)",\n\s*"(\d+)"\n\s*\]',lambda match:'["'+match[1]+'", "'+match[2]+'"]',raw)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--new-report',type=Path);mode.add_argument('--check',type=Path)
    args=parser.parse_args()
    try:
        path=args.new_report or args.check;protect_output(path)
        if args.new_report and (path.exists() or path.is_symlink()):raise ValueError('new report destination already exists')
        result=report(progress=lambda message:print(message,flush=True));payload=serialize(result)
        if args.check:
            if not unit.same_report(result,unit.load_split_json(path.read_text())):raise ValueError('complete covariance report differs from replay')
        else:
            protect_output(path)
            with path.open('x',encoding='utf-8') as out:out.write(payload)
    except (ValueError,OSError,KeyError,TypeError) as error:parser.exit(1,f'Paired interior covariance failed: {error}\n')
    print('All8 joint ensembles and16 paired changes verified.' if args.check else 'All8 joint ensembles and16 paired changes saved.')


if __name__=='__main__':main()
