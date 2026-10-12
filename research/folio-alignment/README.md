# Align folio references to Yale image canvases

Question: can a transcription's folio-side references be joined to image metadata without dropping partial scans or inventing aliases?

This utility supports source-linked decoding and translation by preserving the image references needed to inspect a transcription. It joins explicit folio-side identifiers against labels from a saved [Yale IIIF Presentation 3 manifest](https://collections.library.yale.edu/manifests/2002046), using the shared `index_yale_manifest.build(raw_bytes, access_date)` generator. It adds request validation and incomplete-join handling to the existing image index; it does not parse transcription glyphs or establish equivalence between foliation conventions.

## Behavior

- Keep the original requested identifier. Normalize only surrounding whitespace, an optional `f` prefix, and the case of `r` or `v`.
- Return **every** canvas explicitly naming that folio side, in manifest order, with its original label, stable canvas URI, and supplied image URLs.
- Mark partial and combined views. A combined image stays the same image when returned for either of its named sides; the script does not locate panel boundaries or crop it.
- Record `label_unmatched` for a valid identifier with no explicit label match. An unmatched label does not imply a missing physical leaf.
- Record `unsupported_identifier` for panel/line suffixes or other forms. For example, `f67r1` is not silently reduced to `67r`; a documented transcription-specific mapping is required first.
- Write the report, then exit with status 2 if any identifier is unmatched or unsupported. `--allow-incomplete` permits successful exit for an explicitly exploratory audit while retaining those statuses.
- Optionally require a source-file SHA-256 before processing. The output always records its input hash.

## Run

From the repository root, using Python 3 and a saved manifest:

```sh
curl -fL https://collections.library.yale.edu/manifests/2002046 -o /tmp/voynich-alignment-manifest.json
python3 scripts/align_folio_canvases.py /tmp/voynich-alignment-manifest.json \
  f70v 85r 86v 85v 86r 116v 117v f67r1 \
  --access-date 2026-10-11 \
  --output /tmp/folio-alignment.json
```

The last two requests are deliberate negative controls. The command writes a report and returns status 2. Remove the controls when joining an actual accepted sample, or explicitly use `--allow-incomplete` to audit unresolved inputs. Do not suppress failed joins before defining the sample for a statistical test.

For a version-locked repeat of the recorded input, add:

```sh
--expected-sha256 317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309
```

Use the actual retrieval date of a new download. The live manifest can change. If its digest differs, inspect the new labels and record a new input version; a hash change alone does not show that any foliation changed.

## Recorded result

The [example report](example-alignment.json) uses the manifest retrieved on October 11, 2026 (America/New_York; October 12 UTC). It preserves the following metadata results:

| Requested identifier | Status | Matching canvases | Observation about labels |
| --- | --- | ---: | --- |
| `f70v` | matched | 2 | Both partial views are retained. |
| `85r` | matched | 2 | One partial view also names 86v. |
| `86v` | matched | 2 | One partial view also names 85r. |
| `85v` | matched | 1 | A combined foldout also names 86r. |
| `86r` | matched | 1 | Same combined foldout as 85v. |
| `116v` | matched | 1 | Direct match to the terminal numbered verso label. |
| `117v` | label_unmatched | 0 | No folio alias is supplied. |
| `f67r1` | unsupported_identifier | 0 | No convention-specific panel mapping is supplied. |

The 117v control relates to the unresolved [catalog/digital foliation issue](https://github.com/tobrien6/voynich-manuscript-research/issues/13). It tests safe behavior in the presence of conflicting labels; it does not resolve the conflict.

## Limits and next test

Matching references establish metadata links, not the identity of a physical leaf or the location of a text region within a foldout. Exact compound labels must remain attached to downstream records. Image URLs come from the shared index's checked painting annotations. The generator requires the recorded Yale object, its `none` language-map convention, and one unambiguous image per canvas; changed arrangements require review. The join inherits those source-validation rules.

The Python interface is `align(raw_manifest_bytes, requested_identifiers, access_date)`. Its report includes source URL/hash/date, the original and canonical request identifiers, statuses, and every indexed canvas match. From the repository root, use `from scripts.align_folio_canvases import align`. The CLI can run either as the script above or as `python3 -m scripts.align_folio_canvases`. It applies no historical aliases; a provenance-bearing crosswalk can consume the conservative matches separately.

Cross-component checks exercise the accepted conservative adapter, direct resolver, and shuffle controls together. They retain original locus identifiers and all partial/shared views, distinguish unsupported panels from unmatched labels, and check both control scopes. The adapter's `tokens: null` means an excluded **whole locus**; it cannot be passed as a token array or reinterpreted as one excluded position. The controller's `null` entries **inside** a token array are explicitly declared fixed slots. The integration fixtures are synthetic and establish API behavior, not reviewed image/text identity or a complete corpus mapping.

Run `python3 -m unittest discover -s scripts -p 'test_align_folio_canvases.py'` to check partial/combined mappings, absent aliases, panel-suffix rejection, shared-index image references, CLI failure behavior, and digest verification.

The [whole-corpus image-reference audit](IMAGE_COVERAGE.md) now documents the
pinned ZL3b/IT2a naming convention, retains coarse side references separately
from strict lookups and unresolved panel regions, and derives transitive
shared-scan dependency groups. It leaves this utility's suffix rejection intact.
The next step is a reviewed image/text crosswalk with explicit panel regions.
Record historical aliases only with cited supporting evidence, and keep
incomplete or unsupported joins visible before defining statistical samples.

Images are linked; this report contains metadata rather than redistributed scans. No decipherment or translation is established by an identifier join.
