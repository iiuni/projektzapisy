from django.contrib.auth.models import User

from apps.theses.system_settings import get_master_rejecter
from apps.users.models import Employee, is_employee, is_user_in_group

THESIS_BOARD_GROUP_NAME = "Komisja prac dyplomowych"


def get_theses_board():
    """Returns all members of the theses board."""
    return Employee.objects.select_related(
        'user'
    ).filter(user__groups__name=THESIS_BOARD_GROUP_NAME)


def get_num_board_members() -> int:
    """Returns the number of theses board members."""
    return get_theses_board().count()


def is_theses_board_member(user: User) -> bool:
    """Is the specified user a member of the theses board?"""
    return is_user_in_group(user, THESIS_BOARD_GROUP_NAME)


def is_master_rejecter(user: User) -> bool:
    """Is the specified user a master rejecter of theses board?"""
    return is_employee(user) and get_master_rejecter() == user.employee
