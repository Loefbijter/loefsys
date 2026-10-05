"""Template tags module for not rendering blocks when certain apps aren't installed."""

from decimal import Decimal

from django import template
from django.utils.formats import number_format
from django.utils.translation import gettext as _

register = template.Library()


@register.filter
def euro(value: Decimal | float) -> str:
    """Format a numerical value as euro's, in the active language's number format.

    For example "€ 10,00" in Dutch and "€ 10.00" in English.
    """
    if not value:
        return _("Free!")

    if not isinstance(value, (Decimal, float)):
        raise ValueError("The 'euro' filter only accepts Decimal or float values.")

    return f"€ {number_format(value, 2)}"
