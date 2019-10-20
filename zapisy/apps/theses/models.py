from typing import NamedTuple, Iterable
from datetime import datetime

from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User

from apps.users.models import Employee, Student
from .validators import validate_num_required_votes, validate_master_rejecter
from .system_settings import get_num_required_votes
from .users import is_theses_admin
from .notifications import (
    notify_thesis_accepted, notify_thesis_rejected,
    notify_rejecting_vote_cast
)

from .enums import ThesisKind, ThesisStatus, ThesisVote
from .managers import APIManager

MAX_THESIS_TITLE_LEN = 300
MIN_REJECTION_REASON_LENGTH = 100
MAX_REJECTION_REASON_LENGTH = 500


class VoteToProcess(NamedTuple):
    voter: Employee
    value: ThesisVote
    # if rejecting
    reason: str


VotesToProcess = Iterable[VoteToProcess]


class Thesis(models.Model):
    """Represents a thesis in the theses system.

    A Thesis instance can represent a thesis in many different
    configurations (an idea submitted by an employee, a work in progress
    by a student, or a thesis defended years ago). This is accomplished
    through various possible combinations of mainly the 'status' and 'students'
    fields, as described in more detail below.

    A thesis is first added typically by a regular university employee;
    they are then automatically assigned as the advisor.

    Before the thesis can be assigned to a student, the theses board
    must first determine whether it is suitable; this is facilitated by the
    voting logic. If the thesis is accepted as submitted,
    its status is then automatically changed to either 'in progress' if the advisor
    has assigned a student, or 'accepted' otherwise.
    The advisor is then permitted to change its status to 'archived'
    after the student completes and presents it.
    """

    objects = models.Manager()
    rest_objects = APIManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Save the status so that, when saving, we can determine whether or not it changed
        # See https://stackoverflow.com/a/1793323
        # If pk is None, we are creating this model, so don't save the status
        self.__original_status = self.status if self.pk is not None else None

    title = models.CharField(max_length=MAX_THESIS_TITLE_LEN, unique=True)
    # the related_name's below are necessary because we have multiple foreign keys pointing
    # to the same model and Django isn't smart enough to generate unique reverse accessors
    advisor = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True, null=True,
        related_name='thesis_advisor'
    )
    supporting_advisor = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True, null=True,
        related_name='thesis_supporting_advisor'
    )
    kind = models.SmallIntegerField(choices=ThesisKind.choices())
    status = models.SmallIntegerField(choices=ThesisStatus.choices())
    # How long the assigned student(s) has/have to complete their work on this thesis
    # Note that this is only a convenience field for the users, the system
    # does not enforce this in any way
    reserved_until = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    students = models.ManyToManyField(Student, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    # A thesis is _modified_ when its status changes
    modified = models.DateTimeField(auto_now_add=True)
    # The "official" rejection reason, filled out by the rejecter
    rejection_reason = models.TextField(blank=True)

    def on_title_changed_by(self, user: User):
        if self.advisor is not None and self.advisor.user == user and not is_theses_admin(user):
            self.votes.all().delete()
            self.status = ThesisStatus.BEING_EVALUATED
            self.save()

    def process_new_votes(
        self, votes: VotesToProcess, changing_user: User, should_update_status: True
    ):
        """Whenever one or more votes for a thesis change, this function
        should be called to process & save them

        Arguments:

        changing_user -- The user who's causing the change of votes;
        if they're not changing their own vote, thesis status will not be updated
        (based on the assumption that they're simply adjusting the votes of some
        other voters and don't actually want it to count)

        should_update_status -- Whether the status should be updated based on vote
        counts (only if the condition above holds)
        """
        had_vote_as_self = False
        self_rejecting_vote = None
        for vote in votes:
            if vote.voter.user == changing_user:
                had_vote_as_self = True
                if vote.value == ThesisVote.REJECTED:
                    self_rejecting_vote = vote
            self.votes.update_or_create(
                voter=vote.voter,
                defaults={
                    "value": vote.value.value,
                    "reason": vote.reason if vote.value == ThesisVote.REJECTED else ""
                }
            )
        if had_vote_as_self and should_update_status:
            self.check_for_vote_status_change()
        if self_rejecting_vote:
            notify_rejecting_vote_cast(self, changing_user, self_rejecting_vote.reason)

    def check_for_vote_status_change(self):
        """If we have enough approving votes, accept this thesis
        Only do this if it's still being evaluated; board members can cast
        votes when it's rejected, but that doesn't change anything
        """
        if (
            self.status == ThesisStatus.BEING_EVALUATED and
            self.get_approve_votes_cnt() >= get_num_required_votes()
        ):
            self.status = ThesisStatus.ACCEPTED
            self.save()

    def get_approve_votes_cnt(self):
        return self.votes.filter(value=ThesisVote.ACCEPTED).count()

    def is_archived(self):
        return self.status == ThesisStatus.DEFENDED

    def has_any_students_assigned(self):
        """Check if this thesis has any students assigned.

        NOTICE: this will query the DB. For processing multiple theses,
        you should annotate each object instead.
        """
        return self.students.all().exists()

    def get_students(self):
        """Get all the students assigned to this thesis."""
        return self.students.all()

    def set_students(self, students):
        """Given an interable of students, assign them as to this thesis."""
        self.students.set(students)

    def __str__(self) -> str:
        return self.title

    def clean(self):
        """Ensure that the title never contains superfluous whitespace"""
        self.title = self.title.strip()

    def _adjust_status(self):
        """If there is at least one student and the thesis has been accepted,
        we automatically move it to "in progress"; conversely,
        if it was in progress but the students have been removed, go back to accepted
        """
        current_status = ThesisStatus(self.status)
        has_students = self.has_any_students_assigned()
        if current_status == ThesisStatus.ACCEPTED and has_students:
            self.status = ThesisStatus.IN_PROGRESS
        elif current_status == ThesisStatus.IN_PROGRESS and not has_students:
            self.status = ThesisStatus.ACCEPTED
        if self.status != self.__original_status:
            # If the status changed, update modified date
            self.modified = datetime.now()
            self.__original_status = self.status
            self.notify_on_status_change()

    def save(self, *args, **kwargs):
        self.full_clean()
        skip = kwargs.pop("skip_status_update", False)
        if self.id and not skip:
            self._adjust_status()
        super().save(*args, **kwargs)

    def notify_on_status_change(self):
        old_status = ThesisStatus(self.__original_status) if self.__original_status else None
        new_status = ThesisStatus(self.status)
        # it could jump straight to in progress if there is a student defined already
        newly_accepted_statuses = (ThesisStatus.ACCEPTED, ThesisStatus.IN_PROGRESS)
        nonaccepted_statuses = (ThesisStatus.BEING_EVALUATED, ThesisStatus.RETURNED_FOR_CORRECTIONS)
        if (new_status in newly_accepted_statuses and old_status in nonaccepted_statuses):
            notify_thesis_accepted(self)
        elif new_status == ThesisStatus.RETURNED_FOR_CORRECTIONS:
            notify_thesis_rejected(self)

    class Meta:
        verbose_name = "praca dyplomowa"
        verbose_name_plural = "prace dyplomowe"


@receiver(m2m_changed, sender=Thesis.students.through)
def thesis_students_changed(sender, **kwargs):
    """After the `students` field changes for a thesis,
    we should adjust the status according to the logic defined in
    `Thesis._adjust_status`.

    This has to be done via a signal because m2m relationships are not
    usable until all objects have been saved to the DB and have IDs available
    for use, so doing this in save() would not be enough: for instance,
    a new thesis is created, its save() method runs, no students are yet
    defined, so its status is set to accepted. Only after the save()
    method exits, the students can be defined, but this is not picked up
    by the save method since it's not run again.

    However: we still need to update the status in save() because
    theoretically, this may need to be done even without any changes
    to the `students` field: the advisor may change the status to 'accepted'
    with some students already defined, at which point we should immediately
    move it to 'in progress'
    """
    instance = kwargs["instance"]
    instance._adjust_status()
    instance.save(skip_status_update=True)


def vote_to_string(vote_value: int) -> str:
    for value, vote_string in ThesisVote.choices():
        if value == vote_value:
            return vote_string
    return ""


class ThesisVoteBinding(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name="votes")
    voter = models.ForeignKey(Employee, on_delete=models.PROTECT)
    value = models.SmallIntegerField(choices=ThesisVote.choices())
    # Usually only filled out if the value is 'rejected'
    reason = models.CharField(max_length=MAX_REJECTION_REASON_LENGTH, blank=True)

    def __str__(self) -> str:
        return f'Głos {self.voter} na {self.thesis} - {vote_to_string(self.value)}'


def get_num_ungraded_for_emp(voter: User) -> int:
    """Get the number of ungraded theses for the given employee"""
    return Thesis.rest_objects.get_queryset().filter_only_ungraded(voter).count()


class ThesesSystemSettings(models.Model):
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
