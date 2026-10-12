"""Render both frozen interior diagnostics; no source/model measurement reruns."""
import argparse
import ast
import gzip
from copy import deepcopy
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import re

try:
    from .validate_evaluation_split import load_split_json
except ImportError:
    from validate_evaluation_split import load_split_json

ROOT=Path(__file__).resolve().parents[1]
INPUTS={
    'research/literature/self-citation-interior.json':'113b4b407691c3765e949de5f8390703bf0fdd94cfa3d6d9a30ed05790ff6829',
    'research/literature/self-citation-size-conditioned.json':'2610917f3946dc757d2d68a5839cb9be64c1d38b2567449c218bc4a1c6ad0522',
}
VARIANTS=[(s,p) for s in ('ZL3b','IT2a') for p in ('split','join')]
POLICIES=['ascii_letters','bench_sequences','bench_and_minim_sequences']
SCOPES=['unrestricted','half']
IDENTITIES=[(s,p,pid,scope) for s,p in VARIANTS for pid in POLICIES for scope in SCOPES]
STEM='generator-interior-comparison'
AMENDMENT='research/literature/figures/generator-interior-figure-amendment-1.json'
AMENDMENT_SHA256='d7950bc9292b945a4020bf3116db1dc16e11c1bf8486ec6f82a6a2df78032d39'


def digest(raw):return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def parse_decimal_integer(value):
    if type(value) is int:return value
    if not isinstance(value,str) or not re.fullmatch(r'-?[0-9]+',value):
        raise ValueError('decimal integer required')
    negative=value.startswith('-');digits=value[1:] if negative else value;number=0
    for start in range(0,len(digits),18):
        piece=digits[start:start+18];number=number*10**len(piece)+int(piece)
    return -number if negative else number


def unpack(value):
    if not isinstance(value,dict) or type(value.get('mean')) is not float:
        raise ValueError('exact numeric record and float display mean required')
    numerator,denominator=value['numerator'],value['denominator']
    if type(numerator) not in (int,str) or type(denominator) not in (int,str) or parse_decimal_integer(denominator)<=0:
        raise ValueError('invalid exact numerator or denominator')
    result=Fraction(parse_decimal_integer(numerator),parse_decimal_integer(denominator))
    if not math.isfinite(value['mean']) or value['mean']!=float(result):
        raise ValueError('display mean differs from exact fraction')
    return result


def profiles(record):
    if [p['policy_id'] for p in record['policies']]!=POLICIES:
        raise ValueError('complete ordered count-policy family required')
    return {p['policy_id']:p for p in record['policies']}


def variants(records):
    if [(r['source_id'],r['spacing']) for r in records]!=VARIANTS:
        raise ValueError('all four ordered source/spacing variants required')
    return {(r['source_id'],r['spacing']):r for r in records}


def cases(records):
    if [r['seed'] for r in records]!=list(range(1,32)) or any(type(r['seed']) is not int for r in records):
        raise ValueError('all31 ordered fixed seeds required')
    return records


def comparison_index(records):
    indexed={(r['source_id'],r['spacing'],r['policy_id'],r['scope']):r for r in records}
    if len(records)!=24 or set(indexed)!=set(IDENTITIES):
        raise ValueError('all24 unique comparison identities required')
    return indexed


def extract_family(targets,records,comparisons,standardized):
    target_index=variants(targets);records=cases(records);index=comparison_index(comparisons);out=[]
    for sid,spacing,pid,scope in IDENTITIES:
        target=unpack(profiles(target_index[sid,spacing])[pid]['scores'][scope])
        seed_values=[]
        for case in records:
            source=variants(case['standardized'])[sid,spacing] if standardized else case
            seed_values.append(unpack(profiles(source)[pid]['scores'][scope]))
        low,high=min(seed_values),max(seed_values);item=index[sid,spacing,pid,scope]
        inside=low<=target<=high;gap=max(low-target,target-high,Fraction(0))
        if (item['all_fixed_seed_values_defined'] is not True or item['within_fixed_seed_range'] is not inside
                or unpack(item['target'])!=target or unpack(item['seed_minimum'])!=low
                or unpack(item['seed_maximum'])!=high or unpack(item['outside_range_gap'])!=gap):
            raise ValueError('plotted point, exact range or membership differs from fixed31 values')
        out.append(deepcopy(item))
    return out


