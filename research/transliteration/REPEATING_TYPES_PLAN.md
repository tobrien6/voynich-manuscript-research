# Distinct repeating representations under the existing locus control

Written before computing new manuscript repeating-type counts. Source text,
pair-event baselines, distance profiles, and the published measurement definition
are already exposed. This is an exploratory analysis plan, not preregistration
or an untouched evaluation.

Question: how does counting each representation with any immediate self-repeat
once change the description supplied by the accepted adjacent-pair event count?
The distinction is recorded in `research/literature/README.md`; Amancio et al.
(2013), Materials and Methods / First-order statistics, define a type count.
Their historical input and shuffled-text normalization remain separate from
this modern-source, within-locus analysis.

Use the same intersection of present P0 loci in pinned ZL3b and IT2a as
`BASELINES.md`, with all four split/join and exclude/first treatments per source.
Reuse the accepted tokenizer and retention policy. Preserve original excluded
slots, boundaries, case and representations. Never concatenate loci or promote
them to physical lines. Do not change any accepted report or recorded shuffle.

For observed counts, score equality only on retained endpoints of consecutive
original slots within one locus. Count every equal-pair event, and separately
the number of distinct representation strings producing at least one such
event anywhere in the selected cohort. Multiple events or loci for one string
still contribute one repeating type. These strings are not decoded words.

The stipulated control independently permutes each locus's retained bag while
keeping exclusions fixed. For a type with c occurrences among m retained slots,
its c-position subset is uniform over C(m,c). No equal adjacent pair of that
type occurs exactly when those positions form an independent set in the graph
of eligible original-slot adjacency. This graph consists of retained-slot paths.
For a path of length l, the size-k independent-set count is C(l-k+1,k) when
0 <= k <= ceil(l/2), and zero otherwise. Multiply these polynomials for the
path components and extract coefficient z^c, then divide by C(m,c).

For each representation, multiply its no-repeat probabilities across the
independently shuffled loci where it occurs. Expected distinct repeating types
is the sum of one minus those products. This uses linearity of expectation;
different type indicators are generally dependent. Do not infer a variance,
normal tail, significance, confidence, language, or copying mechanism from
the mean. No resampling, ratio-to-mean decision threshold or favored policy is
specified. Report observed minus expected as a count only.

Retain exact fractions and rounded diagnostics, cohort/source/plan/engine and
preprocessed-slot pins, vocabulary size, repetition-capable type count, and the
observed distribution of event counts per repeating type. Reproduce accepted
pair counts, denominators and expectations in every treatment as integration
checks. Include all treatments and failed or contradictory contrasts.

Validate independent-set coefficients by direct subset enumeration for short
paths and path-component unions, then validate expected corpus type counts by
exhaustive independent locus permutations with fixed gaps. Include global
deduplication, constants, distinct bags, empty edges, exclusions and invalid
inputs. Reproduce the complete report. Guard output aliases of every supplied
calculation input, code file, plan and the accepted baseline.

This implements a counting distinction on an exposed modern cohort under a
different conditional control. It is not a numerical replication of the paper,
a test of natural-language compatibility, a real held-out split, glyph
adjudication, decoding, or translation. A later paper/generator comparison must
match input, counting unit, boundaries and null scope explicitly.
