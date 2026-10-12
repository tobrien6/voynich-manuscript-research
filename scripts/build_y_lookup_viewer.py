"""Build a fresh local packet for the two accepted lookup image pairs."""

import argparse
from html import escape
import hashlib
import json
from pathlib import Path
import re
import subprocess

try:
    from .verify_y_lookup_review import verify_record
except ImportError:
    from verify_y_lookup_review import verify_record


ROOT = Path(__file__).resolve().parents[1]
BASE = 'research/hypotheses/y-lookup-image-v1'
SETTINGS = BASE + '/viewer/inputs.json'
TEMPLATE = BASE + '/viewer/template.html'
INPUTS = (BASE + '/selection.json', BASE + '/image-review.json', 'data/transliterations.json', BASE + '/PLAN.md')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_inputs():
    settings = json.loads((ROOT / SETTINGS).read_bytes())
    require(settings['viewer_id'] == 'y-lookup-pair-review-v1' and settings['schema_version'] == 1
            and set(settings['input_sha256']) == set(INPUTS), 'wrong viewer input declaration')
    commit = settings['accepted_input_commit']
    require(re.fullmatch('[0-9a-f]{40}', commit), 'require an exact accepted commit')
    values = []
    for path in INPUTS:
        raw = (ROOT / path).read_bytes()
        require(sha(raw) == settings['input_sha256'][path], 'viewer input fingerprint changed: ' + path)
        old = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT)
        require(old == raw, 'accepted input blob changed: ' + path)
        values.append(raw)
    selection, review, catalog = [json.loads(raw) for raw in values[:3]]
    verify_record(review, selection, ROOT)
    return settings, selection, review, catalog


def native_html(contexts, catalog, commit):
    sources = {item['id']: item for item in catalog['sources']}
    cards = []
    for identifier in ('ZL3b', 'IT2a'):
        context, source = contexts[identifier], sources[identifier]
        selected, neighbors = [], []
        for role, label in (('preceding', 'Preceding native locus'), ('locus', 'Selected native locus'), ('following', 'Following native locus')):
            locus = context[role]
            if locus is None:
                neighbors.append('<p>No ' + escape(label.lower()) + ' on this page.</p>')
                continue
            url = f'https://github.com/tobrien6/voynich-manuscript-research/blob/{commit}/{source["path"]}#L{locus["file_line"]}'
            item = ('<h4>' + (identifier + ' · ' if role == 'locus' else '') + label + '</h4><p class="source-line">' + escape(locus['identifier'])
                         + ' · <a href="' + escape(url, quote=True) + '" target="_blank" rel="noopener">file line '
                         + escape(str(locus['file_line'])) + '</a></p><pre data-source="' + identifier + '" data-context="' + role + '">'
                         + escape(locus['text']) + '</pre>')
            (selected if role == 'locus' else neighbors).append(item)
        cards.append('<div class="native-source">' + ''.join(selected)
                     + '<details class="native"><summary>' + identifier + ' · neighbor context and source</summary>'
                     + ''.join(neighbors) + '<p>' + escape(source['credit']) + '</p><p>Alphabet: ' + escape(source['alphabet'])
                     + '. Original encoded slot: ' + escape(str(context['original_slot_zero_based']))
                     + ' (zero-based; physical boundary unresolved).</p></details></div>')
    return ''.join(cards)


