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
