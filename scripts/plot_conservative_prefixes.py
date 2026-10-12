"""Render observed prefix contrasts beside their conditional-order references."""

import argparse
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'research/transliteration/conservative_prefixes.json'
FIGURES = ROOT / 'research/transliteration/figures'
SOURCE_IDS = ('ZL3b', 'IT2a')
FEATURE_IDS = ('literal_q_prefix', 'literal_y_prefix')


def quantile(values, probability):
    if not values:
        return None
    ordered = sorted(values)
    location = probability * (len(ordered) - 1)
    lower, upper = math.floor(location), math.ceil(location)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (location - lower)


def plot_data(report, report_sha256, source_hashes, spacing):
    if (report['schema_version'] != 1 or report['adapter_version'] != 'plain-eva-v1' or
            report['method'] != 'exploratory plain-eva-v1 common-cohort prefix controls v1'):
        raise ValueError('unsupported conservative report contract')
    selected = report['selection']['selected_locus_keys']
    count = report['selection']['selected_count']
    digest = hashlib.sha256(('\n'.join(sorted(selected)) + '\n').encode()).hexdigest()
    if len(selected) != len(set(selected)) or len(selected) != count or digest != report['selection']['sorted_selected_locus_keys_sha256']:
        raise ValueError('selected-cohort identity is inconsistent')
    sources = report['sources']
    if len(sources) != 2 or {source['id'] for source in sources} != set(SOURCE_IDS):
        raise ValueError('figure requires the declared ZL/IT pair')
    labels = report['selection']['source_currier_labels_including_unset']
    expected_groups = {(label, start) for label in labels for start in (False, True)}
    points, repetitions = [], set()
    for source in sources:
        if source['sha256'] != source_hashes[source['id']]:
            raise ValueError('figure source hash does not match pinned catalogue')
        variants = [variant for variant in source['variants'] if variant['spacing'] == spacing]
        if len(variants) != 1:
            raise ValueError('missing or duplicate requested spacing policy')
        cohorts = variants[0]['cohorts']
        groups = [(cohort['source_currier_label'], cohort['source_paragraph_start']) for cohort in cohorts]
        if len(groups) != len(set(groups)) or set(groups) != expected_groups or sum(cohort['selected_loci'] for cohort in cohorts) != count:
            raise ValueError('figure cohorts do not partition the selected locations')
        for cohort in cohorts:
            positions = cohort['positions']
            if len(positions) != 2 or {position['boundary'] for position in positions} != {'first', 'last'}:
                raise ValueError('boundary result coverage changed')
            for position in positions:
                size = position['eligible_loci']
                if size != cohort['selected_loci']:
                    raise ValueError('fixed-cohort boundary eligibility changed')
                repetitions.add(position['shuffle_repetitions'])
                features = position['features']
                if len(features) != 2 or {feature['feature'] for feature in features} != set(FEATURE_IDS):
                    raise ValueError('prefix feature coverage changed')
                for feature in features:
                    null = feature['shuffle_differences']
                    if size and len(null) != position['shuffle_repetitions']:
                        raise ValueError('shuffle reference count changed')
                    points.append({
                        'source_id': source['id'], 'source_sha256': source['sha256'],
                        'source_currier_label': cohort['source_currier_label'],
                        'source_paragraph_start': cohort['source_paragraph_start'],
                        'boundary': position['boundary'], 'feature': feature['feature'], 'loci': size,
                        'observed_percentage_points': (100 * feature['paired_difference']) if size else None,
                        'null_2_5_percentage_points': (100 * quantile(null, .025)) if size else None,
                        'null_97_5_percentage_points': (100 * quantile(null, .975)) if size else None,
                    })
    if len(repetitions) != 1:
        raise ValueError('mixed shuffle reference counts')
    return {
        'schema_version': 1, 'figure_version': 'conservative-prefix-figure-v1',
        'input_report_sha256': report_sha256, 'spacing': spacing, 'selected_loci': count,
        'selected_locus_keys_sha256': digest, 'source_ids': list(SOURCE_IDS),
        'source_currier_labels_including_unset': labels,
        'shuffle_repetitions': repetitions.pop(),
        'reference': 'central 95 percent of conditional within-locus shuffle contrasts',
        'quantile_method': 'linear interpolation at p * (n - 1)',
        'points': points,
    }


