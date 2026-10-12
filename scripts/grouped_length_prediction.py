"""Exploratory, previously exposed length prediction with grouped parameter fits."""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import platform

try:
    from .audit_transliterations import ROOT, load_sources
    from .audit_transcription_images import dependency_components, page_reference
    from . import interior_length_order as parent
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from audit_transcription_images import dependency_components, page_reference
    import interior_length_order as parent


METHOD = "grouped-length-prediction-v1"
FOLDS = 5
SEED = 20261012
CLASSES = 10
STRENGTH = 10
PINS = {
    "research/transliteration/interior_length_order.json": "d3ada06de64c80f315ea6fa38f71f25158857cdf0d2a34728d1c6fc6ad7b6a6c",
    "research/folio-alignment/transcription-image-coverage.json": "05ff84a7f0d94881ea411851be31d05fec502f0b30e116f809f5c19d0f061b46",
    "research/image-index/canvases.csv": "a0b03f8f012331e61a1e89b65f6462be0f1d28f896a068a8cc2cd0f63a255b0f",
}
PLAN = ROOT / "research/baselines/GROUPED_LENGTH_PLAN.md"


def length_class(length):
    if type(length) is not int or length < 1:
        raise ValueError("notation lengths must be positive integers")
    return min(length, CLASSES)


def transitions(row):
    lengths = row["lengths"]
    if len(lengths) < 3 or not isinstance(row["label"], str) or not row["label"]:
        raise ValueError("three interior lengths and an explicit source label required")
    values = [length_class(x) for x in lengths]
    boundary = (len(values) + 1) // 2
    return [((row["label"], int(j >= boundary)), values[j - 1], values[j])
            for j in range(1, len(values))]


def fold_for(group_id):
    if not isinstance(group_id, str) or not group_id:
        raise ValueError("dependency group required")
    digest = hashlib.sha256(parent.compact([METHOD, SEED, group_id])).digest()
    return int.from_bytes(digest, "big") % FOLDS


def group_index(image_report, canvas_rows):
    components = dependency_components(canvas_rows)
    if components != image_report["dependency_components"]:
        raise ValueError("image dependency components do not reproduce from the full index")
    by_leaf = {leaf: group["group_id"] for group in components for leaf in group["folio_ids"]}
    by_page = {}
    for page in image_report["pages"]:
        name = page["page_id"]
        if name in by_page:
            raise ValueError("duplicate image-reference page")
        reference = page_reference(name)
        groups = {by_leaf.get(side[:-1]) for side in reference["folio_sides"]}
        if (page["side_reference_status"] != "side_references_matched"
                or not groups or None in groups or len(groups) != 1
                or page["dependency_group"] != next(iter(groups))):
            # Unsupported/unmatched pages remain explicit; selected ones fail
            # below rather than being silently dropped from the cohort.
            by_page[name] = None
        else:
            by_page[name] = page["dependency_group"]
    return components, by_page


def declare_folds(rows, image_report, canvas_rows):
    components, by_page = group_index(image_report, canvas_rows)
    by_group = defaultdict(list)
    seen = set()
    for row in rows:
        if row["key"] in seen:
            raise ValueError("duplicate selected locus")
        seen.add(row["key"])
        group = by_page.get(row["page"])
        if group is None:
            raise ValueError(f"selected page has no supported dependency reference: {row['page']}")
        by_group[group].append(row)
    members = {component["group_id"]: component["folio_ids"] for component in components}
    manifest = []
    assignments = {}
    for group, selected in sorted(by_group.items()):
        fold = fold_for(group)
        assignments[group] = fold
        canvases = sorted({uri for leaf in members[group]
                           for uri in image_report["indexed_canvas_ids_by_leaf"][leaf]})
        manifest.append({"group_id": group, "fold": fold, "folio_ids": members[group],
                         "source_page_ids": sorted({row["page"] for row in selected}),
                         "locus_keys": sorted(row["key"] for row in selected), "canvas_ids": canvases})
    if set(assignments.values()) != set(range(FOLDS)):
        raise ValueError("a declared fold is empty; do not choose a replacement seed")
    return assignments, manifest, by_page


def fit(rows):
    targets = defaultdict(Counter)
    pairs = defaultdict(Counter)
    for row in rows:
        for context, previous, target in transitions(row):
            targets[context][target] += 1
            pairs[(context, previous)][target] += 1
    return {"targets": dict(targets), "pairs": dict(pairs)}


