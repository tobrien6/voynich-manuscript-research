"""Apply one frozen primary-table parser, preserving all unmatched H notation."""

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import re

try:
    from .audit_historical_interlinear import audit, parse_historical, read_pinned_archive
    from .reconstruct_historical_tokens import normalize_body, reconstruct
except ImportError:
    from audit_historical_interlinear import audit, parse_historical, read_pinned_archive
    from reconstruct_historical_tokens import normalize_body, reconstruct

ROOT = Path(__file__).resolve().parents[1]
PLAN = "research/historical/currier-definition-plan.json"
HUMAN_PLAN = "research/historical/CURRIER_DEFINITION_PLAN.md"
SOURCE = "research/transliteration/currier-conversion-source.json"
FROZEN = ("data/historical/interlinear-16e6.json", "data/historical/text16e6.zip",
          "scripts/audit_historical_interlinear.py", "research/historical/intake.json",
          "scripts/reconstruct_historical_tokens.py", "research/historical/parser-plan.json",
          "research/historical/parsing.json", SOURCE)
REFERENCES = ("Curr-Eva_def.bit", "Bitrans_manual.pdf", "000_README.txt")
ALPHABET = set("abcdefghijklmnopqrstuvwxyz*")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")


def vector_sha(tokens):
    return sha((json.dumps(tokens, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))


def read_json(path):
    def unique(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f"nonfinite JSON value: {value}")

    return json.loads(path.read_bytes(), object_pairs_hook=unique, parse_constant=invalid)


def check_report(actual, path):
    if canonical(actual) != canonical(read_json(path)):
        raise ValueError(f"complete report differs: {path.name}")


def load_plan(root):
    plan = read_json(root / PLAN)
    options = {"plan_version": 1, "source_pr": 181,
               "source_published_head": "a03ac3589bb138be98a701666a481d9d4b1174e6",
               "direction": "Eva right column to Currier left column",
               "match_policy": "At each source offset choose the longest matching right-column string; emit its left-column code once without rescanning output",
               "unmatched_policy": "Copy one unmatched original codepoint opaquely and flag its original token-local offset; never discard or replace with asterisk",
               "input_token_pattern": "[a-z*]+", "h_special_codes": [], "manual_exclusions": False,
               "preserve_records_and_tokens": True, "include_asterisks": True,
               "comparison_performed": False, "null": False, "raw_text_redistributed": False}
    if any(canonical(plan.get(key)) != canonical(value) for key, value in options.items()):
        raise ValueError("primary-table parser options differ")
    if set(plan["dependency_hashes"]) != set(FROZEN):
        raise ValueError("primary-table dependency set differs")
    for name in FROZEN:
        if sha((root / name).read_bytes()) != plan["dependency_hashes"][name]:
            raise ValueError(f"frozen primary-table dependency differs: {name}")
    return plan


class Definition:
    def __init__(self, rows):
        self.rows = [dict(row) for row in rows]
        self.forward, self.reverse = {}, {}
        seen_lines = set()
        for row in rows:
            left, right, line = row["currier"], row["eva"], row["line"]
            if (not re.fullmatch(r"[A-Z0-9nv]", left) or not re.fullmatch(r"[a-z]+", right)
                    or type(line) is not int or line < 1 or line in seen_lines or left in self.forward or right in self.reverse):
                raise ValueError("malformed or ambiguous definition")
            seen_lines.add(line)
            self.forward[left] = right
            self.reverse[right] = (left, line)
        single = {s for s in self.reverse if len(s) == 1}
        if not ALPHABET.intersection(self.forward) <= single:
            raise ValueError("input-alphabet condition for opaque decoder fails")
        self.patterns = sorted(self.reverse, key=lambda value: (-len(value), value))

    def convert(self, token):
        if not re.fullmatch(r"[a-z*]+", token):
            raise ValueError("unsupported original H notation token")
        output, uses, unmatched, offset, matched_chars = [], Counter(), [], 0, 0
        while offset < len(token):
            match = next((s for s in self.patterns if token.startswith(s, offset)), None)
            if match is None:
                output.append(token[offset])
                unmatched.append({"source_offset": offset, "codepoint": f"U+{ord(token[offset]):04X}"})
                offset += 1
            else:
                left, line = self.reverse[match]
                output.append(left)
                uses[line] += 1
                matched_chars += len(match)
                offset += len(match)
        return "".join(output), uses, unmatched, matched_chars

    def expand(self, output):
        return "".join(self.forward.get(c, c) for c in output)


def verify_definition(reference, catalog):
    artifacts = catalog["artifacts"]
    if len(artifacts) != 3 or {row["reference_name"] for row in artifacts} != set(REFERENCES):
        raise ValueError("primary reference set differs")
    raw = {}
    for row in artifacts:
        value = (reference / row["reference_name"]).read_bytes()
        if len(value) != row["bytes"] or sha(value) != row["sha256"]:
            raise ValueError(f"primary source identity differs: {row['reference_name']}")
        raw[row["reference_name"]] = value
    value = raw[REFERENCES[0]]
    lines = value.decode("ascii").splitlines()
    if (len(lines) != 42 or not value.endswith(b"\n") or b"\r" in value
            or lines[:4] != ["##BIT  Curr Eva- ", "#=%", "<(comment)>", "#(comment) "]):
        raise ValueError("primary definition header/format differs")
    rows, metadata = [], []
    for line, text in enumerate(lines[4:], 5):
        pair = text.split()
        if len(pair) != 2: raise ValueError("malformed primary rule row")
        left, right = pair
        rows.append({"currier": left, "eva": right, "line": line})
        metadata.append({"physical_file_line": line, "left_sha256": sha(left.encode("ascii")),
                         "right_sha256": sha(right.encode("ascii")), "left_codepoints": len(left),
                         "right_codepoints": len(right), "raw_line_sha256": sha(text.encode("ascii"))})
    definition = Definition(rows)
    right = [row["eva"] for row in rows]
    structure = {"physical_lines": len(lines), "line_endings": "LF", "final_newline": True,
                 "header_sha256": sha(lines[0].encode("ascii")), "header_column_codes": ["Curr", "Eva-"],
                 "direction_restriction": None, "separator_marker": "%",
                 "comment_definitions": [{"start": "<", "end": ">", "kind": "limited_extent"},
                                         {"start": "#", "kind": "full_line", "explicit_terminal_space": True}],
                 "rules": len(rows), "unique_left_strings": len(definition.forward), "unique_right_strings": len(definition.reverse),
                 "left_codepoint_lengths": [{"length": 1, "rules": len(rows)}],
                 "right_codepoint_lengths": [{"length": n, "rules": count} for n, count in sorted(Counter(map(len, right)).items())],
                 "right_proper_prefix_pairs": [{"prefix_rule_line": i["line"], "longer_rule_line": j["line"]}
                                               for i in rows for j in rows if i != j and j["eva"].startswith(i["eva"])],
                 "membership_probe_universe": "abcdefghijklmnopqrstuvwxyz*",
                 "codepoints_absent_anywhere_in_right_strings": sorted(ALPHABET - set("".join(right)))}
    failures = []
    for a, b in itertools.product(rows, repeat=2):
        original, intermediate = a["currier"] + b["currier"], a["eva"] + b["eva"]
        back = definition.convert(intermediate)[0]
        if back != original:
            failures.append({"input_rule_lines": [a["line"], b["line"]],
                             "currier_input_sha256": sha(original.encode("ascii")), "eva_output_sha256": sha(intermediate.encode("ascii")),
                             "currier_roundtrip_sha256": sha(back.encode("ascii")), "input_codepoints": len(original),
                             "eva_codepoints": len(intermediate), "roundtrip_codepoints": len(back)})
    synthetic = {"cohort": "Every ordered pair of the 38 distinct Currier rule codes; no manuscript text",
                 "algorithm": "Concatenate original right-column definitions, then consume input left to right using the longest matching right-column string and emit its left-column code; noncumulative; unmatched characters copied opaquely",
                 "cases": len(rows) ** 2, "failures": len(failures),
                 "passes": len(rows) ** 2 - len(failures), "all_failed_cases": failures}
    if any(canonical(actual) != canonical(catalog[key]) for key, actual in
           (("all_rule_metadata", metadata), ("rule_structure", structure), ("synthetic_roundtrip", synthetic))):
        raise ValueError("complete primary source catalog diagnostic differs")
    return definition


def repetitions(groups):
    within, joining = set(), set()
    within_A = joining_A = 0
    nonempty = [(i, row) for i, row in enumerate(groups) if row]
    for row in groups:
        for a, b in zip(row, row[1:]):
            if a == b: within_A += 1; within.add(a)
    for (i, a), (j, b) in zip(nonempty, nonempty[1:]):
        if a[-1] == b[0]: joining_A += 1; joining.add(a[-1])
    return {"A": within_A + joining_A, "B": len(within | joining),
            "within_A": within_A, "joining_A": joining_A, "within_B": len(within), "joining_B": len(joining),
            "B_scope_overlap": len(within & joining), "within_opportunities": sum(max(0, len(row) - 1) for row in groups),
            "joining_opportunities": max(0, len(nonempty) - 1)}


def analyze(native, definition):
    input_groups, output_groups, ledger, unmatched_events = [], [], [], []
    uses = Counter({row["line"]: 0 for row in definition.rows})
    source_chars, output_chars, lengths, output_lengths = Counter(), Counter(), Counter(), Counter()
    source_types, target_types, pairs, prior_line, seen = {}, {}, Counter(), 0, set()
    for ordinal, record in enumerate(native):
        if (record.transcriber != "H" or record.locator != f"{record.page}.{record.unit}.{record.line};H"
                or record.locator in seen or type(record.physical_line) is not int
                or record.physical_line <= prior_line):
            raise ValueError("selected H identity or source order differs")
        seen.add(record.locator); prior_line = record.physical_line
        tokens = normalize_body(record.body, set())[0]
        converted, record_unmatched, matched_chars, matched_uses = [], 0, 0, 0
        for index, token in enumerate(tokens):
            output, counts, unmatched, matched = definition.convert(token)
            if definition.expand(output) != token: raise ValueError("opaque decoder does not recover original token")
            a, b = sha(token.encode("ascii")), sha(output.encode("ascii"))
            if a in source_types and source_types[a] != token or b in target_types and target_types[b] != output:
                raise ValueError("notation type digest collision")
            source_types[a], target_types[b] = token, output
            pairs[(a, b)] += 1
            converted.append(output); uses.update(counts)
            source_chars.update(token); output_chars.update(output); lengths[len(token)] += 1; output_lengths[len(output)] += 1
            matched_chars += matched; matched_uses += sum(counts.values()); record_unmatched += len(unmatched)
            unmatched_events.extend({"selected_H_ordinal": ordinal, "local_token_index": index, **event} for event in unmatched)
            if matched + len(unmatched) != len(token) or sum(counts.values()) + len(unmatched) != len(output):
                raise ValueError("matched/unmatched character accounting differs")
        input_groups.append(tokens); output_groups.append(converted)
        ledger.append({"selected_H_ordinal": ordinal, "native_locator": record.locator, "page": record.page,
                       "unit": record.unit, "line": record.line, "physical_source_file_line": record.physical_line,
                       "parsed_body_sha256": sha(record.body.encode("latin-1")), "tokens": len(tokens),
                       "input_vector_sha256": vector_sha(tokens), "output_vector_sha256": vector_sha(converted),
                       "input_codepoints": sum(map(len, tokens)), "output_codepoints": sum(map(len, converted)),
                       "matched_input_codepoints": matched_chars, "matched_rule_uses": matched_uses,
                       "unmatched_codepoints": record_unmatched, "fully_defined": record_unmatched == 0})
    mappings = {}
    for a, b in pairs:
        if a in mappings and mappings[a] != b: raise ValueError("original type has multiple outputs")
        mappings[a] = b
    if len(set(mappings.values())) != len(mappings): raise ValueError("model output collapses source type equality")
    original_repeat, output_repeat = repetitions(input_groups), repetitions(output_groups)
    if original_repeat != output_repeat: raise ValueError("equality/repeat scopes differ after invertible model")
    types = [{"input_type_sha256": a, "output_type_sha256": b, "occurrences": count,
              "input_codepoints": len(source_types[a]), "output_codepoints": len(target_types[b]),
              "fully_defined": not definition.convert(source_types[a])[2]} for (a, b), count in sorted(pairs.items())]
    nonempty = [i for i, row in enumerate(input_groups) if row]
    gaps = [{"left_H_ordinal": a, "right_H_ordinal": b, "intervening_normalized_empty_H_ordinals": list(range(a + 1, b)),
             "input_equal": input_groups[a][-1] == input_groups[b][0], "output_equal": output_groups[a][-1] == output_groups[b][0]}
            for a, b in zip(nonempty, nonempty[1:]) if b > a + 1]
    return {"records": len(native), "empty_records": len(native) - len(nonempty), "tokens": sum(map(len, input_groups)),
            "input_types": len(source_types), "output_types": len(target_types), "all_tokens_decode_exactly": True,
            "type_bijection_verified": True, "fully_defined_tokens": sum(row["occurrences"] for row in types if row["fully_defined"]),
            "tokens_with_unmatched_symbols": sum(row["occurrences"] for row in types if not row["fully_defined"]),
            "fully_defined_nonempty_records": sum(row["fully_defined"] and row["tokens"] > 0 for row in ledger),
            "records_with_unmatched_symbols": sum(not row["fully_defined"] for row in ledger),
            "input_notation_codepoints": sum(source_chars.values()), "output_notation_codepoints": sum(output_chars.values()),
            "matched_input_codepoints": sum(row["matched_input_codepoints"] for row in ledger),
            "matched_rule_uses": sum(uses.values()), "unmatched_codepoints": len(unmatched_events),
            "input_character_counts": [{"codepoint": f"U+{ord(c):04X}", "count": n} for c, n in sorted(source_chars.items())],
            "output_character_counts": [{"codepoint": f"U+{ord(c):04X}", "count": n} for c, n in sorted(output_chars.items())],
            "input_token_lengths": [{"length": n, "tokens": count} for n, count in sorted(lengths.items())],
            "output_token_lengths": [{"length": n, "tokens": count} for n, count in sorted(output_lengths.items())],
            "all_rule_use_counts": [{"physical_definition_file_line": line, "uses": count} for line, count in sorted(uses.items())],
            "all_unmatched_events": unmatched_events, "all_record_ledger": ledger, "all_type_pairs": types,
            "input_flat_vector_sha256": vector_sha([token for row in input_groups for token in row]),
            "output_flat_vector_sha256": vector_sha([token for row in output_groups for token in row]),
            "input_repeat_counts": original_repeat, "output_repeat_counts": output_repeat,
            "all_flattened_joins_spanning_empty_H": gaps}


def run_audit(reference, root=ROOT):
    plan = load_plan(root)
    catalog = read_json(root / SOURCE)
    definition = verify_definition(reference, catalog)
    check_report(audit(root), root / "research/historical/intake.json")
    check_report(reconstruct(root)[0], root / "research/historical/parsing.json")
    native_catalog = read_json(root / "data/historical/interlinear-16e6.json")
    member = read_pinned_archive((root / native_catalog["path"]).read_bytes(), native_catalog)
    native = [row for row in parse_historical(member)[0] if row.transcriber == "H"]
    return {"audit_version": 1, "scope": plan["scope"], "plan_sha256": sha((root / PLAN).read_bytes()),
            "human_plan_sha256": sha((root / HUMAN_PLAN).read_bytes()), "producer_sha256": sha(Path(__file__).read_bytes()),
            "frozen_dependency_hashes": plan["dependency_hashes"], "source_pr": 181,
            "source_published_head": plan["source_published_head"], "verified_primary_artifacts": catalog["artifacts"],
            "source_credit": native_catalog["credit"], "source_permission": native_catalog["permission"],
            "archive_sha256": native_catalog["archive_sha256"], "member_sha256": native_catalog["member_sha256"],
            "input_alphabet_decoder_condition_verified": True, "unmatched_policy": plan["unmatched_policy"],
            **analyze(native, definition),
            "limits": "Partial definition-based notation with every unmatched symbol retained; one model, not full Bitrans emulation, complete Currier transliteration, physical glyph units, Reddy comparison, historical execution, language or translation"}


def protect_output(path, reference):
    protected = [ROOT / name for name in (*FROZEN, PLAN, HUMAN_PLAN)] + [Path(__file__)]
    protected += [reference / name for name in REFERENCES]
    if any(path.resolve() == p.resolve() or path.exists() and p.exists() and path.samefile(p) for p in protected):
        raise ValueError("primary-table output aliases a frozen source, reference, plan or producer")


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
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"primary-table H audit failed: {error}\n")
    if args.check: print("complete primary-table H report reproduces")


if __name__ == "__main__":
    main()
