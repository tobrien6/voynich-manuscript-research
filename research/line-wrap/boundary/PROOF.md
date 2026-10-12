# Conditional boundary labels under width-only selection

Let a finite IID sequence have labels A_i with strictly positive probabilities
p(a) on the fixed finite support. Let W_i=w(A_i) be a deterministic positive
integer width. For a complete width sequence w_1,...,w_H with positive mass,

```text
P(A_1=a_1,...,A_H=a_H | W_1=w_1,...,W_H=w_H)
    = product_i p(a_i) / P(W_i=w_i),
```

for compatible labels, and zero otherwise. Thus the conditional label law
factors across distinct occurrence indices, including when their labels repeat.
This follows by dividing the IID product by the width-sequence product mass.

The fixed positive-width additive wrapper has capacity at least its maximum
supported width and nonnegative separators. Append on equality, close only on
overflow, and carry the same occurrence unchanged. Every cut, completed-row
start/end, unclosed tail, eligible boundary and boundary count N is therefore a
deterministic function of the complete width sequence. The registered capacities
additionally guarantee at least two tokens per completed row.

For any retained boundary let i be the left row's last occurrence and j the
right row's first. They are distinct (indeed consecutive incoming positions),
even if A_i=A_j. Both rows must be overflow-closed. Conditioning on the widths
fixes that inclusion and gives

```text
E[d(A_i,A_j) | complete width sequence] = mu(W_i,W_j),
mu(u,v) = sum p(a|u) p(b|v) d(a,b).
```

All ordered compatible pairs, including repeated-label pairs, are retained.
The probabilities within a width bin come from the actual categorical law;
they need not be uniform. The edit-cost matrix is fixed before enumeration.

Let S be the sum of the N observed boundary costs and M the sum of the N mu
values. Linearity gives E[S-M | widths]=0. This is a mean identity and requires
no independent-boundary claim. In a general singleton middle row the same
occurrence can enter two boundary costs; those costs can be dependent even
under conditional label factorization. The registered capacity guard excludes
singleton completed rows here, and no variance is claimed in either setting.

For positive expected boundary count, integrating the mean identity gives

```text
E[S]/E[N] - E[M]/E[N] = 0.
```

For the second estimand, N and the event N>0 are functions of widths. Division
by a positive N therefore preserves the conditional mean identity, yielding

```text
E[S/N | N>0] - E[M/N | N>0] = 0.
```

These are different finite averages. If there is no eligible boundary, neither
mean is defined; an empty sum of zero must not become a successful zero mean.
The incoming-pair reference E[d(A,B)] for independent original-law labels is
a different distribution. Width selection can change its contrast without
changing the conditional factorization. Constant-width cases match that
incoming reference but individual residuals can still be nonzero.

The proof retains the initial transient, all declared stream probabilities and
the excluded final tail, including exact capacity equality. It assumes no
stationarity or independence of generated rows. Spelling-dependent selection,
cost-dependent weights, label dependence or contextual widths would invalidate
the stated conditioning argument. Known finite calibration cannot establish
the manuscript's geometry, token boundaries, glyph accuracy, language or
translation, or replicate an empirical anchored-locus permutation control.
