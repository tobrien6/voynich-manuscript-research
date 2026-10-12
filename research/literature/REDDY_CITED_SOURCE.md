# Current cited source and the published f81v sample

Every one of the **258 notation tokens in Figure 1 of Reddy and Knight (2011)**
matches the recovered author-associated f81v stream exactly, in both full and B
files. This corroborates a fixed publication sample beyond matching population
counts. Separately, the current bytes at the paper's cited `voynich.now` URL
match a linked legacy mirror and have a different nominal envelope structure.
Neither result authenticates the complete 2011 input or its preprocessing.

## Sources and committed comparison

The [paper](https://aclanthology.org/W11-1511/), section 2.2 on printed page 79,
cites `http://www.voynich.net/reeds/gillogly/voynich.now` and reports 225 pages,
37,919 tokens and 8,114 types. A current verified HTTPS retrieval of
[that exact resource](https://www.voynich.net/reeds/gillogly/voynich.now)
succeeds, despite the web reader being unable to open it. The author's
[transliteration resource listing](https://www.voynich.nu/transcr.html) links
a [legacy mirror](https://www.voynich.nu/hist/rand/voynich_now.txt).
Both raw downloads are byte-identical: **164,743 bytes**, SHA-256
`d919262e625b106d3aaf23dde02aa9f06ea320c154aeda464fdaa87245732425`.
Retrieved 2026-10-12 (America/New_York); no 2011 execution/download receipt is
recovered by this current correspondence.

The [accepted source intake](REDDY_SOURCE_INTAKE.md) and
[manifest](reddy-source-manifest.json) identify six recovered local files at
author-associated commit `643b881b2937bae8193814d8ff5d6e99a48bf7c5`, with
their later chronology and raw-local-only reuse limitation. Their full/B
population counts and complete native page/subset agreements remain unchanged.

The [human plan](REDDY_CITED_SOURCE_PLAN.md) and
[machine parameters](reddy-cited-source-plan.json) were committed at
[`d3f6837`](https://github.com/tobrien6/voynich-manuscript-research/commit/d3f6837);
the tested producer was committed at
[`43f53c0`](https://github.com/tobrien6/voynich-manuscript-research/commit/43f53c0).
Both were pushed before full-source census or figure/reference scoring. Whole
sources, accepted inventories, printed figure text/layout, extraction identity
and anchors, and three leading cited-source header formats were already
exposed. This is a descriptive diagnostic, not untouched evaluation.

Before scoring, the producer verifies five frozen dependency hashes, four local
reference identities, all six Reddy byte/SHA-256/Git-blob identities and complete
accepted source-intake replay. It executes no author program.

## Complete current-source census and its limits

The [complete report](reddy-cited-source.json) accounts for every physical LF
line and every raw prefix-envelope candidate. Latin-1 is reversible byte
transport, not an asserted encoding of source commentary. A carried curly
comment mask retains nested comments, source errors and all raw candidates
inside comment state. No malformed source is repaired, no continuation is
silently appended, and no word tokenization or alternative-reading resolution
is performed on the current cited file.

| Operational line category | Physical lines |
| --- | ---: |
| Blank | 560 |
| Comment-only under the declared mask | 360 |
| Bare active page-envelope candidates | 150 |
| Active dot-bearing envelope candidates | 2,955 |
| Unrecognized outside-comment material | 22 |
| Complete LF-line denominator | 4,047 |

The 3,105 raw line-initial angle-envelope candidates are all retained.
The 2,955 dot-bearing items use only the first dot to separate a literal page
prefix from an opaque suffix. They are the producer's operational
`record_envelope` class, **not a validated locus, physical-row or word count**:
68 have empty outside-comment bodies, and identifiers can look like unit
headers or compound source containers. No unit/line interpretation is imposed.
Their 153 literal page prefixes likewise are not automatically physical leaves.

The comment model flags unmatched closing braces at one-based file lines
1,938 (zero-based character offset 7) and 2,248 (offset 6); its validity flag
is false. All 22 unrecognized lines and all 41 envelope/page-context mismatches
retain file positions and raw-line hashes. These failures remain part of the
result, so this inventory is not presented as a complete validated legacy reader.

All five repeated literal identifiers are retained with both occurrences:

| Literal identifier | Physical file lines |
| --- | --- |
| `f100r.1` | 3,430; 3,431 |
| `f68r1.S4.3` | 2,161; 2,170 |
| `f68r1.S4.4` | 2,162; 2,171 |
| `f68r1.S4.5` | 2,163; 2,172 |
| `f68v3.S8.1` | 2,307; 2,308 |

The recovered full file has 5,213 annotated records and 225 native page groups;
the current cited-file envelope categories and prefix set are different.
Those record definitions are not interchangeable. This does not measure
missing physical pages, establish an alias crosswalk, or show which URL bytes
were available to the authors in 2011. Word/type counts for the current cited
file remain **unmeasured**; its bracket/parenthetical alternatives, punctuation,
paragraph marks and asterisks are not filtered to seek the paper's totals.

## Fixed Figure 1 correspondence

The primary PDF is 966,546 bytes, SHA-256
`842e285c544bffefc1eefa58704cbde6a5e93f0706542dc6a67d374f2c7da599`.
Figure 1 identifies f81v. Its complete transcription area was visually checked
on PDF page 2 (printed 79), then frozen at 72 dpi:
`x=314, y=373, width=226, height=317`. Poppler `pdftotext` 24.04.0 extracts
that page/rectangle with layout mode and no page-break marker. The entire
1,315-byte extraction has SHA-256
`e4ad579d69aeb4f2ed5a19c7ece85de6fecc60a8d13ca1cb1df5ed71173eea44`.
Every run requires exact extraction-byte equality before comparison.

The whole extracted text is split only on whitespace, with all literal capital
letters, digits and asterisks retained. The source anchors are pinned in the
plan. No I/1 or O/0 substitution, case folding, selected row, glyph mapping or
annotation filter is introduced.

| Comparison to exact nominal f81v | Printed tokens | Reference tokens | Native reference records | Mismatch positions |
| --- | ---: | ---: | ---: | ---: |
| Full annotated file | 258 | 258 | 28 | 0 |
| B annotated file | 258 | 258 | 28 | 0 |

All three token vectors have SHA-256
`f6a833512906b72cd14985c64290cee5dd1f8f3ecd6298c8157ac0c0b3db0199`.
The report retains each reference record's literal four-field header, original
global ordinal, physical file line, token denominator and vector hash, plus the
complete mismatch ledger (empty here). The full/B page vectors are the same
source subset and are **not independent replications**.

The publication's transcription indicates paragraphs rather than native line
breaks. Whitespace-vector agreement therefore supplies no printed-line/native
record crosswalk. This comparison concerns the PDF text layer and the recovered
notation strings, not verification of manuscript glyphs, the embedded image's
readings or every page in the original corpus. No current-cited-file words are
compared with the figure or recovered files.

## Reproduce and validation

Python 3.10 or later, standard library and Poppler `pdftotext` 24.04.0. Retrieve
the two exact current source URLs and primary PDF, retain the six Reddy files
under `reference/reddy/` following the accepted manifest, and generate the local
fixed extraction:

```sh
pdftotext -f 2 -l 2 -r 72 -x 314 -y 373 -W 226 -H 317 -layout -nopgbrk reference/paper.pdf reference/figure1.txt
python3 -m unittest tests.test_reddy_cited_source -v
python3 scripts/audit_reddy_cited_source.py --reference /path/to/reference --check research/literature/reddy-cited-source.json
python3 scripts/audit_reddy_cited_source.py --reference /path/to/reference --output /tmp/reddy-cited-source.json
cmp /tmp/reddy-cited-source.json research/literature/reddy-cited-source.json
```

The four reference filenames and fingerprints are specified in the machine
plan. Thirteen focused tests cover multiline/nested comment masks, all raw
candidate/duplicate/context/lexical-error cases, exact line accounting,
unrepaired locators, literal figure tokens/anchors, missing pages, symbol and
length-tail disagreements, native provenance, extraction/version failures,
every reference/dependency/parent pin, strict JSON and existing-output
preservation. Ninety temporary early/late direct/symlink/hardlink cases protect
all eighteen source/reference/plan/producer paths. Additional regressions refuse
removed source-name case variants during calculation/serialization and retain
entry resolved targets after source-symlink retargeting. Within the same physical
parent directory, NFC-normalized case variants are conservatively protected
even when the original file is absent. Entry and current resolved paths are
retained; the post-check filesystem race limitation is unchanged.

The report replays byte for byte. An independent whole-file byte-position mask
agrees with all 4,047 line classifications, 3,105 raw candidates, every active
descriptor/hash, notation count, duplicate/context case and both errors. A
separate PDF bbox-word extraction, rather than cropped-layout text, and direct
raw annotation scans agree with every figure token and all 28 reference
descriptors in each case. Original first-report SHA-256, preserved in result commit `636b6a0`:
`7e729a0bf285488dc115dd28071efe1b8f63dd34ce660144e7864a355be4538f`.

A later output-guard repair refreshes only the truthful producer fingerprint.
Every census, figure comparison, source identity, frozen plan choice and other
report field is unchanged. The current report remains 2,466,829 bytes; SHA-256:
`759a83d4ca589d0dae810696ecdba6c701207534bb5c31e8e3c84ea7b54bb73f`.

The raw current sources, PDF, extracted transcription and unlicensed Reddy
data/code remain local; this contribution publishes original audit code and
metadata only. Next, preserve current-source format irregularities in any
separately frozen legacy parser, and seek archival or author evidence before
claiming 2011 full-corpus identity. No Table 2 procedure, statistical tail,
language, decipherment or translation is validated here.
