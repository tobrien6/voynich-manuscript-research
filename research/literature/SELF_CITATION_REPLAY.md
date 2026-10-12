# Repeated source builds reproduce the supplied self-citation output

On Homebrew OpenJDK 22.0.2, the pinned `v1.0.1` Java source generated identical
complete files in all three repeated cases. Both 1,200-line runs also reproduced
the release's supplied `vms_generated.txt` **byte-for-byte**, including its
comment header. This establishes a bounded software reproduction on one runtime.
It does not test the mechanism against the manuscript or reproduce the paper's
statistical analysis.

The [plan](SELF_CITATION_REPLAY_PLAN.md) was committed before executing these
six runs. The source and supplied artifact were already exposed by the
[implementation audit](COPYING_MECHANISM.md); this is not independently
timestamped preregistration or a registered manuscript hypothesis. The
[complete run record](self-citation-repeatability.json) retains every planned
case, source/class fingerprint, effective setting, exit outcome and output hash.

Review added `JDK_JAVAC_OPTIONS` to the suppressed compiler/VM environment
variables and made version checks compare the exact version token. The earlier
[run record at the original PR head](https://github.com/tobrien6/voynich-manuscript-research/blob/7e92ba26f3df19ef2d336510fcb2564fa26a7250/research/literature/self-citation-repeatability.json)
remains available. The corrected runner repeated all six fixed cases in new
directories. Source/class inventories, frozen plan, effective configurations,
and every generated-output fingerprint were unchanged; runner and local
build-log provenance were refreshed. No seed, setting or comparison was chosen
from these repeated outcomes.

## Source, configuration and build

Use author repository commit
[`9e98c9122a0f490905e8b66f3911fc7ce095fd26`](https://github.com/TorstenTimm/SelfCitationTextgenerator/tree/9e98c9122a0f490905e8b66f3911fc7ce095fd26),
the tag identified by the earlier audit. Check the local HEAD and compare all
35 working Java sources with their committed blobs before compilation.
The run record contains each file's SHA-256 and 46 compiled-class fingerprints.

Use the full pinned `executable/conf.properties`, not merely the serialized
output header. It has SHA-256
`00944114753a7019e920199ed2d076065e30aed5e8402057b710d78ad0e1e800`.
Change only the plan's named properties. Within each case, both processes read
identical configuration bytes. Initial text is represented in the committed
record by a hash, retaining its source attribution without copying it here.

Compile all Java sources directly with `javac 22.0.2`, `--release 8`, UTF-8,
`-proc:none`, and an empty external classpath. Compilation succeeded with
warnings retained in the local log. This follows the POM's Java 8 target but
does not reproduce Maven packaging or identify the packaged JAR. No external
library was needed for this direct source build.

Each run uses a fresh JVM, explicit UTF-8 encoding, UTC and English/US locale,
and the same compiled class directory. Inherited Java option/classpath variables
are suppressed; former values are not recorded. Writes go to a fresh run
directory with the fixed relative filename `./output/generated.txt`. The
reference checkout remained unchanged. Third-party source, compiled classes,
configurations, logs and generated text remain local; only identities, settings
and original observations are committed.

## All planned outcomes

All processes exited zero and met their requested row count without timeout.
The hashes below are 12-character prefixes for reading; use the complete
SHA-256 values in JSON for verification.

| Case | Rows including initialization | Repeats | Bytes per output | Full bytes equal between repeats | Full hash prefix |
| --- | ---: | ---: | ---: | --- | --- |
| short-19 | 60 | 2 | 4,089 | yes | `f81ab51d839d` |
| short-20 | 60 | 2 | 3,998 | yes | `b4fad9a461fc` |
| release-19 | 1,200 | 2 | 62,795 | yes | `a9f8237c9d74` |

Both short projections differ between seeds 19 and 20, while repeating a seed
produces identical full and projected bytes. This is the planned seed-change
diagnostic for that pair, not a claim about all possible seeds.

The full release-19 output SHA-256 is
`a9f8237c9d7428ed148718d5aef2563a220b0df3fbc137eea197751af8ce2956`
in both runs, exactly matching the verified supplied file. Its text projection
has SHA-256
`b6cbeff13faecb33f01c2a50f3c7b22258adc9217373dd5c431a30fb3e491c5a`.
The projection removes only blank and comment lines as specified in the plan,
preserves characters/order within retained lines, and normalizes line endings
to LF with a final LF. It does not create manuscript locus or glyph units.

One row in every output is initialization from the supplied line attributed
by `Constants` to `f103v.P.9`, with the source's initial-line trimming procedure.
Thus 60 and 1,200 are total output rows, including one initialization row;
they contain 59 and 1,199 newly generated rows respectively. The identical
first-row fingerprint across cases is input reuse, not a successful prediction
of manuscript text. No initial text, dictionary information, or previously
inspected manuscript material is relabeled as unseen evaluation material.

## Reproduction

Obtain an unchanged local checkout of the pinned author release and Java
22.0.2. The harness downloads nothing and rejects other source/runtime versions.
Inspect the external code before executing it, as with the recorded run.
Use new work and output paths:

```sh
python3 scripts/replay_self_citation.py \
  --reference PATH_TO_PINNED_RELEASE \
  --java-home PATH_TO_JAVA_22_0_2 \
  --work PATH_TO_NEW_LOCAL_RUN_DIRECTORY \
  --output PATH_TO_NEW_RUN_RECORD.json
PYTHONPATH=tests python3 -m unittest test_self_citation_replay -v
```

The harness retains build/process stdout and stderr, every effective property
file, compiled classes, and all six outputs beneath the work directory. The
JSON records fingerprints instead of their text. Eight helper tests use
synthetic property/text fixtures, including duplicate/unsupported declarations,
exact preservation of unmodified properties and row characters, invalid UTF-8,
preservation of failed/timed-out process logs, compiler/VM environment filtering,
and rejection of near-matching version strings. A deliberately injected synthetic
compiler option was excluded in an actual launcher check. The six actual Java executions
are the integration check; ordinary unit tests do not download or invoke Java.

## Interpretation and next test

The result closes the specific source-build/supplied-output repeatability gap
on this runtime, while the packaged binary/archive provenance audit remains
separate. Equality to the release artifact does not establish that it is the
paper's analyzed sample. No cross-runtime portability, parameter identifiability,
ablation result, statistical goodness of fit, glyph reading, language, cipher,
or translation is established.

A mechanism comparison must still define compatible units, manuscript cohort,
prior exposure, initialization handling, a frozen seed/settings list, controls,
and rejection criteria before fitting. Generated rows and algorithmic glyph
segments cannot be silently equated with IVTFF P0 loci or actual glyphs. Preserve
the [comparison requirements](COPYING_MECHANISM.md) and
[decipherment evaluation protocol](../DECIPHERMENT_PROTOCOL.md) when designing
that prospective test.
