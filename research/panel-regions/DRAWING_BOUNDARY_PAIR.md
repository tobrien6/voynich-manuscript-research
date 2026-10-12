# Two drawing-notation boundary cases

The [complete native separator ledger](../transliteration/BOUNDARY_SEPARATOR_PROVENANCE.md)
has two disputed offsets involving drawing notation. What physical context can
be proposed for each while preserving both source alternatives? This records
both attempts, provisional row placements and all source requests. It assigns
no preferred transcription, verified glyph region or physical word boundary.

The prerequisite is [PR #196](https://github.com/tobrien6/voynich-manuscript-research/pull/196),
published head `8b9771bc7af7517caf1af4a79204a99062e056a2`. This is a separate
dependent draft until that contribution is accepted and its integration is
reviewed. It does not change the held span/viewer contributions or their fields.

## Frozen source packet and selection

The [plan](drawing-boundary-pair-plan.json) and
[complete source-context packet](drawing-boundary-pair-source-context.json)
were committed and pushed at `2d38762344509d19d37db08d199706192af6e06b`
before this contribution's image requests and views. The rule retains **every**
offset whose left or right native marker is `<->` or `<~>` in the 1,458-offset
union-disagreement ledger. Exactly two match: `f13v.8`/30 and `f75r.44`/48.
Source letters, full inventories and prior work were already exposed. This
publication chronology is author-reported, without an independently observed
freeze or untouched-evaluation claim.

The packet retains all twelve immediate-neighbor native readings, all 24
source/policy adapter records, page variables, complete P0 identifier orderings,
source editions/hashes, original file lines, target ranks and every selected
separator field. Neighbor differences and ZL's ambiguous `f13v.7` remain visible.
The ZL/IT inputs and CC0 credits follow the [accepted catalog](../../data/transliterations.json).

| Target | Native counts in each source | Target P0 rank | Yale carrier | Dependency group |
| --- | --- | ---: | --- | --- |
| `f13v.8` | 10 loci, all 10 present P0 | 8 | [1006099, label 13v](https://collections.library.yale.edu/catalog/2002046?child_oid=1006099) | `yale-leaves:13` |
| `f75r.44` | 53 loci, 46 present P0 | 44 | [1006208, label 75r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006208) | `yale-leaves:75` |

Both exact-side metadata associations are retained from the accepted index.
They do not certify physical row or glyph joins. Live service metadata matches
the frozen native dimensions: 13v is 2,812×3,770 and 75r is 2,852×3,759.

## Source-informed image observations

On 13v, the carrier shows two five-row text blocks around a plant drawing.
The target is provisionally the third row of the lower block. A slanted stem
separates its middle and right ink clusters. The right cluster begins with a
looped ink form, then a narrow blank interval and a taller stroke group. These
are broad visible shapes; their exact correspondence to source letters is
unverified.

The original sources already describe neighboring marker alternatives:
ZL has `...okchy.o,kald<->d,y,taiin`, while IT has
`...okchy.okald.d<->ytaiin`. At encoded offset 29 both sources cut under both
policies, but use different marker kinds (`<->` versus `.`). At selected
offset 30, ZL has a comma and IT has `<->`. An exclusive-cut ledger does not
record the marker-kind difference at their shared cut. A reviewer therefore
needs to adjudicate the stem/ink relationship around **both** adjacent positions,
without assuming that shared cuts already identify the same drawing boundary.

On 75r, the target is provisionally the third-from-bottom row of the lowest
15-row text block, matching source P0 rank 44/46. A right-hand figure's
ankle/foot outline reaches the broad writing band near the candidate locus end
and continues below it. Exact stroke ownership near the source alternatives
remains unresolved. ZL ends `...olaiin.ch<->dar.dy`; IT ends
`...olaiin.chdar.dy`. A source's decision to join or divide these pieces is
preserved without treating the nearby outline as certified word separation.

Both regions are proposals informed by source strings and order. The windows
include adjacent text and illustration strokes, and are not glyph masks. No
new glyph transcription, image-assigned word, data correction, source ranking
or statistical inclusion is made. Independent confirmation remains pending.

## Complete request and exposure record

The [observation record](drawing-boundary-pair-review.json) preserves all URLs,
native rectangles, returned JPEG dimensions, byte counts, SHA-256 identities,
service metadata pins, viewing order and unresolved status. One whole carrier,
one adaptive block and one native-resolution detail were used per case. All six
image and two metadata requests succeeded. No rotation, replacement target,
additional leaf, extra image or additional viewing-tool resize was requested.

| Case/view | Native viewing rectangle x,y,w,h | Returned dimensions | Bytes |
| --- | --- | --- | ---: |
| [13v whole](https://collections.library.yale.edu/iiif/2/1006099/full/!1800,1800/0/default.jpg) | whole carrier | 1343×1800 | 630571 |
| [13v lower block](https://collections.library.yale.edu/iiif/2/1006099/650,2210,1900,600/1500,/0/default.jpg) | 650,2210,1900,600 | 1500×473 | 199870 |
| [13v detail](https://collections.library.yale.edu/iiif/2/1006099/1860,2400,620,330/full/0/default.jpg) | 1860,2400,620,330 | 620×330 | 57613 |
| [75r whole](https://collections.library.yale.edu/iiif/2/1006208/full/!1800,1800/0/default.jpg) | whole carrier | 1366×1800 | 651525 |
| [75r lower block](https://collections.library.yale.edu/iiif/2/1006208/330,2800,2250,550/1600,/0/default.jpg) | 330,2800,2250,550 | 1600×391 | 158131 |
| [75r detail](https://collections.library.yale.edu/iiif/2/1006208/1820,2960,760,350/full/0/default.jpg) | 1820,2960,760,350 | 760×350 | 61947 |

The first-view clock reading was 12:47:31 UTC on 2026-10-12; the clock after the
six views read 12:53:25 UTC. This is an author observation log. After the whole
carriers and before block viewing, ZL's full 75r P0 prefixes/order were consulted
to understand its 26/5/15 text-block structure. This additional same-leaf source
exposure did not replace targets or introduce more image requests. Other project
inventories may have exposed these leaves earlier.

The JPEGs and full IIIF metadata responses remain local. Public access does not
establish an open image license; the packet publishes technical identifiers,
original observations, modern CC0 source context and links.

## Verification and next review

The complete parent separator ledger replays against its frozen accepted inputs.
The two-case predicate, all source-context rows/variables/token arrays and P0
orderings, exact canvas associations, input fingerprints, six image
hash/size/dimension triples, two metadata identities/dimensions and rectangle
bounds were checked. Every case retains null glyph/preference/correction fields
and false join/inclusion flags. These are data/observation files, without new
executable implementation or unit tests. Machine consistency cannot certify
the proposed physical rows or glyph readings.

Recheck the prerequisite with:

```sh
python3 scripts/boundary_separator_provenance.py --check research/transliteration/boundary_separator_provenance.json
```

The plan's six `input_sha256` entries identify every original selection/context
dependency. The review separately pins the unchanged plan/context bytes.
Source-file lines and linked windows allow a reviewer to inspect both original
alternatives. Live service or image changes require a recorded new response
rather than silent replacement of the published hashes.

An independently assigned reviewer should next confirm each full candidate row,
its neighbors and the ownership of strokes near the stem/foot, then compare all
adjacent source separator alternatives. Exact glyph boundaries and independent
agreement are needed before corpus-join readiness or any source correction.
Related editions, common imagery and prior exposure remain dependent evidence;
no untouched evaluation, language, decipherment or translation follows.
