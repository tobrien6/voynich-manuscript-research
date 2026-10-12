# Response to the paragraph augmentation intervention

Changing the paragraph augmentation condition to a zero threshold increased
both planned first-boundary contrasts in model paragraph-initial rows when
averaged across the twenty fixed seeds: **+1.7543 percentage points for q** and
**+1.5116 for y**. The q response was positive in all 20 seeds; the y response
was positive in 16 and negative in four. Both planned mean-direction predictions
passed, while those four opposite y responses remain part of the result.

The [plan](SELF_CITATION_GALLOWS_PLAN.md) was committed before ablated execution,
after the default [census](SELF_CITATION_PREFIX_SEEDS.md) was exposed. This is an
intervention in the source program, not an independently registered manuscript
test or decipherment. The [complete record](self-citation-gallows-zero.json)
retains every seed, all 160 paired cells, denominators, exact rational
differences, process outcomes and artifact identities.

## The exact change and its scope

In the pinned source's
[`AbstractBaseGroupMorpher.handleGallows`](https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/9e98c9122a0f490905e8b66f3911fc7ce095fd26/source/src/main/java/de/voynich/text/morph/AbstractBaseGroupMorpher.java),
the shared threshold 94 is used both for paragraph-initial augmentation and
for replacement of existing gallows in other rows. The experiment changes
only the paragraph augmentation predicate to use literal zero. The random
draw immediately preceding that predicate remains. The shared constant and
other source bytes are preserved; only the observer's declared main-method
insertion is added in the observed build.

Under the pinned pseudo-random implementation, `rand(100)` returns 0–99, so
the zero-threshold predicate never requests that augmentation branch. The
ordinary line-initial fallback and other gallows rules still operate, and
gallows already present in source groups can remain. This is an intervention
on one specified condition, not removal of all gallows forms.

The only changed compiled class, relative to each corresponding default
observation mode, is `AbstractBaseGroupMorpher.class`. All 35 copied source
files were checked against their declared expected bytes. Third-party and
instrumented/ablated source, classes, configurations, raw output/logs and
ledgers remain local; only the original experiment code and measurements are
committed.

## Controls and all outcomes

Use the same source release, full configuration, Java 22.0.2, compiler/locale
controls and seeds 1–20 as the frozen default census. For each seed, run one
fresh unobserved ablated JVM and one observed ablated JVM. All **40 new
generation processes** exited zero, all **20 pairs** preserved their complete
bytes, and all observed cases had the expected 1,199 generation-call events
and 1,200-row ledger. The original reference checkout remained unchanged.

Exclude only initialization and apply the same native-token eligibility and
exact equal-row q/y contrast function as the default census. No generated row
had fewer than two tokens. The ablated non-initial populations contain 955–968
rows per seed; initial populations contain 231–244. Default populations differ,
so these comparisons retain both denominators and do not pair identical row
contexts or word trajectories.

Every cell below reports the mean of its 20 seed-specific row means, in
percentage points. The change is `ablated - default`. Display rounding does
not replace the exact rational records. Sign counts describe this deterministic
grid; they are not p-values or probabilities.

| Model paragraph-initial flag | Boundary | Prefix | Default mean | Ablated mean | Mean change | Negative / zero / positive changes |
| --- | --- | --- | ---: | ---: | ---: | --- |
| false | first | q | +0.7690 | +1.1247 | +0.3557 | 8 / 0 / 12 |
| false | first | y | +1.7037 | +2.0751 | +0.3714 | 8 / 0 / 12 |
| false | last | q | -1.9490 | -2.1327 | -0.1838 | 10 / 0 / 10 |
| false | last | y | -1.6227 | -1.9835 | -0.3608 | 12 / 0 / 8 |
| true | first | q | -1.7347 | +0.0196 | +1.7543 | 0 / 0 / 20 |
| true | first | y | -5.6774 | -4.1658 | +1.5116 | 4 / 0 / 16 |
| true | last | q | -0.6761 | -0.8153 | -0.1392 | 11 / 0 / 9 |
| true | last | y | -0.4400 | -0.6748 | -0.2347 | 11 / 0 / 9 |

The paragraph-initial first-y contrast remains negative on average after the
intervention. The observed response therefore does not eliminate that entire
default deficit. The data do not attribute the remaining value to a particular
other rule. Non-initial and last-boundary changes are also retained; the
source program's state and subsequent random-call paths can change throughout
generation after this intervention.

## Reproduction and validation

The producer checks the frozen default census, its measurement-helper bytes,
the replay control and runtime identities before reusing default results.
Supply the unchanged pinned source checkout and the recorded Java installation,
with new work/output paths:

```sh
python3 scripts/ablate_self_citation_paragraph_gallows.py \
  --reference PATH_TO_PINNED_RELEASE --java-home PATH_TO_RECORDED_JAVA \
  --work PATH_TO_NEW_ABLATION_DIRECTORY --output PATH_TO_NEW_RECORD.json
PYTHONPATH=tests python3 -m unittest test_self_citation_gallows \
  test_self_citation_prefix_seeds test_self_citation_trace \
  test_self_citation_replay test_prefix_conditional_bounds -v
```

Twenty-four focused tests passed. Synthetic cases verify a single reversible
predicate change with the other threshold reference retained, cell-identity
pairing despite reordered inputs, distinct denominator preservation, incomplete
primary predictions remaining unresolved, and a zero mean failing the positive
prediction. Existing row/trace/environment/exact-moment checks remain in use.
All 40 actual JVM runs are retained as integration evidence. Source patches,
build classes, configurations, native output/trace/ledger/log fingerprints,
exact means and all 160 differences are available for separate verification.

## Interpretation

This quantifies the response to one source-program intervention under the
chosen grid. Changes in conditional populations, accepted words and random-call
sequences prevent interpretation as isolated direct effects on matched rows.
The eight measures are related descriptors of shared outputs. No confidence
interval, calibrated seed probability, manuscript mechanism fit, source-label
transfer, glyph equivalence, plaintext reading or translation is established.
The initialized manuscript-derived input is reused throughout.

A later manuscript comparison must establish compatible units and exposure,
and specify controls and rejection criteria separately. Any parameter fitting
needs a new candidate version and honest evaluation record under the
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
