"""Inspect fixed paper-associated local artifacts without executing author code."""

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'research/literature/reddy-source-manifest.json'
PLAN = 'research/literature/REDDY_SOURCE_PLAN.md'
REPORT = 'research/literature/reddy-source-intake.json'
COMMIT = '643b881b2937bae8193814d8ff5d6e99a48bf7c5'
TREE = '4e529b53db765deb6c243a38731c947e7ab25e92'
SELECTED = {
    'README.md': '46bf6c6e1c1c576c57dbbb93e86d99a9a7bfcb6c21a67fbab06794363afba6a0',
    'basic_stats.py': '12102b9c290838ebe0c60580f62cb449759cb71d13949dbcf5c23c82d1aa4ccc',
    'data/voy.ann.wds': 'a3a1fb64a8f227e0fb0b81e7fe6aecec719888a4efeb5c1f7df5e2539c91d1d4',
    'data/voy.b.ann.wds': '7f6ee35b7ae7a0663f4b67d7b60effe9d539d8c2adb3d24de1153c3fbb4ae24b',
    'data/voy.b.paged.wds': '723cb2746da37c8272005f71298917abfed60412b23597b2b8aecb95dc7a0ee4',
    'data/voy.paged.wds': '92cd656360e2c0b728ce7338c59149e1f3d17263881fc9c4dc9514131f764a04',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def token_hash(tokens):
    return digest((json.dumps(tokens, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8'))


def population(tokens):
    characters = Counter(character for token in tokens for character in token)
    return {'token_occurrences': len(tokens), 'token_types': len(set(tokens)),
            'notation_characters': sum(characters.values()), 'notation_character_types': len(characters),
            'character_counts': [{'codepoint': f'U+{ord(c):04X}', 'count': n} for c, n in sorted(characters.items())],
            'token_stream_sha256': token_hash(tokens)}


def annotated(raw):
    rows, pages, seen, closed = [], [], set(), set()
    blank = 0
    for ordinal, line in enumerate(raw.decode('utf-8').splitlines(), 1):
        if not line.strip():
            blank += 1
            continue
        match = re.fullmatch(r'<([^<>]+)>\s+([^<>]+)', line)
        fields = match.group(1).split() if match else []
        if len(fields) != 4 or not match.group(2).split():
            raise ValueError(f'malformed annotated record at native file line {ordinal}')
        header = tuple(fields)
        if header in seen:
            raise ValueError(f'duplicate native header at file line {ordinal}')
        seen.add(header)
        page = fields[0]
        if not pages or pages[-1]['page'] != page:
            if page in closed:
                raise ValueError(f'noncontiguous native page at file line {ordinal}')
            if pages:
                closed.add(pages[-1]['page'])
            pages.append({'page': page, 'tokens': [], 'record_headers': []})
        tokens = match.group(2).split()
        rows.append({'header': header, 'native_file_line': ordinal, 'tokens': tokens})
        pages[-1]['tokens'].extend(tokens)
        pages[-1]['record_headers'].append(header)
    if not rows:
        raise ValueError('annotated input has no records')
    return rows, pages, blank


def compare_pages(pages, raw):
    lines = [line.split() for line in raw.decode('utf-8').splitlines()]
    comparisons = []
    for index in range(max(len(pages), len(lines))):
        left = pages[index] if index < len(pages) else None
        right = lines[index] if index < len(lines) else None
        comparisons.append({
            'paged_file_line_1based': index + 1, 'native_page': left['page'] if left else None,
            'annotated_tokens': len(left['tokens']) if left else None,
            'paged_tokens': len(right) if right is not None else None,
            'annotated_stream_sha256': token_hash(left['tokens']) if left else None,
            'paged_stream_sha256': token_hash(right) if right is not None else None,
            'exact_token_vector_match': left is not None and right is not None and left['tokens'] == right,
            'native_record_count': len(left['record_headers']) if left else None,
        })
    return {'paged_file_lines': len(lines), 'paged_blank_lines': sum(not line for line in lines),
            'annotated_pages': len(pages), 'all_pages_match': all(r['exact_token_vector_match'] for r in comparisons),
            'page_comparisons': comparisons}


def subset_check(full_rows, full_pages, b_rows, b_pages):
    by_header = {r['header']: (i, r['tokens']) for i, r in enumerate(full_rows)}
    positions, missing, unequal = [], [], []
    for row in b_rows:
        match = by_header.get(row['header'])
        if match is None:
            missing.append(list(row['header']))
        else:
            positions.append(match[0])
            if match[1] != row['tokens']:
                unequal.append(list(row['header']))
    full = {p['page']: p['tokens'] for p in full_pages}
    checks = [{'native_page': p['page'], 'in_full': p['page'] in full,
               'exact_token_vector_match': full.get(p['page']) == p['tokens']} for p in b_pages]
    return {'b_records': len(b_rows), 'records_missing_from_full': missing,
            'records_with_unequal_tokens': unequal,
            'record_order_preserved': positions == sorted(positions),
            'page_checks': checks,
            'all_records_and_pages_match': not missing and not unequal and
                positions == sorted(positions) and all(c['exact_token_vector_match'] for c in checks)}


def read_selected(reference, manifest):
    if manifest.get('source_commit') != COMMIT or manifest.get('source_tree') != TREE:
        raise ValueError('source snapshot differs')
    entries = manifest['selected_local_files']
    if {r['path']: r['sha256'] for r in entries} != SELECTED or len(entries) != len(SELECTED):
        raise ValueError('selected source pins differ')
    result = {}
    for row in entries:
        raw = (reference / row['path']).read_bytes()
        blob = hashlib.sha1((f'blob {len(raw)}\0').encode('ascii') + raw).hexdigest()
        if len(raw) != row['bytes'] or digest(raw) != row['sha256'] or blob != row['git_blob_sha1']:
            raise ValueError(f'source file identity differs: {row["path"]}')
        result[row['path']] = raw
    return result


def make_report(reference):
    manifest_raw = (ROOT / MANIFEST).read_bytes()
    manifest = json.loads(manifest_raw)
    raw = read_selected(reference, manifest)
    parsed = {name: annotated(raw[name]) for name in ['data/voy.ann.wds', 'data/voy.b.ann.wds']}
    reports = []
    for kind, ann, paged in [('full', 'data/voy.ann.wds', 'data/voy.paged.wds'),
                             ('b', 'data/voy.b.ann.wds', 'data/voy.b.paged.wds')]:
        rows, pages, blank = parsed[ann]
        tokens = raw[paged].decode('utf-8').split()
        comparison = compare_pages(pages, raw[paged])
        observed = {'pages': comparison['paged_file_lines'], 'tokens': len(tokens), 'types': len(set(tokens)),
                    'characters': len(set(''.join(tokens)))}
        reported = manifest['paper_reported_counts'][kind]
        reports.append({'case': kind, 'annotated_file': ann, 'paged_file': paged,
                        'annotated_native_records': len(rows), 'annotated_blank_file_lines': blank,
                        'source_tag_counts': dict(sorted(Counter(r['header'][3] for r in rows).items())),
                        'placement_counts': dict(sorted(Counter(r['header'][1] for r in rows).items())),
                        'annotated_population': population([t for r in rows for t in r['tokens']]),
                        'paged_population': population(tokens), **comparison,
                        'paper_reported_counts': reported, 'observed_counts': observed,
                        'observed_minus_reported': {k: observed[k] - v for k, v in reported.items()}})
    tree = ast.parse(raw['basic_stats.py'].decode('utf-8'))
    functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
    methods = {node.name: [child.name for child in node.body if isinstance(child, ast.FunctionDef)]
               for node in tree.body if isinstance(node, ast.ClassDef)}
    return {'schema_version': 1, 'method': 'fixed Reddy/Knight source intake v1',
            'source_commit': COMMIT, 'source_tree': TREE,
            'source_manifest_sha256': digest(manifest_raw),
            'plan_sha256': digest((ROOT / PLAN).read_bytes()), 'producer_sha256': digest(Path(__file__).read_bytes()),
            'cases': reports, 'b_full_membership': subset_check(*parsed['data/voy.ann.wds'][:2],
                                                               *parsed['data/voy.b.ann.wds'][:2]),
            'static_python_file': {'path': 'basic_stats.py', 'executed': False,
                                   'top_level_functions': functions, 'class_methods': methods},
            'scope': 'source inventory and native token identities/counts only; no Table2 prediction, historical byte authentication, modern-notation equivalence or translation'}


def write_new(path, raw):
    with path.open('xb') as output:
        output.write(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    options = parser.add_mutually_exclusive_group()
    options.add_argument('--check', action='store_true')
    options.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        report = make_report(args.reference)
        raw = (json.dumps(report, indent=2) + '\n').encode('utf-8')
        if args.check:
            if (ROOT / REPORT).read_bytes() != raw:
                raise ValueError('committed intake report differs from complete regeneration')
        else:
            write_new(args.output or ROOT / REPORT, raw)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError) as error:
        parser.exit(1, f'Source intake failed: {error}\n')
    print('Reddy source intake checked.' if args.check else 'Reddy source intake created.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
