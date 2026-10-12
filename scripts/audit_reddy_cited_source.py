"""Audit current cited bytes and one fixed publication sample, without glyph repair."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import subprocess

try:
    from . import audit_reddy_sources as parent
except ImportError:
    import audit_reddy_sources as parent

ROOT = Path(__file__).resolve().parents[1]
PLAN = "research/literature/reddy-cited-source-plan.json"
HUMAN_PLAN = "research/literature/REDDY_CITED_SOURCE_PLAN.md"
FROZEN = ("research/literature/methods.json", parent.MANIFEST, parent.PLAN, parent.REPORT,
          "scripts/audit_reddy_sources.py")
REFERENCES = ("cited-voynich.now", "mirror-voynich-now.txt", "paper.pdf", "figure1.txt")
CLASSES = ("blank", "comment_only", "page_envelope", "record_envelope", "unrecognized_outside_comment")
ENVELOPE = re.compile(r"^[ \t]*<([^<>]+)>(.*)$")


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")


def read_json(path):
    def unique(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError(f"nonfinite JSON constant: {value}")
    return json.loads(path.read_bytes(), object_pairs_hook=unique, parse_constant=invalid)


def check_report(value, path):
    if canonical(value) != canonical(read_json(path)):
        raise ValueError(f"complete accepted/report payload differs: {path.name}")


def load_plan(root):
    plan = read_json(root / PLAN)
    expected = {"plan_version": 1, "current_cited_tokenization": False, "comparison_cases": ["full", "b"],
                "retain_all_mismatch_positions": True, "raw_sources_redistributed": False,
                "author_program_executed": False, "source_snapshot": parent.COMMIT,
                "cited_paper_url_literal": "http://www.voynich.net/reeds/gillogly/voynich.now",
                "current_cited_retrieval_url": "https://www.voynich.net/reeds/gillogly/voynich.now",
                "mirror_url": "https://www.voynich.nu/hist/rand/voynich_now.txt"}
    expected["cited_comment_model"] = "Balanced/nested curly comment mask carried across physical LF lines; retain errors and all raw prefix-envelope candidates, including masked candidates"
    expected["cited_locator_policy"] = "Literal line-initial angle-envelope string; first dot only separates page prefix from opaque suffix; no H tag, unit alias or physical-locus crosswalk assumed"
    expected["comparison_scope"] = "Exact nominal page f81v only, all original tokens and native reference-record descriptors; paragraph whitespace has no native-line alignment implication"
    figure = {"number": 1, "page_label": "f81v", "pdf_page_1based": 2, "printed_page": 79,
              "crop_pixels_at_dpi": 72, "crop_x": 314, "crop_y": 373, "crop_width": 226, "crop_height": 317,
              "pdftotext_version": "24.04.0", "layout": True, "nopgbrk": True,
              "first_token": "BAR", "last_two_tokens": ["OPON", "OEFOE"],
              "token_rule": "Unchanged whitespace split; require literal ASCII A-Z/0-9/asterisk tokens; no symbol repair/case fold"}
    if any(canonical(plan.get(key)) != canonical(value) for key, value in expected.items()) or canonical(plan["figure"]) != canonical(figure):
        raise ValueError("cited-source/figure plan options differ")
    if set(plan["dependency_hashes"]) != set(FROZEN) or set(plan["reference_files"]) != set(REFERENCES):
        raise ValueError("cited-source/figure pin set differs")
    for name in FROZEN:
        if parent.digest((root / name).read_bytes()) != plan["dependency_hashes"][name]:
            raise ValueError(f"frozen cited-source dependency differs: {name}")
    return plan


def read_references(reference, plan):
    values = {}
    for name, pin in plan["reference_files"].items():
        raw = (reference / name).read_bytes()
        if len(raw) != pin["bytes"] or parent.digest(raw) != pin["sha256"]:
            raise ValueError(f"current source/publication reference identity differs: {name}")
        values[name] = raw
    if values[REFERENCES[0]] != values[REFERENCES[1]]:
        raise ValueError("two pinned current cited-source copies differ")
    return values


def native_census(raw):
    physical = raw.split(b"\n")
    if physical[-1] == b"": physical.pop()
    counts = Counter(dict.fromkeys(CLASSES, 0))
    depth, current_page = 0, None
    records, headers, candidates, unrecognized, errors = [], [], [], [], []
    locators, body_characters = defaultdict(list), Counter()
    for number, raw_line in enumerate(physical, 1):
        line = raw_line.removesuffix(b"\r").decode("latin-1")
        initial_depth = depth
        prefix = ENVELOPE.fullmatch(line)
        payload = []
        for offset, c in enumerate(line):
            if c == "{": depth += 1
            elif c == "}":
                if depth: depth -= 1
                else:
                    payload.append(c)
                    errors.append({"physical_file_line": number, "character_offset": offset, "error": "unmatched_closing_brace"})
            elif depth == 0: payload.append(c)
        outside = "".join(payload)
        outside_match = ENVELOPE.fullmatch(outside)
        supported = bool(prefix and prefix[1] and not any(c.isspace() or c in "{}" for c in prefix[1]))
        active = bool(supported and initial_depth == 0 and outside_match and outside_match[1] == prefix[1])
        if prefix:
            candidates.append({"physical_file_line": number, "literal_locator": prefix[1],
                               "initial_comment_depth": initial_depth, "literal_syntax_supported": supported,
                               "recognized_as_active": active, "raw_physical_line_sha256": parent.digest(raw_line)})
        if not line.strip(): category = "blank"
        elif not outside.strip(): category = "comment_only"
        elif active:
            key = prefix[1]
            if "." not in key:
                category, current_page = "page_envelope", key
                headers.append({"physical_file_line": number, "literal_locator": key,
                                "raw_physical_line_sha256": parent.digest(raw_line),
                                "outside_comment_payload_nonwhitespace": sum(not c.isspace() for c in outside_match[2])})
            else:
                category = "record_envelope"
                page, _, suffix = key.partition(".")
                body = outside_match[2]
                body_characters.update(c for c in body if not c.isspace())
                row = {"source_record_ordinal": len(records), "physical_file_line": number, "literal_locator": key,
                       "page_prefix_before_first_dot": page, "opaque_suffix_after_first_dot": suffix,
                       "preceding_page_header": current_page, "prefix_matches_page_header": page == current_page,
                       "raw_physical_line_sha256": parent.digest(raw_line),
                       "body_nonwhitespace_codepoints_outside_comments": sum(not c.isspace() for c in body)}
                records.append(row); locators[key].append(number)
        else:
            category = "unrecognized_outside_comment"
            unrecognized.append({"physical_file_line": number, "raw_physical_line_sha256": parent.digest(raw_line),
                                 "outside_comment_nonwhitespace_codepoints": sum(not c.isspace() for c in outside)})
        counts[category] += 1
    if depth: errors.append({"physical_file_line": len(physical), "error": "unclosed_comment_at_eof", "remaining_depth": depth})
    pages = sorted({row["page_prefix_before_first_dot"] for row in records})
    return {"physical_LF_lines": len(physical), "final_LF": raw.endswith(b"\n"), "CRLF_sequences": raw.count(b"\r\n"),
            "lone_CR_bytes": raw.count(b"\r") - raw.count(b"\r\n"), "line_classification": dict(counts),
            "comment_lexical_model_valid": not errors, "all_comment_model_errors": errors,
            "active_record_envelopes": len(records), "record_bearing_literal_page_prefixes": len(pages),
            "page_header_envelopes": len(headers), "distinct_page_header_identifiers": len({row["literal_locator"] for row in headers}),
            "all_raw_prefix_envelope_candidates": candidates, "all_active_page_headers": headers,
            "all_active_record_envelopes": records, "all_unrecognized_lines": unrecognized,
            "duplicate_record_locators": [{"literal_locator": key, "physical_file_lines": numbers} for key, numbers in sorted(locators.items()) if len(numbers) > 1],
            "out_of_context_records": [row for row in records if not row["prefix_matches_page_header"]],
            "pages": [{"literal_page_prefix": page, "record_envelopes": sum(row["page_prefix_before_first_dot"] == page for row in records)} for page in pages],
            "record_body_nonwhitespace_notation_counts_outside_comments": [{"codepoint": f"U+{ord(c):04X}", "count": n} for c, n in sorted(body_characters.items())],
            "locator_order_sha256": parent.digest(canonical([row["literal_locator"] for row in records])),
            "raw_line_digest_encoding": "Original physical bytes without LF; CR retained in digest if present",
            "word_tokenization_performed": False}


def extract_figure(reference, figure):
    result = subprocess.run(["pdftotext", "-v"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    version = (result.stderr + result.stdout).decode("utf-8").splitlines()[0]
    if version != "pdftotext version " + figure["pdftotext_version"]:
        raise ValueError("fixed publication extractor version differs")
    args = ["pdftotext", "-f", str(figure["pdf_page_1based"]), "-l", str(figure["pdf_page_1based"]),
            "-r", str(figure["crop_pixels_at_dpi"]), "-x", str(figure["crop_x"]), "-y", str(figure["crop_y"]),
            "-W", str(figure["crop_width"]), "-H", str(figure["crop_height"]), "-layout", "-nopgbrk",
            str(reference / "paper.pdf"), "-"]
    raw = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    if raw != (reference / "figure1.txt").read_bytes():
        raise ValueError("complete fixed Figure1 extraction bytes differ")
    return raw


def figure_tokens(raw, figure):
    tokens = raw.decode("utf-8").split()
    if (not tokens or tokens[0] != figure["first_token"] or tokens[-2:] != figure["last_two_tokens"]
            or any(not re.fullmatch(r"[A-Z0-9*]+", token) for token in tokens)):
        raise ValueError("fixed Figure1 anchors or literal notation differ")
    return tokens


def compare_figure(tokens, rows, page):
    reference, provenance, descriptors, seen, prior_line = [], [], [], set(), 0
    for ordinal, row in enumerate(rows):
        header = tuple(row["header"])
        if (len(header) != 4 or any(type(value) is not str or not value for value in header) or header in seen
                or type(row["native_file_line"]) is not int or row["native_file_line"] <= prior_line):
            raise ValueError("native reference header/order provenance differs")
        seen.add(header); prior_line = row["native_file_line"]
        if header[0] != page: continue
        descriptors.append({"native_header": list(header), "source_record_ordinal": ordinal,
                            "physical_file_line": row["native_file_line"], "tokens": len(row["tokens"]),
                            "token_vector_sha256": parent.token_hash(row["tokens"])})
        for index, token in enumerate(row["tokens"]):
            reference.append(token)
            provenance.append({"native_header": list(header), "source_record_ordinal": ordinal,
                               "physical_file_line": row["native_file_line"], "local_token_index": index})
    mismatches = []
    for index in range(max(len(tokens), len(reference))):
        a, b = tokens[index] if index < len(tokens) else None, reference[index] if index < len(reference) else None
        if a != b:
            mismatches.append({"page_token_index": index,
                               "figure_token_sha256": parent.digest(a.encode("utf-8")) if a is not None else None,
                               "reference_token_sha256": parent.digest(b.encode("utf-8")) if b is not None else None,
                               "reference_provenance": provenance[index] if index < len(provenance) else None})
    return {"exact_nominal_page": page, "reference_page_present": bool(descriptors), "figure_tokens": len(tokens),
            "reference_tokens": len(reference), "figure_vector_sha256": parent.token_hash(tokens),
            "reference_vector_sha256": parent.token_hash(reference), "exact_token_vector_equal": bool(descriptors) and tokens == reference,
            "all_reference_record_descriptors": descriptors, "all_mismatch_positions": mismatches}


def run_audit(reference, root=ROOT):
    plan = load_plan(root)
    if root.resolve() != parent.ROOT.resolve(): raise ValueError("accepted intake must use the same repository root")
    raw = read_references(reference, plan)
    manifest = read_json(root / parent.MANIFEST)
    selected = parent.read_selected(reference / "reddy", manifest)
    check_report(parent.make_report(reference / "reddy"), root / parent.REPORT)
    extracted = extract_figure(reference, plan["figure"])
    tokens = figure_tokens(extracted, plan["figure"])
    comparisons = []
    for case, name in (("full", "data/voy.ann.wds"), ("b", "data/voy.b.ann.wds")):
        rows = parent.annotated(selected[name])[0]
        comparisons.append({"case": case, "reference_file": name, **compare_figure(tokens, rows, plan["figure"]["page_label"])})
    census = native_census(raw["cited-voynich.now"])
    accepted = read_json(root / parent.REPORT)["cases"][0]
    return {"audit_version": 1, "scope": plan["scope"], "plan_sha256": parent.digest((root / PLAN).read_bytes()),
            "human_plan_sha256": parent.digest((root / HUMAN_PLAN).read_bytes()), "producer_sha256": parent.digest(Path(__file__).read_bytes()),
            "frozen_dependency_hashes": plan["dependency_hashes"], "verified_reference_files": plan["reference_files"],
            "verified_selected_reddy_files": manifest["selected_local_files"], "source_commit": parent.COMMIT,
            "cited_paper_url_literal": plan["cited_paper_url_literal"], "current_cited_retrieval_url": plan["current_cited_retrieval_url"],
            "mirror_url": plan["mirror_url"], "current_cited_and_mirror_bytes_equal": True,
            "current_cited_source_census": census, "figure_selection": plan["figure"], "figure_comparisons": comparisons,
            "nominal_population_comparison": {"current_cited_record_envelopes": census["active_record_envelopes"],
                                               "current_cited_record_bearing_page_prefixes": census["record_bearing_literal_page_prefixes"],
                                               "recovered_full_annotated_records": accepted["annotated_native_records"],
                                               "recovered_full_annotated_pages": accepted["annotated_pages"],
                                               "paper_reported_counts": accepted["paper_reported_counts"],
                                               "current_cited_word_counts_measured": False},
            "limits": "Current URL/mirror identity and fixed PDF text-layer correspondence only; not 2011 full-corpus bytes, native-line/glyph/image alignment, original preprocessing, Table2 replication, language or translation. Raw corpus/PDF/author payloads remain local."}


def protect_output(path, reference):
    paths = [ROOT / name for name in (*FROZEN, PLAN, HUMAN_PLAN)] + [Path(__file__)]
    paths += [reference / name for name in REFERENCES]
    paths += [reference / "reddy" / name for name in parent.SELECTED]
    if any(path.resolve() == p.resolve() or path.exists() and p.exists() and path.samefile(p) for p in paths):
        raise ValueError("cited-source output aliases a frozen source/reference/plan/producer")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        if args.output: protect_output(args.output, args.reference)
        result = run_audit(args.reference)
        if args.check: check_report(result, args.check)
        if args.output:
            payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
            protect_output(args.output, args.reference)
            args.output.write_text(payload, encoding="utf-8")
        elif not args.check: print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"current cited-source/figure audit failed: {error}\n")
    if args.check: print("complete current cited-source/figure report reproduces")


if __name__ == "__main__": main()
