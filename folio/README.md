# Illustrated investigation folio

Five generated information pages explain the investigation's goal, evidence,
transcription choices, selected exploratory findings, and next tests. The
12 October 2026 refresh replaces all five earlier plates with shorter text,
consistent reading order, definitions beside counts, and limitations beside
results. No validated decipherment or translation has been established.

The [manifest](folio.json) uses the 99Tokens portrait folio format. Its cover
reuses page 1; captions, descriptive alt text, credits, uncertainty notes and
dates accompany every page. `current` means current for the cited snapshot,
not scientifically validated. Each PNG is below the 10 MB image limit.

## Evidence snapshot

Scientific claims are taken from accepted public main revision
[`1c74085`](https://github.com/tobrien6/voynich-manuscript-research/tree/1c74085cee3ad1369ffa4a93fec802f22d9b8c85),
checked on 12 October 2026. Open proposals are excluded from the results. Issue
[#13](https://github.com/tobrien6/voynich-manuscript-research/issues/13) was still
open when the roadmap was prepared. These are selected results; the repository
reports retain complete treatments, exclusions and contradictions.

| Page | Evidence and interpretation limits |
| --- | --- |
| [1. Project status](01-project-overview.png) | [Project brief](../99TOKENS.md), [evaluation protocol](../research/DECIPHERMENT_PROTOCOL.md), and [leading-y diagnostic](../research/hypotheses/y-layout-prefix-v1/RESULTS.md). An explicit exploratory rule exists; an exposure-valid frozen evaluation, supported translation and independent reproduction remain pending. |
| [2. Evidence coverage](02-source-and-folio-map.png) | [Pilot inventory](../research/pilot/INVENTORY.md), [Yale index](../research/image-index/README.md), [pilot readiness](../research/pilot/TRANSCRIPTION_READINESS.md), and [native page conventions](../research/pilot/NATIVE_PAGE_CONVENTIONS.md). Ten sides, 213 scan views and 204 numbered side labels count different units. Seven exact page metadata links and three mapping gaps remain the readiness result. Provisional regions do not pass that gate. |
| [3. Transcription choices](03-transcription-choices.png) | [Source decision](../research/transliteration/DECISION.md) and [boundary concordance](../research/transliteration/TOKEN_BOUNDARY_CONCORDANCE.md). Among 2,940 eligible loci, 2,054 share encoded chains; 562 split and 767 join disagreements occur within that subset. The counts overlap at 359 loci and cannot be added. These are encoded-source comparisons, not adjudicated words. |
| [4. Selected findings](04-measured-findings.png) | [Repetition](../research/transliteration/BASELINES.md), [interior half controls](../research/transliteration/INTERIOR_HALVES.md), [independent-position counterexample](../research/baselines/independent-position-length/RESULTS.md), [exact-slot prediction](../research/baselines/EXACT_SLOT_LENGTH_RESULTS.md), and [y-specificity controls](../research/hypotheses/y-prefix-specificity-v1/RESULTS.md). Studies use different cohorts and statistics. Repetition uses primary ZL split/exclude on the 3,884-key candidate intersection. Interior order uses 2,165 eligible loci; IT split/join are identical dependent treatments. The y comparison uses the same 13 units before/after matching, rounded from +0.39232859 and +0.10641026; this differs from the q/o comparison's 13-unit cohort. Matching changes weighting, not an established causal share. All material was previously exposed. |
| [5. Next tests](05-open-work-and-roadmap.png) | [Evaluation protocol](../research/DECIPHERMENT_PROTOCOL.md), [pilot readiness](../research/pilot/TRANSCRIPTION_READINESS.md), [local f76r reviewer](../research/pilot/viewer/README.md), [recorded viewer assets](../research/assets/README.md), and [issue #13](https://github.com/tobrien6/voynich-manuscript-research/issues/13). The original 8/2 pilot split remains a proposal. Review, exposure/dependency assessment, frozen rules, prospective evaluation and reproduction precede supported translation. |

## Generation and provenance

All five pages were generated with the built-in `image_gen` tool; its underlying
model identifier was not exposed. The images contain original editorial layouts
and explanatory graphics, with no manuscript facsimiles or invented glyphs.
No Yale images, private caches, credentials or transcription payloads were
sent to generation or added to this contribution.

[generation-prompts.json](generation-prompts.json) records the shared design
specification and exact five page prompts. [provenance.json](provenance.json)
records source hashes, image hashes, generation method, snapshot, role evidence
and the previous folio's provenance reference. Reports supply the facts;
generated graphics must not be used as research measurements.

## Display and upkeep

The 99Tokens renderer reads the manifest and images from the default branch.
The [live example](https://99tokens.org/folio.example.json) and
[project folio API](https://99tokens.org/api/projects/59210176-9997-4f13-84fc-c46b43d165b3/folio)
were checked on 12 October 2026; the API reported `ready` for the previous five
plates. Updated images appear after merge and the site's cache refresh. A branch
preview does not complete the public update.

For future refreshes, revise the image, caption, alt text, note and provenance
together. Pin claims to accepted evidence and date the snapshot. Git history
preserves earlier artwork and provenance. If a superseded page remains in the
manifest, label it `outdated` and name its replacement.
