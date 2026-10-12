# Explicit foliation alias decisions

A transcription reference must retain its numbering system. This registry
records proposed aliases separately from reviewed mappings so a plausible
correspondence cannot silently become an input to decipherment or translation.
It complements the Yale canvas index and direct folio lookup; it does not
replace either one.

## Current finding: legacy 117v remains unresolved

The [legacy Yale MS 408 catalog](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM)
attributes a short presumed key to 117v. The
[current Yale manifest](https://collections.library.yale.edu/manifests/2002046)
labels the final numbered verso 116v, image 1006277, with no exact 117v entry.
[The linked image](https://collections.library.yale.edu/catalog/2002046?child_oid=1006277)
shows short writing near the top and small figures at the left. These are
source statements and a direct observation; the candidate alias remains an
interpretation needing review.

Two historical research records reinforce the 116v convention while exposing
another numbering distinction:

| Record inspected 2026-10-11 | Identification in that source | What it supports |
| --- | --- | --- |
| [Jim Reeds, *A Provisional Checklist of Voynich MS pages*, 11 Sep 1995](https://www.ic.unicamp.br/~stolfi/voynich/mirror/gillogly/checklist), format explanation and final entry | 116v; Petersen-column page number 235 | A historical 116v designation for final short-text material; page numbers require the source scheme. |
| [Jorge Stolfi's page notes](https://ic.unicamp.br/~stolfi/voynich/Notes/040/html/f116v.htm), Identification and Description | f116v; p234 in Stolfi's scheme | Another explicit final-page identification as 116v, with a different page-number convention. |

Neither explicitly equates the legacy catalog's 117v with current 116v. Do not
collapse page 234 and page 235 without their schemes, declare a missing leaf
from an absent label, or infer a global folio offset. The proposed resolution
and remaining checks are tracked in [issue #13](https://github.com/tobrien6/voynich-manuscript-research/issues/13).
No glyph reading, cipher key, dating conclusion, or translation is established.

The [source-numbering follow-up](SOURCE_CHECK.md) inspects the hosted Currier
Table A, whose folio 116 row has page fields 235 and 236. It retains Reeds's
Petersen counter and Stolfi's attributed page label separately, with a PDF
fingerprint and explicit limits. These counter differences do not verify the
legacy Yale alias or authorize a global folio shift.

The [editorial-marker follow-up](CATALOG_EDITORIAL_FLAG.md) locates a Spanish
publisher file and an English licensed snippet that retain the catalog label
with `[sic]`. These bounded observations supply no explicit replacement or
catalog-to-canvas correspondence. The registry and blocked lookup remain unchanged.

## Registry and verification gate

[decisions.json](decisions.json) is the versioned registry. Each source key is
the pair `source_scheme` and **verbatim** `source_label`. The checker performs
no prefix stripping, whitespace trimming, numeric shifting, or panel inference.
Only explicitly registered decisions are returned.

| Field | Purpose |
| --- | --- |
| `decision_id` | Stable local identifier; must be unique. |
| `source_scheme`, `source_label` | Preserve the original reference and its numbering convention. |
| `status` | `unresolved`, `verified`, or `rejected`. |
| `candidate_target` | Optional possible label and canvas identifiers; never authorizes a mapping. |
| `verified_target` | Required only for a verified decision: exact Yale label, canvas identifiers, manifest SHA-256, and `mapping_scope: canvas_reference_only`. |
| `evidence` | Source URLs, precise locators, and the limited statement each source supports. |
| `review` | Required for verification: reviewer, date, finding, and citations to recorded evidence. |
| `rationale`, `recorded_on` | Explain the decision and preserve its date. |

A `verified` record is a reviewer's documented attestation, not automated proof
of historical identity. The checker validates its required evidence fields and
exact target labels against the supplied canvas index and manifest checksum.
It does not fetch sources, authenticate reviewers, decide whether the evidence
is persuasive, or establish a panel/line region. Independent scholarly review
remains necessary before relying on an attestation in research.

For unresolved and rejected entries, `verified_target` and `review` must be
null. This prevents a downstream reader from mistaking a candidate target for
a verified mapping. Unknown fields/statuses, duplicate decisions, wrong target
labels, and stale verification checksums are errors.

## Run offline

From the repository root, using Python's standard library:

```sh
python3 scripts/check_folio_aliases.py
python3 scripts/check_folio_aliases.py --lookup yale_legacy_ms408_catalog 117v
python3 -m unittest discover -s tests -p 'test_folio_aliases.py' -v
```

The first command validates the registry and exits 0. The second prints the
unresolved candidate with `mapping_allowed: false` and `target: null`, then
exits **1**. Do not pipe or interpret the candidate as an approved mapping.
An unregistered reference also exits 1. Invalid input exits **2**.

To check candidate identifiers against the existing Yale index (introduced in
[PR #8](https://github.com/tobrien6/voynich-manuscript-research/pull/8)):

```sh
python3 scripts/check_folio_aliases.py \
  --canvas-index research/image-index/canvases.csv \
  --index-audit research/image-index/audit.json
```

Both index arguments must be supplied together. A verified decision cannot be
validated or looked up without them. The JSON report includes the registry
and canvas CSV checksums, the manifest checksum, and whether targets were
checked against the index. The audit checksum identifies the manifest used to
generate the supplied index; use the index generator's own reproduction check
to verify its relationship to a downloaded source response.

The public `lookup(registry, scheme, source_label, index=None,
manifest_sha256=None)` helper always validates before returning a mapping.
Its result only concerns source references. Multiple canvas identifiers remain
multiple views; neither one nor several identifiers proves a full folio surface
or independent text samples.

## Next test

Review an explicit source for the legacy 117v reference or compare a documented
facsimile foliation against the final recto and verso. Record the evidence for
or against the proposed alias without overwriting the source labels. If a
decision becomes verified, commit the review and target manifest checksum
together. If the target snapshot changes, repeat review before reusing it.
Images and complete historical source texts are linked rather than republished.

The [Newbold original-source follow-up](NEWBOLD_TERMINAL_SOURCE.md) locates the
credited early reading, the later chapter's editorial provenance and the longer
transcript on printed p. 109, with separate plate/PDF locators. It retains the
historical final-number claim and all proposed readings as documentary context;
the unresolved registry gate and source/statistical inputs remain unchanged.

The [original 1921 lecture follow-up](NEWBOLD_1921_LECTURE.md) subsequently
inspects the complete credited pp. 461–474 and selected earlier context. It
retains the printed final number 116, the Part V folio ranges and a concrete
OCR-added `V` separately from a source designation. S009's original exposure
ledger is preserved; the legacy alias and historical readings remain unresolved.
