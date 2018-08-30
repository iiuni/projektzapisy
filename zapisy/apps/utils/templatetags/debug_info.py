from functools import lru_cache
import subprocess
import sys

import django
from django import template

register = django.template.Library()


def get_line_from_process(process):
    p = subprocess.Popen(process, stdout=subprocess.PIPE)
    outlines = p.stdout.readlines()
    if len(outlines) < 1:
        return ""
    return outlines[0].decode("utf-8")


@lru_cache(maxsize=1)
def get_debug_info():
    """Queries environment for git commit, python and Django versions.

    The operation is time-consuming, so the result is being cached.
    """
    log_output = get_line_from_process([
        "git", "log", "-n", "1", "--pretty=format:%h %s --- %an %ad"
    ])
    branch_name = get_line_from_process(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    python_info = f'<p>Python <strong>{sys.version}</strong></p>'
    django_info = f'<p>Django <strong>{django.get_version()}</strong></p>'
    git_info = f'<p>{branch_name} {log_output}</p>'
    return f'{python_info}{django_info}{git_info}'


@register.simple_tag
def debug_info():
    """A template tag to return debug info:

    This information is displayed at the bottom of the main page in the debug
    mode.
    """
    return get_debug_info()
