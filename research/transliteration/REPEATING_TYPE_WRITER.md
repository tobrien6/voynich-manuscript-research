# Guarded companion for the repeating-type mean

Use the companion when writing the accepted mean report:

```sh
python3 scripts/write_repeating_types.py --output /tmp/repeating-types.json
python3 scripts/write_repeating_types.py \
  --check research/transliteration/repeating_types.json
```

The original `scripts/repeating_types.py` stays unchanged at SHA-256
`d6ce0b03beb336813757c9ee5d7aa747632d14b8f7752e94d4831f2c84ec7cca`.
Its bytes and report fingerprints are dependencies of the accepted exact
variance and the fixed image selection. Changing that producer solely for an
output repair would invalidate those scientific input pins. The companion
calls its existing `report()` and `encoded()` functions; it adds no new
filter, measurement, statistic or report provenance field.

## Reproduced gap and protected command

The frozen producer checks output aliases before calculation and again before
writing, but invokes serialization inside the write call after the last check.
An output link introduced during serialization can therefore bypass the last
check and overwrite a protected input. Six temporary synthetic-source probes
reproduce this: symbolic and hard links targeting a copied plan, copied ZL raw
file and copied producer are each overwritten by the legacy CLI path.
No real source, plan or implementation file was used as a probe target.

The protected command is **`write_repeating_types.py --output`**. It captures
declared input paths at entry, rejects aliases before calculation, completes
both calculation and serialization, then checks the original paths and current
catalog declarations immediately before writing. Direct, symbolic and hard
aliases of the catalog, plan, baseline, raw sources, calculation engines and
both the actual producer and companion are rejected. Keeping the original
path snapshot also protects a consulted raw file if its catalog declaration
is removed during construction/serialization; new current declarations are
included as well.

The original frozen CLI is **not repaired** by this companion. Its output path
still has the reproduced gap; use the command above for writes. Read-only
legacy check mode remains available. These checks cover aliases present at
entry or after construction/serialization; the final check and filesystem
write are not an atomic operation. No concurrency lock or complete source
mutation/execution attestation is introduced.

## Compatibility and validation

Standard library, Python 3.10 or later; recorded on Python 3.14.3:

```sh
PYTHONPATH=tests python3 -m unittest \
  test_repeating_type_writer test_repeating_types \
  test_repetition_moments test_token_baselines
```

All **28** targeted tests pass: five new companion methods plus the 23 accepted
mean/moment/tokenizer methods. New tests run the actual copied CLI on temporary
synthetic inputs and match its complete output bytes to the original producer;
verify ordinary check mode, typed and duplicate-key cache rejection and source
pin drift; reject entry aliases for every declared input before calculation;
and preserve copied plan/raw/producer/companion bytes when symbolic or hard
aliases are introduced during either construction or serialization. Separate
catalog-mutation fixtures cover retained entry paths and newly declared paths.

The new command's native output is byte-for-byte identical to the entire
accepted `repeating_types.json`, including all eight treatments, fractions,
counts, slot digests and producer/source/plan/baseline fingerprints. Its SHA-256
remains `6e4ea04bc75ba936da93d80143928cf98e7d953d2be2e34aa5f14e6a5400f6ea`.
The original producer, mean report, plans, source catalog, baseline and all
calculation engines remain unchanged. This is post-result output maintenance,
not a new scientific result or a change to interpretation.

Final maintainer integration with main `8a08e771936e05fb3d8f7e283fe9e7a0cb206e89` passes all
**864** repository tests. A separate temporary-copy audit reproduced the six
legacy overwrites and verified 24 construction/serialization alias refusals,
36 entry refusals, four relocated actual-module refusals and four catalog
snapshot/current-path refusals. The complete native output still matches the
accepted report bytes; no frozen producer or input/report pin changes.
