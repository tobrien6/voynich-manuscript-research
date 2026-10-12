# Evaluation split records and validation

A decoding rule can appear successful if closely related material occurs in
both development and evaluation. The [decipherment protocol](../DECIPHERMENT_PROTOCOL.md)
therefore requires a committed split before fitting, complete folio units,
dependency grouping, and an explicit record of prior exposure.

This contribution supplies a record format and an offline checker. It does
not choose real held-out folios or certify that any manuscript material is
unseen. Transcription selection and the folio/image crosswalk are separate
inputs. Preserve their versioned identifiers and unresolved mappings.

The CLI rejects repeated object member names at every depth, even when their
values agree or their names use different JSON escapes. A record containing
both `"state": "unknown"` and `"state": "none_reported"` must not pass a
freeze check by silently keeping only the latter declaration. This failure
was reproduced on a synthetic record; no actual manuscript split was changed.
The loader also rejects literal `NaN`, `Infinity`, and `-Infinity`, which are
outside JSON's numeric grammar. [RFC 8259 sections 4 and 6](https://www.rfc-editor.org/rfc/rfc8259)
describe the object-name interoperability problem and numeric grammar.

Python callers reading serialized records should use
`load_split_json(text)` before `validate(...)`. The dictionary validation API
cannot recover duplicate declarations discarded by another decoder. These
parsing checks preserve unambiguous declarations; they do not independently
verify exposure, mappings, source identity, or pre-fit Git history.

## Records

`schema_version` is `1`. Required top-level fields:

| Field | Meaning |
| --- | --- |
| `split_id`, `candidate_version` | Versioned identifiers for the split and candidate it governs. |
| `status` | `draft` or `frozen`. Drafts may retain unresolved evaluation exposure. |
| `evaluation_claim` | `excluded_from_fitting` or the stronger `unseen_material`. |
| `created_at`, `frozen_at`, `fit_started_at` | ISO timestamps with timezones. Draft freeze and not-yet-started fitting use JSON `null`. |
| `input` | Object with `edition`, `source`, and lowercase 64-character `sha256`; pin the exact bytes used. |
| `expected_counts` | Positive integer `development` and `evaluation` unit counts. Use 8 and 2 for the project's provisional ten-unit pilot. |
| `units` | The sampling/dependency units described below. |

Each unit contains `unit_id`, `partition`, `folio_ids`, `canvas_ids`,
`dependency_groups`, `source_refs`, and `prior_exposure`. `folio_ids` are
canonical physical leaf numbers such as `67`, without recto/verso/panel
suffixes. All selected sides/panels of one physical leaf belong in one unit.
For a composite covering folios 85 and 86, list both numbers. These identifiers
must come from reviewed mappings; the checker does not infer them from a
canvas label or resolve legacy foliation aliases.

Counts refer to grouped sampling units. A composite unit can cover several
physical leaves, so an eight/two unit count does not by itself establish the
project's requested folio coverage. Explain that coverage in the candidate record.

`canvas_ids` can be empty for material without a confirmed image mapping.
That absence must be explained in `source_refs` and the research record; it
does not establish that the mapping is safe for analysis. Reuse of one canvas
in different units is rejected. `dependency_groups` is a nonempty list of
researcher-defined identifiers for related material, such as a foldout or
repeated passage family. Groups may span several units within one partition
but must not cross partitions. The checker cannot discover missing dependencies.

`prior_exposure` contains:

- `state`: `known`, `none_reported`, or `unknown`.
- `note`: scope and kind of exposure, including image inspection,
  transcription inspection, previous candidate work, or unresolved history.
- `declared_by`, `recorded_at`: who made the declaration and when.
- `used_for_development`: `true`, `false`, or `null` if unresolved.

Do not turn a lack of records into `none_reported`. That state requires an
explicit declaration; it still does not prove absence of exposure. Material
used in candidate development cannot be evaluation material. Known exposure
can coexist with `excluded_from_fitting` only when the declaration says it
was not used for development. A split claiming `unseen_material` rejects
known exposure. Unknown evaluation exposure or development use blocks freezing.
All visually inspected pilot images must disclose that exposure; this format
does not relabel them as unseen.

## Before fitting

1. Supply the pinned transcription input, resolve sampling/dependency units,
   and record exposure. Keep unavailable or disputed mappings explicit.
2. Validate the draft. Choose the scope of the evaluation claim before viewing
   material for candidate development.
3. Resolve unknown evaluation exposure, set `status` to `frozen`, and record
   `frozen_at`. Leave `fit_started_at` null until fitting actually starts.
4. Run the frozen check with input bytes and commit the split, input identity,
   and candidate rules before fitting. Record the commit in the candidate record.
5. When fitting begins, record its timestamp in the run record. It must be
   strictly later than the freeze. Changes to rules, data, or the split require
   a new version and an honest account of newly exposed evaluation material.

```sh
python3 scripts/validate_evaluation_split.py PATH_TO_SPLIT.json
python3 scripts/validate_evaluation_split.py PATH_TO_SPLIT.json \
  --input PATH_TO_PINNED_TRANSCRIPTION --require-frozen
python3 -m unittest discover -s tests -p 'test_evaluation_split.py'
```

The checker rejects duplicate units, multiple units for a physical leaf or
canvas, cross-partition dependency groups, mismatched declared counts,
contradictory/unknown evaluation exposure at freeze, unpinned or changed input
bytes, and inconsistent timestamp order. Its timestamps are declarations,
not independently verified Git history. Reviewers must check the actual
pre-fit commit and run records. A passing check cannot prove correct foliation,
complete grouping, an honest exposure declaration, or a valid decipherment.

Tests use entirely synthetic material, including deliberately leaking related
folios/panels, a changed input, and exposure recorded after a freeze. They
contain no actual manuscript split or claim of untouched folios.

The [synthetic example](examples/synthetic-split.json) is a runnable record with
two development units and one evaluation unit; it is not the project's real
eight/two split. Its [input](examples/synthetic-input.txt) contains no manuscript
text. Run it with:

```sh
python3 scripts/validate_evaluation_split.py \
  research/evaluation/examples/synthetic-split.json \
  --input research/evaluation/examples/synthetic-input.txt --require-frozen
```

To integrate a folio-join report, retain all matched `canvas_uri` values in
`canvas_ids` and preserve its original labels and partial/combined flags in
the associated source record. Derive physical `folio_ids` only from reviewed
folio-side mappings. Unmatched or unsupported identifiers remain unresolved;
do not infer an alias or a text-region boundary from a shared canvas.

The [whole-corpus image-reference audit](../folio-alignment/IMAGE_COVERAGE.md)
adds a stricter optional gate for the pinned ZL3b/IT2a naming convention and
Yale index. It recomputes transitive dependencies across explicit shared scans,
requires the derived group IDs and all indexed canvas references for selected
leaves, and requires selected leaves in one image component to share one unit.
Run its `--split` check in addition to this validator's input/freeze check.
Both CLIs use the same strict split decoder: repeated object members and
non-JSON numeric constants fail before interpreting declarations, even if
ordinary JSON decoding would leave a structurally valid final value. Invalid
split input cannot produce a dependency PASS or replace an output report.
Its coarse side references do not resolve image regions or substitute for a
reviewed physical mapping. Preserve prior exposure and any unresolved panel
localization in the candidate record.
