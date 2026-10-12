# Paired symbol entropy: descriptive sensitivity plan

Question: how do the accepted notation segmentation and token-boundary policies
change pooled empirical symbol entropy on one fixed clear-locus source cohort?
This is exploratory analysis of previously exposed ZL3b/IT2a text. It registers
no decoding candidate, language comparison, unseen set or significance test.

## Cohort and source identity

Use the pinned `ZL3b` and `IT2a` sources, `plain-eva-v1`, P0 only, with both
`split` and `join` uncertain-space policies. Start from the intersection of
present native P0 locus keys. Keep a key only when all four representations are
eligible, have at least one token, have locators `@`, `+` or `*`, and have no
drawing interruptions. Exclude a whole locus when any representation fails.
Record every retained/excluded key, overlapping source/policy reasons, source-only
P0 keys and all cohort/input fingerprints. Do not select a page or stratum from
an entropy result. Native keys are transcription loci, not verified physical rows.

Pin the source catalog, reader/adapter/tokenizer implementations and the accepted
unit-policy file in [paired-entropy-plan.json](paired-entropy-plan.json). Require
exact source bytes through the existing loader. Preserve native case, all token
boundaries under each spacing policy, source identifiers and locus metadata.

## Units, boundaries and statistics

Use exactly the existing `ascii_letters`, `bench_sequences` and
`bench_and_minim_sequences` policies in `research/baselines/eva-unit-protocol.json`.
Reuse its case-sensitive longest-match implementation within each token. Never
group across tokens, infer glyph truth, alter patterns, or prefer a policy from
the resulting entropy. Rejoining emitted pieces must recover the original token.

Report both fixed edge populations for every source/spacing/unit treatment:

1. `within_token`: each original token is a separate segment. Score only adjacent
   emitted units inside it; each token has its own final unit without a successor.
2. `within_locus_with_space`: join the locus's token-unit arrays with one reserved
   `<SPACE>` atomic label between tokens. Score adjacent units within that locus.
   Add no leading/trailing separator and never connect different loci.

The reserved label cannot occur in the adapter's plain-letter token alphabet.
Singleton segments contribute full-unit counts and zero edges; keep them in the
segment/coverage denominator. If an entire treatment has no edges, record its
conditional estimate as null rather than zero. No padding or wraparound is used.

Pool counts over the declared edges, weighting successor opportunities equally,
not loci equally. Retain full-unit counts, directed-pair counts and predecessor
counts derived from those pairs. Compute base-2 unsmoothed empirical full-unit
entropy, pair entropy, predecessor entropy and conditional successor entropy:

```text
H(next | predecessor) = -sum n[i,j]/E * log2(n[i,j]/n_out[i])
                     = H(pairs; E) - H(predecessors; E)
```

Also retain `H(pairs; E) - H(full units; N)` as a separately named quantity and
its difference from the matching-marginal conditional estimate. Do not clip it
or call it conditional entropy. Report scored/terminal/singleton counts and
source/spacing/unit/boundary identities with all frequency tables. Differences
in emitted units also change what one unit of preceding context means.

## Execution, interpretation and validation

Commit this plan before manuscript execution. Implement and commit synthetic-
tested code before running the corpus. Verify manual singleton/branching cases,
no cross-token/locus edges, explicit separator behavior, reversible segmentation,
pooled weighting, matching-marginal identity and complete cohort/exclusion
accounting. Test changed input pins and duplicate/missing sources or records.
Replay the full report and keep all 24 treatments without outcome selection.

This is descriptive sensitivity, with no fitted model, language control,
permutation test, p-value or hypothesis rejection. Related source editions and
IT's identical spacing treatments are not independent replications. Source
uncertainty and selection limit coverage. The segment policies are analyst-
declared notation units, not manuscript glyphs or phonemes. This is not a
historical paper replication; its isolated-locus/token boundaries differ from
a globally concatenated text. No source correction, decipherment or translation
is authorized by the result. Later mechanism comparisons must freeze comparable
units, boundary rules and controls under the decipherment protocol.

Role: contributor for the continuing Voynich goal, with verified `tobrien6`
identity, upstream ownership and admin permission. Work is isolated on
`codex/paired-symbol-entropy-1ebd`; existing review owners retain merge decisions.
