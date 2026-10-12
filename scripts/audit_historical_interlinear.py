"""Audit a pinned 1.6e6 EVMT archive without tokenization or decoding.

This envelope differs from IVTFF 2.0: unit tags are explicit and curly braces
are comments. No archive entry is extracted to the filesystem.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PAGE = r"f[1-9][0-9]*[rv][0-9]*"
UNIT = r"[A-Za-z][A-Za-z0-9]*"
RECORD = re.compile(rf"<({PAGE})\.({UNIT})\.([0-9]+[a-e]?);([A-Z])>[ \t]+(.+)")
HEADER = re.compile(rf"<(f0\.{UNIT}|{PAGE}(?:\.{UNIT})?)>[ \t]+\{{[^{{}}]*\}}")
MARKERS = {".": "period", ",": "comma", "-": "hyphen", "=": "equals",
           "!": "exclamation", "%": "percent", "*": "asterisk"}


@dataclass(frozen=True)
class HistoricalRecord:
    locator: str
    page: str
    unit: str
    line: str
    transcriber: str
    body: str
    physical_line: int


def remove_comments(body):
    """Strip only balanced, nonnested historical curly comments."""
    payload = re.sub(r"\{[^{}]*\}", "", body)
    if "{" in payload or "}" in payload:
        raise ValueError("unbalanced or nested historical inline comment")
    return payload, body.count("{")


def parse_historical(data):
    """Read the release's native envelopes; unsupported lines fail explicitly."""
    # Latin-1 is a reversible byte-to-code-point transport, not a claim that
    # every author's comment was encoded in that character set.
    lines = data.decode("latin-1").split("\n")
    if lines[-1] == "":
        lines.pop()
    counts = Counter({key: 0 for key in ("physical_lines", "blank_lines",
        "comment_lines", "active_page_headers", "active_unit_headers",
        "passive_page_headers", "passive_unit_headers", "documentation_headers")})
    records, seen, page_headers, unit_headers = [], set(), set(), set()
    current_page = None
    for number, raw in enumerate(lines, 1):
        counts["physical_lines"] += 1
        line = raw.removesuffix("\r").strip()
        if not line:
            counts["blank_lines"] += 1
            continue
        passive = line.startswith("##")
        if line.startswith("#") and not passive:
            counts["comment_lines"] += 1
            continue
        header = HEADER.fullmatch(line[2:].strip() if passive else line)
        if header:
            locator = header[1]
            if locator.startswith("f0."):
                if not passive:
                    raise ValueError(f"active documentation header at line {number}")
                counts["documentation_headers"] += 1
            elif "." in locator:
                page, unit = locator.split(".")
                if page != current_page:
                    raise ValueError(f"unit outside its page at line {number}")
                if (page, unit) in unit_headers:
                    raise ValueError(f"duplicate unit header at line {number}")
                unit_headers.add((page, unit))
                counts[("passive" if passive else "active") + "_unit_headers"] += 1
            else:
                if locator in page_headers:
                    raise ValueError(f"duplicate page header at line {number}")
                page_headers.add(locator)
                current_page = locator
                counts[("passive" if passive else "active") + "_page_headers"] += 1
            continue
        match = RECORD.fullmatch(line)
        if not match:
            raise ValueError(f"unsupported historical envelope at line {number}")
        page, unit, line_id, transcriber, body = match.groups()
        if page != current_page or (page, unit) not in unit_headers:
            raise ValueError(f"record lacks page/unit context at line {number}")
        key = (page, unit, line_id, transcriber)
        if key in seen:
            raise ValueError(f"duplicate historical record at line {number}")
        seen.add(key)
        remove_comments(body)  # Validate even unselected transcriber records.
        locator = f"{page}.{unit}.{line_id};{transcriber}"
        records.append(HistoricalRecord(locator, page, unit, line_id,
                                        transcriber, body, number))
    if not records:
        raise ValueError("historical input contains no records")
    return records, dict(counts)


