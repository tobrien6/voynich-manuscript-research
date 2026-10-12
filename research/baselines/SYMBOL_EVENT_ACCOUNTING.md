# Where the grouped symbol predictor gain occurs

In the primary ZL3b split ASCII treatment, later emitted units contribute
**+0.13543425 bits per total target** to the fixed Q2/Q1 gain of +0.21010809.
Second units contribute +0.05582825, token termination +0.01880020 and initial
units +0.00004539. These are terms in the same score-sum identity. They locate
the reported gain without assigning its cause or selecting a language.

The initial-event contribution is small here and changes sign under some
representation policies. The related [constant-context control](INITIAL_CONTEXT_CONTROL.md)
establishes a constructed possibility; it does not explain the magnitude of
the manuscript's full gain. Larger later/second terms still combine context,
position/boundary opportunities, smoothing and transcription choices.

## Fixed reference, exposure and chronology

The [plan](SYMBOL_EVENT_ACCOUNTING_PLAN.md) and [input manifest](symbol-event-accounting-inputs.json)
were committed and published at
[`132ef93`](https://github.com/tobrien6/voynich-manuscript-research/commit/132ef93).
The standalone implementation and eleven synthetic tests were committed and
published at
[`ec7469a`](https://github.com/tobrien6/voynich-manuscript-research/commit/ec7469a483b162dc03d0d15acb735574afb87f56)
before the role-specific manuscript calculation. These chronological records
are declarations, not independent certification of execution history.

The complete reference is the reviewed
[PR #123 report](https://github.com/tobrien6/voynich-manuscript-research/blob/7a4b7ae3ccd1196e1389f16247c77e9505a626fe/research/baselines/grouped-symbol-prediction.json),
SHA-256 `9afa08f7073188be5930191110517bb3bd88a2ef61c681931489782aeff4dc3c`,
with producer SHA-256
`b02e32a636b4f4b42c2798e5ce6f15128410d3eb97c9e3b14206b6cc4f1a4458`.
It was exposed and unaccepted at planning. Its results, input corpora and the
constructed smoothing example were already inspected. This accounting
provides no untouched candidate evaluation or independently sampled manuscript
evidence. It changes no reference model, report, source or decision.

The exact reference JSON is supplied as a separate local numeric input. Its
producer is neither imported nor copied into this contribution. All twenty
original artifacts/helpers remain byte-pinned. The accepted reader and cohort
helpers regenerate the entire paired-entropy receipt and the same 2,485 clear
regular P0 loci. The accepted dependency helper reconstructs all transitive
components from the full canvas index, preserving complete leaves/canvases of
the same 91 groups and five hash folds. These are coarse source references;
physical text/glyph alignment and other content dependencies remain unresolved.

An independent unit scanner, flat context counters and rational probabilities
reconstruct all twelve ZL3b/IT2a × split/join × unit-policy treatments and all
sixty fitted-count hashes. Every original per-locus count, loss, group/fold and
unseen-context count, all summary weightings and the original criterion agree.
The maximum original locus-loss discrepancy is **5.684341886080802e-14 bits**,
within the predeclared absolute computational tolerance of 1e-10. That
tolerance is not a statistical threshold. Original reference summaries are
retained alongside the computed accounting.

## Events, classes and denominators

Each retained native token resets two BOS context labels. It emits the declared
case-sensitive longest-match units and one EOS target. Every event belongs
to exactly one class:

| Role | Definition |
| --- | --- |
| Initial unit | Emitted unit at token-unit index 0 |
| Second unit | Emitted unit at index 1, when present |
| Later unit | Emitted unit at index 2 or greater |
| Termination | The one EOS target, regardless of token length |

These indices reset within every token. They describe notation units and
source tokenization; image-verified glyphs, phonetic units and words are not
established. A one-unit token has initial and termination events only. BOS is
never a target and EOS is never a manuscript glyph. The reference includes
all 52 ASCII letters, the policy's patterns and EOS in its target alphabet,
with root pseudocount 1/2 and context strength 16. All priors remain unchanged.

For role r, sum Q1 loss minus Q2 loss to obtain D_r and count N_r events. Its
class mean is D_r/N_r, null for an empty class. Its pooled contribution is
**D_r/N**, using the original total target count N. Contributions sum to the
original pooled gain; the four class means do not have that denominator.

For group g, its role contribution uses **D[g,r]/N_g**, where N_g includes all
of that group's targets. Average those terms over the same 91 groups to get
the equal-group contribution. An empty role contributes zero through the
original N_g and G denominators. No group is dropped or reweighted to groups
containing the role. Every group has each role in these retained treatments;
empty per-locus roles are still explicit in the full ledger.

## Primary role budget

The primary treatment contains 21,343 tokens and 107,808 emitted units,
giving 129,151 targets including termination. Counts and all three model
losses sum across roles to those of the original reference.

| Role | Targets | Mean gain within role | Contribution per total target | Equal-group contribution |
| --- | ---: | ---: | ---: | ---: |
| Initial unit | 21,343 | +0.00027466 | +0.00004539 | +0.00001167 |
| Second unit | 20,741 | +0.34763385 | +0.05582825 | +0.06410006 |
| Later unit | 65,724 | +0.26613519 | +0.13543425 | +0.13788983 |
| Termination | 21,343 | +0.11376398 | +0.01880020 | +0.01885744 |
| Sum of contributions | 129,151 | — | **+0.21010809** | **+0.22085900** |

All quantities are bits per their stated target denominator. Display is rounded
to eight decimal places; full values are in the inspectable
[summary](symbol-event-accounting-summary.json) and complete ledger.

## All twelve treatments

The following terms all use each treatment's original total target denominator.
They preserve the negative initial contributions and every representation
policy rather than selecting a favorable subset.

| Source/spaces | Unit policy | Initial term | Second term | Later term | Termination term | Total gain |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ZL3b split | `ascii_letters` | +0.00004539 | +0.05582825 | +0.13543425 | +0.01880020 | +0.21010809 |
| ZL3b split | `bench_sequences` | +0.00003393 | +0.05946035 | +0.08894435 | +0.01661358 | +0.16505221 |
| ZL3b split | `bench_and_minim_sequences` | -0.00012481 | +0.06333402 | +0.07212892 | +0.01852788 | +0.15386601 |
| ZL3b join | `ascii_letters` | -0.00026593 | +0.05582837 | +0.13778038 | +0.02251732 | +0.21586015 |
| ZL3b join | `bench_sequences` | -0.00030683 | +0.06045773 | +0.08998369 | +0.02097524 | +0.17110982 |
| ZL3b join | `bench_and_minim_sequences` | -0.00030916 | +0.06426494 | +0.07343681 | +0.02303143 | +0.16042401 |
| IT2a split | `ascii_letters` | +0.00004865 | +0.06081863 | +0.13507063 | +0.02497094 | +0.22090884 |
| IT2a split | `bench_sequences` | +0.00003771 | +0.06502940 | +0.08835418 | +0.02332118 | +0.17674247 |
| IT2a split | `bench_and_minim_sequences` | +0.00005584 | +0.06923753 | +0.07181977 | +0.02558906 | +0.16670220 |
| IT2a join | `ascii_letters` | +0.00004865 | +0.06081863 | +0.13507063 | +0.02497094 | +0.22090884 |
| IT2a join | `bench_sequences` | +0.00003771 | +0.06502940 | +0.08835418 | +0.02332118 | +0.17674247 |
| IT2a join | `bench_and_minim_sequences` | +0.00005584 | +0.06923753 | +0.07181977 | +0.02558906 | +0.16670220 |

Equal-group terms are retained for all twelve in the summary/full report.
Weighting can reverse the initial term's sign: ZL split bench has pooled
initial contribution +0.00003393 but equal-group contribution -0.00000806;
IT bench has +0.00003771 versus -0.00000948 under either spacing label.
Small component losses retain their original influence in equal-group means.

IT split/join records are identical apart from the spacing label and remain
dependent treatments. The editions describe related manuscript material;
changing notation units also changes context reach and the event population.
Absolute losses or class means across these policies cannot select a preferred
physical glyph system. The full ledger retains negative cells and empty roles.

## Interpretation and next test

At initial `(BOS,BOS)` events, Q2 and Q1's BOS counts contain the same
information. Another hierarchical shrinkage step changes predictions, as
the constructed control proved. The initial score term bounds that part of
the existing budget; it is small or negative in these data.

At second units, older BOS can distinguish initial-position predecessors from
the same representation later in a token. Later events have two emitted
context labels, and termination represents a boundary opportunity. None of
these labels or contributions identifies a causal source of the gain. Smoothing
also differs in later/termination contexts, and some older labels may add
little information given the immediate label. The larger terms cannot by
themselves establish extra glyph information, linguistic content or a copying
mechanism.

The source/cohort restrictions, transcription choices, coarse grouping and
whole-corpus exposure remain. This version fits no additional model and
changes no preference criterion. Separately planned regularization and
position/boundary controls can examine those alternatives. A stronger
decipherment claim requires source-linked glyph evidence, prospective
evaluation and independent reproduction under the project protocol. No
language, glyph function, decipherment or English translation is established.

## Complete artifact and reproduction

The [full ledger](symbol_event_accounting.json.gz) retains all 29,820 locus
scores and **119,280 role cells**, all 1,092 group and 60 fold breakdowns,
input/reference/cohort/fitted-count hashes and source group declarations.
It is lossless gzip: 9,330,943 compressed bytes and 66,850,918 JSON bytes,
with no filename, optional metadata or timestamp in its header.

- Compressed SHA-256: `e2d5bb1f4f09b73dc13b3b4cfb83eb3550b5db986d9f640a6552a6cd02d7e83a`
- Uncompressed JSON SHA-256: `88a24aa4653fbb9228948cf383e8db3953e2d3ccbf76fbeac935bfc2770c9054`

Python 3.10+, standard library, accepted repository inputs, and a local copy
of the exact public numeric reference report are required. The reference is
not added to this branch or supplied through its Git history. Save the linked
public reference JSON as a local file, verify the reference SHA-256 above, then
run from the repository root, replacing `REFERENCE.json` with its path:

```sh
PYTHONPATH=tests python3 -m unittest test_grouped_symbol_event_accounting -v
python3 scripts/grouped_symbol_event_accounting.py --reference-report REFERENCE.json --check research/baselines/symbol_event_accounting.json.gz
python3 scripts/grouped_symbol_event_accounting.py --reference-report REFERENCE.json --output /tmp/symbol-event-accounting-replay.json.gz
cmp research/baselines/symbol_event_accounting.json.gz /tmp/symbol-event-accounting-replay.json.gz
python3 - <<'PY'
import gzip
from pathlib import Path
raw = gzip.decompress(Path('research/baselines/symbol_event_accounting.json.gz').read_bytes())
with Path('/tmp/symbol-event-accounting-inspect.json').open('xb') as output:
    output.write(raw)
PY
```

The last command creates a new full JSON file for inspection. The CLI
output path must be new; direct, symlink and hardlink aliases introduced before
or during calculation cannot overwrite the reference, code or other inputs.
Complete replay compares all decompressed JSON and container bytes with exact
types. Pins are checked before and after accounting and before output.

Eleven synthetic tests cover role assignment, token reset/termination,
case-sensitive longest match, hand-derived rational probabilities/losses,
unequal group/role denominators and empty classes, a hand-derived five-fold
reference, excluded-group parameter perturbation, field/digest/count/loss drift,
transitive components with unselected leaves, input/helper drift, strict JSON,
lossless metadata-free compression and early/late exclusive-output refusal.
Full replay and a separate output replay are byte-identical.

A separate union/find graph, unit scanner, flat counters and rational scorer
reuses only the accepted source reader/cohort. It independently verifies all
sixty fitted-count digests, 29,820 locus scores, **every one of 119,280 role
cells**, all group/fold/overall aggregates, both contribution denominators,
empty roles and signed cases. Its largest numerical difference is
5.684341886080802e-14 bits. This is computational agreement on the same
exposed inputs, with no independent manuscript reading or validation implied.
