"""Compare pinned H/IT page envelopes without aligning or normalizing text."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import zipfile

try:
    from .audit_historical_interlinear import parse_historical, read_pinned_archive
    from .inspect_ivtff import repository_path
    from .ivtff import parse_ivtff
except ImportError:
    from audit_historical_interlinear import parse_historical, read_pinned_archive
    from inspect_ivtff import repository_path
    from ivtff import parse_ivtff


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_CATALOG = "data/historical/interlinear-16e6.json"
MODERN_CATALOG = "data/transliterations.json"


def ordered_digest(identifiers):
    """Hash a source-ordered identifier array, including native punctuation."""
    return hashlib.sha256(json.dumps(identifiers, separators=(",", ":"))
                          .encode("ascii")).hexdigest()


def compare_pages(historical, modern):
    """Only exact page strings define shared groups; totals do not align rows."""
    historical = [record for record in historical if record.transcriber == "H"]
    if not historical or not modern.loci:
        raise ValueError("both selected sources must contain records")
    if any(locus.transcriber is not None for locus in modern.loci):
        raise ValueError("modern input must be a single-source export")
    old, new = defaultdict(list), defaultdict(list)
    for record in historical:
        old[record.page].append(record)
    for locus in modern.loci:
        new[locus.page].append(locus)
    present = [locus for locus in modern.loci if locus.present]
    old_pages = set(old)
    new_pages = {locus.page for locus in present}
    shared = old_pages & new_pages
    profiles, differing = [], []
    for page in sorted(old_pages | set(modern.pages)):
        old_records, new_records = old[page], new[page]
        new_present = [locus for locus in new_records if locus.present]
        is_shared = page in shared
        difference = len(new_present) - len(old_records) if is_shared else None
        profile = {
            "page_id": page,
            "status": ("shared_exact_page_id" if is_shared else
                       "historical_only" if page in old_pages else
                       "modern_only" if page in new_pages else
                       "modern_nonexistent_only" if new_records else "modern_header_only"),
            "historical_H_records": len(old_records),
            "historical_native_units": dict(sorted(Counter(r.unit for r in old_records).items())),
            "historical_ordered_locator_sha256": ordered_digest([r.locator for r in old_records]),
            "modern_declared_loci": len(new_records),
            "modern_present_loci": len(new_present),
            "modern_present_kinds": dict(sorted(Counter(r.kind for r in new_present).items())),
            "modern_ordered_declared_identifier_sha256": ordered_digest([r.identifier for r in new_records]),
            "modern_nonexistent_loci": [r.identifier for r in new_records if not r.present],
            "modern_minus_historical_present_count": difference,
        }
        profiles.append(profile)
        if is_shared and difference:
            differing.append({
                "page_id": page, "historical_H_records": len(old_records),
                "modern_present_loci": len(new_present), "difference": difference,
                "historical_locators_in_source_order": [r.locator for r in old_records],
                "modern_declared_identifiers_in_source_order": [r.identifier for r in new_records],
                "modern_nonexistent_loci": profile["modern_nonexistent_loci"],
            })
    return {
        "summary": {
            "historical_H_records": len(historical), "historical_record_pages": len(old_pages),
            "modern_declared_loci": len(modern.loci), "modern_present_loci": len(present),
            "modern_page_headers": len(modern.pages),
            "modern_present_pages": len(new_pages),
            "modern_pages_without_present_loci": sorted(set(modern.pages) - new_pages),
            "global_present_counts_equal": len(historical) == len(present),
            "shared_exact_page_ids": len(shared),
            "shared_pages_with_equal_present_counts": len(shared) - len(differing),
            "shared_pages_with_different_present_counts": len(differing),
            "historical_only_present_page_ids": sorted(old_pages - new_pages),
            "modern_only_present_page_ids": sorted(new_pages - old_pages),
            "modern_nonexistent_loci": [r.identifier for r in modern.loci if not r.present],
            "historical_ordered_locator_sha256": ordered_digest([r.locator for r in historical]),
            "modern_ordered_declared_identifier_sha256": ordered_digest([r.identifier for r in modern.loci]),
        },
        "page_profiles": profiles, "different_count_pages": differing,
    }


def load_inputs(root):
    historical_path = repository_path(root, HISTORICAL_CATALOG)
    modern_path = repository_path(root, MODERN_CATALOG)
    historical_raw, modern_raw = historical_path.read_bytes(), modern_path.read_bytes()
    historical_catalog, modern_catalog = json.loads(historical_raw), json.loads(modern_raw)
    if historical_catalog.get("schema_version") != 1 or modern_catalog.get("schema_version") != 1:
        raise ValueError("unsupported source catalog version")
    if historical_catalog["selected_transcriber"] != "H":
        raise ValueError("this comparison requires historical H")
    candidates = [s for s in modern_catalog["sources"] if s["id"] == "IT2a"]
    if len(candidates) != 1:
        raise ValueError("modern catalog must select exactly one IT2a source")
    source = candidates[0]
    archive_path = repository_path(root, historical_catalog["path"])
    modern_source_path = repository_path(root, source["path"])
    archive_raw, modern_source_raw = archive_path.read_bytes(), modern_source_path.read_bytes()
    member = read_pinned_archive(archive_raw, historical_catalog)
    if (len(modern_source_raw) != source["bytes"] or
            hashlib.sha256(modern_source_raw).hexdigest() != source["sha256"]):
        raise ValueError("modern source bytes differ from catalog")
    modern = parse_ivtff(modern_source_raw.decode("ascii"))
    if modern.alphabet != source["alphabet"]:
        raise ValueError("modern alphabet differs from catalog")
    historical, _ = parse_historical(member)
    pins = {
        "historical": {key: historical_catalog[key] for key in
                       ("id", "archive_sha256", "archive_bytes", "member", "member_sha256", "member_bytes")},
        "modern": {key: source[key] for key in ("id", "sha256", "bytes", "alphabet", "url")},
        "catalog_sha256": {HISTORICAL_CATALOG: hashlib.sha256(historical_raw).hexdigest(),
                           MODERN_CATALOG: hashlib.sha256(modern_raw).hexdigest()},
    }
    protected = {historical_path, modern_path, archive_path, modern_source_path}
    protected.update(Path(function.__code__.co_filename).resolve() for function in
                     (parse_historical, read_pinned_archive, parse_ivtff, repository_path, load_inputs))
    return historical, modern, pins, protected


def build_report(historical, modern, pins):
    return {
        "schema_version": 1, "method": "historical-H-modern-IT-exact-page-envelope-v1",
        "scope": "Source envelope counts and identifier order; no text comparison, normalization or locus crosswalk",
        "inputs": pins, **compare_pages(historical, modern),
    }


def audit(root=ROOT):
    historical, modern, pins, _ = load_inputs(root)
    return build_report(historical, modern, pins)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        historical, modern, pins, protected = load_inputs(ROOT)
        if args.output and args.output.resolve() in protected:
            raise ValueError("output must not overwrite an input or reader")
        report = build_report(historical, modern, pins)
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError("page-envelope audit differs from committed report")
        serialized = json.dumps(report, indent=2) + "\n"
        if args.output:
            args.output.write_text(serialized, encoding="utf-8")
        elif not args.check:
            print(serialized, end="")
    except (ValueError, KeyError, OSError, UnicodeError, zipfile.BadZipFile) as error:
        parser.exit(1, f"page-envelope audit failed: {error}\n")
    if args.check:
        print("historical/modern page-envelope audit reproduces")


if __name__ == "__main__":
    main()
