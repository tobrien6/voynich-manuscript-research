"""Plot all accepted paired-entropy treatments with distinct unit/context facets."""

import argparse
import hashlib
import io
import itertools
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'research/representation/paired_symbol_entropy.json'
REPORT_SHA256 = '3555bb88a361c4f487cb58bef3045877fa50fc3b1c3ddec2c71ecbaebc5d57b6'
FIGURES = ROOT / 'research/representation/figures'
STEM = 'paired-entropy-sensitivity'
SOURCES = ('ZL3b', 'IT2a')
SPACING = ('split', 'join')
UNITS = ('ascii_letters', 'bench_sequences', 'bench_and_minim_sequences')
BOUNDARIES = ('within_token', 'within_locus_with_space')


def figure_data(report, report_sha256):
    if (type(report.get('schema_version')) is not int or report['schema_version'] != 1 or
            report.get('analysis_id') != 'paired-symbol-entropy-sensitivity-v1' or
            report.get('null_or_language_comparison') is not None or
            report.get('may_apply_as_source_correction') is not False):
        raise ValueError('unsupported descriptive entropy report contract')
    selection = report['selection']
    keys = selection['retained_locus_keys']
    if (len(keys) != len(set(keys)) or keys != sorted(keys) or len(keys) != selection['retained_loci'] or
            hashlib.sha256(json.dumps(keys, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
            != selection['retained_locus_keys_sha256']):
        raise ValueError('selected-cohort identity differs')
    sources = report['sources']
    if len(sources) != 2 or {source['id'] for source in sources} != set(SOURCES):
        raise ValueError('figure requires the declared paired source identities')
    if [policy['id'] for policy in report['unit_policies']] != list(UNITS):
        raise ValueError('notation-unit policies changed')
    pins = {source['id']: source['sha256'] for source in sources}
    expected = set(itertools.product(SOURCES, SPACING, UNITS, BOUNDARIES))
    points, seen = [], set()
    for result in report['treatments']:
        identity = tuple(result[field] for field in ('source_id', 'spacing', 'unit_policy', 'boundary_policy'))
        if identity in seen or identity not in expected:
            raise ValueError('duplicate or unexpected treatment')
        seen.add(identity)
        if result['loci'] != len(keys) or result['source_sha256'] != pins[result['source_id']]:
            raise ValueError('source/cohort changes across plotted treatments')
        if (result['edge_count'] != result['unit_count'] - result['segment_count'] or
                result['terminal_unit_count'] != result['segment_count']):
            raise ValueError('segment/edge accounting differs')
        values = [result['bits'][key] for key in ('conditional_successor_entropy', 'difference_due_to_full_marginal')]
        if any(type(value) not in (int, float) or not math.isfinite(value) for value in values):
            raise ValueError('figure requires all declared estimates to be finite')
        points.append({
            **{key: result[key] for key in ('source_id', 'source_sha256', 'spacing', 'unit_policy',
                'boundary_policy', 'loci', 'native_token_count', 'segment_count',
                'segments_without_edges', 'unit_count', 'edge_count', 'terminal_unit_count')},
            'conditional_successor_bits': values[0], 'full_marginal_shift_bits': values[1],
        })
    if seen != expected:
        raise ValueError('figure must retain all 24 treatments')
    return {
        'schema_version': 1, 'figure_version': 'paired-entropy-figure-v1',
        'input_report_sha256': report_sha256,
        'selected_loci': len(keys), 'selected_locus_keys_sha256': selection['retained_locus_keys_sha256'],
        'unit_policies': report['unit_policies'], 'sources': sources,
        'weighting': report['weighting'],
        'lower_panel_definition': 'H(edge predecessors) - H(full units); full-marginal subtraction minus conditional edge entropy',
        'interpretation': 'descriptive within-policy comparison; units and contexts differ between columns; no intervals or language comparison',
        'points': sorted(points, key=lambda p: (UNITS.index(p['unit_policy']), SOURCES.index(p['source_id']),
                                             SPACING.index(p['spacing']), BOUNDARIES.index(p['boundary_policy']))),
    }


def load_report(path):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != REPORT_SHA256:
        raise ValueError('accepted report bytes changed; review and version the figure')
    return figure_data(json.loads(raw), digest)


def protect_targets(output_dir, report_path, root=ROOT):
    targets = [output_dir / (STEM + suffix) for suffix in ('.png', '.svg', '.json')]
    catalog = root / 'data/transliterations.json'
    inputs = [report_path, Path(__file__).resolve(), catalog]
    if catalog.exists():
        inputs.extend(root / source['path'] for source in json.loads(catalog.read_bytes())['sources'])
    for index, target in enumerate(targets):
        if any(target.resolve() == source.resolve() or
               (target.exists() and source.exists() and target.samefile(source)) for source in inputs):
            raise ValueError('figure output aliases a report, source catalog, or implementation')
        if any(target.resolve() == previous.resolve() or
               (target.exists() and previous.exists() and target.samefile(previous)) for previous in targets[:index]):
            raise ValueError('figure artifact paths must be distinct')
    return targets


def write_artifacts(payloads, output_dir, report_path):
    targets = protect_targets(output_dir, report_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    for target, payload in zip(targets, payloads):
        protect_targets(output_dir, report_path)
        target.write_bytes(payload)


def draw(data, output_dir, report_path=REPORT):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    protect_targets(output_dir, report_path)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'svg.hashsalt': 'voynich-paired-entropy-v1'})
    figure, axes = plt.subplots(2, 3, figsize=(13.3, 8.7), sharex=True, sharey='row')
    identities = {(p['source_id'], p['spacing'], p['unit_policy'], p['boundary_policy']): p for p in data['points']}
    categories = list(itertools.product(SOURCES, SPACING))
    styles = {'within_token': ('#126a8a', 'o', -.065),
              'within_locus_with_space': ('#bd650d', 's', .065)}
    titles = ('ASCII letters', 'Listed bench sequences', 'Bench and minim sequences')
    for column, unit in enumerate(UNITS):
        for row, field in enumerate(('conditional_successor_bits', 'full_marginal_shift_bits')):
            axis = axes[row, column]
            axis.grid(axis='y', color='#e5e7eb', linewidth=.7, zorder=0)
            for index, (source, spacing) in enumerate(categories):
                values = [identities[source, spacing, unit, boundary][field] for boundary in BOUNDARIES]
                axis.plot([index-.065, index+.065], values, color='#a3abb4', linewidth=1.3, zorder=1)
                for boundary, value in zip(BOUNDARIES, values):
                    color, marker, offset = styles[boundary]
                    axis.plot(index+offset, value, marker=marker, linestyle='none', color=color,
                              markeredgecolor='white', markeredgewidth=.6, markersize=7, zorder=2)
            axis.set_xlim(-.4, 3.4)
            axis.set_xticks(range(4), [f"{'ZL' if source == 'ZL3b' else 'IT'}\n{spacing}" for source, spacing in categories])
            for spine in ('top', 'right'):
                axis.spines[spine].set_visible(False)
            for spine in ('left', 'bottom'):
                axis.spines[spine].set_color('#c0c6cd')
            if row == 0:
                axis.set_title(titles[column], loc='left', fontsize=12, fontweight='bold', pad=12)
            else:
                axis.axhline(0, color='#6e7781', linewidth=.8, zorder=0)
    all_values = [p['conditional_successor_bits'] for p in data['points']]
    axes[0, 0].set_ylim(min(all_values)-.045, max(all_values)+.045)
    gaps = [p['full_marginal_shift_bits'] for p in data['points']]
    axes[1, 0].set_ylim(min(gaps)-.035, max(0, max(gaps))+.03)
    axes[0, 0].set_ylabel('Conditional successor entropy\n(bits per declared next unit)', labelpad=10)
    axes[1, 0].set_ylabel('Full-marginal subtraction minus\nconditional edge entropy (bits)', labelpad=10)
    figure.suptitle('Entropy depends on the declared units and scored boundaries',
                   x=.065, y=.98, ha='left', fontsize=17, fontweight='bold')
    figure.text(.065, .936, f"{data['selected_loci']:,} fixed clear P0 loci · pooled successor-edge weights · "
                'all 24 source/spacing/unit/boundary treatments', fontsize=10.5, color='#4b5563')
    handles = [Line2D([], [], color=styles[b][0], marker=styles[b][1], linestyle='none', markersize=7,
                      label='Within token' if b=='within_token' else 'Within locus, including space units') for b in BOUNDARIES]
    figure.legend(handles=handles, loc='upper left', bbox_to_anchor=(.058, .918), frameon=False, ncol=2)
    figure.text(.065, .095,
                'Compare paired points within a column. Changing units also changes the preceding-unit context.\n'
                'Lower panels isolate the counting-population difference; negative values mean a lower full-marginal subtraction.\n'
                'Gray connectors pair boundary definitions; no uncertainty ranges are estimated.\n'
                'Source editions and spacing treatments are dependent. The figure makes no language comparison.',
                fontsize=9.5, color='#4b5563', linespacing=1.5, va='top')
    figure.subplots_adjust(left=.1, right=.985, top=.805, bottom=.195, hspace=.35, wspace=.13)
    png, svg = io.BytesIO(), io.BytesIO()
    figure.savefig(png, format='png', dpi=180, facecolor='white', metadata={'Software': 'Voynich Manuscript Research'})
    figure.savefig(svg, format='svg', facecolor='white', metadata={'Date': None, 'Creator': 'Voynich Manuscript Research'})
    svg_bytes = ('\n'.join(line.rstrip() for line in svg.getvalue().decode('utf-8').splitlines())+'\n').encode('utf-8')
    plt.close(figure)
    data['renderer'] = {'matplotlib': matplotlib.__version__, 'font': 'DejaVu Sans',
                        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    # Rendering completes in memory before guarded output writes begin.
    write_artifacts([png.getvalue(), svg_bytes, (json.dumps(data, indent=2)+'\n').encode('utf-8')],
                    output_dir, report_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=REPORT)
    parser.add_argument('--output-dir', type=Path, default=FIGURES)
    args = parser.parse_args()
    try:
        data = load_report(args.input)
        draw(data, args.output_dir, args.input)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'paired entropy figure failed: {error}\n')
    print('Rendered all 24 descriptive treatments and their counting-population shifts.')


if __name__ == '__main__':
    main()
