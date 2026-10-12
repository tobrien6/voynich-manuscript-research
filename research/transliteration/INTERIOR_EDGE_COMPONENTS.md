# Early, crossing and late contributions to interior order

The accepted half-centered departure extends inside both halves of the encoded
interior sequence. In the primary ZL3b split ASCII treatment, early-half edges
contribute **+0.02622437**, the single crossing pair **+0.01954377**, and late-half
edges **+0.02156168**, summing to the accepted **+0.06732982**. The two within-half
components together contribute +0.04778605. All 72 aggregate components across
four source/spacing treatments, three operational counts and both centering
scopes are positive. These signs are descriptive; no component tail or test
criterion has been calculated.

This exact decomposition of the [existing order](INTERIOR_ORDER.md),
[half constraint](INTERIOR_HALVES.md), [unit sensitivity](INTERIOR_UNITS.md) and
[joint-moment report](INTERIOR_COVARIANCE.md) keeps all **2,165** common P0 loci.
It locates the existing effect, while retaining finer positional structure,
transcription conventions and other production processes as possible explanations.
It does not establish direct neighbor dependence or a decipherment.

## What the components mean

The early half contains ceil(m/2) original interior slots and the late half the
remainder. Early and late components contain only adjacent edges inside their
respective halves; the bridge contains the single crossing pair. For m=3 the
late component has no edges and is exactly zero. Constants and all such zero
contributions remain in the full equal-locus denominator.

Every component uses the **original whole-locus association scale**, calculated
from all interior counts. None is separately divided by its number of edges or
its own variance. The signed component values therefore add exactly to the
accepted statistic; they are not three independently normalized correlations.
The arbitrary midpoint is encoded position bookkeeping, not an adjudicated
manuscript or paragraph boundary. Counts remain the three declared notation maps,
not physical glyphs or linguistic words.

The [plan](INTERIOR_EDGE_COMPONENTS_PLAN.md) specifies the integer-scaled
association and its exact expected components. Under unrestricted permutations
all interior edges have the same expectation. Under independent half permutations,
within-half expectations sample distinct ordered occurrences from the same block;
the bridge samples one occurrence independently from each block. Repeated values
retain their occurrence multiplicities. Subtract each component's own expectation
before equal-locus averaging. These components reassemble both old centered totals.

## Complete aggregate components

Values are rounded to eight decimals. Exact raw, expected and centered triplets,
all 25,980 locus/policy records, centering shifts and 48 grouped-minus-ASCII
component differences are in the [complete gzip report](interior_edge_components.json.gz).
Lossless compression reduces the 18,136,079-byte first JSON to 803,501 bytes;
decompression recovers every original byte, with no scientific or provenance
revision. The pinned producer still creates/checks plain JSON. The independent
checker reads either form, and the local expanded file is excluded from Git.
Each table's entries use the same full 2,165-locus denominator. IT split/join
coincide and remain related sensitivity views, rather than independent replications.

### Unrestricted centering

| Source / spaces | Count policy | Early | Crossing | Late | Accepted total |
| --- | --- | ---: | ---: | ---: | ---: |
| ZL3b / split | ASCII | +0.03755838 | +0.01607397 | +0.03542959 | +0.08906193 |
| ZL3b / split | Bench | +0.02456796 | +0.00988417 | +0.02888913 | +0.06334126 |
| ZL3b / split | Bench/minim | +0.03792214 | +0.01324362 | +0.04177654 | +0.09294230 |
| ZL3b / join | ASCII | +0.02358629 | +0.01243994 | +0.02064816 | +0.05667439 |
| ZL3b / join | Bench | +0.01123457 | +0.00821570 | +0.01362831 | +0.03307857 |
| ZL3b / join | Bench/minim | +0.02454338 | +0.01090931 | +0.02669894 | +0.06215164 |
| IT2a / split | ASCII | +0.02966937 | +0.01588519 | +0.03355941 | +0.07911396 |
| IT2a / split | Bench | +0.01709655 | +0.00649619 | +0.02562023 | +0.04921296 |
| IT2a / split | Bench/minim | +0.03258307 | +0.01223410 | +0.03974046 | +0.08455763 |
| IT2a / join | ASCII | +0.02966937 | +0.01588519 | +0.03355941 | +0.07911396 |
| IT2a / join | Bench | +0.01709655 | +0.00649619 | +0.02562023 | +0.04921296 |
| IT2a / join | Bench/minim | +0.03258307 | +0.01223410 | +0.03974046 | +0.08455763 |

### Half-constrained centering

