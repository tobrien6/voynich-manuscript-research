"""Reconcile the three initial pilot inventories without counting reused scans.

This audits recorded references, not actual exposure history or independent images.
"""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path

try:
    from .audit_transcription_images import audit
    from .audit_transliterations import ROOT
    from .index_yale_manifest import build
except ImportError:
    from audit_transcription_images import audit
    from audit_transliterations import ROOT
    from index_yale_manifest import build


INVENTORIES = (
    ("section_beginnings", "research/pilot/inventory.json", "research/pilot/INVENTORY.md"),
    ("boundary_survey", "research/boundary-pilot/selection.json", "research/boundary-pilot/INVENTORY.md"),
    ("standalone_rectos", "research/data/pilot-folios.csv", "research/PILOT_INVENTORY.md"),
)


def load_inventory(inventory_id, raw, index, manifest_sha256, expected_count=10):
    """Preserve each source's target convention; match by image/canvas identity."""
    if inventory_id == "standalone_rectos":
        entries = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    else:
        document = json.loads(raw)
        if document["manifest_sha256"] != manifest_sha256:
            raise ValueError(f"{inventory_id}: manifest identity differs")
        entries = document["records" if inventory_id == "section_beginnings" else "entries"]
    if len(entries) != expected_count:
        raise ValueError(f"{inventory_id}: require the declared {expected_count} records, got {len(entries)}")
    result, seen = [], set()
    for entry in entries:
        if inventory_id == "section_beginnings":
            oid, label, canvas = entry["image_id"], entry["yale_label"], entry["canvas_uri"]
            target = entry["target"]
        elif inventory_id == "boundary_survey":
            oid = entry["image_service"].rsplit("/", 1)[-1]
            label, canvas, target = entry["canvas_label"], entry["canvas_id"], entry["target_folio"]
        else:
            oid, label, canvas = entry["image_oid"], entry["yale_label"], entry["canvas_id"]
            target = None  # This inventory selects complete canvas labels, not one folio side.
        if oid in seen:
            raise ValueError(f"{inventory_id}: repeated selected image {oid}")
        seen.add(oid)
        match = index.get(oid)
        if match is None or match["yale_label"] != label or match["canvas_uri"] != canvas:
            raise ValueError(f"{inventory_id}: image/canvas/label identity differs for {oid}")
        if target is not None and target not in match["explicit_folio_sides"].split(";"):
            raise ValueError(f"{inventory_id}: target {target} is not explicitly named by image {oid}")
        result.append({"inventory_id": inventory_id, "source_target": target, "source_label": label,
                       "image_oid": oid, "canvas_uri": canvas,
                       "explicit_label_folio_sides": match["explicit_folio_sides"].split(";"),
                       "catalog_image_url": match["catalog_image_url"]})
    return result


def make_report(records, coverage, inputs):
    leaf_groups = {leaf: group["group_id"] for group in coverage["dependency_components"] for leaf in group["folio_ids"]}
    by_canvas = defaultdict(list)
    inventory_canvases = defaultdict(set)
    inventory_groups = defaultdict(set)
    for record in records:
        group_ids = {leaf_groups[side[:-1]] for side in record["explicit_label_folio_sides"] if side}
        if len(group_ids) != 1:
            raise ValueError("selected canvas has no single supported dependency component")
        group_id = next(iter(group_ids))
        copied = dict(record, dependency_group=group_id)
        by_canvas[record["canvas_uri"]].append(copied)
        inventory_canvases[record["inventory_id"]].add(record["canvas_uri"])
        inventory_groups[record["inventory_id"]].add(group_id)
    canvases = []
    for uri, references in sorted(by_canvas.items()):
        first = references[0]
        canvases.append({"canvas_uri": uri, "image_oid": first["image_oid"],
            "yale_label": first["source_label"], "explicit_label_folio_sides": first["explicit_label_folio_sides"],
            "dependency_group": first["dependency_group"], "catalog_image_url": first["catalog_image_url"],
            "inventory_references": [{"inventory_id": ref["inventory_id"], "source_target": ref["source_target"]}
                                     for ref in references]})
    names = [spec[0] for spec in INVENTORIES]
    overlaps = [{"left": left, "right": right,
                 "shared_canvases": sorted(inventory_canvases[left] & inventory_canvases[right]),
                 "shared_dependency_groups": sorted(inventory_groups[left] & inventory_groups[right])}
                for n, left in enumerate(names) for right in names[n + 1:]]
    group_counts = Counter(canvas["dependency_group"] for canvas in canvases)
    explicit_leaves = sorted({side[:-1] for canvas in canvases
                              for side in canvas["explicit_label_folio_sides"] if side}, key=int)
    return {"schema_version": 1, "method": "initial-three-pilot-image-overlap-v1", "inputs": inputs,
        "image_index": coverage["image_index"], "scope": "three initial inventories only; no complete exposure history is certified",
        "record_count": len(records), "distinct_canvas_count": len(canvases),
        "distinct_dependency_component_count": len(group_counts),
        "explicit_label_leaf_ids": explicit_leaves,
        "explicit_label_leaf_count": len(explicit_leaves),
        "inventories": [{"inventory_id": name, "records": sum(r["inventory_id"] == name for r in records),
                         "distinct_canvases": len(inventory_canvases[name]),
                         "distinct_dependency_components": len(inventory_groups[name])} for name in names],
        "pairwise_overlaps": overlaps, "canvases": canvases,
        "components_with_multiple_selected_canvases": [{"dependency_group": group,
            "canvas_uris": [canvas["canvas_uri"] for canvas in canvases if canvas["dependency_group"] == group]}
            for group, count in sorted(group_counts.items()) if count > 1],
        "limits": ["Repeated observations may be useful reviews, but do not create additional manuscript samples.",
                   "Different canvases in one component are conservatively related, not proven independent.",
                   "Canvas labels and inventory records do not establish complete visible text, glyph alignment, or actual exposure by a particular researcher.",
                   "No evaluation units, partition, freeze timestamp, or unseen-material claim is assigned."]}


def run(raw_manifest, root=ROOT):
    coverage = audit(raw_manifest, root)
    rows = build(raw_manifest, coverage["image_index"]["access_date"])["canvases.csv"]
    index = {row["image_oid"]: row for row in rows}
    if len(index) != len(rows):
        raise ValueError("review repeated image services before using an image-identifier lookup")
    records, inputs = [], []
    for name, metadata_path, observations_path in INVENTORIES:
        raw = (root / metadata_path).read_bytes()
        records.extend(load_inventory(name, raw, index, coverage["image_index"]["manifest_sha256"]))
        inputs.append({"inventory_id": name, "metadata_path": metadata_path,
                       "metadata_sha256": hashlib.sha256(raw).hexdigest(),
                       "observations_path": observations_path,
                       "observations_sha256": hashlib.sha256((root / observations_path).read_bytes()).hexdigest()})
    return make_report(records, coverage, inputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        result = run(args.manifest.read_bytes())
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("committed pilot overlap report differs")
        if args.output:
            args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        elif not args.check:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        if args.check:
            print("PASS: index pins, all three inventories, and complete overlap report reproduce")
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"FAIL: {error}\n")


if __name__ == "__main__":
    main()
