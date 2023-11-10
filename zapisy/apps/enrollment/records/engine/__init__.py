"""Module rngine is the heart of enrollment logic.

Record Lifetime:

  The record's status transitions in one direction: QUEUED ->(Optional: BLOCKED) -> ENROLLED ->
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

  fill_group(group_id): The asynchronous task runs this function. This function
    checks if enrolment are open and if yes call `pull_records_into_group`.

  It is a loop
    calling `pull_record_into_group` as long as it returns True, which means
    that there still place in the group and students in the queue.

  pull_record_into_group(group_id): It is a loop calling `enroll_student`
    as long there still is a place in the group and students in the queue.

  enroll_student(record): Takes the record and tries to change it's status from
    QUEUED to ENROLLED. This operation will be unsuccessful if the function
    `can_enroll` does not pass, in which case the record's status will be
    changed to BLOCKED if `can_enroll` return ECTS_LIMIT or REMOVED,
    when `can_enroll` return different value. This function additionally
    removes the student from all the parallel groups upon enrolling him into this one,
    and removes him from all the queues of lower priority.

  remove_from_group(student, group): Removes student from the group or its
    queue, thus changing the record's status to REMOVED. All the groups that are
    vacated by the student must be filled by an asynchronous process, so the
    GROUP_CHANGE_SIGNAL is sent.
"""


from apps.enrollment.records.engine.fillup_group import (
    fill_group,
    process_ects_limit_change
)
from apps.enrollment.records.engine.dequeue import (
    remove_from_group,
    can_dequeue,
    can_dequeue_groups,
    )
from apps.enrollment.records.engine.enqueue import (
    can_enqueue,
    can_enqueue_groups,
    can_enroll,
    enqueue_student,
    set_queue_priority
)
from apps.enrollment.records.engine.auto_enrollment import (
    update_records_in_auto_enrollment_group
)
from apps.enrollment.records.engine.checks import (
    is_enrolled,
    is_recorded,
    is_recorded_in_groups,
    student_points_in_semester,
    list_waiting_students,
    groups_stats,
    common_groups
)

__all__ = ['fill_group',
           'process_ects_limit_change',
           'remove_from_group',
           'can_dequeue',
           'can_dequeue_groups',
           'can_enqueue',
           'can_enqueue_groups',
           'can_enroll',
           'enqueue_student',
           'set_queue_priority',
           'update_records_in_auto_enrollment_group',
           'is_enrolled',
           'is_recorded',
           'is_recorded_in_groups',
           'student_points_in_semester',
           'list_waiting_students',
           'groups_stats',
           'common_groups'
           ]
