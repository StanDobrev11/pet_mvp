from django import template
from django.db.models import Model, QuerySet

register = template.Library()

@register.filter
def ensure_iterable(value):
    """
    Ensures that a value is iterable (returns a list or queryset).
    - If it's already a QuerySet, return it as is
    - If it's a single Model instance, wrap it in a list
    - If it's None, return empty list
    - Otherwise, try to return it as is (assuming it's iterable)
    """
    if value is None:
        return []
    elif isinstance(value, QuerySet):
        return value
    elif isinstance(value, Model):
        return [value]
    else:
        try:
            iter(value)
            return value
        except TypeError:
            return [value]