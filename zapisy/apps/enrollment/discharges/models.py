"""Models for director's discharge requests (wypisy dyrektorskie).

A director discharge allows a student to request unenrollment from a course
after the regular enrollment period has ended. The request requires
administrator approval before the student is removed from all groups in that
course.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from apps.enrollment.records.models.records import Record, RecordStatus
from apps.enrollment.records.signals import GROUP_CHANGE_SIGNAL

if TYPE_CHECKING:
    from apps.enrollment.courses.models.course_instance import CourseInstance
    from apps.enrollment.courses.models.semester import Semester
    from apps.users.models import Student

LOGGER = logging.getLogger(__name__)


class DischargeStatus(models.IntegerChoices):
    PENDING = 0, 'Oczekujący'
    APPROVED = 1, 'Zatwierdzony'
    REJECTED = 2, 'Odrzucony'


class DirectorDischarge(models.Model):
    """A student's request to be discharged from a course by the director.

    Each student has a limited number of such discharges (stored on the
    Student model as `discharge_limit`, default 2) and can use at most one
    per semester.

    Lifecycle:
        PENDING  - student submitted the request, awaiting admin decision
        APPROVED - admin approved; student has been removed from all groups
        REJECTED - admin rejected; student remains enrolled
    """
    student = models.ForeignKey(
        'users.Student',
        on_delete=models.CASCADE,
        related_name='director_discharges',
        verbose_name='Student',
    )
    course = models.ForeignKey(
        'courses.CourseInstance',
        on_delete=models.CASCADE,
        related_name='director_discharges',
        verbose_name='Przedmiot',
    )
    status = models.IntegerField(
        choices=DischargeStatus.choices,
        default=DischargeStatus.PENDING,
        verbose_name='Status',
    )
    admin_comment = models.TextField(
        blank=True,
        verbose_name='Komentarz administratora',
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='decided_discharges',
        verbose_name='Zatwierdził/Odrzucił',
    )
    decided_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data decyzji',
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data złożenia')
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')
        verbose_name = 'Wypis dyrektorski'
        verbose_name_plural = 'Wypisy dyrektorskie'
        ordering = ['-created']

    def __str__(self) -> str:
        return f'Wypis dyrektorski: {self.student} z {self.course}'

    @property
    def is_pending(self) -> bool:
        return self.status == DischargeStatus.PENDING

    @property
    def is_approved(self) -> bool:
        return self.status == DischargeStatus.APPROVED

    @classmethod
    def get_used_total(cls, student: 'Student') -> int:
        """Returns the number of approved director discharges the student has used."""
        return cls.objects.filter(
            student=student,
            status=DischargeStatus.APPROVED,
        ).count()

    @classmethod
    def get_used_in_semester(cls, student: 'Student', semester: 'Semester') -> int:
        """Returns the number of approved director discharges in a given semester."""
        return cls.objects.filter(
            student=student,
            status=DischargeStatus.APPROVED,
            course__semester=semester,
        ).count()

    @classmethod
    def can_request(
        cls,
        student: 'Student',
        course: 'CourseInstance',
        time: datetime | None = None,
    ) -> tuple[bool, str]:
        """Checks whether the student can submit a director discharge request.

        Returns:
            (True, '') if the request is allowed.
            (False, reason) if not, where reason is a human-readable message.

        Conditions (all must be met):
            - student is active
            - student is enrolled (ENROLLED status) in at least one group of the course
            - current time is after semester's records_closing
            - current time is before semester's director_discharge_deadline (if set)
            - no existing PENDING or APPROVED discharge for this (student, course) pair
            - student hasn't exceeded their total discharge_limit
            - student hasn't already used a discharge in this semester (max 1 per semester)
        """
        if time is None:
            time = datetime.now()

        if student is None or not student.is_active:
            return False, 'Konto studenta jest nieaktywne.'

        semester = course.semester

        if semester.records_closing is None or time <= semester.records_closing:
            return False, 'Składanie wniosków jest możliwe dopiero po zamknięciu zapisów.'

        if semester.director_discharge_deadline is not None:
            if time > semester.director_discharge_deadline:
                return False, 'Termin składania wniosków o wypis dyrektorski minął.'

        enrolled = Record.objects.filter(
            student=student,
            group__course=course,
            status=RecordStatus.ENROLLED,
        ).exists()
        if not enrolled:
            return False, 'Nie jesteś zapisany na żadną grupę tego przedmiotu.'

        existing = cls.objects.filter(
            student=student,
            course=course,
            status__in=[DischargeStatus.PENDING, DischargeStatus.APPROVED],
        ).exists()
        if existing:
            return False, 'Wniosek o wypis dyrektorski dla tego przedmiotu już istnieje.'

        used_total = cls.get_used_total(student)
        if used_total >= student.discharge_limit:
            return False, (
                f'Wyczerpano limit wypisów dyrektorskich '
                f'({used_total}/{student.discharge_limit}).'
            )

        existing_in_semester = cls.objects.filter(
            student=student,
            course__semester=semester,
            status__in=[DischargeStatus.PENDING, DischargeStatus.APPROVED],
        ).exists()
        if existing_in_semester:
            return False, 'Możliwy jest tylko jeden wypis dyrektorski w semestrze.'

        return True, ''

    def approve(self, admin_user: User) -> None:
        """Approves the discharge request.

        Removes the student from all enrolled/queued groups of the course,
        bypassing the normal deadline restrictions (admin override).

        Raises:
            ValueError: If the discharge is not in PENDING status.
        """
        if self.status != DischargeStatus.PENDING:
            raise ValueError(
                f'Wniosek nie jest w stanie oczekującym (aktualny status: '
                f'{self.get_status_display()}).'
            )

        records = Record.objects.filter(
            student=self.student,
            group__course=self.course,
        ).exclude(status=RecordStatus.REMOVED)

        affected_group_ids = [record.group_id for record in records]

        # Directly set to REMOVED — bypasses can_dequeue deadline check
        records.update(status=RecordStatus.REMOVED)

        for group_id in affected_group_ids:
            GROUP_CHANGE_SIGNAL.send(None, group_id=group_id)

        self.status = DischargeStatus.APPROVED
        self.decided_by = admin_user
        self.decided_at = datetime.now()
        self.save()

        LOGGER.info(
            'Director discharge approved: student=%s course=%s by=%s',
            self.student, self.course, admin_user,
        )

    def reject(self, admin_user: User, comment: str = '') -> None:
        """Rejects the discharge request.

        The student remains enrolled in their groups.

        Raises:
            ValueError: If the discharge is not in PENDING status.
        """
        if self.status != DischargeStatus.PENDING:
            raise ValueError(
                f'Wniosek nie jest w stanie oczekującym (aktualny status: '
                f'{self.get_status_display()}).'
            )

        self.status = DischargeStatus.REJECTED
        self.decided_by = admin_user
        self.decided_at = datetime.now()
        self.admin_comment = comment
        self.save()

        LOGGER.info(
            'Director discharge rejected: student=%s course=%s by=%s',
            self.student, self.course, admin_user,
        )
