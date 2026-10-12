# Interior permutation symmetry under IID greedy wrapping

The accepted IID wrapping rule can bias the first token's length while leaving
interior order uniform conditional on a completed row's endpoints and bag.
The accepted full and half centered interior scores therefore have conditional
expectation zero under this particular mechanism. A realized row or stream can
still have a nonzero score.

This derives a property of the [accepted synthetic control](../RESULTS.md),
using the [frozen protocol](PLAN.md) and [settings](settings.json). It is an
analytical control, with known synthetic calibration cases. It supplies no
manuscript-line mapping or empirical model fit.

## Domain and likelihood

Incoming widths are IID from a finite positive-integer support with strictly
positive probabilities `p(w)`. Capacity `C` is fixed and at least the largest
width; separator `s` is fixed and nonnegative. Append on equality, close only
when the next token would overflow, and carry that same token to the next row.
The final row without a closing overflow is excluded even when exactly full.

Choose a fixed generated row with at least two token positions, or use an
inclusion rule invariant under the permitted interior permutations. A singleton
has the same first/last occurrence and is outside the following formula. Future
draws after the observed first token remain IID: reaching a row start examines
only past draws and that carried token, without inspecting later draws. No
stationary first-width distribution is needed.

Fix the first width `a`, last width `z`, and interior multiset `M` of size `k`.
They specify distinct positions even when some widths are equal. Occupancy is

```text
T = a + z + sum(M) + s*(k+1).
```

If `T <= C`, every partial prefix fits: its positive-width/nonnegative-separator
sum cannot exceed the complete sum. If `T > C`, no ordering can form this
completed row. For a fitting row, closure on next width `b` is exactly
`T+s+b > C`, independent of interior order. Thus each distinct ordering has
the same joint completed-row event weight conditional on its first width:

```text
p(z) * product(p(x), x in M) * p(b) * 1[T+s+b > C].
```

Marginalizing `b` replaces its last two factors with the overflow mass
`q(T) = sum(p(b), b with T+s+b > C)`. This raw event weight is distinct from
the probability of an order conditional on endpoints, bag and completion.
For a positive-probability class, normalize across its `N` unique orders:
every order has probability `1/N`, where `N=k!/product(multiplicity!)`.
An over-capacity class or a class with zero overflow mass has no conditional
ordering distribution; neither is evidence for a successful zero mean.

## Full and half statistics

Score only overflow-closed rows with at least five tokens, using the accepted
[full](../../transliteration/INTERIOR_ORDER.md) and
[half](../../transliteration/INTERIOR_HALVES.md) definitions. For interior
widths `x_i`, set `u_i=k*x_i-sum(x)`, `D=sum(u_i^2)` and
`A=sum(u_i*u_(i+1))`. For nonconstant interiors,

```text
R = k*A / ((k-1)*D)
full centered score = R + 1/(k-1).
```

Uniform without-replacement interior order has `E[A]=-D/k`; consequently
`E[R]=-1/(k-1)` and the full centered expectation is zero. Constant interiors
use the accepted zero convention and stay in the denominator.

For the half control, the early block has `ceil(k/2)` positions and the late
block the remainder. Fix each block's bag. Every compatible ordering still has
the same likelihood; within-block permutation choices are uniform. If a block
has deviation sum `S`, squared sum `Q` and size `n`, its expected within-block
adjacent sum is `(S^2-Q)/n`, including a zero contribution for a singleton.
The crossing pair contributes `S_early*S_late/(n_early*n_late)`. Multiplying
their sum by `k/((k-1)*D)` gives the accepted half expectation of `R`.
Subtracting it therefore also has conditional mean zero in every half-bag class.

## Finite streams and limits

Permuting a completed row's interiors preserves its total and token count.
Every prefix still fits, and its next carried token still overflows. Previous
and following row starts, endpoints, closure indices and the final unclosed
tail remain unchanged. The map preserves the product probability of a finite
IID input stream. Conditional on those bags/endpoints/tail, all compatible
streams form a uniform orbit. Order-invariant inclusion and weights, including
an equal vote per eligible completed row, preserve the zero conditional mean.
This argument does not infer independence between the generated rows.

The first-width marginal in the parent control is shaped by previous overflow.
The present argument fixes that first width; both properties can hold at once.
These width units are synthetic. Native source loci need not be physical rows,
and ASCII notation lengths need not be glyph or image widths. Dependencies,
order-sensitive selection, nonadditive widths or other production rules require
their own analysis. This proof does not determine how manuscript lines were
produced or establish glyph identities, a language, a decipherment or translation.

The [checker](../../../scripts/wrap_interior_symmetry.py) retains all eight
fixed class attempts and the complete nine-order stream orbit. Its bounded
certificates test the implementation of this derivation; they do not replace
the proof or supply a manuscript sample. The numerical record is published
only after the frozen inputs and implementation are available in Git history.
