from apps.enrollment.courses.tests import factories as courses_factories
from apps.offer.proposal.models import Proposal

__all__ = ['ProposalFactory', ]


class ProposalFactory(courses_factories.CourseInformationFactory):
    """Creates a new Proposal instance."""
    class Meta:
        model = Proposal
