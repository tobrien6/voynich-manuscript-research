#!/usr/bin/env python3
"""Build an offline folio-side work ledger from committed evidence."""

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = Path("research/coverage")
OUTPUTS = (DIRECTORY / "coverage.json", DIRECTORY / "STATUS.md")
STAGES = ("visual_observation", "image_text_alignment", "independent_review",
          "validated_translation")
BASE_INPUTS = (
    "research/image-index/audit.json",
    "research/image-index/canvases.csv",
    "research/image-index/folio-sides.csv",
    "research/folio-alignment/transcription-image-coverage.json",
    "research/pilot/inventory.json",
    "research/boundary-pilot/selection.json",
    "research/boundary-pilot/INVENTORY.md",
    "research/data/pilot-folios.csv",
    "research/PILOT_INVENTORY.md",
    "research/coverage/evidence.json",
    "research/coverage/tasks.json",
)


def side_key(side):
    match = re.fullmatch(r"([1-9][0-9]*)([rv])", side)
    if not match:
        raise ValueError(f"Invalid folio side: {side!r}")
    return int(match[1]), match[2]


def build(root=ROOT):
    inputs = {}

    def read(path):
        candidate = root / path
        if Path(path).is_absolute() or not candidate.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Evidence must stay inside the repository: {path}")
        if candidate.resolve() in {(root / output).resolve() for output in OUTPUTS}:
            raise ValueError("Generated outputs cannot be evidence inputs")
        raw = candidate.read_bytes()
        inputs[path] = hashlib.sha256(raw).hexdigest()
        return raw.decode("utf-8")

    def load(path):
        return json.loads(read(path))

    def table(path):
        return list(csv.DictReader(read(path).splitlines()))

    for path in BASE_INPUTS:
        read(path)
    audit = load(BASE_INPUTS[0])
    canvases = table(BASE_INPUTS[1])
    indexed_sides = table(BASE_INPUTS[2])
    alignment = load(BASE_INPUTS[3])
    if len(canvases) != audit["canvas_count"] or len(indexed_sides) != audit["explicit_folio_side_count"]:
        raise ValueError("Image index counts differ from its audit")
    if alignment["image_index"]["manifest_sha256"] != audit["manifest_sha256"]:
        raise ValueError("Image index and transcription report use different manifests")
    if len(alignment["pages"]) != alignment["distinct_page_ids"]:
        raise ValueError("Transcription page count differs from its report")

    rows = {}
    for indexed in indexed_sides:
        side = indexed["folio_side"]
        side_key(side)
        if side in rows:
            raise ValueError(f"Duplicate indexed side: {side}")
        images = [c for c in canvases if side in c["explicit_folio_sides"].split(";")]
        if len(images) != int(indexed["canvas_count"]):
            raise ValueError(f"Canvas count differs for {side}")
        rows[side] = {
            "folio_side": side,
            "canvases": [{k: c[k] for k in ("image_oid", "yale_label", "catalog_image_url")}
                         for c in images],
            "transcription_page_ids": [],
            "unresolved_panel_page_ids": [],
            "dependency_groups": [],
            "stages": {stage: "not_recorded" for stage in STAGES},
            "evidence_ids": [],
            "task_ids": [],
        }

    pages = []
    seen_pages = set()
    for page in alignment["pages"]:
        page_id = page["page_id"]
        if page_id in seen_pages:
            raise ValueError(f"Duplicate transcription page: {page_id}")
        seen_pages.add(page_id)
        sides = page["reference"]["folio_sides"]
        pages.append({"page_id": page_id, "folio_sides": sides,
                      "source_counts": page["source_counts"],
                      "panel_region_status": page["panel_region_status"]})
        for side in sides:
            if side not in rows:
                raise ValueError(f"Transcription reference has unknown side: {side}")
            row = rows[side]
            row["transcription_page_ids"].append(page_id)
            if page["panel_region_status"] == "unresolved":
                row["unresolved_panel_page_ids"].append(page_id)
            if page["dependency_group"] not in row["dependency_groups"]:
                row["dependency_groups"].append(page["dependency_group"])

    evidence = []
    evidence_ids = set()

    def add(entry):
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"]:
            raise ValueError("Evidence requires a nonempty id")
        if entry["id"] in evidence_ids:
            raise ValueError(f"Duplicate evidence id: {entry['id']}")
        stage, status = entry.get("stage"), entry.get("status")
        if stage not in STAGES or status not in ("partial", "complete"):
            raise ValueError(f"Invalid evidence stage/status: {entry['id']}")
        sides, refs = entry.get("folio_sides"), entry.get("references")
        if not isinstance(sides, list) or not sides or len(sides) != len(set(sides)):
            raise ValueError("Evidence needs distinct folio sides")
        if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and ref for ref in refs):
            raise ValueError("Evidence needs repository references")
        if not isinstance(entry.get("summary"), str) or not entry["summary"].strip():
            raise ValueError("Evidence needs a scope summary")
        if entry.get("scope") not in ("surface_overview", "selected_regions", "whole_folio"):
            raise ValueError("Evidence needs an explicit scope")
        if status == "complete" and entry["scope"] != "whole_folio":
            raise ValueError("Partial/overview evidence cannot complete a folio")
        if stage == "independent_review" and not entry.get("independence_statement", "").strip():
            raise ValueError("Independent review requires an independence statement")
        for ref in refs:
            read(ref)
        for side in sides:
            if side not in rows:
                raise ValueError(f"Evidence has unknown side: {side}")
            row = rows[side]
            row["evidence_ids"].append(entry["id"])
            if row["stages"][stage] != "complete":
                row["stages"][stage] = status
        evidence_ids.add(entry["id"])
        evidence.append(entry)

    def inventory_entry(identifier, side, canvas_uri, reference, summary):
        sides = [side] if isinstance(side, str) else side
        images = [c for c in canvases if c["canvas_uri"] == canvas_uri]
        if len(images) != 1 or not set(sides).issubset(images[0]["explicit_folio_sides"].split(";")):
            raise ValueError(f"Inventory target/canvas mismatch: {identifier}")
        add({"id": identifier, "folio_sides": sides, "stage": "visual_observation",
             "status": "partial", "scope": "surface_overview", "summary": summary,
             "references": [reference]})

    for record in load(BASE_INPUTS[4])["records"]:
        inventory_entry("pilot-" + record["target"], record["target"], record["canvas_uri"],
                        BASE_INPUTS[4], "Pilot overview; no full glyph or region verification.")
    for record in load(BASE_INPUTS[5])["entries"]:
        # The 86r target is explicitly named "86r with 85v" in this survey.
        side = record["target_folio"].split()[0]
        inventory_entry("boundary-" + side, side, record["canvas_id"], BASE_INPUTS[6],
                        "Boundary survey overview; shared canvas context is not a separate sample.")
    for record in table(BASE_INPUTS[7]):
        matches = [c for c in canvases if c["canvas_uri"] == record["canvas_id"]]
        if len(matches) != 1:
            raise ValueError("Standalone inventory has an unknown canvas")
        sides = matches[0]["explicit_folio_sides"].split(";")
        inventory_entry("standalone-" + record["image_oid"], sides,
                        record["canvas_id"], BASE_INPUTS[8],
                        "Standalone-recto inventory overview; shared foldout context is one observation, not independent side reviews.")
    registry = load(BASE_INPUTS[9])
    if registry.get("schema_version") != 1:
        raise ValueError("Unsupported evidence schema")
    for entry in registry["entries"]:
        add(entry)

    task_registry = load(BASE_INPUTS[10])
    if task_registry.get("schema_version") != 1:
        raise ValueError("Unsupported task schema")
    tasks = task_registry["tasks"]
    task_ids = set()
    for task in tasks:
        identifier = task.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in task_ids:
            raise ValueError("Task ids must be nonempty and unique")
        task_ids.add(identifier)
        if task.get("stage") not in STAGES or task.get("status") not in (
                "planned", "in_progress", "blocked", "done", "cancelled"):
            raise ValueError(f"Invalid task stage/status: {identifier}")
        owner = task.get("owner")
        if owner is not None and (not isinstance(owner, str) or not owner.strip()):
            raise ValueError("Task owner must be null or a public identifier")
        if task["status"] == "in_progress" and owner is None:
            raise ValueError("An in-progress task needs an owner")
        if not isinstance(task.get("next_action"), str) or not task["next_action"].strip():
            raise ValueError("Tasks need a next action")
        if not isinstance(task.get("blockers"), list) or not all(
                isinstance(item, str) and item.strip() for item in task["blockers"]):
            raise ValueError("Task blockers must be a list of nonempty strings")
        if task["status"] == "blocked" and not task["blockers"]:
            raise ValueError("Blocked tasks need a blocker")
        sides = task.get("folio_sides")
        if not isinstance(sides, list) or not sides or len(sides) != len(set(sides)):
            raise ValueError("Tasks need distinct folio sides")
        for side in sides:
            if side not in rows:
                raise ValueError(f"Task has unknown side: {side}")
            rows[side]["task_ids"].append(identifier)
        refs = task.get("references")
        if not isinstance(refs, list) or not refs:
            raise ValueError("Tasks need repository references")
        for ref in refs:
            read(ref)
        # Finishing a task is an operational event, not scientific verification.

    ordered_rows = [rows[side] for side in sorted(rows, key=side_key)]
    for row in ordered_rows:
        row["full_image_text_review_recorded"] = all(
            row["stages"][stage] == "complete"
            for stage in ("image_text_alignment", "independent_review"))
        row["gaps"] = []
        if not row["transcription_page_ids"]:
            row["gaps"].append("No transcription page reference in the imported pair")
        if row["unresolved_panel_page_ids"]:
            row["gaps"].append("Panel regions unresolved in the imported metadata audit")
        for stage in STAGES:
            if row["stages"][stage] != "complete":
                row["gaps"].append(f"{stage}: {row['stages'][stage]}")

    summary = {
        "indexed_folio_sides": len(rows), "indexed_canvases": len(canvases),
        "non_numbered_views": sum(not c["explicit_folio_sides"] for c in canvases),
        "transcription_page_ids": len(pages),
        "folio_sides_with_transcription_references": sum(bool(r["transcription_page_ids"]) for r in ordered_rows),
        "unresolved_transcription_panel_ids": sum(p["panel_region_status"] == "unresolved" for p in pages),
        "stage_counts": {stage: {status: sum(r["stages"][stage] == status for r in ordered_rows)
                                 for status in ("not_recorded", "partial", "complete")}
                         for stage in STAGES},
        "full_image_text_reviews_recorded": sum(r["full_image_text_review_recorded"] for r in ordered_rows),
        "active_owned_tasks": sum(t["status"] == "in_progress" for t in tasks),
    }
    return {"schema_version": 1, "method": "committed-evidence-folio-side-ledger-v1",
            "denominator": "Explicit folio sides in the pinned Yale image index; not panels, independent samples, or all physical manuscript material",
            "limits": ["Not recorded means absent from this ledger, not proof no work exists.",
                       "This generator validates records and source identity; it does not verify scientific claims.",
                       "Shared carriers and overlapping studies do not create independent observations.",
                       "Only explicitly recorded tasks are tracked; chat activity is not inferred."],
            "input_sha256": dict(sorted(inputs.items())), "summary": summary,
            "unrepresented_leaf_numbers": audit["unrepresented_leaf_numbers_within_observed_span"],
            "non_numbered_views": [{k: c[k] for k in ("image_oid", "yale_label", "catalog_image_url")}
                                   for c in canvases if not c["explicit_folio_sides"]],
            "transcription_pages": pages, "evidence": evidence, "tasks": tasks,
            "folio_sides": ordered_rows}


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def markdown(report):
    summary = report["summary"]
    lines = ["# Manuscript coverage status", "",
             "Generated from committed records. Regenerate with `python3 scripts/build_manuscript_coverage.py --write`.", "",
             "[How to use and update this tracker](README.md) · [Machine-readable report](coverage.json)", "",
             f"**{summary['indexed_folio_sides']} labeled folio sides**, {summary['indexed_canvases']} image canvases, "
             f"and {summary['transcription_page_ids']} transcription page/panel identifiers are different denominators.", "",
             f"**{summary['full_image_text_reviews_recorded']} complete image/text reviews recorded** "
             f"(whole-folio alignment plus whole-folio independent review). "
             f"**{summary['active_owned_tasks']} tasks explicitly in progress.**", "",
             "Metadata links and partial observations do not establish a decipherment or translation. "
             "Not recorded means absent from the imported evidence, not proof no other work exists.", "",
             "| Stage | Not recorded | Partial | Complete |", "| --- | ---: | ---: | ---: |"]
    for stage, counts in summary["stage_counts"].items():
        lines.append(f"| {stage.replace('_', ' ')} | {counts['not_recorded']} | {counts['partial']} | {counts['complete']} |")
    lines += ["", f"The imported metadata audit retains **{summary['unresolved_transcription_panel_ids']} "
              "unresolved panel/special identifiers**. This count is not a count of physical pages.", "",
              "## Work queue", "",
              "Tasks are planning records. A done task does not change evidence-stage completion.", "",
              "| Task / sides | Stage | Owner | Status | Next action / blockers |",
              "| --- | --- | --- | --- | --- |"]
    for task in report["tasks"]:
        notes = task["next_action"] + (" Blockers: " + "; ".join(task["blockers"]) if task["blockers"] else "")
        lines.append("| " + " | ".join(cell(v) for v in (
            task["id"] + " / " + ", ".join(task["folio_sides"]), task["stage"],
            task["owner"] or "unassigned", task["status"], notes)) + " |")
    lines += ["", "## Folio-side ledger", "",
              "Each row keeps shared image carriers visible. Evidence numbers refer to the register below.", "",
              "| Folio / Yale images | Transcription IDs | Visual observations | Image/text alignment | Independent review | Validated translation | Tasks | Evidence |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    numbers = {e["id"]: i for i, e in enumerate(report["evidence"], 1)}
    for row in report["folio_sides"]:
        images = ", ".join(f"[{c['image_oid']}]({c['catalog_image_url']})" for c in row["canvases"])
        page_ids = ", ".join(row["transcription_page_ids"]) or "not recorded"
        if row["unresolved_panel_page_ids"]:
            page_ids += " (regions unresolved)"
        values = [row["folio_side"] + " / " + images, page_ids]
        values += [row["stages"][stage].replace("_", " ") for stage in STAGES]
        values += [", ".join(row["task_ids"]) or "none recorded",
                   ", ".join(str(numbers[e]) for e in row["evidence_ids"]) or "—"]
        lines.append("| " + " | ".join(cell(v) for v in values) + " |")
    lines += ["", "## Evidence register", ""]
    for i, entry in enumerate(report["evidence"], 1):
        refs = ", ".join(f"[{Path(ref).name}](../../{ref})" for ref in entry["references"])
        lines.append(f"{i}. **{entry['id']}** ({', '.join(entry['folio_sides'])}; "
                     f"{entry['stage']}; {entry['status']}; {entry['scope']}): "
                     f"{entry['summary']} {refs}")
    lines += ["", "## Other indexed material", "",
              "Unnumbered views stay outside the folio-side denominator and still need separately scoped work.", ""]
    for view in report["non_numbered_views"]:
        lines.append(f"- {view['yale_label']}: [Yale {view['image_oid']}]({view['catalog_image_url']})")
    lines += ["", "Leaf numbers without labels within the indexed range: " +
              ", ".join(str(n) for n in report["unrepresented_leaf_numbers"]) +
              ". These are index gaps, not a new claim about loss or missing physical material.", "",
              "All input hashes and conservative shared-carrier dependency groups are in `coverage.json`.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="replace only the two generated tracker files")
    mode.add_argument("--check", action="store_true", help="fail if either committed output is stale")
    args = parser.parse_args()
    try:
        report = build()
        contents = (json.dumps(report, indent=2, ensure_ascii=False) + "\n", markdown(report))
        for relative, content in zip(OUTPUTS, contents):
            destination = ROOT / relative
            if args.check:
                if not destination.is_file() or destination.read_text(encoding="utf-8") != content:
                    raise ValueError(f"Stale or missing output: {relative}; regenerate with --write")
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                                 delete=False) as stream:
                    temporary = Path(stream.name)
                    stream.write(content)
                try:
                    os.replace(temporary, destination)
                finally:
                    temporary.unlink(missing_ok=True)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"Coverage tracker error: {error}\n")
    print(json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
