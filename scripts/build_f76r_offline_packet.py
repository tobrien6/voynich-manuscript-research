"""Copy the five recorded f76r assets into a new local comparison packet."""

import argparse
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import stat
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DECLARATION = 'research/pilot/offline-packet/inputs.json'
INPUTS = ('research/pilot/viewer/f76r.html', 'research/pilot/viewer/inputs.json',
          'research/pilot/f76r-anchor-review.json', 'research/pilot/f76r-anchor-selection.json',
          'data/transliterations.json')
MAX_BYTES = 40 * 1024 * 1024
ASSET_NAMES = ('f76r-overview.jpg', 'f76r-first.jpg', 'f76r-median.jpg', 'f76r-last.jpg', 'f76r-info.json')
MEMBERS = {'index.html', 'packet.json', *('assets/' + name for name in ASSET_NAMES)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def serialize(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode('utf-8')


class PageRecord(HTMLParser):
    def __init__(self):
        super().__init__()
        self.native, self.images, self.links = {}, [], []
        self.current, self.pieces = None, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'pre':
            self.current = tuple(attrs[key] for key in ('data-anchor', 'data-source', 'data-context'))
            require(self.current not in self.native, 'duplicate native field')
            self.pieces = []
        elif tag == 'img':
            self.images.append(attrs)
        elif tag == 'a':
            self.links.append(attrs['href'])

    def handle_data(self, data):
        if self.current is not None:
            self.pieces.append(data)

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.native[self.current] = ''.join(self.pieces)
            self.current = None


def load_inputs():
    declared_raw = (ROOT / DECLARATION).read_bytes()
    declared = json.loads(declared_raw)
    require(declared['schema_version'] == 1 and declared['packet_id'] == 'f76r-accepted-offline-packet-v1'
            and set(declared['input_sha256']) == set(INPUTS), 'wrong packet declaration')
    commit = declared['accepted_viewer_commit']
    require(re.fullmatch('[0-9a-f]{40}', commit), 'require an exact accepted viewer commit')
    blobs = {}
    for path in INPUTS:
        raw = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT)
        require(sha(raw) == declared['input_sha256'][path], 'archived packet input changed: ' + path)
        blobs[path] = raw
    legacy, review, selection, catalog = (json.loads(blobs[path]) for path in INPUTS[1:])
    require(review['selection_sha256'] == sha(blobs[INPUTS[3]])
            and review['source_corrections_applied'] is False
            and review['glyph_adjudication'] == 'unresolved'
            and review['exposure']['untouched_evaluation'] is False, 'wrong accepted evidence boundary')
    for path in INPUTS[2:]:
        require(legacy['input_sha256'][path] == sha(blobs[path]), 'legacy input binding differs')
        old = subprocess.check_output(['git', 'show', legacy['accepted_input_commit'] + ':' + path], cwd=ROOT)
        require(old == blobs[path], 'original source commit differs')
    require([row['key'] for row in review['records']] == ['f76r.1', 'f76r.35', 'f76r.56']
            and [row['native_source_contexts'] for row in review['records']]
            == [row['sources'] for row in selection['selection']['anchors']], 'native anchor selection differs')
    parsed = PageRecord()
    parsed.feed(blobs[INPUTS[0]].decode('utf-8'))
    expected = {(row['key'], edition, role): locus['native_text']
                for row in review['records'] for edition, contexts in row['native_source_contexts'].items()
                for role, locus in contexts.items() if locus is not None}
    require(len(expected) == 14 and parsed.native == expected, 'legacy native fields differ')
    sources = {source['id']: source for source in catalog['sources']}
    links = {'https://github.com/tobrien6/voynich-manuscript-research/blob/' + legacy['accepted_input_commit']
             + '/' + sources[edition]['path'] + '#L' + str(locus['source_file_line'])
             for row in review['records'] for edition, contexts in row['native_source_contexts'].items()
             for locus in contexts.values() if locus is not None}
    require(links <= set(parsed.links), 'legacy source-line links differ')
    images = {item['id']: item for item in review['inspection_files']}
    require([item['id'] for item in review['inspection_files']] == ['overview', 'first', 'median', 'last']
            and [image['src'] for image in parsed.images]
            == [images[row['inspection_file_id']]['url'] for row in review['records']], 'legacy image associations differ')
    return declared, declared_raw, blobs[INPUTS[0]].decode('utf-8'), review


def outside_git(path):
    require(not any((parent / '.git').exists() for parent in (path, *path.parents)),
            'cache and packet must remain outside Git checkouts')


def read_assets(review, directory):
    directory = Path(directory).resolve()
    require(directory.is_dir(), 'image cache must be an existing directory')
    outside_git(directory)
    resources = [*review['inspection_files'], review['service_metadata']]
    require([item['local_filename'] for item in resources] == list(ASSET_NAMES),
            'require all five recorded filenames')
    assets = {}
    for item in resources:
        name = item['local_filename']
        path = directory / name
        info = path.lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'cache member must be a regular singly linked file: ' + name)
        expected_size = item.get('bytes')
        limit = expected_size if expected_size is not None else MAX_BYTES
        require(info.st_size <= limit and (expected_size is None or info.st_size == expected_size),
                'recorded byte count differs: ' + name)
        with path.open('rb') as stream:
            raw = stream.read(limit + 1)
        require(len(raw) <= limit and (expected_size is None or len(raw) == expected_size)
                and sha(raw) == item['sha256'], 'recorded resource bytes differ: ' + name)
        assets['assets/' + name] = raw
    metadata = review['service_metadata']
    info = json.loads(assets['assets/' + metadata['local_filename']])
    require(info['@id'] == metadata['service_id']
            and [info['width'], info['height']] == [metadata['width'], metadata['height']],
            'cached image-service identity differs')
    return assets


