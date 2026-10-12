# Self-citation generator: source audit and comparison requirements

Question: what would a reproducible comparison of the Timm–Schinner copying
mechanism require, and which existing project measurements could test it?

The published implementation supplies a concrete competing mechanism for
future decoding constraints. It includes positional and frequency rules as
well as copying and mutation. Rejection of a token shuffle therefore cannot
by itself identify this mechanism. No generator was executed, model fitted,
manuscript experiment run, published result replicated, or reading proposed
in this contribution.

## Publication and implementation identities

**L004:** Torsten Timm and Andreas Schinner, [*A possible generating algorithm
of the Voynich manuscript*](https://doi.org/10.1080/01611194.2019.1596999),
*Cryptologia* 44(1), 1–19. The publisher records online publication on
2019-05-25 and a 2020 issue. Its abstract reports a self-citation mechanism,
token-similarity analysis and reproduction of selected statistical properties,
including both Zipf laws. These are the authors' claims, not results reproduced
here. The full article was unavailable through the inspected publisher endpoint;
this note does not reconstruct its complete methods from the abstract.

The paper links [the author's additional materials](https://github.com/TorstenTimm/SelfCitationTextgenerator).
[Zenodo record 2531632](https://zenodo.org/records/2531632) identifies version
`v1.0.1`, published 2019-01-04, and links that GitHub tag. The tag resolves to
commit `9e98c9122a0f490905e8b66f3911fc7ce095fd26`. The
[audit record](copying-mechanism.json) fingerprints selected files retrieved
from that **exact commit**, with method/line locators for each finding. The
Zenodo ZIP was not downloaded; tag resolution does not verify its bytes or
prove which binary/configuration produced the paper's analyzed sample.

For comparison, GitHub `master` resolved to
`a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7`. Among the 11 files fetched at both
commits, README, the resource configuration and `Config.java` differ. A moving
branch, release tag, packaged JAR and paper output are distinct identities.
Only citations, fingerprints, selected property facts and original analysis
are committed here; third-party source, binaries and generated text stay local.

## Direct observations in the pinned source

| Component | Observed behavior | Consequence for a comparison |
| --- | --- | --- |
| `SelfCitationTextGenerator.initStatistics()` | Imports a supplied initial line into its remembered groups and output; `Constants` attributes the shipped line to `f103v.P.9`. | A manuscript-derived starting line is an input and exposure, not a prediction. Separate initialization from newly generated material. |
| `PageSourceGroupChooser.chooseSourceGroup()` / `chooseFromPage()` | Chooses from generated lines, with same-position selection, separate paragraph-initial context and suggestion branches. | The shipped process is more specific than an unspecified nearest-neighbor copy rule. |
| `SlimGroupMorpher.morphGroup()` | Uses add/remove, combine/split and replacement branches; paragraph/line flags change branch choice. | Preserve the full rules and position flags. Mutation changes token counts and lengths. |
| `SelfCitationTextGenerator.generateText()` / `generateLine()` | Constructs pages and paragraphs, limits repeat patterns, and trims groups when the remaining line space is insufficient. | Layout and acceptance rules can affect measured order and endpoints. Generator rows are not automatically IVTFF P0 loci or manuscript lines. |
| `GlyphGroup.getTokenCount()` / `length()` / `parse()` | Separates algorithmic segments from Java string length; its segment table includes multi-letter forms such as `ch`, `sh`, `qo`, `ol` and `dy`. | Internal “tokens” are pieces of a generated group. They are not the project's space-delimited tokens or independently verified manuscript glyphs. |
| `VoynichCanFollow.isValid()` | Optional dictionary mode checks membership in a supplied Voynich vocabulary. | A dictionary-constrained variant must disclose that information. Vocabulary compatibility is partly imposed by this setting. The shipped setting is `curveline`, not dictionary mode. |

The source and executable configurations both set 1,200 lines, maximum line
length 55, minimum paragraph-final length 15, 29 lines per page, pseudo-random
seed 19, page selection, `curveline`, `slim` mutation and `top` suggestions.
Their files differ, but the selected generation properties in the audit agree.
The recorded 20/30/50 mutation values are **configuration parameters**; branch
inequalities, source state and failed/accepted attempts mean they should not
be relabeled as observed event proportions.

For example, at an ordinary position with a source group whose type is not
`COMBINE`, enumerating the 100 possible `rand(100)` values against the
inspected `<=` branches gives 21 add/remove, 30 combine/split and 49 replacement
selections. This is a conditional branch count, not an empirical mutation rate;
paragraph-initial flags, combined sources and unsuccessful attempts change it.

The release also contains `executable/generate/vms_generated.txt`: 62,795
bytes, SHA-256 `a9f8237c9d7428ed148718d5aef2563a220b0df3fbc137eea197751af8ce2956`.
It has 35 comment lines and 1,200 nonblank noncomment lines. Selected header
settings agree with the values above. This pins a supplied artifact; it is
neither a regenerated output nor proof of identity with the paper's sample.

## Reproduction gaps found by source inspection

The later [static packaged-artifact check](GENERATOR_ARTIFACT_IDENTITY.md)
pins the JAR and embedded configuration and compares a compiler-only source
build. It retains unmatched classes and disassembly differences without
inferring changed generator behavior. The source-only inspection above remains
distinct from this later artifact evidence and from runtime reproduction.

`PseudoRandomNumberGenerator.seed()` constructs `java.util.Random` from a
numeric seed. `Config` prefers an external configuration file when present,
otherwise using the resource loader. Preserve the complete effective file,
its location and digest rather than relying on “defaults.” Comments mention
an `auto` seed search, but the inspected `Config` assigns a parsed integer or
`Constants.RANDOM_SEED_DEFAULT` (19). No seed-search behavior was established
in this source path; do not treat that comment as an executed selection rule.

The serialized `Config.toString()` omits the same-position probability and
combined-group dismissal probability, and prints only the first initial line.
An output's property header alone therefore cannot reproduce every input.
Keep the original configuration as well as the saved header and output digest.

`ChooserHelper.chooseRandomly()` indexes an unsorted map key list, while
`StatisticHelper` uses hash maps. `Glyph.determineStartLigature()` also scans
map keys after a special `eee` case. Java's [Random contract](https://docs.oracle.com/javase/8/docs/api/java/util/Random.html)
specifies repeatability for the same seed and call sequence; its
[HashMap contract](https://docs.oracle.com/javase/8/docs/api/java/util/HashMap.html)
does not specify iteration order. **Inference:** a numeric seed alone does
not establish portability across runtimes or modified implementations. Pin
Java/build versions and compare repeated output bytes. No cross-runtime
difference was tested here, and this inspection is not a generator defect
claim or a complete software audit.

## A later experiment must freeze these choices

1. Pin source/build or binary, every effective property, starting lines,
   dependency/runtime versions, random algorithm and the complete seed list.
   Repeat a small run twice and retain byte comparisons before scaling up.
   Establish whether a source build reproduces the supplied artifact; a
   discrepancy requires a recorded approximate-reproduction label.
2. Define output parsing, initialization exclusion, row/page boundaries and
   measurement units. Preserve a row/token provenance ledger. The project's
   [ASCII-notation interior statistic](../transliteration/INTERIOR_ORDER.md)
   and [unit sensitivity](../baselines/EVA_UNIT_RESULTS.md) require
   an explicit bridge to generated group strings, not a name change.
3. Declare manuscript source/cohort, prior exposure and candidate scope before
   fitting. If manuscript inputs or dictionary rules inform the generator,
   report that dependence. Follow the [evaluation protocol](../DECIPHERMENT_PROTOCOL.md)
   for any prospective claim; this methods note creates no frozen candidate.
4. Specify measurements and rejection conditions before execution. Compare
   the same statistic and eligible units in manuscript and generated data,
   retaining uncertainty/representation treatments and every seed outcome.
   Compare simulated distributions with observations; a shuffle tail is not
   a goodness-of-fit score for a generator.
5. Use separately versioned ablations to distinguish copying, position rules,
   suggestions and layout. Specify each changed rule precisely and report its
   changed denominators. Matching one endpoint, Zipf curve, repetition count
   or interior association does not identify the generating process or meaning.

The existing [repetition baseline](../transliteration/BASELINES.md) counts
equal adjacent events within selected loci. It does not measure the graph of
similar types described by L004. Both event definitions and conditioning must
be matched before comparing them. A future copying experiment must also
retain negative results and competing language/encoding controls, as required
by the project's decipherment protocol.

## Validation and limits

Inspected 2026-10-12 (America/New_York). Publication/Zenodo metadata, commit/tag
resolution, selected configuration fields, method locations, file sizes and
SHA-256 fingerprints were checked against primary sources. The original
configuration values and supplied artifact header were cross-checked without
running the generator. Local links and JSON structure were verified.

This is a bounded static methods audit. It does not validate the authors'
interpretation, verify the archived ZIP/JAR, assert faithful paper replication,
or select a mechanism for the manuscript. A fresh run with fully recorded
inputs and a prospectively specified comparison remains the next test.