def read_pinned_archive(data, catalog):
    """Verify outer bytes before decompression, then exact member identity."""
    if (len(data) != catalog["archive_bytes"] or
            hashlib.sha256(data).hexdigest() != catalog["archive_sha256"]):
        raise ValueError("historical archive bytes differ from catalog")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        if len(entries) != 1 or entries[0].filename != catalog["member"]:
            raise ValueError("historical archive member inventory differs")
        if entries[0].file_size != catalog["member_bytes"]:
            raise ValueError("historical member length differs from catalog")
        member = archive.read(entries[0])
    if hashlib.sha256(member).hexdigest() != catalog["member_sha256"]:
        raise ValueError("historical member bytes differ from catalog")
    return member


def summarize(records, counts, transcriber):
    if not re.fullmatch(r"[A-Z]", transcriber):
        raise ValueError("transcriber must be one native uppercase code")
    selected = [r for r in records if r.transcriber == transcriber]
    if not selected:
        raise ValueError("selected historical transcriber has no records")
    markers = Counter({name: 0 for name in MARKERS.values()})
    comments, nonascii_raw, nonascii_payload = 0, 0, 0
    for record in selected:
        payload, count = remove_comments(record.body)
        comments += count
        markers.update({name: payload.count(char) for char, name in MARKERS.items()})
        nonascii_raw += any(ord(c) > 127 for c in record.body)
        nonascii_payload += any(ord(c) > 127 for c in payload)
    locators = json.dumps([r.locator for r in selected], separators=(",", ":")).encode("ascii")
    return {
        "line_classification": counts,
        "all_native_records": len(records),
        "all_record_page_ids": len({r.page for r in records}),
        "all_record_logical_units": len({(r.page, r.unit) for r in records}),
        "records_by_transcriber": dict(sorted(Counter(r.transcriber for r in records).items())),
        "selected": {
            "transcriber": transcriber, "records": len(selected),
            "record_page_count": len({r.page for r in selected}),
            "record_logical_unit_count": len({(r.page, r.unit) for r in selected}),
            "records_by_native_unit_tag": dict(sorted(Counter(r.unit for r in selected).items())),
            "ordered_locator_sha256": hashlib.sha256(locators).hexdigest(),
            "curly_comment_occurrences": comments,
            "marker_occurrences_outside_comments": dict(sorted(markers.items())),
            "records_with_nonascii_in_raw_body": nonascii_raw,
            "records_with_nonascii_outside_comments": nonascii_payload,
        },
    }


def audit(root=ROOT):
    catalog = json.loads((root / "data/historical/interlinear-16e6.json").read_text())
    if catalog.get("schema_version") != 1:
        raise ValueError("unsupported historical catalog version")
    data = (root / catalog["path"]).read_bytes()
    member = read_pinned_archive(data, catalog)
    records, counts = parse_historical(member)
    return {
        "audit_version": 1,
        "scope": "Native historical record/notation inventory; no tokenization, mapping or published-result replication",
        "source": {key: catalog[key] for key in ("id", "archive_sha256", "archive_bytes",
            "member", "member_sha256", "member_bytes", "historical_identity_status")},
        "structure": summarize(records, counts, catalog["selected_transcriber"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        catalog_path = ROOT / "data/historical/interlinear-16e6.json"
        catalog = json.loads(catalog_path.read_text())
        protected = {catalog_path.resolve(), (ROOT / catalog["path"]).resolve()}
        if args.output and args.output.resolve() in protected:
            raise ValueError("output must not overwrite the catalog or source archive")
        result = audit(ROOT)
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("historical audit differs from committed report")
        serialized = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.write_text(serialized, encoding="utf-8")
        elif not args.check:
            print(serialized, end="")
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f"historical intake failed: {error}\n")
    if args.check:
        print("historical interlinear audit reproduces")


if __name__ == "__main__":
    main()
