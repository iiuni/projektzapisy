"""This module defines high-level thesis-related permissions
checks used when deserializing a received thesis object and performing actions.
"""
from typing import Optional

from django.contrib.auth.models import User
from apps.users.models import Employee, BaseUser

from .enums import UNVOTEABLE_STATUSES
from .models import Thesis, ThesisStatus
from .users import (
    is_theses_admin, is_theses_regular_employee,
    is_theses_board_member, is_master_rejecter,
)


def is_thesis_staff(user: User) -> bool:
    """Determine whether the user should be considered a "staff member" in the theses system.
    Those are generally permitted to administer any thesis
    """
    return is_theses_admin(user) or is_theses_board_member(user)


def can_add_thesis(user: User) -> bool:
    """Is the given user permitted to add new thesis objects?"""
    return is_theses_admin(user) or is_theses_regular_employee(user)


def is_owner_of_thesis(user: User, thesis: Thesis) -> bool:
    """Is the specified user the advisor of the specified thesis?"""
    return BaseUser.is_employee(user) and thesis.advisor == user.employee


EMPLOYEE_DELETABLE_STATUSES = (
    ThesisStatus.BEING_EVALUATED,
    ThesisStatus.RETURNED_FOR_CORRECTIONS
)


def can_delete_thesis(user: User, thesis: Thesis) -> bool:
    """Determine if the specified user is permitted to delete the specified thesis"""
    return (
        is_theses_admin(user) or
        is_theses_board_member(user) and not thesis.is_archived() or
        is_theses_regular_employee(user) and is_owner_of_thesis(user, thesis) and
        ThesisStatus(thesis.status) in EMPLOYEE_DELETABLE_STATUSES
    )


def can_modify_thesis(user: User, thesis: Thesis) -> bool:
    """Is the specified user permitted to make any changes to the specified thesis?"""
    if thesis.is_archived():
        return is_theses_admin(user)
    return is_thesis_staff(user) or is_owner_of_thesis(user, thesis)


def can_change_title(user: User, thesis: Thesis) -> bool:
    """Is the specified user permitted to change the title of the specified thesis?

    Only called if the user is permitted to modify the thesis in general
    (that is, `can_modify_thesis` returns True)
    """
    allowed_statuses = (ThesisStatus.BEING_EVALUATED, ThesisStatus.RETURNED_FOR_CORRECTIONS)
    return (
        is_thesis_staff(user) or
        is_owner_of_thesis(user, thesis) and ThesisStatus(thesis.status) in allowed_statuses
    )


def can_set_status_for_new(user: User, status: ThesisStatus) -> bool:
    """Can the specified user set the specified status for a new thesis?

    Only called if the user is permitted to modify the thesis in general
    (that is, `can_modify_thesis` returns True)
    """
    return is_thesis_staff(user) or status == ThesisStatus.BEING_EVALUATED


def can_change_status_to(user: User, thesis: Thesis, new_status: ThesisStatus) -> bool:
    """Can the specified user change the status
    of the specified thesis to the new specified status?

    Only called if the user is permitted to modify the thesis in general
    (that is, `can_modify_thesis` returns True)
    """
    old_status = ThesisStatus(thesis.status)
    return (
        is_theses_admin(user) or
        is_master_rejecter(user) or
        is_theses_board_member(user) and new_status != ThesisStatus.RETURNED_FOR_CORRECTIONS or
        old_status == ThesisStatus.IN_PROGRESS and new_status == ThesisStatus.DEFENDED
    )


def can_set_advisor(user: User, advisor: Optional[Employee]) -> bool:
    """Is the specified user permitted to set the given advisor (may be None)?

    Only called if the user is permitted to modify the thesis in general
    (that is, `can_modify_thesis` returns True)
    """
    return is_thesis_staff(user) or (BaseUser.is_employee(user) and user.employee == advisor)


def can_cast_vote_as_user(caster: User, user: User) -> bool:
    """Can the specified user cast a vote in the other user's name?"""
    return is_theses_admin(caster) or is_theses_board_member(user) and caster == user


def can_change_vote_for_thesis(user: Employee, thesis: Thesis) -> bool:
    """Can the specified user change votes for the specified thesis?"""
    return (
        is_theses_admin(user) or
        is_theses_board_member(user) and ThesisStatus(thesis.status) not in UNVOTEABLE_STATUSES
    )


def can_see_thesis_rejection_reason(
    thesis: Thesis, is_staff: bool, is_employee: bool, user: User
):
    """Should the official rejection reason be disclosed to the specified user?
    As an optimization, is_staff/is_employee is passed directly so that we don't need to check
    that in this function (this will be called for every serialized thesis)
    """
    return (
        is_staff or
        is_employee and (thesis.advisor == user.employee or thesis.supporting_advisor == user.employee)
    )


def can_see_thesis_votes(is_staff: bool):
    """Should the votes for a thesis be disclosed to this user?
    As above, this takes a bool argument as an optimization
    """
    return is_staff
