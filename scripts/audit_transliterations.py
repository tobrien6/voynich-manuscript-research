"""Verify pinned source bytes and report coverage without interpreting glyphs."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

try:
    from .ivtff import parse_ivtff, without_free_comments
except ImportError:
    from ivtff import parse_ivtff, without_free_comments


ROOT = Path(__file__).resolve().parents[1]


def load_sources(root=ROOT):
    catalog = json.loads((root / "data/transliterations.json").read_text())
    sources = []
    for source in catalog["sources"]:
        data = (root / source["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != source["sha256"] or len(data) != source["bytes"]:
            raise ValueError(f"source bytes do not match catalog: {source['id']}")
        document = parse_ivtff(data.decode("ascii"))
        if document.alphabet != source["alphabet"]:
            raise ValueError(f"alphabet does not match catalog: {source['id']}")
        if any(locus.transcriber is not None for locus in document.loci):
            raise ValueError("this audit requires single-source, non-interlinear files")
        sources.append((source, document))
    return sources


def summarize(source, document):
    existing = [locus for locus in document.loci if locus.present]
    annotations = Counter()
    for locus in existing:
        text = without_free_comments(locus.text)
        annotations.update({
            "uncertain_spaces": text.count(","),
            "alternative_groups": text.count("["),
            "illegible_question_marks": text.count("?"),
            "ligature_groups": text.count("{"),
            "high_ascii_codes": len(re.findall(r"@[0-9]{3};", text)),
            "drawing_intrusions": text.count("<->") + text.count("<~>"),
            "paragraph_starts": text.count("<%>"),
            "paragraph_ends": text.count("<$>"),
        })
    return {
        "id": source["id"], "sha256": source["sha256"], "header": document.header,
        "page_headers": len(document.pages), "records": len(document.loci),
        "present_records": len(existing),
        "explicitly_nonexistent_loci": [locus.identifier for locus in document.loci if not locus.present],
        "present_loci_by_kind": dict(sorted(Counter(locus.kind for locus in existing).items())),
        "present_loci_by_page": dict(sorted(Counter(locus.page for locus in existing).items())),
        "annotation_counts_in_present_loci": dict(sorted(annotations.items())),
    }


def audit(root=ROOT):
    sources = load_sources(root)
    summary = {"schema_version": 1, "method": "structural coverage audit v1",
               "sources": [summarize(*source) for source in sources], "comparisons": []}
    for i, (left_source, left_document) in enumerate(sources):
        left = {locus.key: locus for locus in left_document.loci if locus.present}
        for right_source, right_document in sources[i + 1:]:
            right = {locus.key: locus for locus in right_document.loci if locus.present}
            shared = set(left) & set(right)
            summary["comparisons"].append({
                "left": left_source["id"], "right": right_source["id"],
                "shared_present_loci": len(shared),
                "present_only_in_left": sorted(set(left) - set(right)),
                "present_only_in_right": sorted(set(right) - set(left)),
                "shared_loci_with_different_kind": [
                    {"locus": key, "left": left[key].kind, "right": right[key].kind}
                    for key in sorted(shared) if left[key].kind != right[key].kind
                ],
            })
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path, help="compare a committed report without changing it")
    args = parser.parse_args()
    try:
        report = audit()
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError("committed audit differs from recomputed report")
    except (ValueError, OSError) as error:
        parser.exit(1, f"audit failed: {error}\n")
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered)
    elif not args.check:
        print(rendered, end="")
    if args.check:
        print("Pinned source bytes and committed audit verified.")


if __name__ == "__main__":
    main()