def probabilities(model, context, previous, target):
    if any(type(value) is not int or not 1 <= value <= CLASSES for value in (previous, target)):
        raise ValueError("use the fixed length classes 1 through 10")
    targets = model["targets"].get(context, {})
    pairs = model["pairs"].get((context, previous), {})
    baseline = (targets.get(target, 0) + 1) / (sum(targets.values()) + CLASSES)
    transition = (pairs.get(target, 0) + STRENGTH * baseline) / (sum(pairs.values()) + STRENGTH)
    return baseline, transition


def model_record(model):
    contexts = sorted(model["targets"])
    return [{"source_label": c[0], "target_half": c[1],
             "target_counts": [model["targets"][c].get(y, 0) for y in range(1, CLASSES + 1)],
             "previous_target_counts": [[model["pairs"].get((c, x), {}).get(y, 0)
                                         for y in range(1, CLASSES + 1)] for x in range(1, CLASSES + 1)]}
            for c in contexts]


def score_row(row, model, fold):
    baseline_losses, transition_losses, missing_previous = [], [], 0
    for context, previous, target in transitions(row):
        q0, q1 = probabilities(model, context, previous, target)
        baseline_losses.append(-math.log2(q0))
        transition_losses.append(-math.log2(q1))
        missing_previous += (context, previous) not in model["pairs"]
    q0_loss, q1_loss = math.fsum(baseline_losses), math.fsum(transition_losses)
    count = len(baseline_losses)
    return {"locus_key": row["key"], "page_id": row["page"], "group_id": row["group"],
            "source_label": row["label"], "fold": fold, "transitions": count,
            "baseline_loss_bits": q0_loss, "transition_loss_bits": q1_loss,
            "gain_bits": q0_loss - q1_loss, "gain_bits_per_transition": (q0_loss - q1_loss) / count,
            "unseen_previous_context_transitions": missing_previous}


def aggregate(scores):
    if not scores:
        raise ValueError("nonempty scored rows required")
    count = sum(row["transitions"] for row in scores)
    baseline = math.fsum(row["baseline_loss_bits"] for row in scores)
    transition = math.fsum(row["transition_loss_bits"] for row in scores)
    return {"loci": len(scores), "transitions": count, "baseline_loss_bits": baseline,
            "transition_loss_bits": transition, "gain_bits": baseline - transition,
            "micro_gain_bits_per_transition": (baseline - transition) / count,
            "locus_macro_gain_bits_per_transition": math.fsum(
                row["gain_bits_per_transition"] for row in scores) / len(scores),
            "unseen_previous_context_transitions": sum(row["unseen_previous_context_transitions"] for row in scores)}


def evaluate(rows, assignments):
    keys = [row["key"] for row in rows]
    if len(keys) != len(set(keys)) or not rows:
        raise ValueError("unique nonempty selected loci required")
    groups = {row["group"] for row in rows}
    if (set(assignments) != groups or set(assignments.values()) != set(range(FOLDS))
            or any(type(fold) is not int for fold in assignments.values())):
        raise ValueError("fold assignments must cover every group and all five folds")
    fold_results, scored = [], []
    for fold in range(FOLDS):
        train = [row for row in rows if assignments[row["group"]] != fold]
        test = [row for row in rows if assignments[row["group"]] == fold]
        training_groups = {row["group"] for row in train}
        scoring_groups = {row["group"] for row in test}
        if not train or not test or training_groups & scoring_groups:
            raise ValueError("empty fold or dependency leakage")
        model = fit(train)
        counts = model_record(model)
        scores = [score_row(row, model, fold) for row in test]
        scored.extend(scores)
        fold_results.append({"fold": fold, "training_loci": len(train),
                             "training_transitions": sum(len(transitions(row)) for row in train),
                             "training_group_ids": sorted(training_groups),
                             "scoring_group_ids": sorted(scoring_groups),
                             "fitted_counts_sha256": hashlib.sha256(parent.compact(counts)).hexdigest(),
                             "fitted_counts": counts, **aggregate(scores)})
    if Counter(row["locus_key"] for row in scored) != Counter(keys):
        raise ValueError("not every locus was scored exactly once")
    by_group = defaultdict(list)
    for row in scored:
        by_group[row["group_id"]].append(row)
    group_results = [{"group_id": group, "fold": assignments[group], **aggregate(scores)}
                     for group, scores in sorted(by_group.items())]
    summary = aggregate(scored)
    summary["group_macro_gain_bits_per_transition"] = math.fsum(
        row["micro_gain_bits_per_transition"] for row in group_results) / len(group_results)
    summary["groups"] = len(group_results)
    summary["positive_fold_count"] = sum(row["micro_gain_bits_per_transition"] > 0 for row in fold_results)
    summary["positive_group_count"] = sum(row["micro_gain_bits_per_transition"] > 0 for row in group_results)
    summary["fixed_diagnostic_preference"] = (summary["micro_gain_bits_per_transition"] > 0
        and summary["group_macro_gain_bits_per_transition"] > 0 and summary["positive_fold_count"] >= 4)
    return {"summary": summary, "folds": fold_results, "groups": group_results,
            "loci": sorted(scored, key=lambda row: row["locus_key"])}