def figure_data(prior,sized):
    if (type(prior['schema_version']) is not int or prior['schema_version']!=1
            or prior['method']!='fixed-self-citation-interior-order-v1'
            or type(sized['schema_version']) is not int or sized['schema_version']!=1
            or sized['method']!='fixed-self-citation-exact-size-standardization-v1'
            or sized['parent_report_sha256']!=list(INPUTS.values())[0]):
        raise ValueError('frozen experiment schema or parent identity changed')
    prior_keys=prior['selection']['selected_keys'];selection=sized['selection'];common=selection['selected_keys']
    if (not prior_keys or len(prior_keys)!=len(set(prior_keys)) or not common
            or len(common)!=len(set(common)) or not set(common)<=set(prior_keys)
            or selection['parent_keys']!=len(prior_keys)
            or unpack(selection['coverage'])!=Fraction(len(common),len(prior_keys))):
        raise ValueError('full/common source cohort or coverage changed')
    old=extract_family(prior['targets'],prior['cases'],prior['comparisons'],False)
    full=sized['primary'];primary=comparison_index(full['comparisons']);variants(full['targets'])
    complete=[0]*4
    for case in cases(full['cases']):
        for j,record in enumerate(variants(case['standardized']).values()):
            if type(record['target_rows']) is not int or record['target_rows']!=len(prior_keys):
                raise ValueError('full source denominator changed')
            supported=not record['missing_required_sizes']
            if record['all_required_sizes_supported'] is not supported:
                raise ValueError('complete-size support flag differs from missing cells')
            complete[j]+=int(supported)
            for p in profiles(record).values():
                for scope in SCOPES:
                    value=p['scores'][scope]
                    if supported:unpack(value)
                    elif value is not None:raise ValueError('missing required size must retain undefined score')
    if full['comparison_ranges_defined'] is not False or full['all_target_points_within_fixed_seed_ranges'] is not None:
        raise ValueError('primary undefinedness must remain explicit')
    for previous in old:
        identity=tuple(previous[k] for k in ('source_id','spacing','policy_id','scope'));item=primary[identity]
        if (item['all_fixed_seed_values_defined'] is not False or item['within_fixed_seed_range'] is not None
                or any(item[k] is not None for k in ('seed_minimum','seed_maximum','outside_range_gap'))
                or unpack(item['target'])!=unpack(previous['target'])):
            raise ValueError('undefined primary range or unchanged source point misrepresented')
    supported=sized['supported_common']
    for record in variants(supported['targets']).values():
        if type(record['target_rows']) is not int or record['target_rows']!=len(common):
            raise ValueError('common source denominator changed')
    common_points=extract_family(supported['targets'],supported['cases'],supported['comparisons'],True)
    values=[float(unpack(item[field])) for item in old+common_points for field in ('target','seed_minimum','seed_maximum')]
    low,high=min(values),max(values);padding=(high-low)*.08
    return {'schema_version':1,'figure_version':'frozen-generator-interior-comparison-v1','input_report_sha256':INPUTS,
            'prior_source_loci':len(prior_keys),'common_source_loci':len(common),'common_coverage':selection['coverage'],
            'common_generator_original_sizes':selection['common_generator_sizes'],
            'prior_plotted_comparisons':old,'supported_plotted_comparisons':common_points,
            'primary_undefined_comparisons':[deepcopy(primary[identity]) for identity in IDENTITIES],
            'primary_seeds_with_complete_size_support':[{'source_id':s,'spacing':p,'complete_seeds':n,'fixed_seeds':31} for (s,p),n in zip(VARIANTS,complete)],
            'shared_x_limits':[low-padding,high+padding],
            'scope':'48 existing points/ranges and24 undefined primary ranges; no new measurements, calibrated probability coverage, independent treatments or decipherment'}


def read_data():
    reports=[]
    for name,expected in INPUTS.items():
        raw=(ROOT/name).read_bytes()
        if digest(raw)!=expected:raise ValueError('frozen input report changed: '+name)
        reports.append(load_split_json(raw.decode()))
    return figure_data(*reports)


