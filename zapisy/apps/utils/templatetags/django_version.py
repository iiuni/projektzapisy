"""
Allows templates to access the Django version.
"""

from django import template
import django

register = template.Library()


@register.simple_tag
def django_version():
    return django.get_version()
