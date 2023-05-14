"""Module records is the heart of enrollment logic.

Record Lifetime:

  The record's status transitions in one direction: QUEUED -> ENROLLED ->
  REMOVED. The ENROLLED phase may be skipped if the student removes his record
  while he is in the queue, or if the enrollment is unsuccessful. The REMOVED
  phase may not occur if the student ends up being enrolled into the group.

  enqueue_student(student, group): The life of a record begins with this
    function, which puts the student into the queue of the group. The record
    will not be created if the function `can_enqueue` does not pass.

    Immediately after records are created, an asynchronous task is placed (in
    the task queue), to pull as many records in these groups as possible from
    their respective queues. The tasks are placed using a signal
    (GROUP_CHANGE_SIGNAL) defined in `apps/enrollment/records/signals.py`. They
    are picked up by the function `pull_from_queue_signal_receiver` in
    `apps/enrollment/records/tasks.py`.

  fill_group(group_id): The asynchronous task runs this function. It is a loop
    calling `pull_record_into_group` as long as it returns True, which means
    that there still place in the group and students in the queue.

  pull_record_into_group(group_id): Picks the first student in the group's queue
    and tries to enroll him in the group using `enroll_or_remove`.

  enroll_or_remove(record): Takes the record and tries to change its status from
    QUEUED to ENROLLED. This operation will be unsuccessful if the function
    `can_enroll` does not pass, in which case the record's status will be
    changed to REMOVED. This function additionally removes the student from all
    the parallel groups upon enrolling him into this one, and removes him from
    all the queues of lower priority.

  remove_from_group(student, group): Removes student from the group or its
    queue, thus changing the record's status to REMOVED. All the groups that are
    vacated by the student must be filled by an asynchronous process, so the
    GROUP_CHANGE_SIGNAL is sent.
"""

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
