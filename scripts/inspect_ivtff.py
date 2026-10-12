#!/usr/bin/env python3
"""Audit extra transcription editions with the repository's accepted IVTFF reader.

Uses existing pinned ZL/IT sources and locally downloaded GC/RF editions.
No network requests; aggregate JSON contains no manuscript text payloads.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    from .ivtff import parse_ivtff, without_free_comments
except ImportError:
    from ivtff import parse_ivtff, without_free_comments

ROOT = Path(__file__).resolve().parents[1]
FEATURES = {
    "uncertain_space_marker": lambda text: "," in text,
    "alternative_reading_marker": lambda text: bool(re.search(r"\[[^\]]*:[^\]]*\]", text)),
    "illegible_character_marker": lambda text: "?" in text,
    "extended_character_code": lambda text: bool(re.search(r"@[0-9]{3};", text)),
    "drawing_intrusion_marker": lambda text: "<->" in text or "<~>" in text,
    "paragraph_start_marker": lambda text: "<%>" in text,
    "paragraph_end_marker": lambda text: "<$>" in text,
}


def repository_path(root, relative):
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("Catalog paths must stay inside the repository root")
    return resolved


def summarize(document, data):
    present = [record for record in document.loci if record.present]
    features = Counter({name: 0 for name in FEATURES})
    for record in present:
        text = without_free_comments(record.text)
        for name, predicate in FEATURES.items():
            features[name] += int(predicate(text))
    return {
        "header": document.header,
        "alphabet": document.alphabet,
        "page_declaration_count": len(document.pages),
        "declared_locus_record_count": len(document.loci),
        "present_locus_record_count": len(present),
        "explicitly_nonexistent_locus_identifiers": [r.identifier for r in document.loci if not r.present],
        "locus_subtype_counts_in_present_records": dict(sorted(Counter(r.kind for r in present).items())),
        "relation_marker_counts_in_declared_records": dict(sorted(Counter(r.locator for r in document.loci).items())),
        "records_containing_markers_in_present_records_outside_comments": dict(sorted(features.items())),
        "physical_line_count": len(data.decode("ascii").splitlines()),
        "text_payloads_published": False,
    }


def audit_registry(registry, input_directory, root=ROOT):
    catalog = json.loads(repository_path(root, registry["base_catalog"]).read_text(encoding="utf-8"))
    requested = registry["base_source_ids"]
    sources = {source["id"]: source for source in catalog["sources"]}
    if len(sources) != len(catalog["sources"]) or len(set(requested)) != len(requested):
        raise ValueError("Duplicate base source identifiers")
    entries = []
    for ident in requested:
        source = sources[ident]
        entries.append((dict(source, edition=source["header_version_statement"]), repository_path(root, source["path"])))
    for entry in registry["editions"]:
        filename = entry["filename"]
        if Path(filename).name != filename or filename in {".", ".."}:
            raise ValueError("Edition filename must be a single local filename")
        entries.append((entry, input_directory / filename))
    if len({entry["id"] for entry, _ in entries}) != len(entries):
        raise ValueError("Duplicate edition IDs across base and extension catalogs")
    reports, documents = [], {}
    for entry, path in entries:
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"Pinned SHA-256 mismatch for {entry['id']}; review and version changed source bytes")
        document = parse_ivtff(data.decode("ascii"))
        if document.alphabet != entry["alphabet"]:
            raise ValueError(f"Alphabet differs from catalog for {entry['id']}")
        documents[entry["id"]] = document
        reports.append({"id": entry["id"], "edition": entry["edition"],
                        "url": entry["url"], "sha256": digest,
                        "byte_count": len(data), **summarize(document, data)})
    comparisons = []
    for pair in registry.get("exact_record_comparisons", []):
        left, right = (documents[edition] for edition in pair)
        # A transcriber remains part of identity, even for these single-source editions.
        lmap = {(r.page, r.number, r.transcriber): r for r in left.loci if r.present}
        rmap = {(r.page, r.number, r.transcriber): r for r in right.loci if r.present}
        common = lmap.keys() & rmap.keys()
        comparisons.append({
            "editions": pair,
            "shared_present_locus_keys": len(common),
            "left_only_present_locus_keys": len(lmap.keys() - rmap.keys()),
            "right_only_present_locus_keys": len(rmap.keys() - lmap.keys()),
            "shared_records_with_different_native_text": sum(lmap[k].text != rmap[k].text for k in common),
            "interpretation": "Native text retains annotations; the accepted reader removes locator padding and joins wrapped records. This is not a glyph-error rate or independent validation.",
        })
    return {"schema_version": 2, "access_date_local": registry["access_date_local"],
            "timezone": registry["timezone"], "license_statement_url": registry["license_statement_url"],
            "reader": "scripts.ivtff.parse_ivtff (accepted conventional IVTFF 2.0 reader)",
            "normalization": "No tokenization, uncertainty resolution, alphabet conversion, or case folding; accepted reader strips locator padding and joins wrapped records.",
            "editions": reports, "exact_record_comparisons": comparisons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "research/transcriptions/editions.json")
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory holding the three extra edition files")
    parser.add_argument("--output", type=Path, help="Write aggregate audit JSON; omit to print")
    parser.add_argument("--check", type=Path, help="Compare a committed aggregate report")
    args = parser.parse_args()
    try:
        result = audit_registry(json.loads(args.registry.read_text(encoding="utf-8")), args.input_dir)
        if args.check and result != json.loads(args.check.read_text(encoding="utf-8")):
            raise ValueError("Committed aggregate audit differs from the recomputed result")
        serialized = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(serialized, encoding="utf-8")
        elif not args.check:
            print(serialized, end="")
        if args.check:
            print("PASS: all five edition pins and the committed aggregate audit verified.")
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
