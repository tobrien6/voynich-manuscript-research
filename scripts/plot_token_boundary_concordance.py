"""Render a descriptive fixed-cohort boundary-concordance figure and provenance."""

import argparse
import hashlib
import io
from pathlib import Path
import platform

try:
    from .audit_eva_token_coverage import encoded, load_json
    from .audit_transliterations import ROOT
    from .paragraph_token_corpus import protect_outputs
    from .token_boundary_concordance import build, key_set, CATEGORIES
except ImportError:
    from audit_eva_token_coverage import encoded, load_json
    from audit_transliterations import ROOT
    from paragraph_token_corpus import protect_outputs
    from token_boundary_concordance import build, key_set, CATEGORIES


REPORT = ROOT / 'research/transliteration/token_boundary_concordance.json'
REPORT_SHA256 = '8c93d9cf1bb83e4f9690378d5fdd6100377e019bf17dede7e0f70de7a4df1bb6'
FIGURES = ROOT / 'research/transliteration/figures'
STEM = 'token-boundary-concordance'


def verified_keys(reference):
    keys = reference['native_locus_keys']
    if (not isinstance(keys, list) or not all(isinstance(key, str) and key for key in keys) or
            len(keys) != len(set(keys)) or keys != sorted(keys) or
            encoded(reference) != encoded(key_set(keys))):
        raise ValueError('invalid native-key count, order, identity or digest')
    return set(keys)


def figure_data(report, sha256):
    if (type(report['schema_version']) is not int or report['schema_version'] != 1 or
            report['method'] != 'exploratory literal-chain boundary concordance v1'):
        raise ValueError('unsupported boundary-concordance report')
    selected = verified_keys(report['selection']['common_eligible'])
    candidates = verified_keys(report['selection']['candidate_shared_present_p0'])
    if not selected or not selected <= candidates:
        raise ValueError('invalid or empty common eligible cohort')
    rows, chain_differences, mismatches = [], [], []
    for policy in ('split', 'join'):
        comparison = report['cross_source'][policy]
        if (comparison['left'] != {'source_id': 'ZL3b', 'spacing': policy} or
                comparison['right'] != {'source_id': 'IT2a', 'spacing': policy} or
                set(comparison['category_key_sets']) != set(CATEGORIES)):
            raise ValueError('source/policy/category contract changed')
        sets = {category: verified_keys(comparison['category_key_sets'][category]) for category in CATEGORIES}
        if set.union(*sets.values()) != selected or sum(map(len, sets.values())) != len(selected):
            raise ValueError('categories must partition the identical common cohort')
        chain_differences.append(sets['different_chains'])
        mismatches.append(sets['same_chain_different_boundaries'])
        rows.append({'spacing': policy, 'selected_native_loci': len(selected),
                     'category_counts': {category: len(sets[category]) for category in CATEGORIES}})
    if chain_differences[0] != chain_differences[1]:
        raise ValueError('comma policies changed different-chain key identities')
    persistent = verified_keys(report['cross_source_boundary_disagreements_under_both_policies'])
    if persistent != set.intersection(*mismatches):
        raise ValueError('persistent boundary-disagreement intersection differs')
    return {
        'schema_version': 1, 'figure_version': 'token-boundary-concordance-figure-v1',
        'input_report_sha256': sha256,
        'selected_native_loci': len(selected), 'candidate_shared_present_p0': len(candidates),
        'excluded_candidate_loci': len(candidates - selected),
        'selected_native_keys_sha256': report['selection']['common_eligible']['sorted_native_keys_sha256'],
        'sources': report['sources'], 'rows': rows,
        'boundary_disagreements_under_both_policies': len(persistent),
        'interpretation': 'descriptive related transcription treatments; ASCII chains/boundaries, not glyphs or linguistic words; no independent samples or decipherment',
    }


