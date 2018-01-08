"""
Allows templates to access OS environment vars.
"""

from django import template
import os

register = template.Library()

@register.filter
def osenv_value(name):
    return os.environ.get(name)
