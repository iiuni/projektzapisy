from django import template

from apps.offer.proposal.models import SemesterChoices

register = template.Library()


@register.filter
def semester_order(proposals):
    """Arranges semesters in order in which they actually occur."""
    ordering = {
        SemesterChoices.WINTER: 1,
        SemesterChoices.SUMMER: 2,
        SemesterChoices.UNASSIGNED: 3
    }
    return sorted(proposals, key=lambda p: ordering[p.semester])
