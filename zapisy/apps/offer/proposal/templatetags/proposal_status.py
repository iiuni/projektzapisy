from django import template

from apps.offer.proposal.models import ProposalStatus, SemesterChoices

register = template.Library()


@register.filter
def status_label(status: int) -> str:
    """Returns a lowercase label (const identifier) for a given status code."""
    status = ProposalStatus(status)
    return status._name_.lower()


@register.filter
def semester_display(semester: SemesterChoices) -> str:
    """Returns a display value of a SemesterChoices enum."""
    semester = SemesterChoices(semester)
    return semester.label


@register.filter
def semester_order(proposals):
    """Arranges semesters in order in which they actually occur."""
    ordering = {
        SemesterChoices.WINTER: 1,
        SemesterChoices.SUMMER: 2,
        SemesterChoices.UNASSIGNED: 3
    }
    return sorted(proposals, key=lambda p: ordering[p.semester])