def image_html(page, kind, resource):
    w, h = resource['pixel_dimensions']
    label = {'whole': 'Whole-page overview', 'context': 'Row-context window', 'token': 'Group window'}[kind]
    box = resource.get('native_region_xywh')
    identity = ('Native region: ' + ', '.join(map(str, box)) if box else 'Full page fitted to 1,600 pixels')
    dom_id = page + '-' + kind
    return ('<details class="window" open><summary>' + label + '</summary><figure><div class="image-window">'
            + f'<img src="assets/{escape(resource["name"], quote=True)}" width="{w}" height="{h}" '
            + f'data-width="{w}" data-height="{h}" data-hash="{resource["sha256"]}" '
            + 'alt="' + escape(page + ' ' + label.lower() + '; provisional association', quote=True) + '"></div>'
            + '<div class="zoom-controls" hidden><label for="zoom-' + dom_id + '">Zoom from fitted width</label>'
            + '<input id="zoom-' + dom_id + '" type="range" min="1" max="6" step="0.25" value="1"><output>1×</output></div>'
            + '<figcaption>' + identity + f' · JPEG size {w} × {h}. '
            + '<a href="' + escape(resource['url'], quote=True) + '" target="_blank" rel="noopener">Original Yale image</a></figcaption>'
            + '<p class="image-status muted" aria-live="polite">Input bytes checked by the builder; display not yet checked.</p>'
            + '<p class="hash-status muted" aria-live="polite">Build-time SHA-256 check passed.</p>'
            + '<details><summary>Recorded image fingerprint</summary><p class="hash">' + resource['sha256'] + '</p></details>'
            + '</figure></details>')


def render(settings, selection, review, catalog, template):
    resources = {item['name']: item for item in review['retrieved_resources']}
    pairs, options = [], []
    for index, (pair, case) in enumerate(zip(selection['selection']['selected_pairs'], review['cases'])):
        dom_id = 'pair-' + str(index)
        title = pair['locus_key'] + ' → ' + pair['chosen_reference']['locus_key']
        options.append('<option value="' + dom_id + '">' + escape(title) + '</option>')
        roles = []
        for role, label, page, context in (
                ('target', 'Diagnostic target', case['target_page'], pair['target_native_context']),
                ('reference', 'Development occurrence', case['reference_page'], pair['reference_native_context'])):
            key = case['target_key'] if role == 'target' else case['reference_key']
            roles.append('<article class="role"><h3>' + label + ' · ' + escape(key) + '</h3>'
                         + native_html(context, catalog, settings['accepted_input_commit'])
                         + ''.join(image_html(page, kind, resources[page + '-' + kind + '.jpg'])
                                   for kind in ('whole', 'context', 'token'))
                         + '</article>')
        notes = ''.join('<h3>' + label + '</h3><p>' + escape(case[field]) + '</p>' for field, label in (
            ('target_row_evidence', 'Proposed target association'), ('reference_row_evidence', 'Proposed development association'),
            ('target_visible', 'Original target description'), ('reference_visible', 'Original reference description'),
            ('comparison', 'Original comparison'), ('alternatives', 'Alternative placements considered')))
        notes += '<ul>' + ''.join('<li>' + escape(item) + '</li>' for item in case['remaining_uncertainties']) + '</ul>'
        pairs.append('<section class="pair" id="' + dom_id + '"><h2>' + escape(title) + '</h2><p>'
                     + 'Literal lookup: <code>' + escape(pair['original_first_form']) + '</code> → <code>'
                     + escape(pair['reference_form']) + '</code>. Original target slot 0; development slot '
                     + str(pair['chosen_reference']['original_slot_zero_based']) + ' (zero-based).</p>'
                     + '<div class="roles">' + ''.join(roles) + '</div>'
                     + '<details class="observations"><summary>Original nonblind AI observations from PR #115</summary>'
                     + '<p><a href="https://github.com/tobrien6/voynich-manuscript-research/pull/115">Accepted evidence record</a>. '
                     + 'Single-observer provisional descriptions; independent human adjudication remains pending.</p>' + notes + '</details></section>')
    pins = '<p>Accepted commit: ' + settings['accepted_input_commit'] + '</p>'
    pins += ''.join('<p class="hash">' + escape(path) + ': ' + checksum + '</p>' for path, checksum in settings['input_sha256'].items())
    reference = resources['basic-eva.gif']
    notation = ('<figure><div class="image-window"><img src="assets/basic-eva.gif" width="' + str(reference['pixel_dimensions'][0])
                + '" height="' + str(reference['pixel_dimensions'][1]) + '" data-width="' + str(reference['pixel_dimensions'][0])
                + '" data-height="' + str(reference['pixel_dimensions'][1]) + '" data-hash="' + reference['sha256']
                + '" alt="Publisher Basic Eva shape reference"></div><div class="zoom-controls" hidden>'
                + '<label for="zoom-notation">Zoom from fitted width</label><input id="zoom-notation" type="range" '
                + 'min="1" max="6" step="0.25" value="1"><output>1×</output></div>'
                + '<p class="image-status muted" aria-live="polite">Reference input bytes checked by the builder.</p>'
                + '<p class="hash-status muted" aria-live="polite">Build-time SHA-256 check passed.</p></figure>'
                + '<p><a href="' + escape(reference['url'], quote=True) + '" target="_blank" rel="noopener">Original publisher image</a> · '
                + '<a href="https://voynich.nu/transcr.html" target="_blank" rel="noopener">Publisher notation description</a>. '
                + 'Shape labels do not establish phonetic readings.</p>')
    for marker, value in {'__PAIR_OPTIONS__': ''.join(options), '__PAIR_SECTIONS__': ''.join(pairs),
                          '__INPUT_PINS__': pins, '__NOTATION_REFERENCE__': notation}.items():
        require(template.count(marker) == 1, 'missing or duplicated template marker')
        template = template.replace(marker, value)
    return template


