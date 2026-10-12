# Exact moments for the interior-half control ensemble

An exact calculation independently reproduces **every invariant locus
identifier** in the accepted [swap audit](HALF_DEGENERACY.md): 55 ZL split,
73 ZL join, and 58 in each IT treatment. On the unchanged 2,165-locus cohort,
the original 999-control empirical standard deviations are 0.978–1.026 times
the ideal permutation-ensemble standard deviations. The finite controls and
their recorded tails remain unchanged.

This is an exposed-data mathematical audit of the
[accepted half-position study](INTERIOR_HALVES.md). It supplies exact
conditional first and second moments; it supplies no new tail probability,
normal approximation, physical ordering mechanism, reading, or translation.

## Inputs and ensemble

Use the original shared conservative P0 selection in pinned ZL3b/IT2a,
both split/join spacing policies, plain ASCII notation lengths, and identical
exclusions. Each locus's original first/last source-token slots stay outside
the interior statistic. Divide its m interior positions at ceil(m/2), then
independently and uniformly permute original occurrences within each half.
Equal lengths are still separate occurrences. All invariant and constant loci
remain in the equal-locus denominator.

The calculation concerns an **ideal uniform occurrence-permutation ensemble**.
The accepted 999 hash-generated controls form a separate, deterministic finite
empirical measure. Their empirical variance is not the exact ideal-ensemble
variance. Independent locus permutations are stipulated by the control; they
do not make manuscript loci, folios, images, sources or spacing treatments
independent observations. IT split/join have identical numerical inputs.

The producer pins all three accepted reports, the source catalog, parser,
tokenizer, conservative adapter and imported analysis/control helpers. It
rebuilds every vector and verifies the complete original selection, source
identity, length-corpus digest, denominator and accepted observation before
calculating any new second moment. The [complete report](half_control_moments.json)
records every input pin, the plan and implementation identity, all four
treatments, and exact per-locus moments. Original source tokens and manuscript
images are not included in this supplemental report. Source credits and reuse
terms remain in the [accepted catalog](../../data/transliterations.json) and
[source decision](DECISION.md).

## Calculation and independent checks

Set d[i] = m*x[i] - sum(x), D = sum(d[i]^2), and
Q = sum(d[i]*d[i+1]). The uncentered association is
m*Q/((m-1)*D), with the accepted zero convention for D=0.
Half-centering subtracts a fixed mean and leaves variance unchanged.

For a product on k distinct positions within a block, sum injective
assignments of its original occurrences and divide by the falling factorial
(n)_k. A subset dynamic program tracks which labelled positions have been
filled: each occurrence may be unused or occupy one unfilled position, with
its value raised to that position's exponent. Every update reads the previous
occurrence's states, preventing reuse of an occurrence. At most four positions
and total degree four are needed.

Sum block-product moments across chain edges for E[Q]. For E[Q^2], sum across
all **ordered** edge pairs, combining exponents at shared positions. This
includes identical edges, shared-vertex edges, disjoint edges and cross-half
edges. Block independence permits multiplication of early/late moments.
Integer/Fraction arithmetic gives Var(Q)=E[Q^2]-E[Q]^2 and the normalized
variance after multiplying by (m/((m-1)*D))^2.

The first moment equals the accepted half-expectation formula exactly at every
locus. On the finite positive-weight support, zero exact variance is equivalent
to a constant statistic. Its full identifier set equals the independently
derived accepted swap-feasibility set. The moment calculation does not call
that classifier. Under the stipulated independent locus ensemble, variance
of the equal-locus mean is sum(locus variances)/2165^2, including every zero.

Before manuscript calculation, 11 tests passed, including all **3,267**
vectors of sizes 3–7 over {1,2,3} against complete occurrence permutations,
and **3,918** signed block-moment cases against direct injective assignments.
They also cover singleton/repeated/constant cases, affine invariance of
normalized variance, input immutability, denominator weighting, malformed
inputs, changed pins and output protection.

A separate power-sum calculation checked all **8,660** recorded locus moment
sets and all four exact aggregate variances after generation. It decomposed
Q into the two within-half chains and their connecting edge, using explicit
same-edge/shared-edge/disjoint-edge formulas rather than the production subset
algorithm or its geometric-pattern counter. Both methods agree exactly.

## All source/spacing results

All values below are approximate standard deviations of the equal-locus mean
in association units. Their squares are variances; no tail is inferred.

| Treatment | Exact zero-variance loci | Ideal ensemble SD | Original empirical SD | Empirical / ideal SD |
| --- | ---: | ---: | ---: | ---: |
| ZL3b / split | 55 | 0.005827848847 | 0.005977390668 | 1.025659866 |
| ZL3b / join | 73 | 0.005884180256 | 0.005753739806 | 0.977832010 |
| IT2a / split | 58 | 0.005868070853 | 0.005829790665 | 0.993476529 |
| IT2a / join | 58 | 0.005868070853 | 0.005829790665 | 0.993476529 |

This comparison describes finite-control spread around the ideal control
scale. It neither proves uniformity of hash-generated draws nor supplies an
uncertainty interval for their SD ratio. The four treatments share text, and
the two IT rows are identical, so they are not four independent replications.

## Reproduce and chronology

Python 3.10 or later, standard library only:

```sh
python3 -m unittest discover -s tests -p test_half_control_moments.py
python3 scripts/half_control_moments.py --check research/transliteration/half_control_moments.json
python3 -m scripts.half_control_moments --output /tmp/half-control-moments.json
```

Script and package entry points regenerate identical report bytes. Exact
per-locus fractions use decimal numerator/denominator strings. The larger
aggregate fraction uses explicitly labelled base-16 integer strings; restore
it with `Fraction(int(record["numerator"], 16), int(record["denominator"], 16))`.
A separate 60-significant-digit decimal presentation and all SDs/ratios are
approximations. A synthetic 9,001-digit aggregate round-trips without changing
interpreter integer-string limits, including under decimal precision 1 and
a different ambient rounding mode. On integration with accepted main `bfdc64c`,
all 668 tests under `tests/` and nine legacy script tests pass (677 total).

Direct paths, symlinks and hardlinks to all inputs, code and the plan are
rejected before calculation and immediately before writing. Temporary-only
tests cover each protected class, including aliases created during calculation
and optional check-file aliases. Serialization finishes before the final
guard. This is not an atomic filesystem guarantee.

The [plan](HALF_MOMENTS_PLAN.md) was remotely published at `0258255` and
the synthetic-verified implementation/tests at `45a5a46` before the first new
manuscript variance calculation. These records concern an already exposed
corpus and existing controls, rather than an independent preregistration or
untouched evaluation. No accepted effect, selection, source, control, tail or
classification is revised. A prospective mechanism comparison still requires
specified predictions and exposure-valid evidence beyond this diagnostic.
