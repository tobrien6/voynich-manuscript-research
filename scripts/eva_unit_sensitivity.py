"""Compare declared segment counts on the parent's unchanged encoded-token cohort.

Segment labels retain their native substrings. They are not image-verified
glyphs, phonetic units, or a complete conversion to another alphabet.
"""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys

try:
    from .locus_position_baseline import contrast, null_variance, uniform_index, quantile
    from .run_locus_position_baseline import read_packet, validate_protocol
except ImportError:
    from locus_position_baseline import contrast, null_variance, uniform_index, quantile
    from run_locus_position_baseline import read_packet, validate_protocol


ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / "research/baselines/eva-unit-protocol.json"
PARENT = ROOT / "research/baselines/locus-position-results.json"
PARENT_PROTOCOL = ROOT / "research/baselines/locus-position-protocol.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ordered_patterns(patterns):
    require(isinstance(patterns, list) and all(isinstance(pattern, str)
            and len(pattern) > 1 and re.fullmatch(r"[A-Za-z]+", pattern) for pattern in patterns),
            "Patterns must be literal multi-letter ASCII sequences")
    require(len(set(patterns)) == len(patterns), "Duplicate grouping pattern")
    return tuple(sorted(patterns, key=lambda pattern: (-len(pattern), pattern)))


def segment(token, patterns):
    """Apply patterns precompiled by ordered_patterns(), preserving source case."""
    require(isinstance(token, str) and re.fullmatch(r"[A-Za-z]+", token),
            "Require a nonempty native ASCII-letter token")
    pieces, position = [], 0
    while position < len(token):
        matched = next((pattern for pattern in patterns if token.startswith(pattern, position)), None)
        piece = matched if matched else token[position]
        pieces.append(piece)
        position += len(piece)
    require("".join(pieces) == token, "Internal error: segmentation changed source text")
    return pieces


def summary(observed, variance, draws):
    return {"observed_equal_locus_mean_contrast": round(observed, 12),
            "exact_conditional_null_expectation": 0.0,
            "exact_conditional_null_standard_deviation": round(math.sqrt(variance), 12),
            "empirical_null_mean": round(sum(draws) / len(draws), 12),
            "empirical_null_interval": {"quantiles": [0.025, 0.975],
                "lower": round(quantile(draws, 0.025), 12),
                "upper": round(quantile(draws, 0.975), 12)},
            "conditional_null_draws": [round(value, 12) for value in draws]}


def measure(tokens_by_key, source_id, spacing, settings, parent_null):
    policies = settings["policies"]
    require([policy["id"] for policy in policies] ==
            ["ascii_letters", "bench_sequences", "bench_and_minim_sequences"], "Unexpected unit policies")
    patterns = [ordered_patterns(policy["patterns"]) for policy in policies]
    require(not patterns[0], "ASCII control must not group letters")
    require(set(patterns[1]) <= set(patterns[2]), "Third policy must retain the bench patterns")
    require(tokens_by_key, "Empty fixed cohort")
    rows, audits = [], []
    keys = sorted(tokens_by_key)
    for pattern_list in patterns:
        audits.append({"pattern_hits": Counter({pattern: 0 for pattern in pattern_list}),
                       "uppercase_single_letter_fallback_counts": Counter(),
                       "unlisted_example_substring_counts": Counter({example: 0 for example
                           in settings["fallback_examples_not_grouped"]}),
                       "encoded_token_count": 0, "emitted_segment_count": 0})
    for key in keys:
        tokens = tokens_by_key[key]
        require(isinstance(tokens, list) and len(tokens) >= 2, "Fixed cohort requires two tokens per locus")
        lengths_per_policy, alternatives = [], []
        for index, pattern_list in enumerate(patterns):
            lengths = []
            for token in tokens:
                pieces = segment(token, pattern_list)
                lengths.append(len(pieces))
                audits[index]["pattern_hits"].update(piece for piece in pieces if len(piece) > 1)
                audits[index]["uppercase_single_letter_fallback_counts"].update(
                    piece for piece in pieces if len(piece) == 1 and piece.isupper())
                audits[index]["unlisted_example_substring_counts"].update({
                    example: token.count(example) for example in settings["fallback_examples_not_grouped"]})
                audits[index]["encoded_token_count"] += 1
                audits[index]["emitted_segment_count"] += len(pieces)
            count, total = len(lengths), sum(lengths)
            lengths_per_policy.append(lengths)
            alternatives.append([(count * length - total) / (count - 1) for length in lengths])
        context = json.dumps([parent_null["seed"], source_id, spacing, key],
                             ensure_ascii=True, separators=(",", ":")).encode("ascii")
        rows.append((lengths_per_policy, alternatives, context))
    size = len(rows)
    observed = [sum(contrast(lengths[index]) for lengths, _, _ in rows) / size
                for index in range(len(policies))]
    variances = [sum(null_variance(lengths[index]) for lengths, _, _ in rows) / size ** 2
                 for index in range(len(policies))]
    delta_variances = [sum(sum((choices[index][j] - choices[0][j]) ** 2
                         for j in range(len(choices[0]))) / len(choices[0])
                         for _, choices, _ in rows) / size ** 2 for index in [1, 2]]
    draws = [[] for _ in policies]
    for replicate in range(parent_null["replicates"]):
        totals = [0.0] * len(policies)
        for lengths, alternatives, context in rows:
            choice = uniform_index(len(lengths[0]), context, replicate)
            for index in range(len(policies)):
                totals[index] += alternatives[index][choice]
        for index in range(len(policies)):
            draws[index].append(totals[index] / size)
    results = []
    for index, policy in enumerate(policies):
        audit = {key: dict(sorted(value.items())) if isinstance(value, Counter) else value
                 for key, value in audits[index].items()}
        result = {"policy_id": policy["id"], "unit": policy["unit"],
                  "matching_precedence": list(patterns[index]), "scope_audit": audit,
                  **summary(observed[index], variances[index], draws[index])}
        if index:
            differences = [grouped - ascii_value for grouped, ascii_value in zip(draws[index], draws[0])]
            result["paired_change_from_ascii"] = summary(observed[index] - observed[0],
                                                         delta_variances[index - 1], differences)
        results.append(result)
    return {"source_id": source_id, "spacing_policy": spacing,
            "cohort_locus_count": size, "unit_policies": results}


