"""Emit conservative native-Eva token records with explicit spacing policies.

Tokens are encoded transcription strings, not decoded words or manuscript glyph
units. Ambiguous/unreadable/extended records remain visible as exclusions. The
shared reader and source catalog provide provenance and locus identities.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

try:
    from .audit_transliterations import ROOT, load_sources
    from .token_baselines import tokenize as native_token_slots
    from .ivtff import TAG
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from token_baselines import tokenize as native_token_slots
    from ivtff import TAG


INLINE = re.compile(r"<[^<>]*>")
ALPHABETS = {"Eva-", "EvaT"}
DEFAULT_SOURCES = ("ZL3b", "IT2a")
DEFAULT_KINDS = ("P0", "P1")


def tokenize(text, uncertain_spaces):
    if uncertain_spaces not in ("split", "join"):
        raise ValueError("uncertain_spaces must be split or join")
    drawing_count = 0

    def annotation(match):
        nonlocal drawing_count
        tag = match[0]
        if tag in ("<->", "<~>"):
            drawing_count += 1
            return "."
        if tag in ("<%>", "<$>") or tag.startswith("<!") or TAG.fullmatch(tag):
            return ""
        raise ValueError("unsupported inline annotation")

    payload = INLINE.sub(annotation, text)
    if "<" in payload or ">" in payload:
        raise ValueError("malformed inline annotation")
    payload = re.sub(r"\s+", "", payload)
    flags = []
    for marker, reason in (("[", "alternative_reading"), ("?", "unreadable"),
                           ("@", "high_ascii_escape"), ("{", "ligature_braces")):
        if marker in payload:
            flags.append(reason)
    # These characters are notation errors unless opened by their matching form.
    if any(marker in payload for marker in ("]", "}", ";", ":")) and not flags:
        flags.append("unsupported_notation")
    comma_count = payload.count(",")
    tokens = None
    if not flags:
        try:
            # Reuse the existing grammar and boundary handling. Flagged ambiguous
            # loci never reach its first-alternative selection path.
            tokens = [slot.value for slot in native_token_slots(text, uncertain_spaces)]
        except ValueError:
            flags.append("unsupported_token_structure")
        else:
            if not tokens:
                flags.append("empty_token_boundary")
            elif any(not re.fullmatch(r"[A-Za-z]+", token) for token in tokens):
                flags.append("non_plain_eva_character")
    return {
        "tokens": tokens if not flags else None,
        "token_count": len(tokens) if not flags else None,
        "eligible": not flags,
        "exclusion_reasons": flags,
        "uncertain_space_count": comma_count,
        "drawing_interruption_count": drawing_count,
    }


def adapt(source, document, uncertain_spaces, kinds=DEFAULT_KINDS):
    if document.alphabet not in ALPHABETS:
        raise ValueError(f"{source['id']}: unsupported alphabet {document.alphabet}; define a unit mapping first")
    records = []
    for locus in document.loci:
        result = {"tokens": None, "token_count": None, "eligible": False,
                  "exclusion_reasons": [], "uncertain_space_count": None,
                  "drawing_interruption_count": None}
        if not locus.present:
            result["exclusion_reasons"].append("nonexistent_locus")
        if locus.kind not in kinds:
            result["exclusion_reasons"].append("unselected_locus_kind")
        if not result["exclusion_reasons"]:
            result = tokenize(locus.text, uncertain_spaces)
        records.append({
            "source_id": source["id"], "page_id": locus.page,
            "locus_key": locus.key, "locus_identifier": locus.identifier,
            "locus_type": locus.kind, "locator": locus.locator,
            "transcriber": locus.transcriber, "source_line_number": locus.line_number,
            "variables": locus.variables, **result,
        })
    return records


def build(uncertain_spaces, source_ids=DEFAULT_SOURCES, kinds=DEFAULT_KINDS, root=ROOT):
    if uncertain_spaces not in ("split", "join"):
        raise ValueError("uncertain_spaces must be split or join")
    if not source_ids or len(source_ids) != len(set(source_ids)):
        raise ValueError("source IDs must be nonempty and unique")
    if not kinds or any(not re.fullmatch(r"[PLCR][a-z0-9]", kind) for kind in kinds):
        raise ValueError("select valid complete locus types")
    available = {source["id"]: (source, document) for source, document in load_sources(root)}
    unknown = set(source_ids) - set(available)
    if unknown:
        raise ValueError(f"unknown source IDs: {', '.join(sorted(unknown))}")
    records, provenance = [], []
    for source_id in source_ids:
        source, document = available[source_id]
        provenance.append({"id": source_id, "sha256": source["sha256"],
                           "alphabet": document.alphabet, "url": source["url"],
                           "path": source["path"]})
        records.extend(adapt(source, document, uncertain_spaces, kinds))
    reasons = Counter(reason for record in records for reason in record["exclusion_reasons"])
    return {
        "schema_version": 1, "adapter_version": "plain-eva-v1",
        "analysis_unit": "transcription_locus",
        "sources": provenance,
        "processing": {"uncertain_space_policy": uncertain_spaces,
                       "selected_locus_types": list(kinds),
                       "token_representation": "native Eva ASCII letters; case preserved",
                       "ambiguity_policy": "exclude entire selected locus with explicit reasons",
                       "drawing_interruption_policy": "separator under both comma policies"},
        "summary": {"records": len(records),
                    "eligible_records": sum(record["eligible"] for record in records),
                    "excluded_records": sum(not record["eligible"] for record in records),
                    "exclusion_reason_record_counts": dict(sorted(reasons.items()))},
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uncertain-spaces", required=True, choices=("split", "join"))
    parser.add_argument("--source", action="append", help="Repeat to select pinned source IDs; default ZL3b and IT2a")
    parser.add_argument("--kind", action="append", help="Repeat for complete locus types; default P0 and P1")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = build(args.uncertain_spaces, args.source or DEFAULT_SOURCES, args.kind or DEFAULT_KINDS)
    except (ValueError, OSError) as error:
        parser.exit(1, f"token adapter failed: {error}\n")
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {result['summary']['records']} locus records; {result['summary']['eligible_records']} eligible under {args.uncertain_spaces} policy.")


if __name__ == "__main__":
    main()
