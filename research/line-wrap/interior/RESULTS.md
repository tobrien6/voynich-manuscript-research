# IID wrapping biases the first width while preserving conditional interior order

The [proof](PROOF.md) derives uniform interior order from the specified IID
greedy-wrapping rule, conditional on a completed row's endpoints and bag.
The full and half centered scores have exact conditional expectation zero.
This complements the [parent's first-width bias](../RESULTS.md): that marginal
contrast and the present conditional symmetry use different conditions.

The bounded [certificate record](certificates.json) retains every declared
attempt. These are known mathematical calibrations, not blind predictions,
an IID simulation or a sample of manuscript rows.

## Fixed classes

Raw weights below are completed-row event weights conditional on the first
width. Conditional order probabilities additionally condition on the endpoints,
bag and completion. They must not be interchanged.

| Fixed class | Retained unique orders | Raw weight per order | Conditional probability per order | Full / half conditional mean |
| --- | ---: | ---: | ---: | --- |
| Repeated bag, capacity 18 | 3 | 4/3125 | 1/3 | 0 / 0 |
| Distinct even bag, capacity 24 | 24 | 1/3125 | 1/24 | 0 / 0 |
| Distinct odd bag, capacity 30, exactly full | 120 | 1/15625 | 1/120 | 0 / 0 |
| Constant bag, capacity 18 | 1 | 1/625 | 1 | 0 / 0 |
| Unequal-law fixture, capacity 24 | 24 | 1/1024 | 1/24 | 0 / 0 |
| Two-token short class, capacity 8 | 1 | 1/2 | 1 | Unscored |
| Fitting class with no possible closing overflow | 0 | 0 | Undefined | Undefined |
| Class exceeding capacity | 0 | 0 | Undefined | Undefined |

The record contains all **172 score-eligible ordered rows**, one short ordered
row, and both impossible-class attempts. It keeps every incoming-width event,
including values that cannot close the selected row, and all **25** eligible
half-bag classes. Every half class has exact half-centered mean zero. Repeated
values are counted as unique observable orders; constant interiors remain zero
contributions. Impossible conditioning events are not reported as zero means.

## Whole-stream orbit

The fixed fifteen-token stream yields two overflow-closed five-token rows and
the exactly full tail `[2,2,2,3,5]`. That final tail remains unclosed and excluded.
The original equal-row scores are **−1/8** under the full control and **−3/16**
under the half control. Both are nonzero, despite zero conditional expectations.

All nine joint interior permutations preserve closure indices, carried first
tokens, endpoints, occupancy, completed-row count and that tail. Their IID
input-stream weights are equal. Both full-orbit centered means are exactly
zero, as are all four joint half-class means (class sizes 1, 2, 2 and 4).
Every stream, trace and individual score remains in the record. This finite
fixture demonstrates the conditioning argument; it does not infer independent
generated rows or supply a new random simulation.

## Freeze, reproduction and validation

The corrected [plan](PLAN.md) and [settings](settings.json) were published at
[`1a5a02a`](https://github.com/tobrien6/voynich-manuscript-research/commit/1a5a02a54147c0d1c30762f6ec9bc4585249e7d2).
The proof, implementation and tests were published at
[`1574fb0`](https://github.com/tobrien6/voynich-manuscript-research/commit/1574fb0b1c3a602499190647cffcbf995b7ec2ae)
after syntax compilation and before the first unit-test/certificate calculation.
Both remote heads were checked before execution. These are recorded chronology
and input-identity statements, not independent certification of exposure.

The producer checks actual frozen protocol blobs and eight accepted parent/method
artifacts at `dbb043382516d19acecc837ba42fbaef2b005ca4`. Its standard-library
implementation uses exact rational probabilities and scores. No source text,
image, fitted token law or empirical control array enters this calculation.

From the repository root, with Python 3.10+ and the cited Git history:

```sh
python3 -m unittest tests.test_wrap_interior_symmetry -v
python3 scripts/wrap_interior_symmetry.py --check research/line-wrap/interior/certificates.json
python3 scripts/wrap_interior_symmetry.py --output /tmp/new-wrapping-certificates.json
```

Eight tests independently compare every positive ordered event with the accepted
sequential wrapper and every eligible score with the accepted full/half methods.
They cover unequal-law weights versus normalized probabilities, repeated and
constant bags, short and impossible cases, singleton/domain guards, a separate
zero-separator boundary implementation check, whole-stream carry/tail behavior,
frozen-input drift, deterministic reporting and existing/late hardlink outputs.
Outputs require a new unlinked file and are guarded before generation and again
before an exclusive write. All eight tests pass; the entire report replays byte
for byte. Its SHA-256 is
`749e8228723845ba533c7b68325587ed025038a336a671eb7353b19d1066e030`.

## Interpretation

The theorem requires at least two distinct token positions, positive conditioning
and row inclusion invariant under the permitted permutations. Scoring requires
at least five tokens. Order-sensitive selection would change the conditioning.
Fixed additive geometry and IID input are assumptions of this particular model.

The exposed manuscript interior analyses use encoded source loci and notation
lengths, with unresolved physical-line/glyph mappings and related editions.
The present theorem describes the toy mechanism; it does not determine whether
those assumptions describe the manuscript or exclude every layout process.
It adds a mechanism constraint without glyph adjudication, a language claim,
decipherment, translation or untouched evaluation material.
