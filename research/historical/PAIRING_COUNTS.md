# How many maximum projected-record index pairings remain?

The 12 ambiguous pages in the accepted [record-order audit](RECORD_ORDER.md)
have between **two and 18 distinct maximum index pairings**. Equal weighting of
those complete pairings need not give each possible pair the same share: on
`f49v`, nonmandatory pairs occur in **1/16 to 13/16** of the 16 pairings. These
are counts of encoded index choices, without a probability of source correctness
or physical manuscript-row correspondence.

The [complete report](pairing-counts.json) retains all 211 equal-multiset pages,
including 182 equal-order identity controls, all 29 differing orders and all
16 excluded union pages. Of the complete selected cohort, 199 pages have one
maximum pairing and 12 have multiple. The 17 unique differing-order pages and
all 182 controls remain explicit; unique index pairing does not establish a
native-locator alias.

## Fixed sources and exposure

The [declared plan](PAIRING_COUNTS_PLAN.md) was published and its remote head
verified at `e53b95ab0764ee4ec2495dc061b78667daaabb6f`. The count producer and seven
synthetic tests were then published/verified at
`bc6bbba851d6666eb56564a57c0806ac34e2b395` before this complete native count-summary
assembly. During review of #167, an independent DAG oracle had already computed
native path counts internally to check uniqueness and mandatory flags. That
prior computational exposure is disclosed in the plan. This follow-up is neither
an untouched test nor independent certification of private first-look timing.

The entire accepted parent is frozen to SHA-256
`0f053fd9a3bdeb2e92ae95da9d9c352cdf908b3a8be4aaec75b52c9a99211365`
and reconstructed against its unchanged historical H/modern IT2a archive,
member, export, catalogs, plans and implementation pins. Exact source-specific
nonempty lowercase projections are compared before hashing. Native page IDs,
orders, notation losses, empty descriptors and the nonexistent modern envelope
are retained. Candidate indices refer to the same immutable parent descriptor
lists; no projected bodies, source corrections or page aliases are published.

Credits and reuse terms remain those of the [historical data note](../../data/historical/README.md)
and [modern export catalog](../../data/transliterations.json): Jorge Stolfi,
Gabriel Landini, Jim Reeds, Takeshi Takahashi, the other named contributors and
publisher René Zandbergen. The historical-paper input identity remains unproven.

## Count complete pairings, not skip routes

Each node of the equal-pair DAG is one equal projected-string index pair (i,j).
Edges require strict increases in both source indices. A longest path is one
distinct maximum ordered index-pair sequence. Counting arbitrary routes through
sequence-DP skip states could count that same pairing multiple times; this
producer counts index-pair sequences once each.

Exact integer counts of longest prefixes and suffixes give the number of
maximum pairings through a supported pair. Their product, divided by the page's
total maximum-pairing count, gives its reduced support fraction. At every matched
rank the through-pair counts sum exactly to that page total. A mandatory pair
has fraction 1; a unique page has one complete maximum pairing. Synthetic
zero-length optima retain one empty pairing. Counts and fraction components are
serialized as decimal strings to preserve arbitrary integer precision.

The weighting is explicit: **each distinct optimal index sequence counts once**.
It supplies no prior over physical row identities. Repeated projected strings
remain observationally indistinguishable even when their index choices differ.
The report retains all 885 possible parent pairs, all 800 mandatory flags and
all 836 matched ranks unchanged; no matching witness or preferred source is
selected. Counts are never pooled into a joint physical distribution over pages.

| Maximum pairings per page | Differing-order pages | All selected pages |
| ---: | ---: | ---: |
| 1 | 17 | 199 |
| 2 | 6 | 6 |
| 3 | 2 | 2 |
| 4 | 1 | 1 |
| 12 | 1 | 1 |
| 16 | 1 | 1 |
| 18 | 1 | 1 |

## Every differing-order page

The range excludes mandatory pairs; it describes complete index-pairing shares
under the stated uniform weighting. It is not a confidence interval, likelihood
or probability that a locator refers to a manuscript row.

