"""Template tags that draw the layered wave banners.

The wave height at a point only depends on its relative horizontal position, so a
path drawn for a 1000-unit wide viewBox and stretched with
``preserveAspectRatio="none"`` keeps the same shape at any screen width. The
sailboat script (``static/JS/sailboat.js``) uses the same formula to find the
water line, so the two must stay in sync.
"""

import math

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import SafeString, mark_safe

register = template.Library()

WIDTH = 1000
STEP = 10

# (base, amplitude, phase, strength) per layer, back to front. The strength is
# the share of the wave colour mixed into the page background.
LAYERS = {
    "top": ((20, 5, 0.4, 33), (14, 5, 1.6, 66), (7, 4, 2.9, 100)),
    "bottom": ((52, 6, 0.9, 33), (58, 6, 4.1, 66), (66, 6, 2.2, 100)),
    "nav": ((10, 4, 0.7, 33), (13, 4, 3.3, 66), (16, 3, 1.9, 100)),
}
HEIGHTS = {"top": 26, "bottom": 86, "nav": 20}


def wave_y(x: float, base: float, amp: float, phase: float) -> float:
    """Return the height of the wave at relative position ``x`` (0..1)."""
    tau = 2 * math.pi
    return base + amp * (
        0.62 * math.sin(x * tau * 1.3 + phase)
        + 0.38 * math.sin(x * tau * 3.1 + phase * 1.7)
    )


def wave_path(base: float, amp: float, phase: float, height: int, *, fill_below: bool):
    """Build the SVG path for one wave layer.

    With ``fill_below`` the area under the curve is filled (a wave rising from the
    bottom of the screen); otherwise the area above it (a banner hanging down).
    """
    points = " ".join(
        f"L{x} {wave_y(x / WIDTH, base, amp, phase):.1f}"
        for x in range(0, WIDTH + 1, STEP)
    )
    edge = height if fill_below else 0
    return f"M0 {edge} {points} L{WIDTH} {edge} Z"


@register.simple_tag
def wave_svg(kind: str, css_class: str = "wave") -> SafeString:
    """Render the layered wave SVG for the top banner, bottom wave or phone nav."""
    height = HEIGHTS[kind]
    paths = "".join(
        f'<path style="fill: color-mix(in oklab, var(--wave) {strength}%, var(--bg))" '
        f'd="{wave_path(base, amp, phase, height, fill_below=kind != "top")}"/>'
        for base, amp, phase, strength in LAYERS[kind]
    )
    return mark_safe(
        f'<svg class="{conditional_escape(css_class)}" viewBox="0 0 {WIDTH} {height}" '
        f'preserveAspectRatio="none" aria-hidden="true" focusable="false">'
        f"{paths}</svg>"
    )
