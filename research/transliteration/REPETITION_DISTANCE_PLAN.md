# Exploratory recurrence at fixed slot distances

Written before computing this follow-up's manuscript distance results. The
underlying sources and adjacent-repetition baseline have already been inspected;
this is an exploratory analysis plan, not preregistration or untouched evaluation.

Question: how do equal-representation counts at original apparent-token slot
distances 1, 2, 3, and 4 compare with independent uniform permutations of each
locus's retained token bag? Distance 1 must reproduce the accepted adjacent
baseline. Longer distances may constrain local recurrence without attributing
it to a particular copying, linguistic, or cipher mechanism.

Use the pinned ZL3b and IT2a inputs and the intersection of present `P0` loci,
as in `BASELINES.md`. Retain all four split/join and exclude/first uncertainty
treatments for both sources. Apply the existing tokenizer and retention rule.
Preserve every excluded position as `null`; do not compact token slots, mix
loci, cross locus boundaries, or silently equate a locus with a physical line.

At distance `d`, compare positions `i` and `i+d` only when both endpoints are
retained. Interior slots can be excluded. Such a pair still has distance `d`,
never distance 1. Report the number of eligible pairs spanning excluded
interior slots so that this part of the denominator remains visible. Spacing
policies can change the original apparent-slot coordinates and denominators.

Count equal-pair events, not distinct repeating types. Report eligible pairs,
contributing loci, observed counts/rates, exact conditional means/variances,
conditional SD, and descriptive observed-minus-expected counts in SD units.
Return `null` for SD scaling when variance is zero. The control permutes each
locus independently while preserving its bag and excluded slots. Independence
is a control assumption, not an assertion about the manuscript.

Reuse the accepted simple-graph moment calculation. Distance graphs have
disjoint edge sets, so compute cross-distance covariance from
`[Var(T_d + T_e) - Var(T_d) - Var(T_e)] / 2`, using the union graph and exact
rational arithmetic. Sum means and covariance matrices across loci. Preserve
exact fractions alongside rounded diagnostics. Do not treat distances or source
treatments as independent tests, attach normal-tail probabilities, or choose a
favored distance after seeing results. No Monte Carlo tail is requested.

Pin source bytes, sorted cohort keys, preprocessed slot arrays, this plan, and
calculation dependencies. Keep the existing baseline and its recorded shuffles
unchanged. Validate complete mean/covariance matrices against exhaustive unique
permutations of small synthetic bags, including excluded interior slots,
all-distinct/constant/empty bags, and independent-locus addition. Check distance
1 against every accepted source/policy baseline and replay the new report.

Report all distance results and preprocessing sensitivities. A departure from
this conditional token-bag control is neither support for a particular
generator nor a decipherment. A later candidate comparison needs a separately
frozen mechanism and a disclosed exposure history; this analysis supplies no
real evaluation split, glyph adjudication, decoding, or translation.
