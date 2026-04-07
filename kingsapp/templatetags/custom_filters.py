from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return Decimal(value) * Decimal(arg)
    except (ValueError, TypeError, Decimal.InvalidOperation):
        return 0

@register.filter(name='sub')
def sub(value, arg):
    """Subtracts the arg from the value."""
    try:
        return Decimal(value) - Decimal(arg)
    except (ValueError, TypeError, Decimal.InvalidOperation):
        return 0