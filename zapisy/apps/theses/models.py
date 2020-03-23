from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from apps.theses.enums import ThesisKind, ThesisStatus, ThesisVote
from apps.theses.users import is_theses_board_member
from apps.theses.validators import validate_master_rejecter, validate_num_required_votes
from apps.users.models import Employee, Student
from apps.notifications.custom_signals import thesis_voting_activated

MAX_THESIS_TITLE_LEN = 300
MAX_REJECTION_REASON_LENGTH = 500
MAX_ASSIGNED_STUDENTS = 2


class ThesesSystemSettings(models.Model):
    """Represents thesis system settings.

    Stores information about required votes to automatically accept
    thesis and master rejecter of theses board.

    There is only one instance of this object. It is created during
    migrations.
    """
    num_required_votes = models.SmallIntegerField(
        verbose_name="Liczba głosów wymaganych do zaakceptowania",
        validators=[validate_num_required_votes]
    )
    master_rejecter = models.ForeignKey(
        Employee, null=True, on_delete=models.PROTECT,
        verbose_name="Członek komisji odpowiedzialny za zwracanie prac do poprawek",
        validators=[validate_master_rejecter]
    )

    def __str__(self):
        return "Ustawienia systemu"

    class Meta:
        verbose_name = "ustawienia systemu prac dyplomowych"
        verbose_name_plural = "ustawienia systemu prac dyplomowych"


class ThesesQuerySet(models.QuerySet):
    def visible(self, user):
        if user.is_staff or is_theses_board_member(user):
            return self
        return self.filter(
            (~Q(status=ThesisStatus.BEING_EVALUATED) & ~Q(status=ThesisStatus.RETURNED_FOR_CORRECTIONS)) |
            Q(advisor__user=user) |
            Q(supporting_advisor__user=user))


class Thesis(models.Model):
    """Represents a thesis in the theses system.

    A Thesis instance can represent a thesis in many different
    configurations (an idea submitted by an employee, a work in progress
    by a student, or a thesis defended years ago). This is accomplished
    through various possible combinations of mainly the 'status' and 'students'
    fields, as described in more detail below.

    A thesis is first added typically by a regular university employee;
    they are then automatically assigned as the advisor.

    Before the thesis can be seen by all employees and students, the theses board
    must first determine whether it is suitable; this is facilitated by the
    voting logic. If the thesis is accepted as submitted,
    its status is then automatically changed to either 'in progress' if the advisor
    has assigned a student, or 'accepted' otherwise.
    """
    title = models.CharField(max_length=MAX_THESIS_TITLE_LEN, unique=True)

    advisor = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True, null=True,
        related_name='thesis_advisor'
    )
    supporting_advisor = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True, null=True,
        related_name='thesis_supporting_advisor'
    )
    kind = models.SmallIntegerField(choices=ThesisKind.choices())
    status = models.SmallIntegerField(
        choices=ThesisStatus.choices(), blank=True, null=True)
    # How long the assigned student(s) has/have to complete their work on this thesis
    # Note that this is only a convenience field for the users, the system
    # does not enforce this in any way
    reserved_until = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(Student, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    # A thesis is _modified_ when its status changes
    modified = models.DateTimeField(auto_now_add=True)
    objects = ThesesQuerySet.as_manager()

    class Meta:
        verbose_name = "praca dyplomowa"
        verbose_name_plural = "prace dyplomowe"

    def save(self, *args, **kwargs):
        """Overloaded save method - during save check changes and send signals to notifications app"""
        old = self.pk and type(self).objects.get(pk=self.pk)
        super(Thesis, self).save(*args, **kwargs)
        if not old or (old.status != ThesisStatus.BEING_EVALUATED and self.status == ThesisStatus.BEING_EVALUATED):
            thesis_voting_activated.send(sender=self.__class__, instance=self)

    def get_accepted_votes(self):
        return len(self.thesis_votes.filter(vote=ThesisVote.ACCEPTED))

    def is_mine(self, user):
        return self.advisor is not None and user == self.advisor.user

    def is_student_assigned(self, user):
        return self.students is not None and self.students.filter(user=user).exists()

    def is_supporting_advisor_assigned(self, user):
        return self.supporting_advisor is not None and user == self.supporting_advisor.user

    @property
    def has_no_students_assigned(self):
        return self.students is not None and not self.students.exists()

    @property
    def is_reserved(self):
        return self.reserved_until and date.today() <= self.reserved_until

    @property
    def has_been_accepted(self):
        return self.status != ThesisStatus.RETURNED_FOR_CORRECTIONS and self.status != ThesisStatus.BEING_EVALUATED

    @property
    def is_voting_active(self):
        return self.status == ThesisStatus.BEING_EVALUATED

    @property
    def is_returned(self):
        return self.status == ThesisStatus.RETURNED_FOR_CORRECTIONS


class Remark(models.Model):
    """Represents a remark in theses system.

    Remarks are text notes that theses board member can add to any
    evaluated or rejected thesis. Remarks can be seen by board members
    and thesis advisors.
    """
    modified = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="remark_author")
    text = models.TextField(blank=True)
    thesis = models.ForeignKey(
        Thesis, on_delete=models.CASCADE, blank=True, related_name="thesis_remarks")

    class Meta:
        verbose_name = "uwaga"
        verbose_name_plural = "uwagi"


class Vote(models.Model):
    """Represents vote in theses system.

    Votes are used in thesis voting logic system. Any board member
    can cast a vote when thesis has __being_evaluated__ status.
    Particular vote can have three possible values: __accept__,
    __reject__ and __none__.

    Votes can be seen by all board members and thesis advisor.
    """
    owner = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="vote_owner")
    vote = models.SmallIntegerField(choices=ThesisVote.choices())
    thesis = models.ForeignKey(
        Thesis, on_delete=models.CASCADE, blank=True, related_name="thesis_votes")

    class Meta:
        verbose_name = "głos"
        verbose_name_plural = "głosy"
