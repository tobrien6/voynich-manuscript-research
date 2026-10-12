# Historical H and modern IT2a: equal totals, different envelopes

Question: do the recovered 1.6e6 H selection and accepted IT2a export have the
same page identifiers and record counts, given their equal corpus-wide total?

**H contains 5,214 native records and IT2a contains 5,214 present loci, but
that total does not establish an alignment.** Exact page strings overlap on
223 pages. Of those, 219 have equal comparison counts and four differ.
The differences cancel in aggregate.
Two record-bearing identifiers occur only in H and two only in IT2a.

These are native source-envelope observations. Neither source record counts
physical manuscript leaves or visible writing rows. Equal counts on a page do
not establish equal text, row order, segmentation, or glyph readings.

## Pinned inputs and method

The [historical intake](README.md) pins the publisher-hosted 1.6e6 candidate,
including the ZIP and exact member bytes. The [modern source catalog](../../data/transliterations.json)
pins IT2a: SHA-256 `7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5`.
The [complete report](modern-page-envelopes.json) records both catalog hashes,
source identities, and every page profile.

The offline [auditor](../../scripts/audit_historical_modern_pages.py) verifies
archive/member identity and modern source hash, length, and alphabet before
comparison. It reuses the accepted historical and IVTFF readers; only native
transcriber `H` is selected, and modern interlinear records are rejected.
Every modern record is retained as declared, while locator `!` excludes it
from present counts. Empty modern headers and nonexistent-only pages remain
explicit diagnostics.

Groups share a key only when their full page strings are identical. No panel
suffix is truncated, no alias registry is consulted, and no native unit or
line number is converted to a modern locus. Historical unit tags retain case;
modern kinds retain subtypes. Source-ordered identifier arrays are fingerprinted
globally and per page using ASCII JSON with separators `(',', ':')`. The
four differing exact-page groups also retain all native and modern identifiers
in source order, without pairing individual records.

No text payload is compared, converted to modern notation, tokenized, or
written to the report. A separate historical diagnostic removes only native
curly comments and flags bodies containing at least one `!` or `%` and otherwise
only fillers, whitespace, periods, commas, hyphens, or equals signs. It retains
their native counts and records filler/structural-marker counts separately.
The historical unknown/rare-glyph marker `*` is never treated as padding.
The comparison cannot establish whether any strings or glyphs are equal.

The [modern publisher's description](https://voynich.nu/transcr.html), sections
“The interlinear transliteration file” and “Common transliteration file format”,
identifies IT as an older Takahashi contribution from the interlinear and
describes later consolidation of locus definitions. This supplies provenance
context, not a documented row crosswalk for these pinned files.

The [historical release page](https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/98-12-28-interln16e6/),
“Main differences between versions 1.6e5 and 1.6e6”, documents renaming the
nine-rosette page `f86r4` to `f85v2` and merging `f101v1` into `f101v2`. Those
are changes between historical editions; they are not evidence for automatically
joining this candidate's `f101v2` to modern `f101v`. Source-specific conventions
need separate support.

## Exact-page observations

| Full page identifier | Historical H records | IT2a present loci | IT2a declared loci | Count difference, IT present minus H native |
| --- | ---: | ---: | ---: | ---: |
| `f46v` | 12 | 13 | 13 | +1 |
| `f75v` | 69 | 70 | 70 | +1 |
| `f89v2` | 28 | 27 | 28 | −1 |
| `f106r` | 47 | 46 | 46 | −1 |

IT2a's sole explicitly nonexistent record is `f89v2.26,!Lf`. It remains in
the declared count and identifier ledger, without entering the present count.
Historical H records are selected as recorded by the accepted intake, including
padding-only envelopes; no modern presence rule is assigned to them. Equal
declared counts on `f89v2` do not identify that modern placeholder with a
particular historical label or adjudicate manuscript visibility.

On `f106r`, modern identifiers jump from `f106r.28` to `f106r.30`; the native H
ledger includes `f106r.P.29;H`. That native body contains 67 percent fillers
and a terminal hyphen, with no other payload. It is the only H record selected
by the padding-only diagnostic. The pinned member's format comments, physical
lines 248–272, distinguish `%` as lacking transcription information from the
alignment uses of `!`; this does not assert that manuscript writing is absent.
The historical record stays in the native denominator. These remain separate
numbering observations, not a verified row correspondence. On
`f46v` and `f75v`, the report preserves source-specific unit and kind partitions
without diagnosing a split, merge, omission, or transcription error.

The source-only identifier observations are:

| Identifier appearing only in the H-record or IT-present page set | Source | Selected count |
| --- | --- | ---: |
| `f101r1` | Historical H | 10 |
| `f101v2` | Historical H | 28 |
| `f101r` | IT2a | 10 |
| `f101v` | IT2a | 28 |

Similar spelling and equal counts do not authorize an alias. The unmatched
groups stay separate from exact-page differences. Totals across every retained
profile are 5,214 H records, 5,215 declared IT2a loci, and 5,214 present IT2a
loci. All 225 modern page declarations contain present records in these inputs.

## Reproduce and validate

Python 3.10 or later, standard library only; no downloads or archive extraction:

```sh
python3 scripts/audit_historical_modern_pages.py --output research/historical/modern-page-envelopes.json
python3 scripts/audit_historical_modern_pages.py --check research/historical/modern-page-envelopes.json
python3 -m unittest tests.test_historical_modern_pages -v
```

Eleven synthetic tests verify cancelling discrepancies under equal global totals,
present/nonexistent accounting, panel-suffix isolation, empty headers, native
identifier/order retention, modern interlinear rejection, both source pins,
duplicate selection and repository path containment, padding-only detection
without dropping unknown glyphs or changing counts, and CLI input protection
against canonical paths and hardlink aliases
and output preservation on failed checks. The report also replays against the
real pinned inputs. Invalid inputs or a changed committed report return 1.
A successful check confirms reproduction of this diagnostic, not a corpus
alignment.

Existing output paths are checked with filesystem identity as well as resolved
path equality before writing. A hardlink alias of a source, catalog, or protected
reader is rejected; unrelated new or existing report outputs remain allowed.

## Limits and next test

This diagnostic exposes metadata across the complete H/IT inputs and must be
recorded as prior exposure for later evaluation. It does not establish identity
with a paper's downloaded or processed bytes, reproduce published token counts,
implement manual exclusions, or decide which representation is correct.
Historical comments and modern notation have different conventions; a later
content comparison needs its own explicit transformation contract.

Before applying modern exclusions to historical data, document source-specific
page conventions and inspect the four differing count groups. Build any row
crosswalk from documented source provenance and content/region evidence,
preserving unmatched, split, merged, and nonexistent records. Do not match
rows by global ordinal position: local count differences can shift such a
pairing even when total counts agree. No image mapping, glyph adjudication,
decipherment, or translation is established here.
