"""Explore lossy lowercase notation agreement without claiming text identity."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import string
import zipfile

try:
    from .audit_historical_modern_pages import load_inputs
    from .audit_historical_interlinear import remove_comments
    from .ivtff import FREE_COMMENT, TAG, without_free_comments
except ImportError:
    from audit_historical_modern_pages import load_inputs
    from audit_historical_interlinear import remove_comments
    from ivtff import FREE_COMMENT, TAG, without_free_comments


ROOT = Path(__file__).resolve().parents[1]
LOWERCASE = frozenset(string.ascii_lowercase)


def project_body(body, historical):
    """Retain only a-z outside human comments and defined modern text tags."""
    if historical:
        visible, comment_count = remove_comments(body)
        payload, metadata_count = visible, 0
    else:
        comment_count = len(FREE_COMMENT.findall(body))
        visible = without_free_comments(body)
        metadata_count = len(TAG.findall(visible))
        payload = TAG.sub("", visible)
    stream = "".join(char for char in payload if char in LOWERCASE)
    omitted = Counter(visible)
    omitted.subtract(Counter(stream))
    return stream, +omitted, comment_count, metadata_count


def page_projection(records, historical):
    streams, omitted, comments, metadata = [], Counter(), 0, 0
    for record in records:
        stream, discarded, comment_count, metadata_count = project_body(
            record.body if historical else record.text, historical)
        streams.append(stream)
        omitted.update(discarded)
        comments += comment_count
        metadata += metadata_count
    joined = "".join(streams)  # Deliberately erases every record boundary.
    frequencies = dict(sorted(Counter(joined).items()))
    return joined, {
        "selected_records": len(records), "projected_lowercase_symbols": len(joined),
        "projected_stream_sha256": hashlib.sha256(joined.encode("ascii")).hexdigest(),
        "projected_frequencies": frequencies,
        "omitted_characters_outside_human_comments": dict(sorted(omitted.items())),
        "removed_human_comment_occurrences": comments,
        "removed_modern_text_metadata_tags": metadata,
    }


def compare_projections(historical, modern):
    old, new = defaultdict(list), defaultdict(list)
    for record in historical:
        if record.transcriber == "H":
            old[record.page].append(record)
    for locus in modern.loci:
        if locus.transcriber is not None:
            raise ValueError("modern projection requires a single-source export")
        if locus.present:
            new[locus.page].append(locus)
    if not old or not new:
        raise ValueError("both selections require record-bearing pages")
    old_pages, new_pages = set(old), set(new)
    profiles = []
    for page in sorted(old_pages | new_pages):
        left, left_profile = page_projection(old[page], True)
        right, right_profile = page_projection(new[page], False)
        shared = bool(old[page] and new[page])
        nonempty = bool(shared and left and right)
        profiles.append({
            "page_id": page,
            "status": ("comparable_nonempty_projection" if nonempty else
                       "shared_empty_projection" if shared else "unmatched_page_id"),
            "historical_H": left_profile if old[page] else None,
            "modern_IT2a_present": right_profile if new[page] else None,
            "lowercase_streams_equal": left == right if nonempty else None,
            "lowercase_frequencies_equal": Counter(left) == Counter(right) if nonempty else None,
        })
    comparable = [p for p in profiles if p["status"] == "comparable_nonempty_projection"]
    nonexistent, declared_diagnostics = [], []
    missing_pages = sorted({locus.page for locus in modern.loci if not locus.present})
    for locus in modern.loci:
        if not locus.present:
            _, projection = page_projection([locus], False)
            nonexistent.append({"page_id": locus.page, "identifier": locus.identifier,
                                "used_in_primary_comparison": False, "projection": projection})
    for page in missing_pages:
        left, _ = page_projection(old[page], True)
        declared = [locus for locus in modern.loci if locus.page == page]
        right, projection = page_projection(declared, False)
        declared_diagnostics.append({
            "page_id": page, "status": "declared-envelope diagnostic, not manuscript content inclusion",
            "modern_declared_projection": projection,
            "including_nonexistent_lowercase_stream_equals_historical": left == right if left and right else None,
        })
    return {
        "summary": {
            "shared_record_bearing_page_ids": len(old_pages & new_pages),
            "comparable_nonempty_page_ids": len(comparable),
            "shared_empty_projection_page_ids": [p["page_id"] for p in profiles if p["status"] == "shared_empty_projection"],
            "equal_lowercase_stream_page_ids": [p["page_id"] for p in comparable if p["lowercase_streams_equal"]],
            "different_lowercase_stream_page_ids": [p["page_id"] for p in comparable if not p["lowercase_streams_equal"]],
            "same_frequencies_different_stream_page_ids": [p["page_id"] for p in comparable if p["lowercase_frequencies_equal"] and not p["lowercase_streams_equal"]],
            "historical_only_page_ids": sorted(old_pages - new_pages),
            "modern_only_page_ids": sorted(new_pages - old_pages),
        },
        "page_profiles": profiles,
        "modern_nonexistent_projection_inventory": nonexistent,
        "declared_envelope_diagnostics": declared_diagnostics,
    }


def build_report(historical, modern, pins):
    return {
        "schema_version": 1, "method": "exploratory-ascii-lowercase-projection-v1",
        "scope": "Lossy notation projection; equality does not establish text, glyph or locus identity",
        "rules": {
            "historical_selection": "native transcriber H, including padding-only envelopes",
            "modern_selection": "IT2a present loci; nonexistent loci excluded",
            "comments": "historical balanced curly comments; modern IVTFF free comments",
            "metadata": "modern defined <@X=value> text tags removed",
            "projection": "retain only lowercase ASCII a-z, concatenate in native source order per exact page ID",
            "losses": "record boundaries, spaces, word breaks, unknown/rare signs, case and other notation",
            "empty_projection": "not comparable; equality fields null",
            "inference_limit": "Neither equal streams nor equal frequencies authorize a crosswalk or full text equality",
        },
        "inputs": pins, **compare_projections(historical, modern),
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
        protected.add(Path(__file__).resolve())
        if args.output:
            output = args.output.resolve()
            if output in protected or (output.exists() and any(
                    output.samefile(source) for source in protected if source.exists())):
                raise ValueError("output must not overwrite an input or reader")
        result = build_report(historical, modern, pins)
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("lowercase projection differs from committed report")
        serialized = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.write_text(serialized, encoding="utf-8")
        elif not args.check:
            print(serialized, end="")
    except (ValueError, KeyError, OSError, UnicodeError, zipfile.BadZipFile) as error:
        parser.exit(1, f"lowercase projection failed: {error}\n")
    if args.check:
        print("historical/modern lowercase projection reproduces")


if __name__ == "__main__":
    main()
