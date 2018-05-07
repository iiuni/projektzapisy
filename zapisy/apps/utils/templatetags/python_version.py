"""
Allows templates to access the Python version.
"""
import sys

from django import template

register = template.Library()


@register.simple_tag
def python_version():
    return sys.version
