"""Descriptive paired-source entropy sensitivity with declared segment boundaries."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

try:
    from .audit_transliterations import load_sources
    from .eva_token_adapter import adapt
    from .eva_unit_sensitivity import ordered_patterns, segment
except ImportError:
    from audit_transliterations import load_sources
    from eva_token_adapter import adapt
    from eva_unit_sensitivity import ordered_patterns, segment


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = Path("research/representation/paired-entropy-plan.json")
PLAN_NOTE = Path("research/representation/PAIRED_ENTROPY_PLAN.md")
SOURCE_IDS = ("ZL3b", "IT2a")
SPACING = ("split", "join")
BOUNDARIES = ("within_token", "within_locus_with_space")
UNIT_IDS = ("ascii_letters", "bench_sequences", "bench_and_minim_sequences")
PIN_PATHS = {
    "data/transliterations.json", "research/baselines/eva-unit-protocol.json",
    "scripts/audit_transliterations.py", "scripts/ivtff.py", "scripts/eva_token_adapter.py",
    "scripts/token_baselines.py", "scripts/eva_unit_sensitivity.py",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def digest(value):
    return hashlib.sha256(compact(value)).hexdigest()


def load_plan(root=ROOT):
    raw = (root / PLAN_PATH).read_bytes()
    plan = json.loads(raw)
    expected = {
        "schema_version": 1, "analysis_id": "paired-symbol-entropy-sensitivity-v1",
        "source_ids": list(SOURCE_IDS), "spacing_policies": list(SPACING),
        "selected_locus_kinds": ["P0"], "regular_locators": ["@", "+", "*"],
        "minimum_tokens": 1, "exclude_drawing_interruptions": True,
        "common_cohort_across_all_four_variants": True,
        "unit_policy_file": "research/baselines/eva-unit-protocol.json",
        "unit_policy_ids": list(UNIT_IDS), "boundary_policies": list(BOUNDARIES),
        "word_boundary_unit": "<SPACE>", "null_or_language_comparison": None,
        "may_apply_as_source_correction": False,
    }
    for key, value in expected.items():
        require(plan.get(key) == value and type(plan.get(key)) is type(value),
                f"review changed plan field before versioning: {key}")
    require(set(plan["input_pins"]) == PIN_PATHS, "plan input-pin scope changed")
    for path, expected_digest in plan["input_pins"].items():
        require(hashlib.sha256((root / path).read_bytes()).hexdigest() == expected_digest,
                f"pinned input changed: {path}")
    settings = json.loads((root / plan["unit_policy_file"]).read_bytes())
    policies = settings["policies"]
    require([p["id"] for p in policies] == list(UNIT_IDS), "unit policies changed")
    for policy in policies:
        ordered_patterns(policy["patterns"])
    return plan, policies, hashlib.sha256(raw).hexdigest()


def record_index(records):
    indexed = {}
    for record in records:
        key = record["locus_key"]
        require(key not in indexed, f"duplicate source locus key: {key}")
        indexed[key] = record
    return indexed


def prepare(sources, plan):
    selected = [(s, d) for s, d in sources if s["id"] in SOURCE_IDS]
    require(Counter(s["id"] for s, _ in selected) == Counter(SOURCE_IDS),
            "require exactly one ZL3b and IT2a source")
    available = {s["id"]: (s, d) for s, d in selected}
    native = {sid: {l.key for l in available[sid][1].loci if l.present and l.kind == "P0"}
              for sid in SOURCE_IDS}
    common = set.intersection(*native.values())
    require(common, "no shared present P0 loci")
    maps = {(sid, spacing): record_index(adapt(*available[sid], spacing, ("P0",)))
            for sid in SOURCE_IDS for spacing in SPACING}
    accepted, excluded, reason_counts = [], [], Counter()
    for key in sorted(common):
        reasons = []
        for (sid, spacing), mapping in maps.items():
            require(key in mapping, f"missing shared locus: {sid}/{spacing}:{key}")
            record = mapping[key]
            require(record["locus_key"] == key and record["page_id"] == key.rsplit(".", 1)[0],
                    f"source identity mismatch: {key}")
            prefix = f"{sid}/{spacing}:"
            if not record["eligible"]:
                reasons.extend(prefix + reason for reason in record["exclusion_reasons"])
            elif record["token_count"] < plan["minimum_tokens"]:
                reasons.append(prefix + "too_few_tokens")
            if record["locator"] not in plan["regular_locators"]:
                reasons.append(prefix + "nonregular_locator")
            if record["drawing_interruption_count"]:
                reasons.append(prefix + "drawing_interruption")
        if reasons:
            reasons = sorted(set(reasons))
            excluded.append({"locus_key": key, "reasons": reasons})
            reason_counts.update(reasons)
        else:
            accepted.append(key)
    require(accepted, "no common eligible clear regular P0 loci")
    return maps, accepted, {
        "shared_present_P0_loci": len(common), "shared_keys_sha256": digest(sorted(common)),
        "source_only_present_P0_keys": {sid: sorted(native[sid] - common) for sid in SOURCE_IDS},
        "retained_loci": len(accepted), "retained_locus_keys": accepted,
        "retained_locus_keys_sha256": digest(accepted),
        "excluded_loci": len(excluded), "exclusions": excluded,
        "reason_counts_may_overlap": dict(sorted(reason_counts.items())),
        "digest_serialization": "UTF-8 compact JSON, ensure_ascii=False, separators comma/colon",
    }


def segments_for(rows, patterns, boundary):
    require(boundary in BOUNDARIES, "unsupported boundary policy")
    segments = []
    for tokens in rows:
        require(isinstance(tokens, list) and tokens, "each locus requires a nonempty token list")
        pieces = [segment(token, patterns) for token in tokens]
        if boundary == "within_token":
            segments.extend(pieces)
        else:
            joined = []
            for index, token_pieces in enumerate(pieces):
                if index:
                    joined.append("<SPACE>")
                joined.extend(token_pieces)
            segments.append(joined)
    return segments


def entropy(counts):
    total = sum(counts.values())
    return -math.fsum(n / total * math.log2(n / total) for n in counts.values())


def rounded(value):
    return None if value is None else 0.0 if value == 0 else round(value, 12)


def pooled_statistics(segments):
    require(isinstance(segments, list) and segments, "require a nonempty segment population")
    full, pairs, predecessors, terminals = Counter(), Counter(), Counter(), Counter()
    for units in segments:
        require(isinstance(units, list) and units and
                all(isinstance(unit, str) and unit for unit in units), "require nonempty atomic-label segments")
        full.update(units)
        pairs.update(zip(units[:-1], units[1:]))
        terminals[units[-1]] += 1
    for (left, _), count in pairs.items():
        predecessors[left] += count
    unit_count, edge_count = sum(full.values()), sum(pairs.values())
    require(edge_count == unit_count - len(segments), "segment edge accounting changed")
    require(all(predecessors[u] + terminals[u] == n for u, n in full.items()),
            "predecessor/terminal counts differ from full population")
    h_full = entropy(full)
    h_pair = entropy(pairs) if edge_count else None
    h_predecessor = entropy(predecessors) if edge_count else None
    conditional = (-math.fsum(n / edge_count * math.log2(n / predecessors[left])
                             for (left, _), n in pairs.items())) if edge_count else None
    if edge_count:
        require(math.isclose(conditional, h_pair - h_predecessor, rel_tol=0, abs_tol=1e-12),
                "matching-population chain rule failed")
    return {
        "segment_count": len(segments), "segments_without_edges": sum(len(u) == 1 for u in segments),
        "unit_count": unit_count, "edge_count": edge_count,
        "terminal_unit_count": sum(terminals.values()), "observed_unit_types": len(full),
        "full_unit_counts": [{"unit": u, "count": n} for u, n in sorted(full.items())],
        "predecessor_counts_from_edges": [{"unit": u, "count": n} for u, n in sorted(predecessors.items())],
        "terminal_unit_counts": [{"unit": u, "count": n} for u, n in sorted(terminals.items())],
        "directed_pair_counts": [{"predecessor": a, "successor": b, "count": n}
                                 for (a, b), n in sorted(pairs.items())],
        "bits": {
            "full_unit_entropy": rounded(h_full), "pair_entropy": rounded(h_pair),
            "edge_predecessor_entropy": rounded(h_predecessor),
            "conditional_successor_entropy": rounded(conditional),
            "pair_minus_full_unit_entropy": rounded(h_pair - h_full) if edge_count else None,
            "difference_due_to_full_marginal": rounded(h_predecessor - h_full) if edge_count else None,
        },
    }


def make_report(root=ROOT):
    plan, policies, plan_hash = load_plan(root)
    sources = load_sources(root)
    maps, accepted, selection = prepare(sources, plan)
    provenance = {source["id"]: source for source, _ in sources}
    results = []
    for (sid, spacing), mapping in maps.items():
        selected = [mapping[key] for key in accepted]
        rows = [record["tokens"] for record in selected]
        row_identity = [{key: record[key] for key in
                         ("locus_key", "locus_identifier", "source_line_number", "variables", "tokens")}
                        for record in selected]
        for policy in policies:
            patterns = ordered_patterns(policy["patterns"])
            for boundary in BOUNDARIES:
                statistics = pooled_statistics(segments_for(rows, patterns, boundary))
                results.append({
                    "source_id": sid, "source_sha256": provenance[sid]["sha256"],
                    "spacing": spacing, "unit_policy": policy["id"], "boundary_policy": boundary,
                    "loci": len(accepted), "native_token_count": sum(len(row) for row in rows),
                    "source_page_ids": len({record["page_id"] for record in selected}),
                    "selected_records_sha256": digest(row_identity),
                    "source_currier_metadata": dict(sorted(Counter(
                        record["variables"].get("L", "unset") for record in selected).items())),
                    **statistics,
                })
    paths = [PLAN_PATH, PLAN_NOTE, Path("scripts/paired_symbol_entropy.py")]
    return {
        "schema_version": 1, "analysis_id": plan["analysis_id"], "analysis_status": plan["analysis_status"],
        "plan_sha256": plan_hash, "pinned_inputs": plan["input_pins"],
        "record_fingerprints": {str(path): hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths},
        "sources": [{key: provenance[sid][key] for key in ("id", "sha256", "path", "url", "alphabet")}
                    for sid in SOURCE_IDS],
        "unit_policies": policies, "boundary_unit": plan["word_boundary_unit"],
        "sampling_unit": "source locus, not a verified physical row or independent image observation",
        "weighting": plan["weighting"], "estimator": plan["estimator"],
        "null_or_language_comparison": None, "may_apply_as_source_correction": False,
        "selection": selection, "treatments": results,
    }


def protect_output(output, inputs):
    for path in inputs:
        if output.resolve() == path.resolve() or output.exists() and path.exists() and output.samefile(path):
            raise ValueError("output must not overwrite an input or implementation, including file aliases")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        plan, _, _ = load_plan(ROOT)
        protected = [ROOT / path for path in plan["input_pins"]] + [ROOT / PLAN_PATH, ROOT / PLAN_NOTE, Path(__file__)]
        catalog = json.loads((ROOT / "data/transliterations.json").read_bytes())
        protected.extend(ROOT / source["path"] for source in catalog["sources"])
        if args.output:
            protect_output(args.output, protected)
        report = make_report(ROOT)
        if args.check and report != json.loads(args.check.read_text(encoding="utf-8")):
            raise ValueError("paired entropy report differs from replay")
        text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            protect_output(args.output, protected)
            args.output.write_text(text, encoding="utf-8")
        elif not args.check:
            print(text, end="")
        if args.check:
            print("PASS: pinned sources, common cohort, all frequency tables and paired entropy treatments reproduce")
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"paired symbol entropy failed: {error}\n")


if __name__ == "__main__":
    main()
