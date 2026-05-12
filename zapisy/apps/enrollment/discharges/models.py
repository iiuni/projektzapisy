"""Models for director's discharge requests (wypisy dyrektorskie).

A director discharge allows a student to request unenrollment from a course
after the regular enrollment period has ended. The request requires
administrator approval before the student is removed from all groups in that
course.
"""

from django.conf import settings
from django.db import models


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

    def __str__(self):
        return f'Wypis dyrektorski: {self.student} z {self.course}'

    @property
    def is_pending(self):
        return self.status == DischargeStatus.PENDING

    @property
    def is_approved(self):
        return self.status == DischargeStatus.APPROVED
