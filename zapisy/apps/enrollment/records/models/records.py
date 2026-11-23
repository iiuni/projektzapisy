"""All enrollment login was moved to engine module."""

import logging
from enum import Enum

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.enrollment.courses.models import Group
from apps.users.models import Student

LOGGER = logging.getLogger(__name__)


class RecordStatus(models.IntegerChoices):
    """RecordStatus describes a lifetime of a record."""
    QUEUED = 0
    ENROLLED = 1
    REMOVED = 2
    BLOCKED = 3


class CanEnroll(Enum):
    OK = "(zapis dozwolony)"
    ECTS_LIMIT = "Przekroczony limit ECTS"
    CANNOT_QUEUE = "Grupa nie otwarta dla studenta"
    OTHER = "Błąd programistyczny"

    def __bool__(self):
        return self == self.OK


class Record(models.Model):
    """Record is a tie between a student and a group.

    Once the student signs up for the course or its queue, the record is
    created. It must not be ever removed. When the student is removed from the
    group or its queue, the record status should be changed.
    """
    group = models.ForeignKey(Group, verbose_name='grupa', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.IntegerField(choices=RecordStatus.choices)
    priority = models.IntegerField(
        verbose_name='priorytet',
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
