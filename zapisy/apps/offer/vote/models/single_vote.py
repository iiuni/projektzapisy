from django.db import models

from apps.enrollment.courses.models.course import CourseEntity
from apps.enrollment.courses.models.course_information import SemesterChoices
from apps.offer.proposal.models import Proposal
from apps.users.models import Student

from .system_state import SystemState


class SingleVote (models.Model):
    """Student's single vote for a course proposal in an academic cycle (year).
    """
    VALUE_CHOICES = [(0, '0'), (1, '1'), (2, '2'), (3, '3')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="głosujący")
    entity = models.ForeignKey(CourseEntity, verbose_name='podstawa', on_delete=models.CASCADE)
    proposal = models.ForeignKey(
        Proposal, verbose_name="propozycja", on_delete=models.CASCADE, null=True)

    state = models.ForeignKey(SystemState, on_delete=models.CASCADE, verbose_name="Rok akademicki")

    value = models.PositiveSmallIntegerField("przyznane punkty", choices=VALUE_CHOICES, default=0)
    correction = models.PositiveSmallIntegerField(
        "punkty przyznane w korekcie", choices=VALUE_CHOICES, default=0)

    class Meta:
        verbose_name = "pojedynczy głos"
        verbose_name_plural = "pojedyncze głosy"
        app_label = 'vote'
        ordering = ('student', 'proposal', '-value')

        unique_together = ('proposal', 'state', 'student')

    def __str__(self):
        return (f"[{self.state.year}] Głos użytkownika: {self.student.user.username}; "
                f"{self.proposal.name}; {self.value}")

    @staticmethod
    def points_for_semester(student: Student, state: SystemState, semester: SemesterChoices):
        pass
