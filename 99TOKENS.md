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

The [visual inventory](research/pilot/INVENTORY.md) now records ten selected target folio sides with Yale image identifiers, visible text layouts, illustrations, and uncertainties. Its [selection protocol](research/pilot/SAMPLING.md), [machine-readable records](research/pilot/inventory.json), and [source-check script](scripts/verify_pilot.py) make the contribution checkable. Several canvases contain multiple foldout panels retained within one record. The development/evaluation split, first registered hypothesis, independent observation review, and translations remain pending. The visual inspection of all ten images must be disclosed when defining prior exposure for a later split.

The [section boundary survey](research/boundary-pilot/INVENTORY.md) and [standalone-recto boundary inventory](research/PILOT_INVENTORY.md), with its [selection protocol](research/PILOT_SELECTION.md) and [CSV](research/data/pilot-folios.csv), add complementary boundary records. The survey includes 102r within a shared scan; the standalone-recto rule selects 100r instead. These inventories share most of their images, so their observations do not create independent manuscript samples. Prior exposure must be recorded across all inventories when defining a later split.

The [working transliteration decision](research/transliteration/DECISION.md) now recommends the pinned ZL3b source for preserving uncertainty, with IT2a for paired sensitivity checks. Source bytes, credits, reuse terms, and structural coverage are recorded in the [data catalog](data/transliterations.json) and [coverage audit](research/transliteration/coverage_audit.json). This supplies the initial source choice; glyph adjudication, image alignment, the evaluation split, and a registered hypothesis remain pending.

The [reference variant audit](research/transcriptions/REFERENCE_VARIANTS.md) extends the accepted ZL/IT source decision with GC and both RF variants, using the same IVTFF reader. Identical RF alphabet headers conceal different native text, so later analyses must retain exact variant URLs and source hashes. This is a corpus identity check, not a decipherment result.

The [exploratory token and repetition baselines](research/transliteration/BASELINES.md) compare uncertainty policies on 3,884 shared present P0 loci in ZL3b and IT2a, with [complete recorded results](research/transliteration/token_baselines.json). The primary split/exclude treatment has 272 equal adjacent pairs against a conditional expectation of 270.77; other treatments expose sensitivity to preprocessing. This full-corpus exploration does not provide an untouched evaluation set or validate a decoding rule.

The [token-order control generator](research/token-controls/README.md) supplies reproducible within-row and within-folio-side shuffles that preserve excluded slots and stated sampling constraints. Its committed examples are synthetic. The [split record format and validator](research/evaluation/SPLIT_FORMAT.md) check declared dependencies, input identity, exposure, and freeze chronology; they do not choose real held-out material or prove exposure history. A reviewed image/transcription mapping, a real frozen split, and a first registered hypothesis remain the next steps toward a decipherment test.

The [locus-position analysis](research/transliteration/POSITION_EFFECTS.md) records literal EVA q/y-prefix and notation-length contrasts at original first and last token slots under the same uncertainty policies, with [complete results](research/transliteration/locus_positions.json). It uses conditional within-locus controls and explicit eligibility counts. These measurements constrain simple exchangeability within the chosen units; they do not identify a language, cipher, glyph reading, or translation.

The [fixed-cohort position comparison](research/transliteration/COHORT_EFFECTS.md)
tests transcription sensitivity on identical eligible locus samples. The
observed effect directions persist, while notation-length measurements and
individual-locus contrasts remain sensitive to source and uncertainty choices.
This is exploratory evidence for candidate constraints, not a decipherment.

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
