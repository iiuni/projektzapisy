"""Module records is the heart of enrollment logic.

The entry point to signing up for a course group is the function
enqueue_student. It creates the record with status QUEUED. Then the record might
transfer into ENROLLED, if all the conditions for enrolling are satisfied.
Ultimately the record can be removed, either on student leaving the group or an
unsuccessful enrollment.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from choicesenum import ChoicesEnum
from django.db import DatabaseError, models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.enrollment.courses.models import Group, StudentPointsView, Semester
from apps.enrollment.records.models.opening_times import GroupOpeningTimes
from apps.enrollment.records.signals import GROUP_CHANGE_SIGNAL
from apps.users.models import Student

LOGGER = logging.getLogger(__name__)


class RecordStatus(ChoicesEnum):
    """RecordStatus describes a lifetime of a record."""
    QUEUED = '0'
    ENROLLED = '1'
    REMOVED = '2'


class Record(models.Model):
    """Record is a tie between a student and a group.

    Once the student signs up for the course or its queue, the record is
    created. It must not be ever removed. When the student is removed from the
    group or its queue, the record status should be changed.
    """
    group = models.ForeignKey(Group, verbose_name='grupa', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=RecordStatus.choices())
    priority = models.IntegerField(
        verbose_name='priorytet',
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @staticmethod
    def can_enqueue(student: Optional[Student], group: Group, time: datetime = None) -> bool:
        """Checks if the student can join the queue of the group.

        Will return False if student is None. The function will not check if the
        student already belongs to the queue.
        """
        if time is None:
            time = datetime.now()
        if student is None:
            return False
        if not GroupOpeningTimes.is_group_open_for_student(student, group, time):
            return False
        return True

    @staticmethod
    def can_enqueue_groups(student: Optional[Student], groups: List[Group],
                           time: datetime = None) -> Dict[int, bool]:
        """Checks if the student can join the queues of respective course groups.

        For given groups, the function will return a dict representing groups
        associated with that course. For every group primary key the return
        value will tell, if the student can enqueue into the group. It will
        return all False values if student is None. It is not checking if the
        student is already present in the groups.

        This function should be called instead of multiple calls to the
        :func:`~apps.enrollment.records.models.Record.can_enqueue` function to
        save on DB queries.
        """
        if time is None:
            time = datetime.now()
        if student is None:
            return {k.id: False for k in groups}
        return GroupOpeningTimes.are_groups_open_for_student(student, groups, time)

    @classmethod
    def can_enroll(cls, student: Optional[Student], group: Group, time: datetime = None) -> bool:
        """Checks if the student can join the queue of the group.

        At the point the function is purely cosmetic. Some conditions may be
        added in future. Will return False if student is None. The function will
        not check if the student is already enrolled into the group or present
        in its queue.
        """
        if time is None:
            time = datetime.now()
        if student is None:
            return False
        if not cls.can_enqueue(student, group, time):
            return False
        # Check if enrolling would not make the student exceed the current ECTS
        # limit.
        semester: Semester = group.course.semester
        points = StudentPointsView.student_points_in_semester_with_added_courses(
            student, semester, [group.course])
        if points > semester.get_current_limit(time):
            return False
        return True

    @staticmethod
    def can_dequeue(student: Optional[Student], group: Group, time: datetime = None) -> bool:
        """Checks if the student can leave the group or its queue.

        This function will return False if student is None. It will not check
        for student's presence in the group. The function's role is to verify
        legal constraints."""
        if time is None:
            time = datetime.now()
        if student is None:
            return False
        semester = group.course.semester
        if semester.is_closed(time):
            return False
        if not semester.can_remove_record(time):
            return False
        return True

    @staticmethod
    def can_dequeue_groups(student: Optional[Student], groups: List[Group],
                           time: datetime = None) -> Dict[int, bool]:
        """Checks which of the groups the student can leave (or leave their queues).

        It is preferable to call this function rather than
        :func:`~apps.enrollment.records.models.Record.can_dequeue` multiple
        times to save on database queries.

        If student is None, the function will return all False values. It does
        not check for student's presence in the groups. Currently the function
        is fairly simplistic. It is assumed, that all the groups are held in the
        same semester.
        """
        if time is None:
            time = datetime.now()
        if student is None:
            return {k.id: False for k in groups}
        if not groups:
            return {}
        semester = groups[0].course.semester
        if semester.is_closed(time):
            return {k.id: False for k in groups}
        if not semester.can_remove_record(time):
            return {k.id: False for k in groups}
        return {k.id: True for k in groups}

    @classmethod
    def is_enrolled(cls, student_id: int, group_id: int) -> bool:
        """Checks if the student is already enrolled into the group."""
        records = cls.objects.filter(
            student_id=student_id, group_id=group_id, status=RecordStatus.ENROLLED)
        return records.exists()

    @classmethod
    def is_recorded(cls, student_id: int, group_id: int) -> bool:
        """Checks if the student is already enrolled or enqueued into the group."""
        records = cls.objects.filter(
            student_id=student_id, group_id=group_id).exclude(status=RecordStatus.REMOVED)
        return records.exists()

    @classmethod
    def is_recorded_in_groups(cls, student: Optional[Student],
                              groups: List[int]) -> Dict[int, Dict[str, bool]]:
        """Checks, in which groups the student is already enrolled or enqueued.

        The returned object will be a dict indexed by group id. Every entry will
        be a dict with boolean fields 'enrolled' and 'enqueued'. If the student
        is None, every field will be False.
        """
        ret_dict = {g: {'enrolled': False, 'enqueued': False} for g in groups}
        if student is None:
            return ret_dict
        records = cls.objects.filter(
            student_id=student.id, group_id__in=groups).exclude(status=RecordStatus.REMOVED)
        record: cls
        for record in records:
            if record.status == RecordStatus.QUEUED:
                ret_dict[record.group_id]['enqueued'] = True
                ret_dict[record.group_id]['priority'] = record.priority
            elif record.status == RecordStatus.ENROLLED:
                ret_dict[record.group_id]['enrolled'] = True
        return ret_dict

    @classmethod
    def groups_stats(cls, groups: List[int]) -> Dict[int, Dict[str, int]]:
        """For a list of groups returns number of enqueued and enrolled students.

        The data will be returned in the form of a dict indexed by group id.
        Every entry will be a dict with fields 'num_enrolled' and
        'num_enqueued'.
        """
        enrolled_agg = models.Count('id', filter=models.Q(status=RecordStatus.ENROLLED))
        enqueued_agg = models.Count('id', filter=models.Q(status=RecordStatus.QUEUED))
        records = cls.objects.filter(group_id__in=groups).exclude(
            status=RecordStatus.REMOVED).values('group_id').annotate(
                num_enrolled=enrolled_agg, num_enqueued=enqueued_agg).values(
                    'group_id', 'num_enrolled', 'num_enqueued')
        ret_dict: Dict[int, Dict[str, int]] = {
            g: {
                'num_enrolled': 0,
                'num_enqueued': 0
            }
            for g in groups
        }
        for rec in records:
            ret_dict[rec['group_id']]['num_enrolled'] = rec['num_enrolled']
            ret_dict[rec['group_id']]['num_enqueued'] = rec['num_enqueued']
        return ret_dict

    @classmethod
    def enqueue_student(cls, student: Student, group: Group) -> List[int]:
        """Puts the student in the queue of the group.

        If the group is an exercise/lab group, the student will first be
        enqueued into the lecture group as well.

        The function triggers further actions, so the student will be pulled
        into the group as soon as there is vacancy and he is first in line.

        As the operation may result with enqueuing to more than one group, a
        list of these group's ids will be returned.
        """
        cur_time = datetime.now()
        if cls.is_recorded(student.id, group.id):
            return [group.id]
        if not cls.can_enqueue(student, group, cur_time):
            return []
        enqueued_groups = []
        if group.type != Group.GROUP_TYPE_LECTURE:
            lecture_group = Group.get_lecture_group(group.course_id)
            if lecture_group is not None:
                enqueued_groups = cls.enqueue_student(student, lecture_group)
                if not enqueued_groups:
                    return []
        Record.objects.create(
            group=group, student=student, status=RecordStatus.QUEUED, created=cur_time)
        LOGGER.info('User %s is enqueued into group %s', student, group)
        GROUP_CHANGE_SIGNAL.send(None, group_id=group.id)
        enqueued_groups.append(group.id)
        return enqueued_groups

    @classmethod
    def remove_from_group(cls, student: Student, group: Group) -> List[int]:
        """Removes the student from the group.

        If the group is a lecture group, he is also removed from the
        corresponding exercise/lab groups or their respective queues. The user
        can only leave the group before unenrolling deadline, and can only leave
        the queue until the end of enrolling period.

        The function triggers further actions, so the another student will be
        pulled into the group as there is a vacancy caused by the student's
        departure.

        Since the operation might result in removing not only from this group,
        the list of group ids, from which the records have been removed is
        returned.
        """
        record = None
        try:
            record = Record.objects.filter(
                student=student, group=group).exclude(status=RecordStatus.REMOVED).get()
        except cls.DoesNotExist:
            return []
        if not cls.can_dequeue(student, group):
            return []
        removed_groups = []
        # If this is a lecture, remove him from all other groups as well.
        if record.group.type == Group.GROUP_TYPE_LECTURE:
            other_groups_query = Record.objects.filter(
                student=student,
                group__course__id=record.group.course_id).exclude(status=RecordStatus.REMOVED)
            removed_groups = list(other_groups_query.values_list('group_id', flat=True))
            other_groups_query.update(status=RecordStatus.REMOVED)
            for g_id in removed_groups:
                LOGGER.info('User %s removed (CASCADE) from group %s', student, g_id)
                GROUP_CHANGE_SIGNAL.send(None, group_id=g_id)
        record.status = RecordStatus.REMOVED
        record.save()
        removed_groups.append(record.group_id)
        LOGGER.info('User %s removed from group %s', student, group)
        GROUP_CHANGE_SIGNAL.send(None, group_id=record.group_id)
        return removed_groups

    @classmethod
    def set_queue_priority(cls, student: Student, group: Group, priority: int) -> bool:
        """If the student is in a queue for the group, sets the queue priority.

        Returns true if the priority is changed.
        """
        num = cls.objects.filter(
            student=student, group=group, status=RecordStatus.QUEUED).update(priority=priority)
        return num == 1

    @classmethod
    def pull_record_into_group(cls, group_id: int) -> bool:
        """Checks if there are vacancies in the group and pulls the first
        student from the queue if possible.

        This function might be run concurrently. A data race could potentially
        lead to number of students enrolled exceeding the limit. It therefore
        needs to be atomic. A lock is obtained on all the records in the same
        group (so the member limit is not exceeded). It optimistically assumes
        that the group limit is not going to change while it is executing.

        The function will return False if the group is already full, or the
        queue is empty or the enrollment is closed for the semester. True value
        will mean, that it should be run again on that group. The function may
        throw DatabaseError if transaction fails.
        """
        group = Group.objects.select_related('course', 'course__semester').get(id=group_id)
        if not GroupOpeningTimes.is_enrollment_open(group.course, datetime.now()):
            return False
        # If there is a corresponding lecture group, we should first pull
        # records into that group in order to avoid dropping the record, when a
        # student enqueues into the groups at the same time, and this group is
        # being worked before the lecture group.
        if group.type != Group.GROUP_TYPE_LECTURE:
            lecture_group = Group.get_lecture_group(group.course_id)
            if lecture_group is not None:
                cls.fill_group(lecture_group.pk)

        # Groups that will need to be pulled into afterwards.
        trigger_groups = []

        with transaction.atomic():
            # We obtain a lock on the records in this group.
            records = cls.objects.filter(group_id=group_id).exclude(
                status=RecordStatus.REMOVED).select_for_update()
            num_enrolled = records.filter(status=RecordStatus.ENROLLED).count()
            if num_enrolled >= group.limit:
                return False
            try:
                first_in_line = records.filter(status=RecordStatus.QUEUED).earliest('created')
                trigger_groups = first_in_line.enroll_or_remove(group)
            except cls.DoesNotExist:
                return False
        # The tasks should be triggered outside of the transaction
        for trigger_group_id in trigger_groups:
            GROUP_CHANGE_SIGNAL.send(None, group_id=trigger_group_id)
        return True

    @classmethod
    def fill_group(cls, group_id: int):
        """Pulls records from the queue into the group as long as possible.

        This function may raise a DatabaseError when too many transaction errors
        occur.
        """
        num_transaction_errors = 0
        still_free = True
        while still_free:
            try:
                still_free = cls.pull_record_into_group(group_id)
            except DatabaseError:
                # Transaction failure probably means that Postgres decided to
                # terminate the transaction in order to eliminate a deadlock. We
                # will want to retry then. It would not however be responsible
                # to retry too many times and obscure some real error.
                num_transaction_errors += 1
                if num_transaction_errors == 3:
                    raise

    def enroll_or_remove(self, group: Group) -> List[int]:
        """This function takes a single QUEUED record and tries to change its
        status into ENROLLED.

        The function will be run concurrently. A data race might potentially
        lead to a student breaching ECTS limit. To prevent that a lock is
        obtained on all records of this student.

        The operation might fail under certain circumstances (the student is not
        enrolled in the lecture group, enrolling would exceed his ECTS limit).

        The return value is a list of group ids that need to be triggered
        (pulled from). The function may raise a DatabaseError.
        """
        with transaction.atomic():
            records = Record.objects.filter(student_id=self.student_id).exclude(
                status=RecordStatus.REMOVED).select_for_update()

            # Check if he is enrolled into the lecture group.
            if group.type != Group.GROUP_TYPE_LECTURE:
                lecture_group = Group.get_lecture_group(group.course_id)
                if lecture_group is not None:
                    if not self.is_enrolled(self.student_id, lecture_group.id):
                        self.status = RecordStatus.REMOVED
                        self.save()
                        return []

            # Check if he can be enrolled at all.
            if not self.can_enroll(self.student, group):
                self.status = RecordStatus.REMOVED
                self.save()
                return []
            # Remove him from all parallel groups (and queues of lower
            # priority). These groups need to be afterwards pulled into
            # (triggered).
            other_groups_query = records.filter(
                group__course__id=group.course_id,
                group__type=group.type).exclude(id=self.pk).filter(
                    models.Q(priority__lt=self.priority) | models.Q(status=RecordStatus.ENROLLED))
            # The list of groups to trigger must be computed now, after the
            # update it would be empty. Note that this list should have at most
            # one element.
            other_groups_query_list = list(
                other_groups_query.filter(status=RecordStatus.ENROLLED).values_list(
                    'group_id', flat=True))
            other_groups_query.update(status=RecordStatus.REMOVED)
            self.status = RecordStatus.ENROLLED
            self.save()
            return other_groups_query_list
