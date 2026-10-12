# Primary Currier / Eva conversion definition

An independently supplied conversion definition is available from René
Zandbergen's [Bitrans directory](https://www.voynich.nu/software/bitrans/).
This intake pins that definition and its documentation for a future frozen
notation test. **No manuscript corpus is converted or compared here.** It
does not authenticate Reddy's 2011 preprocessing, a historical rule snapshot,
glyph values or a decipherment.

## Retrieved sources and scope

The [complete metadata catalog](currier-conversion-source.json), source TR005,
records all identities, rule-row hashes, prefix relationships and synthetic
round-trip failures. Inspected 2026-10-12 (America/New_York):

| Primary artifact | Retrieved bytes | SHA-256 |
| --- | ---: | --- |
| [Curr-Eva_def.bit](https://www.voynich.nu/software/bitrans/Curr-Eva_def.bit) | 308 | `31105cb66e966bc7532c58178a867bf5b090c0473f047a3fdd30ee84bd339d32` |
| [Bitrans_manual.pdf](https://www.voynich.nu/software/bitrans/Bitrans_manual.pdf) | 1,162,524 | `6873c33d6a093241ceb7cc2796ea8728068a2e390d5de01d22d3a4e2ea186564` |
| [000_README.txt](https://www.voynich.nu/software/000_README.txt) | 6,926 | `9a13f09914ecb927b430af8967df4472317e1c491c887569892aaa38a335d176` |

The directory lists the rule file as last modified `2025-12-05 16:05`, without
a timezone. The PDF identifies document/software version 1.5 and gives the
literal issue date `06/12/2025`; it has 28 PDF pages. Relevant text on printed
pages 3, 5–7, 11–13, 16–17 and 21–22 was inspected; page 21's rules-format layout was
also rendered and visually checked. These are current retrieved bytes, not an
immutable publisher release or evidence of the rules used in 2011.

The author's README describes the file as the exact Currier/Basic Eva
definition, restricted to Eva codes defined by Currier. It supplies a concrete
source for a comparison rule without fitting one from manuscript word pairs.
The `Eva-` alphabet label does not mean an incomplete conversion flag: the
manual's alphabet table uses it for basic or extended Eva. The definition's
coverage still needs separate inspection.

## Observed definition and processing requirements

The ASCII file has 42 LF-terminated physical lines, including its final
newline. Four leading records declare the header, separator-context marker
and two comment protections. Its column codes are `Curr` and `Eva-`, without
a header direction restriction. Angle-bracketed material and hash-led full
lines are protected; the full-line definition includes its trailing space.
The percent sign selects the context separator marker; it is not a command to
delete percent signs from a transcription.

IVTFF headers have a documented exception: matching alphabet codes can be
rewritten despite hash-line protection. Strict mode rejects mismatches;
non-strict mode warns and keeps the header code (section 3.6, pages 12–13).

There are 38 distinct entries in each column. Every Currier entry is one
codepoint; Eva entries have the following lengths:

| Eva definition length | Rules |
| --- | ---: |
| 1 | 20 |
| 2 | 6 |
| 3 | 8 |
| 4 | 4 |

Thirteen ordered proper-prefix relationships occur among the Eva strings;
their physical rule-line pairs are all retained in the catalog. This makes
replacement order material to a naive sequence of substitutions.

The [manual](https://www.voynich.nu/software/bitrans/Bitrans_manual.pdf),
sections 2.2–3.2, 3.5–3.6 and 5, specifies case-sensitive, noncumulative
substitution with larger-group priority. Its left-to-right clause concerns
repeated occurrences of the same rule. Equal-length overlapping rules can
depend on file order, and rule-block separators alter priority (section 3.8,
pages 16–17). Direction 2 uses the right column as input. Header alphabet checks,
protected comments,
boundary markers and whole-text reversibility are separate concerns. A future
implementation must declare those semantics and its unmatched-symbol policy;
replacing entries in arbitrary sequence is insufficient.

As a simple membership probe, five characters in the historical normalizer's
permitted `a-z`/asterisk universe appear nowhere in the right-column strings:
asterisk and `b`, `u`, `w`, `z`. This universe is a parser acceptance set,
not an asserted list of official basic Eva characters. Presence anywhere in
a rule string also does not prove that a character has a standalone rule.
Neither this file nor its row uniqueness justifies discarding symbols or
replacing unmatched material with uncertainty marks.

Incomplete-substitution reporting is separate from conversion (section 3.9,
page 17). This diagnostic has zero unmatched characters, so it does not test
its fallback on arbitrary text. A future candidate must freeze handling and
completeness checks.

## Complete synthetic round-trip diagnostic

All 1,444 ordered pairs of the 38 Currier rule codes were expanded by
concatenating their Eva definitions, then parsed from left to right using the
longest matching Eva definition. This original small diagnostic executes no
downloaded author program and uses no manuscript words. Of those cases,
**1,432 round-trip and 12 do not**. Every failed input-rule-line pair and its
input/intermediate/returned hashes and lengths are retained, without selecting
only one successful or failed class.

For example, the synthetic two-code string `ID` expands to `in`, whose greedy
reverse interpretation is `N`. This is a string-segmentation ambiguity despite
both columns having unique entries. It demonstrates why per-row uniqueness
and a bidirectional header do not prove that every possible string round-trips.
It neither identifies an actual manuscript token nor reproduces Bitrans's
complete behavior on arbitrary annotated input.

A second diagnostic used a prefix trie, rather than a list of matching
definitions. It independently reproduced every one of the 1,444 outcomes and
all twelve failure descriptors. Raw file length/hash and all 38 row identities,
column lengths/uniqueness and thirteen prefix pairs were checked separately.
These checks validate the source inventory and stated synthetic calculation;
they are not a corpus conversion experiment.

## Reuse and next test

The three raw source artifacts remain local. This intake establishes no
redistribution license for the rule/manual/README and does not extend the
publisher's separate transliteration-dataset CC0 statement to them. It adds
original metadata, limited factual examples and source-linked paraphrases.
No author C program or binary was downloaded or executed.

Retrieve the three exact URLs into a local reference directory and compare
their bytes and hashes to `artifacts` in the catalog. Rule-row hashes use the
ASCII physical line without its LF; column hashes use the individual ASCII
string. Rows 5–42 are the substitution entries. The synthetic failure ledger
identifies input codes by their rule-line numbers, so the calculation can be
repeated from those locally retained bytes without a published mapping copy.

Before comparing any source streams, freeze the direction, greedy tokenization,
case/annotation handling, permitted input alphabet and treatment of unmatched
symbols. Keep historical code deletion and manual exclusions separate from
notation conversion. Require exact input identity and preserve contradictions,
source boundaries and all uncertain positions. A source-backed conversion
definition is a notation candidate, not a verified glyph or language model.
