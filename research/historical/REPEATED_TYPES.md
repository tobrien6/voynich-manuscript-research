# Repeated types under a global frequency null

Question: how do distinct types with a self-repeat and equal-pair events compare
under the same global null on the four approximate H reconstructions?

The [plan](REPEATED_TYPES_PLAN.md) and [machine parameters](repeated-types-plan.json)
were committed before the assay. The [complete report](repeated-types.json)
retains both statistics, exact means, all ten controls per variant, source and
method hashes, and boundary/asterisk diagnostics. The inputs retain their
[parsing discrepancies](PARSING.md); none is verified as the authors' processed
corpus. This is an exploratory source-defined assay, not an exact replication
of [Amancio et al. (2013)](https://doi.org/10.1371/journal.pone.0067310).

## Observations

A counts every equal adjacent-pair event; B counts each repeating token type
once, following the paper's Methods definition. These statistic names do not
select Currier A/B sections. All N−1 edges of each surviving whole-text stream
are measured, including joins between different native records.

| Ring treatment | f66r removed unit | N | Pair events A | Exact E[A] | Repeated types B | Exact E[B] | B / E[B] |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Omit R2 | M | 37,759 | 313 | 116.54 | 114 | 47.52 | 2.399 |
| Omit R2 | L | 37,776 | 314 | 116.56 | 115 | 47.56 | 2.418 |
| Remove ring singletons | M | 37,713 | 314 | 116.52 | 114 | 47.46 | 2.402 |
| Remove ring singletons | L | 37,730 | 315 | 116.53 | 115 | 47.50 | 2.421 |

Both counts exceed their corresponding global-null means in every declared
variant. All ten sampled B values in each variant are below its observed B.
Their means are 46.1, 45.5, 45.7 and 47.3, respectively. These deterministic
trials are fully retained; ten samples do not provide a finely resolved tail,
and no calibrated significance claim is made.

Within native records there are 304 or 305 equal-pair events and 113 repeating
types. Cross-record joins contribute 9 or 10 events and 6 or 7 types, with five
types overlapping the within-record set. The total B is therefore 114 or 115,
not the sum of those two type counts. Record IDs do not establish physical
manuscript lines or independently sampled text units.

The singleton treatments have 13 within-record edges crossing gaps in their
pre-manual normalized indices; one is an equal pair. These indices do not
capture earlier syntactic deletions. No observed repeating type contains an
asterisk in any variant. That limited diagnostic does not adjudicate glyphs or
remove the effects of other normalization uncertainties.

## Exact expectation and validation

For one type with c occurrences, every c-position subset is equally likely
under a uniform multiset permutation. Nonadjacent subsets number C(N−c+1,c).
Subtracting their proportion gives the probability that the type repeats.
Summing those probabilities uses linearity of expectation, without assuming
independence between different types. The [plan](REPEATED_TYPES_PLAN.md) provides
the formula and impossible-placement/empty-stream conventions.

`scripts/global_repeated_types.py` groups frequency classes and computes exact
rational means for B and A. It also separates overlapping pair events from
deduplicated types. Rationals are stored as hexadecimal numerator/denominator
strings, with decimal approximations for display; the process's integer-string
safety limit remains unchanged. The report does not supply a B variance or tail.

Eight core tests verify the formula against exhaustive distinct permutations of
eleven small multisets, plus case/relabeling, empty/forced-repeat boundaries,
asterisk diagnostics, record/gap overlap, seeded replay, multiset preservation,
strict seed input and large-rational round-trip. Five runner tests cover complete
trial retention, undefined denominators, both corpus hashes, dependency drift
before reconstruction, and output protection/failure preservation.

The runner replays the frozen parser and validates all four record/flat corpus
hashes before analysis. It reuses the accepted SHA-256 counter/Fisher–Yates
primitive under an explicitly declared whole-text frame, with seed 20261012 and
trials 0–9. Every control begins from the original token stream and preserves
its frequency bag. The script, metric helper and frozen dependencies are pinned.

## Reproduce

Python 3.10+, standard library only; recorded run used Python 3.14.3. From the
repository root at the reviewed study commit:

```sh
python3 scripts/historical_repeated_types.py --output research/historical/repeated-types.json
python3 scripts/historical_repeated_types.py --check research/historical/repeated-types.json
python3 -m unittest tests.test_global_repeated_types tests.test_historical_repeated_types -v
```

The full report and all forty control rows replay exactly. Source/dependency
drift fails before measurement; do not refresh a frozen pin merely to make a
later checkout pass. Restore the reviewed dependency versions when needed.

## Comparison limits and next test

The accepted [modern pair baseline](../transliteration/BASELINES.md) uses shared
P0 loci, explicit eligible slots and conditional within-locus frequency bags.
This assay uses a different H input and includes native-record joins under a
whole-text frequency bag. The [modern fixed-gap repeated-type work](https://github.com/tobrien6/voynich-manuscript-research/pull/119) likewise
conditions within loci and deduplicates types across that cohort. Keep these
corpora, edge populations and conditioning rules separate; differences between
these studies do not isolate a change of statistic or establish a contradiction
with earlier results.

A global shuffle removes local composition and layout clustering along with
order. Further work should test matched input/edges with explicitly conditioned
controls, or compare preregistered language/synthetic mechanisms. Retain the
original parser/input recovery requirement and every prior negative result.

The four variants share exposed source material and are not independent
replications. Literal token equality is not a verified linguistic word or glyph
identity. Neither these mean contrasts nor the sampled controls identify a
language, explain a cipher, validate a decoding rule, or provide a translation.
