"""Build a local source/image packet for the three accepted immediate-repeat cases."""

import argparse
import hashlib
from html import escape
from pathlib import Path
import re
import subprocess

try:
    from . import select_immediate_repeat_images as selector
    from .verify_immediate_repeat_images import verify
except ImportError:
    import select_immediate_repeat_images as selector
    from verify_immediate_repeat_images import verify


ROOT = Path(__file__).resolve().parents[1]
BASE = 'research/transliteration/repeat-viewer'
SETTINGS = BASE + '/inputs.json'
TEMPLATE = BASE + '/template.html'
INPUTS = ('research/transliteration/immediate_repeat_image_selection.json',
          'research/transliteration/immediate_repeat_image_review.json',
          'research/transliteration/IMMEDIATE_REPEAT_IMAGE_PLAN.md', 'data/transliterations.json')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_inputs():
    settings = selector.load_split_json((ROOT / SETTINGS).read_text())
    require(type(settings['schema_version']) is int and settings['schema_version'] == 1 and
            settings['viewer_id'] == 'immediate-repeat-review-v1' and
            set(settings['input_sha256']) == set(INPUTS), 'unexpected viewer input declaration')
    commit = settings['accepted_input_commit']
    require(isinstance(commit, str) and re.fullmatch('[0-9a-f]{40}', commit), 'require an exact accepted commit')
    raw = {}
    for path in INPUTS:
        current = (ROOT / path).read_bytes()
        require(sha(current) == settings['input_sha256'][path], 'viewer input fingerprint changed: ' + path)
        saved = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT)
        require(saved == current, 'accepted input blob changed: ' + path)
        raw[path] = current
    selection = selector.load_split_json(raw[INPUTS[0]].decode())
    review = selector.load_split_json(raw[INPUTS[1]].decode())
    catalog = selector.load_split_json(raw[INPUTS[3]].decode())
    require(review['selection_sha256'] == sha(raw[INPUTS[0]]), 'review selection fingerprint differs')
    require(selector.encoded(selection) == selector.encoded(selector.report()), 'complete source selection replay differs')
    verify(review, selection)
    return settings, selection, review, catalog


def native_html(record, role, source, commit):
    if record is None:
        return '<p>No ' + escape(role) + ' native record on this page.</p>'
    url = ('https://github.com/tobrien6/voynich-manuscript-research/blob/' + commit + '/' + source['path']
           + '#L' + str(record['source_file_line']))
    return ('<p class="source-line">' + escape(record['locus_identifier']) + ' · '
            + '<a href="' + escape(url, quote=True) + '" target="_blank" rel="noopener">source-file line '
            + str(record['source_file_line']) + '</a></p><pre data-source="' + escape(source['id'], quote=True)
            + '" data-context="' + role + '">' + escape(record['native_text']) + '</pre>')


def treatment_html(variant):
    event_slots = {i for event in variant['events'] for i in event[:2]}
    items = []
    for i, value in enumerate(variant['slots']):
        repeated = i in event_slots
        label = 'Slot ' + str(i) + (': excluded' if value is None else ': ' + value)
        if repeated:
            label += '; participates in an encoded equal-adjacent event'
        items.append('<li class="slot' + (' repeated' if repeated else '') + '" data-slot="' + str(i)
                     + '" aria-label="' + escape(label, quote=True) + '"><span class="slot-number">'
                     + str(i) + '</span><code>' + (escape(value) if value is not None else 'excluded') + '</code></li>')
    events = '; '.join(escape(event[2]) + ' at slots ' + str(event[0]) + '–' + str(event[1]) for event in variant['events'])
    policy = variant['uncertain_spaces'] + '/' + variant['alternatives']
    return ('<div class="treatment" data-policy="' + escape(policy, quote=True) + '" data-source="' + escape(variant['source_id'], quote=True)
            + '"><h4>' + escape(policy.replace('/', ' / ')) + '</h4><p class="event-count">'
            + str(len(variant['events'])) + ' encoded equal-adjacent event' + ('s' if len(variant['events']) != 1 else '')
            + (': ' + events if events else '') + '.</p><ol class="slots">' + ''.join(items) + '</ol></div>')


def list_html(items):
    return '<ul>' + ''.join('<li>' + escape(item) + '</li>' for item in items) + '</ul>'


