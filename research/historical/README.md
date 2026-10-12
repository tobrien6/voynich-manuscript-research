# Historical interlinear intake

Question: can the historical source cited by Voynich statistical papers be
recovered as a reproducible candidate input without treating modern IVTFF as
the same edition?

The [release page](https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/98-12-28-interln16e6/)
offers Stolfi's 1.6e6 interlinear and identifies Takahashi's contribution by code
`H`. It describes basic EVA, aligned versions, and edited boundaries. The HTTPS
form of the paper's older directory returned 404 on inspection; the export page
provided the download. The [catalog](../../data/historical/interlinear-16e6.json)
and [unmodified ZIP](../../data/historical/text16e6.zip) now pin the recovered
candidate. Reuse terms and credits are retained in the
[data note](../../data/historical/README.md).

This does **not** establish byte identity with the source obtained in 2010 by
[Amancio et al.](https://doi.org/10.1371/journal.pone.0067310). Their
[supplement](https://doi.org/10.1371/journal.pone.0067310.s007) selects H from the
named archive and prescribes additional parsing and manual exclusions. Those
steps have not been implemented here. No published result is reproduced.
The [published-methods register](../literature/README.md) records the measurement
units and null scopes that a later replication must match.
The [planned parsing reconstruction](PARSING.md) now implements four explicit
exclusion interpretations and preserves their length discrepancies and unmatched
label phrases. It does not reproduce a published statistic.
The [label phrase provenance audit](LABEL_PHRASES.md) traces the unmatched names
to other native codes and retains repeated strings elsewhere, without changing
the H parser or establishing the authors' input.
The [repeated-type assay](REPEATED_TYPES.md) applies the published B definition
and a declared global control to all four approximate streams, with exact means
and complete ten-trial results. It preserves the difference from modern
conditional-locus controls and does not claim an exact historical replication.
The [matched native-record control](RECORD_CONDITIONED.md) keeps those input
streams and all measured joining edges fixed while changing the null's bags.
It retains the resulting reduction of B's contrast and reversal of A's mean
contrast, without a causal explanation or significance claim.
The [equal-join provenance census](JOIN_PROVENANCE.md) locates every repeated
joining edge in the original H record order. None bridges an excluded/empty H
record; all source descriptors, overlap counts and singleton cases are retained
without asserting physical-line or glyph alignment.
The [matched-null comparison figure](figures/REPEAT_NULLS.md) displays every
global/record-conditioned ratio with A/B units kept separate, and preserves
the opposing within-record/joining A residuals without new sampling or tails.
The [exact conditional B variance](TYPE_VARIANCE.md) preserves that full edge
path and global type deduplication, with signed type covariance, all four
outcomes and descriptive SD scaling without a calibrated tail.
The [fixed B tail-control block](TYPE_TAILS.md) retains 1,000 additional controls
per variant, both inclusive tail definitions and distinct frequency/rank scores,
with the original controls and exposure/randomization limits explicit.
The [literal H/Reddy envelope audit](REDDY_ENVELOPES.md) locates the recovered
paper file's one-record gap in a normalized-empty H record. Every shared key
retains the same order and fallback-retained count; all eight listed-code count
differences remain explicit without claiming text or alphabet equivalence.

## Method

`scripts/audit_historical_interlinear.py` checks the entire ZIP hash and length
before reading it in memory, requires its one cataloged member, and verifies the
member hash and length. It never extracts archive paths to the filesystem.
Original source bytes and comments remain unchanged.

The native envelope is `<page.unit.line;transcriber>`. The auditor preserves
unit case, line suffixes, source order, and transcriber identity. It accepts
declared page/unit headers and fails on unknown lines, missing context, duplicate
records, or malformed inline comments. Unsupported continuation lines are not
silently joined. Latin-1 supplies a reversible byte-to-code-point transport for
inspection, without asserting the original encoding of every comment.

In this historical format, `{...}` is a comment; it is not the modern IVTFF
ligature syntax. The report counts punctuation outside balanced curly comments
for H only. These are notation occurrences, not glyph or token frequencies.
The H locator digest hashes the source-ordered array of native locator strings,
serialized as ASCII JSON with separators `(',', ':')`; it contains no text body.
The historical unit tags are not automatically mapped to modern P0/P1 categories
or physical manuscript lines.

## File observations

The [complete report](intake.json) accounts for every physical line:

- 17,357 native transcription records across 227 record-bearing page identifiers
  and 494 logical units, with all transcriber counts retained.
- H: 5,214 records across 225 page identifiers and 473 logical units.
- H: 2,044 curly comments. Outside comments there are 31,850 periods, 4,472
  exclamation marks, 4,287 hyphens, 1,783 equals signs, 280 asterisks, and 120
  percent signs; no commas. Two H bodies contain non-ASCII bytes inside comments,
  and none do outside comments.

The accepted [modern audit](../transliteration/coverage_audit.json) also records
5,214 **present** IT2a loci; its 5,215 total records include one explicitly
nonexistent locus. Equal totals do not establish matching content, ordering,
segmentation, or identifiers. No historical-to-modern locus crosswalk is claimed.

The [exact-page envelope comparison](MODERN_PAGE_ENVELOPES.md) now accounts for
all H and IT2a page groups: four shared identifiers have different selected-record
counts, and two identifiers occur only in each source's page set. The equal
global total hides those discrepancies; the diagnostic supplies no row pairing.

The [lossy lowercase comparison](LOWERCASE_PROJECTION.md) then finds 183 matching
streams on 223 exact shared page IDs, while 39 differing streams retain the same
symbol frequencies. It preserves omitted-symbol counts and the excluded modern
envelope separately; those matches do not establish full text or glyph identity.

The [native record-projection audit](RECORD_PROJECTIONS.md) retains record
boundaries and order under that same lossy projection: 211 shared pages have
equal nonempty projection bags, including 29 with different order. One-to-one
and ambiguous projection groups retain native locators without becoming a
verified locus or image crosswalk.

The [complete projected-record order diagnostic](RECORD_ORDER.md) measures every
equal-multiset page under both native orders. On all 29 differing-order pages,
maximum pairings retain 836 of 1,006 nonempty records per edition; every possible
optimal index pair and ambiguity is retained without selecting a row crosswalk.

The [f46v source-container example](F46V_SOURCE_CONTAINER.md) preserves one
historical H envelope and two present IT2a P0/Pt loci with the same joined
lowercase projection. The default modern adapter excludes Pt by kind; this
source-unit difference creates no verified record or image crosswalk.

## Reproduce and next test

Python 3.10 or later, standard library only; run from the repository root:

```sh
python3 scripts/audit_historical_interlinear.py --output research/historical/intake.json
python3 scripts/audit_historical_interlinear.py --check research/historical/intake.json
python3 -m unittest tests.test_historical_interlinear -v
```

Validation checks both container/member identity, native envelopes and comment
boundaries, complete line accounting, source-order sensitivity, selected-code
handling, and exact report replay. The source format descriptions were checked
against the member's `FORMAT OF THIS FILE` comments and the release page.

Next, freeze a parser plan for one published statistic, implement every manual
exclusion with a locator-level ledger, and retain stage counts and uncertainty
choices. Matching the paper's reported token count would be a diagnostic, not
proof of the original processed sequence. Keep historical replication distinct
from modern-source sensitivity tests and disclose approximations.

This is an exploratory full-source intake. Native source headers, records,
comments and snippets were inspected; record that exposure in any later split.
No glyph adjudication, statistical mechanism test, decipherment, or translation
was performed.
