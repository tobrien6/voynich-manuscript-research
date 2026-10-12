"""Render exact annotation counts from the verified comparator profile."""

import argparse
import hashlib
import json
from pathlib import Path
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    from .audit_transcription_comparators import ROOT, audit
except ImportError:
    from audit_transcription_comparators import ROOT, audit


EXPORTS = ("ZL3b", "IT2a", "GC2a", "RF1b-full", "RF1b-basic")
LABELS = ("ZL 3b", "IT 2a", "GC 2a", "RF 1b / full", "RF 1b / basic")
COLUMNS = (
    ("uncertain_space_comma", "Uncertain\ncommas"),
    ("alternative_group", "Alternative\ngroups"),
    ("paragraph_start", "Paragraph\nstarts"),
    ("ligature_group", "Ligature\ngroups"),
    ("high_ascii_escape", "Extended\nescapes"),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path,
                        default=ROOT / "research/transliteration/comparator_profiles.json")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "research/transliteration/figures")
    args = parser.parse_args()
    profile_bytes = args.profile.read_bytes()
    report = json.loads(profile_bytes)
    if report != audit():
        raise ValueError("Figure input differs from the verified source-byte audit")
    profiles = report["profiles"]
    counts = np.array([[profiles[export]["annotation_occurrences_in_present_records"][key]
                        for key, _ in COLUMNS] for export in EXPORTS], dtype=int)
    if np.any(counts < 0):
        raise ValueError("Annotation counts must be nonnegative")
    values = np.log10(counts + 1)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "svg.fonttype": "path", "svg.hashsalt": "voynich-annotation-figure-v1"})
    fig, ax = plt.subplots(figsize=(11.8, 7.1), facecolor="white")
    fig.subplots_adjust(left=0.23, right=0.92, top=0.73, bottom=0.22)
    image = ax.imshow(values, cmap="Blues", vmin=0, vmax=values.max(), aspect="auto")
    ax.set_xticks(range(len(COLUMNS)), [label for _, label in COLUMNS])
    ax.xaxis.tick_top()
    ax.tick_params(axis="both", length=0, pad=12)
    row_labels = [f"{label}\n{profiles[export]['present_locus_record_count']:,} present loci"
                  for export, label in zip(EXPORTS, LABELS)]
    ax.set_yticks(range(len(EXPORTS)), row_labels)
    ax.set_xticks(np.arange(-0.5, len(COLUMNS), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(EXPORTS), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=3)
    ax.tick_params(which="minor", bottom=False, top=False, left=False, right=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for row in range(len(EXPORTS)):
        for col in range(len(COLUMNS)):
            rgba = image.cmap(image.norm(values[row, col]))
            luminance = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
            ax.text(col, row, f"{counts[row, col]:,}", ha="center", va="center",
                    fontsize=15, fontweight="bold", color="white" if luminance < 0.5 else "#142b41")
    fig.text(0.04, 0.94, "Transcription notation differs by export", fontsize=23,
             fontweight="bold", color="#142b41")
    fig.text(0.04, 0.885, "Exact annotation occurrences in present locus records", fontsize=13,
             color="#475569")
    fig.text(0.04, 0.13, "Color uses log10(count + 1). Printed values are raw counts; zero marks absent file notation.",
             fontsize=10, color="#475569")
    fig.text(0.04, 0.087, "RF combines ZL and GC. Coverage and annotation conventions differ across these related sources.",
             fontsize=10, color="#475569")
    fig.text(0.04, 0.045, "Source: pinned comparator_profiles.json | Original observations from licensed transcription exports",
             fontsize=9, color="#64748b")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    base = args.output_dir / "transcription-annotations"
    fig.savefig(base.with_suffix(".png"), dpi=180, facecolor="white",
                metadata={"Title": "Transcription notation differs by export"})
    fig.savefig(base.with_suffix(".svg"), facecolor="white",
                metadata={"Title": "Transcription notation differs by export", "Date": None})
    # Matplotlib leaves spaces before path-data newlines; canonicalize the text
    # without changing SVG whitespace semantics, and hash the canonical export.
    svg = base.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(fig)
    provenance = {
        "figure_version": 1,
        "input_profile_sha256": hashlib.sha256(profile_bytes).hexdigest(),
        "exports": list(EXPORTS),
        "annotation_fields": [key for key, _ in COLUMNS],
        "printed_counts": counts.tolist(),
        "color_transform": "log10(count + 1)",
        "python": platform.python_version(),
        "matplotlib": matplotlib.__version__,
        "numpy": np.__version__,
        "source_sha256": {export: profiles[export]["sha256"] for export in EXPORTS},
        "output_sha256": {extension: hashlib.sha256(base.with_suffix(extension).read_bytes()).hexdigest()
                          for extension in (".png", ".svg")},
    }
    base.with_suffix(".json").write_text(json.dumps(provenance, indent=2) + "\n")
    print("Verified source profile and rendered PNG/SVG annotation figure.")


if __name__ == "__main__":
    main()
