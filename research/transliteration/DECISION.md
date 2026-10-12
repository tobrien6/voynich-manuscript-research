# Transliteration selection and coverage audit

## Question and decision

Which versioned text sources can support reproducible decoding experiments while
retaining uncertainty and permitting sensitivity checks?

Use **ZL3b** as the initial primary source because this downloaded version retains
explicit spacing and reading alternatives. Use **IT2a** as a comparison on shared
loci. Preserve both original files and their distinct alphabets; do not pool
their records or treat them as independent experimental replicates. This is a
working data choice, not a judgment that either reading is correct.

The [comparator extension](COMPARATORS.md) adds GC2a native v101 and RF1b's
full/basic Eva exports. RF is a combined reference rather than an independent
transcriber; each export remains a separately pinned input. The coverage report
now includes all five exports while the initial ZL/IT comparison below remains
unchanged.

## Source records

- **TR-CATALOG:** René Zandbergen, [Transliteration of the Text](https://voynich.nu/transcr.html).
  Links and provenance for the available editions. The source identifies IT as
  the Takahashi version extracted from the Landini–Stolfi interlinear file, rather
  than a new download of Takahashi's original HTML pages.
- **ZL3b / IT2a:** exact URLs, source credits, version statements, byte lengths,
  and digests in [the machine-readable catalogue](../../data/transliterations.json).
- **TR-FORMAT:** René Zandbergen, [IVTFF format definition](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
  sections 4.2, 6.1, 6.3–6.4, and 6.6–6.9. Defines locus identifiers, special
  foldout page names, annotations, and metadata scope.
- **TR-LICENSE:** the publisher's [licence statement](https://voynich.nu/roadmap.html),
  inspected 2026-10-11, specifies CC0 for the collected transliterations.

## Method and observations

`scripts/audit_transliterations.py` verifies exact source bytes, reads conventional
IVTFF 2.0 records, and compares locations by page name and locus number. It does
not compare proposed plaintext. Counts are computed from the pinned bytes;
the report is [coverage_audit.json](coverage_audit.json).

| Observation | ZL3b | IT2a |
| --- | ---: | ---: |
| Page headers (transliteration units, not physical leaves) | 227 | 225 |
| All locus records | 5,385 | 5,215 |
| Records not marked nonexistent | 5,385 | 5,214 |
| Uncertain-space markers in present records | 2,748 | 0 |
| Alternative-reading groups in present records | 817 | 0 |
| Question marks in present records | 308 | 254 |

There are **5,214 shared present locations**, 171 present only in ZL3b, and none
present only in IT2a. Locus kinds agree at all shared locations. The full location
lists and per-page counts are in the report. IT2a retains
`f89v2.26,!Lf`; IVTFF's `!` locator marks nonexistent text, so this record is
excluded from present-location comparisons.

Annotation-like strings inside free comments are excluded from marker counts.
Question marks count literal markers, not unreadable glyphs: `???` denotes an
unknown number of characters. Absence of uncertainty markers in IT2a is a file
convention, not evidence of superior certainty. Published catalogue totals may
describe different editions; reproduce the counts from the pinned bytes.

## Limits and next experiment

The [native-Eva token adapter](TOKEN_ADAPTER.md) supplies explicit split/join
spacing policies and traceable eligible/excluded locus records for later tests.
It is a conservative preprocessing choice, not a glyph adjudication or decoding.

The reader rejects unsupported versions and compact identifiers rather than
silently dropping them. It handles continuation lines, `fRos`, foldout suffixes,
transcriber IDs, and inherited page/text metadata, but is not a complete IVTFF
conformance validator. No glyph adjudication or image alignment has been done.
EVA character strings are representations of shapes, not established phonetic
or semantic units; their string lengths must not be called manuscript glyph counts.

Next, report token statistics under both split and join treatments of uncertain
spaces, with explicit handling of alternative readings and unreadable material.
Compare paired sources on common loci of the same kind. A paragraph locus is
not automatically a whole physical line (`=` can mark a second item on the same
line), so positional tests need a stated locus or line definition.

The full-corpus audit is exploratory. It neither defines an untouched evaluation
set nor validates a decipherment. Later candidates must record prior exposure
and reserve material before fitting rules under the project's evaluation protocol.
