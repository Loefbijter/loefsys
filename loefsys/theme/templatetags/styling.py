from clsx import clsx
from starmerge import merge
from django import template

from .. import variants

register = template.Library()

@register.simple_tag(name="cn")
def do_cn(*args, **kwargs):
    return merge(clsx(args, kwargs))

@register.simple_tag(name="variants")
def do_variants(variant_type: str, **choices: dict[str, str]):
    variant_type_obj = getattr(variants, variant_type, None)
    if not variant_type_obj:
        raise ValueError(f"VariantType {variant_type} does not exist.")

    return variant_type_obj(**choices)
