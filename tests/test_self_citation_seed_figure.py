import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import plot_self_citation_prefix_seeds as plot


def synthetic_report():
    case = {'accepted_case': True, 'measurements': {'cells': [
        {'model_paragraph_initial': start, 'boundary': boundary, 'prefix': prefix,
         'eligible_rows': 1, 'mean_difference_exact': {'numerator': '0', 'denominator': '1'}}
        for start in [False, True] for boundary in ['first', 'last'] for prefix in ['q', 'y']]}}
    return {'schema_version': 1, 'method': 'fixed-seed native generated prefix census v1',
            'all_planned_cases_accepted': True, 'seed_schedule': list(range(1, 21)),
            'cases': [dict(copy.deepcopy(case), seed=seed) for seed in range(1, 21)]}


class SeedFigureProtectionTests(unittest.TestCase):
    def test_direct_source_stem_is_rejected_before_plotting_or_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'source.json'
            raw = json.dumps(synthetic_report()).encode(); source.write_bytes(raw)
            with patch.object(plot, 'SOURCE', source), patch.object(plot, 'ROOT', root), \
                    patch.object(sys, 'argv', ['plot', '--output-prefix', str(source.with_suffix(''))]):
                with self.assertRaisesRegex(ValueError, 'protected input'):
                    plot.main()
            self.assertEqual(source.read_bytes(), raw)
            self.assertFalse(source.with_suffix('.png').exists())

    def test_existing_symlink_hardlink_and_cross_artifact_aliases_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'source'; source.write_bytes(b'synthetic source')
            symbolic = root / 'symbolic.png'; symbolic.symlink_to(source)
            hard = root / 'hard.png'; hard.hardlink_to(source)
            for destination in [symbolic, hard]:
                with self.assertRaises(ValueError):
                    plot.protect_destination(destination, [source], [destination])
                self.assertEqual(source.read_bytes(), b'synthetic source')
            svg = root / 'same.svg'; svg.hardlink_to(hard)
            with self.assertRaises(ValueError):
                plot.protect_destination(svg, [], [hard, svg])

    def test_late_sidecar_aliases_during_actual_main_are_rejected(self):
        # Stub drawing only: execute the complete real writer/control flow without Matplotlib.
        class Axis:
            spines = {'top': type('Spine', (), {'set_visible': lambda *args: None})(),
                      'right': type('Spine', (), {'set_visible': lambda *args: None})()}
            def __getattr__(self, name):
                return lambda *args, **kwargs: None
        class Axes:
            def __getitem__(self, index):
                return Axis()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'source.json'
            raw = json.dumps(synthetic_report()).encode(); source.write_bytes(raw)
            for alias in ['symbolic', 'hard']:
                prefix = root / alias; sidecar = prefix.with_suffix('.json')
                class Figure:
                    def __getattr__(self, name):
                        return lambda *args, **kwargs: None
                    def savefig(self, path, **kwargs):
                        path.write_bytes(b'<svg/>\n' if path.suffix == '.svg' else b'synthetic png')
                        if path.suffix == '.png':
                            sidecar.symlink_to(source) if alias == 'symbolic' else sidecar.hardlink_to(source)
                fake_pyplot = type('Pyplot', (), {'rcParams': {}, 'subplots': staticmethod(lambda *args, **kwargs: (Figure(), Axes()))})()
                fake_matplotlib = type('Matplotlib', (), {'use': staticmethod(lambda *args: None), '__version__': 'synthetic'})()
                fake_lines = type('Lines', (), {'Line2D': staticmethod(lambda *args, **kwargs: None)})()
                fake_matplotlib.pyplot = fake_pyplot
                fake_matplotlib.lines = fake_lines
                modules = {'matplotlib': fake_matplotlib, 'matplotlib.pyplot': fake_pyplot, 'matplotlib.lines': fake_lines}
                with patch.dict(sys.modules, modules), patch.object(plot, 'SOURCE', source), patch.object(plot, 'ROOT', root), \
                        patch.object(sys, 'argv', ['plot', '--output-prefix', str(prefix)]):
                    with self.assertRaisesRegex(ValueError, 'protected input'):
                        plot.main()
                self.assertEqual(source.read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
