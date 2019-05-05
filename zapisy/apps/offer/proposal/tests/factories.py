from apps.enrollment.courses.tests.factories import CourseInformationFactory
from apps.offer.proposal.models import Proposal

__all__ = ['ProposalFactory', ]


class ProposalFactory(CourseInformationFactory):
    """Creates a new Proposal instance."""
    class Meta:
        model = Proposal
