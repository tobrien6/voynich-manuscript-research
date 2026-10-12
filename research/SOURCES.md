# Primary source register

## S001 — Yale Beinecke manuscript overview

- URL: https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript
- Institution: Beinecke Rare Book and Manuscript Library, Yale University.
- Inspected: 2026-10-11 (America/New_York).
- Use: manuscript identity, descriptive overview, illustrated sections, provenance narrative, and links to further material.
- Limitation: an institutional overview is a starting point; trace individual historical or scientific claims to their supporting evidence before using them in an analysis. Dating statements require particular care because historical attributions and material dating address different questions.

## S002 — Beinecke catalog record for MS 408

- URL: https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM
- Institution: Beinecke Rare Book and Manuscript Library, Yale University.
- Author credited: Barbara A. Shailor; inspected 2026-10-11 (America/New_York).
- Use: physical description, foliation, and catalog context.
- Inspected: 2026-10-11; Parts I–VI supply the pilot's reported range attributions. These attributions are kept separate from image observations.
- Limitation: preserve the catalog's folio conventions and distinguish its descriptions from new observations. Check folio availability against the digital collection before defining a sample.

## S003 — Yale digital manuscript

- URL: https://collections.library.yale.edu/catalog/2002046
- Institution: Yale University Library.
- Use: manuscript images and stable collection reference for folio-level work.
- Inspected: 2026-10-11 (America/New_York); catalog page, viewer, and selected IIIF JPEGs.
- Access note: automated page retrieval returned HTTP 503 during setup and inventory work, while browser access and direct manifest/image endpoints succeeded. Image observations are documented in the [section-beginning inventory](pilot/INVENTORY.md), [section boundary survey](boundary-pilot/INVENTORY.md), and [standalone-recto boundary inventory](PILOT_INVENTORY.md). Individual catalog image links retain Yale's `child_oid` identifiers.
- Reuse: the record marks access as public but cautions that copyright, licenses, or other rights conditions may apply. Public access is not a blanket reuse license. The inventories store image links and original observations rather than redistributing scans.
- Citation: Cipher manuscript (Voynich manuscript). General Collection, Beinecke Rare Book and Manuscript Library, Yale University.

## S004 — Yale IIIF Presentation 3 manifest for MS 408

- URL: https://collections.library.yale.edu/manifests/2002046
- Institution/provider: Yale University Library.
- Retrieved: 2026-10-11 (America/New_York); 213 canvases.
- Version: IIIF Presentation 3; the manifest supplies no edition/version number.
- Retrieved JSON SHA-256: `317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`.
- Use: exact scan labels, image/canvas identifiers, pixel dimensions, image service URLs, and per-image catalog links for the [section-beginning inventory](pilot/inventory.json), [section boundary survey](boundary-pilot/selection.json), and [standalone-recto CSV](data/pilot-folios.csv).
- Limitations: canvas order is digitization order, not a count of physical leaves. Partial/composite scans and foldouts prevent a one-to-one mapping of canvases to folios or panels. A simple label such as `67r` can span more than one panel; labels do not define transcription boundaries. The live manifest and image derivatives may change. A checksum identifies inspected bytes rather than an immutable edition.
- Reuse: the manifest repeats S003's rights caution and credits Yale University Library as provider; it does not supply a blanket image reuse license.

## S005 — Zandbergen's foliation description

- Author: René Zandbergen; [Description of the Voynich MS](https://voynich.nu/descr.html), Foliation, Theodore Petersen's numbering, and note 17.
- Inspected: 2026-10-11 (America/New_York); web text and browser display.
- Use: separate source-numbering conventions in the [terminal-reference check](folio-aliases/SOURCE_CHECK.md).
- Limitation: does not explicitly verify the legacy Yale 117v/current 116v correspondence; reported historical counter inconsistencies are not physical folio offsets.
- Reuse: link and selected paraphrase only; no whole-page copy is redistributed.

## S006 — Hosted Currier Table A

- Credit: Prescott Currier, *Table A: Voynich MS Pagination*, digital table hosted by René Zandbergen at [this PDF endpoint](https://voynich.nu/extra/img/curr_tabA.pdf).
- Inspected: 2026-10-11 (America/New_York); one page, rendered visually and checked against extracted text.
- Retrieved PDF: 9,421 bytes; SHA-256 `3be46a0016a61e17d27e6d9d7086236c1a363f3c09927535ce9de525fdca54d3`.
- Use: column legend and folio 116 row in the [source-numbering observations](folio-aliases/source-numbering-observations.json).
- Limitation: fingerprint identifies the hosted digital representation; it does not authenticate an original print or establish a Yale canvas mapping.
- Reuse: source PDF/render kept local; only a citation, fingerprint, and selected identifier facts are recorded. No open PDF/image reuse license is asserted.

## S007 — D'Imperio report preserved by GovInfo

- Author: M. E. D'Imperio; *The Voynich Manuscript: An Elegant Enigma*, 1978. Rendered cover credits the National Security Agency/Central Security Service.
- Sources: [GovInfo record](https://www.govinfo.gov/app/details/GOVPUB-D-PURL-gpo58694) and [preserved PDF](https://www.govinfo.gov/content/pkg/GOVPUB-D-PURL-gpo58694/pdf/GOVPUB-D-PURL-gpo58694.pdf).
- Inspected: 2026-10-12 (America/New_York); cover and PDF pages 4, 31, 32, 38, 81 and 103 rendered in full and visually checked.
- Representation: 141 PDF pages, 32,892,602 bytes; SHA-256 `e357921308c1ba43e327378a47bec389f755f843b3ad26ec11bb48cc3d6e066a`.
- Use and limits: selected terminal-reference locators and reproduction credits in the [source follow-up](folio-aliases/ENIGMA_CONTEXT.md); no accepted historical reading, original-source inspection, Yale alias or complete-text absence claim.
- Reuse: PDF, extracted text and renders remain local; only brief observations, citations and fingerprints are published.

## Recording future sources

The [historical interlinear intake](historical/README.md) records a recovered
publisher-hosted 1.6e6 candidate, its original permission terms, exact archive and
member identity, and a native-envelope audit. It does not establish equality to
the input used by published studies.

Assign each source a stable identifier. Record its author or institution, title, URL or persistent identifier, version and access date when inspected, relevant folios or pages, the specific claim it supports, limitations, and reuse terms when data or images are involved.

The [reference variant register](transcriptions/SOURCES.md) uses `TR` identifiers for edition publishers, format documentation, reuse terms, and the GC/RF extension to the accepted ZL/IT corpus. Its records distinguish source claims from the local aggregate audit.

The [published-methods register](literature/README.md) uses `L` identifiers for a
selective set of primary research papers. Its [records](literature/methods.json)
pin inspected publication artifacts and distinguish reported measurements and
nulls from unresolved historical corpus identity. It does not report replicated
results or a decipherment.
