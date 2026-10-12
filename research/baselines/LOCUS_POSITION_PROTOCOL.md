# Exploratory locus-position baseline protocol

Recorded 2026-10-11 before computing token-level measures for this analysis.
Commit this protocol before running the manuscript data. This is a local
prospective method record, not an independently timestamped preregistration.
The machine-readable settings are in [locus-position-protocol.json](locus-position-protocol.json).

## Question

For a matched cohort of normal paragraph-text loci, how does the ASCII string
length of the first token compare with the remaining tokens? Does the observed
difference change when uncertain spaces are split versus joined, or when the
paired transliteration edition changes?

This tests the analysis workflow and describes an encoding-level constraint.
It does not identify a language or mechanism and is not a candidate translation.
There is no predeclared directional prediction or fitted decipherment rule.

## Inputs and inclusion

Use the pinned **ZL3b** and **IT2a** sources in
[the source catalog](../../data/transliterations.json), checking their exact
SHA-256 values against the protocol. Retain their distinct alphabet labels and
case. The editions are paired representations, not independent experimental
replicates. Do not pool them.

Use the accepted IVTFF reader and the team's conservative token adapter. The
adapter must preserve certain periods and drawing interruptions as boundaries,
and provide both policies for uncertain commas. It must record excluded loci
instead of choosing alternative readings or filling illegible text. This
baseline accepts only case-preserving ASCII letter tokens; it excludes whole
loci with unresolved alternatives, illegible characters, ligature notation,
extended codes, unsupported annotation, or invalid boundary structure. Free
comments, recognized text tags, paragraph markers, and file-layout whitespace
are handled by the adapter's documented rules, not counted as encoded letters.

Restrict both editions to **P0/P1** loci and **@, +, or *** locators, with at
least two tokens under **every** edition/policy combination. Use the exact
intersection of those eligible locus keys. Publish the included keys and each
source/policy's excluded keys and reasons. This fixed-cohort rule prevents a
change in record membership from masquerading as a spacing-policy effect.

The [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
Tables 8–11 and sections 6.6–6.7, defines the selected locus metadata and
boundary annotations. Its metadata describes relative locus placement; it
does not make every locus an independently checked physical manuscript line.
Call this measure **locus-initial**, not manuscript-line-initial.

## Measurements fixed in advance

For each included locus with token lengths `l[0] ... l[n-1]`, compute:

```text
d = l[0] - sum(l[1:]) / (n - 1)
D = sum(d across included loci) / number of included loci
```

Each locus has equal weight. Report locus/token counts, distinct token strings,
hapax types (strings occurring once), token-length histogram, and the observed
`D` separately for each edition and spacing policy. Length means ASCII letter
count in the encoding: for example, `ch` contributes two letters even if a
different representation would treat the shape as one glyph.

For a conditional token-order null, independently choose a uniformly random
token to be first in each locus. The remaining tokens keep their multiset.
This is equivalent to shuffling token order for this statistic; only the first
position affects the result. It preserves every locus's token count, token
strings, and length multiset. The exact null expectation of each locus contrast
is zero. Compute the exact variance from the finite per-locus alternatives and
the variance of `D` under independent conditional choices.

Use 2,000 deterministic replicates and the seed in the protocol. Use SHA-256
counter draws with rejection sampling to select token indices without a
Python-version-dependent random generator. Include source ID, spacing policy,
replicate index, and locus key in each draw. Report the null mean and the 2.5%
and 97.5% empirical quantiles using linear interpolation. Retain the signed
observed contrast and report its position relative to that reference interval.
Do not label an interval exceedance a validated hypothesis or decipherment.

## Prior exposure and limitations

This chat inspected public source descriptions, existing source-level coverage
audits, parser code, and selected manuscript images before recording the
protocol. The analysis intentionally uses an exploratory whole-corpus cohort;
it creates **no untouched evaluation set**. Publish this exposure and the
exclusions with the result. Any later decipherment candidate must define its
own development/evaluation split and disclose use of this baseline.

The conservative filter may discard systematically difficult or unusual text.
The cohort is not a random manuscript sample. Transcription decisions, locus
layout, paragraph boundaries, and mixed writing traditions may affect the
result. Shuffle expectations are conditioned on the selected encoded tokens,
not a model of the manuscript's production or natural language.

Changing the primary metric, cohort, policies, or randomization after seeing
the result requires a new exploratory version and an explicit explanation.
First report these planned results, including null-looking or contradictory
outcomes. The next test is independent reproduction, followed by a broader
annotation policy and reviewed image/line alignment before making claims about
physical line-position effects.
