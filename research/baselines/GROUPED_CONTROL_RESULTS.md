# Fixed predictor detects the specified synthetic persistence processes

Across all 64 fixed replicates, the grouped Q0/Q1 predictor meets its original
preference criterion in **0 independent-uniform simulations**, **64 quarter-
persistence simulations**, and **64 three-quarter-persistence simulations**.
Every independent case has negative pooled and equal-group gain. This is an
estimator check under three specified processes and the primary manuscript
layout; it does not explain the manuscript's mixed predictive gains.

## Frozen choices and inputs

The [plan](GROUPED_CONTROL_PLAN.md) was published at `c08fa4d`. The tested
implementation and a correction to a plan line break were published and the
remote head verified at **`8e5851e3abd2c21d18766a1b884c0a321cd6048f`** before
the benchmark ran. No case, seed, model choice or preference criterion was
changed after observing results.

The [parent analysis](GROUPED_LENGTH_RESULTS.md), supplied by PR #76, had
already exposed the manuscript data. The generator reads only its primary
ZL3b split **metadata layout**: 2,165 locus keys and source labels, 86 groups,
five original folds and 13,713 transitions. Each generated row retains its
original interior size and group, but replaces every observed length class.
It does not use manuscript gains, fitted probabilities or class frequencies.
The layout digest and complete templates are retained in the report.

Classes are uniform on 1 through 10. Each row starts independently; at each
later slot, it keeps the previous class with probability rho, otherwise draws
a new uniform class. Rho is fixed at 0, 1/4 or 3/4. Uniform redraws can match
the previous value, so adjacent equality probabilities are **10%, 32.5% and
77.5%**, respectively. Streams are separate per case, replicate and locus;
the plan specifies the SHA-256 rejection sampler, seed 20261012 and replicate
indices 0 through 63.

Run the unchanged parent's five-fold estimator with its ten classes, source
label/target-half contexts and smoothing strength ten. Its criterion requires
positive pooled and equal-group gains and at least four positive folds. These
are generated class sequences with known distributions; no glyphs, words,
natural language, encoding or manuscript production mechanism is supplied.

## All results retained

Positive gain means Q1 has lower log-loss than Q0. Values below are means over
all 64 replicates, in bits per transition.

| Process | Pooled fitted gain | Equal-group fitted gain | Realized oracle gain | Ideal stationary oracle gain | Criterion hits |
| --- | ---: | ---: | ---: | ---: | ---: |
| Independent uniform | -0.021975 | -0.037884 | 0 | 0 | 0 / 64 |
| Quarter persistence | +0.249233 | +0.226666 | +0.272058 | +0.272493 | 64 / 64 |
| Three-quarter persistence | +1.812964 | +1.777072 | +1.840277 | +1.839502 | 64 / 64 |

Independent pooled gains range from -0.027519 to -0.017541; equal-group gains
range from -0.054319 to -0.022700. Quarter-persistence pooled gains range from
+0.224477 to +0.267673; equal-group gains from +0.192918 to +0.286893.
Three-quarter-persistence pooled gains range from +1.778567 to +1.858640;
equal-group gains from +1.679825 to +1.839804. The complete
[report](grouped-predictor-controls.json) retains all **192** datasets,
including each seed's losses, three fitted gain averages, criterion flag,
every fold and group summary, fitted-count hashes and generated sequence hash.
Raw sequences and fitted tables are deterministically regenerated.

The oracle uses known process probabilities rather than fitted parameters.
If `d = rho+(1-rho)/10` and `o = (1-rho)/10`, its ideal gain over uniform
prediction is `d*log2(10*d)+9*o*log2(10*o)`. Its realized gain sums the
diagonal/off-diagonal log ratios over generated transitions. Both are exactly
zero for independence. For persistence, the finite fitted estimator's mean
gain lies below this known-process reference. This comparison is specific
to the fixed simulation and does not estimate a manuscript effect.

## Reproduction and checks

For the current checkout with the accepted repaired producer:

```sh
python3 -m unittest discover -s tests -p 'test_grouped_predictor_controls.py' -v
python3 scripts/verify_grouped_predictor_controls.py --check research/baselines/grouped-controls-verification.json
```

