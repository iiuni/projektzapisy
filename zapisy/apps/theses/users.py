"""Defines various utility functions related to operations
on users of the theses system"""

from django.contrib.auth.models import User
from apps.users.models import BaseUser, Employee, is_user_in_group
from .system_settings import get_master_rejecter

THESIS_BOARD_GROUP_NAME = "Komisja prac dyplomowych"


def is_theses_board_member(user: User) -> bool:
    """Is the specified user a member of the theses board?"""
    return is_user_in_group(user, THESIS_BOARD_GROUP_NAME)


def is_theses_admin(user: User):
    """Is the specified user an admin the thesis system?

    Currently fereol admins are also automatically thesis admins;
    restricting their permissions in the frontend client wouldn't
    make much sense as they're allowed to do anything in the Django admin
    interface
    """
    return user.is_staff


def is_master_rejecter(user: User) -> bool:
    """Is the specified user the master rejecter
    (the board member responsible for rejecting theses)?
    """
    rejecter = get_master_rejecter()
    return rejecter is not None and rejecter.user == user


def is_theses_regular_employee(user: User):
    """Is the specified user a regular university employee?

    Those have permissions to create theses and can be set as advisors,
    but otherwise have no administrative privileges
    """
    return BaseUser.is_employee(user) and not user.is_staff


def get_theses_board():
    """Return all members of the theses board"""
    return Employee.objects.select_related(
        'user'
    ).filter(user__groups__name=THESIS_BOARD_GROUP_NAME)


def get_num_board_members() -> int:
    """Return the number of theses board members"""
    return len(get_theses_board())


def get_theses_user_full_name(user: BaseUser):
    """Returns the full name of the user for use by the theses system.

    If the user is an Employee, `get_full_name_with_academic_title` will be used;
    otherwise, `get_full_name` will be used.

    Accepts a BaseUser instance because this is only called by the person serializer,
    and doing it this way is faster (no need to look up the employee/student instance
    via FK)
    """
    if isinstance(user, Employee):
        return user.get_full_name_with_academic_title()
    return user.get_full_name()
