# Minimal shared-anchor boundary spans

The accepted [boundary audit](TOKEN_BOUNDARY_CONCORDANCE.md) identifies whole
native loci with identical encoded strings but different token boundaries.
This inventory exposes the smaller encoded regions where those boundaries
disagree. It gives **650 spans across 562 loci under split** and **978 spans
across 767 loci under join**, preserving all disagreement locations and both
source partitions. A locus can contain several spans.

Each span lies between consecutive offsets shared by both editions, including
the common locus endpoints. It is minimal with respect to those shared anchors,
not a smallest physical word or glyph region. Its source pieces are original
complete tokens; the method introduces no partial-token cuts.

## Method and input identity

Reuses the pinned ZL3b/IT2a sources, `plain-eva-v1`, and the accepted common cohort
of **2,940 P0 native keys**. The parent report is verified against its complete
fresh source/implementation producer before extracting anything. Across both
policies, 2,054 keys have identical case-preserved ASCII chains; the other 886
keys remain explicitly unaligned. Identical partitions produce no span, rather
than a synthetic zero-change interval.

For an identical chain, take the intersection of the two internal boundary
offset sets and add endpoints `0` and `chain_length`. Sort the anchors. Within
each consecutive anchor interval, emit a record only when the source cuts
differ. Every shared internal cut would itself be an anchor, so all emitted
internal cuts are exclusive to one source. Slice the literal chain using each
source's original cuts. The result recovers that source's complete original
tokens between the anchors, without joining different native loci.

The [complete inventory](boundary_disagreement_spans.json) records all span
strings, absolute ASCII offsets, both source token partitions, signed token
differences, identifiers/file lines, source hashes, parent identity and code
pins. The existing [IVTFF/adapter conventions](TOKEN_ADAPTER.md) still apply.
Offsets are in the processed concatenated ASCII chain, not raw-file byte
coordinates, manuscript glyph counts, image pixels or phonetic units.
In records, `left` means ZL3b and `right` IT2a; it is not image orientation.

## Coverage and local structure

| Source cut pattern inside an emitted interval | Split spans | Join spans |
| --- | ---: | ---: |
| ZL-only internal cuts | 431 | 42 |
| IT-only internal cuts | 212 | 927 |
| Both sources have distinct internal cuts | 7 | 9 |
| Total | 650 | 978 |

Split has 482 loci with one span, 73 with two, six with three and one with four.
Join has 586 with one, 154 with two, 24 with three and three with four. These
totals recover all 562/767 parent disagreement keys exactly. The sum of local
ZL-minus-IT token differences is +239 under split and −943 under join, matching
the accepted [count accounting](BOUNDARY_COUNT_ACCOUNTING.md). These are the
same exposed cases represented locally, not additional manuscript samples.

Examples, with half-open ASCII intervals:

| Native key / policy | Interval | Literal span | ZL partition | IT partition |
| --- | --- | --- | --- | --- |
| `f67r1.1`, both | `[44,49)` | `oaiin` | `o` / `aiin` | `oaiin` |
| `f102r1.14`, both | `[37,40)` | `sor` | `s` / `or` | `sor` |
| `f102r1.15`, both | `[34,42)` | `ykeeykam` | `ykeeykam` | `ykeey` / `kam` |
| `f100r.24`, split | `[26,33)` | `yksheey` | `yk` / `sheey` | `yksheey` |
| `f100r.24`, both | `[33,43)` | `cholsheody` | `cholsheody` | `chol` / `sheody` |

The two `f100r.24` split spans have token differences +1 and −1, which cancel
at the ten-versus-ten locus level. They are separated by a shared encoded
boundary at offset 33. This local representation shows why equal total counts
need not identify one physical space that moved. The first span is absent
under join; the original uncertain comma is handled by the accepted policy.
The [67r](../panel-regions/67R_BOUNDARY_CASE.md) and
[102r](../panel-regions/102R_BOUNDARY_PAIR.md) image cases retain their own
provisional row associations; these intervals add no verified pixel masks.

## Separator and interpretation limits

Drawing interruptions remain adapter separators. Each span retains both
source **locus-level** comma and drawing-interruption counts, which do not locate
those markers inside this interval. `separator_types_within_span` is therefore
null. Do not interpret an encoded cut as a word space without separately
checking original notation and image context. Source comments and paragraph
markers are handled by the existing parser/adapter, rather than a new lexer.

`verified_glyph_region` remains null throughout. The original source/policy
dependencies, whole-locus exclusions, singleton/fragment inclusion and prior
exposure remain unchanged. No source correction, accuracy ranking, linguistic
word-span assignment, independent samples, inferential test, untouched
evaluation, decipherment or translation is introduced.

## Replay and verification

```sh
python3 scripts/boundary_disagreement_spans.py --check research/transliteration/boundary_disagreement_spans.json
python3 scripts/boundary_disagreement_spans.py --output /tmp/boundary-disagreement-spans.json
python3 -m unittest tests.test_boundary_disagreement_spans -v
```

Nine tests cover identical/singleton chains, rejection of different strings or
case, original complete-token partitions, common-anchor context removal, both
sources' distinct cuts, opposite local contributions that cancel, all **1,024**
pairs of six-letter partitions, exact native examples and complete inventory
replay. Initial and post-serialization symlink/hardlink output guards protect
the parent, catalog, sources and implementation paths. A regression creates
aliases during calculation or serialization and verifies the parent remains byte-identical.
The final guard is repeated immediately before writing, with no atomic
filesystem-transaction claim.

Next, use these source-linked intervals to plan specific glyph/region reviews.
Their shared anchors are agreement between related encodings, rather than
independent physical evidence. A candidate segmentation rule still needs
frozen predictions and exposure-valid tests under the
[evaluation protocol](../DECIPHERMENT_PROTOCOL.md).
