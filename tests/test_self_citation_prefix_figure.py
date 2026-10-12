import os
from pathlib import Path
import tempfile
import unittest

from scripts.plot_self_citation_prefix_profile import write_figure


class FixtureFigure:
    def __init__(self, payload, during_render=lambda: None):
        self.payload = payload
        self.during_render = during_render

    def savefig(self, stream, **kwargs):
        stream.write(self.payload)
        self.during_render()


class SelfCitationPrefixFigureTests(unittest.TestCase):
    def test_late_input_aliases_cannot_be_reopened_for_normalization_or_writing(self):
        for alias_kind in ('symlink', 'hardlink'):
            for suffix in ('png', 'svg'):
                with self.subTest(alias_kind=alias_kind, suffix=suffix), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    source = root / 'synthetic-input.txt'
                    original = b'protected synthetic source with intentional spaces  \n'
                    source.write_bytes(original)
                    target = root / ('figure.' + suffix)

                    def introduce_alias():
                        if alias_kind == 'symlink':
                            target.symlink_to(source)
                        else:
                            os.link(source, target)

                    figure = FixtureFigure(b'<svg>replacement  \n</svg>\n', introduce_alias)
                    with self.assertRaises(FileExistsError):
                        write_figure(figure, target, suffix, {})
                    self.assertEqual(source.read_bytes(), original)
                    self.assertEqual(target.read_bytes(), original)

    def test_existing_artifact_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'figure.svg'
            target.write_bytes(b'original artifact\n')
            with self.assertRaises(FileExistsError):
                write_figure(FixtureFigure(b'replacement\n'), target, 'svg', {})
            self.assertEqual(target.read_bytes(), b'original artifact\n')

    def test_failed_render_creates_no_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'figure.png'

            def fail():
                raise ValueError('synthetic rendering failure')

            with self.assertRaises(ValueError):
                write_figure(FixtureFigure(b'incomplete payload', fail), target, 'png', {})
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
