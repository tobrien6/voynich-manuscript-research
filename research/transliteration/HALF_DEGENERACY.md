# Exact invariance under the early/late controls

The primary ZL3b split treatment has **55** loci whose adjacent-length statistic
cannot change under any allowed early/late permutation. The
[accepted half-position analysis](INTERIOR_HALVES.md) correctly reports the
narrower count of **41** loci with two individually constant halves. The extra
14 are nonconstant-half cases with an invariant statistic. This supplement
classifies them exactly and preserves the accepted 2,165-locus denominator,
all statistics and all control draws.

## Question, sources and chronology

The [plan](HALF_DEGENERACY_PLAN.md) was committed at `525f477`; the
synthetic-verified implementation was committed at `5ea7f0c` before inspecting
the manuscript classifications. This is a diagnostic on previously exposed
ZL3b/IT2a material, not a registered decoding hypothesis or unseen evaluation.
The later size-frequency fields report the lengths of the classified interiors
without changing the decision rule.

The program checks source bytes through the accepted catalog loader, then
recreates the parent selection, exclusions, source pins, length-corpus digests
and treatment denominators. It requires the exact parent report SHA-256
`d3ada06de64c80f315ea6fa38f71f25158857cdf0d2a34728d1c6fc6ad7b6a6c`
and accepted half-control report SHA-256
`6b239d3a7b52018f6f71bffb07f40df9347bf3c1bf964387378e8c926ce94d6c`.
Source references, original preprocessing and exclusions remain those of
[the interior-order analysis](INTERIOR_ORDER.md).

## Exact test

Each permitted permutation preserves the squared deviations and normalization
of the statistic. With `d[i] = m*x[i] - sum(x)`, only
`A = sum(d[i]*d[i+1])` can change. Swapping neighboring values `a` and `b`
changes `A` by `(b-a)*(left-right)`; a missing chain neighbor contributes zero.
Adjacent swaps within each half generate every allowed arrangement.

The algorithm therefore checks all feasible unequal swapped values and their
neighbor values at every within-half pair position. It enforces occurrence
multiplicities after reserving the swapped pair, including when both neighbors
come from the same block. Every feasible nonzero change can be completed to
two full permitted arrangements; these are constructed and their exact integer
numerators checked. If none exists, every generator step has zero change, so
the statistic is invariant across the complete permitted set. This avoids
factorial enumeration without replacing it with a Monte Carlo approximation.

For example, interior lengths `[1,3,2]` have nonconstant early lengths `[1,3]`
and a singleton late length `[2]`. Swapping the early pair changes its order
but leaves the numerator fixed because the late centered deviation is zero.
The plan records this example before manuscript classification.

## Results

| Treatment | Both halves constant | All invariant loci | Additional invariant loci | Loci with a verified variation witness |
| --- | ---: | ---: | ---: | ---: |
| ZL3b split, primary | 41 | **55** | 14 | 2,110 |
| ZL3b join | 54 | **73** | 19 | 2,092 |
| IT2a split | 45 | **58** | 13 | 2,107 |
| IT2a join | 45 | **58** | 13 | 2,107 |

Every row sums invariant and varying counts to **2,165**. The IT treatments
share the same numerical input and classification; they are dependent.
The [complete diagnostic](half_control_invariance.json) retains every invariant
identifier, every additional identifier, interior-size frequencies and the
source/parent/plan/cohort identities. Identifiers name transcription loci,
not independently aligned physical lines or leaves. No source text is copied.

## Reproduce and interpretation

```sh
python3 -m unittest discover -s tests -p 'test_half_control_invariance.py' -v
python3 scripts/half_control_invariance.py --check research/transliteration/half_control_invariance.json
```

The tests independently enumerate all permitted orders for every one of the
3,267 integer vectors of sizes 3–7 over `{1,2,3}`. They check exact agreement,
the validity of every returned witness, constant and nonconstant invariants,
affine changes, multiplicities, invalid inputs, complete denominators, identity
pins and protection against overwriting either parent report, the plan, catalog
or source files. The size-seven cases include two neighbors in a four-element
block, where independent draws would incorrectly reuse an occurrence.

As a separate source-level check, unique multiset permutations of every
classified invariant interior were enumerated with a recursive occurrence
counter and an independent numerator calculation. All 55 / 73 / 58 / 58
identifiers remained invariant across 69 / 92 / 71 / 71 unique allowed orders.
Every other locus's constructed witness preserved both block multisets and
changed that independent numerator. The complete diagnostic also replays
byte for byte through both the script and package entry points.

An invariant locus contributes zero after subtracting its exact conditional
expectation. It remains in the accepted effect denominator. This diagnostic
does not recalculate effects, discard loci, run new draws or change p-values.
Invariance is a property of the control model and source notation lengths;
it establishes no glyph identity, physical alignment, mechanism or reading.
The next step is a separately justified finer position model, preserving the
accepted sensitivity analysis's alternatives and exploratory limits.

## Independent moment check

The [exact half-control moment audit](HALF_MOMENTS.md) independently reproduces
every invariant identifier through zero exact variance, without calling the
swap classifier. It retains all loci and changes no accepted classification,
effect or tail.
