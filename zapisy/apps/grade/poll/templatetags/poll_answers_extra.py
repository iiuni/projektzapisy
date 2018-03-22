from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def as_divs_with_errors(obj, errs):
    return obj.as_divs(errs)


@register.filter
def get_value(obj, key):
    return obj[key]
