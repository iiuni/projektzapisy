from datetime import datetime
import logging
from typing import Dict, List, Optional

from apps.enrollment.courses.models import Group
from apps.enrollment.records.signals import GROUP_CHANGE_SIGNAL
from apps.enrollment.records.models.records import Record, RecordStatus
from apps.users.models import Student
from apps.enrollment.records.engine.checks import is_recorded_in_groups

LOGGER = logging.getLogger(__name__)


def remove_from_group(student: Student, group: Group) -> bool:
    """Removes the student from the group.

    The student can only leave the group before unenrolling deadline,
    and can only leave the queue until the end of enrolling period.

    The function triggers further actions, so another student will be pulled
    into the group as there is a vacancy caused by the student's departure.

    If ECTS limit is set to initial value and the student has status ENROLLED
    in this group,  his records in all gropus change status to QUEUED
    and triger accion will be emitted to fill this groups.

    Returns:
        bool: Whether the removal was successfull.
    """
    if not can_dequeue(student, group):
        return False
    try:
        record = (
            Record.objects.filter(student=student, group=group)
            .exclude(status=RecordStatus.REMOVED)
            .select_related('group__course__semester')
            .get()
        )
    except Record.DoesNotExist:
        return False

    was_enrolled = record.status == RecordStatus.ENROLLED
    record.status = RecordStatus.REMOVED
    record.save()

    # Emit triger action to fillup student in queues where is blocked
    if record.group.course.semester.is_initial_limit() and was_enrolled:
        records = (
            Record.objects.filter(student=student, status=RecordStatus.BLOCKED)
            .select_related('group')
        )
        for record in records:
            GROUP_CHANGE_SIGNAL.send(None, group_id=record.group.pk)
        records.update(status=RecordStatus.QUEUED)

    LOGGER.info('User %s removed from group %s', student, group)
    GROUP_CHANGE_SIGNAL.send(None, group_id=record.group_id)
    return True


def can_dequeue(student: Optional[Student], group: Group, time: datetime = None) -> bool:
    """Checks if the student can leave the group or its queue.

    This function will return False if student is None. It will not check
    for student's presence in the group. The function's role is to verify
    legal constraints.
    """
    return can_dequeue_groups(student, [group], time)[group.pk]


def can_dequeue_groups(student: Optional[Student], groups: List[Group],
                       time: datetime = None) -> Dict[int, bool]:
    """Checks which of the groups the student can leave (or leave their queues).

    It is preferable to call this function rather than
    :func:`~apps.enrollment.records.models.Record.can_dequeue` multiple
    times to save on database queries. The groups should contain .course and
    .course.semester.

    If student is None, the function will return all False values. It does
    not check for student's presence in the groups.
    """
    if time is None:
        time = datetime.now()
    if student is None or not student.is_active:
        return {g.pk: False for g in groups}
    ret = {}
    groups = is_recorded_in_groups(student, groups)
    for group in groups:
        if group.auto_enrollment:
            ret[group.pk] = False
        elif group.course.records_end is not None:
            ret[group.pk] = time <= group.course.records_end
        elif not group.course.semester.can_remove_record(time):
            # When disenrolment is closed, QUEUED record can still be
            # removed, ENROLLED may not.
            ret[group.pk] = getattr(group, 'is_enqueued', False)
        else:
            ret[group.pk] = True
    return ret
