#!/usr/bin/env python3
"""Replay cached adapter inputs and verify the historical position baseline.

Preserves the baseline report, protocol and engine bytes pinned by downstream
studies. Verification produces a separate receipt, without new measurements.
"""

import argparse
import hashlib
from pathlib import Path
import sys

try:
    from . import run_locus_position_baseline as engine
    from .audit_eva_token_coverage import encoded, load_json, verify_cached
except ImportError:
    import run_locus_position_baseline as engine
    from audit_eva_token_coverage import encoded, load_json, verify_cached


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "research/baselines/locus-position-results.json"
ENGINE_FILES = ("run_locus_position_baseline.py", "locus_position_baseline.py", "shuffle_token_lines.py")
VERIFIER_FILES = ("verify_locus_position_baseline.py", "audit_eva_token_coverage.py", "eva_token_adapter.py",
                  "audit_transliterations.py", "ivtff.py", "token_baselines.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def protect_output(output, paths, root=ROOT):
    catalog_path = root / "data/transliterations.json"
    catalog = load_json(catalog_path.read_bytes())
    inputs = [*paths.values(), BASELINE, engine.PROTOCOL, catalog_path,
              *(root / source["path"] for source in catalog["sources"])]
    folders = (root / "data/raw", root / "scripts")
    resolved = output.resolve()
    require(not any(resolved.is_relative_to(folder.resolve()) for folder in folders)
            and not any(resolved == path.resolve() for path in inputs),
            "Receipt must not replace an analysis input, source, or verifier script")
    if output.exists():
        inputs.extend(path for folder in folders for path in folder.rglob("*") if path.is_file())
        require(not any(path.exists() and output.samefile(path) for path in inputs),
                "Receipt must not replace an input or script through a hardlink alias")


def verify(raw, root=ROOT):
    """Verify complete scientific results against producer-replayed packets."""
    protocol = load_json(raw["protocol"])
    engine.validate_protocol(protocol)
    recorded = load_json(raw["baseline"])
    require(set(recorded["implementation_sha256"]) == set(ENGINE_FILES),
            "Unexpected historical engine dependency set; review before verification")
    implementation = {name: digest((root / "scripts" / name).read_bytes()) for name in ENGINE_FILES}
    require(encoded(implementation) == encoded(recorded["implementation_sha256"]),
            "Historical engine bytes changed; review instead of silently replacing its pins")
    require(digest(raw["protocol"]) == recorded["input_sha256"]["protocol"],
            "Protocol bytes differ from the recorded baseline")
    # Check both complete packets before any cohort analysis or null draws.
    packets = {policy: verify_cached(raw[policy], root=root) for policy in ("split", "join")}
    result = engine.build_report(protocol, packets)
    scientific = {key: value for key, value in recorded.items()
                  if key not in ("input_sha256", "implementation_sha256")}
    require(encoded(result) == encoded(scientific),
            "Recorded baseline science differs from trusted-input replay")
    actual_hashes = {name: digest(data) for name, data in raw.items()}
    return {
        "schema_version": 1,
        "verification_method": "pinned-producer-position-baseline-replay-v1",
        "analysis_id": result["analysis_id"],
        "baseline_results_sha256": actual_hashes["baseline"],
        "input_sha256": {name: actual_hashes[name] for name in ("protocol", "split", "join")},
        "recorded_baseline_input_sha256": recorded["input_sha256"],
        "input_bytes_match_recorded_baseline": {
            name: actual_hashes[name] == recorded["input_sha256"][name]
            for name in ("protocol", "split", "join")},
        "canonical_adapter_snapshot_sha256": {
            policy: digest(encoded(packet)) for policy, packet in packets.items()},
        "historical_engine_sha256": implementation,
        "verification_implementation_sha256": {
            name: digest((root / "scripts" / name).read_bytes()) for name in VERIFIER_FILES},
        "verified_scientific_report_sha256": digest(encoded(result)),
        "cohort_locus_count": result["cohort"]["count"],
        "cohort_sorted_keys_sha256": result["cohort"]["sorted_keys_sha256"],
        "limits": "Verifies pinned transcription/preprocessing consistency and the complete recorded analysis, not glyph accuracy, physical-line alignment, unseen evaluation, decipherment or translation.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=engine.PROTOCOL)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--split", type=Path, required=True)
    parser.add_argument("--join", type=Path, required=True)
    destination = parser.add_mutually_exclusive_group()
    destination.add_argument("--output", type=Path, help="Write a compact verification receipt")
    destination.add_argument("--check", type=Path, help="Verify an existing receipt after full replay")
    args = parser.parse_args(argv)
    try:
        paths = {"protocol": args.protocol, "baseline": args.baseline,
                 "split": args.split, "join": args.join}
        if args.output:
            protect_output(args.output, paths, root=ROOT)
        receipt = verify({name: path.read_bytes() for name, path in paths.items()})
        if args.check:
            require(encoded(receipt) == encoded(load_json(args.check.read_bytes())),
                    "Verification receipt differs from complete replay")
        elif args.output:
            args.output.write_bytes(encoded(receipt))
        print("PASS: full adapter packets and every recorded baseline result verified")
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
