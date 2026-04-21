"""Business logic for director's withdrawal requests.

Public API:
    can_request_withdrawal(student, course, time=None) -> (bool, str)
    get_withdrawals_used_total(student) -> int
    get_withdrawals_used_in_semester(student, semester) -> int
    request_withdrawal(student, course) -> DirectorWithdrawal
    approve_withdrawal(withdrawal, admin_user) -> None
    reject_withdrawal(withdrawal, admin_user, comment='') -> None
"""

import logging
from datetime import datetime

from apps.enrollment.records.models.records import Record, RecordStatus
from apps.enrollment.records.signals import GROUP_CHANGE_SIGNAL

from .models import DirectorWithdrawal, WithdrawalStatus

LOGGER = logging.getLogger(__name__)


def get_withdrawals_used_total(student):
    """Returns the number of approved director withdrawals the student has used."""
    return DirectorWithdrawal.objects.filter(
        student=student, status=WithdrawalStatus.APPROVED
    ).count()


def get_withdrawals_used_in_semester(student, semester):
    """Returns the number of approved director withdrawals in a given semester."""
    return DirectorWithdrawal.objects.filter(
        student=student,
        status=WithdrawalStatus.APPROVED,
        course__semester=semester,
    ).count()


def can_request_withdrawal(student, course, time=None):
    """Checks whether the student can submit a director withdrawal request.

    Returns:
        (True, '') if the request is allowed.
        (False, reason) if not, where reason is a human-readable message.

    Conditions (all must be met):
        - student is active
        - student is enrolled (ENROLLED status) in at least one group of the course
        - current time is after semester's records_closing
        - current time is before semester's director_withdrawal_deadline (if set)
        - no existing PENDING or APPROVED withdrawal for this (student, course) pair
        - student hasn't exceeded their total withdrawal_limit
        - student hasn't already used a withdrawal in this semester (max 1 per semester)
    """
    if time is None:
        time = datetime.now()

    if student is None or not student.is_active:
        return False, 'Konto studenta jest nieaktywne.'

    semester = course.semester

    # Must be after records_closing
    if semester.records_closing is None or time <= semester.records_closing:
        return False, 'Składanie wniosków jest możliwe dopiero po zamknięciu zapisów.'

    # Must be before director_withdrawal_deadline (if set)
    if semester.director_withdrawal_deadline is not None:
        if time > semester.director_withdrawal_deadline:
            return False, 'Termin składania wniosków o wypis dyrektorski minął.'

    # Student must be enrolled in at least one group of the course
    enrolled = Record.objects.filter(
        student=student,
        group__course=course,
        status=RecordStatus.ENROLLED,
    ).exists()
    if not enrolled:
        return False, 'Nie jesteś zapisany na żadną grupę tego przedmiotu.'

    # No duplicate pending/approved request
    existing = DirectorWithdrawal.objects.filter(
        student=student,
        course=course,
        status__in=[WithdrawalStatus.PENDING, WithdrawalStatus.APPROVED],
    ).exists()
    if existing:
        return False, 'Wniosek o wypis dyrektorski dla tego przedmiotu już istnieje.'

    # Total limit check
    used_total = get_withdrawals_used_total(student)
    if used_total >= student.withdrawal_limit:
        return False, (
            f'Wyczerpano limit wypisów dyrektorskich '
            f'({used_total}/{student.withdrawal_limit}).'
        )

    # Max 1 per semester
    used_in_semester = get_withdrawals_used_in_semester(student, semester)
    if used_in_semester >= 1:
        return False, 'Możliwy jest tylko jeden wypis dyrektorski w semestrze.'

    return True, ''


def request_withdrawal(student, course):
    """Creates a pending director withdrawal request.

    Raises:
        ValueError: If the student is not eligible (can_request_withdrawal fails).
    """
    allowed, msg = can_request_withdrawal(student, course)
    if not allowed:
        raise ValueError(msg)

    withdrawal = DirectorWithdrawal.objects.create(
        student=student,
        course=course,
        status=WithdrawalStatus.PENDING,
    )
    LOGGER.info('Director withdrawal request created: student=%s course=%s', student, course)
    return withdrawal


def approve_withdrawal(withdrawal, admin_user):
    """Approves a director withdrawal request.

    Removes the student from all enrolled/queued groups of the course,
    bypassing the normal deadline restrictions (this is an admin override).

    Raises:
        ValueError: If the withdrawal is not in PENDING status.
    """
    if withdrawal.status != WithdrawalStatus.PENDING:
        raise ValueError(
            f'Wniosek nie jest w stanie oczekującym (aktualny status: '
            f'{withdrawal.get_status_display()}).'
        )

    student = withdrawal.student
    course = withdrawal.course

    # Remove student from all non-removed records in this course (admin bypass)
    records = Record.objects.filter(
        student=student,
        group__course=course,
    ).exclude(status=RecordStatus.REMOVED)

    # Collect group IDs before deleting records (after update the queryset changes)
    affected_group_ids = []
    for record in records:
        affected_group_ids.append(record.group_id)

    # Directly set to REMOVED (bypasses can_dequeue deadline check)
    records.update(status=RecordStatus.REMOVED)

    # Trigger queue-fill for each vacated group
    for group_id in affected_group_ids:
        GROUP_CHANGE_SIGNAL.send(None, group_id=group_id)

    withdrawal.status = WithdrawalStatus.APPROVED
    withdrawal.decided_by = admin_user
    withdrawal.decided_at = datetime.now()
    withdrawal.save()

    LOGGER.info(
        'Director withdrawal approved: student=%s course=%s by=%s',
        student, course, admin_user,
    )


def reject_withdrawal(withdrawal, admin_user, comment=''):
    """Rejects a director withdrawal request.

    The student remains enrolled in their groups.

    Raises:
        ValueError: If the withdrawal is not in PENDING status.
    """
    if withdrawal.status != WithdrawalStatus.PENDING:
        raise ValueError(
            f'Wniosek nie jest w stanie oczekującym (aktualny status: '
            f'{withdrawal.get_status_display()}).'
        )

    withdrawal.status = WithdrawalStatus.REJECTED
    withdrawal.decided_by = admin_user
    withdrawal.decided_at = datetime.now()
    withdrawal.admin_comment = comment
    withdrawal.save()

    LOGGER.info(
        'Director withdrawal rejected: student=%s course=%s by=%s',
        withdrawal.student, withdrawal.course, admin_user,
    )
