# Image pilot for five residual paragraph-end disagreements

## Question and selection

The [generic-P context audit](GENERIC_P_CONTEXT.md) retains 38 P0 end-mark
disagreements outside its exact centred-line pattern. This pilot inspects
the first three residual pages selected by numeric folio and literal page
identifier: **19v, 24v, 26v**. All five residual contexts on those pages are
included. The [plan](RESIDUAL_PARAGRAPH_IMAGE_PLAN.md) was committed before
opening the images; source metadata had already been explored.

The [structured record](residual_paragraph_image_pilot.json) preserves every
source context, complete generic-P page annotations, image references and
local derivative fingerprints, direct observations, provisional associations,
exposure, and dispositions. The images stay local and are linked below.
All five divisions remain unresolved after AI-assisted initial inspection.

## Source annotations and direct observations

| Yale source | Disputed P0 end | Next encoded locus | Observed layout near the transition | Disposition |
| --- | --- | --- | --- | --- |
| [19v](https://collections.library.yale.edu/catalog/2002046?child_oid=1006111) | `f19v.13` | `f19v.14,+Pr` | Short right-shifted final row below the preceding writing, without a clear blank separator. | unresolved |
| [24v](https://collections.library.yale.edu/catalog/2002046?child_oid=1006121) | `f24v.11` | `f24v.12,+P0` | Writing continues beside the plant with no clear enlarged gap at the candidate transition. | unresolved |
| [26v](https://collections.library.yale.edu/catalog/2002046?child_oid=1006125) | `f26v.2` | `f26v.3,+P0` | Continuous upper writing block, without a clear blank band after row two. | unresolved |
| same 26v image | `f26v.4` | `f26v.5,+P0` | Same continuous block, without a clear blank band after row four. | unresolved |
| same 26v image | `f26v.6` | `f26v.7,+P0` | Same continuous block, without a clear blank band after row six. | unresolved |

In every selected source context, IT has one end mark on the current P0 locus
and one start mark on the next locus; ZL has neither. The next locus is Pr on
19v and P0 in the other four cases. These encoded relationships explain why
none matches the audit's narrowly specified Pc pattern. They do not establish
which source's paragraph convention is preferable.

On **19v**, fourteen ordered writing rows occupy two groups near the upper
left beside the plant. The last row is much shorter and shifted right. Both
sources classify it as Pr. ZL's markers place it with the preceding lower
paragraph; IT marks it as a separate one-locus paragraph. The visible short
row resembles the earlier centred-line cases in its terminal position, while
its right alignment is a different subtype. Shortness and alignment do not
supply the clear block separation required for an adjudication.

On **24v**, sixteen ordered rows follow the left side of the plant. A larger
gap follows the first five rows, where the sources agree on a boundary. The
disputed eleventh-to-twelfth transition lies within the subsequent writing
sequence, with no comparably clear blank band. Both adjacent loci are P0;
there is no Pc or Pr terminal-line context at this position. ZL annotates
the later sequence through locus 16 as one paragraph, while IT inserts an
additional division after locus 11.

On **26v**, nine ordered rows form a wide block above the plant. The disputed
transitions after rows two, four, and six show no clear enlarged gaps. Tall
strokes occur at several row starts; this observation assigns no glyph identity
or meaning. ZL's page markers enclose loci 1–9 together, while IT's markers
divide them into 1–2, 3–4, 5–6, and 7–9. The marker interpretation is separate
from the image observations and does not establish four visual blocks.

## Association, uncertainty, and implications

Both sources have 14, 16, and 9 present generic-P loci on these three pages,
respectively. Their ordered layout and the independently counted visible
rows support provisional source-row associations. Individual glyph strings
have not been independently aligned to image regions. The source record also
retains a drawing-interruption annotation on 24v's second locus in ZL but not
IT; that difference is outside the selected transition and is not resolved.

**All five divisions remain unresolved.** No candidate supplies both an
independently verified row association and clear block separation under the
pre-inspection rule. Absence of a large gap does not disprove a paragraph
convention that uses other cues. Retain both sets of source marks until the
project declares a paragraph definition and checks the glyph-level alignment.

The earlier [centred-line pilot](https://github.com/tobrien6/voynich-manuscript-research/pull/40)
and this residual sample show distinct contexts for source grouping differences.
This sample adds three inspected pages and five locus comparisons. Its three
26v comparisons share one image and text block, so they are not three
independent manuscript samples. Neither pilot estimates an annotation error
rate or supports a decipherment or translation.

## Reproduce the provenance checks

Python 3.10 or later; standard library only:

```sh
python3 scripts/verify_residual_paragraph_pilot.py
PYTHONPATH=tests python3 -m unittest test_residual_paragraph_pilot -v
```

The checker verifies the generic-P audit against pinned sources, both input
fingerprints, fixed page selection, complete coverage of all five contexts,
all generic-P page annotations, exact standalone image links, and required
uncertainty declarations. It does not certify the visual judgments. To verify
the locally retrieved image bytes, add `--image-dir /path/to/local/images` with
files named `f19v.jpg`, `f24v.jpg`, and `f26v.jpg`.

The derivatives were bounded to 2,200 pixels in height; inspected widths were
1,663, 1,671, and 1,663 pixels, checked separately from the offline script.
Sources, edition credits, and marker conventions are inherited from the
[generic-P audit](GENERIC_P_CONTEXT.md) and its pinned source register.

All three image exposures are recorded. Future evaluation splits must disclose
them, alongside earlier project exposure, rather than represent these pages
as previously unseen.
