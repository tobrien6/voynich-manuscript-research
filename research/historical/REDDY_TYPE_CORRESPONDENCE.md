# Positional H / Reddy type partitions and immediate repeats

The recovered Reddy notation preserves every native H type equality under the
fixed nominal token pairing, but merges some different H types. Its equality
partition is therefore coarser on these exposed positions, not identical:
**8,151 H types map to 8,114 Reddy types**. Five additional immediate-repeat
edges occur in Reddy, while both streams have 118 repeated types. Matching
record order and token counts do not guarantee transferable equality events.

## Prerequisite, sources and fixed rule

This follow-up depends on the complete
[literal-envelope comparison](REDDY_ENVELOPES.md) published in
[PR #175](https://github.com/tobrien6/voynich-manuscript-research/pull/175) at
`c6df1ef7401a61a51a8896bb2c93ccc155076bb1`. That comparison verifies every
shared literal key, source order and fallback-retained count, and retains the
H-only normalized-empty record `f106r.P.29;H`. Its acceptance is a prerequisite
for merging this follow-up. The parent input is the publisher's native 1.6e6
H release and the six locally verified paper-associated Reddy files at commit
`643b881b2937bae8193814d8ff5d6e99a48bf7c5`; the
[source manifest](../literature/reddy-source-manifest.json) and
[accepted source intake](../literature/REDDY_SOURCE_INTAKE.md) retain identities,
paper associations and historical limitations.

The [human plan](REDDY_TYPE_CORRESPONDENCE_PLAN.md) and
[machine parameters](reddy-type-correspondence-plan.json) were committed at
[`977fedc`](https://github.com/tobrien6/voynich-manuscript-research/commit/977fedc).
Before any new type scoring, a collaborator suggested exact position-pair
contingency checks; these and explicit repeat boundary scopes were declared at
[`0ce0552`](https://github.com/tobrien6/voynich-manuscript-research/commit/0ce0552).
The synthetic-tested producer was committed at
[`b72488e`](https://github.com/tobrien6/voynich-manuscript-research/commit/b72488e).
All three commits were pushed before the source type graph was measured.
Full sources, inventories, parent envelope/count/order results and prior
approximate repetition results were already exposed. No untouched evaluation
or general conversion success is claimed.

The producer verifies fifteen frozen dependency hashes, six local reference
identities and complete parent report replay. Pair only an exact literal shared
`(page, unit/placement, line, transcriber)` key and the same local token index.
Fail on changed shared order, unequal token counts or unmatched nonempty text.
H uses the accepted normalizer with **no listed-code deletion or manual
exclusions**; the code-deleted stage loses 23 tokens and cannot supply this
equal-rank pairing. Reddy retains its original whitespace tokens, case and
uncertainty notation. Asterisks and singleton tokens are never filtered.

Within each source, type means exact original notation-string equality. Type
IDs are SHA-256 of UTF-8 token bytes, checked for within-domain collision, with
separate H/Reddy domains. No cross-domain spelling equality, alphabet map,
optimized alignment or author program is used. This nominal positional pairing
does not establish physical word or glyph correspondence.

## Complete type relation

The [complete report](reddy-type-correspondence.json) retains 37,919 paired
positions, all 8,151 type-pair edges and their complete support positions, every
node frequency/degree/notation length/asterisk/repeated-type flag, the unmatched
source ledger, all discordant repeat events and all 5,212 flattened joins.
Support positions are `(selected H ordinal, local token index)`, both zero
based; the parent report supplies literal envelopes and physical file lines.
No raw notation token strings or author payload are published.

| Measure | Native H, fallback retained | Reddy full annotation |
| --- | ---: | ---: |
| Paired token occurrences | 37,919 | 37,919 |
| Exact notation types | 8,151 | 8,114 |
| Types with one partner | 8,151 | 8,078 |
| Types with two partners | 0 | 35 |
| Types with three partners | 0 | 1 |
| Nonfunctional types toward the other domain | 0 | 36 |
| Occurrences of nonfunctional types | 0 | 321 |
| Asterisk-containing types | 125 | 292 |
| Asterisk-containing occurrences | 160 | 392 |

All H types have one Reddy partner. Thirty-five Reddy types combine two H types
each, and one combines three: 36 target classes combine 73 source types,
reducing the type total by 37. Six of those 36 classes contain asterisks in
Reddy; thirty do not. The diagnostic retains both groups. It supplies a finite
observed many-to-one type relation, not a character-level conversion rule or an
explanation of how the files were produced.

Let `n_ab` be the count of paired occurrences of H type `a` and Reddy type `b`.
Equality in both domains for unordered pairs of distinct positions is
`sum choose(n_ab, 2)`. Source equality separately uses the corresponding row
or column marginal frequencies. The full position-pair accounting is:

| Equality of a pair of positions | Unordered pairs |
| --- | ---: |
| Both notations | 2,207,028 |
| H only | 0 |
| Reddy only | 835 |
| Neither | 716,698,458 |
| Complete denominator | 718,906,321 |

The zero H-only count independently matches the functional H-to-Reddy graph.
The 835 Reddy-only pairs establish that equality partitions differ. No accuracy
percentage dominated by the numerous unequal pairs, random control, tail or
linguistic interpretation is introduced.

## Immediate-repeat scopes and every discordant edge

A counts equal consecutive occurrence edges; B counts distinct types with at
least one such edge. The flattened stream has 37,918 edges: 32,706 within
records and 5,212 joins. A join is a declared file-stream edge, not verified
physical adjacency. No cyclic edge or manually excluded token is introduced.

| Edge scope | Both equal | H only equal | Reddy only equal | Neither equal |
| --- | ---: | ---: | ---: | ---: |
| Within record | 311 | 0 | 4 | 32,391 |
| Flattened joining | 12 | 0 | 1 | 5,199 |
| All flattened edges | 323 | 0 | 5 | 37,590 |

Thus flattened A is 323 for H and 328 for Reddy; within-record A is 311/315,
and joining A is 12/13. B is 118 in each full stream: 115 within-record types
and nine joining types, with six types in both scopes. The 118 H repeated types
have 118 distinct Reddy partners, which are exactly the Reddy repeated types.
The five added edges introduce no additional repeated Reddy type. These latter
set statements are direct accounting from the complete retained graph and
repeated-type node flags, not a further fitted experiment.

All five discordant edges are Reddy-only equality events involving an
asterisk-containing Reddy type:

| Flat left token index | Scope | Left H envelope / local index | Right H envelope / local index |
| --- | --- | --- | --- |
| 10,095 | Within | `f57v.R2.1;H` / 4 | `f57v.R2.1;H` / 5 |
| 10,112 | Within | `f57v.R2.1;H` / 21 | `f57v.R2.1;H` / 22 |
| 10,129 | Within | `f57v.R2.1;H` / 38 | `f57v.R2.1;H` / 39 |
| 10,146 | Within | `f57v.R2.1;H` / 55 | `f57v.R2.1;H` / 56 |
| 11,036 | Join | `f66r.M.9;H` / 0 | `f66r.M.10;H` / 0 |

All indices refer to the fallback-retained source normalization before manual
exclusions. The joins retain intervening selected-H ordinals. One join runs
from H ordinal 4,421 to 4,423 across the sole unmatched empty ordinal 4,422;
both notation equality flags are false there. This does not hide the empty
record or claim physical continuity through it.

## Reproduce and validation

Python 3.10 or later, standard library only. Keep the six pinned Reddy reference
files local and run from the repository root:

```sh
python3 -m unittest tests.test_historical_reddy_types -v
python3 scripts/audit_historical_reddy_types.py --reference /path/to/local/reference --check research/historical/reddy-type-correspondence.json
python3 scripts/audit_historical_reddy_types.py --reference /path/to/local/reference --output /tmp/reddy-type-correspondence.json
cmp /tmp/reddy-type-correspondence.json research/historical/reddy-type-correspondence.json
```

Fifteen focused tests cover bijective relabeling, merges, splits, nonfunctional
relations, empty/singleton cases, asterisk/Unicode transport, unmatched/count/
order failures, duplicate keys, hash collisions, fifteen dependency pins,
complete parent rejection before scoring and output failure preservation.
All 1,365 pairs of binary type sequences of lengths zero through five agree
with a direct unordered-position-pair oracle, direct immediate-edge equality,
repeated-type sets and complete support accounting. Tests include equal A/B
totals with different edge events, and equal immediate events with different
nonadjacent equality partitions. One hundred twenty temporary early/late
direct/symlink/hardlink alias cases preserve all twenty-four protected files.
Two additional regressions retain protected names and entry-time resolved
targets when input entries disappear or symlinks change during calculation or
serialization. Matching names also account for case and Unicode normalization.
These checks are pre-write safeguards, not an atomic filesystem transaction.

The complete report replays byte for byte. An independent raw ZIP/annotation
scanner importing none of the accepted readers/normalizer or new producer
checks every paired position, both node tables, all graph edges and supports,
original-order digest, pair contingency, repeated-type sets/scopes, all five
discordant events and every join. Its Reddy-only equality count uses cross-H
type frequency products within target classes, rather than the producer's
marginal subtraction. Original report SHA-256:
`651c5b9227c9f7559863cb64329a2b89e39eedd37bd11effd4bc619fa3f27ef3`.
The later output-guard repair refreshes only `producer_sha256`; every other
report value and both preregistered plans are unchanged. The complete repaired
report SHA-256 is
`e082834abaf5f72ba0aba72062edcb810ddf91dd35dac985e74d802a202b2ef5`.

## Rights, interpretation and next work

Native H credits Jorge Stolfi, Gabriel Landini, Jim Reeds, Takeshi Takahashi and
the original transcribers in the unmodified member. Its publisher permits
copying, use, modification and republication with due credit and without
additional conditions or copyrights. Those source terms are not replaced by
the repository MIT license. No license was found in the pinned Reddy tree;
its raw tokens, corpus bodies and author program remain local.

The graph constrains which equality-based measurements transfer between these
finite source streams. It does not identify a language, glyph mapping, physical
word pairing, historically used transform, original-author corpus bytes or
decipherment. Character prediction results, uncertainty symbols and any future
conversion candidate need their own stated notation policy. A candidate must
freeze a complete rule and separate evaluation material before claiming
generalization; this exposed full-source relation is not that evaluation.
