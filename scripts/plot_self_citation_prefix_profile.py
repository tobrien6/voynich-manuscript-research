"""Render every fixed prefix-profile comparison; no model or target is refitted."""

import argparse
import hashlib
import json
from pathlib import Path
import platform


ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def render(report_path, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy

    raw = report_path.read_bytes()
    report = json.loads(raw)
    if (report['planned_execution_complete'] is not True or
            report['all_comparison_ranges_defined'] is not True or
            len(report['cases']) != 31 or len(report['comparisons']) != 32):
        raise ValueError('figure requires all planned executions and defined comparison points')
    output.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'svg.hashsalt': 'fixed-self-citation-prefix-v1',
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 4, figsize=(17, 8.1))
    variants = [('ZL3b', 'split', '#276b89', 'o'), ('ZL3b', 'join', '#276b89', '^'),
                ('IT2a', 'split', '#bd633d', 'o'), ('IT2a', 'join', '#bd633d', '^')]
    all_values = [item['target']['mean'] for item in report['comparisons']]
    all_values += [item['contrast']['mean'] for case in report['cases'] for item in case['profile']]
    low, high = min(all_values), max(all_values)
    padding = (high - low) * .08
    plotted = []
    for row_index, initial in enumerate((False, True)):
        for column, (boundary, prefix) in enumerate((('first', 'q'), ('first', 'y'), ('last', 'q'), ('last', 'y'))):
            ax = axes[row_index, column]
            points = [item for item in report['comparisons'] if item['paragraph_initial'] == initial and
                      item['boundary'] == boundary and item['prefix'] == prefix]
            seeds = [next(item['contrast']['mean'] for item in case['profile']
                          if item['paragraph_initial'] == initial and item['boundary'] == boundary and
                          item['prefix'] == prefix) for case in report['cases']]
            ax.plot([min(seeds), max(seeds)], [0, 0], color='#404449', lw=3, zorder=2)
            ax.scatter(seeds, [((index % 3) - 1) * .055 for index in range(31)],
                       color='#767c83', s=16, alpha=.65, zorder=3)
            for y, (source, spacing, color, marker) in enumerate(variants, 1):
                point = next(item for item in points if item['source_id'] == source and item['spacing'] == spacing)
                ax.scatter(point['target']['mean'], y, color=color, marker=marker, s=45, zorder=4)
                plotted.append(point)
            ax.axvline(0, color='#bdc2c7', lw=.8, zorder=1)
            ax.set_xlim(low - padding, high + padding)
            ax.set_ylim(4.6, -.6)
            ax.set_yticks(range(5), ['Model: 31 seeds', 'ZL split', 'ZL join', 'IT split', 'IT join'])
            ax.set_title(f'{boundary.capitalize()} slot: {prefix}', loc='left', fontweight='bold', pad=12)
            ax.grid(axis='x', alpha=.18)
            if column:
                ax.tick_params(axis='y', labelleft=False)
            if row_index:
                ax.set_xlabel('Boundary prefix contrast')
        axes[row_index, 0].set_ylabel('Start flag: ' + ('true' if initial else 'false'), labelpad=14)
    outside = sum(item['within_fixed_seed_range'] is False for item in report['comparisons'])
    fig.suptitle('Fixed self-citation profile and source-defined B contrasts', x=.045, ha='left', fontsize=19)
    fig.text(.045, .925, f'{outside} of 32 related source/policy points fall outside the observed seed ranges. '
             'Bars show minimum to maximum across fixed seeds 1-31.', fontsize=11, color='#3f464e')
    fig.text(.045, .055, 'Equal-locus source weights; equal-row model weights. '
             'Initialization is excluded from the measured rows and retained as an input dependency.', fontsize=10)
    fig.text(.045, .025, 'Ranges have no calibrated probability coverage. '
             'Source/model paragraph contexts and physical/glyph units remain unverified as equivalents.',
             fontsize=10, color='#555d65')
    fig.subplots_adjust(left=.12, right=.985, bottom=.15, top=.855, hspace=.38, wspace=.12)
    paths = []
    for suffix, kwargs in [('png', {'dpi': 160}), ('svg', {'metadata': {'Date': None}})]:
        path = output / ('profile.' + suffix)
        with path.open('xb') as stream:
            fig.savefig(stream, format=suffix, **kwargs)
        paths.append(path)
    plt.close(fig)
    provenance = {'schema_version': 1, 'input_report_sha256': digest(raw),
                  'renderer_sha256': digest(Path(__file__).read_bytes()),
                  'runtime': {'python': platform.python_version(), 'matplotlib': matplotlib.__version__,
                              'numpy': numpy.__version__, 'backend': 'Agg'},
                  'plotted_comparisons': plotted,
                  'artifacts': [{'filename': path.name, 'bytes': path.stat().st_size,
                                 'sha256': digest(path.read_bytes())} for path in paths],
                  'scope': 'Original statistical figure; fixed-seed range, no calibrated interval or mechanism validation'}
    with (output / 'provenance.json').open('x') as stream:
        json.dump(provenance, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT / 'research/literature/self-citation-prefix-profile.json')
    parser.add_argument('--new-output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        render(args.report, args.new_output_dir)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'Profile figure failed: {error}\n')


if __name__ == '__main__':
    main()
