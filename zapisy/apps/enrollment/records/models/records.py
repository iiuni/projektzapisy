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
from collections import defaultdict
import copy
from datetime import datetime
from enum import Enum
from typing import DefaultDict, Dict, Iterable, List, Optional, Set

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.enrollment.courses.models import CourseInstance, Group, Semester
from apps.enrollment.records.models.opening_times import GroupOpeningTimes
from apps.enrollment.records.signals import GROUP_CHANGE_SIGNAL
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

    @staticmethod
    def can_enqueue(student: Optional[Student], group: Group, time: datetime = None) -> bool:
        """Checks if the student can join the queue of the group.

        Will return False if student is None. The function will not check if the
        student already belongs to the queue.
        """
        return Record.can_enqueue_groups(student, [group], time)[group.pk]

    @staticmethod
    def can_enqueue_groups(student: Optional[Student], groups: List[Group],
                           time: datetime = None) -> Dict[int, bool]:
        """Checks if the student can join the queues of respective groups.

        For given groups, the function will return a dict representing groups.
        For every group primary key the return value will tell, if the student
        can enqueue into the group. It will return all False values if student
        is None. It is not checking if the student is already present in
        the groups.

        This function should be called instead of multiple calls to the
        :func:`~apps.enrollment.records.models.Record.can_enqueue` function to
        save on DB queries.
        """
        if not groups:
            return {}

        # Preload groups with realted objects to reduce sql queries
        groups = Group.objects.filter(pk__in=[g.pk for g in groups]).select_related(
                    "course",
                    "course__semester"
                    ).all()

        if time is None:
            time = datetime.now()
        if student is None or not student.is_active:
            return {k.pk: False for k in groups}
        ret = GroupOpeningTimes.are_groups_open_for_student(student, groups, time)
        points = Record.student_points_in_semester(
            student, groups[0].course.semester
        )
        is_in_courses = Record.are_student_in_courses(student, {g.course for g in groups})

        for group in groups:
            if group.auto_enrollment or (
                    points + group.course.points > Semester.get_final_limit()
                    and not is_in_courses[group.course.pk]):
                ret[group.pk] = False
        return ret

    @staticmethod
    def are_student_in_courses(student: Student,
                               courses: Set[CourseInstance]) -> Dict[int, bool]:
        """Checks if the student is enrolled or queued to each course in courses.

        Result: dict with keys as course.pk and value is enrolled or queued.
        """
        records = Record.objects.filter(
            student=student,
            group__course__in=courses,
        ).exclude(status=RecordStatus.REMOVED).select_related("group__course")

        ret: Dict[int, bool] = {course.pk: False for course in courses}

        for rec in records:
            ret[rec.group.course.pk] = True

        return ret

    @classmethod
    def can_enroll(cls, student: Optional[Student], group: Group, time: datetime = None) -> CanEnroll:
        """Checks if the student can join the queue of the group.

        The function will not check if the student is already enrolled
        into the group or present in its queue.
        """
        if time is None:
            time = datetime.now()
        if student is None:
            return CanEnroll.OTHER
        if not cls.can_enqueue(student, group, time):
            return CanEnroll.CANNOT_QUEUE
        # Check if enrolling would not make the student exceed the current ECTS
        # limit.
        semester: Semester = group.course.semester
        points = cls.student_points_in_semester(student, semester, [group.course])
        if points > semester.get_current_limit(time):
            return CanEnroll.ECTS_LIMIT
        return CanEnroll.OK

    @classmethod
    def student_points_in_semester(cls, student: Student, semester: Semester,
                                   additional_courses: Iterable[CourseInstance] = []) -> int:
        """Returns total points the student has accumulated in semester.

        Args:
            additional_courses is a list of potential courses a student might
            also want to enroll into.
        """
        records = cls.objects.filter(
            student=student,
            group__course__semester=semester, status=RecordStatus.ENROLLED).select_related(
                'group', 'group__course')
        courses = set(r.group.course for r in records)
        courses.update(additional_courses)
        return sum(c.points for c in courses)

    @staticmethod
    def can_dequeue(student: Optional[Student], group: Group, time: datetime = None) -> bool:
        """Checks if the student can leave the group or its queue.

        This function will return False if student is None. It will not check
        for student's presence in the group. The function's role is to verify
        legal constraints.
        """
        return Record.can_dequeue_groups(student, [group], time)[group.pk]

    @staticmethod
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
            return {k.id: False for k in groups}
        ret = {}
        groups = Record.is_recorded_in_groups(student, groups)
        for group in groups:
            if group.auto_enrollment:
                ret[group.id] = False
            elif group.course.records_end is not None:
                ret[group.id] = time <= group.course.records_end
            elif not group.course.semester.can_remove_record(time):
                # When disenrolment is closed, QUEUED record can still be
                # removed, ENROLLED may not.
                ret[group.id] = getattr(group, 'enqueued', False)
            else:
                ret[group.id] = True
        return ret

    @staticmethod
    def list_waiting_students(
            courses: List[CourseInstance]) -> DefaultDict[int, DefaultDict[int, int]]:
        """Returns students waiting to be enrolled.

        Returned students aren't enrolled in any group of given type within
        given course, but they are enqueued into at least one.

        Returns:
            A dict indexed by a course_id. Every entry is a dict mapping
            group_type to a number of waiting students.
        """
        queued = Record.objects.filter(
            status=RecordStatus.QUEUED, group__course__in=courses).values(
                'group__course', 'group__type', 'student__user',
                'student__user__first_name', 'student__user__last_name')
        enrolled = Record.objects.filter(
            status=RecordStatus.ENROLLED, group__course__in=courses).values(
                'group__course', 'group__type', 'student__user', 'student__user__first_name',
                'student__user__last_name')
        waiting = queued.difference(enrolled)
        ret = defaultdict(lambda: defaultdict(int))
        for w in waiting:
            ret[w['group__course']][w['group__type']] += 1
        return ret

    @classmethod
    def is_enrolled(cls, student: Student, group: Group) -> bool:
        """Checks if the student is already enrolled into the group."""
        records = cls.objects.filter(
            student=student, group=group, status=RecordStatus.ENROLLED)
        return records.exists()

    @classmethod
    def is_recorded(cls, student: Student, group: Group) -> bool:
        """Checks if the student is already enrolled or enqueued into the group."""
        entry = cls.is_recorded_in_groups(student, [group])[0]
        return getattr(entry, 'is_enqueued', False) or getattr(entry, 'is_enrolled', False)

    @classmethod
    def is_recorded_in_groups(cls, student: Optional[Student],
                              groups: Iterable[Group]) -> List[Group]:
        """Checks, in which groups the student is already enrolled or enqueued.

        The function modifies provided groups by setting additional attributes:
        'is_enrolled', 'is_enqueued' and 'priority'. The attributes must always
        be checked with a default, because they are sometimes skipped.
        """
        groups = [copy.copy(g) for g in groups]
        if student is None:
            return groups
        records = cls.objects.filter(student=student,
                                     group_id__in=groups).exclude(status=RecordStatus.REMOVED)
        by_group = {record.group_id: record for record in records}
        for group in groups:
            if group.id not in by_group:
                continue
            record = by_group[group.id]
            if record.status in [RecordStatus.QUEUED, RecordStatus.BLOCKED]:
                setattr(group, 'is_enqueued', True)
                setattr(group, 'priority', record.priority)
            elif record.status == RecordStatus.ENROLLED:
                setattr(group, 'is_enrolled', True)
        return groups

    @classmethod
    def groups_stats(cls, groups: List[Group]) -> Dict[int, Dict[str, int]]:
        """For a list of groups returns number of enqueued and enrolled students.

        The data will be returned in the form of a dict indexed by group id.
        Every entry will be a dict with fields 'num_enrolled' and
        'num_enqueued'.
        """
        enrolled_agg = models.Count('id', filter=models.Q(status=RecordStatus.ENROLLED))
        enqueued_agg = models.Count('id', filter=models.Q(status=RecordStatus.QUEUED))
        records = cls.objects.filter(group__in=groups).exclude(
            status=RecordStatus.REMOVED).values('group_id').annotate(
                num_enrolled=enrolled_agg, num_enqueued=enqueued_agg).values(
                    'group_id', 'num_enrolled', 'num_enqueued')
        ret_dict: Dict[int, Dict[str, int]] = {
            g.pk: {
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
    def common_groups(cls, user: User, groups: List[Group]) -> Set[int]:
        """Returns ids of those of groups that user is involved in.

        User may be an employee — we then return groups he is teaching. If user
        is a student, we return those of the groups, he is enrolled into. If
        user is neither a student nor an employee, an empty set is returned.
        """
        common_groups = set()
        if user.student:
            student_records = Record.objects.filter(
                group__in=groups, student=user.student, status=RecordStatus.ENROLLED)
            common_groups = {r.group_id for r in student_records}
        if user.employee:
            common_groups = set(
                Group.objects.filter(pk__in=[g.pk for g in groups],
                                     teacher=user.employee).values_list('pk', flat=True))
        return common_groups

    @classmethod
    def enqueue_student(cls, student: Student, group: Group) -> bool:
        """Puts the student in the queue of the group.

        The function triggers further actions, so the student will be pulled
        into the group as soon as there is vacancy and he is first in line.

        Concurrency:
            This function may lead to a race when run concurrently. The race
            will result in a student enqueued multiple times in the same group.
            This could be prevented with database locking, but was considered
            not harmful enough: the student will only be pulled into the group
            once. Upon second pulling his first ENROLLED record is going to be
            removed.

        Returns:
            bool: Whether the student could be enqueued. Will return True if the
            student had already been enqueued in the group.
        """
        cur_time = datetime.now()
        if not cls.can_enqueue(student, group, cur_time):
            return False
        if cls.is_recorded(student, group):
            return True
        Record.objects.create(
            group=group, student=student, status=RecordStatus.QUEUED, created=cur_time)
        LOGGER.info('User %s is enqueued into group %s', student, group)
        GROUP_CHANGE_SIGNAL.send(None, group_id=group.id)
        return True

    @classmethod
    def remove_from_group(cls, student: Student, group: Group) -> bool:
        """Removes the student from the group.

        The user can only leave the group before unenrolling deadline, and can
        only leave the queue until the end of enrolling period.

        The function triggers further actions, so another student will be pulled
        into the group as there is a vacancy caused by the student's departure.

        Returns:
            bool: Whether the removal was successfull.
        """
        record = None
        if not cls.can_dequeue(student, group):
            return False
        try:
            record = Record.objects.filter(
                student=student, group=group).exclude(status=RecordStatus.REMOVED).get()
        except cls.DoesNotExist:
            return False
        record.status = RecordStatus.REMOVED
        record.save()
        LOGGER.info('User %s removed from group %s', student, group)
        GROUP_CHANGE_SIGNAL.send(None, group_id=record.group_id)
        return True

    @classmethod
    def set_queue_priority(cls, student: Student, group: Group, priority: int) -> bool:
        """If the student is in a queue for the group, sets the queue priority.

        Returns true if the priority is changed.
        """
        num = cls.objects.filter(
            student=student, group=group, status=RecordStatus.QUEUED).update(priority=priority)
        return num == 1

    @classmethod
    def update_records_in_auto_enrollment_group(cls, group_id: int):
        """Automatically syncs students in an auto-enrollment group.

        Auto-enrollment groups must always reflect the state of other groups in
        the course: people enrolled to some other group must also be enrolled in
        the auto-enrollment group. People enqueued in other groups (but not
        enrolled in any) will be enqueued in the auto-enrollment group. Everyone
        else must be out.

        Args:
            group_id: Must be an id of a auto-enrollment group.
        """
        other_groups = Group.objects.filter(course__groups=group_id, auto_enrollment=False)

        def get_all_students(**kwargs):
            qs = cls.objects.filter(**kwargs)
            return set(qs.values_list('student_id', flat=True).distinct())

        enrolled_other = get_all_students(group__in=other_groups, status=RecordStatus.ENROLLED)
        queued_other = get_all_students(group__in=other_groups, status=RecordStatus.QUEUED)
        enrolled_in_group = get_all_students(group=group_id, status=RecordStatus.ENROLLED)
        queued_in_group = get_all_students(group=group_id, status=RecordStatus.QUEUED)
        # First we enqueue people who are in some groups but are completely absent in our group.
        missing_students = (enrolled_other | queued_other) - (enrolled_in_group | queued_in_group)
        cls.objects.bulk_create([
            Record(student_id=s, group_id=group_id, status=RecordStatus.QUEUED)
            for s in missing_students
        ])
        # We change the status from queued to enrolled for those, who should be enrolled.
        cls.objects.filter(group=group_id,
                           status=RecordStatus.QUEUED,
                           student_id__in=enrolled_other).update(status=RecordStatus.ENROLLED)
        # We change the status from enrolled to queued for those who should be queued.
        cls.objects.filter(
            group=group_id,
            status=RecordStatus.ENROLLED,
            student_id__in=(queued_other - enrolled_other)).update(status=RecordStatus.QUEUED)
        # Drop records of people not in the group.
        cls.objects.filter(group_id=group_id).exclude(status=RecordStatus.REMOVED).exclude(
            student_id__in=(enrolled_other | queued_other)).update(status=RecordStatus.REMOVED)