def inputs():
    raw = {}
    for path, digest in PINS.items():
        raw[path] = (ROOT / path).read_bytes()
        if hashlib.sha256(raw[path]).hexdigest() != digest:
            raise ValueError(f"pinned input changed: {path}")
    old = json.loads(raw["research/transliteration/interior_length_order.json"])
    image = json.loads(raw["research/folio-alignment/transcription-image-coverage.json"])
    canvas_rows = list(csv.DictReader(io.StringIO(raw["research/image-index/canvases.csv"].decode())))
    sources = load_sources()
    treatments, accepted, selection = parent.prepare(sources)
    if selection != old["selection"]:
        raise ValueError("parent cohort or exclusions changed")
    old_by_variant = {(t["source_id"], t["spacing"]): t for t in old["treatments"]}
    provenance = {source["id"]: source for source, _ in sources}
    prepared = []
    for (sid, spacing), mapping in treatments.items():
        vectors = [(mapping[k]["page_id"], k, parent.interior_lengths(mapping[k]["tokens"])) for k in accepted]
        old_variant = old_by_variant[sid, spacing]
        if (old_variant["source_sha256"] != provenance[sid]["sha256"]
                or old_variant["length_corpus_sha256"] != hashlib.sha256(parent.compact(vectors)).hexdigest()
                or old_variant["loci"] != len(vectors)
                or abs(old_variant["mean_centered_association"] - parent.mean_score(vectors)) > 1e-12):
            raise ValueError("parent numerical inputs or observation changed")
        rows = [{"page": page, "key": key, "lengths": lengths,
                 "label": mapping[key]["variables"].get("L", "unset")} for page, key, lengths in vectors]
        prepared.append((sid, spacing, rows, old_variant["length_corpus_sha256"]))
    assignments, manifest, by_page = declare_folds(prepared[0][2], image, canvas_rows)
    for _, _, rows, _ in prepared:
        for row in rows:
            row["group"] = by_page[row["page"]]
    return prepared, assignments, manifest, provenance, selection


def report():
    prepared, assignments, manifest, provenance, selection = inputs()
    results = []
    for sid, spacing, rows, digest in prepared:
        results.append({"source_id": sid, "spacing": spacing, "source_sha256": provenance[sid]["sha256"],
                        "source_url": provenance[sid]["url"], "length_corpus_sha256": digest,
                        **evaluate(rows, assignments)})
    return {"schema_version": 1, "method": METHOD,
            "analysis_status": "exploratory; known whole-corpus exposure; per-fold parameter-fit exclusion only",
            "python_version": platform.python_version(), "plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
            "input_pins": PINS, "primary_treatment": "ZL3b/split",
            "models": {"classes": list(range(1, 10)) + ["10+"], "baseline_pseudocount": 1,
                       "transition_prior_strength": STRENGTH, "context": "source Currier label and target early/late half"},
            "selection": {"loci": len(selection["retained_locus_keys"]),
                          "cohort_sha256": selection["retained_locus_keys_sha256"]},
            "folds": {"count": FOLDS, "seed": SEED, "group_assignments": manifest,
                      "manifest_sha256": hashlib.sha256(parent.compact(manifest)).hexdigest()},
            "all_treatments_meet_fixed_preference": all(t["summary"]["fixed_diagnostic_preference"] for t in results),
            "treatments": results}


def protect_output(destination, protected):
    """Reject resolved paths and existing inode aliases of protected inputs."""
    output = destination.resolve()
    if output in protected or (output.exists() and any(
            output.samefile(source) for source in protected if source.exists())):
        raise ValueError("output must not overwrite a pinned input or plan")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        protected = {(ROOT / path).resolve() for path in PINS} | {PLAN.resolve(), (ROOT / "data/transliterations.json").resolve()}
        protected.update((ROOT / source["path"]).resolve() for source in json.loads(
            (ROOT / "data/transliterations.json").read_text())["sources"])
        if args.output:
            protect_output(args.output, protected)
        result = report()
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("committed grouped-prediction report differs from replay")
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            protect_output(args.output, protected)
            args.output.write_text(rendered)
        elif not args.check:
            print(rendered, end="")
    except (ValueError, OSError) as error:
        parser.exit(1, f"grouped prediction failed: {error}\n")
    if args.check:
        print("Pinned inputs, grouped fits and complete prediction report verified.")


if __name__ == "__main__":
    main()