def render(data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    labels = ('Same chain\nand boundaries', 'Same chain,\ndifferent boundaries', 'Different\nencoded chains')
    colors = ('#246C94', '#EAA333', '#6B7280')
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 12,
                         'svg.hashsalt': 'token-boundary-concordance-v1', 'svg.fonttype': 'none'}):
        fig, ax = plt.subplots(figsize=(12, 7.5))
        fig.subplots_adjust(left=.16, right=.965, bottom=.36, top=.73)
        total = data['selected_native_loci']
        for index, row in enumerate(data['rows']):
            left = 0
            for category, color in zip(CATEGORIES, colors):
                count = row['category_counts'][category]
                ax.barh(index, count, left=left, height=.42, color=color, edgecolor='white', linewidth=2)
                if count:
                    ax.text(left + count / 2, index, f'{count:,}', ha='center', va='center',
                            color='#161616' if color == colors[1] else 'white', fontsize=16, fontweight='bold')
                left += count
        ax.set_yticks([0, 1], ['Comma split\nZL vs IT', 'Comma join\nZL vs IT'])
        ax.invert_yaxis()
        ax.set_xlim(0, total)
        ax.set_xticks([0, total / 3, 2 * total / 3, total], [f'{round(v):,}' for v in (0, total / 3, 2 * total / 3, total)])
        ax.set_xlabel('Paired native locus keys — the same cohort in both rows', labelpad=10)
        ax.tick_params(axis='both', length=0, pad=10)
        ax.set_axisbelow(True)
        ax.grid(axis='x', color='#E4E7EB', linewidth=.8)
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.text(.055, .94, 'Identical encoded text can have different token boundaries',
                 fontsize=20, fontweight='bold', va='top')
        fig.text(.055, .875, f"{total:,} common eligible P0 loci • pinned ZL3b / IT2a • case preserved", fontsize=13)
        fig.legend(handles=[Patch(facecolor=color, label=label) for color, label in zip(colors, labels)],
                   loc='upper left', bbox_to_anchor=(.05, .825), ncol=3, frameon=False,
                   handlelength=1.1, columnspacing=2.3, fontsize=12)
        fig.text(.055, .18,
                 f"{data['boundary_disagreements_under_both_policies']:,} loci have boundary disagreements under both policies.\n"
                 'Offsets are compared only on identical ASCII chains; different chains are not aligned.', fontsize=12)
        fig.text(.055, .09,
                 f"{data['candidate_shared_present_p0']:,} shared present P0 candidates; {data['excluded_candidate_loci']:,} jointly excluded.\n"
                 'Related source treatments, not independent samples. Word divisions, glyphs and decipherment remain unresolved.',
                 fontsize=11, color='#444444')
        png, svg = io.BytesIO(), io.BytesIO()
        fig.savefig(png, format='png', dpi=160, metadata={'Software': 'Matplotlib'})
        fig.savefig(svg, format='svg', metadata={'Date': None, 'Creator': 'Voynich Manuscript Research / Matplotlib',
                                               'Title': 'Literal-chain and token-boundary concordance'})
        plt.close(fig)
    svg_bytes = ('\n'.join(line.rstrip() for line in svg.getvalue().decode('utf-8').splitlines()) + '\n').encode('utf-8')
    result = {'png': png.getvalue(), 'svg': svg_bytes}
    provenance = dict(data, renderer={'matplotlib': matplotlib.__version__, 'python': platform.python_version(),
                                      'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
                      output_sha256={ext: hashlib.sha256(raw).hexdigest() for ext, raw in result.items()})
    result['json'] = encoded(provenance)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output-dir', type=Path)
    mode.add_argument('--check-dir', type=Path)
    args = parser.parse_args()
    try:
        directory = args.output_dir or args.check_dir
        targets = [directory / (STEM + '.' + ext) for ext in ('png', 'svg', 'json')]
        protect_outputs(targets if args.output_dir else [], [REPORT], root=ROOT)
        raw = REPORT.read_bytes()
        if hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
            raise ValueError('pinned report bytes changed; review and version the figure')
        report = load_json(raw)
        if encoded(report) != encoded(build()):
            raise ValueError('input report differs from complete fresh source replay')
        output = render(figure_data(report, REPORT_SHA256))
        if args.check_dir:
            for path in targets:
                if path.read_bytes() != output[path.suffix[1:]]:
                    raise ValueError('committed export differs from deterministic rendering: ' + path.name)
        else:
            directory.mkdir(parents=True, exist_ok=True)
            for path in targets:
                path.write_bytes(output[path.suffix[1:]])
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f'boundary figure failed: {error}\n')
    print('Verified both source/spacing contrasts and all three figure exports.')


if __name__ == '__main__':
    main()
