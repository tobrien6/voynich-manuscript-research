# Voynich Manuscript Research

## Research question

What can the Voynich manuscript's text, illustrations, and documented history establish when evidence is recorded consistently and competing explanations are tested reproducibly?

The manuscript is held by Yale's Beinecke Rare Book and Manuscript Library as MS 408. Yale describes its script as undeciphered. This project begins with an evidence base and testable questions; it has no preferred translation or decipherment.

## First milestone: a research baseline

1. **Build the source register.** Start with Yale's overview, manuscript catalog, and digitized folios. Record what each source supports, its limitations, and relevant rights or access conditions.
2. **Create a folio inventory.** Record folio identifiers, image links, visible text regions, illustration themes, and uncertainties for a small, explicitly selected pilot set.
3. **Review transcription choices.** Identify documented transcription systems and available editions. Compare treatment of ambiguous glyphs, spaces, line breaks, and missing material before selecting a dataset.
4. **Establish reproducible baselines.** Once a transcription is selected, measure glyph and token frequencies, token lengths, and line-position effects. Record preprocessing, sample sizes, code, and sensitivity to transcription decisions.
5. **Register hypotheses before testing them.** Specify the claim, evidence for and against it, a measurable prediction, comparison baselines, and a held-out evaluation set.

## First task

Produce a pilot inventory of 10 folios selected across the illustrated sections described in Yale's overview. Document the selection rule before collecting observations. For each folio, record the stable image link, section attribution and source, visible text layout, illustration description, and uncertain observations. Deliver the inventory with a short note explaining coverage and sampling limitations.

The [first pilot inventory](research/pilot/INVENTORY.md) now records ten selected target folio sides with Yale image identifiers, visible text layouts, illustrations, and uncertainties. Its [selection protocol](research/pilot/SAMPLING.md), [machine-readable records](research/pilot/inventory.json), and [source-check script](scripts/verify_pilot.py) make the contribution checkable. A canvas may include several foldout panels; these are retained within one record. Independent observation review and transcription/statistical analyses remain pending.

## Evidence standard

- Cite a source and folio for factual statements about the manuscript.
- Separate direct observations, reported claims, and interpretations.
- Keep an explicit record of contradictions and failed tests.
- Compare patterns against appropriate shuffled and language baselines before interpreting them.
- Test promising explanations on held-out folios and across transcription variants.
- Treat apparent matches as hypotheses until independently reproducible.

## Primary sources

- [Yale Beinecke overview](https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript)
- [Beinecke manuscript catalog: MS 408](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM)
- [Yale digital manuscript](https://collections.library.yale.edu/catalog/2002046)
- [Source register and access notes](research/SOURCES.md)

## Contribute

Open an issue for a focused question or propose a pull request with a documented observation, source correction, transcription comparison, or reproducible analysis. Include enough source detail and method description for another researcher to check the result.
