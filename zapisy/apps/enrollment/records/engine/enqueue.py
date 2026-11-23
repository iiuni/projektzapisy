import logging
from datetime import datetime
from typing import Dict, List, Optional, Set

from apps.enrollment.courses.models import CourseInstance, Group, Semester
from apps.enrollment.records.models.records import Record, RecordStatus, CanEnroll
from apps.enrollment.records.signals import GROUP_CHANGE_SIGNAL
from apps.users.models import Student
from apps.enrollment.records.engine.checks import is_recorded, student_points_in_semester

LOGGER = logging.getLogger(__name__)


def can_enqueue(student: Optional[Student], group: Group, time: datetime = None) -> bool:
    """Checks if the student can join the queue of the group.

    Will return False if student is None. The function will not check if the
    student already belongs to the queue.
    """
    return can_enqueue_groups(student, [group], time)[group.pk]


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
    if time is None:
        time = datetime.now()
    if student is None or not student.is_active:
        return {k.pk: False for k in groups}

    # Preload groups with realted objects to reduce sql queries
    groups = Group.objects.filter(pk__in=[g.pk for g in groups]).select_related(
                "course",
                "course__semester"
                ).all()

    from apps.enrollment.records.models.opening_times import GroupOpeningTimes
    ret = GroupOpeningTimes.are_groups_open_for_student(student, groups, time)
    points = student_queue_points(student, groups[0].course.semester)

    is_in_courses = are_student_in_courses(student, {g.course for g in groups})

    for group in groups:
        if group.auto_enrollment or (
                points + group.course.points > Semester.get_final_limit()
                and not is_in_courses[group.course.pk]):
            ret[group.pk] = False
    return ret


def student_queue_points(student: Student, semester: Semester) -> int:
    """Returns total points the student has enqueued in semester.

    Sum records with statuses different than REMOVED

    Args:
        additional_courses is a list of potential courses a student might
        also want to enroll into.
    """
    records = (
        Record.objects.filter(
            student=student,
            group__course__semester=semester)
        .exclude(status=RecordStatus.REMOVED)
        .select_related('group', 'group__course')
    )
    courses = set(r.group.course for r in records)
    return sum(c.points for c in courses)


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


def can_enroll(student: Optional[Student], group: Group, time: datetime = None) -> CanEnroll:
    """Checks if the student can join the queue of the group.

    The function will not check if the student is already enrolled
    into the group or present in its queue.
    """
    if time is None:
        time = datetime.now()
    if student is None:
        return CanEnroll.OTHER
    if not can_enqueue(student, group, time):
        return CanEnroll.CANNOT_QUEUE
    # Check if enrolling would not make the student exceed the current ECTS
    # limit.
    semester: Semester = group.course.semester
    points = student_points_in_semester(student, semester, [group.course])
    if points > semester.get_current_limit(time):
        return CanEnroll.ECTS_LIMIT
    return CanEnroll.OK


def enqueue_student(student: Student, group: Group) -> bool:
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
    if not can_enqueue(student, group, cur_time):
        return False
    if is_recorded(student, group):
        return True
    Record.objects.create(
        group=group, student=student, status=RecordStatus.QUEUED, created=cur_time)
    LOGGER.info('User %s is enqueued into group %s', student, group)
    GROUP_CHANGE_SIGNAL.send(None, group_id=group.id)
    return True


def set_queue_priority(student: Student, group: Group, priority: int) -> bool:
    """If the student is in a queue for the group, sets the queue priority.

    Returns true if the priority is changed.
    """
    num = Record.objects.filter(
        student=student, group=group, status__in=[RecordStatus.QUEUED, RecordStatus.BLOCKED]
        ).update(priority=priority)
    return num == 1