| Source / spaces | Count policy | Early | Crossing | Late | Accepted total |
| --- | --- | ---: | ---: | ---: | ---: |
| ZL3b / split | ASCII | +0.02622437 | +0.01954377 | +0.02156168 | +0.06732982 |
| ZL3b / split | Bench | +0.01764351 | +0.01242426 | +0.01629136 | +0.04635914 |
| ZL3b / split | Bench/minim | +0.02370081 | +0.01753754 | +0.02421467 | +0.06545302 |
| ZL3b / join | ASCII | +0.01655126 | +0.01400414 | +0.01423667 | +0.04479207 |
| ZL3b / join | Bench | +0.00915047 | +0.00805063 | +0.00928883 | +0.02648993 |
| ZL3b / join | Bench/minim | +0.01553757 | +0.01306730 | +0.01631059 | +0.04491546 |
| IT2a / split | ASCII | +0.02200558 | +0.01906046 | +0.02131233 | +0.06237837 |
| IT2a / split | Bench | +0.01403263 | +0.00835457 | +0.01486193 | +0.03724913 |
| IT2a / split | Bench/minim | +0.02240689 | +0.01570054 | +0.02253595 | +0.06064338 |
| IT2a / join | ASCII | +0.02200558 | +0.01906046 | +0.02131233 | +0.06237837 |
| IT2a / join | Bench | +0.01403263 | +0.00835457 | +0.01486193 | +0.03724913 |
| IT2a / join | Bench/minim | +0.02240689 | +0.01570054 | +0.02253595 | +0.06064338 |

Moving to half centering lowers each early/late aggregate contribution. Its
bridge contribution increases in eleven of the twelve treatments, including
primary ASCII (+0.00346981), but decreases by 0.00016507 for ZL3b join bench.
The full-to-half decrease of the total therefore cannot be read as a uniform
attenuation of every part of the sequence. The bridge exception and all signed
policy differences remain in the report. These arithmetic shifts describe
changed conditional expectations; they are not causal fractions explained by
layout. The accepted total finite-control tails remain attributed parent facts
and are not assigned to individual components.

## Publication and independent verification

The plan was pushed and remote-verified at
`0d6aa9e17530b2ab772859cc67ac4c9aa52e0e7d`. The tested implementation and
[24-entry manifest](interior-edge-component-pins.json) were pushed and remote-
verified at `83291c568c10d48566a38bbcdc3c836194aad090` before the new component
measurements. **62 relevant tests** passed beforehand, including eleven new
regressions. Four subsequent independent-checker/transport regressions bring the
total to **66**. No source, count map, accepted effect, old array, seed or trial changed.
No new permutation draw, component probability, generator run or fitted parameter
was introduced.

- Producer SHA-256: `6e94f6e809f88a3b487d2aa6aab2e33e75d939b72b742a5e95743b2c960566d2`.
- Manifest SHA-256: `923773ef90fdfefdeb52dce5934bf12ff1ec3b8b9704504eaf7b8fb50e5e32e6`.
- Report SHA-256: `67931c2d041084a6bf85aea40f001855e7ae245d0831b2f1087d57356b890caa`.
- Gzip transport SHA-256: `c5d53510f799bb4c90a2019868c159687f75c695c0eb6c40baacca0cbc06d88d` (mtime zero, no filename header).

Complete occurrence enumeration on small synthetic vectors checks each separate
component expectation under both scopes, including repeated values, constants,
odd/even sizes and a singleton late half. Other tests check exact additivity,
affine invariance, full equal-locus weighting, paired changes, centering-shift
signs, malformed counts, missing/duplicate identities, altered parent means and
effects, typed cache replay, exclusive creation and direct/symbolic/hard/parent-
redirect aliases, including an alias introduced during serialization. A 9,001-
digit aggregate roundtrips without changing interpreter or Decimal settings.

The separate [checker](../../scripts/verify_interior_edge_components.py) uses the
established native adapter only for ingestion. Its own literal longest-match
scanner rebuilds all twelve count-vector fingerprints. Independent eligibility
accounting reproduces the entire 2,165 retained/1,719 excluded locus ledger.
Expected edge products come from direct sums over distinct ordered occurrences,
without production component, centering or aggregation functions. It verifies
**233,820** exact locus component values, all **216** aggregate values and **48**
paired component differences, plus all **51,960** accepted locus null means and
24 exact centered totals. Complete producer replay matches the saved report.

For the recorded Python 3.14.3 runtime, standard library only:

```sh
gzip -dk research/transliteration/interior_edge_components.json.gz
python3 scripts/interior_edge_components.py \
  --check research/transliteration/interior_edge_components.json
python3 scripts/verify_interior_edge_components.py
python3 -m unittest tests.test_interior_edge_components \
  tests.test_independent_interior_edge_components
```

Use `--new-report NEW_PATH.json` for an exclusive new output. Native sources,
code, settings, plans and accepted reports are protected before calculation and
again after complete serialization. Existing outputs and input aliases are
refused. Exact fractions use decimal pairs locally and labelled base-16 integers
for aggregates; display decimals are separately rounded. No raw transcription,
source image, third-party generator payload or private local path is published.

## Limits and next test

These are sums of signed conditional deviations on exposed encoded rows. The
positive within-half components show that the aggregate surviving departure is
not confined to the single bridge. They supply no component uncertainty or new
rejection claim, and related count policies are not independent evidence. Neither
physical-line correspondence, actual glyph units nor a linguistic interpretation
has been established.

A further experiment still needs a justified finer position model, registered
controls and evidence that those controls retain enough permissible variation.
An explicit mechanism or proposed reading additionally requires prospective,
source-linked predictions and an exposure-valid evaluation under the
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md). Locating an existing order
effect does not validate a language, cipher or translation.
