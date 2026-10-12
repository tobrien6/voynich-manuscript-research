"""Replay frozen controls after a parent CLI-only repair without repinning results."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import platform
import sys


ROOT = Path(__file__).resolve().parents[1]
FROZEN = "8e5851e3abd2c21d18766a1b884c0a321cd6048f"
ENGINE = "scripts/grouped_length_prediction.py"
PROGRAM = "scripts/grouped_predictor_controls.py"
RESULT = "research/baselines/grouped-predictor-controls.json"
RESULT_SHA256 = "c89b5fbc1bbe06d005eca566c2ea44d4751943f34eb5648e5c0198f3c0e5d1bc"
GUARD_AST_SHA256 = "7f75d126ee0229fbcdb9418339a2169ef53da39126738d7f4dc69d0bde377822"
SNAPSHOTS = {
    ENGINE: "research/baselines/frozen/grouped-length-prediction-v1.source.txt",
    PROGRAM: "research/baselines/frozen/grouped-predictor-controls-v1.source.txt",
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def scientific_ast(raw):
    """Compare scientific code outside the CLI body and one audited helper.

    Keep its name, arguments, decorators and all other module statements.
    Moving code outside main, changing a constant, import or scoring function,
    or adding another main fails equivalence. Only the reviewed protect_output
    definition with its exact syntax hash may be added outside main. Neither
    the CLI main nor that helper is called by this verifier.
    """
    tree = ast.parse(raw)
    mains = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    if len(mains) != 1:
        raise ValueError("exactly one top-level CLI main required")
    mains[0].body = [ast.Pass()]
    helpers = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "protect_output"]
    if len(helpers) > 1:
        raise ValueError("duplicate output helper")
    if helpers:
        encoded = ast.dump(helpers[0], include_attributes=False).encode()
        if sha(encoded) != GUARD_AST_SHA256:
            raise ValueError("output helper differs from the explicitly reviewed syntax")
        tree.body.remove(helpers[0])
    return ast.dump(tree, include_attributes=False)


def frozen_file(path, root=ROOT):
    if path not in SNAPSHOTS:
        raise ValueError("unsupported frozen source artifact")
    try:
        return (root / SNAPSHOTS[path]).read_bytes()
    except OSError as error:
        raise ValueError("frozen source snapshot is unavailable; do not substitute a new producer") from error


def verified_inputs(root=ROOT):
    raw = (root / RESULT).read_bytes()
    if sha(raw) != RESULT_SHA256:
        raise ValueError("frozen synthetic result bytes changed")
    stored = json.loads(raw)
    if platform.python_version() != stored["python_version"]:
        raise ValueError("use the recorded Python environment for exact replay")
    original = frozen_file(ENGINE, root)
    current = (root / ENGINE).read_bytes()
    if sha(original) != stored["input_pins"][ENGINE]:
        raise ValueError("pre-benchmark producer does not match the frozen result")
    if scientific_ast(original) != scientific_ast(current):
        raise ValueError("producer scientific AST changed; reviewed CLI-guard compatibility does not apply")
    program = (root / PROGRAM).read_bytes()
    if sha(program) != stored["implementation_sha256"] or program != frozen_file(PROGRAM, root):
        raise ValueError("frozen benchmark program changed")
    plan = root / "research/baselines/GROUPED_CONTROL_PLAN.md"
    if sha(plan.read_bytes()) != stored["plan_sha256"]:
        raise ValueError("frozen benchmark plan changed")
    hashes = {}
    for name, expected in stored["input_pins"].items():
        hashes[name] = sha((root / name).read_bytes())
        if name != ENGINE and hashes[name] != expected:
            raise ValueError(f"non-CLI pinned input changed: {name}")
    return stored, hashes


def verify(progress=None):
    stored, hashes = verified_inputs()
    # Verify source equivalence and exact hashes before importing the producer.
    try:
        from . import grouped_predictor_controls as benchmark
    except ImportError:
        import grouped_predictor_controls as benchmark
    templates, assignments = benchmark.layout_from_report(json.loads((ROOT / benchmark.PARENT).read_bytes()))
    expected_layout = {"source_treatment": "ZL3b/split", "templates": templates,
                       "group_assignments": assignments, "sha256": benchmark.digest([templates, assignments])}
    if stored["layout"] != expected_layout or stored["seed"] != benchmark.SEED:
        raise ValueError("frozen layout or seed differs")
    regenerated = []
    for case, quarters in benchmark.CASES.items():
        records = []
        for replicate in range(benchmark.REPLICATES):
            rows = benchmark.simulate(templates, replicate, case)
            scores = benchmark.estimator.evaluate(rows, assignments)
            records.append({"replicate": replicate, "sequence_sha256": benchmark.digest(rows),
                            "oracle": benchmark.oracle_score(rows, quarters),
                            **benchmark.compact_evaluation(scores)})
        regenerated.append({"case": case, "persistence_quarters": quarters,
                            "ideal_stationary_gain_bits_per_transition": benchmark.ideal_gain(quarters),
                            "summary": benchmark.summarize_replicates(records), "replicates": records})
        if progress:
            progress(f"Verified {case}: all {benchmark.REPLICATES} frozen datasets")
    if (stored["replicates_per_case"] != benchmark.REPLICATES or stored["total_datasets"] != 192
            or regenerated != stored["cases"]):
        raise ValueError("frozen dataset fields differ from current producer replay")
    helper_present = any(isinstance(node, ast.FunctionDef) and node.name == "protect_output"
                         for node in ast.parse((ROOT / ENGINE).read_bytes()).body)
    return {"schema_version": 2, "method": "frozen-grouped-controls-reviewed-cli-guard-compatibility-v2",
            "freeze_commit": FROZEN, "frozen_result_sha256": RESULT_SHA256,
            "frozen_source_snapshots": {name: {"path": path, "sha256": sha(frozen_file(name))}
                                        for name, path in SNAPSHOTS.items()},
            "frozen_producer_sha256": stored["input_pins"][ENGINE],
            "current_producer_sha256": hashes[ENGINE],
            "producer_bytes_changed": hashes[ENGINE] != stored["input_pins"][ENGINE],
            "scientific_ast_identical_outside_reviewed_cli_guard": True,
            "excluded_cli_main_body": True,
            "reviewed_output_helper_ast_sha256": GUARD_AST_SHA256 if helper_present else None,
            "benchmark_program_sha256": stored["implementation_sha256"],
            "benchmark_plan_sha256": stored["plan_sha256"], "current_input_sha256": hashes,
            "python_version": platform.python_version(), "datasets_replayed": 192,
            "all_stored_dataset_fields_reproduced": True, "frozen_result_records_changed": False,
            "verifier_sha256": sha(Path(__file__).read_bytes()),
            "limits": "Verifies unchanged scientific code and exact synthetic records; does not execute or validate the revised parent CLI, and does not establish a manuscript mechanism."}


def protect_output(path, root=ROOT):
    resolved = path.resolve()
    data = json.loads((root / RESULT).read_bytes())
    protected = {root / name for name in data["input_pins"]}
    protected.update(root / name for name in SNAPSHOTS.values())
    protected.update(root / name for name in (PROGRAM, RESULT, "research/baselines/GROUPED_CONTROL_PLAN.md"))
    catalog = root / "data/transliterations.json"
    if catalog.exists():
        protected.add(catalog)
        protected.update(root / source["path"] for source in json.loads(catalog.read_bytes())["sources"])
    protected.add(Path(__file__).resolve())
    if (resolved.is_relative_to((root / "data").resolve())
            or resolved.is_relative_to((root / "scripts").resolve())
            or any(resolved == source.resolve() or
                   (path.exists() and source.exists() and path.samefile(source)) for source in protected)):
        raise ValueError("verification output must not overwrite inputs, scripts or frozen results")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output, root=ROOT)
        receipt = verify(lambda message: print(message, file=sys.stderr))
        if args.check and receipt != json.loads(args.check.read_bytes()):
            raise ValueError("compatibility receipt differs from current exact replay")
        if args.output:
            protect_output(args.output, root=ROOT)
            args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError, KeyError, TypeError, SyntaxError) as error:
        parser.exit(1, f"frozen grouped-controls verification failed: {error}\n")
    print("All 192 frozen datasets reproduce; scientific AST matches the pre-benchmark producer.")


if __name__ == "__main__":
    main()
