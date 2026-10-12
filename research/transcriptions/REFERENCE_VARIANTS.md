# Native alphabet and reference variant audit

Audited 2026-10-11 (America/New_York). This extends the accepted [ZL/IT corpus decision](../transliteration/DECISION.md) with GC and the full/basic RF variants. The [publisher, TR001](https://voynich.nu/transcr.html), describes RF as derived from ZL and GC, so RF agreement cannot supply independent confirmation of a result developed on those sources.

## Reuse the accepted corpus interface

The extension uses the repository's `scripts.ivtff.parse_ivtff` reader and [ZL/IT source catalog](../../data/transliterations.json). The [extension registry](editions.json) adds three exact source URLs and hashes. It does not introduce a competing primary source choice or a second record parser.

The publisher explicitly releases the transliteration datasets under CC0 in its [licence statement, TR003](https://voynich.nu/roadmap.html). Credits and links remain recorded in the [source register](SOURCES.md). The two accepted source files are already in the repository; the three extra files are local audit inputs and are not added as large copies by this contribution.

## Direct file observations

All five inputs are ASCII with IVTFF 2.0 headers. Counts below distinguish declared records from records that the accepted reader marks present; `!` marks a nonexistent locus. Counts of marker presence mean records with at least one matching notation outside inline comments, rather than numbers of symbols or manuscript glyphs.

| Edition / file | Alphabet | Page declarations | Declared / present records | Records with alternatives | Records with uncertain spaces | Records with extended codes |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ZL 3b / `ZL3b-n.txt` | `Eva-` | 227 | 5,385 / 5,385 | 728 | 1,833 | 132 |
| IT 2a / `IT2a-n.txt` | `EvaT` | 225 | 5,215 / 5,214 | 0 | 0 | 0 |
| GC 2a / `GC2a-n.txt` | `v101` | 226 | 5,367 / 5,366 | 0 | 1,595 | 301 |
| RF 1b full / `RF1b-e.txt` | `Eva-` | 227 | 5,385 / 5,385 | 0 | 575 | 2,360 |
| RF 1b basic / `RF1b-er.txt` | `Eva-` | 227 | 5,385 / 5,385 | 0 | 575 | 0 |

The RF variants have identical alphabet headers and share all 5,385 present locus keys, yet **2,651 native text records differ**. The accepted reader removes locator padding and joins wrapped records; internal annotations remain in the comparison. This is not a glyph-error rate. The result demonstrates that alphabet and release-family names alone do not uniquely specify analysis inputs: exact variant URLs and byte hashes matter.

The [nonexistent-locus source extract](NONEXISTENT_LOCUS.md) identifies the sole
explicit nonexistent key, `f89v2.26`, in IT2a and GC2a. ZL3b and both RF variants
omit that exact key while retaining its page header and numbered-key context.
Explicit placeholders and undeclared keys remain different annotation states;
neither supplies an independently verified manuscript-presence decision.

GC uses a different native alphabet. Comparing its character counts or strings to Eva requires a documented conversion or unit definition; this audit performs neither. Page declarations describe edition surfaces rather than physical leaves. No image crosswalk, semantic reading, accuracy estimate, or translation is inferred from these counts.

## Reproduce with Python 3.10 or later

Obtain `GC2a-n.txt`, `RF1b-e.txt`, and `RF1b-er.txt` using the exact links in [editions.json](editions.json), retaining their filenames in a local directory. From the repository root:

```sh
python3 scripts/inspect_ivtff.py --input-dir /path/to/local/editions --check research/transcriptions/intake-audit.json
python3 -m unittest discover -s tests -v
```

The script makes no network requests. It verifies the accepted ZL/IT catalog pins and all three extension pins before parsing, then compares its result with the committed aggregate report. `--output PATH` writes a fresh report. The JSON omits machine paths and generation timestamps so identical inputs reproduce byte-for-byte.

Four extension tests cover comment/nonexistent-locus exclusion, counting records rather than symbols, same-header/different-text detection, changed-hash rejection, and repository path containment. Parsing and continuation behavior remain covered by the accepted reader's tests.

## Next analysis contract

Retain native notation, source hashes, original locus/page IDs, relation and transcriber identifiers, and uncertainty before tokenization. Specify spacing, alphabet-unit, locus-inclusion, and annotation policies in a separate versioned layer. Do not treat encoded string length as manuscript glyph length or remove rare signs to make alphabets agree. Native files and this audit expose text and metadata; they do not create an untouched evaluation set.
