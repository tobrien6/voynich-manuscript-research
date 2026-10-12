"""Compare annotation coverage using the shared reader and pinned source catalog.

Results are file observations, not transcription accuracy or glyph counts.
No source text is included in the generated report.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

try:
    from .audit_transliterations import ROOT, load_sources
except ImportError:
    from audit_transliterations import ROOT, load_sources


INLINE = re.compile(r"<[^<>]*>")
MARKERS = (
    "paragraph_start", "paragraph_end", "drawing_interruption",
    "free_inline_comment", "text_tag", "uncertain_space_comma",
    "apparent_space_period", "alternative_group", "ligature_group",
    "high_ascii_escape",
)


def annotation_counts(body):
    """Exclude comments/tags from text-marker counts; retain dedicated counts."""
    counts = Counter({name: 0 for name in MARKERS})
    tags = INLINE.findall(body)
    payload = INLINE.sub("", body)
    if "<" in payload or ">" in payload:
        raise ValueError("malformed inline annotation")
    for tag in tags:
        if tag == "<%>":
            counts["paragraph_start"] += 1
        elif tag == "<$>":
            counts["paragraph_end"] += 1
        elif tag in ("<->", "<~>"):
            counts["drawing_interruption"] += 1
        elif tag.startswith("<!"):
            counts["free_inline_comment"] += 1
        elif tag.startswith("<@"):
            counts["text_tag"] += 1
        else:
            raise ValueError("unsupported inline annotation")
    counts["uncertain_space_comma"] += payload.count(",")
    counts["apparent_space_period"] += payload.count(".")
    counts["alternative_group"] += len(re.findall(r"\[[^\[\]]*\]", payload))
    counts["ligature_group"] += len(re.findall(r"\{[^{}]*\}", payload))
    counts["high_ascii_escape"] += len(re.findall(r"@[0-9]{3};", payload))
    return counts, Counter(str(len(run)) for run in re.findall(r"\?+", payload))


def profile(source, document):
    present = [locus for locus in document.loci if locus.present]
    annotations = Counter({name: 0 for name in MARKERS})
    unreadable_runs = Counter()
    for locus in present:
        markers, runs = annotation_counts(locus.text)
        annotations.update(markers)
        unreadable_runs.update(runs)
    generic = Counter(locus.kind[0] for locus in present)
    return {
        "id": source["id"],
        "sha256": source["sha256"],
        "byte_count": source["bytes"],
        "header": document.header,
        "alphabet": document.alphabet,
        "page_header_count": len(document.pages),
        "all_locus_record_count": len(document.loci),
        "present_locus_record_count": len(present),
        "explicitly_nonexistent_loci": [locus.identifier for locus in document.loci if not locus.present],
        "generic_locus_counts_in_present_records": dict(sorted(generic.items())),
        "complete_locus_counts_in_present_records": dict(sorted(Counter(l.kind for l in present).items())),
        "annotation_occurrences_in_present_records": dict(sorted(annotations.items())),
        "unreadable_run_occurrences_by_length": dict(sorted(unreadable_runs.items())),
    }


def audit(root=ROOT):
    return {
        "audit_version": 1,
        "scope": "Present-record structural and annotation audit; no normalization or decoding",
        "profiles": {source["id"]: profile(source, document) for source, document in load_sources(root)},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        result = audit()
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("committed comparator profile differs from recomputed report")
    except (ValueError, OSError) as error:
        parser.exit(1, f"comparator audit failed: {error}\n")
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    elif not args.check:
        print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        print("Pinned comparator bytes and present-record annotation profiles verified.")


if __name__ == "__main__":
    main()
