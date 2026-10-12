"""Compare literal H/Reddy envelopes, source order and pre-exclusion counts."""

import argparse
import hashlib
import json
from pathlib import Path

try:
    from . import audit_reddy_sources as reddy
    from .audit_historical_interlinear import audit, parse_historical, read_pinned_archive
    from .reconstruct_historical_tokens import normalize_body, reconstruct
except ImportError:
    import audit_reddy_sources as reddy
    from audit_historical_interlinear import audit, parse_historical, read_pinned_archive
    from reconstruct_historical_tokens import normalize_body, reconstruct


ROOT = Path(__file__).resolve().parents[1]
PLAN = "research/historical/reddy-envelopes-plan.json"
HUMAN_PLAN = "research/historical/REDDY_ENVELOPES_PLAN.md"
FROZEN = (
    "data/historical/interlinear-16e6.json", "data/historical/text16e6.zip",
    "scripts/audit_historical_interlinear.py", "research/historical/intake.json",
    "scripts/reconstruct_historical_tokens.py", "research/historical/parser-plan.json",
    "research/historical/parsing.json", "scripts/audit_reddy_sources.py",
    "research/literature/reddy-source-manifest.json", "research/literature/REDDY_SOURCE_PLAN.md",
    "research/literature/reddy-source-intake.json",
)
STAGES = (
    "comment/filler/separator normalization retaining coded fallbacks",
    "accepted listed-code deletion before manual exclusions",
)
STREAMS = ("h_fallback", "h_code_deleted", "reddy")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("ascii")


def read_json(path):
    def reject_constant(value):
        raise ValueError(f"nonfinite JSON constant: {value}")

    def unique(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_bytes(), parse_constant=reject_constant, object_pairs_hook=unique)


def load_plan(root):
    plan = read_json(root / PLAN)
    expected = {
        "plan_version": 1, "key_fields": ["page", "native_unit_or_placement", "native_line", "transcriber_tag"],
        "exact_literal_join": True, "include_all_union_records": True, "h_count_stages": list(STAGES),
        "reddy_file": "data/voy.ann.wds", "execute_author_code": False, "redistribute_raw_text": False,
        "manual_exclusions": False, "ordinal_base": 0, "physical_file_line_base": 1,
        "reference_snapshot": reddy.COMMIT,
    }
    if any(canonical(plan.get(key)) != canonical(value) for key, value in expected.items()):
        raise ValueError("literal-envelope plan options differ")
    if set(plan["dependency_hashes"]) != set(FROZEN):
        raise ValueError("literal-envelope dependency set differs")
    for name in FROZEN:
        if digest((root / name).read_bytes()) != plan["dependency_hashes"][name]:
            raise ValueError(f"frozen literal-envelope dependency differs: {name}")
    return plan


def check_parent(value, path):
    if canonical(value) != canonical(read_json(path)):
        raise ValueError(f"complete accepted parent report differs: {path.name}")


def check_key(key):
    if len(key) != 4 or any(type(part) is not str or not part or any(c.isspace() for c in part) for part in key):
        raise ValueError("malformed literal four-field record key")
    return tuple(key)


def describe_sources(native, annotated, special_codes):
    h_rows, r_rows = [], []
    for index, row in enumerate(native):
        if row.transcriber != "H":
            raise ValueError("non-H record in selected native population")
        key = check_key((row.page, row.unit, row.line, row.transcriber))
        fallback = normalize_body(row.body, set())[0]
        deleted = normalize_body(row.body, special_codes)[0]
        h_rows.append({"key": key, "ordinal": index, "file_line": row.physical_line,
                       "locator": row.locator, "raw_body_sha256": digest(row.body.encode("latin-1")),
                       "fallback_tokens": len(fallback), "code_deleted_tokens": len(deleted),
                       "fallback_token_vector_sha256": reddy.token_hash(fallback),
                       "code_deleted_token_vector_sha256": reddy.token_hash(deleted)})
    for index, row in enumerate(annotated):
        key = check_key(row["header"])
        tokens = row["tokens"]
        if not tokens or any(type(t) is not str or not t or any(c.isspace() for c in t) for t in tokens):
            raise ValueError("invalid annotated token vector")
        r_rows.append({"key": key, "ordinal": index, "file_line": row["native_file_line"],
                       "tokens": len(tokens), "token_vector_sha256": reddy.token_hash(tokens)})
    return h_rows, r_rows


