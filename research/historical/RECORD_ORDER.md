# Native record order under the lossy projection

On the **29 equal-multiset pages with differing native order**, a maximum
order-preserving pairing retains **836 of 1,006 nonempty projected records**
per source. At least **170 slots per edition** must therefore remain unmatched
under that constraint. **Twelve pages have multiple maximum pairings**; the
[complete report](record-order.json) retains every possible index pair and
never chooses a convenient matching witness.

These are exact combinatorial quantities for already exposed source projections.
They do not identify physical manuscript rows, source errors, record moves or
deletions. Even a unique or mandatory projected-record pairing is not a verified
historical/modern locator alias, full-body match, glyph identity or word reading.

## Fixed sources and complete population

The [plan](RECORD_ORDER_PLAN.md) was published at
[`70920a9`](https://github.com/tobrien6/voynich-manuscript-research/commit/70920a96cce6fcbd7820b65741cea126a0f1ed2a)
before implementation and measurement of this statistic. The accepted
[record-projection audit](RECORD_PROJECTIONS.md), its 211/182/29 page split and
all 29 page IDs were already known, as were source bodies and earlier image
contexts. This is descriptive exposed-data follow-up, without untouched-test
or independently certified inspection-chronology claims.

Use the complete accepted parent report, SHA-256
`161734c02648c5dfa0bf09dc91ed26bf8c3113a378317ef870f13d66c9dcb6e9`.
It is checked against the pinned historical 1.6e6 archive/member, all native H
records, modern IT2a present loci and unchanged projection dependencies before
selecting pages. The producer reconstructs exact nonempty strings in each
source's original order, on exact page IDs, before digest serialization.
Empty projections retain every native descriptor and original page-order index
outside the matching population. The explicitly nonexistent modern envelope
and unmatched page names remain unchanged.

All **211 equal-multiset pages** are retained: 29 differing orders receive
complete pair inventories, and 182 equal-order controls have a full identity
index pairing with zero unmatched slots. All **16 excluded union pages** are
listed with their parent comparison flags. No aliases, exclusions or source
corrections are introduced. The report records each empty descriptor on both
selected populations, including historical `f106r.P.29;H` in an identity control.

Credits and reuse terms remain those of the
[historical data note](../../data/historical/README.md) and
[modern export catalog](../../data/transliterations.json): Jorge Stolfi and the
interlinear contributors, Takeshi Takahashi, and publisher René Zandbergen.
Historical-paper input identity remains unproven. The JSON publishes source
locators, file-line positions, lengths and digests, without projected body text.

## Quantity and complete optimal-pair support

For two equal-multiset nonempty sequences of size n, let L be their longest
common subsequence length under exact projected-string equality. L is the
maximum number of index pairs increasing in **both** source orders. Then n-L
is the minimum unmatched slots per edition, and 2(n-L) is the total across the
two source sequences. This sums source slots, not independent manuscript units.

Integer prefix and suffix LCS tables determine whether an equal pair (i,j)
can occur in a maximum pairing: prefix[i,j] + 1 + suffix[i+1,j+1] = L.
Each possible pair then has matched rank prefix[i,j] + 1. Every maximum pairing
uses one pair at each rank; a rank with just one possible pair makes that pair
mandatory. Multiple candidates are retained in full. The inventory is the union
of possible pairs, not one mutually compatible pairing containing all of them.

The 29 pages have **885 possible index pairs**, of which **800** are mandatory
under this conditional computation. There are 836 matched ranks in total;
36 ranks have multiple candidates. **17 pages have a unique maximum pairing**,
while 12 have more than one. Both reordering and repeated projections can create
multiple optimal choices. Repeated projected strings remain observationally
indistinguishable; source indices do not resolve their physical identity.

## Every order-different page

L and unmatched counts are per edition. “Possible” is the complete union of
index pairs on any maximum pairing; “Mandatory” is their intersection.

| Exact page | n | L | Unmatched | Possible | Mandatory | Unique maximum |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| f100r | 27 | 26 | 1 | 27 | 25 | No |
| f102r1 | 17 | 15 | 2 | 15 | 15 | Yes |
| f102r2 | 20 | 17 | 3 | 17 | 17 | Yes |
| f102v2 | 39 | 38 | 1 | 38 | 38 | Yes |
| f49v | 46 | 27 | 19 | 39 | 23 | No |
| f57v | 13 | 10 | 3 | 11 | 9 | No |
| f67r2 | 74 | 62 | 12 | 62 | 62 | Yes |
| f67v1 | 29 | 18 | 11 | 18 | 18 | Yes |
| f67v2 | 20 | 15 | 5 | 17 | 13 | No |
| f68r1 | 37 | 17 | 20 | 18 | 16 | No |
| f68r2 | 31 | 30 | 1 | 31 | 29 | No |
| f68r3 | 22 | 15 | 7 | 20 | 11 | No |
| f68v2 | 18 | 14 | 4 | 14 | 14 | Yes |
| f68v3 | 19 | 13 | 6 | 19 | 11 | No |
| f69r | 49 | 33 | 16 | 33 | 33 | Yes |
| f69v | 31 | 28 | 3 | 28 | 28 | Yes |
| f70r2 | 19 | 14 | 5 | 14 | 14 | Yes |
| f72r3 | 34 | 31 | 3 | 31 | 31 | Yes |
| f73r | 33 | 31 | 2 | 31 | 31 | Yes |
| f73v | 33 | 32 | 1 | 32 | 32 | Yes |
| f76r | 56 | 47 | 9 | 47 | 47 | Yes |
| f77r | 50 | 48 | 2 | 48 | 48 | Yes |
| f77v | 45 | 40 | 5 | 42 | 38 | No |
| f78r | 47 | 45 | 2 | 45 | 45 | Yes |
| f82r | 45 | 43 | 2 | 44 | 42 | No |
| f82v | 48 | 44 | 4 | 47 | 41 | No |
| f85r2 | 24 | 18 | 6 | 18 | 18 | Yes |
| f86v3 | 36 | 22 | 14 | 36 | 8 | No |
| f99v | 44 | 43 | 1 | 43 | 43 | Yes |

All native locators, physical source-file lines, original page-order indices,
nonempty-sequence indices, units/kinds, projection lengths/digests and candidate
indices are retained in the report. A matched rank refers only to its place in
a maximum projected-record pairing. It is not a manuscript line number.

## Reproduce and review

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 scripts/audit_historical_record_order.py --check research/historical/record-order.json
python3 scripts/audit_historical_record_order.py --output /tmp/record-order.json
python3 -m unittest tests.test_historical_record_order -v
```

The first seven synthetic tests passed before native measurement. Exhaustive
index-subsequence enumeration over **961 small sequence pairs** independently
checks L, the complete possible-pair union, mandatory-pair intersection, matched
ranks and uniqueness, including duplicates, empty input and unequal lengths.
Writer checks cover 33 temporary direct/symlink/hardlink aliases, four late alias
introductions during calculation/serialization, and failed typed/duplicate-key
checks preserving an output destination. Protection is repeated after
serialization, immediately before writing; no atomic multi-process guarantee
is asserted. Complete real-input replay and changed-parent rejection also pass.

A separate raw-envelope scanner independently reconstructs all 10,428 selected
source records and the complete parent inventory. An independent longest-path
calculation on the DAG of equal index pairs then verifies every selected page,
all 2,012 detailed nonempty descriptors, all 885 possible pairs/ranks, all 800
mandatory pairs, 182 controls, empty descriptors, 16 exclusions and complete
summary with numeric/Boolean distinctions. It imports neither production reader,
projection nor LCS routine.

Before a row crosswalk, review full source notation, record containers and image
regions, retaining the lossy, empty and ambiguous cases. This order constraint
changes no source and supplies no source preference, physical row alignment,
glyph or linguistic interpretation, calibrated statistic, decipherment or
translation. Both verified-crosswalk and statistical-evaluation flags stay false.
