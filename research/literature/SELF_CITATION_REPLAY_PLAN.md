# Source-build repeatability plan

This tests the software reproducibility gap identified in
[the self-citation source audit](COPYING_MECHANISM.md). It is not a registered
manuscript hypothesis, a decoding/translation claim, a fit to the manuscript,
nor an independently timestamped preregistration. Commit this plan before
executing the generator and retain every planned run, including failures.

## Fixed source and build

- Fetch tag `v1.0.1` of `TorstenTimm/SelfCitationTextgenerator`; require commit
  `9e98c9122a0f490905e8b66f3911fc7ce095fd26` and unchanged committed source files.
- Build the Java sources directly with the available Homebrew OpenJDK 22.0.2
  compiler, UTF-8, `--release 8`, annotation processing disabled, and an empty
  external classpath. The POM specifies Java 8; this is a direct source build,
  not a reproduction of Maven packaging or the shipped JAR. Record compiler,
  runtime, platform, all Java source hashes, class hashes, and build command.
- Inspect the entry point, configuration resolution, file writes, and imports
  before execution. Do not run auxiliary entry points. Keep builds, configurations,
  logs and generated text in new temporary directories; third-party code and
  text are not committed to the research repository.

## Cases and input preservation

Use the release's `executable/conf.properties`, already pinned at SHA-256
`00944114753a7019e920199ed2d076065e30aed5e8402057b710d78ad0e1e800`.
Preserve every property except the explicitly listed overrides. Use two fresh
JVM processes for each case, with identical configuration bytes within a case:

| Case | Lines requested | Pseudo-random seed | Repeats |
| --- | ---: | ---: | ---: |
| short-19 | 60 | 19 | 2 |
| short-20 | 60 | 20 | 2 |
| release-19 | 1,200 | 19 | 2 |

For all cases use `save.path=./output/` and `save.filename=generated.txt`, to
keep writes inside the run directory and remove date-dependent filenames.
Keep the shipped `save.properties_in_seperate_file=false` and
`save.gephi.nodes=false`. Short cases additionally change `text.lines_to_create`
and the seed as specified; the full case changes only the two save properties.
The release initialization includes text attributed to `f103v.P.9`. It is an
input dependency and exposure, not generated prediction or held-out material.

Use explicit UTF-8 file encoding, UTC, English/US locale and a fixed classpath.
Remove inherited Java option/classpath injection variables for these subprocesses;
do not log their former values. Record the effective property file hash and
all property values except the initialization text, represented by its hash.
Record process exit codes and stdout/stderr fingerprints. Each run has a
120-second limit; timeout or generation failure is retained and prevents a
successful repeatability claim.

## Comparisons fixed before execution

1. Compare complete generated-file bytes between the two repeats in every case.
2. Also compare a declared text projection: decode UTF-8, keep nonblank lines
   that do not begin with `#` after leading whitespace, preserve their characters
   and order, and join with LF plus a final LF. Report kept row counts, full and
   projected SHA-256 values, and initialization-row fingerprints. This projection
   separates comment headers/blank lines from generated text; it does not infer
   glyphs, tokens, physical manuscript lines, or paragraph boundaries.
3. Compare the two short cases' projections as a seed-change diagnostic. Do not
   select seeds or settings from the outcome.
4. Verify the supplied `executable/generate/vms_generated.txt` against its
   recorded 62,795 bytes and SHA-256
   `a9f8237c9d7428ed148718d5aef2563a220b0df3fbc137eea197751af8ce2956`.
   Compare full and projected bytes with both release-19 runs. A mismatch must
   be reported; it does not by itself identify a Java/runtime defect or prove
   which source/configuration produced the paper's analyzed sample.

Software repeatability supports later simulations with recorded inputs. It
does not test the mechanism against manuscript observations or replicate the
paper's statistics. No cross-runtime test, model selection, generator ablation,
goodness-of-fit score, language identification, or translation is claimed.
