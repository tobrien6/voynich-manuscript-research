# Yale source and foliation audit

Inspected 2026-10-11 (America/New_York; 2026-10-12 UTC). Research question: which institutional statements and image identifiers can safely be carried into later transcription and provenance work?

This audit compares [Yale's current manuscript overview](https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript) (S001), its [older detailed catalog](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM) (S002), the [digital collection](https://collections.library.yale.edu/catalog/2002046) (S003), and the [IIIF manifest](https://collections.library.yale.edu/manifests/2002046) (S004). It records differences without resolving them by preference. The repository's source identifiers are used here; S004 is defined below.

## 1. John Dee ownership is disputed within Yale's sources

**Reported statements.** S002's provenance discussion favors Dee ownership and attributes the foliation to him. S001's provenance section reports serious doubt about that ownership.

**Result.** Record Dee ownership and foliation attribution as reported, contested claims. Neither page supplies enough evidence here for this audit to settle them. This difference does not establish which historical account is correct.

**Next test.** Trace the handwriting comparison credited to A. G. Watson in S002 and the scholarship underlying S001's doubt. Check whether they concern the same evidence. Keep separate evidence for ownership, foliation, and any proposed cipher author.

The [Dee documentary trail](DEE_EVIDENCE.md) now identifies a published numeral-attribution disagreement and different specimen-reference spellings in the catalog and a mediated quotation. Its [ledger](dee-evidence.json) preserves both representations, exact artifact identities and the still-uninspected original entry. It does not establish an owner, foliator or cipher author.

## 2. The catalog's terminal folio reference does not match the manifest

**Reported statement.** S002's Part VI description ends at 117v and associates that side with a short passage interpreted as a possible key.

**Metadata observation.** The saved S004 manifest has no explicit 117r or 117v reference. Its last numbered pair is 116r and 116v, followed by unnumbered binding/flyleaf views. The [116v image](https://collections.library.yale.edu/catalog/2002046?child_oid=1006277) has canvas ID `https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006277`.

**Direct image observation.** The 116v scan contains a short group of handwriting near the upper edge, small drawings at the left, and a largely empty page. It was inspected from [Yale's reduced image](https://collections.library.yale.edu/iiif/2/1006277/full/!1800,1800/0/default.jpg). No reading, language identification, or claim that it is a key follows from this observation.

**Result and limitation.** A reference discrepancy is established. A mapping from S002's 117v to S004's 116v remains unverified. Do not silently change a transcription's folio identifiers or count 117 as a missing physical leaf on this evidence.

**Next test.** Compare the catalog's foliation scheme with documented transcription conventions and collation research. Verify the correspondence of this passage before recording an alias between the identifiers.

The [terminal-folio intake and image pass](TERMINAL_FOLIOS.md) now distinguishes the 50 P0 records on current 116r from the single Lx record on 116v in ZL/RF and the absent IT/GC verso headers. It links the visible recto numeral and four apparent upper writing rows on the verso, keeping physical rows, source records, the unnumbered flyleaf and historical page counters separate. The legacy alias remains unresolved.

## 3. Image canvases and physical folios are different units

The script parses explicit number-plus-side references from canvas labels. It ignores unlabeled foldout panel numbers, preserves compound labels, and deduplicates numbered references. It does not inspect image content to reconstruct leaves.

| Measure from saved S004 | Result |
| --- | ---: |
| All canvases | 213 |
| Canvases with numbered folio-side references | 204 |
| Other canvases | 9 |
| Distinct folio numbers referenced | 102 |
| Distinct folio-side references | 204 |
| Canvases labeled as partial views | 15 |
| Canvases naming more than one folio side | 9 |
| Largest explicitly referenced folio number | 116 |

Partial and combined categories overlap. Equal totals for numbered canvases and distinct side references do not imply a one-to-one mapping. For example, 70v has two partial canvases; 85v and 86r share a combined canvas. Preserve canvas IDs and exact labels alongside transcription identifiers.

Within 1–116, numbers without explicit label references are **12, 59–64, 74, 91–92, 97–98, and 109–110**. These match S002's listed missing numbered leaves. This is a metadata cross-check, not independent confirmation of physical losses. The count of 102 referenced folio numbers also agrees numerically with S002's parchment extent; labels alone cannot establish collation or panel counts.

## Reproduce

Python 3 and curl are sufficient; the script has no external Python dependencies. It accepts a saved Presentation 3 manifest and performs no network access itself.

```sh
curl -fL https://collections.library.yale.edu/manifests/2002046 -o /tmp/voynich-manifest.json
python3 scripts/audit_yale_manifest.py /tmp/voynich-manifest.json \
  --retrieved-at 2026-10-12T02:00:00Z \
  --output /tmp/yale-manifest-audit.json
```

Use the actual UTC retrieval time for a new download. The recorded retrieval time is rounded to the minute. Compare the generated counts and labels with [the saved audit](manifest-audit.json). A changed SHA-256 indicates different input bytes; it does not by itself imply changed foliation. The source manifest is not committed because it repeats full catalog descriptions. [The frozen label extract](manifest-labels.json) retains every canvas's ID, type, and original language-map label, plus the manifest ID and type. It contains no image pixels or full catalog descriptions.

For an offline check, run the same command with `research/source-audit/manifest-labels.json` as its input. Every result except `manifest_sha256` should equal the saved audit when the retrieval-time argument is the same. The hash differs because the extract is a different file; the saved audit records the complete downloaded manifest's hash. A future live manifest may differ, so exact byte-for-byte reproduction of that hash requires the original downloaded bytes.

## S004 — Yale IIIF Presentation 3 manifest

- Institution: Yale University Library.
- URL: https://collections.library.yale.edu/manifests/2002046
- Retrieved: 2026-10-12T02:00:00Z (rounded to minute; October 11 locally).
- SHA-256: `317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`.
- Use: image/canvas identifiers, labels, sequence, and dimensions. Labels are supplied metadata rather than a new transcription.
- Limitation: mutable endpoint; labels can combine or subdivide sides and cannot establish physical collation by themselves.
- Rights: S003 provides public access with a rights notice requiring the user to consider applicable copyright and other terms. This contribution links images without redistributing manuscript scans and asserts no open image license.

The audit does not establish a decipherment, translation, historical owner, or revised physical foliation. Its contribution is a checkable record that prevents incompatible source claims and image identifiers from being treated as interchangeable facts.
