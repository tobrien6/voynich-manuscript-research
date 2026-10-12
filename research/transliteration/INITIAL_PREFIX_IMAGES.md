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

## f78r.21: same-page comparison supports a provisional l preference

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

**Initial interpretation.** The first review left the `l`/`q` classification
unresolved: the visible contrast with the next token alone does not define a
glyph-family boundary. A targeted reference comparison adds evidence below;
it does not make the row match or classification verified.

### Planned same-page references

The [comparison plan](INITIAL_PREFIX_COMPARISON_PLAN.md), committed at
`4a40321` before inspecting the additional regions, fixes the earliest
source-agreed, readable initial `l` and `q` tokens on this page. The full page
and disputed crop had already been seen, so this is not a blind test.

Both editions and both spacing policies give `lchedy` at `f78r.43`
(ZL line 4425; IT line 2889) and `qokeedy` at `f78r.4`
(ZL line 4385; IT line 2850). These are the first qualifying references in
numeric locus order: there is one `l` candidate and eleven `q` candidates.
The review records all candidate keys and preserves both native source loci.
ZL's `f78r.43` includes a later `[a:o]` alternative; it fails whole-locus adapter
eligibility. Its readable first token qualifies under the explicitly separate
reference rule, which does not enlarge the original disputed-case cohort.

| Reference | Row context | Beginning | Provisional row evidence |
| --- | --- | --- | --- |
| `f78r.4`, agreed `qokeedy` | [Upper block](https://collections.library.yale.edu/iiif/2/1006214/310,430,1280,250/full/0/default.jpg) | [Initial region](https://collections.library.yale.edu/iiif/2/1006214/340,530,620,120/full/0/default.jpg) | Between the opening `f78r.3` and `f78r.5`; the source-agreed neighboring sequence remains in view. |
| `f78r.43`, agreed `lchedy` | [Lower block](https://collections.library.yale.edu/iiif/2/1006214/300,2920,1250,390/full/0/default.jpg) | [Initial region](https://collections.library.yale.edu/iiif/2/1006214/350,3090,750,180/full/0/default.jpg) | Final left-block line after `f78r.41` and `f78r.42`; the second token is represented as `pchedy` in both editions. |

**Comparison observation.** The disputed initial and the selected `l` reference
both have a compact loop/crossed top and an oblique descending stroke. The
selected `q` reference has a more extended, near-vertical stem. Along these
stated features, the disputed beginning is closer to the `l` reference.

**Updated interpretation.** This comparison provisionally favors ZL's `l`
representation over IT's `q`. Both reference row matches remain one observer's
judgments. Agreement between related source editions is not independently
established glyph ground truth; one reference pair cannot define the entire
range of handwriting variants. An independent observer should check all three
alignments and further variations before any versioned correction. This is a
same-page comparison, not a verified assignment of a writing hand.

## Reproduce and limitations

Python 3.10 or later, standard library only. Source files and the canvas index
are committed; the selector performs no network access.

```sh
python3 scripts/select_initial_prefix_images.py --check research/transliteration/initial_prefix_selection.json
python3 scripts/verify_initial_prefix_review.py
PYTHONPATH=tests python3 -m unittest test_initial_prefix_images test_initial_prefix_review
```

Tests exercise numeric ordering and side distinctions, one selection per side,
policy-dependent disagreements, complete-locus exclusions, partial/combined
and duplicate canvases, overlapping exclusions, missing identities, empty
selections, and accounting for all shared pinned P0 locations. Reopen the
linked derivatives to assess the manual observations; automated selection
checks cannot do that. The review verifier recomputes reference choice, preserves
source uncertainty, checks native region URLs/dimensions/bounds and the
selection-byte binding, and rejects omitted cases, changed reference metadata,
or unsupported verified/correction flags. Optional repeated
`--image-file 'RECORDED_URL=/path/to/local/image.jpg'` bindings check byte hashes
and GIF/JPEG header dimensions without decoding pixels or judging shapes.

Two provisional preferences with unresolved independent review cannot rank the sources or
estimate corpus-wide error. Both editions and both policies remain dependent
representations of the same manuscript. Derivative hashes identify inspected
bytes, not future server output or correct readings. No glyph inventory,
decipherment rule, or English translation is established. The image review's
`may_apply_as_source_correction` flag is false; any later correction needs an
independent region review and an explicit versioned decision.

The [separate nonblind AI inspection](PREFIX_SECOND_OBSERVER.md) supports the
proposed row matches and provisionally reproduces the f78r `l` comparison.
It records the small adjacent mark at f18v's initial cluster and leaves its
`r`-token segmentation unresolved. It supplies additional inspection evidence;
independent human adjudication and any versioned correction remain pending.
