# Alternative first prefixes are required by the matched control

The [within-role matched other-prefix comparison in PR #128](https://github.com/tobrien6/voynich-manuscript-research/pull/128)
requires eligible non-y first-slot occurrences in each included unit. A formatter
that prefixes every retained first slot with y supplies no such control pool.
Its matched first mean is undefined, even when the formatter and inverse are
fully known. This is a support property of the declared comparison.

The accepted [known-marker example](KNOWN_MARKER_OPPORTUNITY.md) supplies a
concrete check without manuscript inputs or a new fitted construction. The
example's existing y-only opportunity standardization and PR #128's within-role
non-y matching are different comparisons. Their coverage must be assessed
separately.

## Why the first class becomes unmatched

PR #128's [fixed rule](https://github.com/tobrien6/voynich-manuscript-research/blob/e170810e9291cf2fa4feec5ba9736061181de65e/research/hypotheses/y-layout-prefix-v1/MATCHED_CONTROL_PLAN.md)
matches each y target to all eligible non-y occurrences in the same unit,
original slot role, exact ASCII length and development-frequency bin. Eligible
forms have at least two ASCII letters and a lowercase initial. Frequency zero
has bin zero; positive counts have bin `count.bit_length()`.

Suppose every retained first-slot form in a unit begins with y. Every
first-slot non-y pool is then empty, for every length and frequency bin.
No first target is matched. The role mean and first-minus-other adjusted
contrast are undefined; that unit fails the requirement for both matched
classes. This conclusion needs no lookup gains, frequency estimates or
choice of another prefix. It holds separately for each treatment. If every
unit has this property, the joint comparison has no units.

## The fixed accepted example

The published codec adds exactly one y to every first slot and leaves other
slots intact. Its inverse recovers all 22 source tokens. Diagnostic first forms
are four `yb` and one `ya`; diagnostic other forms are four `ya`, one `yc` and
five `z`. Development internal counts are `a:1, b:1, c:1, ya:2, z:1`.

Applying the declared eligibility and strata gives the complete pool support:

| Original role | ASCII length | Frequency bin | Eligible y targets | Eligible non-y controls |
| --- | ---: | ---: | ---: | ---: |
| first | 2 | 0 | 4 | 0 |
| first | 2 | 2 | 1 | 0 |
| other | 2 | 0 | 1 | 0 |
| other | 2 | 2 | 4 | 0 |

All ten y targets are unmatched. The five internal `z` forms have length one
and are outside control eligibility. Thus this particular fixture lacks both
matched classes. Its first-slot failure also follows from the general argument,
regardless of what eligible controls its other slots might have contained.

The existing y-only standardized contrast remains exactly zero on its two
common cells. No within-role non-y residual is defined on these rows. A zero
defined score and an undefined score caused by missing support are separate
results. These support counts were reasoned from the published fixture before
the diagnostic recheck below; this is an analytical check on already exposed
synthetic material, with no unseen prediction or new manuscript measurement.

## Scope and next prediction

The within-role residual describes units with the required observed prefix
variation and matching support. Its negative manuscript contrast remains the
reported conditional string-membership result; this note changes no cohort,
pool, weight, decision or report. Extending a conclusion to excluded units or
to a universal formatter requires additional predictions and evidence.

The literal codec itself predicts y at every encoded first slot, an extra ASCII
character there, and exact recovery under its stated inverse. Prefix counts
can contradict that specific rule. The support limit concerns the matched
contrast and does not make marker hypotheses untestable. This toy establishes
no manuscript codec, glyph function, language, decipherment or translation.

## Reproduce the support check

From the repository root, standard-library Python:

```sh
python3 - <<'PY'
from collections import Counter, defaultdict
import json
from pathlib import Path
from scripts import known_marker_opportunity as codec
saved = json.loads(Path('research/representation/known-marker-opportunity.json').read_bytes())
assert codec.make_report() == saved
rows = saved['encoded']['diagnostic']
assert codec.decode(rows) == saved['source']['diagnostic']
assert len(rows) == 5 and all(row[0].startswith('y') for row in rows)
counts = Counter(value for row in saved['encoded']['development'] for value in row[1:])
pools = defaultdict(lambda: {'y': 0, 'non_y': 0})
for row in rows:
    for index, value in enumerate(row):
        eligible = len(value) >= 2 and value.isascii() and value.isalpha() and 'a' <= value[0] <= 'z'
        if eligible:
            key = ('first' if index == 0 else 'other', len(value), counts.get(value, 0).bit_length())
            pools[key]['y' if value.startswith('y') else 'non_y'] += 1
assert dict(pools) == {
    ('first', 2, 0): {'y': 4, 'non_y': 0},
    ('first', 2, 2): {'y': 1, 'non_y': 0},
    ('other', 2, 0): {'y': 1, 'non_y': 0},
    ('other', 2, 2): {'y': 4, 'non_y': 0}}
for role in ('first', 'other'):
    assert sum(pool['y'] for key, pool in pools.items() if key[0] == role and pool['non_y']) == 0
print('Complete accepted toy replays; both matched classes lack control support.')
PY
```

The original [complete codec report](known-marker-opportunity.json) and
[input identities](known-marker-opportunity-inputs.json) remain unchanged.
The support recheck uses no manuscript source tokens or images and does not
call the pending matched-control producer or score a new contrast.
