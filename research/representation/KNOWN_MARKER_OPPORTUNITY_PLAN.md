# Known marker and vocabulary opportunity: fixed constructed example

## Question and scope

Can the accepted frequency/length-standardized y-removal lookup contrast be
zero in an explicit, exactly reversible example that adds one y to every row's
first token? This checks the interpretation of that statistic, not a manuscript
mechanism. The accepted [specificity controls](../hypotheses/y-prefix-specificity-v1/RESULTS.md)
and [row-marker example](PREFIX_FORMATTING.md) were already known. No manuscript
text, image, source edition, or empirical split enters this construction.

The example was constructed analytically, with the values below reasoned out
before this plan. They are predictions to verify by code, not an unseen outcome,
a random sample, a fitted model, or a preregistered significance test. Publish
this full construction before executing its report. Do not alter rows or cells
to obtain a favorable score. Preserve the accepted manuscript report unchanged.

## Source, marker, and dictionary

The source vocabulary is exactly `{a, b, c, ya, yc, z}`. Its y-leading forms are
invented source tokens, without linguistic interpretation. The source matrices
and supplied row/slot boundaries are fixed:

| Unit | Source rows |
| --- | --- |
| Dictionary development | One row: `z, a, b, c, ya, ya, z` |
| Diagnostic illustration | Four rows: `b, ya, z`; then one row: `a, yc, z` |

Encode **both** units by prepending exactly one literal y to the first token of
every row. Preserve every other token and every boundary. Decode by removing
exactly one y at those known first slots and checking the source vocabulary.
Natural y-leading source tokens remain intact in other slots; a first-slot
source `ya`, if tested, must encode to `yya` and decode back to `ya`. This is a
bijection on allowed complete row matrices with their boundaries. Reject invalid
source or encoded rows instead of repairing them.

Fit the dictionary once from encoded development non-first slots only. Its
counts must be `a:1, b:1, c:1, ya:2, z:1`. The diagnostic internal `yc` is absent
from that dictionary even though it is in the declared source vocabulary. No
diagnostic token or first slot may contribute to the fitted counts.

## Accepted measurements and exact predictions

Use the accepted control study's pure lookup accounting, opportunity bins,
cell collector and exact mean functions. Supply one synthetic development unit
and one synthetic diagnostic unit, with explicit original slots. This is one
toy treatment, not two real editions or eight independent replications.

For the encoded diagnostic rows, all first and y-leading other candidates have
ASCII length two. The first candidates are four `yb` and one `ya`; other y
candidates are four `ya` and one `yc`. Removing leading y uses the same unchanged
development dictionary. Expected first/other gains are **4/5 and 1/5**, giving
unstandardized selectivity **3/5**. The `ya` first form already matches both ways;
the absent `yb`/`yc` forms match only after removal. Lookup is not marker accuracy.

The two common opportunity cells are original development frequency 0 × length
2–4 and frequency 2+ × length 2–4. In the absent cell, both role means are +1;
in the repeated cell, both are 0. Equal cell weighting within the sole diagnostic
unit therefore gives first/other means **1/2 and 1/2**, matched selectivity **0**,
and matched-minus-unmatched selectivity **-3/5**. Keep all nine declared cells,
including empty singleton/long cells and undefined means.

Record every source/encoded/recovered row, exact round trip, dictionary counts,
before/after lookup cells, all opportunity cells, exact rational means, original
and encoded y-prefix counts, boundary/slot totals and all input/implementation
identities. Exactly six first markers are inserted across both units. All 22
source tokens must be recovered, with unchanged row and slot counts. The five
diagnostic first slots change from zero y-leading forms to five; their five
other y-leading source forms remain unchanged.

## Validation and interpretation

Before reporting, test exact recovery, one-marker removal with natural source y,
domain rejection, all-four-cell lookup accounting, development-only counts,
original slots, fixed frequency/length memberships, empty cells, and the two
exact scores against an independent calculation. Exhaust all allowed two-row,
two-slot source matrices for the codec round trip. Report replay must preserve
all fields, including pins, and outputs must not overwrite plans or code/input
files through direct, resolved or hardlink aliases.

The result is a deliberately constructed counterexample to reading a zero
matched contrast as absence of a marker. Standardization changes the lookup
estimand and weighting; original-form vocabulary membership also mechanically
restricts gains. This demonstrates possibility, not the size or frequency of
the effect under manuscript mechanisms, a power/specificity calibration, or a
causal explanation of the manuscript's observed reduction. It supplies no
evidence that a real writer used this codec. The accepted descriptive manuscript
controls, exposure limits, sparse cells and unresolved glyph interpretation
remain valid and unchanged.
