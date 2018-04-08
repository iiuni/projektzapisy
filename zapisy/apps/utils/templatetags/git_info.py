"""
A template tag to return git repo info:
The latest's commit hash, message author and date
Displayed at the bottom of the main page if debug is on
"""

from django import template
import subprocess

register = template.Library()

def get_line_from_process(process):
    p = subprocess.Popen(process, stdout=subprocess.PIPE)
    outlines = p.stdout.readlines()
    if len(outlines) < 1:
        return ""
    return outlines[0].decode("utf-8")

@register.simple_tag
def git_info():
    log_output = get_line_from_process([
        "git", "log", "-n", "1",
        "--pretty=format:%h %s --- %an %ad"
    ])
    branch_name = get_line_from_process([
        "git", "rev-parse", "--abbrev-ref", "HEAD"
    ])
    return f'{branch_name} {log_output}'