def build(settings, parent, parent_protocol, packets):
    require(settings.get("schema_version") == 1 and
            settings.get("analysis_id") == "fixed-cohort-eva-unit-sensitivity-v1", "Unknown sensitivity protocol")
    require(settings.get("analysis_status") == "post-result exploratory sensitivity",
            "The sensitivity analysis cannot be relabeled confirmatory")
    validate_protocol(parent_protocol)
    require(parent.get("analysis_id") == parent_protocol["analysis_id"], "Wrong parent analysis")
    require(parent["null"]["seed"] == parent_protocol["seed"] and
            parent["null"]["replicates"] == parent_protocol["null_replicates"] and
            parent["null"]["algorithm"] == "shared-HashDraws-uniform-first-v1", "Parent null differs")
    require(parent["cohort"]["sorted_keys_sha256"] == settings["cohort_sha256"], "Parent cohort differs")
    keys = parent["cohort"]["locus_keys"]
    require(len(keys) == len(set(keys)) == parent["cohort"]["count"], "Invalid parent cohort keys")
    require(hashlib.sha256(("\n".join(sorted(keys)) + "\n").encode()).hexdigest()
            == settings["cohort_sha256"], "Parent cohort key checksum differs")
    parsed = {policy: read_packet(packets[policy], policy, parent_protocol) for policy in ["split", "join"]}
    results = []
    contexts = [(variant["source_id"], variant["spacing_policy"]) for variant in parent["variants"]]
    require(len(contexts) == 4 and set(contexts) == {(source, policy)
            for source in parent_protocol["sources"] for policy in ["split", "join"]},
            "Require exactly four unique parent source/policy contexts")
    for parent_variant in parent["variants"]:
        ident, spacing = parent_variant["source_id"], parent_variant["spacing_policy"]
        records = parsed[spacing][0][ident]
        require(all(key in records and records[key]["eligible"] for key in keys), "Missing/excluded fixed-cohort record")
        result = measure({key: records[key]["tokens"] for key in keys}, ident, spacing, settings, parent["null"])
        ascii_result = result["unit_policies"][0]
        for field in ["observed_equal_locus_mean_contrast", "exact_conditional_null_expectation",
                      "exact_conditional_null_standard_deviation", "empirical_null_mean",
                      "empirical_null_interval", "conditional_null_draws"]:
            require(ascii_result[field] == parent_variant[field], f"ASCII control does not reproduce parent: {field}")
        require(ascii_result["scope_audit"]["encoded_token_count"] == parent_variant["encoded_token_count"],
                "Original token count changed")
        result["alphabet"] = parent_variant["alphabet"]
        result["source_sha256"] = parent_variant["source_sha256"]
        results.append(result)
    return {"schema_version": 1, "analysis_id": settings["analysis_id"],
            "analysis_status": settings["analysis_status"], "cohort_sha256": settings["cohort_sha256"],
            "cohort_locus_count": len(keys), "source_reference": settings["source"],
            "processing": {"segmentation": settings["segmentation"], "measurement": settings["measurement"],
                           "pairing": settings["conditional_null"], "policies": settings["policies"]},
            "null": parent["null"], "variants": results, "inference_limit": settings["limit"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", type=Path, default=SETTINGS)
    parser.add_argument("--parent", type=Path, default=PARENT)
    parser.add_argument("--parent-protocol", type=Path, default=PARENT_PROTOCOL)
    parser.add_argument("--split", type=Path, required=True)
    parser.add_argument("--join", type=Path, required=True)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    try:
        paths = {"settings": args.settings, "parent": args.parent, "parent_protocol": args.parent_protocol,
                 "split": args.split, "join": args.join}
        raw = {name: path.read_bytes() for name, path in paths.items()}
        settings, parent = json.loads(raw["settings"]), json.loads(raw["parent"])
        require(hashlib.sha256(raw["parent"]).hexdigest() == settings["baseline_results_sha256"],
                "Parent result checksum differs from prospective settings")
        for name in ["split", "join"]:
            require(hashlib.sha256(raw[name]).hexdigest() == parent["input_sha256"][name],
                    "Token packet differs from fixed parent input")
        require(hashlib.sha256(raw["parent_protocol"]).hexdigest() == parent["input_sha256"]["protocol"],
                "Parent protocol differs")
        for name, digest in parent["implementation_sha256"].items():
            require(Path(name).name == name and hashlib.sha256((ROOT / "scripts" / name).read_bytes()).hexdigest() == digest,
                    "Parent implementation differs; review instead of silently updating")
        report = build(settings, parent, json.loads(raw["parent_protocol"]),
                       {name: json.loads(raw[name]) for name in ["split", "join"]})
        report["input_sha256"] = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
        report["implementation_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        if args.check:
            require(report == json.loads(args.check.read_bytes()), "Sensitivity report does not reproduce")
            print("PASS: ASCII parent, grouped policies, paired draws and provenance reproduce")
        else:
            require(args.output.resolve() not in {path.resolve() for path in paths.values()},
                    "Output must not replace an input")
            args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print("Wrote three unit policies for every fixed source/spacing variant")
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
