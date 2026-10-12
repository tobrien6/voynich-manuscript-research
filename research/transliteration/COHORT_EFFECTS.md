# Position effects on a fixed transcription cohort

## Question and sources

The [accepted position analysis](POSITION_EFFECTS.md) compares eight
transcription/uncertainty variants whose eligibility rules can select different
loci. How much of their contrast difference remains when the locus sample is
fixed across all variants?

Use the exact ZL3b and IT2a editions in the
[pinned source catalog](../../data/transliterations.json), with their publisher
credits, retrieval URLs, source hashes and CC0 text-data reuse statement.
These sources cover 3,884 shared present P0 locus keys, with the same selection
digest as the accepted token and position reports. GC and RF exports do not
enter this analysis. Individual folio/locus keys excluded under each variant
are recorded in [position_cohorts.json](position_cohorts.json); the keys are
source identifiers, not newly verified image alignments.

The [analysis choices](COHORT_PLAN.md) were committed at `dda47bc` before
computing this report. The sources and prior results were already exposed.
This is an exploratory sensitivity analysis, not a held-out decipherment test.

## Method

Reuse the accepted tokenizer and feature definitions: literal `q`/`y`
representation prefixes and EVA notation-unit lengths, preserving native case
and ligature notation. Run split/join uncertain commas and exclude/first-choice
alternatives for each source. Unreadable or empty readings remain excluded
original slots. These are neither phonetic units nor manuscript glyph counts.

For each boundary separately, retain only keys eligible under **all eight**
variants. The original first/last slot must survive, with at least one other
retained token. An excluded boundary cannot be replaced by the next token.
First and last cohorts need not contain the same loci.

For feature `x`, each eligible locus contributes the boundary value minus the
mean of its other retained values. Give every locus equal weight. For every
variant, report this mean on its own eligible sample and on the fixed cohort,
plus the fixed-minus-own shift. On the fixed cohort, subtract the primary
ZL3b split/exclude contrast **at each matching key** before reporting its mean
signed difference, mean absolute difference and differing-locus count.
Differences at or below `1e-12` count as numerical ties for that count only.

The report includes source hashes, cohort digests, excluded keys and native
locator counts. It generates no new significance tests. The editions and
policies are dependent readings of the same manuscript material.

## Observations

The common first-slot cohort contains **3,759 loci** (96.78% of the shared P0
selection), and the last-slot cohort contains **3,726 loci** (95.93%). The
primary variant loses 19 first-slot and 14 last-slot loci when restricted to
these cohorts. Eligibility counts for all variants remain visible in the report.

Every one of the original six feature/boundary effect directions persists
across all variants on the fixed cohorts. Selected equal-locus-weight contrasts:

| Source | Spaces | Alternatives | First-slot y-prefix contrast | First-slot notation-length contrast | Last-slot notation-length contrast |
| --- | --- | --- | ---: | ---: | ---: |
| ZL3b | split | exclude | +0.10665184 | +0.45217021 | -0.31822874 |
| ZL3b | split | first | +0.10660696 | +0.44905601 | -0.32339892 |
| ZL3b | join | exclude | +0.10661957 | +0.48310294 | -0.16074887 |
| ZL3b | join | first | +0.10660207 | +0.47730477 | -0.16801775 |
| IT2a | either | either | +0.10567025 | +0.44490566 | -0.45551580 |

IT's four treatments coincide because its selected text has no uncertain
commas or bracketed alternatives. The complete JSON reports all 48 contrasts.

Joining uncertain ZL spaces with alternatives excluded changes the last-slot
notation-length contrast by **+0.15747987** on identical locus keys. The
fixed-minus-own shifts for the split and join variants are +0.00563708 and
+0.00091296 respectively. Thus the substantial spacing sensitivity survives
controlling which loci are eligible; it cannot be explained solely by their
different eligible-locus samples.

Similar aggregate means can conceal individual disagreement. On the common
first-slot cohort, IT's notation-length contrast differs from the primary by
only -0.00726455 on average, while its mean absolute per-locus difference is
0.46201253 and 1,623 of 3,759 loci differ. This is disagreement between
representation-level contrasts, not an error rate against manuscript truth.

## Reproduce and validate

Python 3.10 or later, standard library only; recorded run: Python 3.14.3.

```sh
python3 scripts/position_cohorts.py --output research/transliteration/position_cohorts.json
python3 scripts/position_cohorts.py --check research/transliteration/position_cohorts.json
python3 -m unittest discover -s tests -v
```

Source hashes are verified before analysis. Check mode compares the complete
parsed report. Synthetic tests cover eligibility changes, separate boundary
cohorts, excluded boundaries, all uncertainty policies, empty intersections,
equal locus weighting, cancelling signed differences, duplicate keys and
isolation of the declared source pair. All 48 own-sample contrasts and all 16
eligibility counts also match the accepted position report exactly at its
reported precision.

## Limits and next test

Fixing keys does not fix segmentation, retained tokens, notation or source
locator conventions. A shared key does not establish equivalent physical-line
boundaries. The common cohort conditions on eligibility across all variants
and omits some uncertain material; its result cannot automatically generalize
to excluded loci. First/last cohorts also cannot be treated as paired with one
another. This descriptive comparison is not a causal attribution of source
differences or independent evidence of a language, cipher or translation.

Next, inspect the loci where paired contrasts disagree most and verify their
boundaries against source images. Extend the accepted
[paragraph-start and same-line-fragment stratification](PREFIX_STRATA.md)
with fixed eligibility within jointly defined source strata. A candidate mechanism
should predict robust structure under declared uncertainty choices, with its
own evaluation split and prior-exposure record.
