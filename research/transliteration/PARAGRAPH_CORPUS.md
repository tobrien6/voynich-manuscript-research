# Native-Eva corpus for exact common paragraph units

## Question and declared processing

The [membership audit](PARAGRAPH_MEMBERSHIP.md) identifies 671 complete encoded
paragraph units with exactly the same ordered member loci in ZL3b and IT2a.
Which can be processed under the conservative native-Eva adapter without
dropping any member in either source or either comma policy?

The [plan](PARAGRAPH_CORPUS_PLAN.md) was committed before eligibility and token
totals were computed. This contribution supplies a corpus producer, full cache
replay, and a [token-free coverage ledger](paragraph_corpus_coverage.json).
It selects no test statistic, candidate mechanism, or untouched evaluation set.

Recompute the parent membership report completely from hash-verified source
bytes before constructing candidates. Use its exact ordered matches, retain
both original unit IDs, and select **all present generic P subtypes** explicitly:
P0, P1, Pb, Pc, Pr, Pt in these pins. The adapter's narrower P0/P1 defaults
are not used. Source credits, editions, and reuse terms remain in the
[source catalog](../../data/transliterations.json) and
[adapter guide](TOKEN_ADAPTER.md).

Apply both split and join treatments of uncertain commas. Native case,
source identities, inherited variables, locators, and drawing-interruption
handling remain unchanged. A paragraph enters the common corpus only if
**every member is adapter-eligible in all four variants**. No additional
locator, length, readability, section, or minimum-token filter is applied.

## Coverage and selection limits

| Measure | Count |
| --- | ---: |
| Exact common membership candidates | 671 units |
| Candidate member loci | 3,647 |
| Common eligible under all four variants | 233 units |
| Their complete member loci | 885 |
| Candidates excluded from the common corpus | 438 units |

| Source | Comma policy | Locally eligible units / 671 | Native tokens in the common corpus |
| --- | --- | ---: | ---: |
| ZL3b | split | 234 | 7,758 |
| ZL3b | join | 234 | 7,198 |
| IT2a | split | 630 | 7,663 |
| IT2a | join | 630 | 7,663 |

Local eligibility and common eligibility are different denominators. One unit
eligible in ZL is excluded by IT; every candidate remains in the ledger.
Equal IT policy totals do not create two independent observations.

ZL's annotation-rich input excludes many entire units under the declared
conservative policy. Unit-level reason counts are 324 for alternative readings,
236 for ligature braces, 99 for unreadable material, 80 for extended escapes,
and 18 for non-plain Eva characters; these reasons overlap. IT excludes 41
units for unreadable material. These are preprocessing exclusions, not counts
of incorrect source readings or manuscript errors.

The retained corpus is a restricted, uncertainty-filtered subset. An experiment
must disclose the 438 excluded candidates and the candidate/member denominators
rather than claim coverage of all paragraph text. A relaxed uncertainty policy
would need its own version and an explicit sensitivity comparison.

## Corpus contract

The generated corpus has `producer_version: common-encoded-paragraph-eva-v1`
and `analysis_unit: source_defined_encoded_paragraph`. Its inputs bind the
parent report bytes, source catalog, pre-execution plan, and implementation
fingerprints. Source pins are also retained directly.

Every candidate has a digest-based common unit ID, native page ID, ordered
member keys, membership digest, original source-unit IDs, common eligibility,
and four source/policy records. Those records retain local eligibility and
every failed member's exclusion reasons. Every original member locus remains
visible with its full source locator, type, physical file line number,
inherited variables, uncertainty counts, and adapter eligibility.

For a common eligible candidate, each member retains **its own token list**.
Rows are never flattened or concatenated across source loci. A singleton unit
can remain eligible; a later statistic must declare any extra size requirement
before its evaluation.

For an excluded candidate, **all token lists and token counts are null in all
four variants**, including locally readable members and locally eligible
variants. This prevents a partially readable paragraph from silently becoming
a new unit or creating adjacency across a dropped row. `adapter_eligible`
describes the original locus, while `common_eligible` governs whether its unit
has a corpus payload; the two fields must not be conflated.

This is a new paragraph interface. It is not an adapter locus packet or a
physical-line reconstruction and should not be passed unchanged to tools
expecting those different schemas.

## Reproduce and verify

Python 3.10 or later; standard library only:

```sh
python3 scripts/paragraph_token_corpus.py --output research/transliteration/paragraph_corpus_coverage.json
python3 scripts/paragraph_token_corpus.py --check research/transliteration/paragraph_corpus_coverage.json
python3 scripts/paragraph_token_corpus.py --corpus-output /tmp/voynich-paragraph-corpus.json
python3 scripts/paragraph_token_corpus.py --check-corpus /tmp/voynich-paragraph-corpus.json
PYTHONPATH=tests python3 -m unittest test_paragraph_token_corpus -v
```

The committed report contains metadata and coverage, with a canonical digest
of the full corpus, while native token payloads are generated locally. Cache
verification compares complete canonical content with fresh pinned producer
output; it checks tokens, types, row coverage, identities, and exclusions rather
than trusting the cache's own summaries. Formatting can vary while canonical
content remains identical. Duplicate JSON keys and non-JSON numeric constants
are rejected. Changes to pinned code, plans, or inputs require regenerated,
reviewed provenance rather than a silent rebinding.

Source inputs, cataloged editions, source implementation, both plans, the parent
report, and verification inputs are protected from output writes, including
resolved and hardlink aliases. Coverage and full-corpus destinations must be
distinct. All input/replay checks complete before any output is written.

## Limits and next step

Units remain source-defined encoded paragraphs, and tokens remain native
transcription strings. They are not verified physical paragraphs, glyph units,
decoded words, or translations. Whole-unit exclusions can select different
text and notation conditions from the full corpus. The two editions and their
policies remain dependent; foldout, leaf, and image dependencies are unchanged.

A later paragraph-level experiment must declare its statistic, controls,
additional eligibility requirements, source/glyph representation, dependency
groups, and exposure-aware split. It should preserve the source-locus boundaries
where its control requires them. This producer supplies a traceable input and
honest exclusion denominators, not a tested decipherment or new unseen data.

The [boundary recurrence follow-up](PARAGRAPH_BOUNDARY_REPETITION.md) measures
exact token equality between consecutive original loci within these whole
units. It keeps all 652 encoded boundaries and accounts for shared-locus
covariance under its declared within-locus permutation control.