def index_rows(rows):
    result, prior_line = {}, 0
    for index, row in enumerate(rows):
        key = check_key(row["key"])
        if key in result:
            raise ValueError("duplicate literal record key")
        if (type(row["ordinal"]) is not int or row["ordinal"] != index
                or type(row["file_line"]) is not int or row["file_line"] <= prior_line):
            raise ValueError("source ordinal or physical file-line order differs")
        for field in ("fallback_tokens", "code_deleted_tokens") if "fallback_tokens" in row else ("tokens",):
            if type(row[field]) is not int or row[field] < 0:
                raise ValueError("invalid record token count")
        result[key], prior_line = row, row["file_line"]
    return result


def accounting(rows):
    result = {"union_records": len(rows), "shared_records": sum(r["presence"] == "shared" for r in rows),
              "h_only_records": sum(r["presence"] == "h_only" for r in rows),
              "reddy_only_records": sum(r["presence"] == "reddy_only" for r in rows)}
    for stream in STREAMS:
        present = [r for r in rows if r["counts"][stream] is not None]
        result[stream] = {
            "records": len(present), "empty_records": sum(r["counts"][stream] == 0 for r in present),
            "nonempty_records": sum(r["counts"][stream] > 0 for r in present),
            "tokens": sum(r["counts"][stream] for r in present),
            "shared_tokens": sum(r["counts"][stream] for r in present if r["presence"] == "shared"),
            "unmatched_tokens": sum(r["counts"][stream] for r in present if r["presence"] != "shared"),
        }
    for stream in STREAMS[:2]:
        deltas = [r["shared_h_minus_reddy"][stream] for r in rows if r["presence"] == "shared"]
        result[stream]["shared_count_comparison"] = {
            "equal_records": sum(d == 0 for d in deltas), "unequal_records": sum(d != 0 for d in deltas),
            "positive_records": sum(d > 0 for d in deltas), "negative_records": sum(d < 0 for d in deltas),
            "positive_sum": sum(d for d in deltas if d > 0), "negative_sum": sum(d for d in deltas if d < 0),
            "net_sum": sum(deltas), "absolute_sum": sum(abs(d) for d in deltas),
        }
        result[stream]["all_tokens_minus_reddy"] = result[stream]["tokens"] - result["reddy"]["tokens"]
    return result


def compare_records(h_rows, r_rows):
    h, r = index_rows(h_rows), index_rows(r_rows)
    rows = []
    for key in sorted(h.keys() | r.keys()):
        a, b = h.get(key), r.get(key)
        counts = {"h_fallback": a["fallback_tokens"] if a else None,
                  "h_code_deleted": a["code_deleted_tokens"] if a else None,
                  "reddy": b["tokens"] if b else None}
        differences = {name: counts[name] - counts["reddy"] if a and b else None for name in STREAMS[:2]}
        rows.append({"key": list(key), "presence": "shared" if a and b else "h_only" if a else "reddy_only",
                     "h": {k: v for k, v in a.items() if k != "key"} if a else None,
                     "reddy": {k: v for k, v in b.items() if k != "key"} if b else None,
                     "counts": counts, "shared_h_minus_reddy": differences,
                     "shared_count_equal": {name: d == 0 if d is not None else None for name, d in differences.items()}})
    shared = h.keys() & r.keys()
    left = [list(row["key"]) for row in h_rows if tuple(row["key"]) in shared]
    right = [list(row["key"]) for row in r_rows if tuple(row["key"]) in shared]
    order = {"shared_records": len(shared), "h_ordered_shared_keys_sha256": digest(canonical(left)),
             "reddy_ordered_shared_keys_sha256": digest(canonical(right)), "exact_shared_order_equal": left == right,
             "discordant_shared_ranks": [{"shared_rank": i, "h_key": a, "reddy_key": b}
                                          for i, (a, b) in enumerate(zip(left, right, strict=True)) if a != b]}
    pages = sorted({row["key"][0] for row in rows})
    return {"summary": accounting(rows), "shared_order": order,
            "pages": [{"page": page, **accounting([r for r in rows if r["key"][0] == page])} for page in pages],
            "all_union_records": rows}


