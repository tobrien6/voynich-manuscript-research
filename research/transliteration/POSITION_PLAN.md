# Exploratory locus-position analysis plan

This plan is committed before running the position analysis. It is a documented
analysis choice for already exposed public data, not an independent timestamped
preregistration or a held-out decipherment test.

## Motivation and question

Reddy and Knight's [2011 study](https://aclanthology.org/W11-1511/), section 6.2,
reports character distributions at line edges in a Currier-based source. The
present analysis asks a narrower representation-level question: do the first
or last apparent tokens in source-assigned P0 loci differ from the other tokens
in the same loci? It is not a numerical replication of their line/glyph analysis.

## Fixed choices

- Inputs: the exact pinned ZL3b and IT2a files in `data/transliterations.json`.
- Selection: the shared present P0 locations, as in `BASELINES.md`.
- Uncertainty: run all four combinations of split/join uncertain spaces and
  exclude/first-choice alternatives. Exclude unreadable or empty readings.
- Features: literal representation prefix `q`, literal prefix `y`, and EVA
  notation-unit length. No phonetic or glyph identity is inferred from these.
- Positions: test original first and original last token slots separately.
  Require that the boundary slot is retained and that at least one other token
  is retained. Do not promote a later token when a boundary reading is excluded.
- Statistic: for each eligible locus, subtract the mean feature of the other
  retained tokens from the boundary token's feature. Average these differences
  across eligible loci, giving each locus equal weight.
- Control: uniformly permute retained tokens over retained slots within each
  locus. Preserve the token bag, count, exclusions, and locus boundaries.
- Report: observed differences, their exact zero conditional expectation,
  exact conditional variance, and 199 shuffled differences (seed 20261011).
  Use a two-sided exploratory tail with a plus-one correction. Report every
  feature, boundary, source, and uncertainty treatment; do not select only
  favorable outcomes. The comparisons are not independent or multiplicity-adjusted.

## Interpretation limits

Position sensitivity would constrain a mechanism that treats token order as
exchangeable within these units. It cannot by itself identify a language or
cipher. The units are loci, not visually reconstructed manuscript lines, and
the eligibility rule can select different rows across sources and uncertainty
policies. Report denominators and source-assigned paragraph-start counts.

Prior exposure includes the complete source audit and token/repetition baselines.
No candidate decoding rule is being fitted or validated.
