"""Render all four accepted H comparisons with A/B units and nulls explicit."""

from fractions import Fraction
import argparse
import hashlib
import io
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_PATH = "research/historical/repeated-types.json"
CONDITIONAL_PATH = "research/historical/record-conditioned.json"
REPORT_PINS = {GLOBAL_PATH: "683a0906eaf01dbacf5394eb0ded820802df0f09c293302a452351494338dc2a",
               CONDITIONAL_PATH: "56fc5f036627cffbf3f597090fbafd22afe102c2430f6f606c4f1d46c5b17b1b"}
FIGURES = ROOT / "research/historical/figures"
STEM = "repeat-null-conditioning"
IDENTITIES = [(ring, column) for ring in ("exclude_R2", "exclude_single_character_tokens") for column in ("M", "L")]
LABELS = ("Omit R2\nM removed", "Omit R2\nL removed", "Drop ring 1-char\nM removed", "Drop ring 1-char\nL removed")
EXTRA_INPUTS = ("research/historical/REPEATED_TYPES_PLAN.md", "research/historical/RECORD_CONDITIONED_PLAN.md",
                "research/historical/repeated-types-plan.json", "research/historical/record-conditioned-plan.json",
                "research/historical/record-conditioned-amendment-1.json", "research/historical/RECORD_CONDITIONED_AMENDMENT_1.md",
                "scripts/global_repeated_types.py", "scripts/historical_repeated_types.py",
                "scripts/record_conditioned_repeated_types.py", "scripts/historical_record_conditioned.py",
                "requirements-figures.txt")


def strict(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))


def exact(value):
    numerator, denominator = int(value["numerator_hex"], 16), int(value["denominator_hex"], 16)
    if denominator <= 0 or type(value["decimal"]) not in (int, float) or not math.isfinite(value["decimal"]):
        raise ValueError("invalid exact-mean display record")
    result = Fraction(numerator, denominator)
    if float(result) != value["decimal"]:
        raise ValueError("decimal display differs from exact source rational")
    return result


def figure_data(global_report, conditional_report):
    if (type(global_report.get("assay_version")) is not int or global_report["assay_version"] != 1
            or type(conditional_report.get("assay_version")) is not int or conditional_report["assay_version"] != 1
            or global_report["edge_scope"] != conditional_report["edge_scope"]
            or global_report["edge_scope"] != "All N-1 adjacent edges in each surviving flat stream, including native-record joins"
            or global_report["frame"] != "historical-whole-text-v1"
            or conditional_report["frame"] != "historical-native-record-v1"
            or conditional_report["condition_on"] != "Independent uniform permutation of every surviving native-record token bag"
            or strict(global_report["source_credit"]) != strict(conditional_report["source_credit"])
            or strict(global_report["source_permission"]) != strict(conditional_report["source_permission"])):
        raise ValueError("figure requires the accepted matched whole-edge studies")
    if len(global_report["variants"]) != 4 or len(conditional_report["variants"]) != 4:
        raise ValueError("retain all four accepted H variants")
    points = []
    for identity, g, c in zip(IDENTITIES, global_report["variants"], conditional_report["variants"], strict=True):
        if identity != (g["ring_policy"], g["f66r_column_unit"]) or identity != (c["ring_policy"], c["f66r_column_unit"]):
            raise ValueError("duplicate, reordered or unexpected figure variant")
        for key in ("flat_corpus_sha256", "record_corpus_sha256", "tokens", "distinct_types", "observed", "observed_boundary_diagnostics"):
            if strict(g[key]) != strict(c[key]):
                raise ValueError("plotted global/conditional input or measured edges differ")
        if type(g["tokens"]) is not int or g["tokens"] < 2 or type(g["distinct_types"]) is not int:
            raise ValueError("invalid plotted population counts")
        observed = {name: g["observed"][field] for name, field in
                    (("A", "equal_pair_events_A"), ("B", "distinct_repeating_types_B"))}
        if any(type(v) is not int or v < 0 for v in observed.values()):
            raise ValueError("A/B observations require nonnegative integer counts")
        global_means = {name: exact(g["exact_global_null_means"][name]) for name in ("A", "B")}
        conditional_means = {name: exact(c["exact_conditional_null_means"][name]) for name in ("A", "B")}
        if any(v <= 0 for v in (*global_means.values(), *conditional_means.values())):
            raise ValueError("this figure requires positive denominators in every accepted treatment")
        if any(exact(c["exact_global_null_means"][name]) != global_means[name] for name in ("A", "B")):
            raise ValueError("conditional report's retained global means differ")
        ratios = {"global": {name: float(Fraction(observed[name]) / global_means[name]) for name in ("A", "B")},
                  "native_record": {name: float(Fraction(observed[name]) / conditional_means[name]) for name in ("A", "B")}}
        if (ratios["global"] != g["observed_over_exact_mean"]
                or ratios["native_record"] != c["observed_over_exact_conditional_mean"]):
            raise ValueError("source ratios do not match the declared A/B units")
        d = g["observed_boundary_diagnostics"]
        if (d["all_adjacent_edges"] != g["tokens"] - 1
                or d["within_record_pair_events"] + d["cross_record_pair_events"] != observed["A"]
                or d["within_record_repeating_types"] + d["cross_record_repeating_types"] - d["types_repeating_in_both_scopes"] != observed["B"]):
            raise ValueError("observed edge/type accounting differs")
        internal = exact(c["exact_A_scope_contributions"]["within_record"])
        joining = exact(c["exact_A_scope_contributions"]["cross_record"])
        residuals = {"within_record": Fraction(d["within_record_pair_events"]) - internal,
                     "cross_record": Fraction(d["cross_record_pair_events"]) - joining,
                     "total": Fraction(observed["A"]) - conditional_means["A"]}
        if (internal + joining != conditional_means["A"]
                or residuals["within_record"] + residuals["cross_record"] != residuals["total"]
                or residuals["total"] != exact(c["observed_minus_conditional_mean"]["A"])):
            raise ValueError("A scope contributions or residuals do not reconcile exactly")
        points.append({"ring_policy": identity[0], "f66r_column_unit_removed": identity[1],
                       "tokens": g["tokens"], "distinct_types": g["distinct_types"],
                       "flat_corpus_sha256": g["flat_corpus_sha256"], "record_corpus_sha256": g["record_corpus_sha256"],
                       "all_adjacent_edges": d["all_adjacent_edges"], "cross_record_joining_edges": d["cross_record_joining_edges"],
                       "observed": observed, "global_exact_mean_decimal": {k: float(v) for k, v in global_means.items()},
                       "native_record_exact_mean_decimal": {k: float(v) for k, v in conditional_means.items()},
                       "observed_over_exact_mean": ratios, "A_conditional_scope_residuals": {k: float(v) for k, v in residuals.items()}})
    return {"figure_version": "historical-repeat-null-conditioning-v1", "input_report_sha256": REPORT_PINS,
            "edge_scope": global_report["edge_scope"], "source_credit": global_report["source_credit"],
            "source_permission": global_report["source_permission"], "points": points,
            "limits": "Display of four exposed approximate H studies; matched input/edges, changed null conditioning; no uncertainty intervals, causal allocation, calibrated tail, language or decipherment"}


