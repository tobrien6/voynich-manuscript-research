# Paragraph context changes the finite generator prefix profile

Suppressing the paragraph-initial argument passed to the mutation component
raises the model's paragraph-initial first-y contrast in all 31 fixed seeds,
under both copying-chooser conditions. The source-informed directional
prediction passes its two strictly positive equal-seed mean criteria. This
establishes dependence of this finite program profile on the specified argument;
it does not identify the corresponding manuscript process or one causal mediator.

The [plan](SELF_CITATION_CONTEXT_PLAN.md) and
[protocol](self-citation-context-protocol.json) were published at
`f0ad3f1919a9e49eb7181fbfbed9a02c2d1aeac1`. The runner and seven synthetic tests
were published at `3597e29100e53d87d515837920722bef026d294d` before changed-generator
execution. The [complete result](self-citation-context-ablation.json) retains
every setting/seed, all native denominators, exact fractions, differences,
interactions, failures and artifact fingerprints. Its SHA-256 is
`8132eb8cc0e31155766153fb8199e03dfcdaffc7dc80d9de6f9ebf40ae3407ee`.

## The intervention and its contexts

The four settings preserve the native paragraph-initial argument, replace it
with false only in `chooseSourceGroup`, replace it only in `morphGroup`, or
replace it at both call sites. Every other source byte is unchanged except the
accepted row-observer insertion. Paragraph bookkeeping, the stored list of
paragraph-initial rows, paragraph-final and line-initial arguments, initial
line and release settings remain as specified. This changes all uses of the
argument inside the selected component, including mutation/gallows behavior;
it is not an ablation of a single glyph rule or of paragraph layout itself.

The observer records the native outer generation-call flag. A row marked
paragraph-initial can therefore pass false to a suppressed component. These
are program states rather than independently checked manuscript annotations.

| Setting | Non-initial measured rows per seed | Initial measured rows per seed |
| --- | ---: | ---: |
| original | 1,342–1,356 | 327–341 |
| chooser_off | 1,341–1,356 | 327–342 |
| morpher_off | 1,338–1,363 | 320–345 |
| both_off | 1,337–1,365 | 318–346 |

Each setting/seed retains 1,683 measured rows and excludes its one reused
initialization row. No newly generated row has fewer than two groups.
All 32 profile strata per seed are defined. Context counts and group-occurrence
denominators differ between settings and remain separate in the result.

## Complete finite-grid profiles

For literal case-sensitive q/y, subtract the mean prefix indicator of other
groups from the first or last group's indicator, then average rows equally.
Reuse the accepted exact rational implementation; do not change weighting to
group occurrences. The table gives equal-seed means rounded to six decimals;
all 992 setting/seed profiles and their denominators are available in JSON.

| Native context | Slot/prefix | Original | Chooser off | Morpher off | Both off |
| --- | --- | ---: | ---: | ---: | ---: |
| Non-initial | first q | +0.007817 | +0.009256 | +0.011301 | +0.010328 |
| Non-initial | first y | +0.018574 | +0.018905 | +0.024446 | +0.025713 |
| Non-initial | last q | -0.018999 | -0.022694 | -0.026794 | -0.027723 |
| Non-initial | last y | -0.019027 | -0.017952 | -0.023526 | -0.020583 |
| Initial | first q | -0.017572 | -0.027434 | +0.009101 | +0.008284 |
| Initial | first y | -0.056570 | -0.072302 | +0.022874 | +0.021512 |
| Initial | last q | -0.006435 | -0.009374 | -0.018826 | -0.028602 |
| Initial | last y | -0.003748 | -0.008417 | -0.019949 | -0.017023 |

## Differences, contrary outcomes and interaction

The two predicted differences concern initial first-y. Suppressing the morpher
flag with the chooser intact increases the contrast by +0.079444 on average,
with differences +0.038347 to +0.117760 and 31 positive/zero negative seeds.
With the chooser flag already suppressed, the increase is +0.093814 on average,
with differences +0.048941 to +0.135595 and 31 positive/zero negative seeds.
These are finite-bank descriptive differences, with no probability coverage
or p-value assigned to their min/max ranges.

The complete difference table includes effects with mixed or contrary signs.
The three sign counts are negative/zero/positive across all 31 seeds. Interaction
is `both_off - chooser_off - morpher_off + original`; its full seed values and
sign counts are retained in JSON alongside every original-relative difference.

