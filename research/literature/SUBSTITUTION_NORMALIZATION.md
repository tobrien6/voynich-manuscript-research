# Affected-word mass can reverse substitution-score rankings

Question: does comparing entropy decreases after separately renormalizing
each affected-word subset preserve a full-corpus substitution ranking?

It need not. The score for the complete corpus is the subset score multiplied
by that subset's occurrence mass. Different replacement candidates can have
different masses. This original synthetic control shows an explicit reversal
and records the normalization required for a later source-grounded comparison.
No manuscript input is processed here.

## Inspected source and interpretation boundary

Reddy–Knight's [paper](https://aclanthology.org/W11-1511.pdf), Section 3.2,
printed page 80, describes BESTSUB through unigram word-entropy decrease and
discusses gallows/case hypotheses. The recovered
[`basic_stats.py`](https://github.com/sravanareddy/deciphervoynich/blob/643b881b2937bae8193814d8ff5d6e99a48bf7c5/basic_stats.py)
at author-associated commit `643b881b2937bae8193814d8ff5d6e99a48bf7c5`
contains `CorpusStats.get_bestsub`. The [source intake](REDDY_SOURCE_INTAKE.md)
pins that 2,466-byte file to SHA-256
`12102b9c290838ebe0c60580f62cb449759cb71d13949dbcf5c23c82d1aa4ccc`.

Static inspection finds that, for each pair of distinct characters, the
function selects token occurrences containing either character. It builds
the original and substituted word distributions on that selected list and
normalizes both by the selected list's length. The stored entropy difference
has no additional multiplication by the fraction of all tokens selected.
The function's description mentions whole-corpus replacement, while its
counting operations calculate a conditional-subset score.

A full-corpus interpretation of the paper's definition would instead use the
mass-weighted score below. This interpretation and the inspected 2015 code
do not establish the actual 2011 implementation. The current example neither
reproduces nor contradicts a particular reported gallows mapping. No author
code is executed, and no claim about the author's intent is made.

## Why the mass factor is necessary

Let the corpus have positive word occurrence counts and total count `N`.
Replace every occurrence of character `c` by distinct character `d`, with no
other operation. Let `S` contain words with `c` or `d`, of total count `T`.
All other words remain unchanged. Every transformed word in `S` contains `d`,
so it cannot collide with a word outside `S`, which contains neither symbol.

Membership in this partition retains the same probabilities before and after
replacement. Shannon's entropy chain rule therefore gives exactly:

$$
\Delta_{\mathrm{whole}} = \frac{T}{N}\,\Delta_{\mathrm{subset}}.
$$

Here the two decreases use separate normalized word distributions. In count
form, for each merged word class with constituent counts `n_i` and class total
`n_g`, the common information numerator is:

$$
I = \sum_g\left(n_g\log_2 n_g - \sum_{i\in g}n_i\log_2 n_i\right),\qquad
\Delta_{\mathrm{subset}}=I/T,\quad\Delta_{\mathrm{whole}}=I/N.
$$

Singleton classes contribute exactly zero. Scores under `c`→`d` and `d`→`c`
are equal because they induce the same equivalence classes; the score alone
does not establish a direction of a case relationship. If two candidates
have equal affected mass, multiplication preserves their score ranking.
Unequal masses require the declared normalization before comparison.

## Fixed synthetic reversal

The deliberately constructed corpus has `A:1`, `B:1`, `C:99`, `XC:99`, for
200 occurrences and four types. Compare just the two declared candidates
`A`→`B` and `A`→`C`. These are original toy strings, not transcription symbols
observed in this contribution. The [complete record](substitution-normalization-control.json)
retains all counts, merged classes, before/after entropies and exact mass
fractions. Entropy values use base two and are rounded to twelve decimals.

| Replacement | Affected occurrences / all | Subset entropy decrease, bits | Whole-corpus entropy decrease, bits |
| --- | ---: | ---: | ---: |
| `A`→`B` | 2 / 200 | 1.000000000000 | 0.010000000000 |
| `A`→`C` | 199 / 200 | 0.040599565777 | 0.040396567948 |

The subset comparison selects `B`: the two equally frequent selected types
merge perfectly. The complete-corpus comparison selects `C`: the smaller
conditional decrease applies to much more occurrence mass. Both candidates
and both scores remain visible. This is a constructed counterexample, not an
estimate of how often rankings differ in the manuscript.

## Reproduction and validation

```sh
PYTHONPATH=tests python3 -m unittest test_substitution_entropy_control -v
python3 scripts/substitution_entropy_control.py --check
# Generate the same fixed synthetic cases into a new file:
python3 scripts/substitution_entropy_control.py --output NEW_REPORT.json
cmp NEW_REPORT.json research/literature/substitution-normalization-control.json
```

The standard-library producer accepts no corpus input and makes no network
request. It records the inspected source identity as provenance, not as a
runtime verification or execution of that file. New outputs are created
exclusively. The report rejects duplicate/non-finite JSON on checking.

Five focused tests pass: a balanced merge has known 1-bit and 0.5-bit scores;
a non-colliding substitution leaves entropy unchanged; simultaneous merges
obey mass weighting and direction symmetry; a separate direct before/after
entropy implementation verifies the complete toy reversal and exact masses;
invalid counts/mappings fail. Complete report replay, producer identity,
links and whitespace pass. Python 3.14.3 was used; printed entropy decimals
are numerical approximations, while the mass ratios and mathematical identity
are exact. Only original synthetic counts/code and public source references
are published.

This clarifies a comparison choice that could otherwise alter constraints on
a decoding proposal. A later native-source experiment should freeze candidate
symbols, token/type weighting, normalization, tie rules and all comparisons
before scoring, and preserve both metrics rather than selecting one after
seeing results. The example supplies no manuscript character mapping,
language, case assignment, decipherment or translation.
