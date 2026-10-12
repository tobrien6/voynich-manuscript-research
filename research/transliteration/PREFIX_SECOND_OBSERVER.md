# Second AI inspection of two initial-prefix disagreements

This separate inspection supports the proposed row matches for `f18v.5` and
`f78r.21`. It provisionally agrees with the first observer's `l` comparison at
`f78r.21`; at `f18v.5`, it supports the compact initial cluster while leaving
its internal glyph segmentation unresolved. Neither result authorizes changing
a source, selecting a canonical reading, or applying a correction to statistics.

## Method and exposure

The [plan](PREFIX_SECOND_OBSERVER_PLAN.md) was committed at `33e400b` before
this observer inspected the image pixels. The observer had already read the
[first review](INITIAL_PREFIX_IMAGES.md), its preferences and source metadata.
This is **nonblind, separate AI inspection**, not independent human adjudication,
independent manuscript evidence or an untouched evaluation.

Keep exactly the two accepted cases and the `f78r.4`/`f78r.43` references.
Read their native neighboring records from the pinned ZL3b/IT2a editions;
inspect each full Yale image before its context and initial regions, and then
inspect both reference regions. Consult the publisher's
[Basic Eva shape table](https://voynich.nu/img/extra/eva01.gif), linked from its
[transliteration description](https://voynich.nu/transcr.html), solely as a
notation reference. No pronunciation or meaning is inferred.

All eleven downloaded images (two full pages, eight declared regions and the
shape table) match the first record's hashes and dimensions. The
[inspection record](prefix_second_observer.json) pins the original selection,
first review, plan, source catalog and canvas index; retains both editions and
spacing policies; and identifies every inspected derivative. Full-page views
were displayed at reduced size for layout; all eight region views were displayed
at their native pixel dimensions. Pixels remain local and are not redistributed.

## f18v.5: row correspondence and segmentation limit

[Yale image 1006109, 18v](https://collections.library.yale.edu/catalog/2002046?child_oid=1006109)
shows one text block at upper right beside the plant drawing. The declared
[context region](https://collections.library.yale.edu/iiif/2/1006109/1400,650,1300,380/full/0/default.jpg)
retains the relevant rows. The proposed target lies between the row with the
repeated tall forms represented as `qotchy.qokay.qokchy` at `f18v.4` and the
row beginning `qotor` at `f18v.6`. The target's next tall form and subsequent
short/tall sequence are consistent with the paired native records. This supports
the proposed match beyond merely counting to locus five; it does not adjudicate
the complete row's spelling.

In the [initial region](https://collections.library.yale.edu/iiif/2/1006109/1250,770,650,140/full/0/default.jpg),
there is a short dark curved mark at the upper left of the initial cluster,
beside a larger curved stroke which continues downward and bends left. The
cluster is followed by lower connected forms. The retained margin shows no
clearly separated extra word-sized group before it.

The overall cluster resembles the Basic Eva `y` reference, but the small
adjacent mark matters: this view cannot establish whether the marks form one
sign, a composite sign, or the sequence motivating IT's `r.y` representation.
A gap between strokes is not by itself a word boundary. ZL starts `ychoees`;
IT starts separate tokens `r` and `ychoees`, so the disagreement concerns first
slot presence/segmentation as well as a literal prefix feature.

This inspection therefore supports the **row match** and a **compact initial
cluster**, while leaving the `r`-token segmentation unresolved. It gives less
definite support to a first-slot preference than the earlier prose. Neither
edition is selected as a corrected source. A qualified reviewer should assess
stroke connection and the segmentation convention at the original resolution,
with comparable `r`/`y` forms, before a versioned decision.

## f78r.21: provisional l comparison reproduced

[Yale image 1006214, 78r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006214)
has a long left text block beside circular illustrations. The
[target context](https://collections.library.yale.edu/iiif/2/1006214/310,1550,1000,310/full/0/default.jpg)
contains the short preceding row represented as `f78r.20`, the target with a
second tall-starting group represented as `qokain`, and the following row
beginning with a curved `y`-like form at `f78r.22`. Their lengths and neighboring
shape sequences support the proposed match. Labels elsewhere on the page
prevent treating a locus number as the same numbered physical paragraph row.

The [target beginning](https://collections.library.yale.edu/iiif/2/1006214/350,1650,700,130/full/0/default.jpg)
has a compact closed/crossed upper part and a short oblique stroke descending
left. The next token has a longer, more vertical descending stem. These are
visible geometric differences, not a glyph-family definition.

The declared [l reference context](https://collections.library.yale.edu/iiif/2/1006214/300,2920,1250,390/full/0/default.jpg)
ends the left block beside the lower illustration. Its preceding two rows and
the second tall-starting group support the proposed `f78r.43` match; the
[initial region](https://collections.library.yale.edu/iiif/2/1006214/350,3090,750,180/full/0/default.jpg)
shows a compact loop with an oblique descending stroke. The declared
[q reference context](https://collections.library.yale.edu/iiif/2/1006214/310,430,1280,250/full/0/default.jpg)
retains the opening paragraph rows. The paired neighboring sequence supports
`f78r.4`, whose [initial region](https://collections.library.yale.edu/iiif/2/1006214/340,530,620,120/full/0/default.jpg)
shows a more extended, near-vertical stem.

Along these specified features, the disputed first sign is closer to the
selected `l` reference than to the selected `q` reference. This reproduces the
earlier **provisional** preference for ZL's literal `l` over IT's literal `q`.
Source agreement at either reference does not establish glyph ground truth,
and one pair does not characterize handwriting variation. ZL's later `[a:o]`
alternative at `f78r.43` remains intact; the reference still fails the whole-locus
adapter rule and is not added to the original analysis cohort.

## Validation and next test

The existing selector and review verifier reproduce the accepted case/reference
identities. Local bindings of all eleven inspected files pass their hash and
bitmap-dimension checks. The new record's input/plan pins, case order, copied
selection metadata, reference identities, region bounds, and provisional-only
flags were checked separately. These checks identify the inputs and restrict
their use; they cannot certify the visible-stroke judgments or row matches.

Recheck the stored input identities and the accepted selection/reference record
offline from the repository root:

```sh
python3 scripts/select_initial_prefix_images.py --check research/transliteration/initial_prefix_selection.json
python3 scripts/verify_initial_prefix_review.py
python3 - <<'PY'
import hashlib, json
from pathlib import Path
record = json.loads(Path('research/transliteration/prefix_second_observer.json').read_text())
for path, digest in record['input_pins'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
for flag in ('blinded', 'independent_human_adjudication', 'may_apply_as_source_correction',
             'apply_to_statistics', 'verified_glyph_ground_truth'):
    assert record[flag] is False, flag
print('Input identities and provisional-only flags match the recorded inspection.')
PY
```

The two cases are selected disagreements on related representations of the
same manuscript, not a random accuracy sample. Keep the f18v segmentation
question open and retain the f78r comparison as provisional. Independent human
region/glyph review remains pending. Any future correction needs a separately
reviewed versioned decision retaining both original readings and contradictions.
No glyph inventory, decoding rule, or translation is established here.
