#!/usr/bin/env python3
"""Plot every defined prefix cell in the completed deterministic seed grid."""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/literature/self-citation-prefix-seeds.json'


def protected_inputs():
    return [SOURCE, Path(__file__), ROOT / 'requirements-figure.txt',
            *[ROOT / path for path in [
                'research/literature/SELF_CITATION_PREFIX_SEED_PLAN.md',
                'research/literature/self-citation-repeatability.json',
                'research/literature/self-citation-row-trace.json',
                'scripts/census_self_citation_prefixes.py', 'scripts/trace_self_citation_rows.py',
                'scripts/replay_self_citation.py', 'scripts/prefix_conditional_bounds.py']]]


def protect_destination(destination, inputs, artifacts):
    """Reject existing or newly created path/inode aliases before each write."""
    for source in [*inputs, *[path for path in artifacts if path != destination]]:
        if (destination.resolve() == source.resolve() or
                (destination.exists() and source.exists() and destination.samefile(source))):
            raise ValueError('figure output aliases a protected input or another artifact')


def figure_data(raw):
    report = json.loads(raw)
    if (report['schema_version'] != 1 or report['method'] != 'fixed-seed native generated prefix census v1' or
            report['all_planned_cases_accepted'] is not True or report['seed_schedule'] != list(range(1, 21)) or
            [case['seed'] for case in report['cases']] != report['seed_schedule']):
        raise ValueError('require the complete accepted twenty-seed contract')
    expected = {(start, boundary, prefix) for start in [False, True] for boundary in ['first', 'last'] for prefix in ['q', 'y']}
    points = []
    for case in report['cases']:
        cells = case['measurements']['cells']
        identities = [(cell['model_paragraph_initial'], cell['boundary'], cell['prefix']) for cell in cells]
        if len(cells) != 8 or set(identities) != expected or case['accepted_case'] is not True:
            raise ValueError('missing/duplicate seed comparison')
        for cell in cells:
            value = cell['mean_difference_exact']
            if value is None or cell['eligible_rows'] < 1:
                raise ValueError('undefined cells need a separately specified missing-value figure')
            exact = Fraction(int(value['numerator']), int(value['denominator']))
            points.append({'seed': case['seed'], 'model_paragraph_initial': cell['model_paragraph_initial'],
                           'boundary': cell['boundary'], 'prefix': cell['prefix'],
                           'eligible_rows': cell['eligible_rows'], 'mean_difference_exact': value,
                           'percentage_points': float(exact) * 100})
    return {'source_report_sha256': hashlib.sha256(raw).hexdigest(), 'units': 'percentage points; equal native-row weight',
            'scope': 'descriptive deterministic seed grid; no confidence band or manuscript comparison', 'points': points}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-prefix', type=Path,
                        default=ROOT / 'research/literature/figures/self-citation-prefix-seeds')
    args = parser.parse_args()
    png, svg, sidecar = [args.output_prefix.with_suffix(suffix) for suffix in ['.png', '.svg', '.json']]
    artifacts, inputs = [png, svg, sidecar], protected_inputs()
    for destination in artifacts:
        protect_destination(destination, inputs, artifacts)
    data = figure_data(SOURCE.read_bytes())
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.hashsalt': 'self-citation-prefix-seed-v1'})
    figure, axes = plt.subplots(2, 2, figsize=(12, 8.3), sharex=True, sharey=True)
    figure.subplots_adjust(left=.09, right=.98, bottom=.17, top=.80, hspace=.30, wspace=.12)
    colors, markers = {'q': '#2374ab', 'y': '#cf5a32'}, {'q': 'o', 'y': 's'}
    for row, start in enumerate([False, True]):
        for column, boundary in enumerate(['first', 'last']):
            axis = axes[row, column]
            subset = [point for point in data['points'] if point['model_paragraph_initial'] == start and point['boundary'] == boundary]
            counts = [point['eligible_rows'] for point in subset]
            for prefix in ['q', 'y']:
                series = [point for point in subset if point['prefix'] == prefix]
                shift = -.11 if prefix == 'q' else .11
                axis.scatter([point['seed'] + shift for point in series], [point['percentage_points'] for point in series],
                             color=colors[prefix], marker=markers[prefix], s=29, alpha=.9, edgecolors='none', zorder=3)
            axis.axhline(0, color='#6e747a', linewidth=1, zorder=1)
            axis.grid(axis='y', color='#e4e7eb', linewidth=.7)
            axis.set_axisbelow(True)
            axis.set_title(f'{boundary.capitalize()} token · paragraph start flag {str(start).lower()}\n'
                           f'{min(counts):,}–{max(counts):,} eligible rows per seed', fontsize=11, loc='left', pad=10)
            axis.set_xlim(.3, 20.7)
            axis.set_ylim(-10.5, 4.8)
            axis.set_xticks([1, 5, 10, 15, 20])
            for spine in ['top', 'right']:
                axis.spines[spine].set_visible(False)
            if column == 0:
                axis.set_ylabel('Boundary minus other-token prefix rate\n(percentage points)')
            if row == 1:
                axis.set_xlabel('Fixed pseudo-random seed')
    handles = [Line2D([], [], color=colors[prefix], marker=markers[prefix], linestyle='none', markersize=7,
                      label=f'literal {prefix} prefix') for prefix in ['q', 'y']]
    figure.legend(handles=handles, loc='upper center', bbox_to_anchor=(.54, .900), ncol=2, frameon=False)
    figure.text(.09, .97, 'Released generator: prefix contrasts across fixed seeds', fontsize=19, weight='bold', va='top')
    figure.text(.09, .922, 'Twenty seeds · 1,199 newly generated rows per seed · Java 22.0.2 · native space-delimited tokens',
                fontsize=11, color='#525b65', va='top')
    figure.text(.09, .09, 'All 20 original/observed pairs preserved complete output bytes across 40 processes.\n'
                         'Initialization is excluded. Dots show the chosen seed grid; no confidence interval or manuscript comparison is drawn.',
                fontsize=10, color='#525b65', va='top')
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    protect_destination(png, inputs, artifacts)
    figure.savefig(png, dpi=160)
    protect_destination(svg, inputs, artifacts)
    figure.savefig(svg, metadata={'Date': None})
    protect_destination(svg, inputs, artifacts)
    normalized = '\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n'
    protect_destination(svg, inputs, artifacts)
    svg.write_text(normalized)
    data.update({'renderer': {'matplotlib': matplotlib.__version__, 'python': platform.python_version(), 'font': 'DejaVu Sans'},
                 'figure_producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    protect_destination(sidecar, inputs, artifacts)
    sidecar.write_text(json.dumps(data, indent=2) + '\n')
    print(f'Plotted all {len(data["points"])} points to {args.output_prefix}.')


if __name__ == '__main__':
    main()
