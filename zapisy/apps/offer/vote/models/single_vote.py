from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, models, transaction
from django.db.models.aggregates import Sum

from apps.enrollment.courses.models.course import Course, CourseEntity
from apps.enrollment.courses.models.semester import Semester
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.users.models import Student

from .system_state import SystemState


class SingleVote (models.Model):
    """Student's single vote for a course proposal in an academic cycle (year).
    """
    votes = [(0, '0'), (1, '1'), (2, '2'), (3, '3')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="głosujący")
    entity = models.ForeignKey(CourseEntity, verbose_name='podstawa', on_delete=models.CASCADE)
    proposal = models.ForeignKey(Proposal, verbose_name="propozycja", on_delete=models.CASCADE, null=True)

    state = models.ForeignKey(SystemState, on_delete=models.CASCADE, verbose_name="Rok akademicki")

    value = models.PositiveSmallIntegerField("przyznane punkty", choices=votes, default=0)
    correction = models.PositiveSmallIntegerField(
        "punkty przyznane w korekcie", choices=votes, default=0)

    # The field used to count votes that should not count into the limit.
    free_vote = models.BooleanField(default=False, verbose_name="Głos nie liczy się do limitu")

    class Meta:
        verbose_name = "pojedynczy głos"
        verbose_name_plural = "pojedyncze głosy"
        app_label = 'vote'
        ordering = ('student', 'proposal', '-value')

        unique_together = ('proposal', 'state', 'student')

    def __str__(self):
        return (f"[{self.state.year}] Głos użytkownika: {self.student.user.username}; "
                f"{self.proposal.name}; {self.value}")

