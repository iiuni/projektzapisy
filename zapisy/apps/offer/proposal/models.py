import choicesenum
from django.db import models

from apps.enrollment.courses.models.course_information import CourseInformation


class SemesterChoices(choicesenum.ChoicesEnum):
    UNASSIGNED = 'u', "nieokreślony"
    WINTER = 'z', "zimowy"
    SUMMER = 'l', "letni"


class ProposalStatus(choicesenum.ChoicesEnum):
    PROPOSAL = 0, "propozycja"
    IN_OFFER = 1, "w ofercie"
    IN_VOTE = 2, "poddana pod głosowanie"
    WITHDRAWN = 4, "wycofana z oferty"
    CORRECTIONS_REQUIRED = 5, "do poprawienia"
    DRAFT = 6, "szkic"


class Proposal(CourseInformation):
    """Models course proposal.

    A proposal is added by an employee. Its initial status is DRAFT. The author
    can promote it to PROPOSAL. Teaching head can change the status further.
    """

    status = models.PositiveSmallIntegerField(
        "status propozycji", choices=ProposalStatus.choices(), default=ProposalStatus.DRAFT)
    semester = models.CharField(
        "semestr",
        choices=SemesterChoices.choices(),
        max_length=1,
        default=SemesterChoices.UNASSIGNED)

    class Meta:
        verbose_name = "propozycja przedmiotu"
        verbose_name_plural = "propozycje przedmiotu"

    def __copy__(self):
        """Clones a proposal.

        Only the fields that are supposed to be input by the employee are
        copied. Name of the clone will indicate that it is indeed a clone.
        """
        copy = super().__copy__()

        # Zeroes the fields that are invisible for employee.
        copy.owner = None
        copy.short_name = None
        copy.teaching_unit = None
        copy.major = None
        copy.level = None
        copy.year = None

        # Resets the status back to default.
        copy.status = ProposalStatus.DRAFT

        copy.name = "Klon: " + copy.name
        if copy.name_en:
            copy.name_en = "Clone: " + copy.name_en

        return copy
