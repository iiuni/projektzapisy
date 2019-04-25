from django.db import models

from apps.enrollment.courses.models.course import CourseEntity
from apps.enrollment.courses.models.course_information import SemesterChoices
from apps.enrollment.courses.models import Semester
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.users.models import Student

from .system_state import SystemState


class SingleVoteQuerySet(models.QuerySet):
    def in_semester(self, semester: Semester):
        """Filters only votes for courses taught in a given semester.

        NOTE: This function will need to be modified when CourseEntity is
        fully replaced with proposal model.
        """
        return self.filter(entity__course__semester=semester)


class SingleVote(models.Model):
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

    objects = SingleVoteQuerySet.as_manager()

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

    @staticmethod
    def create_missing_votes(student: Student, state: SystemState):
        """Creates vote objects for a student.

        Only missing vote objects are created. This is useful, because we may
        call this function multiple times for one student during the vote. It
        might add objects on subsequent runs and proposal might be included in
        the voting during the vote.
        """
        existing_votes = SingleVote.objects.filter(student=student,
                                                   state=state).values_list('proposal_id',
                                                                            flat=True)
        existing_votes = set(existing_votes)
        proposals = Proposal.objects.filter(status=ProposalStatus.IN_VOTE)
        new_votes = []
        for proposal in proposals:
            if proposal.pk not in existing_votes:
                new_votes.append(
                    SingleVote(student=student,
                               state=state,
                               proposal=proposal,
                               entity=proposal.entity))
        SingleVote.objects.bulk_create(new_votes)