def load_reports(global_path, conditional_path):
    reports = []
    for name, path in ((GLOBAL_PATH, global_path), (CONDITIONAL_PATH, conditional_path)):
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != REPORT_PINS[name]:
            raise ValueError("accepted report bytes changed; review/version the figure")
        reports.append(json.loads(raw))
    return reports


def protect_targets(output_dir, global_path, conditional_path, reports):
    targets = [output_dir / (STEM + suffix) for suffix in (".png", ".svg", ".json")]
    sources = [global_path, conditional_path, Path(__file__), *(ROOT / name for name in EXTRA_INPUTS)]
    sources.extend(ROOT / name for report in reports for name in report["frozen_dependency_hashes"])
    for i, target in enumerate(targets):
        if any(target.resolve() == source.resolve() or target.exists() and source.exists() and target.samefile(source) for source in sources):
            raise ValueError("figure output aliases a report, frozen dependency, plan or producer")
        if any(target.resolve() == other.resolve() or target.exists() and other.exists() and target.samefile(other) for other in targets[:i]):
            raise ValueError("figure artifact targets alias each other")
    return targets


def write_artifacts(payloads, output_dir, global_path, conditional_path, reports):
    targets = protect_targets(output_dir, global_path, conditional_path, reports)
    output_dir.mkdir(parents=True, exist_ok=True)
    for path, payload in zip(targets, payloads, strict=True):
        protect_targets(output_dir, global_path, conditional_path, reports)
        path.write_bytes(payload)


