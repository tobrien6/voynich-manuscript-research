# Prefix contrasts under row and comparison-opportunity weights

All eight default generator cell families retain the sign of their mean across
twenty seeds when comparison opportunities replace equal row weights. Five of
the 160 individual seed/cell signs reverse. The exact [complete record](self-citation-prefix-weights.json)
retains both measures and their arithmetic decomposition for every case.

The [plan](SELF_CITATION_PREFIX_WEIGHT_PLAN.md) was published at
`9e0bff189cee9c1c488417750f67f4ee66d87fcc` before these new measurements. The
default [census](SELF_CITATION_PREFIX_SEEDS.md), its results and selected raw rows
were already exposed during review. This is a descriptive weighting audit with
no directional prediction, success threshold or untouched-evaluation claim.

## Same rows, two measures

An eligible native row with n tokens has contrast d = e − k/(n−1), where e is
the chosen first/last q/y indicator and k counts that prefix among other tokens.
The default gives each row equal weight. The alternative gives it n−1 weight:

    equal-row mean = mean(d)
    opportunity-weighted mean = sum((n−1)e − k) / sum(n−1)

The second formula averages every boundary-versus-other-token comparison pair.
It weights the boundary indicator as well as the other-token contribution.
Combining an unweighted boundary rate with a pooled other-token rate would be a
third measure and is not calculated here.

For positive weights w = n−1, subtraction gives the exact identity

    weighted mean − equal-row mean = Cov(w, d) / mean(w)

The population covariance uses divisor N, the number of eligible rows.
Expanding it as mean(wd) − mean(w)mean(d) proves the identity without a
probabilistic or causal assumption. Each cell records this covariance, mean
weight, total opportunities and both component counts. The rows, native tokens,
model flags, eligibility and generator output do not change between measures.

## All outcomes

Each number below is the equally weighted mean of twenty seed-specific cell
means, in percentage points. Seeds are not pooled by their row counts or total
opportunities. Display rounding does not replace the exact rational records.

| Model paragraph-initial | Boundary | Prefix | Equal rows | Opportunities | Change | Seed/cell sign reversals |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| false | first | q | +0.7690 | +0.7276 | -0.0414 | 2 |
| false | first | y | +1.7037 | +1.7850 | +0.0813 | 1 |
| false | last | q | -1.9490 | -1.9852 | -0.0363 | 0 |
| false | last | y | -1.6227 | -1.7196 | -0.0969 | 0 |
| true | first | q | -1.7347 | -1.6742 | +0.0604 | 0 |
| true | first | y | -5.6774 | -5.6930 | -0.0156 | 0 |
| true | last | q | -0.6761 | -0.6730 | +0.0031 | 2 |
| true | last | y | -0.4400 | -0.4688 | -0.0288 | 0 |

Every reversal is retained: paragraph-initial last-q changes positive to
negative in seeds 2 and 8; non-initial first-y changes negative to positive in
seed 10; non-initial first-q changes positive to negative in seed 13 and negative
to positive in seed 18. None has a zero contrast under either measure. All
eight summary mean signs persist, including the negative paragraph-initial
first-q and first-y means in every seed under both measures.

This grid shows both persistence of aggregate direction and sensitivity of
individual signs to the averaging unit. Its sign counts are deterministic
descriptions, not calibrated probabilities or significance tests. No change is
attributed to a generator rule: there is no program intervention here.

## Reproduction and verification

Reuse the pinned source and recorded Java installation to produce a new default
raw census directory with the [existing producer](../../scripts/census_self_citation_prefixes.py)
if needed. The new audit itself runs no Java process and changes no raw artifact:

```sh
python3 scripts/census_self_citation_prefixes.py \
  --reference PATH_TO_PINNED_RELEASE --java-home PATH_TO_RECORDED_JAVA \
  --work PATH_TO_NEW_DEFAULT_DIRECTORY --output PATH_TO_NEW_CENSUS.json
python3 scripts/audit_self_citation_prefix_weights.py \
  --raw-work PATH_TO_DEFAULT_DIRECTORY \
  --check research/literature/self-citation-prefix-weights.json
PYTHONPATH=tests python3 -m unittest test_self_citation_prefix_weights \
  test_self_citation_prefix_seeds test_self_citation_trace \
  test_self_citation_replay test_prefix_conditional_bounds -v
```

The audit verifies the frozen default census and helper identities, every
original/observed complete output pair, configurations, process log fingerprints,
ordered events and complete row ledgers. Initialization stays excluded, and the
same eligibility/exclusion records are retained. Every accepted default
population, denominator, boundary count, exact sum/mean and other-prefix rate
must reproduce before the new weighting result is accepted. Missing or changed
inputs reject the complete computation. New records use exclusive creation and
cannot overwrite existing files or follow aliases introduced during calculation.

Seven new tests pass, with 28 focused tests including the existing controls.
An exhaustive oracle enumerates 1,568 bounded two-row/boundary cases with binary
prefix indicators, checking explicit comparison-pair averages and centered
population covariance. Additional fixtures retain a constructed sign reversal,
constant weights, zero contrasts, excluded short rows, equal seed weights despite
unequal row counts, a changed frozen source, duplicate JSON keys and late output
symlink/hardlink protection.

A separate real-input comparison-pair enumerator, importing no production or
measurement helper, reconstructs all 160 cells and eight exact summaries. It
checks every population, component count, opportunity total, mean, covariance,
decomposition, range and sign transition against the complete report. Original
Torsten Timm source/classes, raw generated output/configuration/logs and ledgers
remain local. The contribution contains original code and token-free measurements.

## Scope for mechanism comparisons

The default source, initialized manuscript-derived input, native ASCII q/y
prefixes and software paragraph flags keep the census's original meaning.
Neither weight establishes manuscript glyph/word units or compatible manuscript
paragraphs. A later mechanism comparison must freeze matching units, eligibility
and averaging weights in addition to source versions and exposure. These
descriptors supply no language identification, fitted mechanism, calibrated seed
population, decipherment or translation.
