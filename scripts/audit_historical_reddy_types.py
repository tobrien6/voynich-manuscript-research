"""Audit positional H/Reddy type equality without fitting a notation map."""

import argparse
from collections import Counter, defaultdict
import json
import unicodedata
from pathlib import Path

try:
    from . import audit_historical_reddy_envelopes as parent
except ImportError:
    import audit_historical_reddy_envelopes as parent

ROOT = Path(__file__).resolve().parents[1]
PLAN = "research/historical/reddy-type-correspondence-plan.json"
HUMAN_PLAN = "research/historical/REDDY_TYPE_CORRESPONDENCE_PLAN.md"
FROZEN = (*parent.FROZEN, parent.HUMAN_PLAN, parent.PLAN,
          "research/historical/reddy-envelopes.json", "scripts/audit_historical_reddy_envelopes.py")


def load_plan(root):
    plan = parent.read_json(root / PLAN)
    expected = {"plan_version": 1, "parent_pr": 175,
                "parent_published_head": "c6df1ef7401a61a51a8896bb2c93ccc155076bb1",
                "pair_rule": "Exact literal shared four-field key and same within-record normalized/annotated token index; require equal counts and shared source order; retain unmatched empty H record",
                "h_special_codes": [], "manual_exclusions": False, "compare_token_spellings": False,
                "type_id_encoding": "SHA256 of original notation token UTF-8 bytes; separate H/Reddy domains",
                "output_raw_tokens": False, "include_asterisk_tokens": True, "sample": False, "null": False,
                "type_graph": "Complete bipartite type graph, every edge count and every (selected H ordinal, local token index) support position; degrees in both directions",
                "repeat_scope": "Every consecutive edge on the complete flattened paired token sequence, including native-record joins; retain all discordant equality events"}
    expected["partition_pair_counts"] = "All unordered distinct paired positions: both-equal=sum choose(n_ab,2); source-equal=sum choose(n_a,2); retain both one-sided equality counts and neither with choose(N,2) denominator"
    if any(parent.canonical(plan.get(key)) != parent.canonical(value) for key, value in expected.items()):
        raise ValueError("positional type-correspondence plan options differ")
    if set(plan["dependency_hashes"]) != set(FROZEN):
        raise ValueError("positional type-correspondence dependency set differs")
    for name in FROZEN:
        if parent.digest((root / name).read_bytes()) != plan["dependency_hashes"][name]:
            raise ValueError(f"frozen positional type dependency differs: {name}")
    return plan


def pair_records(native, annotated):
    envelope = parent.compare_records(*parent.describe_sources(native, annotated, set()))
    if not envelope["shared_order"]["exact_shared_order_equal"]:
        raise ValueError("shared source record order differs")
    if envelope["summary"]["h_fallback"]["shared_count_comparison"]["unequal_records"]:
        raise ValueError("shared record counts differ; positional pairing undefined")
    if any(envelope["summary"][name]["unmatched_tokens"] for name in ("h_fallback", "reddy")):
        raise ValueError("unmatched nonempty source record; positional pairing undefined")
    r_by_key = {tuple(row["header"]): (i, row) for i, row in enumerate(annotated)}
    paired = []
    for ordinal, record in enumerate(native):
        key = (record.page, record.unit, record.line, record.transcriber)
        match = r_by_key.get(key)
        if match is None:
            continue
        r_ordinal, row = match
        paired.append({"key": list(key), "h_ordinal": ordinal, "reddy_ordinal": r_ordinal,
                       "h_tokens": parent.normalize_body(record.body, set())[0], "reddy_tokens": row["tokens"]})
    unmatched = [row for row in envelope["all_union_records"] if row["presence"] != "shared"]
    return paired, {"source_records": {name: envelope["summary"][name]["records"] for name in ("h_fallback", "reddy")},
                    "shared_records": envelope["summary"]["shared_records"], "all_unmatched_records": unmatched,
                    "shared_order": envelope["shared_order"]}


