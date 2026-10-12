# Paired symbol entropy under fixed unit and boundary policies

On one fixed cohort of **2,485 clear regular P0 loci**, empirical conditional
successor entropy changes with both notation segmentation and scored boundaries.
For ZL3b split, the within-token estimates are 1.988404 bits per ASCII unit,
2.113664 per listed bench unit and 2.284549 per listed bench/minim unit.
Adding inter-token space units within each locus raises the first two estimates
but lowers the third. There is no uniform space effect across these policies.

These are descriptive estimates on already exposed paired transcriptions.
Changing an atomic unit also changes one preceding unit of context, so the
values do not select a correct glyph map or rank languages or mechanisms.

## Method, sources and chronology

The [plan note](PAIRED_ENTROPY_PLAN.md) and [machine plan](paired-entropy-plan.json)
were committed at `92aae6c` before this corpus execution. The implementation and
ten synthetic tests were committed at `682ba83` before the first report.
The study reuses the pinned [ZL3b/IT2a sources](../../data/transliterations.json),
the `plain-eva-v1` [adapter](../transliteration/TOKEN_ADAPTER.md), and exactly
the three accepted [unit policies](../baselines/eva-unit-protocol.json).
Source credits and reuse terms remain in the [source decision](../transliteration/DECISION.md).

The policies preserve native case and apply the existing literal longest-match
segmenter inside each token. Rejoining emitted pieces exactly recovers that
token. They are analyst-declared notation units, not adjudicated glyphs,
phonemes, or a complete conversion into another transcription alphabet.

Start from present P0 keys shared by both editions. Retain a key only when all
four source/spacing treatments are eligible, have at least one token, use a
regular `@`/`+`/`*` locator and have no drawing interruption. Exclude a whole
locus on any failure; no boundary or unit policy gets a different cohort.
The paired [complete report](paired_symbol_entropy.json) retains all keys,
overlapping exclusion reasons and original input/implementation fingerprints.

## Coverage

There are 3,884 shared present P0 keys: 2,485 retained and 1,399 excluded.
ZL's source-only P0 key `f106r.29` remains outside the intersection. The retained
cohort spans **195 transcription page identifiers**, which are not independent
physical leaves or verified image regions. Source Currier metadata is retained
as annotation, without inferring languages: 782 A, 1,684 B and 19 unset loci
in each treatment.

| Source/spacing | Native tokens | Retained loci |
| --- | ---: | ---: |
| ZL3b split | 21,343 | 2,485 |
| ZL3b join | 19,799 | 2,485 |
| IT2a split | 21,006 | 2,485 |
| IT2a join | 21,006 | 2,485 |

Eligibility depends on both source editions; this is not an unbiased source
accuracy sample. Exclusion counts overlap across conditions and variants and
must not be summed as independent missing loci. Compared with other project
cohorts, the explicit drawing exclusion and one-token minimum are different
selection rules; their denominators must remain separate.

## Edge populations and estimates

`within_token` scores adjacent emitted units only inside each original token.
`within_locus_with_space` inserts one reserved `<SPACE>` unit between tokens
inside a locus, then scores adjacent units in that locus. Neither connects
different loci, pads an endpoint, or wraps the final unit around to the start.
Grouping never crosses token boundaries under the declared spacing treatment.

Pool successor opportunities equally. This is **edge weighting**, distinct
from the equal-locus weighting in the position experiments. A singleton segment
contributes to the full-unit histogram and segment denominator but has no edge.
The report includes zero-edge segment counts and would use null, not zero,
for an entirely empty conditional-edge population.

For pair counts `n[i,j]`, the conditioning denominator is the outgoing count
`n_out[i]`, with `E` total scored edges:

```text
H(next | predecessor) = -sum n[i,j]/E * log2(n[i,j]/n_out[i])
                     = H(pairs; E) - H(predecessors; E)
```

