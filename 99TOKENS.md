# Voynich Manuscript Research

## Goal: decode and translate the manuscript

Develop an independently reproducible decipherment of the Voynich manuscript's writing system and use it to produce a source-linked English translation. Publish validated passages as progress toward a manuscript-wide translation, preserving unresolved glyphs, alternative readings, and confidence at each step.

The manuscript is held by Yale's Beinecke Rare Book and Manuscript Library as MS 408. [Yale describes its text as undeciphered](https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript). Decoding and translation are the research objective, not an established result. The project has no preferred language, cipher, or encoding mechanism.

## Research question

What reproducible rules explain the manuscript's glyphs, token structure, and text organization, and can those rules support consistent readings and translations of folios not used to develop them?

## Milestones toward decipherment and translation

1. **Build a traceable pilot corpus.** Maintain the source register; inventory a selected set of folios; compare documented transcription systems and editions. Preserve ambiguous glyphs, spaces, line breaks, and missing material. Record image links, dataset versions, access conditions, and preprocessing.
2. **Establish constraints on decoding.** Measure glyph and token frequencies, token lengths, repetition, and line-position effects. Compare appropriate shuffled, language, and synthetic encoding baselines. Test sensitivity to transcription choices. Use the results to constrain candidate mechanisms, without treating a statistical resemblance as a translation.
3. **Test explicit decipherment hypotheses.** Register each candidate's glyph mapping, segmentation rules, proposed mechanism and language (if any), predictions, failure conditions, and evaluation method before testing. Freeze the rules and evaluate on reserved folios; record contradictions and failed candidates.
4. **Translate validated passages.** Show the source image reference, transcription, decoding steps, proposed reading, literal English translation, and explanatory notes together. Mark gaps and competing readings. New exceptions require a new candidate version and another untouched test set.
5. **Seek independent reproduction and expand coverage.** Have another researcher reproduce the readings from the frozen rules and source material. Extend successful candidates across sections and transcription variants before claiming a manuscript-wide decipherment or translation.

## What counts as success

A credible decipherment must explain how readings are derived through documented rules, make successful predictions on held-out material, survive relevant baseline comparisons and transcription uncertainty, and be independently reproducible. A translation must remain traceable to those readings and disclose its unresolved content. Fluent English, an isolated word match, or a plausible match to an illustration is insufficient evidence.

The full goal is a reproducible account of the writing system and a translation of the surviving text with remaining uncertainty documented. Partial readings are interim results with explicitly limited scope. If tests do not support recoverable linguistic content, report that evidence and its limits rather than invent a translation.

## First task

Prepare a decipherment pilot of 10 folios selected across the six sections described in Yale's overview. Document the selection rule before collecting observations. For each folio, record its stable image link, section attribution and source, text layout, illustration description, and uncertainties. Compare available transcription editions and recommend a versioned dataset with documented glyph conventions and reuse terms.

Before developing a candidate, commit a provisional split of eight development folios and two held-out folios, recording any prior exposure. This small pilot tests the workflow; it cannot establish manuscript-wide validity. Deliver the inventory, transcription decision, split manifest, and a first registered hypothesis with a measurable prediction and failure condition using the [evaluation protocol](research/DECIPHERMENT_PROTOCOL.md).

The [visual inventory](research/pilot/INVENTORY.md) now records ten selected target folio sides with Yale image identifiers, visible text layouts, illustrations, and uncertainties. Its [selection protocol](research/pilot/SAMPLING.md), [machine-readable records](research/pilot/inventory.json), and [source-check script](scripts/verify_pilot.py) make the contribution checkable. Several canvases contain multiple foldout panels retained within one record. The pilot-specific development/evaluation split, frozen candidate, independent observation review, and translations remain pending. The visual inspection of all ten images must be disclosed when defining prior exposure for a later split.