def packet_bytes(image_directory):
    settings, selection, review, catalog = load_inputs()
    verify_record(review, selection, ROOT, image_directory)
    template_raw = (ROOT / TEMPLATE).read_bytes()
    page = render(settings, selection, review, catalog, template_raw.decode('utf-8')).encode('utf-8')
    files = {'index.html': page}
    for resource in review['retrieved_resources']:
        name = resource['name']
        require(Path(name).name == name, 'resource filename is not a basename')
        raw = (image_directory / name).read_bytes()
        require(sha(raw) == resource['sha256'], 'image input changed during generation')
        files['assets/' + name] = raw
    manifest = {'schema_version': 1, 'viewer_id': settings['viewer_id'],
                'accepted_input_commit': settings['accepted_input_commit'], 'input_sha256': settings['input_sha256'],
                'generator_sha256': sha(Path(__file__).read_bytes()), 'template_sha256': sha(template_raw),
                'settings_sha256': sha((ROOT / SETTINGS).read_bytes()),
                'files': {name: sha(raw) for name, raw in sorted(files.items())}}
    files['packet.json'] = (json.dumps(manifest, indent=2) + '\n').encode('utf-8')
    return files


def protect_output(output, image_directory):
    resolved, images = output.resolve(), image_directory.resolve()
    require(not resolved.is_relative_to(ROOT.resolve()) and not ROOT.resolve().is_relative_to(resolved),
            'local image packet must be outside the checkout and its ancestors')
    require(not resolved.is_relative_to(images) and not images.is_relative_to(resolved),
            'output must be separate from the image input directory')
    require(not output.is_symlink() and (not output.exists() or (output.is_dir() and not any(output.iterdir()))),
            'output must be a fresh empty directory without a symbolic link')


def write_packet(output, image_directory):
    protect_output(output, image_directory)
    files = packet_bytes(image_directory)
    protect_output(output, image_directory)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'assets').mkdir()
    for name, raw in files.items():
        path = output / name
        with path.open('xb') as stream:
            stream.write(raw)


def check_packet(output, image_directory):
    expected = packet_bytes(image_directory)
    require(not output.is_symlink() and not (output / 'assets').is_symlink(), 'packet directories cannot be linked')
    actual = {path.relative_to(output).as_posix() for path in output.rglob('*') if path.is_file()}
    require(actual == set(expected), 'packet has missing or unexpected files')
    for name, raw in expected.items():
        path = output / name
        require(not path.is_symlink() and path.stat().st_nlink == 1 and path.read_bytes() == raw,
                'packet file differs or is linked: ' + name)


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
            print('Built local two-pair review packet from verified files; keep pixel assets local.')
        else:
            check_packet(args.check, args.image_directory)
            print('Accepted inputs, local asset bytes and complete viewer packet reproduce.')
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'lookup viewer failed: {error}\n')


if __name__ == '__main__':
    main()