A later compatibility companion preserves the original report's exact bytes
and producer pins while checking a current producer after a CLI-only repair.
The original generator deliberately requires its historical producer hash.
Its complete `--check` report also reproduces in a separate disposable bundle
when the two inert snapshots are restored to their original script paths.
Both reproduction routes were checked without a `.git` directory or raw
manuscript corpus; the saved layout, pinned helper files and plan suffice.

Its [receipt](grouped-controls-verification.json) records the original and
current producer hashes separately. Two inert
[producer](frozen/grouped-length-prediction-v1.source.txt) and
[benchmark](frozen/grouped-predictor-controls-v1.source.txt) source snapshots
preserve the exact bytes extracted from the published pre-benchmark commit,
checked against the hashes already in the unchanged result. The compatibility
verifier reads these text files without importing or executing them. They
permit verification from a fresh clone even after a
squash merge. The verifier reads the frozen producer and compares its entire Python
syntax tree with the current source, excluding the body of the sole top-level
`main` and an explicitly reviewed output helper. The helper must match exact
syntax SHA-256 `7f75d126ee0229fbcdb9418339a2169ef53da39126738d7f4dc69d0bde377822`;
no other added helper is allowed. Signatures, decorators, imports, constants
and every scientific function remain compared. The verifier never calls that
CLI or helper. All 192 dataset records
must replay exactly, including every fitted-count and generated-sequence hash.
Ten additional tests reject changes to scientific statements, missing/duplicate
entry points, altered frozen records, missing source snapshots, unreviewed or
changed helpers, helper calls added to scientific functions, and output
aliases. A new current producer requires a newly recorded receipt; it cannot
silently satisfy an old current-producer hash. CLI behavior still needs its
own review and tests. Inert snapshots also have output-alias protection and
can be read without a `.git` directory. When a source catalog is present, the
receipt writer also protects its native sources through hardlink aliases.
It checks again before writing, rejecting an alias created during verification.

The initial v1 receipt excluded only the CLI body and recorded unchanged
producer bytes. After the parent review added a top-level output helper, that
rule correctly rejected it. The post-benchmark v2 verifier adds only the
specific audited helper's syntax hash; it does not alter the generator,
estimator, plan or frozen results. The repaired producer was independently
checked in a disposable checkout before integration. The current receipt
records original producer `3a987a93...` and repaired producer `10d090fa...`
separately and reproduces all 192 original datasets. Parent PR #76 is accepted
with its scientific report bytes unchanged.

The complete report replays exactly in its recorded Python environment.
Eight new tests cover exact draw boundaries, always-consumed innovations,
hand-computed oracle losses and probabilities, stream replay/separation,
metadata-only generation, source labels, disjoint folds, rejected inconsistent
layouts, complete aggregation with adverse values, drift checks, and direct,
symbolic and hardlink output protection. The report reconciles every dataset's
group/fold transition counts and both fitted-model losses. An independent
closed-form calculation verifies all 192 oracle gains from match counts.
Separate Counter fits and direct log-ratios, without the production fitting,
probability or scoring functions, verify all 45 fitted-count hashes and pooled
and equal-group gains in the nine case/seed combinations at seeds 0, 31 and 63.

The benchmark uses the original full producer hash. A guard-only revision to
the parent CLI must be recorded explicitly and must not silently replace that
frozen provenance or its scored results. The benchmark calls the fitting API,
not the parent CLI writer, and its own output guard rejects hardlink aliases.
Any later producer version must be checked against the frozen result. The
published pre-benchmark commit also preserves the original implementation for
reproduction when current producer bytes have changed.

## Interpretation and next step

The fixed estimator detects these two strong, direct class-persistence cases
at the original sample sizes, while fitting additional transition parameters
costs loss under uniform independence. The original manuscript result still
fails its criterion in every treatment. This benchmark does not establish
that manuscript transitions are independent or that a weaker, different or
heterogeneous dependence could be recovered by this model.

Uniform synthetic marginals omit manuscript class frequencies, fine position
profiles, glyph structure, source disagreements, copying and unrecorded content
dependencies. The 64 hit counts are simulation descriptions, not manuscript
p-values, general type-I guarantees, natural-language power estimates or
decipherment confidence. Future mechanism comparisons need explicitly defined
generators and reviewed representations, followed by prospectively evaluated
predictions under the [decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