The [local f76r comparison guide](research/pilot/viewer/README.md) explains how to open the accepted HTML viewer from a local clone. Choose and zoom among [three provisional image/native-text anchors](research/pilot/F76R_ANCHORS.md), with literal ZL3b/IT2a rows, neighbors, unresolved readings and source-file links beside the recorded review windows. Its Yale images require an internet connection. The [offline packet guide](research/pilot/offline-packet/README.md) adds the [recorded asset helper](research/assets/README.md) and exact fetch/build/check commands: reuse a verified five-file cache to view the same windows locally, with internet needed for missing assets or public evidence links. Keep image caches, packets and retrieval receipts local. Row associations remain provisional, glyph adjudication remains pending, and opening this previously exposed material creates no untouched evaluation evidence.

The [section boundary survey](research/boundary-pilot/INVENTORY.md) and [standalone-recto boundary inventory](research/PILOT_INVENTORY.md), with its [selection protocol](research/PILOT_SELECTION.md) and [CSV](research/data/pilot-folios.csv), add complementary boundary records. The survey includes 102r within a shared scan; the standalone-recto rule selects 100r instead. These inventories share most of their images, so their observations do not create independent manuscript samples. Prior exposure must be recorded across all inventories when defining a later split.

The [working transliteration decision](research/transliteration/DECISION.md) now recommends the pinned ZL3b source for preserving uncertainty, with IT2a for paired sensitivity checks. Source bytes, credits, reuse terms, and structural coverage are recorded in the [data catalog](data/transliterations.json) and [coverage audit](research/transliteration/coverage_audit.json). This supplies the initial source choice; glyph adjudication, image alignment, the evaluation split, and a registered hypothesis remain pending.

The [pilot transcription/image-link audit](research/pilot/TRANSCRIPTION_READINESS.md) now identifies seven selected sides with exact page identifiers in both editions, containing 251 shared present locations. Three targets remain blocked: 67r and 68r use unmapped panel identifiers, while 85v belongs to a shared 85v/86r scan and has no exact transcription page. The [reproducible report](research/pilot/transcription-readiness.json) preserves those gaps and source disagreements; its completeness check fails until the mappings are documented. Exact metadata links still need image/glyph review and do not create untouched evaluation material.

The [reference variant audit](research/transcriptions/REFERENCE_VARIANTS.md) extends the accepted ZL/IT source decision with GC and both RF variants, using the same IVTFF reader. Identical RF alphabet headers conceal different native text, so later analyses must retain exact variant URLs and source hashes. This is a corpus identity check, not a decipherment result.

The [literal-chain boundary audit](research/transliteration/TOKEN_BOUNDARY_CONCORDANCE.md)
compares 2,940 native P0 loci eligible in both editions under both comma policies,
from 3,884 shared present candidates with 944 joint exclusions. The editions have
identical concatenated, case-preserved ASCII strings at 2,054 loci, but their token
boundaries disagree at 562 loci under split spacing and 767 under join spacing;
359 disagree under both policies. Different strings are not aligned. These are
dependent encoded source representations, including one-token loci and same-line
fragments, rather than independently verified manuscript words or physical lines.

