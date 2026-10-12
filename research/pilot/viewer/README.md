# Local f76r image/native-text comparison

Open `research/pilot/viewer/f76r.html` from a local clone in a browser. The
self-contained HTML/CSS/JavaScript and native text work without a backend;
the official Yale image windows require an internet connection. With JavaScript
enabled, choose one of the three anchors and zoom from its fitted display size.
Image zoom scrolls inside its window. Neighbor context, original observations,
unresolved readings, edition credits and input provenance remain available.

Without JavaScript, all three anchor sections are shown and native HTML
disclosures still expose their contexts. If an image fails to load, source text
and the official region link remain available. The artifact stores no notes or
annotations and applies no source corrections.

## What is displayed

The [original accepted pilot](../F76R_ANCHORS.md) supplies only `f76r.1`,
`f76r.35` and `f76r.56`, with fourteen complete native anchor/neighbor fields
across ZL3b and IT2a. Case, punctuation, tags, alternatives and unreadability
markers are rendered literally rather than treated as HTML. Source-file line
numbers link to the exact committed files. No text normalization, glyph
substitution, inferred token box or physical-line conversion is introduced.

Official Yale image `1006210` and the three recorded native-pixel review windows
are preserved. All row associations remain **provisional**, and both initial
and median reading disagreements remain unresolved. These windows include
neighboring writing; they are not verified glyph or token boxes.

The displayed observations are attributed to the original pilot record in
[PR #60](https://github.com/tobrien6/voynich-manuscript-research/pull/60).
The separate [second AI-assisted check](https://github.com/tobrien6/voynich-manuscript-research/pull/99)
is linked as later evidence, not merged into the original notes. That check was
non-blind, did not establish model independence or independent human validation,
and retained provisional mappings. This interface makes the evidence easier
to inspect; it does not adjudicate those observations.

## Pinning and reproduction

[inputs.json](inputs.json) fixes the exact accepted input commit
`c6ce2571c52d5880cb8361f3a9074e106f662c7a` and byte digests for the original
review, frozen selection and source catalog. The builder checks both current
bytes and the actual Git blobs at that commit, then runs the accepted review
metadata verifier. Changed inputs require review rather than a silent refresh.
The artifact's metadata also fingerprints its settings, generator and template.
The accepted input commit and blobs must be available locally to rebuild.

From the repository root, using Python 3.10 or later and Git:

```sh
python3 scripts/build_f76r_viewer.py --check research/pilot/viewer/f76r.html
python3 scripts/build_f76r_viewer.py --output /tmp/f76r-comparison.html
python3 -m unittest discover -s tests -p 'test_f76r_viewer.py' -v
```

The builder reuses the guarded f76r cache writer's input protection and also
protects its manifest, template and generator. Direct, symbolic and hardlink
aliases are rejected before production and again before writing. It changes
neither the historical selector nor any original source/review bytes.

Viewing the generated file needs neither Python nor Git. An optional static
server can be used instead of opening the file directly:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory research/pilot/viewer
```

Then open `http://127.0.0.1:8000/f76r.html` locally.

## Validation and delivery boundary

Seven focused tests check all fourteen literal native fields and their exact
source-file links, source-region URLs/dimensions, provisional status, escaped
markup, input/commit drift, byte-for-byte artifact replay, and temporary output
aliases. Browser inspection covered all anchor choices, native keyboard
selection, keyboard zoom, and 1280-, 390- and 320-pixel layouts. Narrow layouts
stack the two source columns; page width does not overflow, including at sixfold
image zoom. A temporary scriptless QA copy exposes all three sections and
fourteen native fields. A separate temporary broken-image copy retains native
text and shows the image failure/link fallback. The viewport override was reset.

The viewer is a **local repository artifact**. The current 99 Tokens renderer
shows Markdown and folio raster plates and does not execute HTML/JavaScript or
iframes. GitHub's HTML-file link displays source rather than this interactive
view. No hosted URL, 99 Tokens integration or deployment configuration is added.

Image pixels are referenced from Yale, not copied into the repository. Recorded
inspection hashes are available, but the page does not verify live image byte
hashes. It observes loaded dimensions only. Native transliteration credits,
editions and publisher links come from the pinned catalog; its CC0 terms do not
extend to Yale images or fonts. The page and texts were already exposed; opening
this viewer creates no untouched evaluation material or decipherment evidence.
