"""
A template tag that determines whether debug information
should be displayed (locally or on the staging server)
"""

from django import template
from django.conf import settings
import os

register = template.Library()


@register.simple_tag
def should_display_debug():
    return (
        getattr(settings, "DEBUG", False) or     # local debug mode
        os.path.exists("/etc/ii_zapisy_staging") # staging server
    )