def image_html(key, item):
    labels = {'overview': 'Whole-page overview', 'block': 'Source-row context',
              'detail': 'Recorded detail', 'wide_detail': 'Wider recorded detail'}
    role = item['role']
    dom = key.replace('.', '-') + '-' + role
    region = item.get('native_region')
    location = 'Native review rectangle: ' + str(region) if region else 'Whole page, fitted to 1,800 pixels'
    return ('<figure data-window="' + role + '"><div class="image-window"><img loading="lazy" '
            + 'src="assets/' + escape(item['file_name'], quote=True) + '" width="' + str(item['width'])
            + '" height="' + str(item['height']) + '" data-width="' + str(item['width'])
            + '" data-height="' + str(item['height']) + '" data-hash="' + item['sha256']
            + '" alt="' + escape(key + ' · ' + labels[role] + '; provisional source correspondence', quote=True) + '"></div>'
            + '<div class="zoom-controls" hidden><label for="zoom-' + dom + '">Zoom from fitted width</label>'
            + '<input id="zoom-' + dom + '" type="range" min="1" max="6" step="0.25" value="1"><output>1×</output></div>'
            + '<figcaption>' + escape(labels[role] + ' · ' + location) + ' · '
            + '<a href="' + escape(item['url'], quote=True) + '" target="_blank" rel="noopener">Original Yale image</a></figcaption>'
            + '<p class="image-status muted" aria-live="polite">Recorded dimensions: ' + str(item['width']) + ' × ' + str(item['height']) + '.</p>'
            + '<p class="hash-status muted" aria-live="polite">Build-time image SHA-256 checked.</p></figure>')


def render(settings, selection, review, catalog, template):
    sources = {s['id']: s for s in catalog['sources']}
    reviews = {c['locus_key']: c for c in review['cases']}
    labels = {'paired_agreement': 'Paired literal agreement', 'ZL_only': 'ZL-only encoded repeat', 'IT_only': 'IT-only encoded repeat'}
    sections, options = [], []
    for selected in selection['selected']:
        key, group = selected['locus_key'], selected['group']
        case = reviews[key]
        dom = 'case-' + key.replace('.', '-')
        title = key + ' · ' + labels[group]
        options.append('<option value="' + dom + '">' + escape(title) + '</option>')
        cards = []
        for record in selected['native_source_records']:
            source = sources[record['source_id']]
            cards.append('<article class="source"><h3>' + escape(source['id']) + ' <span class="muted">'
                         + escape(record['alphabet']) + '</span></h3>'
                         + native_html(record, 'selected', source, settings['accepted_input_commit'])
                         + '<div class="treatments">' + ''.join(treatment_html(v) for v in selected['variants']
                                                                   if v['source_id'] == source['id']) + '</div>'
                         + '<details><summary>Native neighbor context</summary><h4>Preceding record</h4>'
                         + native_html(record['preceding_native_record'], 'preceding', source, settings['accepted_input_commit'])
                         + '<h4>Following record</h4>'
                         + native_html(record['following_native_record'], 'following', source, settings['accepted_input_commit']) + '</details>'
                         + '<details><summary>Edition and credit</summary><p>' + escape(source['credit']) + '</p><p>'
                         + escape(source['header_version_statement']) + '</p><a href="' + escape(source['url'], quote=True)
                         + '" target="_blank" rel="noopener">Publisher source</a><p class="hash">Source SHA-256: '
                         + source['sha256'] + '</p></details></article>')
        files = [f for f in case['inspected_files'] if f['role'] != 'info']
        window_labels = {'block': 'Source-row context', 'overview': 'Whole-page overview',
                         'detail': 'Recorded detail', 'wide_detail': 'Wider recorded detail'}
        windows = ''.join(image_html(key, f) for f in files)
        choices = ''.join('<option value="' + f['role'] + '"' + (' selected' if f['role'] == 'block' else '')
                          + '>' + window_labels[f['role']] + '</option>' for f in files)
        notes = ('<h3>Direct image observation</h3><p>' + escape(case['direct_image_observation']) + '</p>'
                 + '<h3>Source-informed correspondence</h3><p>' + escape(case['source_informed_correspondence']) + '</p>'
                 + '<h3>Neighboring placements compared</h3>' + list_html(case['neighboring_placements_compared'])
                 + '<h3>Contradictions and limits</h3>' + list_html(case['contradictions_and_limits']))
        receipts = ''.join('<li><a href="' + escape(f['url'], quote=True) + '" target="_blank" rel="noopener">'
                           + escape(f['file_name']) + '</a> · ' + str(f['width']) + ' × ' + str(f['height'])
                           + '<div class="hash">SHA-256: ' + f['sha256'] + '</div></li>' for f in case['inspected_files'])
        sections.append('<section class="case" id="' + dom + '"><div class="case-head"><h2>' + escape(title)
                        + '</h2><span class="status">Provisional mapping</span></div><div class="sources">' + ''.join(cards) + '</div>'
                        + '<div class="window-toolbar" hidden><label for="window-' + dom + '">Image window</label>'
                        + '<select id="window-' + dom + '" class="window-select">' + choices + '</select></div><div class="windows">' + windows + '</div>'
                        + '<details class="observations"><summary>Original nonblind AI notes from PR #154</summary>'
                        + '<p>Source preference remains unresolved; these descriptions are not new viewer observations.</p>' + notes + '</details>'
                        + '<details><summary>All recorded file receipts</summary><ul>' + receipts + '</ul></details></section>')
    pins = '<p>Accepted input commit: <a href="https://github.com/tobrien6/voynich-manuscript-research/commit/'
    pins += settings['accepted_input_commit'] + '">' + settings['accepted_input_commit'] + '</a>.</p>'
    pins += ''.join('<p class="hash">' + escape(path) + ': ' + digest + '</p>' for path, digest in settings['input_sha256'].items())
    for marker, value in {'__CASE_OPTIONS__': ''.join(options), '__CASE_SECTIONS__': ''.join(sections), '__INPUT_PINS__': pins}.items():
        require(template.count(marker) == 1, 'missing or duplicate template marker')
        template = template.replace(marker, value)
    return template


