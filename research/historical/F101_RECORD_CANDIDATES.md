# Four fixed comparisons of unmatched f101 identifiers

Historical H `f101r1` and modern IT2a `f101r` have the same ordered list of
**10 nonempty lowercase record projections**. H `f101v2` and IT2a `f101v` have
the same ordered list of **28**. The two opposite-side comparisons share **no
nonempty projection group**. These findings narrow a source-identifier question
while leaving all four page names unmatched in the accepted exact-page audit.
They establish no accepted page alias, physical surface, glyph reading or
translation.

The [fixed plan](F101_CANDIDATE_PLAN.md) and [machine declaration](f101-candidate-plan.json)
were published at `1e7b6a5ac2aa510b4652eafb050248a795992770` before this matrix
was calculated. The implementation and eight synthetic tests were committed at
`3cc47f7` before the first real calculation. This verifies committed chronology;
it is not an independently authenticated execution history or preregistration.
The four unmatched IDs, earlier aggregate results, full source material and
selected previous records were already exposed. There is no untouched evaluation.

## Sources and method

The [complete report](f101-record-candidates.json) uses the same pinned historical
1.6e6 H and modern IT2a bytes as accepted [PR #135](https://github.com/tobrien6/voynich-manuscript-research/pull/135).
Its accepted parent report has SHA-256
`161734c02648c5dfa0bf09dc91ed26bf8c3113a378317ef870f13d66c9dcb6e9`.
All eleven frozen dependencies are checked before the complete parent is
reproduced from its original sources. The parent's 223 exact shared pages and
four unmatched names remain unchanged. No pending H/Reddy work is imported.

Apply the accepted source-specific projection independently to each native body:
remove historical human comments or modern human comments/defined metadata, then
retain ASCII a–z. Case, uncertainty, spacing, punctuation and other notation are
lost within each record. Compare exact strings before serializing hashes; reject
a hash collision between distinct strings. Preserve record order, multiplicity,
native identifiers, source-file lines, units/kinds and empty projections. Empty
projections do not supply positive matches. All four selected pages happen to
have only nonempty projections in these pinned sources.

Every pair in the fixed two-by-two family is retained. The report lists all
shared and one-sided groups, with every native descriptor, length and digest.
Duplicate groups would remain ambiguous without position-based pairing. No
source bodies or projected strings are copied. These comparisons are independent
calculations on related editions, not independent manuscript observations.

## Complete matrix

| Historical H page | Modern IT2a page | Native/nonempty records H / IT2a | Ordered lists equal | Multisets equal | Joined streams equal | Symbol frequencies equal | Shared groups / one-to-one groups |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `f101r1` | `f101r` | 10 / 10 | Yes | Yes | Yes | Yes | 10 / 10 |
| `f101r1` | `f101v` | 10 / 28 | No | No | No | No | 0 / 0 |
| `f101v2` | `f101r` | 28 / 10 | No | No | No | No | 0 / 0 |
| `f101v2` | `f101v` | 28 / 28 | Yes | Yes | Yes | Yes | 28 / 28 |

The recto-named lists contain 1,012 projected letters each; the verso-named
lists contain 1,025 each. Each agreeing pair's groups are unique within its two
selected source pages. This uniqueness is limited to the lossy projection and
selected pages; it does not establish uniqueness across the manuscript or full
native-body equality. Both nonagreeing comparisons preserve all one-sided groups.
There are 114 emitted groups across the four comparisons; these repeated uses
of the same records are not 114 independent observations.

Native structure remains visible: H `f101r1` has ten `P` envelopes, and IT2a
`f101r` has ten `P0` loci. H `f101v2` has nine `R1`, nine `R2`, nine `P` and one
`T` envelope; IT2a `f101v` has eighteen `Lf`, nine `P0` and one `Pc` locus.
These are source unit/kind labels, not verified physical rows or regions.

| Source page | First selected native locator and file line | Last selected native locator and file line |
| --- | --- | --- |
| H `f101r1` | `f101r1.P.1;H` — member line 32821 | `f101r1.P.10;H` — member line 32851 |
| H `f101v2` | `f101v2.R1.1;H` — member line 33179 | `f101v2.T.9;H` — member line 33411 |
| IT2a `f101r` | `f101r.1,@P0` — export line 4197 | `f101r.10,+P0` — export line 4206 |
| IT2a `f101v` | `f101v.1,@Lf` — export line 4208 | `f101v.28,+Pc` — export line 4235 |

The [historical catalog](../../data/historical/interlinear-16e6.json) identifies
the archive/member; the [modern catalog](../../data/transliterations.json)
identifies the export. Credit Jorge Stolfi, Gabriel Landini, Jim Reeds, Takeshi
Takahashi, other interlinear contributors and modern publisher René Zandbergen.
Existing [source terms](../../data/historical/README.md) govern reuse. Equality
to any original historical-paper input remains unproven. No manuscript images
are inspected or redistributed in this contribution.

## Reproduce and limits

Python 3.10+, standard library only, from the repository root:

```sh
python3 scripts/audit_f101_record_candidates.py --check research/historical/f101-record-candidates.json
python3 scripts/audit_f101_record_candidates.py --output /tmp/f101-record-candidates.json
python3 -m unittest tests.test_f101_record_candidates tests.test_historical_record_projections -v
```

Nine focused tests plus eleven accepted parent tests pass. Before real
calculation, eight tests covered all four names/comparisons, 225 exhaustive small
sequence pairs, permutation/split losses, duplicates/empty denominators, collision
failure, strict plan flags/pins and 90 direct/early/late alias cases across 18
protected paths. Check-target aliases and serialization-time aliases preserve
inputs too. Complete checks distinguish Boolean/integer/float JSON values and
reject duplicate keys and nonfinite values. A failed check preserves a separate
output. Guards run before calculation and after serialization; no atomic
filesystem guarantee is claimed.

An independently written raw ZIP/export scanner imports neither production
readers nor the projection function. It reconstructs the parent across all
10,428 selected records and 227 union pages, then verifies all 76 selected f101
records, four profiles and complete four-pair group/flag results, including file
lines and digests. The parent report and eleven frozen files remain byte-identical.

Every candidate's alias/crosswalk flag stays false; the report's physical image
mapping and statistical evaluation flags stay false. No source correction,
accuracy ranking, global suffix-removal rule or source-defined corpus join is
introduced. The [publisher convention and shared scan context](F101_CONTAINER_CONTEXT.md)
now records the modern file containers and all three inherited Yale references.
Physical correspondence still needs reviewed original native bodies, related
panels and precise regions before these similarities can become a mapped corpus.
