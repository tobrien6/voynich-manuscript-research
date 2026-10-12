"""Package the complete pinned modern span inventory in a read-only local page."""

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse

try:
    from .audit_eva_token_coverage import encoded, load_json
    from .audit_transliterations import ROOT
    from .boundary_disagreement_spans import build as build_inventory
    from .paragraph_token_corpus import protect_outputs
except ImportError:
    from audit_eva_token_coverage import encoded, load_json
    from audit_transliterations import ROOT
    from boundary_disagreement_spans import build as build_inventory
    from paragraph_token_corpus import protect_outputs


BASE = Path('research/transliteration/span-viewer')
SETTINGS = BASE / 'inputs.json'
TEMPLATE = BASE / 'template.html'
INPUTS = (Path('research/transliteration/boundary_disagreement_spans.json'), Path('data/transliterations.json'))
REPO = 'https://github.com/tobrien6/voynich-manuscript-research'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_inputs(root=ROOT):
    settings_raw = (root / SETTINGS).read_bytes()
    settings = load_json(settings_raw)
    require(type(settings['schema_version']) is int and settings['schema_version'] == 1
            and settings['viewer_id'] == 'boundary-span-review-v1', 'unsupported viewer input contract')
    commit = settings['input_commit']
    require(isinstance(commit, str) and re.fullmatch('[0-9a-f]{40}', commit), 'require an exact input commit')
    require(set(settings['input_sha256']) == {str(path) for path in INPUTS}, 'viewer input set changed')
    values = []
    for path in INPUTS:
        raw = (root / path).read_bytes()
        require(sha(raw) == settings['input_sha256'][str(path)], 'viewer input bytes changed: ' + str(path))
        committed = subprocess.check_output(['git', 'show', commit + ':' + str(path)], cwd=root)
        require(committed == raw, 'input commit blob differs: ' + str(path))
        values.append(raw)
    inventory, catalog = map(load_json, values)
    require(encoded(inventory) == encoded(build_inventory(root=root)), 'span inventory differs from complete fresh producer')
    require(catalog['license'] == 'CC0-1.0', 'modern source reuse terms changed')
    sources = []
    for identifier in ('ZL3b', 'IT2a'):
        matches = [source for source in catalog['sources'] if source['id'] == identifier]
        require(len(matches) == 1, 'need exactly one declared modern source')
        source = matches[0]
        require(re.fullmatch(r'data/raw/[A-Za-z0-9.-]+\.txt', source['path']), 'unsafe or unexpected source path')
        url = urlparse(source['url'])
        require(url.scheme == 'https' and url.netloc == 'voynich.nu' and not url.username and not url.password,
                'unexpected publisher URL')
        current = (root / source['path']).read_bytes()
        require(sha(current) == source['sha256'], 'native source fingerprint changed')
        require(subprocess.check_output(['git', 'show', commit + ':' + source['path']], cwd=root) == current,
                'native source blob differs from linked input commit')
        sources.append({**{key: source[key] for key in ('id', 'alphabet', 'title', 'credit', 'header_version_statement', 'url', 'sha256')},
                        'blob_url': REPO + '/blob/' + commit + '/' + source['path']})
    rows, totals = [], {}
    for comparison in inventory['comparisons']:
        policy = comparison['spacing']
        require(policy in ('split', 'join') and policy not in totals, 'duplicate or unknown spacing policy')
        records = comparison['span_records']
        require(len(records) == comparison['span_count'], 'span denominator changed')
        totals[policy] = {'spans': len(records), 'loci': comparison['disagreement_loci']['native_locus_count']}
        rows.extend(dict(record, spacing=policy) for record in records)
    require(set(totals) == {'split', 'join'}, 'need both source-spacing comparisons')
    payload = {'viewer_id': settings['viewer_id'], 'input_commit': commit,
               'inventory_sha256': sha(values[0]), 'sources': sources, 'rows': rows,
               'policy_totals': totals, 'parent_selected_native_loci': inventory['parent_selection']['native_locus_count']}
    return settings_raw, settings, payload


def render(payload, template):
    # Encoded fields remain inert text even if a later reviewed metadata value
    # contains markup; the browser renders all source values through textContent.
    data = json.dumps(payload, ensure_ascii=True, separators=(',', ':'), allow_nan=False)
    data = data.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    report_url = REPO + '/blob/' + payload['input_commit'] + '/research/transliteration/BOUNDARY_DISAGREEMENT_SPANS.md'
    for marker in ('__DATA__', '__REPORT_URL__'):
        require(template.count(marker) == 1, 'missing or repeated template marker: ' + marker)
    template = template.replace('__REPORT_URL__', escape(report_url, quote=True))
    template = template.replace('__DATA__', data)
    return template.encode('utf-8')


def package(root=ROOT):
    settings_raw, settings, payload = load_inputs(root)
    template_raw = (root / TEMPLATE).read_bytes()
    page = render(payload, template_raw.decode('utf-8'))
    provenance = {'schema_version': 1, 'viewer_id': settings['viewer_id'],
                  'input_commit': settings['input_commit'], 'input_sha256': settings['input_sha256'],
                  'payload_sha256': sha(encoded(payload)), 'html_sha256': sha(page),
                  'settings_sha256': sha(settings_raw), 'template_sha256': sha(template_raw),
                  'producer_sha256': sha(Path(__file__).read_bytes()),
                  'policy_totals': payload['policy_totals'], 'embedded_span_records': len(payload['rows']),
                  'scope': settings['scope'], 'external_resources_loaded': False,
                  'verified_glyph_regions': False, 'source_corrections_applied': False}
    return {'index.html': page, 'provenance.json': encoded(provenance)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output-dir', type=Path)
    mode.add_argument('--check-dir', type=Path)
    args = parser.parse_args()
    try:
        directory = args.output_dir or args.check_dir
        targets = [directory / name for name in ('index.html', 'provenance.json')]
        reads = [ROOT / path for path in (*INPUTS, SETTINGS, TEMPLATE)]
        protect_outputs(targets if args.output_dir else [], reads, root=ROOT)
        files = package()
        if args.check_dir:
            for path in targets:
                require(path.read_bytes() == files[path.name], 'committed viewer export differs: ' + path.name)
        else:
            directory.mkdir(parents=True, exist_ok=True)
            for path in targets:
                protect_outputs(targets, reads, root=ROOT)
                path.write_bytes(files[path.name])
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'span viewer failed: {error}\n')
    print('Verified both policies, all source spans and both local viewer exports.')


if __name__ == '__main__':
    main()
