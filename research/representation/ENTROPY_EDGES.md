# Entropy estimates need the same counting population

For the invented two-label sequence `ab`, there is one observed successor:
`a` is followed by `b` with certainty. Its empirical conditional successor
entropy is zero. Subtracting full-label entropy from pair entropy instead gives
**-1 bit**, because those two tables describe different populations. A negative
value here is a difference between estimates, not a negative conditional entropy.

This synthetic check complements the [reversible encoding example](ENTROPY_SANITY.md).
That example changes representation units; this one holds atomic units fixed
and changes the marginal counting population. The
[plan](ENTROPY_EDGES_PLAN.md), committed at `8d3757e`, fixes all six examples
before report generation. No manuscript data or external R code is executed.

## Source-method and version audit

Lindemann and Bowern's [arXiv v2 paper](https://arxiv.org/abs/2010.14697v2),
section 4.1, describes `h2` as next-character entropy conditioned on the preceding
character. Figure 7 includes spaces. Its retrieved PDF title page is dated
20 May 2021 and reports 311 Wikipedia samples, while the unversioned arXiv HTML
abstract reports 294. The [source record](../literature/entropy-methods.json)
pins the identified artifacts rather than treating those summaries as equivalent.
Printed pages 1, 23 and 24 were visually inspected. These are reported methods
and version facts; no numerical or linguistic result is reproduced here.

At companion revision `decc4caaa6515b86e42a219d1da8d81114736f2e`,
[`sumentropy`](https://github.com/chirila/Voynich-public/blob/decc4caaa6515b86e42a219d1da8d81114736f2e/R%20code/Entropy_Functions.R#L22)
normalizes full characters and qgrams separately, then subtracts `H1` from `H2`.
[`condbigram`](https://github.com/chirila/Voynich-public/blob/decc4caaa6515b86e42a219d1da8d81114736f2e/R%20code/Entropy_Functions.R#L73)
divides pair counts by full-character counts. Space replacement is the default;
removal is optional. The
[statistics driver](https://github.com/chirila/Voynich-public/blob/decc4caaa6515b86e42a219d1da8d81114736f2e/R%20code/2_Create_Voynich_Stat_File.Rmd#L106)
passes each named document to `multi_stats`, which calls `sumentropy`.
The pinned source is evidence about its algebra, not an established publication
run revision or executed package behavior. Package versions and exact processed
corpus identity remain unresolved.

## Finite-edge derivation

Take one finite sequence of `N >= 2` labels with no padding or wraparound.
There are `E = N - 1` observed directed pairs. Write `n[i,j]` for the count of
`i → j`, `n_out[i]` for its sum over successors, and `n_full[i]` for the count
of `i` among all `N` labels. Only the last occurrence has no successor.

The empirical joint distribution on edges is `n[i,j]/E`; its predecessor
marginal is **`n_out[i]/E`**. The matching-population chain rule is:

```text
H(next | predecessor; edges) = H(pairs; E) - H(predecessors; E)
                            = -sum n[i,j]/E * log2(n[i,j]/n_out[i])
```

The [existing conditional helper](../../scripts/representation_entropy_demo.py)
uses that scored-edge population for context order one. In contrast,
`H(pairs; E) - H(full labels; N)` differs by
`H(predecessors; E) - H(full labels; N)`. Those marginals need not have the
same empirical entropy. This difference is retained, without clipping.

Likewise, values `n[i,j]/n_full[i]` have row mass
`n_out[i]/n_full[i]`. At the last label's row this is `1 - 1/n_full[i]`, including
zero when that label occurs only at the endpoint. Those values therefore do
not form normalized successor distributions in this finite-edge example.
Conditioning on observed successor opportunities uses `n_out[i]` instead.

## Fixed synthetic observations

All units below are invented atomic labels, one ASCII letter each. Counts do
not cross examples, and no spaces, words, source exclusions or glyph units
are inferred. Both formula variants and their complete counts are retained
in [entropy_edge_accounting.json](entropy_edge_accounting.json).

| Sequence | Units | Edges | Pair entropy minus full-label entropy | Conditional successor entropy on edges |
| --- | ---: | ---: | ---: | ---: |
| `ab` | 2 | 1 | -1.000000 | 0.000000 |
| `aab` | 3 | 2 | 0.081704 | 1.000000 |
| `aba` | 3 | 2 | 0.081704 | 0.000000 |
| `abba` | 4 | 3 | 0.584963 | 0.666667 |
| `aaaa` | 4 | 3 | 0.000000 | 0.000000 |
| `abcabc` | 6 | 5 | -0.063034 | 0.000000 |

Both columns are in bits, but the right column conditions on actual successor
edges. `aab` has two successors after `a`, equally split between `a` and `b`,
so its conditional value is one bit. In `aba` each predecessor has one
deterministic successor, so its conditional value is zero. The difference
column alone cannot distinguish those cases as a normalized conditional estimate.

## Reproduce, limits and next test

Python's standard library is sufficient:

```sh
python3 scripts/entropy_edge_accounting.py --check research/representation/entropy_edge_accounting.json
python3 -m unittest tests.test_entropy_edge_accounting -v
```

Nine tests check hand-worked values, endpoint mass, deterministic successors,
unchanged atomic labels/inputs, rejected undefined samples and protected input
files, including existing hardlink aliases. A copied synthetic workspace also
checks that invocation through a directory symlink preserves resolved pin names
and identical output. An independent successor-distribution calculation exhaustively checks
all 252 binary sequences of lengths two through seven. The full synthetic
report replays with its plan/source/implementation fingerprints.

The illustration does not establish the size or significance of this effect
in any published long-corpus result. It does not execute or reproduce an R
pipeline, choose a manuscript segmentation, or support a language/cipher claim.
There is no manuscript entropy measurement, decipherment or translation here.

A later replication must freeze the actual corpus, representation, space and
boundary rules, package behavior/versions and formula. Retain a paper-compatible
quantity as such, and report a matching-marginal estimate separately if needed;
do not silently substitute one for the other. A modern-source sensitivity study
remains a different experiment. When pooling isolated loci or tokens, derive
predecessor counts from only the declared scored edges: each separate segment
has its own endpoint, so the population distinction is no longer limited to
one endpoint of an entire document.
