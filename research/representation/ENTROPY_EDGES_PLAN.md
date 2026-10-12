# Finite-sequence entropy accounting: synthetic plan

Question: when a finite sequence has no wraparound, how does a difference
between independently counted bigram and full-character entropies compare with
conditional entropy on its actual successor edges?

Use only these six invented sequences, in order: `ab`, `aab`, `aba`, `abba`,
`aaaa`, `abcabc`. Each displayed ASCII letter is an atomic label. Count every
letter, and every adjacent pair within the one sequence. Do not pad, wrap,
join sequences, introduce word separators, fit a model or run manuscript data.

For each sequence, retain full-unit counts, directed pair counts, predecessor
counts from those pairs, sample sizes and endpoint. Compute base-2 empirical
entropy of full units, pairs, and pair-derived predecessors. Report the joint
pair entropy minus each marginal separately. Check the pair-derived difference
against the existing `empirical_entropy(sequence, order=1)` helper. Show the
sum of pair count/full-unit count at each predecessor so incomplete successor
mass is visible. Never clip a negative difference or relabel it as a proper
conditional probability estimate.

Pin arXiv `2010.14697v2` and the read-only companion code at
`decc4caaa6515b86e42a219d1da8d81114736f2e`. Inspect source definitions and
relevant PDF pages; run none of the external R code and import no new corpus.
The comparison is with the algebra visible in the pinned source, not a claim
of executing its package behavior or reproducing its publication pipeline.
Identify unresolved package versions, preprocessing and corpus identities.

Commit this plan before generating the demonstration report. Verify hand-worked
examples, transition mass, the chain-rule identity with a matching predecessor
marginal, deterministic successors, unchanged inputs, rejected undefined samples
and exact report replay. Keep the source/publication artifacts local; publish
only links, digests, original code/tests, these synthetic data and a methods note.

This is a measurement convention check, distinct from the earlier reversible
encoding example. It establishes no manuscript statistic, transcription error,
natural-language exclusion, decipherment or translation. For a later replication,
freeze the exact corpus, representation, boundary convention, source/package
versions and statistic before execution. A modern corpus sensitivity test must
remain separate from historical paper replication.

Role: contributor for the user's continuing Voynich goal, using the required
`tobrien6` identity and verified owner/admin access. The dedicated branch is
`codex/entropy-edge-accounting-1ebd` in the isolated maintainer checkout.
Existing review owners retain incoming-PR decisions; no self-approval is used.
