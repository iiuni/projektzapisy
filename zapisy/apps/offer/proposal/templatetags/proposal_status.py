from django import template

from apps.offer.proposal.models import ProposalStatus

register = template.Library()


@register.filter
def status_label(status: int) -> str:
    """Returns a lowercase label (const identifier) for a given status code."""
    status = ProposalStatus(status)
    return status._name_.lower()


@register.filter
def status_display(status: int) -> str:
    "Returns a display value of a given status code."
    status = ProposalStatus(status)
    return status.display
