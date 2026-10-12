# Conditional prefix-bound calculation plan

This is a calibration follow-up to an already exposed exploratory report. It
changes no source, cohort, prefix, boundary, or null model and does not create
a new held-out test.

## Fixed inputs and family

- Reuse the accepted conservative 2,907-key cohort and `plain-eva-v1` gate.
- Recompute literal q/y first/last contrasts from the pinned source tokens,
  preserving each edition's paragraph/Currier partitions and both spacing policies.
- Include every existing contrast: two sources × two spacing policies × the
  source-label/paragraph cohorts × two boundaries × two prefixes. Include empty
  cohorts in the declared family count rather than selecting successful cases.
- Use exact rational per-locus contrasts and variances. Check agreement with
  the existing report's means, denominators, and conditional standard deviations.

## Conditional bound

Under the existing ideal control, token assignments are uniform within each
locus and independent across loci. For a binary prefix feature with `m` retained
tokens, `k` positives, and observed boundary indicator `x`:

```text
D = (m*x - k)/(m - 1), E[D] = 0, |D| <= 1
Var(D) = k*(m - k)/(m - 1)^2
T = sum(D), V = sum(Var(D))
two-sided tail <= min(1, 2*exp(-T^2/(2*V + 2*abs(T)/3)))
```

The standard Bernstein inequality for independent centered bounded variables
supports this calculation; see [Stanford CS229T, Question 12(c)](https://web.stanford.edu/class/cs229t/2017/problems.pdf).
The two-sided factor of two comes from combining its two one-sided inequalities.

Report upper bounds, not estimates of the actual tail probability. Also report
the bound multiplied by the complete declared family size, capped at one. This
union-bound adjustment needs valid marginal conditional models, not independence
between comparisons. It does not account for other exploratory searches in the
project or convert exposed-data analysis into confirmation.

## Numeric and interpretation requirements

Retain exact rational statistics and positive high-precision decimal bound
strings, avoiding a float underflow reported as zero. Expose the ideal-control
independence assumption; do not assert that manuscript loci are independent.
Preserve undefined cases and loose bounds. No bound identifies a language,
glyph reading, cipher, plaintext, or translation.