| Exact page | Nonempty records per edition | Maximum paired records | Maximum index pairings | Nonmandatory support range |
| --- | ---: | ---: | ---: | --- |
| f100r | 27 | 26 | 2 | 1/2 to 1/2 |
| f102r1 | 17 | 15 | 1 | None (all mandatory) |
| f102r2 | 20 | 17 | 1 | None (all mandatory) |
| f102v2 | 39 | 38 | 1 | None (all mandatory) |
| f49v | 46 | 27 | 16 | 1/16 to 13/16 |
| f57v | 13 | 10 | 2 | 1/2 to 1/2 |
| f67r2 | 74 | 62 | 1 | None (all mandatory) |
| f67v1 | 29 | 18 | 1 | None (all mandatory) |
| f67v2 | 20 | 15 | 3 | 1/3 to 2/3 |
| f68r1 | 37 | 17 | 2 | 1/2 to 1/2 |
| f68r2 | 31 | 30 | 2 | 1/2 to 1/2 |
| f68r3 | 22 | 15 | 18 | 1/3 to 2/3 |
| f68v2 | 18 | 14 | 1 | None (all mandatory) |
| f68v3 | 19 | 13 | 12 | 1/6 to 1/2 |
| f69r | 49 | 33 | 1 | None (all mandatory) |
| f69v | 31 | 28 | 1 | None (all mandatory) |
| f70r2 | 19 | 14 | 1 | None (all mandatory) |
| f72r3 | 34 | 31 | 1 | None (all mandatory) |
| f73r | 33 | 31 | 1 | None (all mandatory) |
| f73v | 33 | 32 | 1 | None (all mandatory) |
| f76r | 56 | 47 | 1 | None (all mandatory) |
| f77r | 50 | 48 | 1 | None (all mandatory) |
| f77v | 45 | 40 | 3 | 1/3 to 2/3 |
| f78r | 47 | 45 | 1 | None (all mandatory) |
| f82r | 45 | 43 | 2 | 1/2 to 1/2 |
| f82v | 48 | 44 | 4 | 1/2 to 1/2 |
| f85r2 | 24 | 18 | 1 | None (all mandatory) |
| f86v3 | 36 | 22 | 2 | 1/2 to 1/2 |
| f99v | 44 | 43 | 1 | None (all mandatory) |

## Replay and validation

Standard library, Python 3.10 or later, from the repository root:

```sh
python3 scripts/audit_historical_pairing_counts.py --check research/historical/pairing-counts.json
python3 scripts/audit_historical_pairing_counts.py --output /tmp/new-pairing-counts.json
python3 -m unittest tests.test_historical_pairing_counts tests.test_historical_record_order tests.test_historical_record_projections -v
```

All **29 focused tests** pass: nine count, nine parent order and eleven record
projection tests. The first seven count tests validate all counts and through-pair support against
exhaustive index-subsequence alignment enumeration of 961 binary sequence pairs,
including repeats, reversals, unequal lengths and empty optima. A separate known
case has three pairings and unequal 1/3 versus 2/3 candidate shares. A binomial
case exceeds 2^53 and remains exact. Writer cases preserve protected data under
initial/late direct, symlink and hardlink aliases, failed typed/duplicate/nonfinite
checks and an existing destination; serialization precedes the final guard and
exclusive fresh-file creation. Additional native replay and changed-parent tests
are validation only; the frozen producer and first report are unchanged.

A separate raw-envelope scanner reconstructs all 10,428 native records and
verifies the full accepted parent. An independent count calculation then uses
only edges between consecutive matched ranks, with source-derived support/ranks,
without importing a producer, reader or projection routine. It agrees with every
field of this typed report: all 211 pages, 885 pair counts/fractions, 836 rank
sums, controls, empties, exclusions, source and ten helper pins. Every guide table
row is checked. The first report SHA-256 is
`6acf581d7417966a1841af7071574138482cced21b2d522a75e26a2a9d4ee48d`.

This is an exposed, lossy encoded-record ambiguity descriptor. No native order,
source body, notation mapping, glyph reading or physical row crosswalk changes.
Both verified-crosswalk and statistical-evaluation flags stay false. No
statistical calibration, edit history, language, decipherment or translation is
established; qualified source/image review remains necessary before any row
pairing is adopted.
