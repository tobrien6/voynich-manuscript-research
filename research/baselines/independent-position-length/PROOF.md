# Independence, positional means and the permutation reference

This derivation concerns the four invented processes in the [fixed plan](PLAN.md).
It uses no manuscript measurement, physical line model or inferred glyph unit.

## Factorized process law

For a fixed size m, independently choose B_i from {0,1}, each with probability
1/2. Add the known deterministic offset a_i to obtain X_i=2+a_i+B_i.
For a vector x in the Cartesian product of those slot supports,

```text
P(X_0=x_0,...,X_(m-1)=x_(m-1))
  = product(P(B_i=x_i-2-a_i))
  = 2^(-m).
```

Outside that product support the probability is zero. Each full bit vector
corresponds to one count vector and has the same weight. The variables X_i
are mutually independent by this factorization, not by a correlation inference.
Their slot-specific means are 2+a_i+1/2. Their population variances are 1/4 and
every covariance between distinct slots is zero.

The accepted association instead centers each realized vector by its own pooled
mean and conditions its permutation reference on realized count bags. It does
not subtract the different ensemble means 2+a_i+1/2. Its random normalization
also depends on the realized vector. Zero population covariance under one set
of centering means therefore does not algebraically force that other statistic
to have expectation zero.

## When the ordering reference is valid

For the flat family, every slot has the same two-point law. Conditional on its
whole count bag, each distinct order has the same process weight. The full
uniform occurrence-permutation expectation is therefore the conditional process
expectation. Subtracting that expectation gives mean zero, including the zero
convention for constant vectors. Conditioning further on the two half bags
likewise yields independent uniform within-half orderings, so half centering
also has ensemble mean zero.

The half-step family has identical laws within each half but different laws
between halves. Fixing both half bags leaves every compatible order with equal
process likelihood. Its half-centered total, and each separately centered
component, therefore have conditional and ensemble mean zero. Its whole-bag
orderings need not have equal likelihood under permutations that cross halves,
so there is no corresponding full-centered zero prediction.

Increasing/decreasing families change the slot support within each half.
An observed count bag's arbitrary occurrence permutations need not have the
same process likelihood: some move a count outside a destination slot's support
and have process probability zero. Independence remains intact, while uniform
within-half conditional order is no longer implied. The exact finite ensemble
calculation supplies the stated positive counterexample for size eight; no
general positive theorem for arbitrary gradients is assumed.

The [IID greedy-wrapping theorem](../../line-wrap/interior/PROOF.md) establishes
uniform conditional interior order for its specific positive additive wrapper.
It requires an IID incoming law and order-invariant conditioning/inclusion.
The present independent nonidentical slot laws supply a different process and
do not contradict that theorem or constitute a wrapping/geometry model.

## Scores and directional symmetry

For each realized vector, use the [accepted full](../../transliteration/INTERIOR_ORDER.md)
and [half](../../transliteration/INTERIOR_HALVES.md) score definitions. The early,
crossing and late components retain their original whole-vector normalization.
Subtract each component's own conditional permutation expectation before
averaging over the independent-bit process. The sum commutes with the finite
expectation, so the three ensemble components reassemble the total exactly.

For any bit vector B, decreasing counts satisfy

```text
X_decreasing(B) = m+4-X_increasing(1-B).
```

Subtracting the pooled mean reverses every deviation's sign. Every adjacent
product and squared deviation stays the same; full/half null expectations and
all components are invariant. Complementing all bits is a bijection of the
equally weighted outcome population. Thus increasing and decreasing families
have equal exact score/component distributions, including odd half splits.
This argument changes count signs through an affine relation, rather than
reversing position membership. It supplies no inference about writing direction.

## What the counterexample establishes

A positive half-centered total, even with positive early and late contributions,
can arise under this explicitly independent position-dependent process. That
shows a limitation of interpreting a position-permutation departure as direct
neighbor dependence. It does not establish that manuscript positions follow
these laws, or that this gradient is an adequate empirical explanation.

No count function, noise amplitude, mean trend or size was fitted to manuscript
data. The scale differs from manuscript effects, and notation counts remain
unverified physical units. A defensible manuscript positional model needs its
own prospective predictions, fit/evaluation exclusions, uncertainty treatment
and conditional controls with useful variation. The counterexample supplies
no decipherment, language, translation or manuscript tail calibration.
