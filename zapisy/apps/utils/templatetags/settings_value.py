"""
Allows templates to access constants
defined in settings.py. Credit goes
to Berislav Lopac@stackoverflow
https://stackoverflow.com/a/7716141
We've changed it to a filter because Django's
parser doesn't handle template tags well
"""

from django import template
from django.conf import settings

register = template.Library()


@register.filter
def settings_value(name):
    return getattr(settings, name, "")
