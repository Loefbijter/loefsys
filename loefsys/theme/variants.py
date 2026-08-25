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
    (
        "inline-flex items-center justify-center gap-2 whitespace-nowrap "
        "rounded-md transition-all disabled:pointer-events-none "
        "disabled:opacity-50 shrink-0"
    ),
    {
        "variant": {
            "default": (
                "bg-secondary text-secondary-foreground border-t-2 "
                "border-secondary-accent hover:bg-tertiary "
                "hover:text-tertiary-foreground hover:border-tertiary-accent"
            ),
            "ghost": (
                "bg-background text-foreground border-t-2 border-accent "
                "hover:bg-background/80 hover:text-foreground/80 "
                "hover:border-accent/80"
            ),
            "destructive": (
                "bg-destructive text-destructive-foreground border-t-2 "
                "border-destructive-accent hover:bg-destructive/90 "
                "hover:border-destructive-accent/90"
            ),
        },
        "size": {"default": "h-8 px-4 py-2"},
    },
    {"variant": "default", "size": "default"},
)
