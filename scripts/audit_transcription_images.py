"""Audit IVTFF page references and conservative Yale image dependencies.

Side references are not panel coordinates or reviewed image/text alignments.
No images are downloaded, and no evaluation split is assigned.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

try:
    from .audit_transliterations import ROOT, load_sources
    from .index_yale_manifest import build, serialize, side_sort
    from .validate_evaluation_split import load_split_json, validate
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from index_yale_manifest import build, serialize, side_sort
    from validate_evaluation_split import load_split_json, validate


SOURCE_IDS = ("ZL3b", "IT2a")
CONVENTION_URL = "https://voynich.nu/software/ivtt/IVTFF_format.pdf"
SIMPLE_PAGE = re.compile(r"f([1-9][0-9]*)([rv])")
NUMBERED_PAGE = re.compile(r"f([1-9][0-9]*)([rv])([1-6])")
# Explicit scope: panel page headers observed in the two pinned editions.
# IVTFF section 4.2 explains their side notation, including the 86v exception.
# A new panel name requires review rather than arbitrary suffix truncation.
PANEL_NUMBERS = {
    "67r": (1, 2), "67v": (1, 2),
    "68r": (1, 2, 3), "68v": (1, 2, 3),
    "70r": (1, 2), "70v": (1, 2),
    "72r": (1, 2, 3), "72v": (1, 2, 3),
    "85r": (1, 2), "86v": (3, 4, 5, 6),
    "89r": (1, 2), "89v": (1, 2),
    "90r": (1, 2), "90v": (1, 2),
    "95r": (1, 2), "95v": (1, 2),
    "102r": (1, 2), "102v": (1, 2),
}


def page_reference(page):
    """Interpret only the declared IVTFF naming convention, preserving the page."""
    if SIMPLE_PAGE.fullmatch(page):
        return {"kind": "simple_side_reference", "folio_sides": [page[1:]]}
    if page == "fRos":
        return {"kind": "rosettes_reference", "folio_sides": ["85v", "86r"]}
    match = NUMBERED_PAGE.fullmatch(page)
    if match:
        side = match[1] + match[2]
        if int(match[3]) in PANEL_NUMBERS.get(side, ()):
            return {"kind": "panel_side_reference", "folio_sides": [side]}
    return {"kind": "unsupported_convention", "folio_sides": []}


def dependency_components(canvas_rows):
    """Connect physical leaf references, including transitive shared scans."""
    neighbors = defaultdict(set)
    for row in canvas_rows:
        leaves = {side[:-1] for side in row["explicit_folio_sides"].split(";") if side}
        for leaf in leaves:
            neighbors[leaf].update(leaves)
    remaining = set(neighbors)
    groups = []
    while remaining:
        pending = [min(remaining, key=int)]
        members = set()
        while pending:
            leaf = pending.pop()
            if leaf not in members:
                members.add(leaf)
                pending.extend(neighbors[leaf] - members)
        remaining.difference_update(members)
        leaves = sorted(members, key=int)
        groups.append({"group_id": "yale-leaves:" + "+".join(leaves), "folio_ids": leaves})
    return groups


def make_report(sources, canvas_rows, image_identity):
    selected = [(source, document) for source, document in sources if source["id"] in SOURCE_IDS]
    if Counter(source["id"] for source, _ in selected) != Counter(SOURCE_IDS):
        raise ValueError("require exactly one pinned ZL3b and IT2a source")
    selected.sort(key=lambda item: SOURCE_IDS.index(item[0]["id"]))
    groups = dependency_components(canvas_rows)
    leaf_groups = {leaf: group for group in groups for leaf in group["folio_ids"]}
    indexed_leaf_canvases = defaultdict(set)
    for row in canvas_rows:
        for side in row["explicit_folio_sides"].split(";"):
            if side:
                indexed_leaf_canvases[side[:-1]].add(row["canvas_uri"])
    by_page = defaultdict(list)
    for source, document in selected:
        all_counts = Counter(locus.page for locus in document.loci)
        present = Counter(locus.page for locus in document.loci if locus.present)
        p0 = Counter(locus.page for locus in document.loci if locus.present and locus.kind == "P0")
        for page in document.pages:
            by_page[page].append({
                "source_id": source["id"], "loci": all_counts[page],
                "present_loci": present[page], "present_p0_loci": p0[page],
            })
    records = []
    for page in sorted(by_page):
        reference = page_reference(page)
        sides = reference["folio_sides"]
        matches = []
        matched_sides = set()
        for row in canvas_rows:
            named = row["explicit_folio_sides"].split(";") if row["explicit_folio_sides"] else []
            requested = sorted(set(named) & set(sides), key=side_sort)
            if requested:
                matched_sides.update(requested)
                matches.append({
                    "canvas_uri": row["canvas_uri"], "image_oid": row["image_oid"],
                    "yale_label": row["yale_label"], "label_folio_sides": named,
                    "requested_folio_sides": requested,
                    "has_partial_marker": row["has_partial_marker"],
                    "has_multiple_explicit_sides": row["has_multiple_explicit_sides"],
                    "catalog_image_url": row["catalog_image_url"],
                })
        unmatched = sorted(set(sides) - matched_sides, key=side_sort)
        status = ("unsupported_convention" if not sides else
                  "label_unmatched" if unmatched else "side_references_matched")
        strict = ("unsupported_identifier" if reference["kind"] != "simple_side_reference" else
                  "label_unmatched" if unmatched else "matched")
        group_ids = {leaf_groups[side[:-1]]["group_id"] for side in sides if side[:-1] in leaf_groups}
        if status == "side_references_matched" and len(group_ids) != 1:
            raise ValueError(f"{page}: reviewed convention spans separate dependency groups")
        records.append({
            "page_id": page, "source_counts": by_page[page], "reference": reference,
            "strict_folio_lookup_status": strict, "side_reference_status": status,
            "unmatched_folio_sides": unmatched,
            "panel_region_status": "unresolved" if reference["kind"] in
                {"panel_side_reference", "rosettes_reference"} else "not_assessed",
            "dependency_group": next(iter(group_ids)) if status == "side_references_matched" else None,
            "canvas_matches": matches,
        })
    summaries = []
    for source, document in selected:
        own = [record for record in records if source["id"] in
               {counts["source_id"] for counts in record["source_counts"]}]
        summaries.append({
            "source_id": source["id"], "sha256": source["sha256"], "url": source["url"],
            "alphabet": source["alphabet"], "page_headers": len(document.pages),
            "loci": len(document.loci), "present_loci": sum(locus.present for locus in document.loci),
            "strict_folio_lookup_counts": dict(sorted(Counter(
                record["strict_folio_lookup_status"] for record in own).items())),
            "side_reference_counts": dict(sorted(Counter(
                record["side_reference_status"] for record in own).items())),
            "unresolved_panel_region_pages": [record["page_id"] for record in own
                if record["panel_region_status"] == "unresolved"],
        })
    return {
        "schema_version": 1, "method": "ivtff-yale-side-reference-audit-v1",
        "mapping_scope": "folio_side_references_only", "image_text_alignment": "not_reviewed",
        "convention": {"url": CONVENTION_URL, "document_issue": "2.0.2, 08/07/2025",
                       "locator": "section 4.2 and Figures 1-2, printed pages 11-12",
                       "panel_numbers_by_side": PANEL_NUMBERS},
        "image_index": image_identity, "sources": summaries,
        "distinct_page_ids": len(records),
        "dependency_rule": "same declared leaf, or leaves connected transitively by explicit shared canvas labels",
        "dependency_components": groups, "pages": records,
        "indexed_canvas_ids_by_leaf": {leaf: sorted(canvases) for leaf, canvases in
            sorted(indexed_leaf_canvases.items(), key=lambda item: int(item[0]))},
        "limits": [
            "No image regions, glyph readings, historical aliases, or visual completeness are verified.",
            "Dependencies are conservative label-based hints, not a complete codicological model.",
            "Page names and locus counts are source annotations, not independent manuscript samples.",
            "No evaluation partition or claim of unseen material is assigned.",
        ],
    }


def audit(raw_manifest, root=ROOT):
    index_dir = root / "research/image-index"
    saved_audit = json.loads((index_dir / "audit.json").read_text())
    if hashlib.sha256(raw_manifest).hexdigest() != saved_audit["manifest_sha256"]:
        raise ValueError("manifest differs from the pinned image index; review a new snapshot first")
    indexed = build(raw_manifest, saved_audit["access_date"])
    for name, content in serialize(indexed).items():
        if (index_dir / name).read_bytes() != content.encode("utf-8"):
            raise ValueError(f"image index does not reproduce: {name}")
    identity = {field: saved_audit[field] for field in
                ("manifest_url", "manifest_sha256", "access_date", "access_timezone")}
    identity["canvases_csv_sha256"] = hashlib.sha256((index_dir / "canvases.csv").read_bytes()).hexdigest()
    return make_report(load_sources(root), indexed["canvases.csv"], identity)


def split_dependency_errors(split, report):
    """Check structurally valid split declarations against recomputed references.

    This is an additional gate, not proof of image/text identity or no exposure.
    Call the standard split validator first to validate declaration types.
    """
    leaf_groups = {leaf: group["group_id"] for group in report["dependency_components"]
                   for leaf in group["folio_ids"]}
    # Canvas completeness comes from the entire index, not edition coverage.
    # Missing transcription sides must not hide indexed scans from this gate.
    leaf_canvases = report["indexed_canvas_ids_by_leaf"]
    supported_leaves = set()
    for page in report["pages"]:
        if page["side_reference_status"] == "side_references_matched":
            supported_leaves.update(side[:-1] for side in page["reference"]["folio_sides"])
    memberships = defaultdict(set)
    errors = []
    for unit in split["units"]:
        uid = unit["unit_id"]
        expected_canvases = set()
        for leaf in unit["folio_ids"]:
            group_id = leaf_groups.get(leaf)
            if group_id is None or leaf not in supported_leaves:
                errors.append(f"{uid}: leaf {leaf} has no supported transcription/image references")
                continue
            memberships[group_id].add(uid)
            if group_id not in unit["dependency_groups"]:
                errors.append(f"{uid}: missing derived dependency group {group_id}")
            expected_canvases.update(leaf_canvases[leaf])
        missing = expected_canvases - set(unit["canvas_ids"])
        if missing:
            errors.append(f"{uid}: missing indexed canvas references {sorted(missing)}")
    for group_id, units in sorted(memberships.items()):
        if len(units) > 1:
            errors.append(f"{group_id}: belongs to multiple units {sorted(units)}; combine related leaves")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--split", type=Path, help="also check split declarations against recomputed image dependencies")
    args = parser.parse_args()
    try:
        report = audit(args.manifest.read_bytes())
        # JSON round-trip makes tuple-valued convention declarations comparable.
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.check and json.loads(rendered) != json.loads(args.check.read_text()):
            raise ValueError("committed image coverage report differs")
        if args.split:
            split = load_split_json(args.split.read_text())
            structural = validate(split)
            errors = structural["errors"]
            if not errors:
                errors = split_dependency_errors(split, report)
            if errors:
                raise ValueError("; ".join(errors))
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        elif not args.check and not args.split:
            print(rendered, end="")
        if args.check:
            print("PASS: source pins, image index, and complete coverage report reproduce")
        if args.split:
            print("PASS: declared split respects recomputed image dependencies and canvas references")
            print("NOTE: no input checksum, freeze history, image regions, or exposure history is certified here")
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"FAIL: {error}\n")


if __name__ == "__main__":
    main()
