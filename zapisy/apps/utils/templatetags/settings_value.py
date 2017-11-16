"""
Allows templates to access constants
defined in settings.py. Credit goes
to Berislav Lopac@stackoverflow
https://stackoverflow.com/a/7716141
"""

from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")
