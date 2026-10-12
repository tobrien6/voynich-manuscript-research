"""Render the recorded repetition controls; optional Matplotlib dependency."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    raw = args.report.read_bytes()
    report = json.loads(raw)
    digest = hashlib.sha256(raw).hexdigest()
    cases = []
    for source in report["sources"]:
        variants = source["variants"]
        comparable = [{key: value for key, value in variant.items() if key not in {"uncertain_spaces", "alternatives"}} for variant in variants]
        identical_it = source["id"] == "IT2a" and len(variants) == 4 and all(value == comparable[0] for value in comparable)
        for variant in source["variants"]:
            if identical_it and variant is not variants[0]:
                continue
            label = "all four policies identical" if identical_it else f"{variant['uncertain_spaces']} spaces / {variant['alternatives']} alternatives"
            cases.append((source["id"], variant, label))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.hashsalt": digest, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(len(cases), 1, figsize=(10, 1.4 * len(cases) + 2), sharex=True, squeeze=False)
    axes = axes[:, 0]
    marks = []
    for _, variant, _ in cases:
        stats = variant["adjacent_repetition"]
        marks.extend(stats["null_equal_pair_counts"])
        marks.extend([stats["observed_equal_pairs"], stats["exact_conditional_expected_pairs"] - stats["conditional_standard_deviation"],
                      stats["exact_conditional_expected_pairs"] + stats["conditional_standard_deviation"]])
        if len(stats["null_equal_pair_counts"]) != stats["shuffle_repetitions"]:
            raise ValueError("Recorded shuffle count does not match its declared trial count")
    low = math.floor(min(marks)) - 4
    high = math.ceil(max(marks)) + 4
    bins = [number - 0.5 for number in range(low, high + 2)]
    for ax, (source, variant, label) in zip(axes, cases):
        stats = variant["adjacent_repetition"]
        mean = stats["exact_conditional_expected_pairs"]
        sd = stats["conditional_standard_deviation"]
        observed = stats["observed_equal_pairs"]
        ax.axvspan(mean - sd, mean + sd, color="#dbeafe", label="Exact mean ± 1 SD", zorder=0)
        ax.hist(stats["null_equal_pair_counts"], bins=bins, color="#64748b", alpha=0.65, label="Recorded shuffles")
        ax.axvline(mean, color="#2563eb", linestyle="--", linewidth=1.8, label="Exact mean")
        ax.axvline(observed, color="#c2410c", linewidth=2, label="Observed count")
        ax.set_title(f"{source} · {label}     |     observed {observed}, mean {mean:.2f}, SD {sd:.2f}", loc="left", fontsize=10, pad=5)
        ax.set_xlim(low, high)
        ax.grid(axis="y", color="#e2e8f0", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", labelsize=8)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.934), ncol=4, frameon=False, fontsize=9)
    fig.suptitle("Adjacent repetition: observed counts and conditional controls", fontsize=15, fontweight="bold", y=0.988)
    trial_counts = {variant["adjacent_repetition"]["shuffle_repetitions"] for _, variant, _ in cases}
    trial_label = f"{next(iter(trial_counts))} recorded shuffles per policy" if len(trial_counts) == 1 else "recorded shuffles per policy"
    fig.text(0.5, 0.956, f"{report['selection']['count']:,} shared {report['selection']['kind']} loci · {trial_label} · exploratory", ha="center", fontsize=10, color="#475569")
    axes[-1].set_xlabel("Equal adjacent representation pairs")
    fig.supylabel("Shuffle frequency", x=0.035, fontsize=10)
    fig.text(0.09, 0.035, "Variants share source material. The blue band shows one conditional SD; no probability coverage is asserted.", fontsize=9, color="#475569")
    fig.subplots_adjust(top=0.875, bottom=0.1, left=0.09, right=0.98, hspace=0.63)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    png = args.output_dir / "repetition-variance.png"
    svg = args.output_dir / "repetition-variance.svg"
    fig.savefig(png, dpi=160, metadata={"Software": f"Matplotlib {matplotlib.__version__}"})
    fig.savefig(svg, metadata={"Date": None, "Creator": f"Matplotlib {matplotlib.__version__}"})
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    provenance = {
        "report_sha256": digest,
        "plot_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python_version": platform.python_version(),
        "matplotlib_version": matplotlib.__version__,
        "selection_count": report["selection"]["count"],
        "method": report["method"],
        "plotted_variants": [{"source": source, "spaces": v["uncertain_spaces"], "alternatives": v["alternatives"], "label": label} for source, v, label in cases],
        "output_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (png, svg)},
    }
    (args.output_dir / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