def compare_types(records):
    ids, inverse = {side: {} for side in ("h", "reddy")}, {side: {} for side in ("h", "reddy")}
    frequency = {side: Counter() for side in ids}
    partners = {side: defaultdict(set) for side in ids}
    edge_positions, flat = defaultdict(list), []
    prior_h = prior_r = -1
    seen_keys = set()

    def type_id(side, token):
        if type(token) is not str or not token or any(c.isspace() for c in token):
            raise ValueError("invalid original notation token")
        if token not in ids[side]:
            identifier = parent.digest(token.encode("utf-8"))
            if identifier in inverse[side] and inverse[side][identifier] != token:
                raise ValueError("within-domain type hash collision")
            ids[side][token], inverse[side][identifier] = identifier, token
        return ids[side][token]

    for row in records:
        h_ordinal, r_ordinal = row["h_ordinal"], row["reddy_ordinal"]
        if (type(h_ordinal) is not int or type(r_ordinal) is not int
                or h_ordinal <= prior_h or r_ordinal <= prior_r):
            raise ValueError("paired source ordinals differ")
        key = parent.check_key(row["key"])
        if key in seen_keys:
            raise ValueError("duplicate paired source key")
        seen_keys.add(key)
        if len(row["h_tokens"]) != len(row["reddy_tokens"]):
            raise ValueError("paired token counts differ")
        prior_h, prior_r = h_ordinal, r_ordinal
        for index, (a, b) in enumerate(zip(row["h_tokens"], row["reddy_tokens"], strict=True)):
            left, right = type_id("h", a), type_id("reddy", b)
            frequency["h"][left] += 1
            frequency["reddy"][right] += 1
            partners["h"][left].add(right)
            partners["reddy"][right].add(left)
            edge_positions[(left, right)].append([h_ordinal, index])
            flat.append({"key": row["key"], "h_ordinal": h_ordinal, "reddy_ordinal": r_ordinal,
                         "local_token_index": index, "h_type": left, "reddy_type": right})

    matrix = {kind: {"both_equal": 0, "h_only_equal": 0, "reddy_only_equal": 0, "neither_equal": 0}
              for kind in ("all", "within_record", "joining")}
    repeated = {side: set() for side in ids}
    repeated_by_class = {side: {kind: set() for kind in ("within_record", "joining")} for side in ids}
    discordant, joins = [], []
    for edge_index, (a, b) in enumerate(zip(flat, flat[1:])):
        h_equal, r_equal = a["h_type"] == b["h_type"], a["reddy_type"] == b["reddy_type"]
        kind = "within_record" if a["h_ordinal"] == b["h_ordinal"] else "joining"
        case = "both_equal" if h_equal and r_equal else "h_only_equal" if h_equal else "reddy_only_equal" if r_equal else "neither_equal"
        matrix["all"][case] += 1
        matrix[kind][case] += 1
        if h_equal:
            repeated["h"].add(a["h_type"])
            repeated_by_class["h"][kind].add(a["h_type"])
        if r_equal:
            repeated["reddy"].add(a["reddy_type"])
            repeated_by_class["reddy"][kind].add(a["reddy_type"])
        if kind == "joining" or h_equal != r_equal:
            event = {"flat_left_index": edge_index, "edge_class": kind, "h_equal": h_equal, "reddy_equal": r_equal,
                     "left": a, "right": b}
            if kind == "joining":
                event["intervening_selected_H_ordinals"] = list(range(a["h_ordinal"] + 1, b["h_ordinal"]))
                joins.append(event)
            if h_equal != r_equal: discordant.append(event)

    nodes, populations = {}, {}
    for side in ids:
        nodes[side] = [{"type_sha256": key, "occurrences": count, "degree": len(partners[side][key]),
                        "notation_codepoints": len(inverse[side][key]), "contains_asterisk": "*" in inverse[side][key],
                        "repeats_in_flattened_stream": key in repeated[side]} for key, count in sorted(frequency[side].items())]
        degree_hist = Counter(len(targets) for targets in partners[side].values())
        populations[side] = {"tokens": sum(frequency[side].values()), "types": len(frequency[side]),
                             "degree_histogram": [{"degree": degree, "types": count} for degree, count in sorted(degree_hist.items())],
                             "functional_to_other_domain": all(len(targets) == 1 for targets in partners[side].values()),
                             "nonfunctional_types": sum(len(targets) > 1 for targets in partners[side].values()),
                             "occurrences_of_nonfunctional_types": sum(count for key, count in frequency[side].items() if len(partners[side][key]) > 1),
                             "asterisk_types": sum("*" in token for token in ids[side]),
                             "asterisk_occurrences": sum(frequency[side][key] for token, key in ids[side].items() if "*" in token),
                             "A_equal_edges": matrix["all"]["both_equal"] + matrix["all"][f"{side}_only_equal"],
                             "B_repeated_types": len(repeated[side]),
                             "B_by_edge_class": {kind: len(types) for kind, types in repeated_by_class[side].items()},
                             "B_overlap_within_and_joining": len(repeated_by_class[side]["within_record"] & repeated_by_class[side]["joining"])}
    edges = [{"h_type_sha256": a, "reddy_type_sha256": b, "occurrences": len(positions),
              "support_positions": positions} for (a, b), positions in sorted(edge_positions.items())]
    choose2 = lambda n: n * (n - 1) // 2
    both = sum(choose2(len(positions)) for positions in edge_positions.values())
    h_equal_pairs = sum(choose2(n) for n in frequency["h"].values())
    r_equal_pairs = sum(choose2(n) for n in frequency["reddy"].values())
    all_pairs = choose2(len(flat))
    pair_matrix = {"all_unordered_position_pairs": all_pairs, "both_equal": both,
                   "h_only_equal": h_equal_pairs - both, "reddy_only_equal": r_equal_pairs - both,
                   "neither_equal": all_pairs - h_equal_pairs - r_equal_pairs + both}
    return {"paired_tokens": len(flat), "paired_nonempty_records": sum(bool(row["h_tokens"]) for row in records),
            "position_digest": parent.digest(parent.canonical(flat)),
            "position_digest_content": "source-ordered array of key/H ordinal/Reddy ordinal/local index/H type ID/Reddy type ID objects",
            "support_position_fields": ["selected_H_ordinal", "local_token_index"],
            "equality_partition_identical": all(pop["functional_to_other_domain"] for pop in populations.values()),
            "unordered_position_pair_matrix": pair_matrix,
            "populations": populations, "type_pair_edges": len(edges), "nodes": nodes, "edges": edges,
            "repeat_edge_population": max(0, len(flat) - 1), "repeat_event_matrix": matrix,
            "all_discordant_repeat_events": discordant, "all_joining_edges": joins}


