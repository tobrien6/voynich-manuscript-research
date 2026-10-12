# Transcription comparator extension

Inspected on 2026-10-11 (America/New_York). This extends the [ZL/IT input decision](DECISION.md) and its shared IVTFF reader with **GC2a native v101** and **RF1b full/basic Eva exports**. It addresses the remaining comparator part of [issue #10](https://github.com/tobrien6/voynich-manuscript-research/issues/10). No normalized corpus, cipher hypothesis, or translation is produced.

## Comparison roles

Keep ZL3b as the provisional primary input and IT2a as the paired comparison described in the initial decision. Add GC2a to test sensitivity to a different transcription alphabet after a documented unit conversion. RF1b supplies a combined reference; its full and basic Eva exports test sensitivity to representation loss. The maintainer states that RF combines ZL and GC, so RF is **not an independent third witness**. These roles follow [the publisher's provenance descriptions](https://voynich.nu/transcr.html), not an asserted accuracy ranking.

All five exports are pinned in [the source catalogue](../../data/transliterations.json), with separate identifiers, URLs, credits, exact bytes, and SHA-256 digests. Their unchanged source bytes are in `data/raw/`; `.gitattributes` preserves the hashes through checkouts. The publisher's [CC0 statement](https://voynich.nu/roadmap.html) covers the collected transliterations linked from the edition tables. This statement does not cover Yale images or the site's fonts. [Documentation provenance](comparator_documentation.json) identifies the inspected edition page, format PDF, and license page.

## Reproducible file observations

The [annotation figure](figures/README.md) shows the five exports' retained
notation with exact counts, coverage denominators, and reproducible PNG/SVG
outputs. It visualizes the same verified profiles used below.

The [extended coverage audit](coverage_audit.json) uses the existing shared reader to retain page/locus metadata and distinguish present from explicitly nonexistent records. The [comparator profile](comparator_profiles.json) adds annotation occurrence counts. All counts below are computed from the pinned files, not new manuscript observations.

| Export | All records | Present records | Uncertain commas | Alternative groups | Paragraph starts | High-ASCII escapes | Ligature groups |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ZL3b | 5,385 | 5,385 | 2,748 | 817 | 740 | 178 | 446 |
| IT2a | 5,215 | 5,214 | 0 | 0 | 772 | 0 | 0 |
| GC2a | 5,367 | 5,366 | 2,459 | 0 | 775 | 341 | 0 |
| RF1b-full | 5,385 | 5,385 | 677 | 0 | 0 | 4,125 | 759 |
| RF1b-basic | 5,385 | 5,385 | 677 | 0 | 0 | 0 | 0 |

Annotation counts use **present records only**. IT and GC each retain one record with a `!` locator, which the format marks as nonexistent; those records remain in the all-record denominator but are excluded from annotation totals. A `!` inside a v101 text body remains an alphabet character rather than changing record status.

These measurements expose two processing risks:

- RF full and basic have **identical headers and present-location coverage**, but distinct file hashes and annotation representations. The full export retains high-ASCII escapes and ligature groups; the basic export has none. Header checking alone cannot identify the chosen export.
- RF has no paragraph-start markers and no explicit alternative groups in these exports. Their absence does not establish that paragraph structure or uncertain readings are absent from the manuscript. Derive any later segmentation or uncertainty policy from recorded sources rather than filling it in implicitly.

Zero counts mean absence of the corresponding file notation. A bracketed group is one annotation, not a count of ambiguous glyphs. A comma is a raw annotation occurrence, including commas within alternative groups. Runs of question marks are reported by run length; `???` must not be interpreted as exactly three unreadable glyphs. Native Eva/v101 characters, high-ASCII escape strings, and manuscript glyph units are different objects. No glyph or word counts are computed here.

The new audit reuses `scripts.ivtff` and `load_sources` rather than defining a competing reader. It removes inline comments/tags from text-marker counts while counting paragraph and drawing-interruption annotations separately. Full-line comments do not enter the text bodies. Unexpected angle-bracket annotations fail explicitly. It does not validate every glyph/ligature/alternative syntax rule.

## Format and alignment constraints

The retrieved [IVTFF specification](https://www.voynich.nu/software/ivtt/IVTFF_format.pdf) is document issue 2.0.2 (8 July 2025), describing format 2.0.1. All five files declare `2.0` in their headers; the reader also handles the later `!` locator used by current exports. Keep documentation issue, file-format header, dataset edition, and export representation separate.

Before normalized tokens are emitted, state comma split/join policies; preserve uncertain alternatives and unreadable material; treat high-ASCII escapes and ligatures deliberately; and retain drawing interruptions as boundaries. The format gives `<->` and `<~>` separator meaning, so removing their notation must not concatenate adjoining text. RF needs a sourced paragraph policy. These distinctions come from specification sections 5.6 and 6.4-6.7; they do not supply a decipherment.

Transcription page names may identify foldout panels while a Yale canvas contains several panels. Coverage equality does not resolve image-region alignment. The crosswalk work should map the retained identifiers separately; no legacy 117v-to-current-116v alias is inferred here.

## Validation and prior exposure

Run from the repository root with Python 3.10 or later:

```sh
python3 scripts/audit_transliterations.py --check research/transliteration/coverage_audit.json
python3 scripts/audit_transcription_comparators.py --check research/transliteration/comparator_profiles.json
python3 -m unittest discover -s tests -v
```

Both audit commands verify source bytes before reading them and reproduce the committed reports offline. The tests cover annotation-like punctuation in comments, v101 punctuation, nonexistent-record exclusions, malformed inline comments, source-byte drift, shared-reader structure, and the two RF exports' differing representations. Tests use invented records or the licensed pinned inputs.

This is an exploratory, full-corpus input audit. The pilot images were already inspected, and source headers, structural counts, annotation totals, initial source lines, and excerpts from a raw-file PR diff were exposed during this work. No token-frequency, statistical-mechanism, or decoding fit was run. A later evaluation split must record these exposure types; do not call the whole pilot or these inspected resources untouched.

## Limits and next test

Related sources are correlated; matching coverage is not evidence of transcription accuracy. The audit does not adjudicate glyphs against images, convert v101 to Eva, normalize tokens, or test linguistic content. The extended/baseline exports' information differences are a reason to perform sensitivity checks, not a conclusion about what the manuscript says.

Next, implement an annotation-aware token adapter using the shared reader and synthetic fixtures, with explicit alphabet and uncertainty policies. Freeze a development/evaluation split and a structural prediction before reporting a result. Check conclusions against paired present loci, comparator editions, and appropriate controls, preserving failed comparisons and exclusions.
