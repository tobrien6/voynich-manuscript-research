# Paragraph-context call-site ablation plan

Commit this plan and the [protocol](self-citation-context-protocol.json) before
executing any changed generator or measuring its output. The accepted prefix
profile, full manuscript cohort, author code and original seed outputs are
already exposed. This is development work, not an untouched mechanism test.

## Question and source-informed prediction

How much does the fixed generator's q/y boundary profile depend on passing its
paragraph-initial flag to the copying chooser and mutation component?
The [pinned entry point](https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/9e98c9122a0f490905e8b66f3911fc7ce095fd26/source/src/main/java/de/voynich/text/SelfCitationTextGenerator.java)
passes that flag separately to `chooseSourceGroup` and `morphGroup`.
[SlimGroupMorpher](https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/9e98c9122a0f490905e8b66f3911fc7ce095fd26/source/src/main/java/de/voynich/text/morph/SlimGroupMorpher.java)
forces its first mutation-method draw to zero at paragraph-initial row starts,
and its inherited gallows handling also uses paragraph context. The
[chooser](https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/9e98c9122a0f490905e8b66f3911fc7ce095fd26/source/src/main/java/de/voynich/text/sourcechooser/PageSourceGroupChooser.java)
uses the flag to select remembered paragraph-initial material, subject to its
suggestion override. These are program rules, not manuscript glyph facts.

The directional prediction is that suppressing the mutation component's flag
increases the paragraph-initial first-y contrast in both chooser conditions.
Its finite-grid criterion is two strictly positive equal-seed mean differences:
`morpher_off - original` and `both_off - chooser_off`. Report failure or undefined
status explicitly. No direction is predicted for the copying-chooser ablation,
other profiles or the interaction. All of them are retained.

## Four precisely specified settings

| Setting | Chooser receives | Morpher receives |
| --- | --- | --- |
| original | native paragraph-initial flag | native paragraph-initial flag |
| chooser_off | false | native paragraph-initial flag |
| morpher_off | native paragraph-initial flag | false |
| both_off | false | false |

Replace the single argument at each selected call site in the entry point;
reject missing or repeated anchors. Preserve every other original source byte,
plus the known output-preserving row observer from corrected PR #100.
Paragraph/page bookkeeping, the list of paragraph-initial rows, final-row flags,
line-initial flags, settings, initial line, copying and mutation implementations
stay as specified in the release. The intervention removes the flag's use by
the selected component, not paragraph layout or all positional processing.
The observer records the native outer flag before the generation call; it does
not relabel rows according to the suppressed component argument.

## Fixed executions and provenance

- Author commit `9e98c9122a0f490905e8b66f3911fc7ce095fd26`, all 39 input pins,
  corrected PR #100 observer/helpers and the accepted #103 numerical report.
  Pin the shared profile/runner helpers and their imported dependencies.
- Use the same Zulu Java/javac 17.0.16 build, Java 8 compilation target, empty
  external classpath, disabled annotation processing, fixed JVM flags and
  four-key minimal environment as #103. Pin runtime outputs and executable
  fingerprints. Download nothing in the producer.
- Seeds 1 through 31, all four settings, two fresh observed JVMs per cell:
  248 planned processes. Each retains 1,684 output rows, including the one
  initialized row. This row count comes from the already exposed #103 cohort;
  no manuscript target is reselected or tested here.
- Compile the uninstrumented original and four observed settings. Require 47
  classes per build and only the main generator class to differ from the
  original. Verify every copied source against its exact expected bytes.
- Require each repeat pair's complete output bytes, trace events and ledgers
  to agree. Each original cell must also reproduce the accepted #103 output
  hash, ledger hash, configuration hash and exact profile. Preserve full logs,
  outputs and ledgers locally; publish only fingerprints and original analysis.
- Retain failed builds/processes, timeouts, malformed/incomplete traces and
  repeat discrepancies without substituting seeds or selecting successful
  cases. A failure blocks the complete grid and directional criterion.

## Measurements and complete reporting

Reuse the accepted exact equal-row boundary-minus-other-groups q/y contrast.
Exclude only initialized rows and explicitly retain any new row with fewer than
two space-delimited groups as a short-row exclusion. Native paragraph contexts
remain those of each setting's own observer. Report their distinct counts and
all group-occurrence denominators; do not pair rows across settings.

For every seed retain all eight context/first-or-last/q-or-y profiles for every
setting. Compute three differences from original and the two-factor interaction
`both_off - chooser_off - morpher_off + original` for all eight profiles.
Summarize each finite list with its equal-seed mean, inclusive minimum/maximum
and negative/zero/positive counts. No seed probability distribution, confidence
coverage or p-value is assigned. An empty context remains undefined; retain
every seed and set that summary and any dependent criterion to null rather
than dropping undefined cells. Execution completeness and numerical definition
are separate.

## Interpretation limits

Changed branching alters random-call consumption, subsequent remembered text,
row contents and paragraph counts. Matching seed numbers do not establish
common random numbers or matched row treatments. The interaction describes
the four full program settings, not an isolated biological or scribal effect.
Flag suppression affects all downstream uses of that argument inside a
component, including gallows/mutation rules; it is not a single glyph ablation.

This test can establish dependence of the finite generated profile on specified
rules. It cannot attribute the manuscript pattern, validate copying, isolate
one causal mediator, identify glyphs or a language, reject every self-citation
model, replicate the paper's sample, create a held-out split or translate text.
The manuscript-derived initialization and row-count choice remain dependencies.
No new manuscript fit score is computed and no setting is selected for adoption.