def run_audit(reference, root=ROOT):
    plan = load_plan(root)
    parent.check_parent(parent.run_audit(reference, root), root / "research/historical/reddy-envelopes.json")
    catalog = parent.read_json(root / "data/historical/interlinear-16e6.json")
    member = parent.read_pinned_archive((root / catalog["path"]).read_bytes(), catalog)
    native = [row for row in parent.parse_historical(member)[0] if row.transcriber == "H"]
    manifest = parent.read_json(root / parent.reddy.MANIFEST)
    raw = parent.reddy.read_selected(reference, manifest)
    annotated = parent.reddy.annotated(raw["data/voy.ann.wds"])[0]
    paired, pairing = pair_records(native, annotated)
    return {"audit_version": 1, "scope": plan["scope"],
            "plan_sha256": parent.digest((root / PLAN).read_bytes()),
            "human_plan_sha256": parent.digest((root / HUMAN_PLAN).read_bytes()),
            "producer_sha256": parent.digest(Path(__file__).read_bytes()),
            "frozen_dependency_hashes": plan["dependency_hashes"], "parent_pr": 175,
            "parent_published_head": plan["parent_published_head"], "type_id_encoding": plan["type_id_encoding"],
            "source_credit": catalog["credit"], "source_permission": catalog["permission"],
            "reddy_source_commit": parent.reddy.COMMIT, "verified_local_files": manifest["selected_local_files"],
            "pairing": pairing, **compare_types(paired),
            "limits": "Exposed finite positional type relation only; no physical word/glyph correspondence, fitted alphabet map, historically used conversion, generalization, null/tail, language or translation. Reddy raw files remain local."}


def protected_paths(reference):
    paths = [ROOT / name for name in (*FROZEN, PLAN, HUMAN_PLAN)] + [Path(__file__)]
    paths.extend(reference / name for name in parent.reddy.SELECTED)
    return tuple(p for original in paths for p in (original, original.resolve()))


def protect_output(path, reference, entry_paths=()):
    resolved = path.resolve()
    for source in (*entry_paths, *protected_paths(reference)):
        same_named_entry = (
            unicodedata.normalize("NFC", resolved.name).casefold()
            == unicodedata.normalize("NFC", source.name).casefold()
            and resolved.parent.exists() and source.parent.exists()
            and resolved.parent.samefile(source.parent))
        if resolved == source.resolve() or same_named_entry or path.exists() and source.exists() and path.samefile(source):
            raise ValueError("positional type output aliases a frozen input, reference, plan or producer")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        entry_paths = protected_paths(args.reference) if args.output else ()
        if args.output: protect_output(args.output, args.reference, entry_paths)
        result = run_audit(args.reference)
        if args.check: parent.check_parent(result, args.check)
        if args.output:
            payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
            protect_output(args.output, args.reference, entry_paths)
            args.output.write_text(payload, encoding="utf-8")
        elif not args.check: print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"positional type audit failed: {error}\n")
    if args.check: print("complete positional type report reproduces")


if __name__ == "__main__":
    main()
