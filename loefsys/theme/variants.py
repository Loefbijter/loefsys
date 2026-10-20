"""Variant definitions for theme-aware component classes."""


class VariantType:
    """A callable holder of CSS variants for themed components."""

    def __init__(
        self,
        base: str,
        variants: dict[str, dict[str, str]],
        /,
        defaults: dict[str, str] | None = None,
    ):
        self.base = base
        self.variants = variants
        self.defaults = defaults or {}

    def __call__(self, **variants: str):
        """Render the configured variant styles for the given variant keys."""
        values: list[str] = []
        for k, v in variants.items():
            val = self.variants[k].get(v)
            if val is None:
                default_key = self.defaults.get(k)
                # default_key may be None; provide empty fallback when lookup fails
                val = self.variants[k].get(default_key or "", "")
            values.append(val)
        return f"{self.base} {' '.join(values)}"


button = VariantType(
    "btn",
    {
        "variant": {
            "default": "btn-primary",
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "ghost": "btn-ghost",
            "danger": "btn-danger",
            "destructive": "btn-destructive",
        },
        "size": {"default": "", "sm": "btn-sm", "icon": "btn-icon"},
    },
    {"variant": "default", "size": "default"},
)
"""Pill buttons; the classes are defined in ``styles/globals.css``."""
