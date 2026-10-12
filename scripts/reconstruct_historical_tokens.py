"""Reconstruct declared historical token variants with an exclusion ledger.

No repetition statistic, null sampling, or claimed decipherment is performed.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import zipfile

try:
    from .audit_historical_interlinear import ROOT, parse_historical, read_pinned_archive, remove_comments
except ImportError:
    from audit_historical_interlinear import ROOT, parse_historical, read_pinned_archive, remove_comments


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(data):
    return (json.dumps(data, ensure_ascii=True, separators=(",", ":")) + "\n").encode("ascii")


def normalize_body(body, special_codes):
    """Apply code deletion before comment/filler removal; retain raw offsets."""
    remove_comments(body)
    deleted, events = set(), []
    for match in re.finditer(r"\{([^{}]*)\}", body):
        if match[1] in special_codes:
            position = match.start() - 1
            if position < 0 or not re.fullmatch(r"[a-z*]", body[position]) or position in deleted:
                raise ValueError("listed code lacks one immediate encoded fallback character")
            deleted.add(position)
            events.append({"raw_offset": position, "code": match[1], "character": body[position]})
    after_codes = "".join(c for i, c in enumerate(body) if i not in deleted)
    payload, comment_count = remove_comments(after_codes)
    payload = payload.replace("!", "").replace("%", "")
    tokens = re.sub(r"[.,=\-]", " ", payload).split()
    if any(not re.fullmatch(r"[a-z*]+", token) for token in tokens):
        raise ValueError("unsupported residual historical token notation")
    return tokens, events, comment_count


def rule_matches(record, rule):
    return (record.page == rule["page"] and record.unit == rule["unit"]
            and ("line" not in rule or record.line == rule["line"]))


def make_variant(records, normalized, plan, ring_policy, column_unit):
    if ring_policy not in plan["ring_policies"] or column_unit not in plan["f66r_column_units"]:
        raise ValueError("variant is outside the frozen policy matrix")
    rows, exclusions, ring_deletions = [], [], []
    phrases = set(plan["figure_label_phrases"])
    for record, tokens in zip(records, normalized, strict=True):
        reasons = [r["rule"] for r in plan["resolved_operational_exclusions"] if rule_matches(record, r)]
        if " ".join(tokens) in phrases:
            reasons.append("exact_figure_label")
        if record.page == "f66r" and record.unit == column_unit:
            reasons.append("f66r_column")
        if record.page == plan["ring_page"] and record.unit == "R2" and ring_policy == "exclude_R2":
            reasons.append("f57v_R2")
        retained = [(i, token) for i, token in enumerate(tokens)]
        if not reasons and record.page == plan["ring_page"] and record.unit in plan["ring_units"]:
            if ring_policy == "exclude_single_character_tokens":
                removed = [(i, token) for i, token in retained if len(token) == 1]
                retained = [(i, token) for i, token in retained if len(token) != 1]
                if removed:
                    ring_deletions.append({"locator": record.locator,
                                           "removed_original_token_indices": [i for i, _ in removed],
                                           "removed_encoded_tokens": [t for _, t in removed]})
        if reasons:
            exclusions.append({"locator": record.locator, "reasons": reasons,
                               "body_sha256": digest(record.body.encode("latin-1")),
                               "normalized_tokens_removed": len(tokens)})
            retained = []
        rows.append({"locator": record.locator, "exclusion_reasons": reasons,
                     "tokens": [token for _, token in retained],
                     "original_token_indices": [i for i, _ in retained]})
    flat = [{"token": token, "locator": row["locator"], "original_token_index": index}
            for row in rows for token, index in zip(row["tokens"], row["original_token_indices"], strict=True)]
    summary = {
        "ring_policy": ring_policy, "f66r_column_unit": column_unit,
        "input_records": len(records), "records_excluded_whole": len(exclusions),
        "retained_nonempty_records": sum(bool(row["tokens"]) for row in rows),
        "retained_tokens": len(flat),
        "difference_from_reported_count": len(flat) - plan["reported_token_count"],
        "normalized_tokens_removed_whole": sum(e["normalized_tokens_removed"] for e in exclusions),
        "single_character_ring_tokens_removed": sum(len(e["removed_original_token_indices"]) for e in ring_deletions),
        "exclusions": exclusions, "ring_token_deletions": ring_deletions,
        "record_corpus_sha256": digest(encoded(rows)), "flat_corpus_sha256": digest(encoded(flat)),
    }
    before = sum(len(tokens) for tokens in normalized)
    if before != (len(flat) + summary["normalized_tokens_removed_whole"]
                  + summary["single_character_ring_tokens_removed"]):
        raise ValueError("token ledger does not reconcile")
    return summary, {"records": rows, "flat_tokens_with_provenance": flat}


def reconstruct(root=ROOT):
    plan_bytes = (root / "research/historical/parser-plan.json").read_bytes()
    plan = json.loads(plan_bytes)
    if (plan.get("plan_version") != 1 or plan.get("tune_to_reported_count") is not False
            or plan["ring_policies"] != ["exclude_R2", "exclude_single_character_tokens"]
            or plan["f66r_column_units"] != ["M", "L"]):
        raise ValueError("unsupported historical parser plan")
    catalog = json.loads((root / "data/historical/interlinear-16e6.json").read_text())
    if (catalog.get("schema_version") != 1 or catalog["id"] != plan["source_id"] or catalog["selected_transcriber"] != plan["transcriber"]
            or any(catalog[key] != plan[key] for key in ("archive_sha256", "member_sha256"))):
        raise ValueError("plan and historical source identity differ")
    member = read_pinned_archive((root / catalog["path"]).read_bytes(), catalog)
    records, _ = parse_historical(member)
    records = [r for r in records if r.transcriber == plan["transcriber"]]
    normalized, code_events = [], []
    fallback_retained_token_count = 0
    comment_occurrences = 0
    for record in records:
        fallback_retained_token_count += len(normalize_body(record.body, set())[0])
        tokens, events, comments = normalize_body(record.body, set(plan["special_codes"]))
        normalized.append(tokens)
        comment_occurrences += comments
        if events:
            code_events.append({"locator": record.locator, "body_sha256": digest(record.body.encode("latin-1")),
                                "events": events})
    labels = {phrase: [r.locator for r, tokens in zip(records, normalized, strict=True)
                       if " ".join(tokens) == phrase] for phrase in plan["figure_label_phrases"]}
    selectors = {rule["rule"]: [r.locator for r in records if rule_matches(r, rule)]
                 for rule in plan["resolved_operational_exclusions"]}
    if not all(selectors.values()):
        raise ValueError("an operational exclusion selector has no native records")
    variants, corpora = [], []
    for ring in plan["ring_policies"]:
        for column in plan["f66r_column_units"]:
            summary, corpus = make_variant(records, normalized, plan, ring, column)
            variants.append(summary)
            corpora.append({"ring_policy": ring, "f66r_column_unit": column, **corpus})
    corpus_export = {
        "plan_sha256": digest(plan_bytes), "source_id": catalog["id"],
        "source_credit": catalog["credit"], "source_permission": catalog["permission"],
        "archive_url": catalog["archive_url"], "archive_sha256": catalog["archive_sha256"],
        "member_sha256": catalog["member_sha256"],
        "token_index_definition": "Index in the record after syntactic normalization, before manual exclusions",
        "variants": corpora,
    }
    report = {
        "parser_version": 1, "status": "approximate_reconstruction_with_unresolved_choices",
        "plan_sha256": digest(plan_bytes),
        "parser_sha256": digest(Path(__file__).read_bytes()),
        "reader_sha256": digest(Path(__file__).with_name("audit_historical_interlinear.py").read_bytes()),
        "corpus_export_sha256": digest(encoded(corpus_export)),
        "archive_sha256": plan["archive_sha256"], "member_sha256": plan["member_sha256"],
        "supplement_sha256": plan["supplement_sha256"],
        "source_records_selected": len(records),
        "syntactic_normalization": {
            "normalized_tokens_with_coded_fallbacks_retained": fallback_retained_token_count,
            "tokens_before_manual_exclusions": sum(len(t) for t in normalized),
            "empty_records": sum(not t for t in normalized),
            "curly_comments_removed": comment_occurrences,
            "special_code_event_counts": dict(sorted(Counter(e["code"] for r in code_events for e in r["events"]).items())),
            "special_code_events": code_events,
        },
        "operational_selector_locators": selectors,
        "exact_figure_label_matches": labels,
        "unmatched_figure_label_phrases": [phrase for phrase, matches in labels.items() if not matches],
        "reported_token_count": plan["reported_token_count"], "variants": variants,
        "limits": "No author-compatible input identity, glyph segmentation, repetition statistic, null or decipherment established",
    }
    return report, corpus_export


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--corpus-output", type=Path)
    args = parser.parse_args()
    try:
        catalog_path = ROOT / "data/historical/interlinear-16e6.json"
        catalog = json.loads(catalog_path.read_text())
        protected = {catalog_path.resolve(), (ROOT / catalog["path"]).resolve(),
                     (ROOT / "research/historical/parser-plan.json").resolve(), Path(__file__).resolve()}
        outputs = [p.resolve() for p in (args.output, args.corpus_output) if p]
        if len(outputs) != len(set(outputs)) or any(p in protected for p in outputs):
            raise ValueError("outputs must be distinct and must not overwrite source, catalog, plan or parser")
        report, corpus = reconstruct(ROOT)
        if args.check and report != json.loads(args.check.read_text()):
            raise ValueError("historical parsing report differs")
        if args.output:
            args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        elif not args.check:
            print(json.dumps(report, indent=2))
        if args.corpus_output:
            args.corpus_output.write_bytes(encoded(corpus))
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as error:
        parser.exit(1, f"historical reconstruction failed: {error}\n")
    if args.check:
        print("historical parsing report reproduces")


if __name__ == "__main__":
    main()
