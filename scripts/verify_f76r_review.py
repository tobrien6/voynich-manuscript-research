"""Check frozen source links and review geometry, not visual judgments."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

try:
    from .select_f76r_anchors import ROOT, selection, require
    from .verify_initial_prefix_review import bitmap_dimensions
except ImportError:
    from select_f76r_anchors import ROOT, selection, require
    from verify_initial_prefix_review import bitmap_dimensions


SELECTION = ROOT / "research/pilot/f76r-anchor-selection.json"
REVIEW = ROOT / "research/pilot/f76r-anchor-review.json"
COORDINATES = {"units": "native image pixels", "origin": "upper left",
               "x_direction": "right", "y_direction": "down",
               "region_format": "[x, y, width, height]"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def geometry(region, width, height):
    require(isinstance(region, list) and len(region) == 4
            and all(type(value) is int for value in region), "Require four integer region coordinates")
    x, y, w, h = region
    require(x >= 0 and y >= 0 and w > 0 and h > 0
            and x + w <= width and y + h <= height, "Region is outside the native image")
    return ",".join(map(str, region))


def verify(record, image_dir=None):
    raw = SELECTION.read_bytes()
    frozen = json.loads(raw)
    require(selection() == frozen, "Frozen source selection no longer reproduces")
    require(record["schema_version"] == 1 and record["method"] == "f76r-three-native-locus-image-review-v1",
            "Unknown image review")
    require(record["selection_path"] == "research/pilot/f76r-anchor-selection.json"
            and record["selection_sha256"] == digest(raw), "Review is not bound to the frozen selection")
    require(record["selection_plan_commit"] == "54007c5479a49652c8233b841234eec4b337841f",
            "Recorded pre-inspection commit differs")
    for name in ["image", "manifest", "sources"]:
        require(record[name] == frozen[name], f"Review {name} differs from the frozen identity")
    require(record["coordinate_system"] == COORDINATES, "Review must use native-pixel coordinates")
    image = frozen["image"]
    width, height, service = image["native_width"], image["native_height"], image["service_url"]
    files = record["inspection_files"]
    require([item["id"] for item in files] == ["overview", "first", "median", "last"],
            "Require the overview and all three anchor inspections")
    for item in files:
        require(item["local_filename"] == "f76r-" + item["id"] + ".jpg", "Unexpected image filename")
        require(isinstance(item["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
                and type(item["bytes"]) is int and item["bytes"] > 0, "Invalid image fingerprint")
        if item["id"] == "overview":
            require(item["native_region"] is None and [item["width"], item["height"]] == [1334, 1800],
                    "Overview dimensions differ from the inspected derivative")
            expected_url = service + "/full/!1800,1800/0/default.jpg"
        else:
            region = item["native_region"]
            region_string = geometry(region, width, height)
            require([item["width"], item["height"]] == region[2:], "Native region dimensions differ")
            expected_url = service + "/" + region_string + "/full/0/default.jpg"
        require(item["url"] == expected_url, "Inspection URL and native region differ")
        if image_dir is not None:
            local = (image_dir / item["local_filename"]).read_bytes()
            require(len(local) == item["bytes"] and digest(local) == item["sha256"],
                    "Local inspected image bytes differ")
            require(bitmap_dimensions(local) == (item["width"], item["height"]),
                    "Local bitmap header dimensions differ")
    metadata = record["service_metadata"]
    require(metadata["url"] == service + "/info.json" and metadata["local_filename"] == "f76r-info.json"
            and metadata["service_id"] == service
            and [metadata["width"], metadata["height"]] == [width, height]
            and isinstance(metadata["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", metadata["sha256"]),
            "Image-service metadata differs")
    if image_dir is not None:
        local = (image_dir / metadata["local_filename"]).read_bytes()
        require(digest(local) == metadata["sha256"], "Local service metadata bytes differ")
        info = json.loads(local)
        require(info["@id"] == service and [info["width"], info["height"]] == [width, height],
                "Local service identity or dimensions differ")
    rows = record["records"]
    expected = frozen["selection"]["anchors"]
    require([row["key"] for row in rows] == [anchor["key"] for anchor in expected],
            "All three frozen anchors must remain in order")
    for row, anchor, file_id in zip(rows, expected, ["first", "median", "last"]):
        require(row["selection_role"] == anchor["role"]
                and row["native_source_contexts"] == anchor["sources"], "Native locus/context differs")
        require(row["inspection_file_id"] == file_id, "Anchor image-region association differs")
        association = row["source_row_association"]
        require(association["status"] in {"provisional", "unresolved"}, "Verified row/glyph claims are unsupported")
        for value in [row["direct_observations"], association["basis"], association["unresolved"]]:
            require(isinstance(value, list) and value and all(isinstance(text, str) and text.strip() for text in value),
                    "Observation, association basis and uncertainty must remain separate and nonempty")
        require(isinstance(association["candidate_description"], str) and association["candidate_description"].strip()
                and isinstance(association["alternative_search_limit"], str) and association["alternative_search_limit"].strip(),
                "Missing row/search limitation")
        require(isinstance(association["other_candidate_regions"], list), "Invalid alternative-region record")
        for region in association["other_candidate_regions"]:
            geometry(region, width, height)
    exposure = record["exposure"]
    require(exposure["prior_inventory"] == frozen["exposure"]["prior_inventory"]
            and exposure["whole_corpus_text_exposure"] is True
            and exposure["new_f76r_image_inspection"] is True and exposure["untouched_evaluation"] is False,
            "Prior and new exposure must be disclosed")
    require(record["review_status"] == "single-observer provisional row alignment"
            and record["glyph_adjudication"] == "unresolved" and record["source_corrections_applied"] is False,
            "Unsupported confirmation or source correction")
    require(record["limits"], "Missing review limits")
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=REVIEW)
    parser.add_argument("--image-dir", type=Path)
    args = parser.parse_args()
    try:
        count = verify(json.loads(args.record.read_bytes()), args.image_dir)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {count} frozen native contexts, image identities and review regions verify")
    if args.image_dir is not None:
        print("All local inspected-file and service-metadata bytes match")
    print("Visual judgments and row associations need independent review; bitmap headers do not decode pixels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
