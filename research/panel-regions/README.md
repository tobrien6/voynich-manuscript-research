# Provisional 67r panel layout

Question: can layout and the documented naming convention narrow the image
placement of native `f67r1` and `f67r2` before a glyph-level alignment?

The [proposal record](f67r-proposal.json) is provisional. It is **not usable as
a verified corpus join** and does not make the pilot's unresolved 67r target
complete. It complements the
[whole-corpus side-reference audit in PR #37](https://github.com/tobrien6/voynich-manuscript-research/pull/37).

## Sources and observation method

Inspected Yale image [1006194, labeled 67r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006194)
on 11 October 2026 (America/New_York), using a
[1,800-pixel-bounded derivative](https://collections.library.yale.edu/iiif/2/1006194/full/!1800,1800/0/default.jpg).
The record includes that derivative's exact hash, size, and dimensions, plus
the original image dimensions and pinned manifest identity. No image is
redistributed.

The [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
issue 2.0.2, section 4.2 and Figure 1 (printed pages 11–12), orders recto panel
names away from the binding. Its illustrated example is 72; it does not itself
verify 67r text placement. The source page IDs and locus-type counts were
checked in the [pinned ZL3b/IT2a editions](../../data/transliterations.json).
Source counts and opening loci were viewed **before** image inspection, so
the layout concordance is not a blinded test or independent reproduction.

## Observations and proposed correspondence

| Proposed page | Direct image observation | Source annotations, in each edition | Interpretation to review |
| --- | --- | --- | --- |
| `f67r1` | Left field near the visible binding: four upper horizontal rows above a large colored radial drawing; circular bands and radial writing. | 19 present loci: 4 P0, 3 Cc, 12 Ri. | Native locations 1–4 may be the four upper rows, in order. |
| `f67r2` | Right field beyond the principal crease: compartmented circular drawing and three lower horizontal rows, with a red middle row. | 74 present loci: 27 L0, 32 Pb, 12 Ls, 3 P0. | Native locations 72–74 may be the three lower rows, in order. |

The visible binding and principal vertical crease support these **panel layout
proposals** under the naming convention. The row-count correspondence supports
a targeted review; it does not establish matching glyph strings. The two
editions share location identifiers and type counts but differ in readings.
Do not count those editions as two independent manuscript observations.

The [native P0 review checklist](f67r-p0-review.json) retains the two editions'
unmodified reader text and source-file locators at all seven proposed horizontal
locations. Only `f67r2.72` has identical native record text; the other six differ.
For example, `f67r1.1` ends with separate `o.aiin` in ZL and `oaiin` in IT;
`f67r1.2` contains ZL's `qoekeey` where IT has `qoekshg`. These are encoded
source discrepancies for image review, not adjudicated spaces or glyphs.
The identical record is a possible review anchor, not independent confirmation.

No pixel masks, exact bounding boxes, circular/radial locus placement, or
decoded content are assigned. Both panels reference one leaf and one canvas;
keep them in the same sampling unit and disclose this image/source exposure.

## Reproduce the structural checks

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 - <<'PY'
from collections import Counter
from scripts.audit_transliterations import load_sources
for source, document in load_sources():
    if source['id'] not in {'ZL3b', 'IT2a'}:
        continue
    for page in ('f67r1', 'f67r2'):
        loci = [l for l in document.loci if l.page == page and l.present]
        print(source['id'], page, len(loci), dict(Counter(l.kind for l in loci)))
PY
```

To compare the inspection response, download the linked derivative locally
and check its SHA-256 against the JSON record. A changed image derivative
requires review; a hash match identifies the inspected bytes without proving
that the observation is correct.

Next test: an independent reviewer should compare every proposed horizontal
location with the original-resolution glyph sequence, including ambiguous
spaces and alternative readings in each edition. Reject or revise a placement
when source order or glyphs disagree. Only after recording that review and
precise regions should a separate verified image/text crosswalk be proposed.

Reproduce the complete checklist with the shared source-pin checks:

```sh
python3 scripts/build_67r_review.py --check research/panel-regions/f67r-p0-review.json
```

No alternatives, spaces, paragraph markers, or source comments are resolved.
The seven locations are explicitly declared by this provisional layout proposal;
they are not a randomly sampled test of transcription quality. An absent,
duplicate, nonexistent, or non-P0 target makes the generator fail.

The [four upper-row image inspection](F67R_UPPER_ROWS.md) fixes every left-panel
P0 target before the new pass and records shared sequence anchors, complete
row-context windows and every source uncertainty. All four proposed placements
receive partial image support; full glyph/segmentation review and a verified
crosswalk remain pending. The original proposal/checklist and pilot gap are
unchanged.

The [three lower-row inspection](F67R_LOWER_ROWS.md) retains every right-panel
P0 target, both literal source readings and full context windows. Partial shape
and order anchors support the proposed placements while pale details and all
source differences remain open; both blocks share one exposed scan/leaf and
still require independent glyph/region review before a verified crosswalk.

## Rosette small-circle review

The separate [rosette region proposal](FROS_SMALL_CIRCLE.md) fixes four contiguous
ZL3b/GC2a targets before image retrieval and records a broad source-image inspection
window. Both complete native readings and all uncertain annotations remain in a
reproducible checklist. Layout supports a candidate association; glyph alignment,
arc boundaries/directions and independent review remain unresolved. The shared
85v/86r carrier stays one dependency, and the proposal cannot fill IT2a's absent text.

The [two-direction f102r1 boundary review](102R_BOUNDARY_PAIR.md) freezes one
ZL-only and one IT-only extra-boundary case before new image inspection.
Both adjacent loci retain provisional row placement and unresolved word
division; the shared 101v/102r carrier remains one image dependency.

## f89v bottom-label context

The separate [f89v context packet](F89V_CONTEXT.md) records both coarse Yale
canvases naming 89v and two dependent bottom-band windows. Historical `f89v2`
spans two reported physical panels. A layout match supports a provisional
container association; exact label regions, faint-trace origins and the modern
nonexistent-locus correspondence remain unresolved. It supplies no verified join
or physical text-presence decision.

The [f68r3 non-paragraph packet](F68R3_NONPARAGRAPH.md) retains all 22 native
circular/radial/label records despite zero P0 locations. Its fixed first/last
radial image attempts remain provisional, with all glyph alternatives and
twenty other unreviewed locations preserved on the shared 68r carrier.
