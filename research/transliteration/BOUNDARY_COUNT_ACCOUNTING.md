# Token-count accounting for source-boundary disagreements

On the accepted **2,940-locus** common cohort, ZL has 378 more native tokens than
IT under comma splitting, and 1,421 fewer under joining. Boundary differences
on identical encoded strings contribute **+239** and **−943** respectively.
The remaining **+139** and **−478** come from the different-chain cohort, whose
boundary positions are not aligned. This arithmetic does not attribute that
remainder exclusively to glyph edits or token boundaries.

The [machine-readable accounting](boundary_count_accounting.json) is a direct
decomposition of the accepted [boundary report](TOKEN_BOUNDARY_CONCORDANCE.md),
[PR #113](https://github.com/tobrien6/voynich-manuscript-research/pull/113).
It keeps the exact parent checksum/cohort/source identities and supplies two
deterministically selected cases where equal token counts conceal different
boundaries. No source data, selection rule or parent measurement changes.

## Exact identities and denominators

For a nonempty token list, token count is the number of internal encoded
boundaries plus one. On an identical concatenated ASCII chain, the shared
boundary offsets cancel:

```text
n_ZL − n_IT = |B_ZL \ B_IT| − |B_IT \ B_ZL|
```

For the complete cohort, partition the keys into identical chain/boundaries,
identical chain/different boundaries, and different chains. The first class has
zero token-count difference. Sum the second class's signed differences, and
retain the third as a scalar token-count remainder without aligning strings.
The same key cohort is used under both policies; one-token loci and same-line
fragments remain included.

| Quantity, ZL minus IT | Split | Join |
| --- | ---: | ---: |
| ZL native tokens | 25,233 | 23,434 |
| IT native tokens | 24,855 | 24,855 |
| Overall token difference | +378 | −1,421 |
| Identical chain and boundaries | 0 on 1,492 loci | 0 on 1,287 loci |
| Identical chain, different boundaries | +239 on 562 loci | −943 on 767 loci |
| Different chains, unaligned remainder | +139 on 886 loci | −478 on 886 loci |

These are unweighted sums of native-token counts. They are not averages,
source-accuracy estimates, causal effects or physical-word counts. The third
class can contain both encoded-string and segmentation differences; no method
here separates those contributions.

## Cancellation and equal-count disagreements

Within the identical-chain boundary-disagreement class:

| Quantity | Split | Join |
| --- | ---: | ---: |
| Loci with more ZL tokens | 361 | 27 |
| Loci with more IT tokens | 173 | 719 |
| Equal counts with different boundaries | 28 | 21 |
| Positive token differences summed | +427 | +29 |
| Negative token differences summed | −188 | −972 |
| ZL-only boundary offsets | 462 | 53 |
| IT-only boundary offsets | 223 | 996 |
| Total symmetric boundary differences | 685 | 1,049 |

For example, +427 and −188 cancel to +239 under split. The 685 non-shared
boundary-offset occurrences remain visible despite that smaller net token
difference. Counts of offsets, loci and tokens are distinct denominators.
Encoded drawing-interruption separators are included as in the parent adapter;
none of these events is automatically a manuscript word space.

The complete native-key lists for the equal-count class are retained. Selecting
the lexicographically first key separately within each policy gives:

- **Split, `f100r.24`:** both editions have ten tokens on the same 56-letter
  chain, but ZL alone has boundary offset 28 and IT alone has offset 37.
- **Join, `f103v.38`:** both editions have seven tokens on the same 31-letter
  chain, but ZL alone has boundary offset 6 and IT alone has offset 25.

These are encoded partitions. Two non-shared offsets do not identify a single
physical space that moved. Both full native readings and their split/join token
arrays are retained; the equal-count statement concerns the named policy.
Neither example assigns a glyph/image region or a linguistic word division.

Joining removes 1,799 ZL tokens and zero IT tokens on the full cohort. The
change in the identical-chain contribution is 1,182; the change in the
different-chain remainder is 617. Their sum is exactly 1,799. The parent already
records 1,799 ZL uncertain commas, and unchanged IT token arrays; this is an
accounting identity, rather than another replication or new experiment.

## Replay and validation

The parent bytes have SHA-256
`8c93d9cf1bb83e4f9690378d5fdd6100377e019bf17dede7e0f70de7a4df1bb6`.
Reproduce the central decomposition with Python's standard library:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
raw = Path('research/transliteration/token_boundary_concordance.json').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '8c93d9cf1bb83e4f9690378d5fdd6100377e019bf17dede7e0f70de7a4df1bb6'
p = json.loads(raw)
totals = {(r['source_id'], r['spacing']): r['token_count'] for r in p['variants']}
for policy in ('split', 'join'):
    rows = p['cross_source'][policy]['boundary_disagreements_on_identical_chains']
    deltas = [r['left_token_count'] - r['right_token_count'] for r in rows]
    assert all(delta == len(r['only_left_boundary_offsets']) - len(r['only_right_boundary_offsets'])
               for delta, r in zip(deltas, rows))
    overall = totals[('ZL3b', policy)] - totals[('IT2a', policy)]
    print(policy, 'overall', overall, 'same-chain boundary contribution', sum(deltas),
          'unaligned different-chain remainder', overall - sum(deltas))
PY
```

All category-specific token sums and every per-locus difference were also checked
against a fresh accepted-adapter replay of the pinned source text, rather than
only subtracting aggregate report totals. Every equal-count key and both
examples' original identifiers, source file lines, text, token arrays and offsets
were verified. This documentation/data follow-up adds no executable or tests.

The sources and results were already exposed. No inferential test, independent
sample, source correction, glyph-conversion claim or untouched evaluation is
introduced. For a decoding mechanism that relies on token counts or lengths,
these identities show why aggregate agreement is insufficient: retain source
segmentation choices and inspect local disagreements before proposing a frozen
rule under the [evaluation protocol](../DECIPHERMENT_PROTOCOL.md).
