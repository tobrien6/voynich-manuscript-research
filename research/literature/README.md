# Published methods and comparison limits

Question: which published measurements can the project's transcription baselines
actually be compared with, and what must be recovered before replication?

This is a selective methods register, not a literature review or a replication.
The [machine-readable records](methods.json) separate reported methods from
unresolved input details. `L` identifiers refer to research publications and do
not replace the manuscript-image `S` or transcription-publisher `TR` registers.
The inspected paper and supplement hashes identify the **publications**, not the
text corpora used by their authors. No historical corpus has been recovered or
processed in this contribution. PDFs and the supplement are linked, not copied
into this repository.

The separate [self-citation implementation audit](COPYING_MECHANISM.md), with
[source fingerprints and observations](copying-mechanism.json), adds L004 and
an explicit comparison contract for a published copying mechanism. It separates
the paper's abstract claims from inspected release code, configuration, and a
supplied output artifact; no generator execution or mechanism test is reported.

## Three comparisons that need care

| Source | Relevant reported measurement | Comparison limit |
| --- | --- | --- |
| L001: [Reddy & Knight (2011)](https://aclanthology.org/W11-1511/) | Table 2: letter prediction accuracy on held-out word types in their Currier VMS B selection | Percentage correct is not an entropy estimate in bits. Their historical input is not established as the pinned GC2a comparator. |
| L002: [Montemurro & Zanette (2013)](https://doi.org/10.1371/journal.pone.0066344) | Word-location information across partitions of reordered EVA text | Macroscale word-location information has a different unit and context from character entropy or within-locus order. |
| L003: [Amancio et al. (2013)](https://doi.org/10.1371/journal.pone.0067310) | Distinct types with an immediate self-repeat, normalized by shuffled-text mean | The project's equal-adjacent-pair event count and within-locus control answer a different question. |

Detailed input, preprocessing, null, and page/section locators are recorded once
in `methods.json`. In particular, L003's [Supporting Information S1](https://doi.org/10.1371/journal.pone.0067310.s007)
provides a transcription selection and manual parsing instructions. An archive
directory alone does not establish the exact processed sequence.

## Why the counting rule and null both matter

These are synthetic examples constructed here, not observations about the
manuscript or published result estimates.

For `a a a b b a a`, four adjacent-pair **events** are equal. Only two **types**
(`a` and `b`) have an immediate self-repeat. Repeated occurrences of the same
type increase the event count without necessarily increasing the type count.

For two rows `[a, a]` and `[b, b]`, measure equal pairs only within those rows:

| Shuffle scope, same measured edges | Expected equal pairs |
| --- | ---: |
| Independently within each row | 2 |
| Across all four slots, keeping the row edges fixed | 2/3 |

The global-slot expectation follows by enumerating the six distinct placements
of two `a` and two `b`: only `aabb` and `bbaa` contribute two equal row pairs.
The within-row control preserves each row's token bag, making this example
degenerate. Thus an ordering result can change when the conditioning changes,
even before changing the corpus. This toy's fixed-edge global control is not a
reconstruction of L003's whole-text analysis.

The accepted [token baseline](../transliteration/BASELINES.md) counts events on
eligible edges within shared P0 loci and conditions on each locus's retained
token multiplicities. Its uncertainty treatments and excluded slots remain part
of the experiment. The [control generator](../token-controls/README.md) similarly
requires a declared row unit; a locus is not automatically a complete physical
line. Neither result can be relabeled as a published whole-text statistic by
changing its display label.

## Minimum plan for a later replication

The [fixed generator prefix diagnostic](SELF_CITATION_PREFIX_PROFILE.md)
compares a source-informed model profile with an explicitly exposed B cohort.
All 31 control/observer pairs preserve bytes; 24 of 32 related target points
fall outside the finite seed ranges. Unit/context equivalence remains unverified.

1. Select one paper, measurement, table, and null before inspecting new results.
   Freeze the plan and distinguish a historical replication from a test on the
   project's modern inputs.
2. Recover the author's corpus edition and selection. Record original bytes,
   rights, digest, parser version, and every manual exclusion. If the exact
   input cannot be established, label the run an approximation.
3. Preserve a token-to-source mapping and report counts after each parsing step.
   Record uncertain spaces, unreadable tokens, labels, locus/line boundaries,
   page ordering, and any edges introduced by concatenation. Reconcile reported
   counts as diagnostics; matching a count alone does not establish identity.
4. Implement the stated statistic, denominator, null scope, averaging, and
   uncertainty calculation. Test definitions on small enumerated examples.
   For sampled nulls, retain seed, algorithm, all trials, and runtime.
5. Keep the paper-compatible run separate from ZL3b/IT2a sensitivity runs. Change
   input, preprocessing, statistic, and null one at a time on a declared common
   cohort where possible. Report unmatched material and boundary effects.
6. Compare with the specific published table/figure and its precision. Report
   agreement, discrepancy, and unresolved methodological choices. An independent
   researcher should replay the frozen result before it constrains a decoding
   candidate.

This register does not adjudicate the papers' linguistic interpretations.
Statistical compatibility alone supplies neither a glyph mapping nor a
translation. Future hypothesis tests must follow the project's
[evaluation protocol](../DECIPHERMENT_PROTOCOL.md) and disclose prior exposure.

The separate [entropy methods and finite-edge note](../representation/ENTROPY_EDGES.md)
pins Lindemann/Bowern's v2 publication and companion definitions. Its original
synthetic examples distinguish full-character marginals from predecessor
counts on scored edges. It executes no external R or manuscript corpus and
does not reproduce the paper's results.

## Validation and scope

Inspected 2026-10-11 (America/New_York). Article metadata and relevant methods
were checked against the primary publications; the Reddy Table 2, Montemurro
ordering/source sections, and Amancio definition/normalization pages were also
visually checked in the PDFs. L003's publisher-supplied LaTeX supplement was
read as text, including its database and parsing sections. JSON structure,
source locators, downloaded-artifact digests, local links, and both synthetic
examples were checked. No published numerical result or manuscript hypothesis
was independently reproduced. This small selection is not exhaustive.