Full-unit, pair and predecessor entropies, all frequency tables and both
boundary populations are retained in the report. These are unsmoothed empirical
estimates without bias correction or uncertainty intervals. They are not
general entropy-rate estimates.

Conditional successor entropy in bits per **declared next unit**:

| Source/spacing | Unit policy | Within token | Within locus with space |
| --- | --- | ---: | ---: |
| ZL3b split | `ascii_letters` | 1.988404 | 2.038662 |
| ZL3b split | `bench_sequences` | 2.113664 | 2.150500 |
| ZL3b split | `bench_and_minim_sequences` | 2.284549 | 2.262744 |
| ZL3b join | `ascii_letters` | 2.010786 | 2.052746 |
| ZL3b join | `bench_sequences` | 2.135777 | 2.167199 |
| ZL3b join | `bench_and_minim_sequences` | 2.304731 | 2.281961 |
| IT2a split | `ascii_letters` | 2.002357 | 2.041316 |
| IT2a split | `bench_sequences` | 2.126043 | 2.153245 |
| IT2a split | `bench_and_minim_sequences` | 2.296636 | 2.265685 |
| IT2a join | `ascii_letters` | 2.002357 | 2.041316 |
| IT2a join | `bench_sequences` | 2.126043 | 2.153245 |
| IT2a join | `bench_and_minim_sequences` | 2.296636 | 2.265685 |

IT's split/join token arrays, counts and estimates are exactly identical here;
they are dependent sensitivity treatments, not separate replications. ZL/IT
also represent the same manuscript through related source conventions.

## Effect of using a different marginal population

The report separately retains `H(pairs; E) - H(full units; N)` and its
difference from matching-marginal conditional entropy. On ZL split, the
within-token differences are **-0.260303**, **-0.267814** and **-0.356186** bits
under the three policies. Within-locus-with-space differences are **-0.023259**,
**-0.024506** and **-0.032069** bits. Negative differences mean that subtracting
the full-unit marginal gives a lower estimate in these populations.

Each isolated segment has an endpoint without a successor: the terminal count
is 21,343 for ZL split within-token and 2,485 within-locus-with-space. Thus this
is a repeated-segment population distinction, rather than merely the single
last character of a globally concatenated document. Both quantities remain
named separately. This observation does not establish an effect in a published
paper's different corpus, package pipeline or boundary rules.

## Reproduce and assess the limits

Python's standard library is sufficient; no downloads or input rewriting occur:

```sh
python3 scripts/paired_symbol_entropy.py --check research/representation/paired_symbol_entropy.json
python3 -m unittest tests.test_paired_symbol_entropy -v
```

Check mode verifies the plan's source/implementation pins before loading data,
checks exact source bytes, recreates the common cohort and all 24 treatments,
and compares the complete report. Changed pins require review and versioning.
Output guards preserve inputs even through symlink/hardlink aliases.

Ten synthetic tests cover manual branching and pooled weighting, singleton/null
cases, both boundary policies, reversible grouping/case, cohort/exclusion
accounting, duplicate/missing identities, changed pins and safe output behavior.
An independent successor-distribution calculation checks all 196 pairs of
binary segments of lengths one through three. All 24 real frequency tables
were independently recalculated, including count/endpoint identities, source
pairing, and IT split/join equality; the full first report replays exactly.

The full paired texts and previous statistics were already exposed. This
creates no untouched evaluation set, glyph adjudication or source correction.
Clear-locus selection, incomplete glyph units, transcription dependence,
boundary rules and pooling limit interpretation. No language comparator,
shuffle control, fitted model, p-value or hypothesis rejection was specified;
none is inferred from these values. No decipherment or translation is produced.

Before testing a mechanism, freeze its comparable atomic units, context,
boundaries and control populations. Match these choices in reference language
or synthetic-encoding data rather than comparing unmatched numerical entropy
columns. A historical paper replication remains a separate source-recovery
and execution task under the [decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
