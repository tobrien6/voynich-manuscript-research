# Three fixed immediate-repeat image cases

The same uncertainty treatments can agree on a repeat while the two editions
still disagree about its literal representation. Fixed cases at `f4r.2` and
`f2r.10` demonstrate that source fact; the image windows make the differing
starts and similar neighboring structures inspectable. No glyph or source
reading is adjudicated. The paired `f1r.15` case supplies broad visible
correspondence for an encoded repeat agreed by both editions, with fading and
segmentation differences retained.

This pilot connects the accepted [distinct repeating-type count](REPEATING_TYPES.md)
to source/image questions. It selects **one adjacent event within a native
locus**, whereas the accepted statistic counts each repeating representation
once across the entire cohort. The three cases cannot estimate type accuracy,
repeat prevalence or a decipherment mechanism.

## Frozen selection and source accounting

The [plan](IMMEDIATE_REPEAT_IMAGE_PLAN.md) was committed at `f3fcc9f`, and the
synthetic-tested selector at `b48848a`, before its first manuscript run.
The [selection and complete audit](immediate_repeat_image_selection.json) were
committed at `d447e3d` before selected image inspection. The [prior-packet scope
inventory](IMMEDIATE_REPEAT_IMAGE_COVERAGE.md) and [page-exposure note](IMMEDIATE_REPEAT_IMAGE_EXPOSURE.md)
retain known overlap. These are local exploratory records, not independent
preregistration or an untouched evaluation.

All **3,884** accepted shared present P0 loci remain in the audit. Original slot
positions and null exclusions are retained. Eight source/policy slot digests,
total equal-adjacent event counts and globally distinct repeating-type counts
match accepted `repeating_types.json` exactly. There are **288** loci with a
repeat in at least one treatment and **3,596** with none. Those are locus counts;
a locus can contain several events/types.

Image-candidate filters exclude **993** loci, with all overlapping failure
reasons retained. Of the other **2,891**, **157** have one event of the same
literal type in every treatment, **12** have one stable ZL-only event, and
**23** have one stable IT-only event. The remaining **2,699** include zero,
multiple, policy-sensitive or type-discordant event patterns. These counts
describe a restricted selection rule, not all source disagreements or repeats.
Numeric folio/locus order selects the first case in each group:

| Group | Fixed locus | ZL3b native evidence | IT2a native evidence |
| --- | --- | --- | --- |
| Paired agreement | `f1r.15,+P0` | `...kol.chol.chol.kor.chal` | Same terminal sequence |
| ZL-only | `f4r.2,+P0` | `dchor.shol.shol.cthol...` | `dchor.chol.shol.cthol...` |
| IT-only | `f2r.10,+P0` | `...keol.saiin.e'a'iin` | `...keol.saiin.saiin` |

All eight treatments retain every apparent slot in these selected loci. They
do not contain uncertain commas or bracket alternatives. Joining uncertain
commas cannot reconcile fixed literal reading or period-boundary differences
between editions. Apostrophes, `{ck}` and `@163;` remain native notation rather
than inferred manuscript punctuation, phonetic symbols or adjudicated glyphs.

Complete native source records, physical source-file line numbers, alphabets,
inherited variables, preceding/following records, token arrays and event
coordinates are preserved. Even the paired case has different slot coordinates:
ZL's `chol` event is at zero-based slots **7–8**, IT's at **6–7**, because earlier
portions are segmented differently. Agreement of the repeated string does not
establish agreement of every encoded boundary.

## Source-informed image observations

The [machine-readable review](immediate_repeat_image_review.json) separates
direct observations, proposed source-row correspondence, neighboring placements
and contradictions. All placements are **provisional**, with source preference
unresolved. Whole-page context and block windows were inspected before smaller
details. Rectangles use native pixels, upper-left origin; they are review
windows rather than glyph/word masks.

