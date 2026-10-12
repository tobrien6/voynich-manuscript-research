"""Inventory exact rosette source identifiers without creating a locus crosswalk."""

import argparse
from collections import Counter
import csv
import hashlib
import itertools
import json
from pathlib import Path

try:
    from .audit_historical_interlinear import parse_historical, read_pinned_archive
    from .audit_pilot_transcriptions import page_summary
    from .audit_transliterations import load_sources
    from .rosette_cohort import MODERN_IDS, check as check_cohort
except ImportError:
    from audit_historical_interlinear import parse_historical, read_pinned_archive
    from audit_pilot_transcriptions import page_summary
    from audit_transliterations import load_sources
    from rosette_cohort import MODERN_IDS, check as check_cohort


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("fRos", "f85v2", "f86r4", "f86r6", "f85v1", "f86r3", "f86r5")
INPUTS = (
    "data/transliterations.json", "data/historical/interlinear-16e6.json",
    "research/pilot/inventory.json", "research/image-index/canvases.csv",
    "research/image-index/audit.json",
    "scripts/audit_rosette_coverage.py", "scripts/audit_historical_interlinear.py",
    "scripts/audit_pilot_transcriptions.py", "scripts/audit_transliterations.py",
    "scripts/ivtff.py",
    "scripts/rosette_cohort.py",
)


def historical_page(records, page):
    selected = [record for record in records if record.page == page]
    codes = sorted({record.transcriber for record in selected} | {"H"})
    keys = {code: {(record.unit, record.line) for record in selected
                   if record.transcriber == code} for code in codes}
    return {
        "page_id": page,
        "native_records": len(selected),
        "distinct_unit_line_keys": len({(r.unit, r.line) for r in selected}),
        "records_by_transcriber": {code: sum(r.transcriber == code for r in selected)
                                   for code in codes},
        "records_by_native_unit_tag": dict(sorted(Counter(r.unit for r in selected).items())),
        "within_source_key_overlap": [
            {"left_code": left, "right_code": right,
             "shared_unit_line_keys": len(keys[left] & keys[right]),
             "left_only_unit_line_keys": len(keys[left] - keys[right]),
             "right_only_unit_line_keys": len(keys[right] - keys[left])}
            for left, right in itertools.combinations(codes, 2)],
        "ordered_record_refs": [{"locator": r.locator, "physical_line": r.physical_line}
                                for r in selected],
    }


def canvas_context(inventory, index, audit):
    targets = [r for r in inventory["records"] if r["target"] == "85v"]
    if len(targets) != 1:
        raise ValueError("require the one original 85v pilot target")
    target = targets[0]
    matches = [r for r in index if r["image_oid"] == "1006231"]
    if len(matches) != 1:
        raise ValueError("require the one indexed rosette canvas")
    row = matches[0]
    if (row["yale_label"] != "85v and 86r (foldout)" or
            row["explicit_folio_sides"] != "85v;86r" or
            row["has_multiple_explicit_sides"] != "True" or
            target["canvas_uri"] != row["canvas_uri"] or
            target["yale_label"] != row["yale_label"] or
            target["image_id"] != row["image_oid"] or
            inventory["manifest_sha256"] != audit["manifest_sha256"]):
        raise ValueError("rosette pilot/index carrier identity differs")
    return {"inventory_target": "85v", "yale_label": row["yale_label"],
            "canvas_uri": row["canvas_uri"], "image_id": row["image_oid"],
            "catalog_image_url": row["catalog_image_url"],
            "explicit_folio_sides": row["explicit_folio_sides"].split(";"),
            "mapping_scope": "existing coarse carrier reference only"}


def report(root=ROOT):
    pins = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in INPUTS}
    catalog = json.loads((root / INPUTS[1]).read_text())
    if catalog.get("schema_version") != 1 or catalog.get("id") != "LS16e6":
        raise ValueError("require the accepted historical catalog")
    member = read_pinned_archive((root / catalog["path"]).read_bytes(), catalog)
    records, _ = parse_historical(member)
    inventory = json.loads((root / INPUTS[2]).read_text())
    with (root / INPUTS[3]).open(newline="") as handle:
        index = list(csv.DictReader(handle))
    audit = json.loads((root / INPUTS[4]).read_text())
    return {
        "schema_version": 1,
        "scope": "Source coverage diagnostic; no historical/modern locus alignment or glyph review",
        "apply_to_statistics": False,
        "verified_locus_crosswalk": None,
        "input_pins": pins,
        "canvas_context": canvas_context(inventory, index, audit),
        "historical_source": {key: catalog[key] for key in
            ("id", "archive_sha256", "archive_bytes", "member", "member_sha256", "member_bytes")},
        "historical_pages": [historical_page(records, page) for page in PAGES],
        "modern_sources": [
            {"id": source["id"], "alphabet": source["alphabet"],
             "sha256": source["sha256"], "url": source["url"],
             "pages": [page_summary(document, page) for page in PAGES]}
            for source, document in load_sources(root)],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--require-same-modern-cohort", nargs=2, choices=MODERN_IDS, metavar=("LEFT", "RIGHT"),
                        help="require equal nonempty fRos keys, kinds and locators in two modern exports")
    args = parser.parse_args()
    try:
        catalog = json.loads((ROOT / INPUTS[0]).read_text())
        historical = json.loads((ROOT / INPUTS[1]).read_text())
        protected = {(ROOT / name).resolve() for name in INPUTS}
        protected.add((ROOT / historical["path"]).resolve())
        protected.update((ROOT / source["path"]).resolve() for source in catalog["sources"])
        if args.output and any(args.output.resolve() == path or
                (args.output.exists() and path.exists() and args.output.samefile(path))
                for path in protected):
            raise ValueError("output must not overwrite a pinned source or metadata input")
        result = report()
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("rosette coverage differs from committed report")
        cohort = check_cohort(result, *args.require_same_modern_cohort) if args.require_same_modern_cohort else None
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        elif not args.check:
            print(rendered, end="")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"rosette source coverage failed: {error}\n")
    if args.check:
        print("Pinned rosette source coverage reproduces; no locus crosswalk is assigned.")
    if cohort:
        if cohort["errors"]:
            for error in cohort["errors"]:
                print("INCOMPLETE:", error)
            return 2
        print("PASS: equal nonempty modern native key/kind/locator cohorts")
        print("NOTE: glyph/region agreement and independent source evidence remain unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
