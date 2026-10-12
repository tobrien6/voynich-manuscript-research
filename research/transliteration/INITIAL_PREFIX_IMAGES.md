# Image checks of initial-prefix disagreements

## Question, selection, and scope

When paired source editions disagree about a literal first-token `q` or `y`
prefix, does the manuscript region support either representation?

The [selection plan](INITIAL_PREFIX_IMAGE_PLAN.md) was committed at `57e35db`
before inspecting the selected images. The complete transcriptions and previous
prefix results were already exposed; this exercise creates no untouched
evaluation material. It adds a single observer's image evidence to the
representation-level comparisons, without changing the pinned sources.

Use the [accepted ZL3b/IT2a pins](../../data/transliterations.json) and the
`plain-eva-v1` adapter with P0 only. Require eligibility, at least two tokens,
and regular locators in all four source/spacing combinations. Require the
prefix-feature disagreement to persist under both split and join policies.
Keep only pages with exactly one exact single-side Yale canvas, excluding
partial/combined labels and avoiding panel inference. Sort numerically by
folio, recto before verso, then locus; take the earliest candidate on each of
the first three distinct eligible sides.

The reproducible [selection report](initial_prefix_selection.json) retains the
3,884 shared P0 keys through explicit candidate/exclusion accounting. Exactly
**two** locations qualify: `f18v.5` and `f78r.21`. Both are selected. There is no
third eligible side; no excluded or visually convenient replacement is used.
The 3,882 other locations are accounted for by overlapping eligibility reasons,
unsupported canvas matches, or matching prefix features. These counts describe
the declared filter, not source accuracy or the manuscript's entire glyph set.

The report records every candidate, excluded key and reason, source hashes,
index and implementation hashes, first-token strings, locus identifiers and
file line numbers under every policy. The [image review](initial_prefix_review.json)
binds its records to the selection report's byte hash and records inspected
derivative URLs, original pixel dimensions and byte hashes. Neither script
selection nor those hashes verifies a visual reading.

## Notation reference and image method

The publisher's [Basic Eva table](https://voynich.nu/img/extra/eva01.gif), linked
from [Table 3 of the transliteration description](https://voynich.nu/transcr.html),
is a shape reference. Its ASCII labels supply no phonetic or semantic reading;
handwriting variation can leave a classification uncertain. Credits and source
reuse terms remain in the [transcription source register](../transcriptions/SOURCES.md).

Inspect the full Yale image before its row-context and initial-region
derivatives. The region URLs below use `x,y,width,height` in the original
image's pixels. Neighboring text and layout support each proposed source-to-row
match; a locus number alone is insufficient. Alignments and preferences remain
single-observer judgments needing a second review. Source pixels stay local;
the contribution publishes links and original observations.

## f18v.5: an extra first token in IT

[Yale canvas 1006109, label 18v](https://collections.library.yale.edu/catalog/2002046?child_oid=1006109).
The full image is 2,846 × 3,781 pixels. Consult the
[row context](https://collections.library.yale.edu/iiif/2/1006109/1400,650,1300,380/full/0/default.jpg)
and the [initial region including the preceding margin](https://collections.library.yale.edu/iiif/2/1006109/1250,770,650,140/full/0/default.jpg).

**Source difference.** ZL3b file line 781 begins `ychoees`; IT2a line 466
begins `r.ychoees`, with `r` as a separate apparent token. Joining uncertain
spaces changes neither edition's first slot here. This is a first-slot
segmentation/presence discrepancy, not simply two names for the same first
ASCII character.

**Proposed alignment.** The target is the fifth visible row of the upper-right
text block, between the q-starting rows represented as `f18v.4` and `f18v.6`.
Their repeated tall forms and the target row's sequence support this match.
The region retains surrounding rows so a reviewer can check the alignment.

**Visible evidence.** One prominent looped shape with a descending curved
stroke begins the proposed row, followed by low connected forms. The initial
crop includes the margin before it; no separately spaced preceding r-shaped
sign is apparent at this resolution.

**Interpretation and remaining uncertainty.** The visible start resembles the
Basic Eva `y` shape, provisionally supporting ZL's first-slot feature. This
does not adjudicate the complete token spelling or establish an underlying
glyph count. A second observer should check for a small or combined sign that
might motivate IT's separate token and independently verify the row match.
No correction is applied.

## f78r.21: initial l/q classification remains unresolved

[Yale canvas 1006214, label 78r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006214).
The full image is 2,793 × 3,761 pixels. Consult the
[row context](https://collections.library.yale.edu/iiif/2/1006214/310,1550,1000,310/full/0/default.jpg)
and the [initial shape with the next token](https://collections.library.yale.edu/iiif/2/1006214/350,1650,700,130/full/0/default.jpg).

**Source difference.** ZL3b file line 4402 begins `lchedy`; IT2a line 2867
begins `qchedy`. Both spacing policies retain the literal q-prefix disagreement.

**Proposed alignment.** The target lies left of the upper circular illustration,
after `f78r.20` and before the y-starting `f78r.22`. Its next token shares the
`qokain` representation in both editions. Two label loci precede the paragraph
block, so locus 21 cannot be located by counting the twenty-first visible text
row. The shared neighboring sequence supports a provisional alignment.

**Visible evidence.** The initial sign has a compact loop/crossed top with a
relatively short oblique descending stroke. The next token's initial sign has
a more extended, near-vertical descending stroke. This shape contrast is visible
within the same row.

**Interpretation and remaining uncertainty.** The contrast alone does not
define the boundary between handwritten `l` and `q` variants in this notation.
No preferred representation is recorded. Check the alignment independently and
compare agreed `l`/`q` shapes in the same writing hand before making a decision.

## Reproduce and limitations

Python 3.10 or later, standard library only. Source files and the canvas index
are committed; the selector performs no network access.

```sh
python3 scripts/select_initial_prefix_images.py --check research/transliteration/initial_prefix_selection.json
PYTHONPATH=tests python3 -m unittest test_initial_prefix_images
```

Tests exercise numeric ordering and side distinctions, one selection per side,
policy-dependent disagreements, complete-locus exclusions, partial/combined
and duplicate canvases, overlapping exclusions, missing identities, empty
selections, and accounting for all shared pinned P0 locations. Reopen the
linked derivatives to assess the manual observations; automated selection
checks cannot do that.

One provisional preference and one unresolved case cannot rank the sources or
estimate corpus-wide error. Both editions and both policies remain dependent
representations of the same manuscript. Derivative hashes identify inspected
bytes, not future server output or correct readings. No glyph inventory,
decipherment rule, or English translation is established. The image review's
`may_apply_as_source_correction` flag is false; any later correction needs an
independent region review and an explicit versioned decision.
