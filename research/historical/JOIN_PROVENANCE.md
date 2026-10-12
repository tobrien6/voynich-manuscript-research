# Source context for every equal native-record join

Question: which exact H records form the joining repeats in the four historical
streams, and are any created by concatenating across excluded/empty H records?

The [plan](JOIN_PROVENANCE_PLAN.md), [parameters](join-provenance-plan.json) and
synthetic-tested producer were committed before inspecting event identities.
The global/conditional counts and source inputs were already exposed. The
[complete census](join-provenance.json) retains all four variants, every equal
join, endpoint descriptors and population denominators. It changes no parser,
input, edge definition or repetition statistic from the [global assay](REPEATED_TYPES.md).

## Complete population and negative bridge result

| Ring treatment | f66r removed | All joining edges | Same page/unit | Same page, different unit | Different page | Joins spanning empty/excluded H records | Equal joins |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Omit R2 | M | 5,126 | 4,660 | 242 | 224 | 12 | 9 |
| Omit R2 | L | 5,143 | 4,677 | 242 | 224 | 14 | 10 |
| Remove ring singletons | M | 5,126 | 4,660 | 242 | 224 | 12 | 9 |
| Remove ring singletons | L | 5,143 | 4,677 | 242 | 224 | 14 | 10 |

Every observed equal join is between consecutive selected H records on the same
native page and in the same native unit. None spans an intervening excluded or
empty H record, crosses native units, or crosses pages. Thus those 12/14 bridged
joins supply no observed equal event in these inputs. This is a complete
negative result for this edge population, not a claim that other normalization
or exclusion effects are absent.

H adjacency ignores other transcribers' records. Physical file-line references
below count lines in `L16+H-EV/TEXT16E6.EVT`, not lines on manuscript images.
Every endpoint retains a raw-body SHA-256, zero-based H ordinal, retained length,
pre-manual normalized count/index and all recorded exclusion reasons.

## All distinct endpoint pairs

The nine common pairs and the additional L-removal pair below exhaust the
source-ordered event lists. Ring treatments retain the same endpoint identities;
their flat token indices can differ. Native `;H` codes are shown explicitly.

| Literal token | Left native record | Right native record | Physical source-file lines | Present when f66r M removed | Present when f66r L removed |
| --- | --- | --- | --- | --- | --- |
| `dar` | `f6r.P.3;H` | `f6r.P.4;H` | 3345 → 3349 | Yes | Yes |
| `daiin` | `f35v.P.16;H` | `f35v.P.17;H` | 8597 → 8601 | Yes | Yes |
| `f` | `f66r.M.15;H` | `f66r.M.16;H` | 14033 → 14038 | No | Yes |
| `oteody` | `f73v.S0.2;H` | `f73v.S0.3;H` | 20829 → 20832 | Yes | Yes |
| `qol` | `f78v.P.22;H` | `f78v.P.23;H` | 23406 → 23411 | Yes | Yes |
| `qokaiin` | `f82r.P1.3;H` | `f82r.P1.4;H` | 24959 → 24964 | Yes | Yes |
| `dar` | `f84r.P.10;H` | `f84r.P.11;H` | 26210 → 26215 | Yes | Yes |
| `qokeedy` | `f84r.P.27;H` | `f84r.P.28;H` | 26302 → 26307 | Yes | Yes |
| `daiin` | `f87r.P.12;H` | `f87r.P.13;H` | 28814 → 28817 | Yes | Yes |
| `daiin` | `f90r2.P.5;H` | `f90r2.P.5a;H` | 30592 → 30596 | Yes | Yes |

Joining events involve six types under M removal and seven under L removal.
Five—`daiin`, `dar`, `qokaiin`, `qokeedy`, `qol`—also repeat within records.
`oteody`, and the additional `f` under L removal, are the joining-only repeated
types. This reconciles within-record B=113 with complete B=114/115; adding the
two scope type counts without subtracting overlap would be incorrect.

Both `oteody` endpoints are retained singletons. Their raw H bodies are
`oteody=` in both records. The additional pair's raw bodies are
`f!!!!!!!!!!!!!!=` and `f!!!!!!!!!!!!=`; accepted filler/punctuation removal
leaves one `f` token in each. Removing unit M excludes them; removing L retains
them. These are direct joins already present in selected H order, not new
adjacencies across deleted records.

As a structural inference, any permutation confined to each of these singleton
records leaves its joining repeat unchanged. This identifies source contexts
for the invariant singleton pairs in the [conditional study](https://github.com/tobrien6/voynich-manuscript-research/pull/131);
it does not infer what their marks represent or verify a physical-line boundary.
No change to that study's all-join scope is proposed.

## Source identity, validation and reproduction

The source is the credited publisher-hosted [1.6e6 release](https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/98-12-28-interln16e6/)
and [unmodified archive](https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/98-12-28-interln16e6/text16e6.zip).
Archive/member identities, all twelve frozen dependencies and source reuse terms
are retained in the report. Endpoint notation is a source-derived observation
under those terms; it is not a new translation or material covered by the
repository's code license.

Ten focused tests verify direct/bridged joins, natural versus manual emptiness,
overlapping type sets, page/unit classifications, empty/noncyclic streams,
case-sensitive identity, order/source/index/hash/reference mismatches and strict
JSON failure preservation. Seventy-five temporary direct/symlink/hardlink
alias cases cover every protected path before computation and during it.
The full report replays byte for byte. Separately reading raw ZIP member lines,
without the production envelope parser, confirms the exact native envelopes and
body hashes at every reported endpoint: twenty distinct source records.

Python 3.10+, standard library only; recorded run used Python 3.14.3:

```sh
python3 scripts/audit_historical_joins.py --output research/historical/join-provenance.json
python3 scripts/audit_historical_joins.py --check research/historical/join-provenance.json
python3 -m unittest tests.test_historical_joins -v
```

## Limits and next work

Native pages, units, line suffixes and adjacency are source annotations. They do
not verify physical text/image continuity or independent manuscript units.
In particular, `f90r2.P.5` and `.5a` remain native labels, and `S0`/`M` do not
receive a new physical or linguistic interpretation here. No H/modern crosswalk
or ambiguous record-projection pairing is created; [PR #135](https://github.com/tobrien6/voynich-manuscript-research/pull/135)
addresses a different lossy record-group question.

All four streams share exposed source material and the known parser/count/label
discrepancies. Exact original-author input recovery, image/glyph adjudication,
new null calibration, mechanism comparison and a validated translation remain
separate requirements. The census provides a complete source-addressed review
list; it supplies no language, cipher mapping, significance or decipherment claim.
