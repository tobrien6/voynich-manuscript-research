# Literal-chain and token-boundary concordance

On **2,940 common eligible native P0 loci**, ZL3b and IT2a have identical
concatenated encoded strings at 2,054 loci and different strings at 886.
Among the identical strings, token boundaries disagree at **562** loci under
split spacing and **767** under join spacing. There are **359** boundary
disagreements under both policies, including the
[f67r1.1 case](https://github.com/tobrien6/voynich-manuscript-research/pull/106).
Literal string agreement therefore does not establish tokenization agreement.

The [source-pinned count figure](figures/TOKEN_BOUNDARIES.md) displays both
complete category partitions and the common denominator.

This exposed-data description measures the pinned transcriptions. It does not
adjudicate manuscript spaces, choose an edition, or establish glyph equivalence,
a language, a decipherment, or a translation. It supplies a traceable set of
cases for later image review and a segmentation sensitivity constraint for
candidate mechanisms.

## Sources and fixed cohort

The [source catalog](../../data/transliterations.json) pins the public CC0
[Zandbergen–Landini 3b](https://voynich.nu/data/ZL3b-n.txt) and
[Takahashi/LSI extraction 2a](https://voynich.nu/data/IT2a-n.txt), with credits,
edition statements, alphabet labels and exact checksums. These are the specific
ZL3b `Eva-` and IT2a `EvaT` exports, rather than all work by either transcriber.
The [source decision](DECISION.md) records their relationships and reuse terms.

Use the accepted [plain-eva-v1 adapter](TOKEN_ADAPTER.md) with only P0 selected.
The accepted [coverage/key contract](TOKEN_COVERAGE.md) freezes loci eligible in
both editions under both comma policies. Whole loci with alternatives,
unreadability, ligature braces, extended codes or invalid notation are excluded;
no interior slots are removed to manufacture adjacency. Native case remains
unchanged. Drawing interruptions remain adapter separators under both policies.

There are **3,884 shared present P0 keys**, of which **944** fail joint eligibility.
One ZL-only present P0 key, `f106r.29`, stays outside that candidate intersection;
there are no IT-only present P0 keys. The retained keys span **202 native page
identifiers**. These are source units, including foldout names, rather than
independent leaves or verified physical regions. The selected-key SHA-256 is
`85ee6b804b6e8d0ddfe2dbf7a3b8bb04e34d426ca03429b81cff2dfd983d67c2`.

This diagnostic allows **one token** and includes every present P0 locator,
including same-line fragments. It therefore has a different denominator from
prefix controls requiring regular locators and at least two tokens. Any
cross-source locator differences would be retained; there are none here.
The [complete report](token_boundary_concordance.json) retains candidate and
selected keys, every excluded candidate and its source/policy reasons,
source-only keys, full adapter denominators and snapshot hashes. Exclusion
reasons may overlap and must not be summed as independent losses.

## Measurement

Concatenate each locus's nonempty ASCII-letter tokens without separators.
Record a token boundary at the cumulative ASCII-letter offset after each token
except the final token. Compare offset sets only when the two concatenated
strings are exactly identical, including case. For different strings, report
`different_chains` and perform no alignment or boundary-offset comparison.
Offsets are encoded character coordinates, not image pixels, manuscript-glyph
counts, or phonetic units. Locus endpoints are not counted as token boundaries.

Every contrast uses the same 2,940 keys. Categories are mutually exclusive:

| Cross-source treatment | Same chain and boundaries | Same chain, different boundaries | Different chains |
| --- | ---: | ---: | ---: |
| ZL split vs IT split | 1,492 | 562 | 886 |
| ZL join vs IT join | 1,287 | 767 | 886 |

Splitting or joining commas preserves each source's literal chain at every
retained locus. Consequently, the 886 different-chain keys are identical across
these two contrasts. Boundary disagreements under split and join overlap at
359 loci; this is an intersection, not 562 plus 767 independent observations.

| Source/policy | Native tokens | One-token loci | Loci with commas | Drawing interruptions / loci |
| --- | ---: | ---: | ---: | ---: |
| ZL3b split | 25,233 | 3 | 1,241 | 503 / 418 |
| ZL3b join | 23,434 | 4 | 1,241 | 503 / 418 |
| IT2a split | 24,855 | 3 | 0 | 507 / 422 |
| IT2a join | 24,855 | 3 | 0 | 507 / 422 |

Within ZL, 1,241 loci change boundary sets between split and join; 1,699 retain
them. ZL has 1,799 commas on this cohort, exactly the reduction in token count.
IT's two token treatments are identical and supply no independent replication.
The fourth ZL join singleton is `f99v.43`; retaining it prevents a two-token
minimum from hiding a source/policy segmentation difference.

Drawing interruptions occur in at least one edition at 86 of the 562 split
boundary disagreements and 119 of the 767 join disagreements. These separators
must not be interpreted automatically as word spaces. The report preserves both
interruption counts for each boundary-disagreement record. Every category's
complete native-key set and digest is retained, together with all disagreement
offsets, chain lengths/checksums, original identifiers, source file line numbers
and token counts. The complete boundary arrays can be reconstructed from the
pinned source records; the report stores their differences without copying token
text.

For `f67r1.1`, both editions concatenate to the same 49-character chain under
both policies. ZL has nine tokens and IT eight. ZL alone has a boundary at
offset 45. This reproduces the accepted source-informed image case while
preserving its provisional row/region association and unresolved word division.
The corpus audit adds no image review or source correction.

## Replay and validation

```sh
python3 scripts/token_boundary_concordance.py --check research/transliteration/token_boundary_concordance.json
python3 scripts/token_boundary_concordance.py --output /tmp/token-boundary-concordance.json
python3 -m unittest tests.test_token_boundary_concordance -v
```

Source bytes are verified through the accepted loader before preprocessing.
The report pins the catalog and analysis implementation dependencies; checking
recomputes the complete content with numeric/Boolean type distinctions.
The CLI protects source and implementation paths before writing an output.
Eight tests cover singletons, displaced boundaries at equal token counts,
case-sensitive chain disagreement without alignment, whole-locus exclusion,
source-only/absent/unselected records, fixed selection across all treatments,
metadata differences, invalid producer contracts, source/implementation output
protection, full replay and the exact f67r1.1 result.

An independent bare-letter/separator reconstruction also checked all **11,760**
selected source-policy records directly against their native source text and
recovered every cross-source category key. This validates the implementation
on these inputs without supplying independent manuscript readings.

The case and source statistics were already exposed before this follow-up.
There is no prospective registration, untouched evaluation set, significance
test or random-sampling claim. Joint eligibility can select systematically
different loci, and literal Eva-/EvaT agreement does not resolve their glyph
conventions. Next, review deterministically selected persistent disagreements
against independently assigned manuscript regions, retaining image uncertainty;
test any frozen segmentation rule on exposure-valid reserved material under the
[evaluation protocol](../DECIPHERMENT_PROTOCOL.md).

The [minimal shared-anchor span inventory](BOUNDARY_DISAGREEMENT_SPANS.md)
localizes every identical-chain boundary disagreement to complete source-token
partitions between shared encoded offsets, without assigning physical words.

The [exact token-count accounting](BOUNDARY_COUNT_ACCOUNTING.md) separates
same-chain boundary contributions from the unaligned different-chain remainder
and retains equal-token-count cases with different encoded boundaries.
