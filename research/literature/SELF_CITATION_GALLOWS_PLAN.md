# Paragraph-start augmentation ablation plan

The [twenty-seed census](SELF_CITATION_PREFIX_SEEDS.md) is already exposed.
This follow-up tests a directional response inside the published software,
not a manuscript decipherment or a held-out corpus prediction. Commit this
plan before executing the ablated program and retain every planned outcome.

## Exact source intervention

The pinned release's `AbstractBaseGroupMorpher.handleGallows` uses the shared
`PARAGRAPH_STARTS_WITH_GALLOW_PROPABILITY = 94` in two conditions. In the active
`curveline` path, one condition requests gallows augmentation when a group is
line-initial and paragraph-initial; another controls replacement of existing
gallows outside paragraph-initial rows. A global constant change would affect
both rules.

Change only the paragraph augmentation condition from its named threshold to
literal zero. Require exactly one known source anchor and preserve all other
bytes. The shared constant and its other reference remain 94. The random draw
immediately before the condition remains present. Under the pinned pseudo-random
implementation, `rand(100)` is in 0–99, so `rand < 0` never requests augmentation
through this branch. Ordinary line-initial handling, naturally occurring gallows,
and other paragraph/gallows rules still operate.

This is a precisely versioned source intervention, not a claim that all gallows
forms have been removed. Subsequent branch choices, random-call sequences and
remembered state may diverge; the same seed is not a guarantee of matched
word trajectories or row-context populations.

## Frozen inputs and all cases

- Reuse release `9e98c9122a0f490905e8b66f3911fc7ce095fd26`, the complete
  executable configuration, recorded Java 22.0.2 and reviewed build/environment
  controls. Generation properties match the census, except its declared seed
  and save-path/filename overrides.
- Use every seed 1–20, in order, with 1,200 saved rows per seed.
- Reuse the frozen default census as the reference, with exact producer/input
  hashes. Build the ablated original and ablated observer once each; copy
  third-party source/classes to new local directories only.
- Run one fresh unobserved ablated JVM and one fresh observed ablated JVM per
  seed: 40 new generation processes. Require complete byte equality within each
  pair, successful expected row counts and complete ordered row-call events.
  Retain failures and undefined cells; do not substitute seeds or settings.

## Measurements, predictions and limits

Use the same tested eight q/y first/last, model-paragraph-start cells and exact
equal-row contrast as the census. Exclude initialization, require at least two
native tokens, preserve all eligibility counts/excluded indices, and retain
every per-seed ablated mean and default-to-ablated difference.

Primary predictions: the arithmetic mean across all 20 paired-seed differences
(`ablated - default`) is positive for both **paragraph-initial first-q** and
**paragraph-initial first-y** contrasts. Evaluate only if every planned seed
and both cells are defined; incompleteness is unresolved, not a pass. A
nonpositive difference in either cell fails that directional prediction.
Report the other six cells as descriptive outcomes without selecting a new
success threshold or tuning a parameter after the results.

The paired comparisons describe this deterministic software intervention.
They are not p-values, confidence intervals, a calibrated seed population,
isolated direct effects on matched rows, manuscript mechanism fit, glyph
equivalence, plaintext reading or translation. Model paragraph flags remain
program arguments. A manuscript comparison and any broader causal attribution
need separately specified units, exposure, controls and evaluation conditions.
