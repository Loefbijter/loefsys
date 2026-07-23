"""Template tags module for not rendering blocks when certain apps aren't installed."""

from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def euro(value: Decimal | float) -> str:
    """Format a numerical value as euro's."""
    if not value:
        return "Gratis!"

    if not isinstance(value, (Decimal, float)):
        raise ValueError("The 'euro' filter only accepts Decimal or float values.")

    return f"€ {value:.2f}"
