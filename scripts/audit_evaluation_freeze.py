#!/usr/bin/env python3
"""Bind declared decoding-evaluation artifacts to Git blobs and current bytes.

This checks declared artifacts and ancestry, not actual fitting/exposure history
or whether every dependency was declared. It never executes candidate rules.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

try:
    from .validate_evaluation_split import load_split_json, validate
except ImportError:
    from validate_evaluation_split import load_split_json, validate


ROLES = {'split', 'input', 'rules', 'preprocessing'}
ROOT = Path(__file__).resolve().parents[1]


def git(repo, *arguments):
    result = subprocess.run(['git', '--no-replace-objects', '-C', str(repo), '--literal-pathspecs', *arguments],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise ValueError(f'Git {arguments[0]} failed: {result.stderr.decode(errors="replace").strip()}')
    return result.stdout


def repository_root(repo):
    root = Path(git(repo, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    if root != Path(repo).resolve():
        raise ValueError('--repo must identify the repository root')
    graft_path = Path(git(repo, 'rev-parse', '--git-path', 'info/grafts').decode().strip())
    if not graft_path.is_absolute():
        graft_path = root / graft_path
    if os.environ.get('GIT_GRAFT_FILE') or (graft_path.exists() and graft_path.read_bytes().strip()):
        raise ValueError('legacy Git grafts must be absent for an audit of the recorded history')
    return root


def full_commit(repo, value):
    if not isinstance(value, str) or not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', value):
        raise ValueError('require a full lowercase Git commit object ID')
    resolved = git(repo, 'rev-parse', '--verify', f'{value}^{{commit}}').decode().strip()
    if resolved != value:
        raise ValueError('object ID is not the specified commit')
    return value


def relative_path(value):
    if (not isinstance(value, str) or not value or '\\' in value or '\x00' in value or
            any(part in {'', '.', '..', '.git'} for part in value.split('/'))):
        raise ValueError('artifact paths must be literal relative repository paths without dot components')
    return value


def committed_bytes(repo, commit, path):
    path = relative_path(path)
    entries = git(repo, 'ls-tree', '-z', commit, '--', path).split(b'\x00')
    entries = [entry for entry in entries if entry]
    if len(entries) != 1:
        raise ValueError(f'{path}: require one tracked regular file in commit {commit}')
    metadata, name = entries[0].split(b'\t', 1)
    mode, kind, object_id = metadata.decode().split(' ')
    if mode not in {'100644', '100755'} or kind != 'blob' or name != path.encode():
        raise ValueError(f'{path}: require a tracked regular file, not a symlink or directory')
    return git(repo, 'cat-file', 'blob', object_id)


def working_bytes(repo, path):
    path = relative_path(path)
    target = repo
    for component in path.split('/'):
        target = target / component
        if target.is_symlink():
            raise ValueError(f'{path}: working artifact path contains a symlink')
    if not target.is_file():
        raise ValueError(f'{path}: working artifact is missing or not a regular file')
    return target.read_bytes()


def artifact_records(receipt):
    if not isinstance(receipt, dict) or set(receipt) != {'schema_version', 'candidate_version', 'freeze_commit', 'artifacts'}:
        raise ValueError('receipt requires exactly schema_version, candidate_version, freeze_commit and artifacts')
    if type(receipt['schema_version']) is not int or receipt['schema_version'] != 1:
        raise ValueError('unsupported receipt schema_version')
    version = receipt['candidate_version']
    if not isinstance(version, str) or not version.strip() or version != version.strip():
        raise ValueError('candidate_version must be a nonempty identifier without surrounding whitespace')
    artifacts = receipt['artifacts']
    if not isinstance(artifacts, dict) or set(artifacts) != ROLES:
        raise ValueError('declare split, input, rules and preprocessing artifacts')
    records = []
    for role in ['split', 'input', 'rules', 'preprocessing']:
        entries = artifacts[role] if role in {'rules', 'preprocessing'} else [artifacts[role]]
        if not isinstance(entries, list) or not entries:
            raise ValueError(f'{role}: require a nonempty artifact list')
        paths = set()
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {'path', 'sha256'}:
                raise ValueError(f'{role}: artifact requires exactly path and sha256')
            path = relative_path(entry['path'])
            digest = entry['sha256']
            if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
                raise ValueError(f'{role}: require a lowercase SHA-256 digest')
            if path in paths:
                raise ValueError(f'{role}: duplicate artifact path')
            paths.add(path)
            records.append((role, entry))
    return records


def audit(receipt, repo, run_commit=None):
    records = artifact_records(receipt)
    repo = repository_root(repo)
    freeze = full_commit(repo, receipt['freeze_commit'])
    if run_commit is not None:
        run_commit = full_commit(repo, run_commit)
        if run_commit == freeze:
            raise ValueError('run commit must be a strict descendant of the freeze commit')
        try:
            git(repo, 'merge-base', '--is-ancestor', freeze, run_commit)
        except ValueError as error:
            raise ValueError('run commit is not a descendant of the freeze commit') from error
    payloads = {}
    for role, entry in records:
        path, digest = entry['path'], entry['sha256']
        frozen_bytes = committed_bytes(repo, freeze, path)
        if hashlib.sha256(frozen_bytes).hexdigest() != digest:
            raise ValueError(f'{path}: declared hash differs from freeze-commit bytes')
        if working_bytes(repo, path) != frozen_bytes:
            raise ValueError(f'{path}: working bytes differ from the freeze commit')
        if run_commit is not None and committed_bytes(repo, run_commit, path) != frozen_bytes:
            raise ValueError(f'{path}: run-commit bytes differ from the freeze commit')
        if role in {'split', 'input'}:
            payloads[role] = frozen_bytes
    split = load_split_json(payloads['split'].decode('utf-8'))
    validation = validate(split, payloads['input'], require_frozen=True)
    if validation['errors']:
        raise ValueError('frozen split fails validation: ' + '; '.join(validation['errors']))
    if split['candidate_version'] != receipt['candidate_version']:
        raise ValueError('receipt candidate_version differs from the frozen split')
    if split['fit_started_at'] is not None:
        raise ValueError('freeze-commit split must declare fitting not yet started (fit_started_at null)')
    return {'freeze_commit': freeze, 'run_commit': run_commit,
            'candidate_version': receipt['candidate_version'], 'artifact_count': len(records),
            'split_validation': validation,
            'limitations': ['Git ancestry and declared timestamps do not prove fitting or exposure history.',
                            'Only listed artifacts are checked; omitted dependencies and rule completeness need review.',
                            'Byte identity does not validate a decipherment or translation.']}


def record(repo, commit, split_path, input_path, rule_paths, preprocessing_paths):
    repo = repository_root(repo)
    commit = full_commit(repo, commit)

    def entry(path):
        return {'path': relative_path(path),
                'sha256': hashlib.sha256(committed_bytes(repo, commit, path)).hexdigest()}

    split = load_split_json(committed_bytes(repo, commit, split_path).decode('utf-8'))
    if not isinstance(split, dict):
        raise ValueError('split must be a JSON object')
    receipt = {'schema_version': 1, 'candidate_version': split.get('candidate_version'),
               'freeze_commit': commit,
               'artifacts': {'split': entry(split_path), 'input': entry(input_path),
                             'rules': [entry(path) for path in rule_paths],
                             'preprocessing': [entry(path) for path in preprocessing_paths]}}
    audit(receipt, repo)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('record', help='record hashes from committed artifacts, checking current bytes')
    create.add_argument('--commit', required=True, help='full freeze commit object ID')
    create.add_argument('--split', required=True)
    create.add_argument('--input', required=True)
    create.add_argument('--rules', nargs='+', required=True)
    create.add_argument('--preprocessing', nargs='+', required=True)
    create.add_argument('--output', type=Path, required=True)
    check = commands.add_parser('check', help='check a recorded receipt against Git and current artifacts')
    check.add_argument('receipt', type=Path)
    check.add_argument('--run-commit', help='also check a later commit and its ancestry')
    args = parser.parse_args()
    try:
        if args.command == 'record':
            receipt = record(args.repo, args.commit, args.split, args.input, args.rules, args.preprocessing)
            target = args.output.resolve()
            artifact_paths = {(args.repo / entry['path']).resolve() for _, entry in artifact_records(receipt)}
            if target in artifact_paths:
                raise ValueError('receipt output must not overwrite a pinned artifact')
            if args.output.exists() or args.output.is_symlink():
                raise ValueError('receipt output already exists; choose a new receipt version')
            with args.output.open('x', encoding='utf-8') as output:
                output.write(json.dumps(receipt, indent=2) + '\n')
            print(f'Recorded {receipt["candidate_version"]} at {receipt["freeze_commit"]}.')
        else:
            receipt = load_split_json(args.receipt.read_text(encoding='utf-8'))
            print(json.dumps(audit(receipt, args.repo, args.run_commit), indent=2))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Freeze audit failed: {error}\n')


if __name__ == '__main__':
    main()
