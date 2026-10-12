# Rosette small-circle region proposal

A small circular feature near the lower-left of Yale's shared rosette scan has
curved writing and two flanking short text items, compatible with the source
group at native loci 112-115. The [proposal](fRos-small-circle-proposal.json)
records a **broad inspection window**, not a verified four-locus image join.
Glyph readings, arc boundaries, start positions, and directions remain unresolved.

## Fixed targets and source evidence

The [plan](FROS_SMALL_CIRCLE_PLAN.md) was committed at `ac62f99` before this
contribution retrieved or viewed the manuscript derivative. The four targets
were chosen as one contiguous source-described group, not by selecting glyphs
that appeared easiest to match after inspection. Existing whole-image notes,
the source annotations and both native readings had already been viewed.
This is an informed AI layout proposal, not a blind or expert replication.

In pinned [ZL3b](https://voynich.nu/data/ZL3b-n.txt), physical lines 5390-5394
describe the author's named "clock" and four associated loci. That term is a
source locator label; the function or meaning of the drawing is not established.
Pinned [GC2a](https://voynich.nu/data/GC2a-n.txt) contains the same locus codes
at physical lines 3790-3793, in its different v101 notation. Matching identifiers
and types do not prove matching glyph readings or independent annotation history.

| Native target | ZL source locator description | Status after image inspection |
| --- | --- | --- |
| `fRos.112,@L0` | Left of the named feature | A separate lower-left item is compatible; full glyph alignment is unresolved. |
| `fRos.113,=Cc` | Above; source start comment 08:00 | Curved writing surrounds the candidate ring; exact arc, start and clockwise direction remain unverified. |
| `fRos.114,+Ca` | Below; source start comment 06:30 | Writing extends below the ring; its division from the other arc and anticlockwise direction remain unverified. |
| `fRos.115,=L0` | Right of the named feature | A separate upper-right item is compatible; full glyph alignment is unresolved. |

The [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
issue 2.0.2, Tables 8-9 on printed pages 21-22, defines relative locators and
clockwise/anticlockwise circular types. These are source annotations to check,
not directions independently established by this image review.
The PDF identity is the accepted SHA-256
`7ac9c4a82064763cac8767cca6f661cc4e1b4503ab9342acc03032ddb6939d49`.

The [reproducible native checklist](fRos-small-circle-review.json) retains every
target's complete native text and inline annotations, source physical line,
kind, locator, edition alphabet, URL and exact source hash. No alphabet
conversion, resolution of ligatures/alternatives, or space adjudication occurs.
For example, ZL's lower circular text retains `[aiird:???]`; the checklist
does not choose a reading from that alternative.

## Image observations and region

Inspected on 12 October 2026 (America/New_York), first as the
[4,000-pixel-bounded whole scan](https://collections.library.yale.edu/iiif/2/1006231/full/!4000,4000/0/default.jpg),
then as the [original-resolution region](https://collections.library.yale.edu/iiif/2/1006231/800,6000,1100,1050/full/0/default.jpg).
The proposal records both URLs, hashes, byte lengths, dimensions, and their order.
The original image is 7,925 by 7,268 pixels, matching Yale's image service and
the accepted index. Source images remain linked rather than redistributed.

Direct observations: a small brown ring lies below the lowest large circular
drawing in the left column. Two irregular segments meet inside the ring, and
short dark writing curves around its outside. Separate slanted writing appears
to the lower left and upper right; adjacent text/drawing also enters the window.
That combined layout motivates the provisional group association. It does not
establish four exact text boundaries or a reading of any glyph sequence.

The inspection rectangle uses original-image coordinates with top-left origin:
`x=800, y=6000, width=1100, height=1050`. Its equivalent normalized coordinates
are stored and checked against those dimensions. This is a viewport containing
the whole candidate pattern and nearby context, not per-locus masks, panel crops,
or a physical leaf assignment.

The exact [Yale carrier](https://collections.library.yale.edu/catalog/2002046?child_oid=1006231)
remains `85v and 86r (foldout)`. The existing dependency `yale-leaves:85+86` is
retained. Do not split leaves based on this viewport or discard other indexed
scans because only one region is inspected. The [source-coverage contribution](https://github.com/tobrien6/voynich-manuscript-research/pull/68)
also records IT2a's absent rosette text; this proposal does not supply that text
or make the paired pilot complete.

## Reproduce and next test

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 scripts/build_fros_review.py --check research/panel-regions/fRos-small-circle-review.json
python3 scripts/build_fros_review.py --output /tmp/fRos-small-circle-review.json
python3 -m unittest tests.test_fros_review -v
```

The generator checks both source byte pins and all four exact present targets,
plan/proposal/reader identities, shared carrier/dependency, bounded pixel and
normalized regions, corresponding image requests/dimensions, and the unresolved status. It preserves source inputs and
the plan, including linked paths, and rejects a changed committed checklist.
It validates a declaration's consistency; it cannot validate the image observation.

Independent reviewers should compare the full original-resolution glyph sequences
against both complete native records, resolve arc boundaries/start points/directions,
and record disagreements in spaces, ligatures and alternatives. Keep source-clock
comments separate from actual image positions. Only a separately reviewed glyph
alignment may support an image/text crosswalk. The proposal remains excluded from
statistics with a null verified crosswalk and no independent glyph review.
No decipherment, semantic interpretation, translation, or untouched evaluation
sample is claimed.