def packet_bytes(image_directory):
    settings, selection, review, catalog = load_inputs()
    verify(review, selection, image_directory)
    template_raw = (ROOT / TEMPLATE).read_bytes()
    page = render(settings, selection, review, catalog, template_raw.decode()).encode()
    files = {'index.html': page}
    for case in review['cases']:
        for receipt in case['inspected_files']:
            name = receipt['file_name']
            require(Path(name).name == name, 'asset name must be a basename')
            raw = (image_directory / name).read_bytes()
            require(sha(raw) == receipt['sha256'], 'asset changed during generation')
            require('assets/' + name not in files, 'duplicate asset name')
            files['assets/' + name] = raw
    manifest = {'schema_version': 1, 'viewer_id': settings['viewer_id'],
                'accepted_input_commit': settings['accepted_input_commit'], 'input_sha256': settings['input_sha256'],
                'generator_sha256': sha(Path(__file__).read_bytes()), 'template_sha256': sha(template_raw),
                'settings_sha256': sha((ROOT / SETTINGS).read_bytes()),
                'files': {name: sha(raw) for name, raw in sorted(files.items())},
                'mappings_and_glyph_readings_verified': False}
    files['packet.json'] = selector.encoded(manifest)
    return files


def protect_output(output, image_directory):
    resolved, images = output.resolve(), image_directory.resolve()
    require(not resolved.is_relative_to(ROOT.resolve()) and not ROOT.resolve().is_relative_to(resolved),
            'pixel packet must be outside checkout and its ancestors')
    require(not resolved.is_relative_to(images) and not images.is_relative_to(resolved),
            'output must be separate from image inputs')
    require(not output.is_symlink() and (not output.exists() or (output.is_dir() and not any(output.iterdir()))),
            'output must be a fresh empty directory without symbolic links')


def write_packet(output, image_directory):
    protect_output(output, image_directory)
    files = packet_bytes(image_directory)
    protect_output(output, image_directory)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'assets').mkdir()
    for name, raw in files.items():
        with (output / name).open('xb') as stream:
            stream.write(raw)


def check_packet(output, image_directory):
    expected = packet_bytes(image_directory)
    require(not output.is_symlink() and not (output / 'assets').is_symlink(), 'linked packet directory')
    actual = {p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
    require(actual == set(expected), 'missing or unexpected packet files')
    for name, raw in expected.items():
        path = output / name
        require(not path.is_symlink() and path.stat().st_nlink == 1 and path.read_bytes() == raw,
                'packet bytes differ or file is linked: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image-directory', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            write_packet(args.output, args.image_directory)
            print('Built local repeat review packet; keep pixel assets outside the repository.')
        else:
            check_packet(args.check, args.image_directory)
            print('Frozen inputs, all local assets and complete viewer packet reproduce.')
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'repeat viewer failed: {error}\n')


if __name__ == '__main__':
    main()
