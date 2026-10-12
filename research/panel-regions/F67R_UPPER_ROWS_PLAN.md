# Four upper 67r rows: image-inspection plan

Question: do the four upper horizontal rows in Yale image 1006194 support the
accepted proposal placing native `f67r1.1` through `f67r1.4` there in order?
Inspect all four targets, retaining contradictions and ambiguous features.
This supplements the provisional [layout/checklist](README.md) and
[first-row boundary case](67R_BOUNDARY_CASE.md).

## Selection and known exposure

Fix the four keys before this pass's image retrieval: `f67r1.1`, `f67r1.2`,
`f67r1.3`, `f67r1.4`. They are every P0 record in the proposed left-panel
upper block in both pinned editions. Do not replace an inconvenient row or
choose a favorable edition. The three right-panel P0 records, circular and
radial items are outside this review's target set.

The native readings, panel proposal, source counts and prior first-row gap
observation have been read. The corpus has already informed statistical work.
This is a source-informed, nonblind AI inspection, not an untouched test or an
independent manuscript witness. Publication before this pass records the
selection; it does not independently certify chronology or erase exposure.

Pinned local inputs, SHA-256:

| Input | SHA-256 |
| --- | --- |
| `data/transliterations.json` | `13f5692b57259e50c575f841eb96e351945abf19f94a0c035668dda4c96a5b27` |
| `scripts/build_67r_review.py` | `07e071abd5ceb469c23aa3a16175ae5967b8c9c6d63fb5e47d64d01c3725085f` |
| `f67r-proposal.json` | `f958a98977c56fcbdbb65f3f31c5ebd5733b0f00a5ca699023e3cb164eea45e7` |
| `f67r-p0-review.json` | `13063b8994b342b97721e2fe6c01c6d976736fff23a8959e33c26a4f55b57a0e` |
| `f67r1-1-boundary-case.json` | `9a28e0eb9a0f34bb445280891702846c1a798f535ba6ae2666adc5e27c2e3bbe` |

The accepted collector reproduces all seven native records before this pass.
Preserve both sources' full reader text, identifiers, file lines and alphabet
labels through the existing checklist; no case folding or glyph conversion.

## Image method

First inspect the [complete bounded scan](https://collections.library.yale.edu/iiif/2/1006194/full/!1800,1800/0/default.jpg)
and verify its existing response identity. The accepted native dimensions are
4972 × 3738. Then inspect an initial native-pixel context band
`0,200,2486,900`, covering the left half around the proposed upper block.
This band is selected from the existing layout and first-row detail, before
the new view; it is not an exact locus mask.

After those views, choose row-context rectangles and, where needed, smaller
opening/middle/ending windows. Record every requested URL, native bounds,
returned dimensions and hash, and disclose this adaptive window selection.
Retain the complete row context; extend a window and record the reason if it
clips a target. Do not enhance, rotate, sharpen or invent image marks.

Compare visible opening, middle and ending sequences with the two source
readings, using [Basic Eva Table 3](https://voynich.nu/transcr.html) for shape
context. Encoded letters are notation, not validated glyph or word counts.
Retain the first-row `o.aiin` / `oaiin` difference, row-two reading alternatives,
row-three uncertain/alternative forms and row-four bracket/comma differences.
No source reading wins merely because it provides a convenient anchor.

For each target record the proposed physical row, context bounds, shape/order
evidence, contradictory evidence and unresolved features. Classify the proposed
row association as supported by visible anchors, contradicted, or insufficient
at the inspected scale. Partial anchors do not verify every glyph, linguistic
word division or a preferred source text. All four outcomes must be retained.

## Limits and handoff

Keep the original proposal/checklist/source exports unchanged and keep
`usable_as_verified_corpus_join` false. The new context rectangles are inspection
aids, not exact glyph masks. A separate reviewed crosswalk and any glyph or
segmentation adjudication require their own evidence and decision record.

All views derive from one 67r scan and leaf dependency; the full scan also
exposes the right-panel drawings and writing. Carry this exposure forward.
Publish only links, metadata and original observations; source pixels and font
images stay out of the contribution. No reading, mechanism, language,
decipherment, translation or exposure-valid evaluation is established here.
