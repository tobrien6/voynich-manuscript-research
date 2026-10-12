# Matched other-prefix controls limit the y lookup contrast

The fixed matched comparison gives a **negative adjusted first-minus-other
contrast in all eight treatments**. On the primary ZL split/exclude treatment,
the matched y contrast is +0.43849206 and the assigned non-y control contrast
is +0.70243681, leaving **−0.26394475**. The result limits first-slot specificity
of the lookup diagnostic under this pooled control. It does not identify a
manuscript mechanism or change the [original v1 result](RESULTS.md).

## Registration, inputs and exposure

The [complete control plan](MATCHED_CONTROL_PLAN.md) was committed and remotely
published at `e170810` before new control gains were measured. Its rule is
unchanged. The synthetic-tested implementation, [exact protocol](matched-control-protocol.json),
and [additional exposure record](MATCHED_CONTROL_EXPOSURE.md) were published
at [`41b707b`](https://github.com/tobrien6/voynich-manuscript-research/commit/41b707bb47d4ef8fe7b30e8fb1023ae6a98181ff)
before manuscript execution. The report retains registration and measurement
timestamps as declarations, rather than independent certification of history.

The parent results and full source corpora had already informed this question.
The adjacent [prefix-specificity plan in PR #109](https://github.com/tobrien6/voynich-manuscript-research/pull/109)
was read after this plan was published, before implementation/measurement;
its numerical results were not inspected before this run. It uses fixed y/q/o
comparisons and nine coarse y-only cells with equal cell/unit weighting. This
study uses pooled non-y controls, exact lengths, log-frequency bins and
occurrence-weighted matching pools/targets, with equal unit weights. Keep their
different quantities, cohorts and coverage separate. Neither is independent
manuscript replication or an exposure-valid candidate evaluation.

The pinned ZL3b/IT2a sources, eight uncertainty treatments, original slots,
3,002 common-eligible native loci, development-only internal vocabularies,
source/partition identities and every original y lookup cell are recreated
before scoring. The parent report and registered plan/partition remain unchanged.
No glyph adjudication, new source text, physical-line mapping or translation
is supplied.

## Fixed matching and coverage

For each y candidate, use every retained non-y candidate occurrence in the same
unit and original slot role, of exactly the same ASCII length and development
frequency bin. Count zero is its own bin; positive counts use `bit_length()`:
1, 2–3, 4–7, and successive powers of two. Delete exactly one lower-case leading
ASCII letter from either representation and use the original vocabulary gain
in {-1,0,1}. A target's adjusted gain subtracts its pool's mean gain. There is
no sampled control, fallback, bin widening or choice of a favorable letter.

Pool occurrence weights are equal, and a pool may be reused for several
targets. Within each unit/role, target occurrences have equal weight; final
unit means receive equal weight. Because matched frequency bins have identical
original-membership state, those before-deletion terms cancel in each residual.
The control remains a string-membership comparison, rather than reading accuracy.

The parent's 15-unit frame becomes **12 joint units** with both matched classes
in every treatment. Families 15 and 45 lack a matched first-slot class in every
treatment; family 67 lacks a matched other-slot class in ZL treatments. They
remain in the complete record. The source families are coarse scan-related
groups, rather than independently adjudicated manuscript samples.

| Source | Spaces | Alternatives | Matched first targets / all first targets on the 12 units | Matched other targets / all other targets |
| --- | --- | --- | ---: | ---: |
| ZL3b | split | exclude | 46 / 79 | 57 / 66 |
| ZL3b | split | first | 45 / 79 | 61 / 68 |
| ZL3b | join | exclude | 50 / 87 | 58 / 70 |
| ZL3b | join | first | 50 / 87 | 61 / 71 |
| IT2a | split | exclude | 43 / 85 | 66 / 77 |
| IT2a | split | first | 43 / 85 | 66 / 77 |
| IT2a | join | exclude | 43 / 85 | 66 / 77 |
| IT2a | join | first | 43 / 85 | 66 / 77 |

Coverage differs between roles and treatments. These pooled token counts are
not the equal-unit statistic's denominator. Small strata, unmatched targets
and repeated controls remain visible; no confidence interval or p-value is claimed.

## Complete contrast summary

All contrasts are first-minus-other means on the same 12 joint units. The y
column uses precisely the matched target subset; the control column assigns
its matching pool to each target with the same target weights.

| Source | Spaces | Alternatives | Matched y contrast | Assigned control contrast | Adjusted contrast |
| --- | --- | --- | ---: | ---: | ---: |
| ZL3b | split | exclude | +0.43849206 | +0.70243681 | **−0.26394475** |
| ZL3b | split | first | +0.44543651 | +0.70072460 | −0.25528809 |
| ZL3b | join | exclude | +0.33194444 | +0.49506845 | −0.16312401 |
| ZL3b | join | first | +0.32500000 | +0.48365261 | −0.15865261 |
| IT2a | split | exclude | +0.32500000 | +0.50253970 | −0.17753970 |
| IT2a | split | first | +0.32500000 | +0.50253970 | −0.17753970 |
| IT2a | join | exclude | +0.32500000 | +0.50253970 | −0.17753970 |
| IT2a | join | first | +0.32500000 | +0.50253970 | −0.17753970 |

The predeclared sign outcome is `mixed_or_nonpositive_adjusted_selectivity`;
all eight adjusted values are actually negative. This is a descriptive sign
diagnostic, not a significance test or the parent's +0.05 convention. IT's four
identical outputs are dependent representations, not four replications.

The primary matched y first/other means are +0.50099206 and +0.06250000. Assigned
controls give +0.42364418 and −0.27879263. Thus the negative selective difference
does **not** mean y loses every first-slot comparison: its adjusted first mean
is positive, while its comparative advantage is larger in the other-slot class.
Both role means and their difference are needed to interpret this result.

Control composition differs by role. In the primary equal-unit assigned weights,
first-slot controls are approximately o 27.35%, q 20.07%, d 16.36%, s 16.20%,
t 9.09%, l 8.13%, with smaller c/p shares. Other-slot weights are led by c
28.22%, o 19.16% and q 16.86%. All stratum prefix counts and pool-use counts are
retained. This estimates the declared pooled comparator; it does not establish
that each individual letter has the same effect or isolate a causal feature.

## Full record and reproduction

The [complete report](matched-control-results.json.gz) retains every treatment,
all frame units and strata (including control-only and unmatched strata), lookup
cells, prefix/pool counts, exact numerator/denominator means, missing-class
reasons, original full-frame context, frequency/source/cohort/dependency pins,
and execution record. Lossless gzip packaging preserves all 7,315,802 original
producer JSON bytes. The [archive identity](matched-control-archive.json)
records compressed and decoded sizes and hashes; decoded JSON SHA-256 is
`d7fd4db30835f607ceec2f58a37cdc2fbbe4dd81e1e9ac7b8a70dcb18328eccf`.
Archive bytes identify the stored package; another gzip implementation need
only reproduce the decoded JSON and scientific fields.

From a checkout with both public registration commits available:

```sh
python3 - <<'PY'
import gzip, hashlib, json
from pathlib import Path
base = Path('research/hypotheses/y-layout-prefix-v1')
identity = json.loads((base / 'matched-control-archive.json').read_bytes())
archive = (base / 'matched-control-results.json.gz').read_bytes()
assert len(archive) == identity['archive_bytes']
assert hashlib.sha256(archive).hexdigest() == identity['archive_sha256']
raw = gzip.decompress(archive)
assert len(raw) == identity['decoded_json_bytes']
assert hashlib.sha256(raw).hexdigest() == identity['decoded_json_sha256']
Path('/tmp/voynich-matched-controls.json').write_bytes(raw)
PY
python3 scripts/y_prefix_matched_controls.py --check /tmp/voynich-matched-controls.json
PYTHONPATH=tests python3 -m unittest test_y_prefix_matched_controls -v
```

Thirteen synthetic checks cover lookup cells, bin boundaries, every matching
dimension, occurrence weights, pool reuse, missing coverage, original gaps,
development-only counts, equal unit weights, exact signs and lifecycle drift.
Independent rational arithmetic reconstructed all joint-unit means directly
from stratum cells, reconciled control pair-use/prefix counts, and reproduced
every treatment summary without the production scoring/aggregation functions.
The full report replays and the archive decompresses byte-for-byte.

## Interpretation and next test

The original y lookup prediction survives its original diagnostic; this control
does not retroactively change that record. Its first-slot gain is not distinctive
over the declared matched non-y control relative to other slots. Coarse frequency
matching, incomplete coverage, prefix-mixture differences, source representations
and internal-vocabulary construction still limit interpretation. ASCII length
is not glyph count, and encoded first slots are not verified physical line starts.

Further tests should preserve these results and explicitly separate lexical,
spelling, segmentation and layout alternatives, with image-supported review
and exposure-valid evaluation. No added glyph, language, cipher or translation
is identified by this comparison.
