"""Build a pinned, read-only local image/native-text comparison page."""

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import re
import subprocess
import sys

try:
    from .verify_f76r_review import verify
    from . import write_f76r_selection_cache as writer
except ImportError:
    from verify_f76r_review import verify
    import write_f76r_selection_cache as writer


ROOT = writer.ROOT
SETTINGS = "research/pilot/viewer/inputs.json"
TEMPLATE = "research/pilot/viewer/template.html"
ARTIFACT = "research/pilot/viewer/f76r.html"
INPUTS = ("research/pilot/f76r-anchor-review.json", "research/pilot/f76r-anchor-selection.json",
          "data/transliterations.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def protect_output(output, root, frozen):
    require(output.suffix.lower() == ".html", "Viewer output must be an HTML file")
    writer.protect(output, root, frozen)
    for source in [root / SETTINGS, root / TEMPLATE, root / "scripts/build_f76r_viewer.py", Path(__file__)]:
        require(output.resolve() != source.resolve() and not
                (output.exists() and source.exists() and output.samefile(source)), "Viewer output aliases an input/helper")


def list_html(items):
    return "<ul>" + "".join("<li>" + escape(item) + "</li>" for item in items) + "</ul>"


def native_html(anchor, ident, role, locus, source_blob_url):
    if locus is None:
        return '<p class="muted">No ' + escape(role) + ' source locus on this page.</p>'
    return (f'<p class="file-line"><span class="locus-id">{escape(locus["identifier"])}</span>'
            f' · <a href="{escape(source_blob_url, quote=True)}#L{locus["source_file_line"]}" '
            f'target="_blank" rel="noopener">source-file line {locus["source_file_line"]}</a></p>'
            f'<pre data-anchor="{escape(anchor, quote=True)}" data-source="{escape(ident, quote=True)}" '
            f'data-context="{escape(role, quote=True)}">{escape(locus["native_text"])}</pre>')


def render(record, catalog, settings, template, generation):
    sources = {source["id"]: source for source in catalog["sources"]}
    files = {item["id"]: item for item in record["inspection_files"]}
    sections, options = [], []
    for row in record["records"]:
        key = row["key"]
        dom_id = "anchor-" + key.replace(".", "-")
        role = row["selection_role"].replace("_", " ")
        options.append(f'<option value="{escape(dom_id, quote=True)}">{escape(key)} · {escape(role)}</option>')
        image = files[row["inspection_file_id"]]
        source_cards = []
        for ident in ["ZL3b", "IT2a"]:
            source, contexts = sources[ident], row["native_source_contexts"][ident]
            blob_url = ("https://github.com/tobrien6/voynich-manuscript-research/blob/"
                        + settings["accepted_input_commit"] + "/" + source["path"])
            neighbors = "".join('<div class="neighbor"><h4>' + label + '</h4>' +
                native_html(key, ident, context, contexts[context], blob_url) + '</div>'
                for context, label in [("preceding", "Preceding native locus"), ("following", "Following native locus")])
            source_cards.append(f'<article class="source" aria-label="{escape(ident, quote=True)} native text">'
                f'<div class="source-head"><h3>{escape(ident)}</h3><span class="muted">{escape(source["alphabet"])}</span></div>'
                + native_html(key, ident, "locus", contexts["locus"], blob_url)
                + '<details><summary>Neighbor context</summary>' + neighbors + '</details>'
                + f'<details><summary>Edition and credit</summary><p>{escape(source["title"])}</p>'
                  f'<p>{escape(source["credit"])}</p><p>{escape(source["header_version_statement"])}</p>'
                  f'<a href="{escape(source["url"], quote=True)}" target="_blank" rel="noopener">Original publisher text</a>'
                  f'<p class="hash">Recorded source SHA-256: {escape(source["sha256"])}</p></details></article>')
        association = row["source_row_association"]
        sections.append(f'<section class="anchor" id="{escape(dom_id, quote=True)}" aria-labelledby="{escape(dom_id, quote=True)}-title">'
            f'<div class="anchor-head"><h2 id="{escape(dom_id, quote=True)}-title">{escape(key)} '
            f'<span class="anchor-role">· {escape(role)}</span></h2><span class="status">{escape(association["status"])}</span></div>'
            f'<p>{escape(association["candidate_description"])}</p>'
            f'<figure><div class="image-window"><img loading="lazy" src="{escape(image["url"], quote=True)}" '
            f'width="{image["width"]}" height="{image["height"]}" data-width="{image["width"]}" data-height="{image["height"]}" '
            f'alt="Official Yale review window for provisional native locus {escape(key, quote=True)}; it includes neighboring writing."></div>'
            f'<figcaption>Yale image {escape(record["image"]["image_oid"])} · native region {escape(str(image["native_region"]))}. '
            'Origin is upper left; x increases rightward and y downward. This is a review window, not a verified glyph box.</figcaption>'
            f'<div class="image-controls" hidden><label for="zoom-{escape(dom_id, quote=True)}">Zoom from fit</label>'
            f'<input id="zoom-{escape(dom_id, quote=True)}" type="range" min="1" max="6" step="0.25" value="1">'
            '<output>1×</output></div><div class="image-meta"><span class="image-status muted" aria-live="polite">'
            f'Recorded image size: {image["width"]} × {image["height"]} pixels.</span>'
            f'<a href="{escape(image["url"], quote=True)}" target="_blank" rel="noopener">Open native-resolution Yale window</a></div></figure>'
            '<div class="sources">' + "".join(source_cards) + '</div>'
            '<details class="review-note"><summary>Original pilot observations and unresolved readings</summary>'
            '<p>Observation record: ' + escape(record["review_status"])
            + '. <a href="https://github.com/tobrien6/voynich-manuscript-research/pull/60">Original pilot PR #60</a>.</p>'
            '<h3>Direct observations</h3>' + list_html(row["direct_observations"])
            + '<h3>Provisional association basis</h3>' + list_html(association["basis"])
            + '<h3>Unresolved readings and alternatives</h3>' + list_html(association["unresolved"])
            + '<p>' + escape(association["alternative_search_limit"]) + '</p>'
            + f'<p class="hash">Recorded local inspection SHA-256: {escape(image["sha256"])}</p></details></section>')
    commit = settings["accepted_input_commit"]
    pins = '<p>Accepted input commit: <a href="https://github.com/tobrien6/voynich-manuscript-research/commit/' + commit + '">' + commit + '</a></p><div class="pins">'
    for path, checksum in settings["input_sha256"].items():
        url = f'https://github.com/tobrien6/voynich-manuscript-research/blob/{commit}/{path}'
        pins += f'<div><a href="{escape(url, quote=True)}">{escape(path)}</a><div class="hash">SHA-256: {checksum}</div></div>'
    pins += '</div><p>Original inspection: ' + escape(record["inspection_date_local"]) + ' (' + escape(record["inspection_timezone"]) + ').</p>'
    pins += '<p>Generated from pinned input bytes; source selections and row associations are unchanged.</p>'
    meta = f'<meta name="accepted-input-commit" content="{commit}">'
    for name, checksum in generation.items():
        meta += f'<meta name="{escape(name, quote=True)}" content="{checksum}">'
    replacements = {"__PROVENANCE_META__": meta, "__ANCHOR_OPTIONS__": "".join(options),
                    "__ANCHOR_SECTIONS__": "".join(sections), "__INPUT_PINS__": pins}
    for placeholder, text in replacements.items():
        require(template.count(placeholder) == 1, "Missing or duplicate template placeholder")
        template = template.replace(placeholder, text)
    return template


def build(root=ROOT):
    settings_raw = (root / SETTINGS).read_bytes()
    settings = json.loads(settings_raw)
    require(settings["schema_version"] == 1 and settings["viewer_id"] == "f76r-native-comparison-v1"
            and set(settings["input_sha256"]) == set(INPUTS), "Unknown viewer input manifest")
    commit = settings["accepted_input_commit"]
    require(isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit), "Expected an exact accepted commit")
    raw = {}
    for path in INPUTS:
        current = (root / path).read_bytes()
        require(digest(current) == settings["input_sha256"][path], "Viewer input fingerprint differs: " + path)
        committed = subprocess.run(["git", "show", commit + ":" + path], cwd=root,
                                   check=True, capture_output=True).stdout
        require(committed == current, "Accepted commit bytes differ: " + path)
        raw[path] = current
    review = json.loads(raw[INPUTS[0]])
    verify(review)
    template_raw = (root / TEMPLATE).read_bytes()
    generation = {"viewer-settings-sha256": digest(settings_raw), "viewer-template-sha256": digest(template_raw),
                  "viewer-generator-sha256": digest(Path(__file__).read_bytes())}
    return render(review, json.loads(raw[INPUTS[2]]), settings, template_raw.decode("utf-8"), generation)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        frozen = json.loads((ROOT / writer.SNAPSHOT).read_bytes())
        if args.output:
            protect_output(args.output, ROOT, frozen)
        page = build()
        if args.check:
            require(args.check.read_bytes() == page.encode("utf-8"), "Viewer artifact does not reproduce")
            print("PASS: accepted input commit, source/region text and generated viewer reproduce")
        else:
            protect_output(args.output, ROOT, frozen)
            args.output.write_text(page, encoding="utf-8")
            print("Wrote read-only f76r comparison viewer")
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
