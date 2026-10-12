# Organize manuscript coverage

Open the [folio-side status table](STATUS.md) to see the documented work on each
labeled side, its Yale images, transcription identifiers, evidence, tasks and
remaining gaps. [coverage.json](coverage.json) contains the same ledger for
future interfaces. The generator uses Python 3.10+ and the standard library,
reads repository records and makes no network requests.

## Read the counts correctly

The denominator is the **204 distinct folio sides explicitly labeled in the
pinned Yale index**. Its 213 image canvases include nine unnumbered views, and
the paired transcription audit has 227 page/panel identifiers. A foldout can
have several panel identifiers and a scan can show several sides. These units
must not be counted interchangeably or treated as independent samples.

The tracker imports all three initial inventories and a curated set of accepted
pixel-review records, preserving overlap. Whole-corpus statistical studies are
linked through the [transcription metadata audit](../folio-alignment/IMAGE_COVERAGE.md)
and [token baselines](../transliteration/BASELINES.md); their processing does not
complete visual or glyph review on every side. Shared-carrier dependency groups,
the nine unnumbered views and index gaps remain in the generated report.

The stages are separate:

| Stage | What a complete record would claim |
| --- | --- |
| Visual observation | An explicitly scoped whole-side visual inventory, with remaining uncertainty recorded. |
| Image/text alignment | Whole-side region/locus/glyph review with a documented crosswalk and gaps, rather than only selected anchors. |
| Independent review | A whole-side review with evidence and an explicit statement establishing independence. A second nonblind AI comparison alone does not establish this. |
| Validated translation | A source-linked whole-side translation supported under the [decipherment protocol](../DECIPHERMENT_PROTOCOL.md). |

`partial` preserves useful observations without declaring a whole side finished.
`not_recorded` means the imported records contain no declaration for that stage;
it is not proof that nobody inspected the material. Complete image/text review
requires both whole-side alignment and whole-side independent review records.
Completion is a documented claim: software validates record structure and
source identity, not scientific correctness, independence or decipherment.

The initial registry declares **no complete stages**. Its source images,
transcription records and provisional observations retain their existing limits.
The registry is deliberately explicit, not an exhaustive automatic classification
of every research document. Add omitted studies with their real scope.

## Assign work and record results

Edit [tasks.json](tasks.json) to claim a defined task. Each entry needs a unique
`id`, indexed `folio_sides`, a `stage`, a public `owner` identifier or `null`,
`status`, a concrete `next_action`, a list of `blockers`, and existing
repository-relative `references`. Status is `planned`, `in_progress`, `blocked`,
`done` or `cancelled`. An in-progress task requires an owner; a blocked task
requires a stated blocker. Owners may use a public chat/task identifier or
GitHub username. Keep private identities, emails, credentials and local paths out.

The four initial tasks are **unassigned planning suggestions**, not active agent
jobs. Chat activity and stopped contributors are not imported as assignments.
When taking work, check the shared-carrier groups, existing tasks, current issues
and PRs to avoid duplicate work and accidental reuse of exposed material.

Edit [evidence.json](evidence.json) when there is a result to record. An entry
contains `id`, `folio_sides`, `stage`, `status` (`partial` or `complete`),
`scope` (`surface_overview`, `selected_regions` or `whole_folio`), a precise
`summary`, and nonempty repository-relative `references`. References must exist
inside the repository and must not point to generated tracker outputs. A
complete entry must use `whole_folio`; any independent-review entry also needs
an `independence_statement` that explains the evidence and limits.

For example, after adding an actual region-review record:

```json
{
  "id": "example-region-review",
  "folio_sides": ["67r"],
  "stage": "image_text_alignment",
  "status": "partial",
  "scope": "selected_regions",
  "summary": "State the inspected regions, outcome and remaining uncertainty.",
  "references": ["research/panel-regions/f67r-upper-row-inspection.json"]
}
```

Marking a task `done` never changes scientific-stage completion. A result can
finish a bounded task and leave the folio's evidence partial. Conversely, an
evidence entry does not certify that a named agent is currently working.

## Regenerate and check

From the repository root:

```sh
python3 scripts/build_manuscript_coverage.py --write
python3 scripts/build_manuscript_coverage.py --check
python3 -m unittest tests.test_manuscript_coverage -v
```

Commit changes to the registries together with both regenerated outputs.
`--check` returns a failing exit status for stale or missing outputs. The
generator records SHA-256 hashes of every imported input and evidence reference,
keeps empty transcription headers, and counts source identifiers once even when
they refer to a shared carrier. It never infers a historical foliation alias.
It writes only `coverage.json` and `STATUS.md` in this directory, replacing files
atomically rather than following existing output symlinks or modifying input
files. It does not modify any frozen scientific script or source record.

Run the stale-output check when reviewing a PR that updates tracked evidence.
Check the declared scope and source support independently; a passing generator
check cannot turn a provisional mapping into an accepted manuscript reading.
