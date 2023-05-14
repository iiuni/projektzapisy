from datetime import datetime
import logging
from typing import Dict, List, Tuple

from django.db import DatabaseError, models, transaction

from apps.enrollment.courses.models import Group
from apps.enrollment.courses.models.group import GuaranteedSpots
from apps.enrollment.records.signals import GROUP_CHANGE_SIGNAL
from apps.notifications.custom_signals import student_not_pulled, student_pulled
from apps.enrollment.records.models.records import Record, RecordStatus, CanEnroll
from apps.enrollment.records.engine.enqueue import can_enroll

LOGGER = logging.getLogger(__name__)


def fill_group(group_id: int):
    """Pulls records from the queue into the group as long as possible.

    This function may raise a DatabaseError when too many transaction errors
    occur.
    """
    from apps.enrollment.records.models.opening_times import GroupOpeningTimes
    num_transaction_errors = 0
    group = Group.objects.select_related('course', 'course__semester').get(id=group_id)
    can_enroll = GroupOpeningTimes.is_enrollment_open(group.course, datetime.now())
    if can_enroll:
        while num_transaction_errors <= 3:
            try:
                pull_records_into_group(group)
            except DatabaseError:
                # Transaction failure probably means that Postgres decided to
                # terminate the transaction in order to eliminate a deadlock. We
                # will want to retry then. It would not however be responsible
                # to retry too many times and obscure some real error.
                num_transaction_errors += 1
                if num_transaction_errors == 3:
                    raise
            else:
                break


@transaction.atomic()
def pull_records_into_group(group: Group):
    """Checks for vacancies and pulls first student from queue if possible.

    If there is free spot in the group, this function will pick the first
    record from the queue and try to enroll it into the group. The first
    record may be removed if the student is not eligible for enrollment.

    Returns:
        The function will return False if the group is already full, or the
        queue is empty or the enrollment is closed for the semester. True
        value will mean, that it should be run again on that group. The
        function may throw DatabaseError if transaction fails.

    Concurrency:
        This function may be run concurrently. A data race could potentially
        lead to number of students enrolled exceeding the limit. It therefore
        needs to be atomic. A lock is hence obtained on all the records in the
        same group. This way only one instance of this function can operate on
        the same group at the same time (the second instance will have to wait
        for the lock to be released). We optimistically assume that the group
        limit is not going to change while the function is executing and do
        not obtain a lock on the group in the database.
    """
    # Groups that will need to be pulled into afterwards.
    trigger_groups = set()

    # We obtain a lock on the records in this group.
    records = Record.objects.filter(
        group=group,
        status__in=[RecordStatus.ENROLLED, RecordStatus.QUEUED],
        ).select_for_update()
    free_spots = free_spots_by_role(group)

    for role in sorted(free_spots, reverse=True):
        i = 0
        while (i < free_spots[role]):
            queue_query = records.filter(status=RecordStatus.QUEUED)
            if role != '-':
                queue_query = queue_query.filter(student__user__groups__name=role)
            try:
                first_in_line = queue_query.select_related("group").earliest('created')
            except Record.DoesNotExist:
                break
            (is_enrolded, new_trigger_groups) = enroll_student(first_in_line)
            if is_enrolded:
                i = i + 1
                trigger_groups.update(new_trigger_groups)

    # The tasks should be triggered outside of the transaction
    for trigger_group_id in trigger_groups:
        GROUP_CHANGE_SIGNAL.send(None, group_id=trigger_group_id)
    return False


