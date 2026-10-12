"""Verify an externally downloaded paper source bundle against its inventory.

No TeX, bibliography or analysis code is executed. Archive paths are not extracted.
Optional PDF attachment checks use the locally installed Poppler pdfdetach.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD = ROOT / "research/literature/amancio-source-inventory.json"


def pdf_attachment_count(data):
    if not data.startswith(b"%PDF-"):
        raise ValueError("recorded PDF member lacks a PDF header")
    with tempfile.TemporaryDirectory(prefix="paper-source-pdf-") as directory:
        path = Path(directory) / "figure.pdf"
        path.write_bytes(data)
        result = subprocess.run(["pdfdetach", "-list", str(path)], check=True,
                                capture_output=True, text=True)
    match = re.match(r"\s*(\d+) embedded files\b", result.stdout)
    if not match:
        raise ValueError("unrecognized pdfdetach attachment inventory")
    return int(match[1])


def verify_archive(data, record, pdf_checker=None):
    if record.get("record_version") != 1:
        raise ValueError("unsupported paper-source inventory version")
    if (len(data) != record["archive_bytes"] or
            hashlib.sha256(data).hexdigest() != record["archive_sha256"]):
        raise ValueError("downloaded source archive differs from the recorded bytes")
    expected = record["members"]
    names = [entry["name"] for entry in expected]
    if len(names) != len(set(names)):
        raise ValueError("record contains duplicate member names")
    checked_pdfs = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
        members = archive.getmembers()
        if [member.name for member in members] != names:
            raise ValueError("paper source member inventory/order differs")
        for member, entry in zip(members, expected, strict=True):
            name = member.name
            if (not member.isfile() or PurePosixPath(name).is_absolute() or "\\" in name
                    or any(part in ("", ".", "..") for part in name.split("/"))):
                raise ValueError("ambiguous or nonregular source archive member")
            if member.size != entry["bytes"]:
                raise ValueError(f"source member length differs: {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("source member is unreadable")
            payload = stream.read(entry["bytes"] + 1)
            if (len(payload) != entry["bytes"] or
                    hashlib.sha256(payload).hexdigest() != entry["sha256"]):
                raise ValueError(f"source member bytes differ: {name}")
            if pdf_checker is not None and entry["role"] == "figure_pdf":
                actual = pdf_checker(payload)
                expected_count = record["pdf_attachment_observations"]["embedded_files_by_member"][name]
                if actual != expected_count:
                    raise ValueError(f"PDF attachment count differs: {name}")
                checked_pdfs[name] = actual
    return {
        "archive_sha256": record["archive_sha256"], "verified_regular_members": len(expected),
        "verified_member_bytes": sum(entry["bytes"] for entry in expected),
        "pdf_attachment_counts_checked": checked_pdfs,
        "scope": "Byte/member identity and requested PDF attachment counts; text observations remain separately inspected evidence",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD)
    parser.add_argument("--check-pdf-attachments", action="store_true")
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text())
        result = verify_archive(args.archive.read_bytes(), record,
                                pdf_attachment_count if args.check_pdf_attachments else None)
    except (OSError, ValueError, KeyError, tarfile.TarError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"paper-source inventory verification failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
