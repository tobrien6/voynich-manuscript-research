# Voynich Manuscript Research

An open effort to decode and translate the Voynich manuscript (Beinecke MS 408), grounded in primary sources and reproducible analysis.

## Project goal

Develop an independently reproducible decipherment of the manuscript's writing system and use it to produce a source-linked English translation. Publish validated passages as progress toward a manuscript-wide translation, with unresolved glyphs, alternative readings, and confidence made explicit.

Research on the digitized folios, illustrations, and documented history should advance that goal: establish a reliable transcription, test competing explanations of how the text works, and evaluate whether proposed decoding rules predict readings on unseen material. The project does not assume a particular language, cipher, or encoding mechanism.

## Start here

- [Contribution and PR review guide](CONTRIBUTING.md)
- [Project brief and research plan](99TOKENS.md)
- [Illustrated research folio](folio/README.md): five source-linked summary plates for the 99Tokens project page.
- [Decipherment and translation evaluation protocol](research/DECIPHERMENT_PROTOCOL.md)
- [Primary source register](research/SOURCES.md)
- [Pinned transliteration sources and working selection](research/transliteration/DECISION.md)
- [Section-beginning visual inventory](research/pilot/INVENTORY.md) and [machine-readable records](research/pilot/inventory.json)
- [Pilot transcription/image-link readiness](research/pilot/TRANSCRIPTION_READINESS.md): seven exact page links and three explicit mapping gaps.
- [Three provisional f76r image/native-locus anchors](research/pilot/F76R_ANCHORS.md): frozen selections, both native readings, and source-linked review windows awaiting independent row checks.
- [Local f76r image/native-text comparison](research/pilot/viewer/README.md): a reproducible read-only HTML artifact with literal source context and provisional review windows.
- [Native foldout page conventions](research/pilot/NATIVE_PAGE_CONVENTIONS.md): documented carrier and panel ordering, with region/glyph review pending.
- [Section boundary survey, including the shared 102r scan](research/boundary-pilot/INVENTORY.md)
- [Standalone-recto boundary inventory](research/PILOT_INVENTORY.md) and [selection protocol](research/PILOT_SELECTION.md)
- [Yale image-to-folio crosswalk and foliation audit](research/image-index/README.md)
- [Whole-corpus transcription image references and shared-scan dependencies](research/folio-alignment/IMAGE_COVERAGE.md)
- [GC and full/basic reference variant audit](research/transcriptions/REFERENCE_VARIANTS.md) and [aggregate records](research/transcriptions/intake-audit.json)
- [Exploratory token and repetition baselines](research/transliteration/BASELINES.md) and [recorded results](research/transliteration/token_baselines.json)
- [Interior notation-length order](research/transliteration/INTERIOR_ORDER.md): common-cohort exploration with endpoints fixed in its permutation controls
- [First-slot prefixes across catalog sections](research/transliteration/SECTION_STRATA.md): source-specific paragraph cohorts, section contrasts, and annotation disagreements.
- [Exploratory y-prefix lookup candidate](research/hypotheses/y-layout-prefix-v1/RESULTS.md): a precommitted removal rule and development-only vocabulary test, with prior exposure and diagnostic limitations explicit.
- [Prefix and vocabulary-opportunity controls](research/hypotheses/y-prefix-specificity-v1/RESULTS.md): fixed q/o comparisons and matched y frequency/length cells reduce the raw lookup contrast while retaining all treatments and exclusions.
- [Fixed y-lookup image pairs](research/hypotheses/y-lookup-image-v1/RESULTS.md): two source-stable positive lookup cases traced to provisional target/internal-reference regions, retaining unverified glyph boundaries.
- [Yale's digitized manuscript](https://collections.library.yale.edu/catalog/2002046)

Source-linked visual inventories cover section beginnings and boundaries across the six catalog groups. Their samples overlap; shared folios and scans must not be counted as independent evidence. Independent visual review is pending.

Exploratory token and repetition baselines now compare uncertainty policies on the paired ZL3b and IT2a inputs. A reproducible shuffle generator supplies synthetic-tested controls for later registered experiments, and an evaluation-split validator checks declared dependencies and prior exposure. The precommitted y-prefix representation candidate supplies a specific exploratory lookup prediction on data already used for candidate development. A real exposure-valid evaluation split, glyph adjudication, a validated decipherment, and source-linked translations remain pending. Decoding and translation remain the research objective.

## Research practice

For every contribution, state the question, source and folio references, method, result, limitations, and next test. Explain how the work advances decoding or translation. Distinguish source statements, direct observations, and interpretations. Keep negative results and contradictory evidence. A proposed reading should make predictions that can be tested on material not used to develop it.

Link to source images and transcriptions until their reuse terms have been checked. Record the edition, version, transcription conventions, and any normalization before comparing text statistics.

## Research notes

- [Literal-chain and token-boundary concordance](research/transliteration/TOKEN_BOUNDARY_CONCORDANCE.md): fixed-cohort source/spacing comparisons retain identical encoded strings with different boundaries, without adjudicating manuscript word divisions.
- [Paired symbol entropy](research/representation/PAIRED_ENTROPY.md): a fixed 2,485-locus descriptive sensitivity analysis across source/spacing, declared notation units and segment boundaries, with all frequency populations retained.
- [Synthetic greedy-wrapping control](research/line-wrap/RESULTS.md): an exact and sampled layout counterexample with all declared positive and zero cases, without fitting manuscript geometry.
- [Image checks of initial-prefix disagreements](research/transliteration/INITIAL_PREFIX_IMAGES.md): two deterministically selected source disagreements and a planned same-page shape comparison, with linked manuscript regions and provisional preferences awaiting independent review. No source corrections are applied.
- [Published methods and comparison limits](research/literature/README.md): primary-paper input choices, measurement units, and shuffle scopes, with explicit gaps to resolve before replication.
- [Self-citation generator audit](research/literature/COPYING_MECHANISM.md): pinned copying-model implementation and configuration, representation differences, and requirements for a prospective mechanism comparison.
- [Historical interlinear intake](research/historical/README.md): pin the recovered 1.6e6 archive and audit native H records before attempting published-method replication.
- [Historical H/modern IT2a page envelopes](research/historical/MODERN_PAGE_ENVELOPES.md): equal global totals retain four page-count discrepancies and unmatched identifiers.
- [Lossy lowercase notation comparison](research/historical/LOWERCASE_PROJECTION.md): 183 shared page streams match after explicit losses; frequency agreement can conceal sequence differences.
- [Paired paragraph-annotation agreement](research/transliteration/ANNOTATION_AGREEMENT.md): exact boundary-mark disagreements between the pinned ZL/IT editions, with identifiers for image review and explicit limits on source-defined strata.
- [Encoded paragraph-unit agreement](research/transliteration/PARAGRAPH_MEMBERSHIP.md): marker-pair checks, unassigned loci, and exact common paragraph membership for later unit-level comparisons.
- [Token and repetition baselines](research/transliteration/BASELINES.md), [locus-position effects](research/transliteration/POSITION_EFFECTS.md), and [prefix stratification](research/transliteration/PREFIX_STRATA.md): uncertainty-aware exploratory tests on paired text sources, with conditional controls and recorded limits. The stratification separates paragraph starts and source Currier labels rather than treating the pooled prefix pattern as uniform.
- [Equal-token recurrence at fixed slot distances](research/transliteration/REPETITION_DISTANCES.md): distances 1–4 on the accepted P0 cohort, with excluded coordinates, exact conditional covariance, and source/policy sensitivity retained.
- [Distinct repeating representations](research/transliteration/REPEATING_TYPES.md): each representation with any immediate self-repeat counted once, with an exact mean under the accepted fixed-gap locus control and explicit comparison limits.
- [Interior notation-length order](research/transliteration/INTERIOR_ORDER.md) and [early/late-half controls](research/transliteration/INTERIOR_HALVES.md): neighboring interior lengths depart from the stated controls in 2,165 common loci; finer position gradients and transcription effects remain alternative explanations.
- [Grouped length prediction](research/baselines/GROUPED_LENGTH_RESULTS.md): a fixed previous-length model has mixed cross-validation gains and fails the declared preference criterion in all four treatments on previously exposed data.
- [Synthetic grouped-predictor controls](research/baselines/GROUPED_CONTROL_RESULTS.md): all 64 uniform-independent simulations fail the criterion and all 64 simulations at each specified persistence level meet it; full fixed-seed results and known-process references are retained.
- [Fixed-cohort position comparison](research/transliteration/COHORT_EFFECTS.md): compare transcription and uncertainty variants on identical eligible locus keys, preserving per-locus disagreement.
- [Yale source and foliation audit](research/source-audit/README.md): contested provenance claims, terminal folio identifiers, and a reproducible check of image-label sampling units.
- [Folio request alignment](research/folio-alignment/README.md): preserve all indexed image matches and report unmatched or unsupported transcription identifiers explicitly.
- [Reproducible token-order controls](research/token-controls/README.md): synthetic-tested line and folio-side shuffles with explicit sampling constraints and pinned input provenance.