def draw(data, output_dir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10.5,
                         'svg.hashsalt': 'voynich-conservative-prefix-v1'})
    groups = [(label, start) for label in data['source_currier_labels_including_unset'] for start in (False, True)]
    lookup = {(point['source_id'], point['source_currier_label'], point['source_paragraph_start'],
               point['boundary'], point['feature']): point for point in data['points']}
    styles = {'ZL3b': ('#126a8a', 'o', -.12), 'IT2a': ('#bd650d', 's', .12)}
    figure, axes = plt.subplots(2, 2, figsize=(13.6, 10.2), sharex='col', sharey=True)
    for row, boundary in enumerate(('first', 'last')):
        for column, feature in enumerate(FEATURE_IDS):
            axis = axes[row, column]
            axis.axvline(0, color='#6e7781', linewidth=.9, zorder=0)
            axis.grid(axis='x', color='#e5e7eb', linewidth=.7, zorder=0)
            for index, (label, start) in enumerate(groups):
                for source_id in SOURCE_IDS:
                    point = lookup[(source_id, label, start, boundary, feature)]
                    color, marker, offset = styles[source_id]
                    y = index + offset
                    if point['observed_percentage_points'] is None:
                        axis.text(0, y, 'undefined (n=0)', fontsize=8, color=color)
                        continue
                    low, high = point['null_2_5_percentage_points'], point['null_97_5_percentage_points']
                    axis.plot([low, high], [y, y], color='#c0c6cd', linewidth=3.8, solid_capstyle='butt', zorder=1)
                    axis.plot([low, high], [y, y], '|', color='#a3abb4', markersize=8, zorder=2)
                    axis.plot(point['observed_percentage_points'], y, marker=marker, color=color,
                              markeredgecolor='white', markeredgewidth=.6, markersize=6.5, zorder=3)
            axis.set_title(f"{boundary.capitalize()} slot · literal {'q' if column == 0 else 'y'} prefix",
                           loc='left', fontsize=12, fontweight='bold', pad=10)
            axis.set_ylim(len(groups) - .45, -.55)
            axis.tick_params(axis='y', length=0)
            for spine in ('top', 'right', 'left'):
                axis.spines[spine].set_visible(False)
            axis.spines['bottom'].set_color('#c0c6cd')
            if row == 1:
                axis.set_xlabel('Boundary − mean of locus others\n(percentage points)', labelpad=8)
    labels = []
    for label, start in groups:
        sizes = [lookup[(source_id, label, start, 'first', FEATURE_IDS[0])]['loci'] for source_id in SOURCE_IDS]
        labels.append(f"{label} · paragraph start: {'yes' if start else 'no'}\nn={sizes[0]:,}/{sizes[1]:,} (ZL/IT)")
    axes[0, 0].set_yticks(range(len(groups)), labels)
    for column, feature in enumerate(FEATURE_IDS):
        extent = [0.0]
        for point in data['points']:
            if point['feature'] == feature:
                extent.extend(point[key] for key in ('observed_percentage_points',
                              'null_2_5_percentage_points', 'null_97_5_percentage_points') if point[key] is not None)
        axes[0, column].set_xlim(math.floor((min(extent) - 2) / 5) * 5,
                                math.ceil((max(extent) + 2) / 5) * 5)
    figure.suptitle('Literal EVA prefixes vary by context', x=.055, ha='left', y=.98,
                     fontsize=18, fontweight='bold')
    figure.text(.055, .942, f"plain-eva-v1 · {data['selected_loci']:,} fixed P0 locations · "
                f"{data['spacing']} uncertain spaces", fontsize=11, color='#4b5563')
    handles = [Line2D([], [], marker=styles[source][1], color=styles[source][0], linestyle='none',
                      markersize=7, label=source) for source in SOURCE_IDS]
    handles.append(Line2D([], [], color='#c0c6cd', linewidth=4, label='Central 95% of conditional shuffles'))
    figure.legend(handles=handles, loc='upper left', bbox_to_anchor=(.048, .913), frameon=False, ncol=3)
    figure.text(.055, .085, f"Points: observed contrasts. Gray ranges: {data['shuffle_repetitions']} within-locus "
                "shuffles that preserve token bags.\nSource-defined partitions can differ; unset cohorts are small. "
                "All comparisons are exploratory.\nUnits are encoded source loci; Currier labels are source annotations.",
                fontsize=10, color='#4b5563', linespacing=1.5, va='top')
    figure.subplots_adjust(left=.26, right=.98, top=.82, bottom=.19, hspace=.36, wspace=.19)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = output_dir / f"conservative-prefixes-{data['spacing']}"
    figure.savefig(stem.with_suffix('.png'), dpi=180, facecolor='white',
                   metadata={'Software': 'Voynich Manuscript Research'})
    figure.savefig(stem.with_suffix('.svg'), facecolor='white',
                   metadata={'Date': None, 'Creator': 'Voynich Manuscript Research'})
    svg = stem.with_suffix('.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    plt.close(figure)
    data['renderer'] = {'matplotlib': matplotlib.__version__, 'font': 'DejaVu Sans'}
    stem.with_suffix('.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=REPORT)
    parser.add_argument('--spacing', choices=('split', 'join', 'both'), default='both')
    parser.add_argument('--output-dir', type=Path, default=FIGURES)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    report = json.loads(raw)
    catalog = json.loads((ROOT / 'data/transliterations.json').read_text())
    hashes = {source['id']: source['sha256'] for source in catalog['sources']}
    try:
        for spacing in ('split', 'join') if args.spacing == 'both' else (args.spacing,):
            data = plot_data(report, hashlib.sha256(raw).hexdigest(), hashes, spacing)
            draw(data, args.output_dir)
    except (ValueError, KeyError) as error:
        parser.exit(1, f'figure failed: {error}\n')
    print('Rendered prefix contrasts with source counts and conditional reference ranges.')


if __name__ == '__main__':
    main()
