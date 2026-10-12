# Transcription intake sources

Inspected 2026-10-11 (America/New_York). `TR` identifiers are local to this register to avoid collisions with the manuscript-image source register.

## TR001 — René Zandbergen, transliteration resource listing

- URL: https://voynich.nu/transcr.html
- Author: René Zandbergen, a creator of Eva and the ZL edition.
- Supports: release links and alphabet labels; IT is a historical Takahashi extraction from the interlinear file, distinct from updated TT; RF combines ZL and GC and is not independent of them.
- Limitation: publisher commentary and comparisons are not independent validation of the manuscript readings. Version labels in the listing can differ from internal file headers or later modifications.
- Reuse: see the publisher's explicit statement in TR003. This extension uses the repository's accepted ZL/IT files and locally downloaded GC/RF files; it adds metadata and aggregate results rather than another set of source-text copies.

## TR002 — René Zandbergen, special topics in transliteration

- URL: https://voynich.nu/extra/sp_transcr.html
- Supports: IVTFF record envelopes and annotations, including certain/uncertain spaces, alternative readings, inline comments, extended codes, paragraph markers, and wrapped loci.
- Scope: the accepted `scripts/ivtff.py` reader supports conventional IVTFF 2.0 envelopes, joins wrapped records, and preserves internal text annotations. The audit uses this reader rather than defining a second parser or interpreting alphabet-specific glyph combinations.
- Detailed format reference linked by the author: https://voynich.nu/software/ivtt/IVTFF_format.pdf. The HTML conventions were used for this contribution; the complete PDF specification was not reviewed here.

## TR003 — Publisher's licences and copyright statement

- URL: https://voynich.nu/roadmap.html
- Author: René Zandbergen; inspected the site's Licences and copyright section on 2026-10-11.
- Supports: the site explicitly makes the transliterations collected in its linked tables available under CC0 and requests source acknowledgement. This resolves the earlier intake note that had checked only file headers and the download listing.
- Scope: applies to the linked transliteration datasets; the manuscript-image source register retains its separate rights notes.

## TR004 — IVTFF locator-status specification, targeted follow-up

- Author: René Zandbergen; [IVTFF specification](https://www.voynich.nu/software/ivtt/IVTFF_format.pdf), document issue 2.0.2 (8 July 2025), describing format 2.0.1.
- Inspected: 2026-10-12 (America/New_York); cover, section 1.2, and section 6.4/Table 8, printed page 21.
- Retrieved SHA-256: `7ac9c4a82064763cac8767cca6f661cc4e1b4503ab9342acc03032ddb6939d49`, matching the accepted TR-FORMAT [documentation pin](../transliteration/comparator_documentation.json).
- Supports: the locator field's explicit nonexistent-text status and source-locus numbering conventions, used alongside observed omissions in the [scoped source extract](NONEXISTENT_LOCUS.md).
- Limitation: this checks format semantics, not manuscript visibility, a panel/region mapping, or the accuracy of a particular source annotation. It is a targeted inspection, not full conformance validation.
- Reuse: source PDF remains local; citation, fingerprint and selected paraphrase only are added.

## TR005 — Primary Currier/Eva conversion definition and documentation

- Author: René Zandbergen; [Bitrans directory](https://www.voynich.nu/software/bitrans/), rule definition, version 1.5 manual and software README; inspected 2026-10-12 (America/New_York).
- Identity and observations: [source intake](../transliteration/CURRIER_CONVERSION_SOURCE.md) and [complete catalog](../transliteration/currier-conversion-source.json) pin all three retrieved artifacts and every rule-row identity, with the complete synthetic two-code round-trip diagnostic.
- Use: independently documented notation-conversion inputs and stated processing semantics for a future frozen comparison.
- Limitation: current 2025 material does not authenticate a 2011 preprocessing execution. No corpus conversion, glyph mapping or translation is performed.
- Reuse: source rule/manual/README remain local; metadata and limited source-linked paraphrase only. The separate dataset CC0 statement is not extended to these artifacts.

## TR-D001–TR-D005 — Downloaded edition files

| ID | Exact source | Identity evidence |
| --- | --- | --- |
| TR-D001 | [ZL3b-n.txt](https://voynich.nu/data/ZL3b-n.txt) | Header `Eva-`; internal version 3b dated 2025-05-13. |
| TR-D002 | [IT2a-n.txt](https://voynich.nu/data/IT2a-n.txt) | Header `EvaT`; internal version 2a dated 2023-02-02, modified 2025-06-25. |
| TR-D003 | [GC2a-n.txt](https://voynich.nu/data/GC2a-n.txt) | Header `v101`; internal version 2a dated 2023-02-05, modified 2025-06-25. |
| TR-D004 | [RF1b-e.txt](https://voynich.nu/data/RF1b-e.txt) | Listing links the full variant; header `Eva-`, database generation `D`. |
| TR-D005 | [RF1b-er.txt](https://voynich.nu/data/RF1b-er.txt) | Listing links the basic variant; same alphabet/generation header as full. |

The [extension registry](editions.json) pins GC and both RF variants by SHA-256 and references the accepted [ZL/IT catalog](../../data/transliterations.json). The [aggregate audit](intake-audit.json) records header fields, byte counts, declared/present locus counts, relation/subtype counts, and marker presence. These are direct file observations, not independently verified transcriptions. A matching hash establishes byte identity, not reading accuracy or authenticity. The aggregate report contains no manuscript text payloads.