def free_spots_by_role(group: Group) -> Dict[str, int]:
    """Counts the number of free spots indexed by user role.

    The purpose of this is to establish if the group has free place in it at
    all and how many students are enrolled according to which
    GuaranteedSpots rule. Note, that this function will only work
    deterministically and sanely, if the roles defined in GuaranteedSpots
    rules are distinct for this groups.

    The number of students not matched to any GuaranteedSpots rule will be
    indexed with '-'.
    """
    ret: Dict[str, int] = {}
    guaranteed_spots_rules = GuaranteedSpots.objects.filter(group=group)
    all_enrolled_records = Record.objects.filter(
        group=group, status=RecordStatus.ENROLLED).select_related(
            'student', 'student__user').prefetch_related('student__user__groups')
    all_enrolled_students = set(r.student.user for r in all_enrolled_records)

    for gsr in guaranteed_spots_rules:
        role = gsr.role
        counter = 0
        for user in all_enrolled_students.copy():
            if role in user.groups.all():
                all_enrolled_students.remove(user)
                counter += 1
                if counter == gsr.limit:
                    break
        ret[gsr.role.name] = gsr.limit - counter
    ret['-'] = group.limit - len(all_enrolled_students)
    return ret


@transaction.atomic
def enroll_student(record: Record) -> Tuple[bool, List[int]]:
    """Tries to change a single QUEUED record status to ENROLLED.

    The operation might fail under certain circumstances:
    when enrolling wouldexceed his ECTS limit,
        then record change status to BLOCKED.
    In other cases record change statust to REMOVED.

    The return value is a Tuple: (is_enrolded, trigger_groups)
    * is_enrolded is Tru when record chage status to ENROLLED
    * trigger_groups is set of group ids that need to be
        triggered (pulled from).

    The function may raise a DatabaseError if transaction fails
    (it might happen in a deadlock situation or when any
    exception is raised in running of this function).

    Concurrency:
        The function may be run concurrently. A data race might potentially
        lead to a student breaching ECTS limit. To prevent that a lock is
        obtained on all records of this student. This way, no other instance
        of this function will try to pull him into another group at the same
        time.
    """
    records = Record.objects.filter(student=record.student).exclude(
        status=RecordStatus.REMOVED).select_for_update()

    # Check if he can be enrolled at all.
    can_be_enrolled = can_enroll(record.student, record.group)
    if not can_be_enrolled:
        if can_be_enrolled == CanEnroll.ECTS_LIMIT:
            record.status = RecordStatus.BLOCKED
        else:
            record.status = RecordStatus.REMOVED

        # Send notifications
        student_not_pulled.send_robust(
            sender=record.__class__,
            instance=record.group,
            user=record.student.user,
            reason=can_be_enrolled.value)

        record.save()

        return (False, [])

    # Remove him from all parallel groups (and queues of lower
    # priority). These groups need to be afterwards pulled into
    # (triggered).
    other_groups_query = records.filter(
        group__course=record.group.course,
        group__type=record.group.type).exclude(pk=record.pk).filter(
            models.Q(priority__lt=record.priority) | models.Q(status=RecordStatus.ENROLLED))

    # The list of groups to trigger must be computed now, after the
    # update it would be empty. Note that this list should have at most
    # one element.
    other_groups_query_list = set(
        other_groups_query.filter(status=RecordStatus.ENROLLED).values_list(
            'group_id', flat=True))
    other_groups_query.update(status=RecordStatus.REMOVED)
    record.status = RecordStatus.ENROLLED
    record.save()

    # Send notification to user
    student_pulled.send_robust(
        sender=record.__class__, instance=record.group, user=record.student.user)
    return (True, other_groups_query_list)


@transaction.atomic()
def process_ects_limit_change():
    """Unlock BLOCKED records.

    Function change all BLOCKED records to QUEUED
    and send GROUP_CHANGE_SIGNAL to all groups where was any blocked record.

    Attention:
        This function will cause heavy load on the server,
        so it should be used with care when the load is least
    """
    records = Record.objects.filter(
        status=RecordStatus.BLOCKED,
        ).select_for_update()

    groups = Group.objects.filter(record__status=RecordStatus.BLOCKED)

    for group in groups:
        GROUP_CHANGE_SIGNAL.send(None, group_id=group.pk)

    records.update(status=RecordStatus.QUEUED)