def render(data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MultipleLocator
    import numpy
    import PIL
    labels=['ASCII / full','ASCII / half','Bench / full','Bench / half','Bench+minim / full','Bench+minim / half']
    blue,amber,gray='#246C94','#B9630D','#687685'
    artist_positions=[]
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'generator-interior-comparison-v1','svg.fonttype':'none'}):
        fig,axes=plt.subplots(2,4,figsize=(17,11.6))
        fig.subplots_adjust(left=.135,right=.98,bottom=.13,top=.785,hspace=.72,wspace=.18)
        for row,family in enumerate(('prior_plotted_comparisons','supported_plotted_comparisons')):
            for column,(sid,spacing) in enumerate(VARIANTS):
                ax=axes[row,column];points=[p for p in data[family] if (p['source_id'],p['spacing'])==(sid,spacing)]
                for y,item in enumerate(points):
                    lo,hi,x=[float(unpack(item[k])) for k in ('seed_minimum','seed_maximum','target')]
                    bar=ax.plot([lo,hi],[y,y],color=gray,linewidth=3,solid_capstyle='butt',zorder=2)[0]
                    ax.plot([lo,hi],[y,y],linestyle='none',marker='|',color=gray,markersize=10,zorder=2)
                    inside=item['within_fixed_seed_range']
                    point=ax.scatter([x],[y],color=amber if inside else blue,marker='D' if inside else 'o',s=50,zorder=3)
                    artist_positions.append({'family':family,**{k:item[k] for k in ('source_id','spacing','policy_id','scope')},
                                             'source_xy':[float(v) for v in point.get_offsets()[0]],
                                             'range_x':[float(v) for v in bar.get_xdata()],
                                             'range_y':[float(v) for v in bar.get_ydata()]})
                ax.axvline(0,color='#BDC5CD',linewidth=.8,linestyle=':',zorder=1)
                ax.xaxis.set_major_locator(MultipleLocator(.04));ax.set_xlim(*data['shared_x_limits'])
                ax.set_ylim(5.6,-.6);ax.set_yticks(range(6),labels if column==0 else [])
                ax.tick_params(axis='both',length=0,pad=8);ax.grid(axis='x',color='#E7EBEF',linewidth=.7)
                for spine in ax.spines.values():spine.set_visible(False)
                if row==0:ax.set_title(sid+' '+spacing,fontsize=13,fontweight='bold',loc='left',pad=12)
        fig.text(.045,.965,'Interior order in fixed generator outputs',fontsize=22,fontweight='bold',va='top')
        fig.text(.045,.916,'All 31 archived Java 17 seeds · three operational notation counts · exact full/half centering',fontsize=12)
        handles=[Line2D([0],[0],color=gray,lw=3,label='Fixed 31-seed minimum to maximum'),
                 Line2D([0],[0],color=blue,marker='o',ls='',label='Source mean outside range'),
                 Line2D([0],[0],color=amber,marker='D',ls='',label='Source mean inside range')]
        fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.039,.888),ncol=3,frameon=False,fontsize=11,columnspacing=2.8)
        prior_inside=sum(p['within_fixed_seed_range'] for p in data['prior_plotted_comparisons'])
        common_inside=sum(p['within_fixed_seed_range'] for p in data['supported_plotted_comparisons'])
        fig.text(.045,.818,f"Prior equal-row comparison: {data['prior_source_loci']:,} source loci · {prior_inside}/24 points inside range",fontsize=13,fontweight='bold')
        counts=' · '.join(f"{r['source_id']} {r['spacing']} {r['complete_seeds']}/31" for r in data['primary_seeds_with_complete_size_support'])
        fig.text(.045,.476,f"Full-cohort exact-size comparison: all 24 seed ranges undefined ({data['prior_source_loci']:,} loci).\n"
                 f'Seeds with complete required sizes: {counts}. Missing seeds are retained.',fontsize=11.5,linespacing=1.6,
                 bbox={'boxstyle':'round,pad=.7','facecolor':'#F2F5F7','edgecolor':'#D6DCE2'})
        fig.text(.045,.399,f"Predeclared common-supported comparison: {data['common_source_loci']:,} loci "
                 f"({100*data['common_coverage']['mean']:.2f}%) · {common_inside}/24 points inside range",fontsize=13,fontweight='bold')
        fig.text(.5,.086,'Centered association of neighboring interior counts',ha='center',fontsize=12)
        fig.text(.045,.053,'Bars have no calibrated probability coverage. Related source treatments are not independent replications.',fontsize=10.5)
        fig.text(.045,.025,'Both common cohort and model weights change; compatible points do not isolate a weighting effect. Physical units and meaning remain unresolved.',fontsize=10,color='#444B53')
        buffers={}
        for ext,kwargs in [('png',{'dpi':160,'metadata':{'Software':'Matplotlib'}}),('svg',{'metadata':{'Date':None,'Creator':'Voynich Manuscript Research / Matplotlib','Title':'Frozen generator interior comparison'}})]:
            stream=io.BytesIO();fig.savefig(stream,format=ext,**kwargs);buffers[ext]=stream.getvalue()
        plt.close(fig)
    buffers['svg']=('\n'.join(line.rstrip() for line in buffers['svg'].decode().splitlines())+'\n').encode()
    provenance=dict(data,artist_positions=artist_positions,renderer={'python':platform.python_version(),'matplotlib':matplotlib.__version__,'numpy':numpy.__version__,'pillow':PIL.__version__,
                                  'freetype':matplotlib.ft2font.__freetype_version__,
                                  'dejavu_sans_sha256':digest((Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf').read_bytes()),
                                  'script_sha256':digest(Path(__file__).read_bytes())},
                    output_sha256={ext:digest(raw) for ext,raw in buffers.items()})
    buffers['json']=encoded(provenance)
    return buffers


def verify_export_transition(output):
    amendment=(ROOT/AMENDMENT).read_bytes()
    if digest(amendment)!=AMENDMENT_SHA256:raise ValueError('frozen figure amendment changed')
    record=json.loads(amendment)
    originals={}
    for ext,entry in record['original_exports'].items():
        compressed=(ROOT/entry['path']).read_bytes()
        if digest(compressed)!=entry['compressed_sha256']:raise ValueError('original figure archive changed')
        originals[ext]=gzip.decompress(compressed)
        if digest(originals[ext])!=entry['uncompressed_sha256']:raise ValueError('original figure bytes changed')
    if output['png']!=originals['png'] or output['svg']!=originals['svg']:
        raise ValueError('figure maintenance changed PNG/SVG bytes')
    old,new=json.loads(originals['json']),json.loads(output['json'])
    for key in old:
        if key not in record['allowed_provenance_changed_fields'] and encoded(old[key])!=encoded(new[key]):
            raise ValueError('figure maintenance changed scientific, artist or display data')
    if set(old)!=set(new):raise ValueError('figure provenance field inventory changed')
    if new['input_report_sha256']!=INPUTS:
        raise ValueError('effective figure input identities differ from pinned reports')
    if set(old['renderer'])!=set(new['renderer']) or any(old['renderer'][key]!=new['renderer'][key] for key in old['renderer'] if key!='script_sha256'):
        raise ValueError('figure maintenance changed recorded rendering environment')
    if new['renderer']['script_sha256']!=digest(Path(__file__).read_bytes()):
        raise ValueError('effective renderer identity differs')
    raw=(ROOT/record['original_renderer_archive']).read_bytes()
    if digest(raw)!=record['original_renderer_compressed_sha256']:raise ValueError('original renderer archive changed')
    source=gzip.decompress(raw)
    if digest(source)!=record['original_renderer_sha256']:raise ValueError('original renderer source changed')
    def functions(raw):
        return {node.name:ast.dump(node,include_attributes=False) for node in ast.parse(raw).body if isinstance(node,ast.FunctionDef)}
    before,after=functions(source),functions(Path(__file__).read_bytes())
    if set(after)!=set(before)|{'parse_decimal_integer','verify_export_transition'}:
        raise ValueError('renderer function inventory changed outside amendment')
    if any(before[key]!=after[key] for key in before if key not in ('unpack','main')):
        raise ValueError('renderer changed a protected plotting/data function')
    return True


def new_directory_guard(directory,expected):
    if directory.exists() or directory.is_symlink() or directory.resolve()!=expected:
        raise ValueError('figure output directory must be new and retain its original resolved path')
    if expected.is_relative_to((ROOT/'data').resolve()) or expected.is_relative_to((ROOT/'scripts').resolve()):
        raise ValueError('figure output directory aliases source or code storage')


def write_exports(directory,expected,output):
    new_directory_guard(directory,expected)
    directory.mkdir(parents=True,exist_ok=False)
    for ext,raw in output.items():
        if directory.is_symlink() or directory.resolve()!=expected:
            raise ValueError('figure directory identity changed before writing')
        with (directory/(STEM+'.'+ext)).open('xb') as stream:stream.write(raw)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--new-output-dir',type=Path);mode.add_argument('--check-dir',type=Path)
    args=parser.parse_args()
    try:
        directory=args.new_output_dir or args.check_dir;expected=directory.resolve()
        if args.new_output_dir:new_directory_guard(directory,expected)
        output=render(read_data())
        verify_export_transition(output)
        if args.check_dir:
            for ext,raw in output.items():
                if (directory/(STEM+'.'+ext)).read_bytes()!=raw:raise ValueError('complete deterministic figure export differs: '+ext)
        else:write_exports(directory,expected,output)
    except (ValueError,OSError,KeyError,TypeError,ImportError) as error:parser.exit(1,f'Generator interior figure failed: {error}\n')
    print('Verified48 plotted comparisons and24 explicit undefined primary ranges.' if args.check_dir else 'Saved48 plotted comparisons and24 explicit undefined primary ranges.')


if __name__=='__main__':main()
