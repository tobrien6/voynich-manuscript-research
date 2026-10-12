"""Analyze the fixed common cohort from two conservative token-adapter JSON files."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

try:
    from .locus_position_baseline import analyze_tokens
except ImportError:
    from locus_position_baseline import analyze_tokens


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "research/baselines/locus-position-protocol.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_protocol(protocol):
    require(protocol.get("schema_version") == 1 and
            protocol.get("analysis_id") == "locus-position-ascii-length-v1", "Unknown protocol")
    require(protocol.get("analysis_status") == "exploratory", "V1 is an exploratory analysis")
    require(set(protocol.get("sources", {})) == {"ZL3b", "IT2a"}, "Require the fixed paired sources")
    require(all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
                for value in protocol["sources"].values()), "Invalid source checksum")
    for field, value in [("locus_kinds", ["P0", "P1"]), ("locators", ["@", "+", "*"]),
                         ("spacing_policies", ["split", "join"]),
                         ("minimum_tokens_in_every_source_and_policy", 2),
                         ("empirical_interval_quantiles", [0.025, 0.975]),
                         ("null_replicates", 2000),
                         ("seed", "voynich-locus-position-v1-2026-10-11"),
                         ("unit", "case-preserving ASCII letter count of each encoded token, not manuscript glyph count"),
                         ("metric", "equal-locus mean of first-token length minus mean remaining-token length")]:
        require(protocol.get(field) == value, f"Unsupported v1 setting: {field}")
    require(type(protocol.get("null_replicates")) is int, "Replicate count must be an integer")
    require(isinstance(protocol.get("seed"), str) and protocol["seed"], "Missing null seed")


def read_packet(packet, policy, protocol):
    require(packet.get("schema_version") == 1 and packet.get("adapter_version") == "plain-eva-v1",
            "Require the conservative plain-eva-v1 adapter contract")
    processing = packet.get("processing", {})
    require(processing.get("uncertain_space_policy") == policy, "Adapter spacing policy mismatch")
    require(processing.get("selected_locus_types") == protocol["locus_kinds"],
            "Adapter locus selection differs from protocol")
    sources = packet.get("sources", [])
    require(isinstance(sources, list) and len(sources) == len(protocol["sources"]),
            "Wrong source count in adapter packet")
    declared = {}
    for source in sources:
        ident = source.get("id")
        require(ident in protocol["sources"] and ident not in declared, "Unknown/duplicate adapter source")
        require(source.get("sha256") == protocol["sources"][ident], "Adapter source checksum mismatch")
        require(source.get("alphabet") == {"ZL3b": "Eva-", "IT2a": "EvaT"}[ident],
                "Adapter alphabet differs from pinned source")
        declared[ident] = source
    records = packet.get("records")
    require(isinstance(records, list) and records, "Missing adapter records")
    indexed = {ident: {} for ident in declared}
    for record in records:
        ident, key = record.get("source_id"), record.get("locus_key")
        require(ident in indexed and isinstance(key, str) and key, "Invalid adapter record identity")
        require(key not in indexed[ident], "Duplicate source/locus key")
        require(record.get("transcriber") is None, "Require single-source, non-interlinear records")
        require(isinstance(record.get("locus_type"), str) and isinstance(record.get("locator"), str),
                "Missing locus type/locator")
        require(type(record.get("eligible")) is bool, "Missing Boolean eligibility")
        reasons = record.get("exclusion_reasons")
        require(isinstance(reasons, list) and all(isinstance(reason, str) and reason for reason in reasons),
                "Invalid adapter exclusion reasons")
        if record["eligible"]:
            tokens = record.get("tokens")
            require(isinstance(tokens, list) and tokens and all(isinstance(token, str)
                    and re.fullmatch(r"[A-Za-z]+", token) for token in tokens), "Non-ASCII/empty token sequence")
            require(not reasons and type(record.get("token_count")) is int
                    and record["token_count"] == len(tokens), "Inconsistent eligible record")
            require(record["locus_type"] in protocol["locus_kinds"], "Eligible record outside adapter selection")
        else:
            require(reasons and record.get("tokens") is None and record.get("token_count") is None,
                    "Inconsistent excluded record")
        indexed[ident][key] = record
    require(all(indexed.values()), "Source has no records")
    return indexed, declared


def build_report(protocol, packets):
    validate_protocol(protocol)
    require(set(packets) == set(protocol["spacing_policies"]), "Require both spacing-policy packets")
    parsed = {policy: read_packet(packet, policy, protocol) for policy, packet in packets.items()}
    ids = sorted(protocol["sources"])
    for ident in ids:
        split, joined = parsed["split"][0][ident], parsed["join"][0][ident]
        require(split.keys() == joined.keys(), f"Different source/locus sets across policies: {ident}")
        require(parsed["split"][1][ident] == parsed["join"][1][ident], "Source provenance changed across policies")
        for key in split:
            for field in ("locus_type", "locator", "page_id", "locus_identifier", "source_line_number"):
                require(split[key].get(field) == joined[key].get(field), "Locus metadata changed across policies")
    eligible, exclusions = {}, {}
    for policy in protocol["spacing_policies"]:
        for ident in ids:
            group = (ident, policy)
            eligible[group], exclusions[group] = {}, {}
            for key, record in parsed[policy][0][ident].items():
                reasons = list(record["exclusion_reasons"])
                if record["locus_type"] not in protocol["locus_kinds"]:
                    reasons.append("baseline_unselected_kind")
                if record["locator"] not in protocol["locators"]:
                    reasons.append("baseline_unselected_locator")
                if record["eligible"] and len(record["tokens"]) < 2:
                    reasons.append("baseline_fewer_than_two_tokens")
                if reasons:
                    exclusions[group][key] = sorted(set(reasons))
                else:
                    eligible[group][key] = record["tokens"]
    common = set.intersection(*(set(values) for values in eligible.values()))
    require(common, "No common eligible cohort under all source/policy combinations")
    keys = sorted(common)
    variants = []
    for ident in ids:
        for policy in protocol["spacing_policies"]:
            group = (ident, policy)
            dropped = dict(exclusions[group])
            for key in set(eligible[group]) - common:
                dropped[key] = ["baseline_not_in_all_source_policy_cohorts"]
            reason_counts = Counter(reason for reasons in dropped.values() for reason in reasons)
            grouped_exclusions = defaultdict(list)
            for key in sorted(dropped):
                grouped_exclusions[tuple(dropped[key])].append(key)
            result = analyze_tokens({key: eligible[group][key] for key in keys}, ident, policy,
                                    replicates=protocol["null_replicates"], seed=protocol["seed"])
            result["alphabet"] = parsed[policy][1][ident]["alphabet"]
            result["source_sha256"] = protocol["sources"][ident]
            result["selection_audit"] = {
                "source_locus_record_count": len(parsed[policy][0][ident]),
                "eligible_before_common_cohort": len(eligible[group]),
                "excluded_record_count": len(dropped),
                "reason_counts_may_overlap": dict(sorted(reason_counts.items())),
                "excluded_locus_groups": [{"reasons": list(reasons), "locus_keys": group_keys}
                    for reasons, group_keys in sorted(grouped_exclusions.items())]}
            require(result["cohort_locus_count"] + len(dropped) == len(parsed[policy][0][ident]),
                    "Selection audit does not account for every source record")
            variants.append(result)
    return {
        "schema_version": 1, "analysis_id": protocol["analysis_id"], "analysis_status": "exploratory",
        "unit": protocol["unit"], "metric": protocol["metric"],
        "source_provenance_declared_by_adapter": [parsed["split"][1][ident] for ident in ids],
        "cohort": {"rule": protocol["cohort"], "count": len(keys), "locus_keys": keys,
                   "sorted_keys_sha256": hashlib.sha256(("\n".join(keys) + "\n").encode()).hexdigest()},
        "null": {"algorithm": "shared-HashDraws-uniform-first-v1",
                 "definition": protocol["null"], "replicates": protocol["null_replicates"], "seed": protocol["seed"],
                 "randomness": "JSON-encoded seed/source/policy/locus context plus 16-byte big-endian replicate counter; shared HashDraws rejection sampling"},
        "variants": variants, "inference_limit": protocol["inference_limit"],
        "exposure": "Whole-corpus exploratory analysis after source metadata and selected image exposure; no untouched evaluation set",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=PROTOCOL)
    parser.add_argument("--split", type=Path, required=True)
    parser.add_argument("--join", type=Path, required=True)
    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument("--output", type=Path)
    output.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    try:
        paths = {"protocol": args.protocol, "split": args.split, "join": args.join}
        raw = {name: path.read_bytes() for name, path in paths.items()}
        protocol = json.loads(raw["protocol"])
        report = build_report(protocol, {policy: json.loads(raw[policy]) for policy in ("split", "join")})
        report["input_sha256"] = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
        report["implementation_sha256"] = {
            name: hashlib.sha256((ROOT / "scripts" / name).read_bytes()).hexdigest()
            for name in ("run_locus_position_baseline.py", "locus_position_baseline.py", "shuffle_token_lines.py")}
        if args.check:
            require(report == json.loads(args.check.read_bytes()), "Recorded baseline differs from recomputed result")
            print("PASS: complete cohort, exclusions, provenance, and null statistics reproduce")
        else:
            require(args.output.resolve() not in {path.resolve() for path in paths.values()},
                    "Output must not replace an analysis input")
            args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"Wrote four variants for {report['cohort']['count']} common loci")
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