def draw(data, output_dir, global_path, conditional_path, reports):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    protect_targets(output_dir, global_path, conditional_path, reports)
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 10, "svg.hashsalt": "voynich-historical-repeat-nulls-v1"}):
        figure = plt.figure(figsize=(12.5, 9.6))
        grid = figure.add_gridspec(2, 2, height_ratios=[1, .72])
        top = [figure.add_subplot(grid[0, column]) for column in (0, 1)]
        lower = figure.add_subplot(grid[1, :])
        styles = {"global": ("#136b89", "o", -.12), "native_record": ("#bd660f", "s", .12)}
        for axis, metric, title in zip(top, ("A", "B"), ("A · Equal adjacent-pair events", "B · Distinct self-repeating types"), strict=True):
            axis.axhline(1, color="#677481", linestyle="--", linewidth=1)
            for i, point in enumerate(data["points"]):
                values = [point["observed_over_exact_mean"][null][metric] for null in styles]
                axis.plot([i-.12, i+.12], values, color="#aeb7bf", linewidth=1.4, zorder=1)
                for null, value in zip(styles, values, strict=True):
                    color, marker, offset = styles[null]
                    axis.plot(i+offset, value, marker=marker, linestyle="none", color=color, markersize=8, zorder=2)
                    axis.annotate(f"{value:.3f}", (i+offset, value), xytext=(0, 10 if null=="global" else -18),
                                  textcoords="offset points", ha="center", fontsize=9, color=color)
            axis.set_title(title, loc="left", fontsize=12, fontweight="bold", pad=12)
            axis.set_ylim(.6, 3.0)
            axis.set_xlim(-.45, 3.45)
            axis.set_xticks(range(4), LABELS)
            axis.set_ylabel("Observed count / exact null mean")
        colors = {"within_record": "#498774", "cross_record": "#9869a1", "total": "#29333d"}
        offsets = {"within_record": -.22, "cross_record": 0, "total": .22}
        for i, point in enumerate(data["points"]):
            for scope in colors:
                value = point["A_conditional_scope_residuals"][scope]
                lower.bar(i+offsets[scope], value, width=.19, color=colors[scope], zorder=2)
                lower.annotate(f"{value:+.2f}", (i+offsets[scope], value), xytext=(0, 5 if value>0 else -13),
                               textcoords="offset points", ha="center", fontsize=9, color=colors[scope])
        lower.axhline(0, color="#677481", linewidth=1)
        lower.set_ylim(-35, 30)
        lower.set_xlim(-.45, 3.45)
        lower.set_xticks(range(4), LABELS)
        lower.set_ylabel("Observed − conditional mean\n(pair-event count A)")
        lower.set_title("A's within-record and joining residuals have opposite signs", loc="left", fontsize=12, fontweight="bold", pad=12)
        for axis in [*top, lower]:
            axis.grid(axis="y", color="#e5e7eb", linewidth=.7, zorder=0)
            for spine in ("top", "right"):
                axis.spines[spine].set_visible(False)
            for spine in ("left", "bottom"):
                axis.spines[spine].set_color("#b9c1c9")
        figure.suptitle("The repeat contrast depends on the null's conditioning", x=.065, y=.985, ha="left", fontsize=17, fontweight="bold")
        figure.text(.065, .945, "Same approximate H tokens and all N−1 flat-stream edges within each variant · four related inputs", fontsize=10.5, color="#4b5563")
        null_handles = [Line2D([], [], color=color, marker=marker, linestyle="none", markersize=7,
                              label="Global text bag" if null=="global" else "Independent native-record bags")
                        for null, (color, marker, _) in styles.items()]
        figure.legend(handles=null_handles, loc="upper left", bbox_to_anchor=(.057, .928), ncol=2, frameon=False)
        scope_handles = [Line2D([], [], color=color, linewidth=7, label={"within_record": "Within records", "cross_record": "Joining edges", "total": "Complete edge path"}[scope])
                         for scope, color in colors.items()]
        figure.legend(handles=scope_handles, loc="upper left", bbox_to_anchor=(.057, .137),
                      frameon=False, ncol=3, fontsize=9)
        figure.text(.065, .092,
                    "Labels show ring treatment / removed f66r unit. Top gray connectors pair two exact-mean normalizations; they are not intervals.\n"
                    "The dashed reference is observed = mean. Lower A residuals add exactly; B types are deduplicated and cannot be added by scope.\n"
                    "No null variance or calibrated tail is plotted. Native records are not verified physical lines; variants are not independent replications.\n"
                    "This matched comparison shows sensitivity to conditioning, without a causal allocation, language claim or decipherment.",
                    fontsize=9, color="#4b5563", linespacing=1.5, va="top")
        figure.subplots_adjust(left=.075, right=.985, top=.84, bottom=.18, hspace=.48, wspace=.22)
        png, svg = io.BytesIO(), io.BytesIO()
        figure.savefig(png, format="png", dpi=180, facecolor="white", metadata={"Software": "Voynich Manuscript Research"})
        figure.savefig(svg, format="svg", facecolor="white", metadata={"Date": None, "Creator": "Voynich Manuscript Research"})
        svg_bytes = ("\n".join(line.rstrip() for line in svg.getvalue().decode().splitlines())+"\n").encode()
        plt.close(figure)
    data["renderer"] = {"matplotlib": matplotlib.__version__, "font": "DejaVu Sans", "dpi": 180,
                        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    write_artifacts([png.getvalue(), svg_bytes, (json.dumps(data, indent=2, allow_nan=False)+"\n").encode()],
                    output_dir, global_path, conditional_path, reports)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--global-input", type=Path, default=ROOT / GLOBAL_PATH)
    parser.add_argument("--conditional-input", type=Path, default=ROOT / CONDITIONAL_PATH)
    parser.add_argument("--output-dir", type=Path, default=FIGURES)
    args = parser.parse_args()
    try:
        reports = load_reports(args.global_input, args.conditional_input)
        data = figure_data(*reports)
        draw(data, args.output_dir, args.global_input, args.conditional_input, reports)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"historical repeat figure failed: {error}\n")
    print("Rendered all four matched A/B comparisons and A scope residuals.")


if __name__ == "__main__":
    main()