| Native context | Slot/prefix | Chooser−original mean; signs | Morpher−original mean; signs | Both−original mean; signs | Interaction mean |
| --- | --- | --- | --- | --- | ---: |
| Non-initial | first q | +0.001439; 13/0/18 | +0.003484; 13/0/18 | +0.002511; 12/0/19 | -0.002412 |
| Non-initial | first y | +0.000331; 14/0/17 | +0.005872; 12/0/19 | +0.007139; 10/0/21 | +0.000936 |
| Non-initial | last q | -0.003695; 20/0/11 | -0.007795; 25/0/6 | -0.008724; 26/0/5 | +0.002766 |
| Non-initial | last y | +0.001075; 12/0/19 | -0.004499; 22/0/9 | -0.001556; 17/0/14 | +0.001867 |
| Initial | first q | -0.009862; 28/0/3 | +0.026673; 2/0/29 | +0.025856; 0/0/31 | +0.009044 |
| Initial | first y | -0.015732; 25/0/6 | +0.079444; 0/0/31 | +0.078083; 0/0/31 | +0.014370 |
| Initial | last q | -0.002939; 17/0/14 | -0.012391; 25/0/6 | -0.022167; 28/0/3 | -0.006837 |
| Initial | last y | -0.004669; 19/0/12 | -0.016202; 25/0/6 | -0.013275; 23/0/8 | +0.007596 |

For example, suppressing only the chooser decreases initial first-y on average,
and both suppressed settings change non-initial and final-slot profiles too.
The generator's later history propagates changes beyond the originally flagged
calls. A successful directional check therefore does not mean every profile
improves, or that the intervention is confined to the first group.

## Execution and independent verification

All 248 planned fresh JVMs completed: four settings, seeds 1–31 and two repeats.
Every repeat pair has identical complete output bytes, ordered unique events
and canonical row ledgers. All 62 fresh original-setting runs also reproduce
the accepted [Java17 profile](SELF_CITATION_PREFIX_PROFILE.md)'s per-seed output
hashes, configuration hashes, ledger hashes, short-row exclusions and exact
profiles. This experiment's repeated originals are software reproduction,
not independent manuscript evidence.

Zulu Java/javac 17.0.16, Java 8 target, disabled annotation processing, empty
external classpath, fixed JVM flags and the four-key minimal environment match
the parent experiment. The producer pins the actual java/javac binaries in
addition to launcher hashes and complete version strings. Five builds retain
47 classes each. Unobserved/original class inventories exactly match the accepted
parent builds; only the main generator class differs in each observed setting.
All 39 author-source/config/reference inputs remain unchanged. Third-party
source, class files, configurations, logs, generated text and full ledgers stay
local; the committed result contains only metadata and original measurements.

A separate parser/arithmetic check reconstructed all 417,632 native ledger rows
across both repeats, including 248 initialized rows. It verified every byte
interval, row hash, group count, trace event, configuration/log/output fingerprint,
all 992 exact profiles, all 744 original-relative seed differences and 248
interaction values, plus both prediction differences and summaries. Source
pins, 175 copied Java files, 235 class files and five build-log fingerprints
were checked separately. All 642 tests pass on the recorded branch: 633 standard
tests, including seven new focused tests, plus nine script tests.

## Reproduction and interpretation limits

Use the producer/helper bytes at commit `3597e29`, the exact parent report and
protocols, the pinned 39 author files, and the two corrected observer helpers
at PR #100 head `d86cccdc0afd19ebeea8b4de3f3068294c87d05f`. Inspect them before
execution. The producer verifies all identities and downloads nothing. Its
actual binary hashes identify this runtime installation; another build/platform
requires new provenance rather than an identical-receipt claim. Supply fresh
local work/report paths outside protected input trees.

```sh
python3 scripts/ablate_self_citation_context.py \
  --reference PATH_TO_PINNED_AUTHOR_FILES \
  --observer-dir PATH_TO_PINNED_OBSERVER_HELPERS \
  --java-home PATH_TO_PINNED_JAVA_HOME \
  --work PATH_TO_NEW_LOCAL_WORK_DIRECTORY \
  --new-report PATH_TO_NEW_LOCAL_REPORT.json
PYTHONPATH=tests python3 -m unittest test_self_citation_context
```

A build/process/trace/repeat failure blocks the complete factorial grid and
prediction. An empty context keeps its full seed list, sets the relevant summary
and dependent criterion to null, and never substitutes or drops a seed.
No execution failure or undefined stratum occurred here.

Changed branching consumes random draws differently and changes remembered
text, output rows and contextual mixtures. Equal seed numbers do not establish
common random numbers, matched rows or equal conditional populations. This
is an intervention on full program settings rather than proof of an isolated
scribal/glyph cause. The author-supplied manuscript initial line and the exposed
parent cohort's derived row count remain dependencies.

No manuscript target or new fit score is computed, no setting is selected for
adoption, and no untouched split, paper-sample replication, general copying
validation, glyph identity, language or translation is established. The result
motivates separately specified controls for the paragraph-specific rules when
evaluating explicit mechanisms with independently checked units. Preserve the
[comparison requirements](COPYING_MECHANISM.md) and
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
