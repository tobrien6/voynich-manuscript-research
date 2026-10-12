"""Build the fixed four-locus rosette image-review checklist; no glyph adjudication."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

try:
    from .audit_transliterations import load_sources
except ImportError:
    from audit_transliterations import load_sources


ROOT = Path(__file__).resolve().parents[1]
TARGETS = ("fRos.112,@L0", "fRos.113,=Cc", "fRos.114,+Ca", "fRos.115,=L0")
EDITIONS = {"ZL3b": "Eva-", "GC2a": "v101"}
PROPOSAL = "research/panel-regions/fRos-small-circle-proposal.json"
PLAN = "research/panel-regions/FROS_SMALL_CIRCLE_PLAN.md"
INPUTS = (PROPOSAL, PLAN, "data/transliterations.json", "scripts/ivtff.py",
          "scripts/audit_transliterations.py", "scripts/build_fros_review.py",
          "research/pilot/inventory.json", "research/folio-alignment/transcription-image-coverage.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_proposal(proposal, plan_bytes):
    require(type(proposal.get("schema_version")) is int and proposal["schema_version"] == 1,
            "require proposal schema version 1")
    require(proposal.get("apply_to_statistics") is False and
            proposal.get("verified_locus_crosswalk") is None and
            proposal.get("independent_glyph_review") is None,
            "this checklist requires an unverified proposal excluded from statistics")
    require(proposal.get("plan_sha256") == hashlib.sha256(plan_bytes).hexdigest(), "plan changed")
    require(proposal.get("targets") == list(TARGETS), "fixed review targets changed")
    assessments = proposal.get("target_layout_assessments", [])
    require([x.get("locus_id") for x in assessments] == list(TARGETS) and
            all(x.get("glyph_alignment") == "unresolved" for x in assessments),
            "all four glyph alignments must remain unresolved")
    require(proposal.get("original_image_dimensions") == {"width": 7925, "height": 7268},
            "original image dimensions differ")
    box, normalized = proposal["image_region_pixels"], proposal["image_region_normalized"]
    require(set(box) == {"x", "y", "width", "height"} and
            all(type(v) is int for v in box.values()), "region needs integer pixel coordinates")
    require(box["x"] >= 0 and box["y"] >= 0 and box["width"] > 0 and box["height"] > 0 and
            box["x"] + box["width"] <= 7925 and box["y"] + box["height"] <= 7268,
            "inspection region exceeds the original image")
    require(set(normalized) == set(box), "normalized region fields differ")
    for key, size in (("x", 7925), ("width", 7925), ("y", 7268), ("height", 7268)):
        value = normalized[key]
        require(type(value) in (int, float) and math.isfinite(value) and
                abs(value - box[key] / size) < 1e-12, "normalized/pixel regions differ")
    inspections = proposal.get("image_inspection_order", [])
    require(len(inspections) == 2, "require whole-image inspection followed by one region")
    service = "https://collections.library.yale.edu/iiif/2/1006231/"
    region = ",".join(str(box[key]) for key in ("x", "y", "width", "height"))
    expected = ((service + "full/!4000,4000/0/default.jpg", 4000, 3668),
                (service + region + "/full/0/default.jpg", box["width"], box["height"]))
    for inspection, (url, width, height) in zip(inspections, expected):
        require((inspection.get("url"), inspection.get("width"), inspection.get("height")) ==
                (url, width, height), "image request/dimensions differ from the declared region")
        require(type(inspection.get("bytes")) is int and inspection["bytes"] > 0 and
                isinstance(inspection.get("sha256"), str) and
                re.fullmatch(r"[0-9a-f]{64}", inspection["sha256"]), "invalid inspected image identity")


def select_loci(document):
    rows = []
    for identifier in TARGETS:
        matches = [locus for locus in document.loci if locus.identifier == identifier]
        require(len(matches) == 1 and matches[0].present, f"missing/duplicate present target {identifier}")
        locus = matches[0]
        rows.append({"identifier": locus.identifier, "source_physical_line": locus.line_number,
                     "native_text": locus.text, "kind": locus.kind, "locator": locus.locator,
                     "glyph_alignment": "unresolved"})
    return rows


def report(root=ROOT):
    raw = {name: (root / name).read_bytes() for name in INPUTS}
    proposal = json.loads(raw[PROPOSAL])
    validate_proposal(proposal, raw[PLAN])
    inventory = json.loads(raw["research/pilot/inventory.json"])
    targets = [x for x in inventory["records"] if x["target"] == "85v"]
    require(len(targets) == 1, "original pilot rosette carrier missing/duplicated")
    target = targets[0]
    require(all(proposal[key] == target[key] for key in ("canvas_uri", "yale_label", "image_id")),
            "proposal/pilot carrier differs")
    coverage = json.loads(raw["research/folio-alignment/transcription-image-coverage.json"])
    pages = [x for x in coverage["pages"] if x["page_id"] == "fRos"]
    require(len(pages) == 1, "rosette side-reference missing/duplicated")
    page = pages[0]
    require(proposal["explicit_canvas_sides"] == page["reference"]["folio_sides"] == ["85v", "86r"] and
            proposal["dependency_group"] == page["dependency_group"] == "yale-leaves:85+86" and
            [x["canvas_uri"] for x in page["canvas_matches"]] == [proposal["canvas_uri"]],
            "shared carrier/dependency differs")
    selected = [(source, doc) for source, doc in load_sources(root) if source["id"] in EDITIONS]
    require(len(selected) == len(EDITIONS) and {s["id"] for s, _ in selected} == set(EDITIONS),
            "require both exact source editions")
    rows = []
    for source, document in selected:
        require(document.alphabet == EDITIONS[source["id"]], "source alphabet differs")
        rows.append({"id": source["id"], "alphabet": document.alphabet,
                     "sha256": source["sha256"], "source_url": source["url"],
                     "loci": select_loci(document)})
    return {"schema_version": 1, "scope": "Fixed native records for a provisional image-layout review",
            "apply_to_statistics": False, "verified_locus_crosswalk": None,
            "input_pins": {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()},
            "proposal": PROPOSAL, "target_identifiers": list(TARGETS),
            "canvas_uri": proposal["canvas_uri"], "dependency_group": proposal["dependency_group"],
            "editions": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        catalog = json.loads((ROOT / "data/transliterations.json").read_text())
        protected = {(ROOT / name).resolve() for name in INPUTS}
        protected.update((ROOT / source["path"]).resolve() for source in catalog["sources"])
        if args.output:
            require(not any(args.output.resolve() == path or
                    (args.output.exists() and path.exists() and args.output.samefile(path))
                    for path in protected), "output must not overwrite an input or plan")
        result = report()
        if args.check:
            require(result == json.loads(args.check.read_text()), "committed checklist differs")
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        elif not args.check:
            print(rendered, end="")
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"rosette review failed: {error}\n")
    if args.check:
        print("Pinned rosette checklist verified; glyph alignment remains unresolved.")


if __name__ == "__main__":
    main()
