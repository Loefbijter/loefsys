"""Tests for the wave banner template tag."""

from django.template import Context, Template
from django.test import SimpleTestCase

from loefsys.theme.templatetags.waves import HEIGHTS, wave_path, wave_y


class WaveTagTests(SimpleTestCase):
    """The wave SVG is drawn from one formula shared with the sailboat script."""

    def test_renders_three_layers_for_each_banner(self):
        """Every banner has a back, middle and front layer."""
        for kind in HEIGHTS:
            with self.subTest(kind=kind):
                html = Template("{% load waves %}{% wave_svg kind %}").render(
                    Context({"kind": kind})
                )
                self.assertEqual(html.count("<path"), 3)
                self.assertIn(f'viewBox="0 0 1000 {HEIGHTS[kind]}"', html)

    def test_class_is_escaped(self):
        """The CSS class argument cannot break out of the attribute."""
        html = Template('{% load waves %}{% wave_svg "top" css %}').render(
            Context({"css": '"><script>'})
        )
        self.assertNotIn("<script>", html)

    def test_path_follows_the_wave_formula(self):
        """The path passes through the computed water line at both edges."""
        path = wave_path(66, 6, 2.2, 86, fill_below=True)
        self.assertTrue(path.startswith("M0 86 "))
        self.assertIn(f"L0 {wave_y(0, 66, 6, 2.2):.1f}", path)
        self.assertIn(f"L1000 {wave_y(1, 66, 6, 2.2):.1f}", path)