![Both treatments use the same 2,940 native loci. Split: 1,492 same chain and boundaries, 562 same chain with different boundaries, 886 different chains. Join: 1,287, 767 and 886 respectively.](https://raw.githubusercontent.com/tobrien6/voynich-manuscript-research/main/research/transliteration/figures/token-boundary-concordance.png)

The [figure, exact plotted values and provenance](research/transliteration/figures/TOKEN_BOUNDARIES.md)
retain the complete category partitions and denominators. Source-informed image
cases at [f67r1.1](research/panel-regions/67R_BOUNDARY_CASE.md) and
[f102r1.14–15](research/panel-regions/102R_BOUNDARY_PAIR.md) provide provisional row
context while leaving glyph regions and word divisions unresolved. No source
correction, accuracy ranking, independent or untouched evaluation, decipherment,
or translation follows from literal-string or visible-gap agreement.

The [native separator provenance ledger](research/transliteration/BOUNDARY_SEPARATOR_PROVENANCE.md)
locates period, uncertain-comma and drawing notation at 1,458 distinct encoded
offsets across 970 native loci with a source-only cut under at least one spacing
policy. Of these offsets, 409 disagree only when commas split, 773 only when
commas join, and 276 under both policies. Both sources are traced on the same
2,940-key cohort; paired coordinates are assigned only on identical strings.
The [complete records](research/transliteration/boundary_separator_provenance.json)
preserve native marker ranges, neighboring letter positions and every original
alternative. These source-notation differences make spacing sensitivity
traceable while leaving physical word/glyph boundaries, source accuracy and
translation unresolved.

The [exploratory token and repetition baselines](research/transliteration/BASELINES.md) compare uncertainty policies on 3,884 shared present P0 loci in ZL3b and IT2a, with [complete recorded results](research/transliteration/token_baselines.json). The primary split/exclude treatment has 272 equal adjacent pairs against a conditional expectation of 270.77; other treatments expose sensitivity to preprocessing. This full-corpus exploration does not provide an untouched evaluation set or validate a decoding rule.

The [token-order control generator](research/token-controls/README.md) supplies reproducible within-row and within-folio-side shuffles that preserve excluded slots and stated sampling constraints. Its committed examples are synthetic. The [split record format and validator](research/evaluation/SPLIT_FORMAT.md) check declared dependencies, input identity, exposure, and freeze chronology; they do not choose real held-out material or prove exposure history. A reviewed image/transcription mapping, a real frozen split, and a first registered hypothesis remain the next steps toward a decipherment test.

The [locus-position analysis](research/transliteration/POSITION_EFFECTS.md) records literal EVA q/y-prefix and notation-length contrasts at original first and last token slots under the same uncertainty policies, with [complete results](research/transliteration/locus_positions.json). It uses conditional within-locus controls and explicit eligibility counts. These measurements constrain simple exchangeability within the chosen units; they do not identify a language, cipher, glyph reading, or translation.

The [paired paragraph-annotation audit](research/transliteration/ANNOTATION_AGREEMENT.md)
records 29 paragraph-start and 54 paragraph-end disagreements across the 3,884
shared P0 loci in ZL3b and IT2a. It preserves all discordant identifiers and
source-specific metadata for later image review. These are differences between
source annotations, not adjudicated manuscript boundaries or decoding results.

The [fixed-cohort position comparison](research/transliteration/COHORT_EFFECTS.md)
tests transcription sensitivity on identical eligible locus samples. The
observed effect directions persist, while notation-length measurements and
individual-locus contrasts remain sensitive to source and uncertainty choices.
This is exploratory evidence for candidate constraints, not a decipherment.

The [prefix stratification](research/transliteration/PREFIX_STRATA.md) separates source-marked paragraph starts and source Currier labels on 3,848 shared regular P0 locations, excluding 36 same-line fragments. In the primary treatment, first-slot y enrichment occurs in non-paragraph-start loci, while the q contrast within those non-paragraph-start cohorts has opposite signs in source groups A and B. All uncertainty treatments, denominators, and controls are retained in the [complete report](research/transliteration/prefix_strata.json). These exploratory patterns constrain candidate mechanisms on already exposed text; the labels do not identify natural languages and the results do not validate a decipherment.

The [interior notation-length order analysis](research/transliteration/INTERIOR_ORDER.md) keeps endpoints fixed and tests neighboring interior lengths on 2,165 loci eligible in both sources and spacing policies. All four treatments depart above their conditional permutation expectations, with all 999 controls retained in the [report](research/transliteration/interior_length_order.json). This exploratory result adds an order constraint; interior position gradients and transcription effects remain possible explanations, and no decipherment or untouched evaluation is claimed.

The [early/late-half sensitivity test](research/transliteration/INTERIOR_HALVES.md) preserves each half's interior length distribution on that identical cohort. Centered effects decrease but remain beyond all 999 controls in each treatment; the primary effect changes from 0.089062 to 0.067330. This limits a coarse positional explanation while retaining finer gradients and other mechanisms as alternatives.

The [exact half-control invariance audit](research/transliteration/HALF_DEGENERACY.md) identifies 55 invariant loci in the primary treatment, including 14 nonconstant-half cases outside the earlier narrow counter. Every varying locus has a verified swap witness; all 2,165 loci remain in the original denominator, with no changes to effects, controls or tails.

The [grouped length-prediction comparison](research/baselines/GROUPED_LENGTH_RESULTS.md) fits context-only and previous-length models with five folds over 86 recorded image-dependency components. Every treatment fails its fixed preference criterion: pooled gains can conceal losses when groups receive equal weight, and ZL join loses under both weightings. Whole-corpus prior exposure remains explicit; these diagnostic conditional scores neither create untouched evaluation material nor establish a decoding mechanism.

The [catalog-section prefix analysis](research/transliteration/SECTION_STRATA.md) separates first-slot contrasts across Yale's six numeric ranges and source-marked paragraph starts, with [complete results](research/transliteration/section_strata.json). It retains 29 paragraph-start annotation disagreements and source-specific eligibility. Non-start y contrasts are positive in all six ranges, while the final-text paragraph-start contrast is near zero and differs in sign between sources. These exposed-data measurements preserve small cohorts, unresolved foliation, and representation limits; they do not establish a section's meaning or a decipherment.

The [y-layout-prefix v1 lookup diagnostic](research/hypotheses/y-layout-prefix-v1/RESULTS.md) tests a removal rule and decision criterion committed before dictionary construction. On 15 common diagnostic page-family units, deleting leading literal EVA y improves first-slot matches to a development-only internal vocabulary more than other-slot matches across all eight source/uncertainty treatments. The prediction survives its fixed criterion, with all counts, losses, exclusions, and hashes in the [report](research/hypotheses/y-layout-prefix-v1/results.json). Full-corpus results already helped develop this candidate, so its dictionary partition is not a valid held-out evaluation or the original pilot split. Glyph meaning, a causal layout-marker role, language, and translation remain unresolved.

The [preplanned prefix-specificity controls](research/hypotheses/y-prefix-specificity-v1/RESULTS.md)
retain the accepted lookup diagnostic's locations, partition and dictionaries.
On common units, y removal has greater first-versus-other gain than fixed q/o
controls. Matching y development frequency and representation length lowers
primary selectivity from +0.39232859 to +0.10641026 on the same 13 units, with
sparse cells and every treatment/exclusion in the [complete report](research/hypotheses/y-prefix-specificity-v1/results.json).
These exposed-data controls constrain lookup interpretations; they do not
identify a glyph function, language, or translation.

The [fixed y-lookup image-pair pilot](research/hypotheses/y-lookup-image-v1/RESULTS.md)
traces two source-stable positive removal gains to their selected target and
development-reference regions. Nonblind AI inspection describes broad visible
correspondence with uncertain boundaries; both alignments remain provisional,
no source correction is applied, and no glyph function or translation is inferred.

## Evidence standard

- Cite a source and folio for factual statements about the manuscript.
- Separate direct observations, reported claims, and interpretations.
- Keep an explicit record of contradictions and failed tests.
- Compare patterns against appropriate shuffled and language baselines before interpreting them.
- Test promising explanations on held-out folios and across transcription variants.
- Treat apparent matches as hypotheses until independently reproducible.
- Keep transcription, decoding, and translation separate so each step can be checked.
- Report coverage and uncertainty; never fill unreadable or unsupported passages with invented text.

## Primary sources

- [Yale Beinecke overview](https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript)
- [Beinecke manuscript catalog: MS 408](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM)
- [Yale digital manuscript](https://collections.library.yale.edu/catalog/2002046)
- [Source register and access notes](research/SOURCES.md)

## Contribute

Open an issue for a focused decoding or translation question, or propose a pull request with a documented observation, source correction, transcription comparison, candidate mechanism, reproducible test, or evaluated passage. Explain how it advances the goal, and include enough source detail and method description for another researcher to check the result. Follow the [decipherment and translation evaluation protocol](research/DECIPHERMENT_PROTOCOL.md) for proposed readings.
