"""Build an auditable folio-side/canvas crosswalk for Yale's Voynich manifest.

Reads a saved IIIF v3 response, downloads nothing, and uses the standard library.
This deliberately supports the observed Yale structure, not every IIIF profile.
"""

import argparse
from collections import Counter, defaultdict
import csv
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys


MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
CATALOG_URL = "https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM"
# Manually recorded from the catalog's collation, accessed 2026-10-11.
CATALOG_MISSING_LEAVES = [12, 59, 60, 61, 62, 63, 64, 74, 91, 92, 97, 98, 109, 110]
SIDE_PATTERN = re.compile(r"(?<![0-9A-Za-z])(\d+[rv])(?![0-9A-Za-z])")
EXACT_SIDE_PATTERN = re.compile(r"\d+[rv]")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def folio_sides(label):
    """Extract explicit side labels only; an unqualified 85-86 is not a side."""
    return list(dict.fromkeys(SIDE_PATTERN.findall(label)))


def side_sort(side):
    return int(side[:-1]), side[-1]


def build(raw, access_date):
    datetime.date.fromisoformat(access_date)
    manifest = json.loads(raw)
    require(manifest.get("id") == MANIFEST_URL and manifest.get("type") == "Manifest",
            "Expected Yale object 2002046's IIIF Presentation v3 manifest")
    require(isinstance(manifest.get("items"), list) and manifest["items"],
            "Expected a nonempty canvas list")
    canvas_rows = []
    associations = defaultdict(list)
    seen_canvas_ids = set()
    for index, canvas in enumerate(manifest["items"]):
        require(canvas.get("type") == "Canvas", f"Item {index} is not a Canvas")
        canvas_id = canvas["id"]
        require(canvas_id not in seen_canvas_ids, f"Duplicate canvas ID: {canvas_id}")
        seen_canvas_ids.add(canvas_id)
        labels = canvas["label"]
        require(list(labels) == ["none"] and len(labels["none"]) == 1,
                f"Review changed or ambiguous language-map label at canvas {index}")
        label = labels["none"][0]
        require(isinstance(label, str) and label, f"Empty or nontext label at canvas {index}")
        sides = folio_sides(label)
        paintings = [a for page in canvas["items"] for a in page["items"]
                     if a.get("motivation") == "painting"]
        require(len(paintings) == 1, f"Review painting arrangement for {label}")
        annotation = paintings[0]
        require(annotation.get("target") == canvas_id, f"Review painting target for {label}")
        body = annotation["body"]
        require(body.get("type") == "Image", f"Review image body for {label}")
        services = body["service"]
        require(len(services) == 1, f"Review multiple image services for {label}")
        service = services[0]["@id"]
        prefix = "https://collections.library.yale.edu/iiif/2/"
        require(service.startswith(prefix) and service[len(prefix):].isdigit(),
                f"Unexpected Yale image service for {label}")
        image_oid = service[len(prefix):]
        require(body["id"] == service + "/full/full/0/default.jpg",
                f"Review full-image URL for {label}")
        for axis in ("width", "height"):
            require(type(body[axis]) is int and body[axis] > 0,
                    f"Invalid image {axis} for {label}")
        kind = ("non_numbered_view" if not sides else
                "exact_single_side_label" if EXACT_SIDE_PATTERN.fullmatch(label) else
                "compound_or_partial_label")
        row = {
            "canvas_index_zero_based": index,
            "viewer_image_number_one_based": index + 1,
            "yale_label": label,
            "label_class": kind,
            "explicit_folio_sides": ";".join(sides),
            "has_partial_marker": "(part)" in label,
            "has_multiple_explicit_sides": len(sides) > 1,
            "canvas_uri": canvas_id,
            "image_oid": image_oid,
            "catalog_image_url": f"https://collections.library.yale.edu/catalog/2002046?child_oid={image_oid}",
            "full_image_url": body["id"],
            "image_service_url": service,
            "image_width": body["width"],
            "image_height": body["height"],
        }
        canvas_rows.append(row)
        for side in sides:
            associations[side].append(row)
    require(associations, "No numbered folio sides found; review label conventions")
    side_rows = []
    for side in sorted(associations, key=side_sort):
        rows = associations[side]
        side_rows.append({
            "folio_side": side,
            "folio_number": int(side[:-1]),
            "side": side[-1],
            "canvas_count": len(rows),
            "has_exact_side_label": any(row["yale_label"] == side for row in rows),
            "has_partial_view": any(row["has_partial_marker"] for row in rows),
            "has_shared_view": any(row["has_multiple_explicit_sides"] for row in rows),
            "canvas_indices_zero_based": ";".join(str(row["canvas_index_zero_based"]) for row in rows),
            "image_oids": ";".join(row["image_oid"] for row in rows),
            "canvas_uris": ";".join(row["canvas_uri"] for row in rows),
            "catalog_image_urls": ";".join(row["catalog_image_url"] for row in rows),
        })
    numbers = sorted({row["folio_number"] for row in side_rows})
    unrepresented = [number for number in range(numbers[0], numbers[-1] + 1)
                     if number not in numbers]
    audit = {
        "manifest_url": MANIFEST_URL,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "access_date": access_date,
        "access_timezone": "America/New_York",
        "method": "Explicit folio sides in Yale labels; no visual or transcription inference",
        "canvas_count": len(canvas_rows),
        "label_class_counts": dict(sorted(Counter(row["label_class"] for row in canvas_rows).items())),
        "explicit_folio_side_count": len(side_rows),
        "explicit_folio_number_count": len(numbers),
        "explicit_folio_number_min": numbers[0],
        "explicit_folio_number_max": numbers[-1],
        "unrepresented_leaf_numbers_within_observed_span": unrepresented,
        "numbers_with_only_one_side_in_labels": [number for number in numbers
            if (f"{number}r" in associations) != (f"{number}v" in associations)],
        "sides_with_multiple_canvases": [
            {"folio_side": row["folio_side"], "image_oids": row["image_oids"].split(";")}
            for row in side_rows if row["canvas_count"] > 1
        ],
        "non_numbered_views": [
            {"yale_label": row["yale_label"], "image_oid": row["image_oid"]}
            for row in canvas_rows if row["label_class"] == "non_numbered_view"
        ],
        "catalog_comparison": {
            "source_url": CATALOG_URL,
            "source_access_date": "2026-10-11",
            "manually_recorded_missing_leaf_numbers": CATALOG_MISSING_LEAVES,
            "matches_unrepresented_numbers_in_observed_span": unrepresented == CATALOG_MISSING_LEAVES,
            "catalog_final_section_end": "117v",
            "117r_has_explicit_manifest_label": "117r" in associations,
            "117v_has_explicit_manifest_label": "117v" in associations,
            "limitation": "Absence of a label is not proof of a missing physical leaf; final-range discrepancy unresolved",
        },
    }
    return {"canvases.csv": canvas_rows, "folio-sides.csv": side_rows, "audit.json": audit}


def serialize(outputs):
    import io
    serialized = {}
    for name, value in outputs.items():
        if name.endswith(".json"):
            serialized[name] = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
        else:
            stream = io.StringIO(newline="")
            writer = csv.DictWriter(stream, fieldnames=list(value[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(value)
            serialized[name] = stream.getvalue()
    return serialized


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--access-date", required=True, help="Date the supplied response was retrieved, YYYY-MM-DD")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Compare generated bytes; do not write files")
    args = parser.parse_args()
    try:
        outputs = build(args.manifest.read_bytes(), args.access_date)
        serialized = serialize(outputs)
        if args.check:
            mismatches = [name for name, value in serialized.items()
                          if not (args.output_dir / name).exists()
                          or (args.output_dir / name).read_bytes() != value.encode("utf-8")]
            require(not mismatches, "Generated outputs differ: " + ", ".join(mismatches))
            print("PASS: both CSV indexes and audit reproduce byte-for-byte")
        else:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            for name, value in serialized.items():
                (args.output_dir / name).write_bytes(value.encode("utf-8"))
            print(f"Wrote {len(outputs['canvases.csv'])} canvases and {len(outputs['folio-sides.csv'])} folio sides")
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