- **1r, proposed f1r.15:** in the fifth main writing row of the third block,
  two neighboring groups share a broad horizontal cap, rounded mark and curving
  terminal stroke. One is fainter, and small contours differ. The opening and
  relative sequence broadly fit the known row and differ from its neighbors.
  This is compatible with `chol.chol`, without establishing exact glyph equality
  or word divisions. Green staining, fading and nearby strokes remain visible.
  [Whole image](https://collections.library.yale.edu/catalog/2002046?child_oid=1006076),
  [block](https://collections.library.yale.edu/iiif/2/1006076/400,1370,2200,950/full/0/default.jpg),
  [wider detail](https://collections.library.yale.edu/iiif/2/1006076/1400,1770,900,260/full/0/default.jpg).
- **4r, proposed f4r.2:** the second main upper writing level has two early
  neighboring groups with similar low capped, rounded and curving elements.
  A small curved upper trace is clearer above the second; the first area is
  faint and mottled. The opening and longer sequence before the plant broadly
  fit the known row, compared with taller neighboring starts. The upper trace
  is a concrete question for `shol.shol` versus `chol.shol`; its visibility does
  not adjudicate a `sh/ch` distinction.
  [Whole image](https://collections.library.yale.edu/catalog/2002046?child_oid=1006082),
  [block](https://collections.library.yale.edu/iiif/2/1006082/300,380,1950,480/full/0/default.jpg),
  [detail](https://collections.library.yale.edu/iiif/2/1006082/520,500,700,220/full/0/default.jpg).
- **2r, proposed f2r.10:** two terminal groups on the right of the stem at the
  third lower-block writing level share short upright/slanting runs and curved
  endings, with different left-hand traces and elevated small marks. The left
  opening and right capped sequence broadly fit the known source context; the
  adjacent levels end differently. Similar endings coexist with differing
  starts at the `saiin.saiin` versus `saiin.e'a'iin` disagreement. This does not
  establish equality of full glyph sequences.
  [Whole image](https://collections.library.yale.edu/catalog/2002046?child_oid=1006078),
  [block](https://collections.library.yale.edu/iiif/2/1006078/300,2370,2150,640/full/0/default.jpg),
  [detail](https://collections.library.yale.edu/iiif/2/1006078/1930,2510,600,310/full/0/default.jpg).

Plant-interrupted writing and native `<->` notation must not be converted into
independently verified continuous physical rows. Native locus numbers identify
records rather than count visible writing rows.

## Validation and next review

Standard library, Python 3.10 or later. From the repository root:

```sh
python3 -m unittest discover -s tests -p 'test_immediate_repeat*.py'
python3 scripts/select_immediate_repeat_images.py \
  --check research/transliteration/immediate_repeat_image_selection.json
python3 scripts/verify_immediate_repeat_images.py
```

All **14** targeted tests pass, covering interrupted/overlapping events, numeric
ordering, source/policy/canvas failures, complete case coverage, strict
provisional status, region bounds, source URLs, missing/mutated receipts and
output aliases introduced during construction/serialization. Accepted
selection/count replay passes. All **13** inspected local files also match
recorded byte hashes, dimensions and URLs using the optional
`--image-dir /path/to/local/receipts` check. The verifier reads JPEG dimension
headers; it does not decode image semantics or validate visual judgments.

A separate original-coordinate source calculation, sharing the accepted lexer
but none of the new selector helpers, matches every event list, zero-event key,
candidate group, selected key and excluded-union count in all eight treatments.

Files were retrieved and inspected on 2026-10-12. Current IIIF native dimensions
match the saved index: 1r **2972×3766**, 4r **2682×3740**, 2r **2691×3770**.
Public metadata and every inspected derivative have their own hash/size/time
receipts. Downloaded pixels remain outside the repository; the contribution
publishes Yale links and original notes.

Both readings and repeat classifications were known before inspection. Earlier
whole-page inventories already exposed 1r and 2r; other exposure is not ruled
out for 4r. This is nonblind AI observation, not blinded or independent human
review. Next, another observer should inspect all three complete rows and
neighboring placements, preserving contradictions, before any authoritative
mapping or glyph decision. No source correction, accuracy ranking,
decipherment or translation is supplied.