def replace_once(page, old, new):
    require(page.count(old) == 1, 'legacy display conversion does not match exactly once')
    return page.replace(old, new)


def local_page(canonical, review, declared, declared_raw):
    page = canonical
    for image in review['inspection_files'][1:]:
        page = replace_once(page, 'src="' + escape(image['url'], quote=True) + '"',
                            'src="assets/' + image['local_filename'] + '" data-sha256="' + image['sha256'] + '"')
    page = replace_once(page,
                        'Inspection hashes describe recorded local files. This page loads official Yale images but does not verify their live byte hashes.',
                        'The packet builder verified all five cached resource hashes. This page loads local image copies and checks loaded dimensions; the browser does not recheck their byte hashes.')
    page = replace_once(page,
                        'Yale image could not load. Use the official region link; the native text remains available.',
                        'Local image could not load. Recheck the packet or use the official region link; the native text remains available.')
    note = ('<p class="intro">Offline packet: images come from the verified local cache. '
            '<a href="assets/f76r-overview.jpg">Recorded whole-page overview</a> · '
            '<a href="assets/f76r-info.json">Recorded service metadata</a>. '
            'Public evidence links require internet when opened; row associations remain provisional.</p>')
    page = replace_once(page, '  </header>', note + '\n  </header>')
    meta = ('<meta name="offline-packet-inputs-sha256" content="' + sha(declared_raw) + '">'
            '<meta name="offline-packet-builder-sha256" content="' + sha(Path(__file__).read_bytes()) + '">')
    page = replace_once(page, '</head>', meta + '\n</head>')
    note = ('<p>Local packet derived from accepted viewer '
            '<a href="https://github.com/tobrien6/voynich-manuscript-research/commit/' + declared['accepted_viewer_commit']
            + '">' + declared['accepted_viewer_commit'] + '</a>. '
            'Use the <a href="packet.json">packet manifest</a> for copied resource identities. '
            'No new observations or source corrections were added.</p>')
    page = replace_once(page, '  </footer>', note + '\n  </footer>')
    return page.encode('utf-8')


def packet_files(image_directory):
    declared, declared_raw, canonical, review = load_inputs()
    files = read_assets(review, image_directory)
    files['index.html'] = local_page(canonical, review, declared, declared_raw)
    record = {'schema_version': 1, 'packet_id': declared['packet_id'],
              'accepted_viewer_commit': declared['accepted_viewer_commit'],
              'input_sha256': declared['input_sha256'], 'declaration_sha256': sha(declared_raw),
              'builder_sha256': sha(Path(__file__).read_bytes()),
              'files': {name: {'sha256': sha(raw), 'bytes': len(raw)} for name, raw in sorted(files.items())},
              'limits': 'Local copies of accepted exposed material; no glyph adjudication, source corrections or new observations. Browser dimension checks do not authenticate bytes.'}
    files['packet.json'] = serialize(record)
    return files


def protect_output(output, image_directory):
    output = Path(output)
    require(not output.exists() and not output.is_symlink(), 'packet output must be a fresh unlinked directory')
    resolved, cache = output.resolve(), Path(image_directory).resolve()
    outside_git(resolved)
    require(resolved != cache and cache not in resolved.parents and resolved not in cache.parents,
            'cache and packet directories must be separate')
    return resolved


def build_packet(output, files, image_directory):
    require(set(files) == MEMBERS, 'require the exact seven named packet members')
    output = protect_output(output, image_directory)
    output.mkdir(mode=0o700)
    (output / 'assets').mkdir(mode=0o700)
    for name, raw in files.items():
        with (output / name).open('xb') as stream:
            stream.write(raw)


def check_packet(output, files):
    require(set(files) == MEMBERS, 'require the exact seven named packet members')
    output = Path(output)
    require(output.is_dir() and not output.is_symlink(), 'packet must be a real directory')
    outside_git(output.resolve())
    members = list(output.rglob('*'))
    require(not any(member.is_symlink() for member in members), 'packet contains symbolic aliases')
    require(all(stat.S_ISREG(member.lstat().st_mode) or stat.S_ISDIR(member.lstat().st_mode) for member in members),
            'packet contains non-regular members')
    actual = {member.relative_to(output).as_posix() for member in members if member.is_file()}
    require(actual == set(files), 'complete packet file inventory differs')
    require({member.relative_to(output).as_posix() for member in members if member.is_dir()} == {'assets'},
            'packet directory inventory differs')
    for name, raw in files.items():
        member = output / name
        require(member.stat().st_nlink == 1 and member.read_bytes() == raw, 'packet file bytes or aliases differ: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image-directory', type=Path, required=True)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument('--output', type=Path, help='fresh directory outside Git checkouts')
    destination.add_argument('--check', type=Path, help='verify a complete existing packet without writing')
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output, args.image_directory)
        files = packet_files(args.image_directory)
        if args.check:
            check_packet(args.check, files)
            print('All pinned inputs, five cached assets and the complete seven-file packet reproduce.')
        else:
            build_packet(args.output, files, args.image_directory)
            print('Built a local f76r packet; keep all image assets outside Git and publication.')
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
