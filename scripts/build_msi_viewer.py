"""Build a local, offline comparison packet from the pinned MSI source intake."""

import argparse
from pathlib import Path
import subprocess

try:
    from .audit_eva_token_coverage import encoded
    from .check_msi_intake import PINS, RECORD, verify, sha, require, ROOT
    from .paragraph_token_corpus import strict_json
except ImportError:
    from audit_eva_token_coverage import encoded
    from check_msi_intake import PINS, RECORD, verify, sha, require, ROOT
    from paragraph_token_corpus import strict_json


BASE='research/image-index/msi-viewer'
SETTINGS=BASE+'/inputs.json'
TEMPLATE=BASE+'/template.html'
SCRIPT=BASE+'/viewer.js'
INPUTS=(*PINS, RECORD, 'scripts/check_msi_intake.py', 'scripts/verify_boundary_repeat_image.py')


def load_inputs(root=ROOT):
    settings=strict_json((root/SETTINGS).read_bytes())
    require(set(settings)=={'schema_version','viewer_id','parent_pr','parent_commit','parent_status_at_creation',
                           'original_parent_commit','current_dependency_status','input_sha256'}
            and type(settings['schema_version']) is int and settings['schema_version']==1
            and settings['viewer_id']=='local-msi-coordinate-comparison-v1'
            and set(settings['input_sha256'])==set(INPUTS), 'wrong viewer settings')
    require(settings['parent_commit']=='8a29dc4e4dab84711d0d82f765b2453acfbc2b8f'
            and type(settings['parent_pr']) is int and settings['parent_pr']==163,
            'wrong declared source contribution')
    require(settings['original_parent_commit']=='ee961733dffbeb98893407114634ed82816a81bc'
            and settings['parent_status_at_creation']=='pending review'
            and settings['current_dependency_status']=='accepted','source dependency history differs')
    for name in INPUTS:
        raw=(root/name).read_bytes()
        require(sha(raw)==settings['input_sha256'][name], 'pinned viewer input changed: '+name)
        old=subprocess.check_output(['git','show',settings['parent_commit']+':'+name],cwd=root)
        require(raw==old,'parent Git blob differs: '+name)
    record=strict_json((root/RECORD).read_bytes());verify(record,root=root)
    return settings,record


def packet_bytes(cache, root=ROOT):
    settings,record=load_inputs(root)
    verify(record,cache=cache,root=root)
    template=(root/TEMPLATE).read_bytes();script=(root/SCRIPT).read_bytes()
    files={'viewer.js':script};images=[]
    for item in record['selected_images']+record['yale_references']:
        filename=item['local_filename'];raw=(cache/filename).read_bytes()
        require(sha(raw)==item['metadata']['sha256'],'original image changed during packet construction')
        files['assets/'+filename]=raw
        is_yale='side' in item
        images.append({'id':'yale-'+item['side'] if is_yale else item['file_id'],
            'side':item['side'] if is_yale else item['source_side'],
            'name':'Ordinary Yale '+item['side'] if is_yale else item['name'],
            'collection':'Yale reference' if is_yale else ('RGB folder' if item['parent_id']=='1to9QOXNrSfIUITnogjkZSTy8zN553OGi' else 'Processed folder'),
            'url':item['index_row']['catalog_image_url'] if is_yale else item['view_url'],
            'asset':'assets/'+filename,'metadata':item['metadata'], 'decoded':item['decoded']})
    model={'viewer_id':settings['viewer_id'],'parent_pr':settings['parent_pr'],
           'parent_commit':settings['parent_commit'],'input_sha256':settings['input_sha256'],
           'original_parent_commit':settings['original_parent_commit'],
           'dependency_status':settings['current_dependency_status'],
           'images':images,'credit':record['release']['credit'],
           'manuscript_citation':record['release']['manuscript_citation'],
           'limits':'Dependent supplementary views of two surfaces. Glyph readings and legacy numbering remain unresolved.'}
    payload=encoded(model).decode().replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    require(template.count(b'__MODEL__')==1,'template must contain one model slot')
    files['index.html']=template.decode().replace('__MODEL__',payload).encode()
    manifest={'schema_version':1,'viewer_id':settings['viewer_id'],
        'parent_commit':settings['parent_commit'],'input_sha256':settings['input_sha256'],
        'settings_sha256':sha((root/SETTINGS).read_bytes()),'template_sha256':sha(template),
        'script_sha256':sha(script),'generator_sha256':sha(Path(__file__).read_bytes()),
        'files':{name:sha(raw) for name,raw in sorted(files.items())}}
    files['packet.json']=encoded(manifest)
    return files


def protect_output(output, cache, root=ROOT):
    resolved=output.resolve();original=cache.resolve();checkout=root.resolve()
    require(not resolved.is_relative_to(checkout) and not checkout.is_relative_to(resolved),
            'image packet must be outside the checkout and its ancestors')
    require(not resolved.is_relative_to(original) and not original.is_relative_to(resolved),
            'image packet must be separate from the source cache')
    require(not output.is_symlink() and (not output.exists() or
            (output.is_dir() and not any(output.iterdir()))),'output must be a fresh empty directory')


def write_packet(output,cache,root=ROOT):
    protect_output(output,cache,root)
    files=packet_bytes(cache,root)
    protect_output(output,cache,root)  # All content/manifest serialization is complete.
    output.mkdir(parents=True,exist_ok=True);(output/'assets').mkdir()
    for name,raw in files.items():
        require(not output.is_symlink() and not (output/'assets').is_symlink(), 'packet directory became a link')
        with (output/name).open('xb') as stream:stream.write(raw)


def check_packet(output,cache,root=ROOT):
    expected=packet_bytes(cache,root)
    require(not output.is_symlink() and not (output/'assets').is_symlink(), 'linked packet directory')
    require({p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}==set(expected),
            'missing or unexpected packet files')
    for name,raw in expected.items():
        path=output/name
        require(not path.is_symlink() and path.stat().st_nlink==1 and path.read_bytes()==raw,
                'changed or linked packet file: '+name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=Path,required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output',type=Path);mode.add_argument('--check',type=Path)
    args=parser.parse_args()
    try:
        if args.output:write_packet(args.output,args.cache)
        else:check_packet(args.check,args.cache)
    except (ValueError,OSError,KeyError,subprocess.CalledProcessError) as error:
        parser.exit(1,f'MSI viewer failed: {error}\n')
    print('Verified local packet: eight original image files; no glyph adjudication or registration.')


if __name__=='__main__':main()
