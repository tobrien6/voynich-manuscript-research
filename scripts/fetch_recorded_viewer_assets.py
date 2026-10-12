"""Retrieve fixed accepted viewer assets into a private, hash-checked local cache."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import uuid


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = Path('research/assets/recorded-viewer-sources.json')
STUDIES = ('f76r', 'y-lookup', 'immediate-repeat')
MAX_BYTES = 40_000_000


class ReceiptError(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise ReceiptError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def validate_url(url):
    parsed = urlsplit(url)
    require(parsed.scheme == 'https' and not parsed.username and not parsed.password
            and not parsed.query and not parsed.fragment and parsed.port in (None, 443),
            'resource URL is not an accepted public HTTPS address')
    allowed = (parsed.hostname == 'collections.library.yale.edu'
               and re.fullmatch(r'/iiif/2/[0-9]+/(?:info\.json|[^/]+/[^/]+/0/default\.jpg)', parsed.path))
    allowed = allowed or (parsed.hostname == 'voynich.nu' and parsed.path == '/img/extra/eva01.gif')
    require(allowed, 'resource URL is outside the recorded public image services')


class RecordedRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        validate_url(new_url)
        require(urlsplit(new_url).hostname == urlsplit(request.full_url).hostname,
                'resource redirect changes the recorded provider')
        return super().redirect_request(request, fp, code, message, headers, new_url)


def load_source(study):
    raw_registry = (ROOT / REGISTRY).read_bytes()
    registry = json.loads(raw_registry)
    require(type(registry['schema_version']) is int and registry['schema_version'] == 1,
            'unknown source registry')
    entries = [x for x in registry['sources'] if x['id'] == study]
    require(len(entries) == 1, 'study must have one accepted source')
    entry = entries[0]
    require(re.fullmatch('[0-9a-f]{40}', entry['accepted_commit']), 'source commit must be exact')
    raw = subprocess.check_output(['git', 'show', entry['accepted_commit'] + ':' + entry['record_path']], cwd=ROOT)
    require(sha(raw) == entry['record_sha256'], 'historical record fingerprint differs')
    record = json.loads(raw)
    if entry['layout'] == 'f76r':
        resources = record['inspection_files'] + [record['service_metadata']]
        names = 'local_filename'
    elif entry['layout'] == 'retrieved':
        resources = record['retrieved_resources']
        require(all(x['status'] == 'retrieved' for x in resources), 'resource is not recorded as retrieved')
        names = 'name'
    elif entry['layout'] == 'cases':
        resources = [x for case in record['cases'] for x in case['inspected_files']]
        names = 'file_name'
    else:
        raise ReceiptError('unsupported fixed record layout')
    result = []
    for item in resources:
        name = item[names]
        require(type(name) is str and Path(name).name == name and name not in ('.', '..')
                and re.fullmatch(r'[A-Za-z0-9._-]+\.(?:jpg|gif|json)', name), 'invalid recorded basename')
        require(type(item['sha256']) is str and re.fullmatch('[0-9a-f]{64}', item['sha256']),
                'invalid recorded digest')
        size = item.get('bytes')
        require(size is None or (type(size) is int and 0 < size <= MAX_BYTES), 'invalid recorded size')
        validate_url(item['url'])
        result.append({'name': name, 'url': item['url'], 'sha256': item['sha256'], 'bytes': size})
    require(len({r['name'] for r in result}) == len(result), 'duplicate resource basenames')
    expected = {'f76r': 5, 'y-lookup': 17, 'immediate-repeat': 13}
    require(len(result) == expected[study], 'fixed resource inventory differs')
    return {**entry, 'registry_sha256': sha(raw_registry)}, result


def protect_directory(directory):
    require(not directory.is_symlink() and (not directory.exists() or directory.is_dir()),
            'asset cache must be an unlinked directory')
    resolved = directory.resolve()
    for ancestor in (resolved, *resolved.parents):
        require(not (ancestor / '.git').exists(), 'asset cache must be outside Git checkouts')
    require(not ROOT.resolve().is_relative_to(resolved), 'asset cache cannot be a checkout ancestor')


def verify_bytes(raw, resource):
    require(len(raw) <= MAX_BYTES, 'resource exceeds bounded size')
    require(resource['bytes'] is None or len(raw) == resource['bytes'], 'resource byte count differs')
    require(sha(raw) == resource['sha256'], 'resource SHA-256 differs')


def existing_asset(path, resource):
    require(not path.is_symlink(), 'existing resource is a symbolic link')
    if not path.exists():
        return False
    require(path.is_file() and path.stat().st_nlink == 1, 'existing resource is not an unlinked file')
    require(path.stat().st_size <= MAX_BYTES, 'existing resource exceeds bounded size')
    verify_bytes(path.read_bytes(), resource)
    return True


def retrieve(resource, timeout, opener):
    request = Request(resource['url'], headers={
        'User-Agent': 'Mozilla/5.0 (compatible; VoynichReceipt/1.0; +https://github.com/tobrien6/voynich-manuscript-research)',
        'Accept': 'image/jpeg,image/gif,application/json;q=0.9,*/*;q=0.5'})
    with opener.open(request, timeout=timeout) as response:
        validate_url(response.geturl())
        require(urlsplit(response.geturl()).hostname == urlsplit(resource['url']).hostname,
                'response changes the recorded provider')
        require(response.status == 200, 'resource response is not successful')
        limit = resource['bytes'] if resource['bytes'] is not None else MAX_BYTES
        raw = response.read(limit + 1)
    verify_bytes(raw, resource)
    return raw


def store_new(directory, path, raw):
    """Install a fully written file under a new name without replacing any file."""
    protect_directory(directory)
    fd, temporary = tempfile.mkstemp(prefix='.recorded-resource-', dir=directory)
    temporary = Path(temporary)
    try:
        with os.fdopen(fd, 'wb') as stream:
            require(stream.write(raw) == len(raw), 'local file write was incomplete')
            stream.flush()
            os.fsync(stream.fileno())
        protect_directory(directory)
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def fetch_assets(study, directory, only=None, timeout=20, opener=None):
    require(type(timeout) is int and 1 <= timeout <= 30, 'timeout must be 1 to 30 seconds')
    source, resources = load_source(study)
    if only:
        require(set(only).issubset({x['name'] for x in resources}), 'requested name is not a recorded resource')
        resources = [x for x in resources if x['name'] in set(only)]
    protect_directory(directory)
    directory.mkdir(parents=True, exist_ok=True)
    opener = opener or build_opener(RecordedRedirects())
    results = []
    for resource in resources:
        item = {**resource}
        path = directory / resource['name']
        try:
            protect_directory(directory)
            if existing_asset(path, resource):
                item['status'] = 'reused_verified'
            else:
                raw = retrieve(resource, timeout, opener)
                protect_directory(directory)
                require(not existing_asset(path, resource), 'resource appeared during retrieval')
                store_new(directory, path, raw)
                item['status'] = 'downloaded_verified'
            item['stored_bytes'] = path.stat().st_size
        except HTTPError as error:
            item.update(status='failed', reason='HTTP response ' + str(error.code))
        except URLError:
            item.update(status='failed', reason='network or TLS retrieval failure')
        except (ReceiptError, OSError) as error:
            item.update(status='failed', reason=str(error) if isinstance(error, ReceiptError) else 'local file operation failed')
        results.append(item)
    report = {'schema_version': 1, 'study': study, 'source': source,
              'retrieved_at_utc_epoch': int(time.time()), 'resources': results,
              'complete_successful_selection': all(x['status'] != 'failed' for x in results),
              'entire_record_inventory_requested': len(resources) == {'f76r': 5, 'y-lookup': 17, 'immediate-repeat': 13}[study],
              'scope': 'Exact receipt bytes only; no pixel adjudication, source correction or image publication'}
    protect_directory(directory)
    report_path = directory / ('retrieval-receipt-' + uuid.uuid4().hex + '.json')
    store_new(directory, report_path, (json.dumps(report, indent=2, sort_keys=True) + '\n').encode())
    return report, report_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', choices=STUDIES, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--only', action='append', help='Retrieve only this exact recorded basename; repeat if needed')
    parser.add_argument('--timeout', type=int, default=20)
    args = parser.parse_args()
    try:
        report, path = fetch_assets(args.study, args.directory, args.only, args.timeout)
        for item in report['resources']:
            print(item['name'] + ': ' + item['status'] + (' (' + item['reason'] + ')' if 'reason' in item else ''))
        print('Local retrieval receipt: ' + str(path))
        if not report['complete_successful_selection']:
            parser.exit(1, 'Some assets were not retrieved or verified; existing files were preserved.\n')
    except (ReceiptError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, 'recorded retrieval failed: ' + (str(error) if isinstance(error, ReceiptError) else 'source or local operation failed') + '\n')


if __name__ == '__main__':
    main()
