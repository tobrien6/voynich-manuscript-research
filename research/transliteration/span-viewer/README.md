# Local encoded boundary span review

Open [index.html](index.html) from a local clone in a browser. Its data, styles
and JavaScript are self-contained. Search and navigation work offline with
JavaScript enabled; following the source-file or publisher links needs an
internet connection. The page loads no images, fonts, libraries or other
external resources and stores no annotations or corrections.

The page displays every record in the [shared-anchor span inventory](../BOUNDARY_DISAGREEMENT_SPANS.md):
650 split spans across 562 native loci and 978 join spans across 767 loci.
It preserves the existing 2,940-key parent cohort and introduces no selection,
transcription, measurement or glyph mapping. The whole-locus notation counters
do not identify a separator type inside a particular span.

## Inspect a source pair

Choose the comma policy, search a native locus or case-sensitive literal ASCII
span, and filter by source cut pattern or local token-count difference. The
drawing filter hides entire loci with a recorded interruption in either source.
The displayed counts distinguish spans from unique native loci and retain the
complete policy denominator. Empty results mean no inventoried disagreement
matches those filters.

The span selector and previous/next controls show the complete original token
pieces, exclusive ASCII offsets and original source identifiers. Source-file
line links point to exact committed ZL3b/IT2a files. Changing policies retains
the same encoded interval when it exists in the other view; otherwise it chooses
the first available span in the same locus. The displayed policy and interval
always update. These are source-code coordinates, with glyph/word status
unresolved throughout.

For example, `f102r1.14` shows `s` / `or` versus `sor` at `[37,40)`.
The opposite-direction `f102r1.15` shows `ykeeykam` versus `ykeey` / `kam`.
Local equal-count spans remain available even when the exclusive cuts differ.
The [original method](../BOUNDARY_DISAGREEMENT_SPANS.md) explains why shared
anchors do not adjudicate physical words or image regions.

## Pinning and replay

[inputs.json](inputs.json) pins the inventory and source catalog to published,
technically reviewed input commit `2dd734bad3a8beb1b32cc4b64ad3b8027c0ecbd3`
from [PR #178](https://github.com/tobrien6/voynich-manuscript-research/pull/178).
The builder checks current bytes against both SHA-256 pins and actual Git blobs,
replays the complete inventory producer, and checks each linked native source's
bytes at that commit. Changed inputs require review rather than a silent refresh.

[provenance.json](provenance.json) records input, payload, template, settings,
generator and HTML fingerprints with both policy denominators. Rebuilding needs
Python 3.10 or later, Git, and the pinned commit/blob objects; opening the saved
HTML needs neither Python nor Git.

```sh
python3 scripts/build_boundary_span_viewer.py --check-dir research/transliteration/span-viewer
python3 scripts/build_boundary_span_viewer.py --output-dir /tmp/boundary-span-viewer
python3 -m unittest tests.test_boundary_span_viewer -v
```

The source, catalog, inventory, settings, template and implementation paths are
protected before packaging and immediately before each artifact write.
Temporary late symlink/hardlink regressions verify that the complete output
set is rejected before any artifact overwrites an input. This is not an atomic
filesystem-transaction guarantee.

An optional loopback server can be used for local inspection:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory research/transliteration/span-viewer
```

Then open `http://127.0.0.1:8000/index.html` locally.

## Verification and scope

Ten focused tests cover all 1,628 literal records and both denominators, exact
source links, input/commit drift, inert escaped metadata, template integrity,
unsafe publisher URLs, complete two-file replay and initial/late output guards.
Native metadata values are rendered through text nodes; embedded JSON escapes
markup and does not interpret source text as executable HTML.

Browser checks covered search, drawing filters, case-sensitive empty results,
reset, previous/next selection, native keyboard policy changes and preservation
of the current region. Equal-count filtering shows five split and eight join
spans, a different unit from whole-locus equal-count cases. At a 320-pixel
breakpoint the source columns stack and the page stays within the viewport.
The longest 19-letter original piece remains intact in its internally scrolling
panel. Browser viewport overrides are reset after testing.

The modern source transliterations are CC0; credits, editions and publisher links
remain visible in the provenance disclosure. Sources, policies, spans and prior
exposure remain dependent. No source preference, correction, statistical test,
independent or untouched evaluation, decipherment or translation is introduced.

This is a local repository artifact. The 99Tokens research renderer displays
Markdown and raster Folio plates; it does not execute this HTML/JavaScript.
The GitHub HTML link displays source. Hosting and site integration are separate
from this contribution.
