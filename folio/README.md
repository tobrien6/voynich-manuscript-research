# Illustrated research folio

Five informational plates summarize the project's evidence, transcription choices,
exploratory measurements, and remaining tests. They are a dated research overview,
not manuscript reproductions or evidence of a decipherment. No validated
decipherment, translation, real evaluation split, or registered decoding hypothesis
has been established.

The manifest [folio.json](folio.json) follows the 99Tokens folio format: portrait
pages, a cover reusing the overview plate, and three sections. Each page has alt
text, a caption, generation credit, an uncertainty note, status, and an update
date. The `current` status describes the plate's correspondence to this snapshot;
it does not mark the research as validated. The PNGs preserve the existing legible
artwork and each fits the 10 MB image limit.

## Evidence and snapshot

Claims were checked on 11 October 2026 against public main revision
[`a7298ab`](https://github.com/tobrien6/voynich-manuscript-research/tree/a7298abeb6cfe4253f9d30d8ffedc4e146518963).
Plates 1–4 reuse earlier generated artwork; the first plate retains its original
`fee42b7` source reference. Plate 5 was refreshed after PRs #28, #32, and #33
merged. Later open proposals are not presented as accepted results.

| Plate | Source and limits |
| --- | --- |
| [1. Project overview](01-project-overview.png) | [Project brief](../99TOKENS.md) and [evaluation protocol](../research/DECIPHERMENT_PROTOCOL.md). Records and exploratory results precede a tested reading. |
| [2. Evidence coverage](02-source-and-folio-map.png) | [Pilot inventory](../research/pilot/INVENTORY.md) and [Yale image index](../research/image-index/README.md). Ten selected sides, six catalog groups, 213 scan views, and 204 explicitly labeled numbered sides describe distinct units. |
| [3. Transcription choices](03-transcription-choices.png) | [Source decision](../research/transliteration/DECISION.md) and [comparators](../research/transliteration/COMPARATORS.md). The 5,214 shared present locations are paired representations, not independent experiments. |
| [4. Measured findings](04-measured-findings.png) | [Token/repetition report](../research/transliteration/BASELINES.md) and [recorded results](../research/transliteration/token_baselines.json). The 3,884-location P0 cohort differs from the all-kind coverage count in plate 3. The 272 versus 270.77 comparison is exploratory, with sensitivity to spacing choices. |
| [5. Next tests](05-open-work-and-roadmap.png) | [Prefix strata](../research/transliteration/PREFIX_STRATA.md), [pilot readiness](../research/pilot/TRANSCRIPTION_READINESS.md), [issue #13](https://github.com/tobrien6/voynich-manuscript-research/issues/13), and [evaluation protocol](../research/DECIPHERMENT_PROTOCOL.md). Seven exact metadata links still require image review; three selected targets remain unmapped. |

## Generation and provenance

The built-in `image_gen` tool generated the illustrations and performed the
roadmap update. Its underlying model identifier was not exposed. Manuscript-like
pages, glyph-like strokes, plants, diagrams, and token circles are newly generated
schematics; no Yale manuscript image or transcription excerpt is redistributed.
Source images remain linked through the research reports.

[provenance.json](provenance.json) records the original prompts, relevant edits,
the refreshed roadmap prompt, source revisions, source links, and SHA-256 values
of the delivered image files. The scientific counts come from repository reports;
the generated illustrations are explanatory and must not be used as measurements.

## Display and upkeep

The 99Tokens renderer reads `folio/folio.json` and its images from the repository's
default branch. A branch-only version cannot appear on the public project page.
The live [example manifest](https://99tokens.org/folio.example.json) and
[project folio API](https://99tokens.org/api/projects/59210176-9997-4f13-84fc-c46b43d165b3/folio)
were verified during this contribution. The API reports `missing` while these
files remain on a topic branch. After merging to the default branch, the
documented content cache can delay display by up to 15 minutes.

When accepted evidence changes, revise the affected plate and its provenance in
a focused PR. Set `status` to `outdated` and add a `note` naming the replacement
while a superseded plate is retained. Keep captions and alt text consistent with
the artwork. Recheck the current PR/issue state before editing a status plate.
