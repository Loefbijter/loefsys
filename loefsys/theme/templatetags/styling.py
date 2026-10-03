"""Template tags for styling helpers."""

from clsx import clsx
from django import template
from starmerge import merge

from .. import variants

register = template.Library()


@register.simple_tag(name="cn")
def do_cn(*args, **kwargs):
    """Build a combined CSS classname string from clsx arguments."""
    return merge(clsx(args, kwargs))


@register.simple_tag(name="variants")
def do_variants(variant_type: str, **choices: dict[str, str]):
    """Resolve variant token values into a CSS class string."""
    variant_type_obj = getattr(variants, variant_type, None)
    if not variant_type_obj:
        raise ValueError(f"VariantType {variant_type} does not exist.")

    return variant_type_obj(**choices)
