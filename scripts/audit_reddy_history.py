"""Audit a bounded local capture of the author's advertised Git history."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'research/literature/reddy-history-intake.json'
REPOSITORY = 'sravanareddy/deciphervoynich'
HISTORY = [
    ('643b881b2937bae8193814d8ff5d6e99a48bf7c5', '4e529b53db765deb6c243a38731c947e7ab25e92'),
    ('03ed8aa41458c9968767a75576e4df9454345056', 'a1638a0b796eefba08152ef76e56cb30eb3eb384'),
    ('7e446ccf210f161368144ad9329b19fcccb1a55c', 'b5e5f96dd96c901f9d255c0249dd46786966c84e'),
    ('e1626855937071d0c69c86ba8677b8359621dfef', '542e2ee767f7386710118e541d4332c4bd43d70b'),
    ('45cc018f464aaba643546cc57218f0a2f2420587', 'a98b324c756dd92d44b4519955e7f65029f45673'),
    ('d483622bad14040b9f8ebc68463dfb8c0274a1ea', '70c87c02194f1341fe1334b2af1bf1b1072ec82a'),
]
PROGRAMS = {
    'd78b72f164ca76258fef7eb29001ffad2ec071dd': (2466, '12102b9c290838ebe0c60580f62cb449759cb71d13949dbcf5c23c82d1aa4ccc'),
    '0d68aa25c6b155b9f6ac5c43acbd07d04b196036': (668, 'a18f815627e25ef45c8195d1b99d10bec9b1190fc66bfeeb69bc6b12a2ddb151'),
}
PROGRAM_SUFFIXES = {'.py', '.ipynb', '.r', '.m', '.java', '.c', '.cpp', '.sh', '.pl', '.rb', '.jl'}
NATIVE_FILES = ['data/voy.ann.wds', 'data/voy.b.ann.wds', 'data/voy.b.paged.wds', 'data/voy.paged.wds']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_object(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON object key')
        result[key] = value
    return result


def load(raw):
    def invalid(value):
        raise ValueError('non-finite JSON number')
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=invalid)


def flatten_pages(value):
    if not isinstance(value, list) or any(not isinstance(page, list) for page in value):
        raise ValueError('expected paginated API capture with --slurp')
    return [item for page in value for item in page]


def verify_tree(tree):
    if tree.get('truncated') is not False:
        raise ValueError('recursive tree is incomplete')
    entries = tree['tree']
    by_path = {}
    for entry in entries:
        path = entry['path']
        if not isinstance(path, str) or any(part in {'', '.', '..'} for part in path.split('/')) or '\\' in path or '\0' in path:
            raise ValueError('invalid literal tree path')
        if path in by_path or not re.fullmatch(r'[0-9a-f]{40}', entry['sha']):
            raise ValueError('duplicate path or invalid Git identity')
        if (entry['mode'], entry['type']) not in {('100644', 'blob'), ('040000', 'tree')}:
            raise ValueError('unexpected tree entry mode/type')
        if entry['type'] == 'blob' and (type(entry['size']) is not int or entry['size'] < 0):
            raise ValueError('invalid blob size metadata')
        by_path[path] = entry
    directories = {'': tree['sha']} | {path: entry['sha'] for path, entry in by_path.items() if entry['type'] == 'tree'}
    for path in by_path:
        if path.rpartition('/')[0] not in directories:
            raise ValueError('recursive tree lost a parent directory')
    for directory, expected in directories.items():
        children = [entry for path, entry in by_path.items() if path.rpartition('/')[0] == directory]
        def sort_key(entry):
            return entry['path'].rsplit('/', 1)[-1].encode('utf-8') + (b'/' if entry['type'] == 'tree' else b'')
        raw = b''.join(entry['mode'].lstrip('0').encode() + b' ' + entry['path'].rsplit('/', 1)[-1].encode('utf-8')
                       + b'\0' + bytes.fromhex(entry['sha']) for entry in sorted(children, key=sort_key))
        if git_object('tree', raw) != expected:
            raise ValueError('recursive entries do not reconstruct their Git tree')
    return sorted((entry for entry in entries if entry['type'] == 'blob'), key=lambda entry: entry['path'])


def source_inventory(raw):
    parsed = ast.parse(raw.decode('utf-8'))
    definitions = []
    def visit(body, prefix=''):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                definitions.append({'name': prefix + node.name, 'line': node.lineno,
                                    'arguments': [arg.arg for arg in node.args.args]})
            elif isinstance(node, ast.ClassDef):
                visit(node.body, prefix + node.name + '.')
    visit(parsed.body)
    imports = []
    for node in ast.walk(parsed):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.extend(str(node.module) + '.' + alias.name for alias in node.names)
    return {'definitions': definitions, 'imports': sorted(imports),
            'literal_native_paths': sorted({node.value for node in ast.walk(parsed)
                                           if isinstance(node, ast.Constant) and isinstance(node.value, str)
                                           and node.value.startswith('data/voy.') and node.value.endswith('.wds')})}


def audit(reference):
    captures = []
    def read(name):
        raw = (reference / name).read_bytes()
        captures.append({'local_capture_name': name, 'bytes': len(raw), 'sha256': sha(raw)})
        return load(raw)
    commits = flatten_pages(read('commits.json'))
    branches = flatten_pages(read('branches.json'))
    tags = flatten_pages(read('tags.json'))
    if [entry['sha'] for entry in commits] != [identity for identity, _ in HISTORY]:
        raise ValueError('commit capture differs from the fixed six-commit chain')
    branch_records = [{'name': branch['name'], 'commit': branch['commit']['sha']} for branch in branches]
    if branch_records != [{'name': 'master', 'commit': HISTORY[0][0]}] or tags:
        raise ValueError('advertised branch/tag capture differs from the inspected snapshot')
    records, programs = [], {}
    for index, ((identity, tree_id), commit) in enumerate(zip(HISTORY, commits)):
        parents = [entry['sha'] for entry in commit['parents']]
        if parents != ([HISTORY[index + 1][0]] if index + 1 < len(HISTORY) else []):
            raise ValueError('commit capture is not the complete fixed parent chain to root')
        if commit['commit']['tree']['sha'] != tree_id:
            raise ValueError('commit tree identity differs from its pin')
        tree = read(identity + '.tree.json')
        if tree['sha'] != tree_id:
            raise ValueError('recursive tree identity differs from its pin')
        blobs = verify_tree(tree)
        named_programs = [entry for entry in blobs if Path(entry['path']).suffix.lower() in PROGRAM_SUFFIXES]
        for entry in named_programs:
            blob_id = entry['sha']
            if entry['path'] != 'basic_stats.py' or blob_id not in PROGRAMS:
                raise ValueError('uninspected named program in this history')
            if blob_id not in programs:
                raw = (reference / (blob_id + '.py')).read_bytes()
                size, fingerprint = PROGRAMS[blob_id]
                if len(raw) != size or entry['size'] != size or sha(raw) != fingerprint or git_object('blob', raw) != blob_id:
                    raise ValueError('author source differs from pinned blob bytes')
                programs[blob_id] = {'git_blob_sha1': blob_id, 'bytes': size, 'sha256': fingerprint,
                                     **source_inventory(raw)}
        records.append({'commit': identity, 'parents': parents, 'tree_sha1': tree_id,
                        'author_date_from_api': commit['commit']['author']['date'],
                        'files': [{key: entry[key] for key in ['path', 'mode', 'sha', 'size']} for entry in blobs],
                        'named_program_paths': [entry['path'] for entry in named_programs]})
    if set(programs) != set(PROGRAMS):
        raise ValueError('history did not supply both source versions')
    native = []
    for path in NATIVE_FILES:
        occurrences = [{'commit': record['commit'], 'git_blob_sha1': entry['sha'], 'bytes': entry['size']}
                       for record in reversed(records) for entry in record['files'] if entry['path'] == path]
        native.append({'path': path, 'first_commit_in_chain': occurrences[0]['commit'],
                       'occurrences': occurrences, 'distinct_blob_identities': sorted({entry['git_blob_sha1'] for entry in occurrences})})
    return {'schema_version': 1, 'method': 'bounded advertised author-history inventory v1',
            'repository': REPOSITORY, 'head': HISTORY[0][0], 'inspected_local_date': '2026-10-12',
            'producer_sha256': sha(Path(__file__).read_bytes()),
            'advertised_branches': branch_records, 'advertised_tags': [],
            'commits_newest_first': records, 'program_versions': [programs[key] for key in sorted(programs)],
            'native_input_blob_history': native, 'api_capture_receipts': captures,
            'scope': 'six reachable commits from the advertised master head; two statically inspected Python blobs; no author execution or comparator payload retrieval; no deleted/unreachable refs, forks or other archives searched'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.output and (args.output.exists() or args.output.is_symlink()):
            raise ValueError('output exists; choose a new record')
        result = audit(args.reference)
        if args.check:
            if result != load(REPORT.read_bytes()):
                raise ValueError('report differs from the captured-source reconstruction')
            print('Author-history report matches all captured metadata and source bytes.')
        else:
            with args.output.open('x', encoding='utf-8') as output:
                output.write(json.dumps(result, indent=2) + '\n')
            print('Wrote bounded author-history report.')
    except (OSError, ValueError, KeyError, TypeError, SyntaxError) as error:
        parser.exit(1, f'History audit failed: {error}\n')


if __name__ == '__main__':
    main()