def run_audit(reference, root=ROOT):
    plan = load_plan(root)
    if root.resolve() != reddy.ROOT.resolve():
        raise ValueError("accepted Reddy reader must use the same repository root")
    manifest = read_json(root / reddy.MANIFEST)
    raw = reddy.read_selected(reference, manifest)
    check_parent(reddy.make_report(reference), root / reddy.REPORT)
    check_parent(audit(root), root / "research/historical/intake.json")
    check_parent(reconstruct(root)[0], root / "research/historical/parsing.json")
    catalog = read_json(root / "data/historical/interlinear-16e6.json")
    member = read_pinned_archive((root / catalog["path"]).read_bytes(), catalog)
    native = [row for row in parse_historical(member)[0] if row.transcriber == "H"]
    annotated = reddy.annotated(raw[plan["reddy_file"]])[0]
    parser_plan = read_json(root / "research/historical/parser-plan.json")
    result = compare_records(*describe_sources(native, annotated, set(parser_plan["special_codes"])))
    return {"audit_version": 1, "scope": plan["scope"],
            "plan_sha256": digest((root / PLAN).read_bytes()),
            "human_plan_sha256": digest((root / HUMAN_PLAN).read_bytes()),
            "producer_sha256": digest(Path(__file__).read_bytes()),
            "frozen_dependency_hashes": plan["dependency_hashes"],
            "source_credit": catalog["credit"], "source_permission": catalog["permission"],
            "archive_url": catalog["archive_url"], "archive_sha256": catalog["archive_sha256"],
            "member": catalog["member"], "member_sha256": catalog["member_sha256"],
            "reddy_source_commit": reddy.COMMIT, "reddy_source_tree": reddy.TREE,
            "verified_local_files": manifest["selected_local_files"],
            "key_fields": plan["key_fields"], "ordinal_base": 0, "physical_file_line_base": 1,
            "record_output_order": "lexicographic literal key; original source ordinals retained separately",
            "key_order_digest_encoding": "ASCII sorted-key compact JSON with final newline",
            "token_vector_digest_encoding": "UTF-8 compact JSON, ensure_ascii=False, with final newline",
            **result,
            "limits": "Nominal envelope/order/count correspondence only; not text, alphabet, glyph, physical-line, original-author execution, historical byte identity or decipherment. Reddy raw files remain local: no license found in pinned tree."}


def protect_output(path, reference):
    protected = [ROOT / name for name in (*FROZEN, PLAN, HUMAN_PLAN)] + [Path(__file__)]
    protected.extend(reference / name for name in reddy.SELECTED)
    if any(path.resolve() == source.resolve() or path.exists() and source.exists() and path.samefile(source)
           for source in protected):
        raise ValueError("literal-envelope output aliases a frozen input, local reference, plan or producer")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output, args.reference)
        result = run_audit(args.reference)
        if args.check:
            check_parent(result, args.check)
        if args.output:
            payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
            protect_output(args.output, args.reference)
            args.output.write_text(payload, encoding="utf-8")
        elif not args.check:
            print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"literal-envelope audit failed: {error}\n")
    if args.check:
        print("complete literal-envelope report reproduces")


if __name__ == "__main__":
    main()
