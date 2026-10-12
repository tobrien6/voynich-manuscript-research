# A known row marker can have zero matched lookup selectivity

An explicit reversible formatter inserts one y at every first slot. In a small
constructed example, y-removal lookup selectivity is **3/5 before opportunity
standardization and 0 afterward**, while every source token is recovered
exactly. This checks what the statistic measures: a zero matched lookup contrast
does not establish that no marker was inserted. It supplies no evidence for a
marker mechanism in the manuscript.

## Construction and prior knowledge

The [fixed plan](KNOWN_MARKER_OPPORTUNITY_PLAN.md) and
[input identities](known-marker-opportunity-inputs.json) were committed and
published at
[`e69a257`](https://github.com/tobrien6/voynich-manuscript-research/commit/e69a2573ae2191fcdbb8c396f03da4943fb15205)
before program execution. The rows and exact predictions were
constructed analytically and reasoned out before the plan; this is not an unseen
result, sampled data, a fitted model, a significance test, or a power calibration.
The [complete report](known-marker-opportunity.json) verifies those predictions
with the accepted [specificity-control implementation](../../scripts/y_prefix_specificity.py).

The manuscript's [descriptive prefix/opportunity results](../hypotheses/y-prefix-specificity-v1/RESULTS.md)
and the previous [reversible-marker example](PREFIX_FORMATTING.md) were known.
Their report/code identities are retained as provenance pins. No manuscript
tokens, images, source edition, or empirical split enters construction or
scoring, and the accepted manuscript report is unchanged. There is one synthetic
development unit and one diagnostic unit, in one toy treatment.

The invented source vocabulary is `{a, b, c, ya, yc, z}`. Its y-leading tokens
have no linguistic meaning. The fixed source and encoded rows are:

| Unit | Multiplicity | Source row | Encoded row |
| --- | ---: | --- | --- |
| Development | 1 | `z, a, b, c, ya, ya, z` | `yz, a, b, c, ya, ya, z` |
| Diagnostic | 4 | `b, ya, z` | `yb, ya, z` |
| Diagnostic | 1 | `a, yc, z` | `ya, yc, z` |

Prepend exactly one y to the first token of **both** units. Keep every other
token and the supplied row/slot boundaries intact. Decode only at known first
slots by removing exactly one y and validating the recovered vocabulary.
Natural y-leading source tokens remain intact elsewhere. For example, a
first-slot source `ya` encodes to `yya` and recovers as `ya`, not `a`.
The codec is bijective on allowed complete matrices with those boundaries.

All **22 tokens in six rows** recover exactly; all counts, positions and
boundaries remain intact. Six markers increase the ASCII-character count
from **29 to 35**. Diagnostic first-slot y counts change from **0 to 5**;
the five other y-leading source tokens remain unchanged. The known intervention
and successful inverse establish these facts within the construction, without
estimating a manuscript mechanism.

## Fixed dictionary and lookup cells

Fit one dictionary from encoded **development non-first slots only**. Its exact
counts are `a:1, b:1, c:1, ya:2, z:1`, six occurrences and five distinct strings.
The diagnostic internal `yc` is outside the fitted dictionary, although it is
inside the declared source vocabulary. Diagnostic values and every first slot
are excluded from fitting.

The accepted lookup gain is
`I(form after one leading y removed in dictionary) - I(original in dictionary)`.
Score five diagnostic first y candidates and five other y candidates. There
are ten other slots in total; the five `z` tokens are outside this y-candidate
score. Candidate counts and total slot counts are different denominators.

| Role/form | Candidates | Original dictionary frequency | Original match | Stripped match | Gain |
| --- | ---: | ---: | --- | --- | ---: |
| First `yb` | 4 | 0 | No | Yes (`b`) | +1 |
| First `ya` | 1 | 2 | Yes | Yes (`a`) | 0 |
| Other `ya` | 4 | 2 | Yes | Yes (`a`) | 0 |
| Other `yc` | 1 | 0 | No | Yes (`c`) | +1 |

The first role has four stripped-only matches and one both-way match; the other
role has one stripped-only match and four both-way matches. Neither role loses
a match or remains unmatched here. All four lookup cells remain explicit in
the report and are exercised by separate synthetic tests.

Unstandardized first/other mean gains are **4/5 and 1/5**. Their difference is
**3/5**. A first `ya` really contains an inserted marker but has zero gain
because both forms match. Conversely, deleting the natural source y from the
other `yc` improves lookup while changing its source token. Thus lookup gain
is neither marker detection nor source-token recovery accuracy.

## Opportunity standardization on the same unit

Use the manuscript control's fixed original-development-frequency bins 0, 1,
2+ and representation-length bins 2–4, 5–7, 8+. All candidates have length two.
There are two common cells with both roles; the seven other declared cells are
empty, with undefined means retained.

| Development frequency/length cell | First n | Other n | First mean gain | Other mean gain |
| --- | ---: | ---: | ---: | ---: |
| 0 / 2–4 | 4 | 1 | 1 | 1 |
| 2+ / 2–4 | 1 | 4 | 0 | 0 |

Equal cell weights within the sole diagnostic unit give both role means **1/2**.
Matched selectivity is **0**, with matched-minus-unstandardized selectivity
**-3/5**. The unit and tokens are the same; only opportunity weighting changes.
There are no omitted units, independent replications, intervals, or tail scores.
All counts and rational means precede decimal presentation.

Original dictionary membership mechanically restricts gains: absent originals
can improve or remain unmatched, while present originals can retain or lose a
match. Here absent and repeated forms have opposing role frequencies; the
standardization equalizes those compositions. The marker still exists at every
first slot. The statistic measures dictionary behavior under a changed weighting,
which need not track the presence of the known formatting operation.

## Interpretation and reproducibility

This deliberate counterexample demonstrates a possibility. It estimates neither
the frequency nor the size of such effects under realistic mechanisms. In
particular, it does not explain the manuscript control's reduction, establish a
causal share removed by matching, validate this codec for glyphs, or overturn
the accepted descriptive measurement. That study's positive matched residual,
exposed material, different strings, coarse bins, and sparse cells remain as
reported. Discriminating manuscript mechanisms still requires additional
predictions, reviewed glyph regions and an exposure-valid evaluation design.

Standard-library Python 3.10+, from the repository root:

```sh
python3 -m unittest tests.test_known_marker_opportunity tests.test_y_prefix_specificity tests.test_y_layout_prefix tests.test_prefix_formatting_demo
python3 scripts/known_marker_opportunity.py --check research/representation/known-marker-opportunity.json
python3 scripts/y_prefix_specificity.py --check research/hypotheses/y-prefix-specificity-v1/results.json
```

All 48 relevant tests pass, including eight new tests. Codec recovery is
exhausted over all **1,296** two-row/two-slot source matrices. Tests cover natural
source y, invalid domains, unchanged other slots, development-only counts,
independently calculated lookup/cell means, fixed memberships and empty cells,
all-four-cell accounting, pin drift and direct/symlink/hardlink input-output
aliases. Complete report replay verifies source/encoded/recovered matrices,
all counts, cells, exact fractions and provenance. Output guards preserve
plans, code/helpers, catalog/raw inputs and fixed records, and recheck before
writing. No actual source text or image is redistributed by this example.
