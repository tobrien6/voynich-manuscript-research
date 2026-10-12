# Distinct representations with an immediate self-repeat

The primary ZL split/exclude treatment contains **103 distinct repeating
representations**, against an exact conditional expectation of **93.9073**.
Its accepted pair-event count remains 272 against 270.7699 expected. These
statistics weight repetition differently; an above-mean type count alone
supplies no calibrated excess, uncertainty interval, or decipherment evidence.

## Counting unit and source comparison

[Amancio et al. (2013)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0067310),
Materials and Methods / First-order statistics, count a vocabulary type once
when it has any immediate self-repeat. Their shuffled-text normalization and
historical input are separate from this analysis. The
[published-methods register](../literature/README.md) already distinguishes
their type count from the project's pair-event count. This contribution
implements that counting distinction on the modern P0 cohort under the
existing within-locus control; it is not a numerical paper replication.

For the synthetic sequence `a a a b b a a`, there are four equal adjacent
pair events but only two repeating types. Repetition in multiple loci still
counts once for a given representation. Strings denote preserved transcription
representations, without assuming identified words or glyphs.

The [plan](REPEATING_TYPES_PLAN.md) was committed at `d074efa` before this new
measurement. Implementation and 23 passing targeted tests were committed at
`a88b2a7` before the manuscript run. Previously inspected source text, pair
baselines, distance profiles and the published definition remain disclosed
exposure. These local chronology records are not preregistration or proof of
untouched evaluation.

## Cohort, slots and exact expectation

Use the accepted **3,884 shared present P0 loci**, source byte pins, tokenizer
and all eight source/uncertainty treatments from [BASELINES.md](BASELINES.md).
Excluded original slots remain gaps. Equality is scored only between retained
tokens in consecutive original slots of the same locus. No locus concatenation,
physical-line reconstruction or new selection is introduced.

Uniformly permute each locus's retained bag over retained slots, independently
between loci. For a representation occurring `c` times among `m` retained
positions, every size-`c` position subset is equally likely. No self-repeat
occurs exactly when the subset contains no eligible adjacency edge.

The adjacency graph separates into retained runs. A run with `l` retained
positions has `C(l-k+1,k)` independent subsets of size `k` when
`0 <= k <= ceil(l/2)`, and zero for larger `k`. Choosing nonadjacent positions
and subtracting their required intervening gaps gives this binomial count.
For component sizes `l_j`, form:

```text
P(z) = product_j sum_k C(l_j-k+1,k) z^k
q_locus(type) = [z^c] P(z) / C(m,c)
E[distinct repeating types] = sum_type [1 - product_locus q_locus(type)]
```

Absent or once-per-locus types have no repeat opportunity there. Empty
components use the constant polynomial 1. Gap-separated singleton positions
cannot create adjacency. Component coefficients are calculated with integers
and cached once per component layout; probabilities and products use exact
fractions. The cross-locus product follows the declared independent-locus
shuffle model. The sum follows linearity of expectation, requiring no
independence between different type indicators.

For two synthetic loci with bag `a a b`, each locus has repeat probability
2/3 for `a`; probability it repeats anywhere is **8/9**. Summing the two local
probabilities would yield 4/3 and double-count the type. A globally frequent
type present only once per locus contributes zero under this within-locus
statistic. This explains why corpus-level type counting needs the product.

## Observations and policy sensitivity

All eight treatments and exact fractions remain in
[repeating_types.json](repeating_types.json). IT2a's four full results are
identical apart from policy labels, verified before collapsing this table.

| Source / spaces / alternatives | Repeat-capable types under control | Observed repeating types | Expected repeating types | Observed minus expected | Pair events / expectation |
| --- | ---: | ---: | ---: | ---: | ---: |
| ZL / split / exclude | 209 | 103 | 93.9073 | 9.0927 | 272 / 270.7699 |
| ZL / split / first | 209 | 104 | 94.8820 | 9.1180 | 274 / 274.3704 |
| ZL / join / exclude | 186 | 97 | 84.7705 | 12.2295 | 241 / 219.2347 |
| ZL / join / first | 188 | 98 | 85.9505 | 12.0495 | 242 / 222.1758 |
| IT / all policies | 203 | 106 | 93.3767 | 12.6233 | 282 / 264.7307 |

Every treatment's observed type count is above its conditional mean. The
primary pair-event count is close to its pair-event mean, while the type
count has a different descriptive contrast. The primary histogram includes
65 types with one event, 13 with two, and one with 24. The complete histogram
reconciles both the type and pair counts, preserving their different weights.

No type-count variance or tail has been calculated. Type indicators share
finite token bags and are generally dependent; a binomial or independent-type
variance would be unjustified. The source and policy treatments share text.
The mean contrasts neither establish a statistically reliable departure nor
identify a language, copying mechanism, glyph reading or translation.

## Reproduce and validation

Python 3.10 or later, standard library only; recorded on Python 3.14.3. Obtain
the [pinned sources](DECISION.md), then run:

```sh
PYTHONPATH=tests python3 -m unittest \
  test_repeating_types test_repetition_moments test_token_baselines
python3 scripts/repeating_types.py --check research/transliteration/repeating_types.json
python3 scripts/repeating_types.py --output /tmp/repeating-types.json
```

Eight new tests cover all 511 original retention/gap layouts of sizes 0–8
and their 9,841 marked-position subsets, exhaustive independent multiset
permutations, cross-locus deduplication, constants/empty edges, global frequency
without local opportunity, invalid inputs, full synthetic source/policy replay,
and actual-CLI direct/symlink/hardlink input protection. The accepted moment and
tokenizer suites bring the targeted total to 23 tests. A typed or altered pair
reference is rejected, as is a typed cache change.

A 3,884-locus synthetic stress case exposed the integer-to-decimal string
conversion limit when exact cross-locus products become large. Exact integer
construction through [Decimal](https://docs.python.org/3.14/library/decimal.html#decimal.Decimal)
formats the fractions without decimal arithmetic or changes to process limits.
The repaired 16,317-character fraction round-trips through JSON, including
under decimal precision 1; it computed in approximately 0.16 seconds on the
recorded environment. This is a software stress fixture, not manuscript text.

Exact fractions are decimal `numerator/denominator` strings, or a single
integer when the denominator is 1. For very large strings, reconstruct a
Fraction from `int(Decimal(numerator))` and `int(Decimal(denominator))` rather
than changing the interpreter's integer-string limit. Rounded displays use
eight decimals. Check mode compares the entire typed canonical report, including
source/catalog, plan, engine, baseline and preprocessed-slot fingerprints.

The producer checks every accepted source/policy pair count, denominator,
token/slot/vocabulary count, cohort key digest and expectation before emitting
a report. Those accepted baseline bytes and its 199-shuffle arrays are unchanged.
Output guards protect its raw inputs, catalog, code, plan and pair reference.

Assess the spread of this type statistic using joint probabilities or a
disclosed shuffle protocol before applying it in a candidate comparison. A
paper or generator comparison must explicitly match counting units, input,
boundaries and null scope. Physical mapping, source/glyph adjudication and a
real exposure-aware evaluation split remain outside this description.

The [exact type-variance follow-up](REPEATING_TYPE_VARIANCE.md) adds joint
no-event probabilities and signed type-pair covariance under this same
fixed-gap locus control, preserving every count and mean in the present report.
Its SD-scaled descriptions supply no normal-tail or decipherment claim.
