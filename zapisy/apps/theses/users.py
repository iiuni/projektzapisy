from django.contrib.auth.models import User

from apps.theses.system_settings import get_master_rejecter
from apps.users.models import Employee, is_employee, is_user_in_group

THESIS_BOARD_GROUP_NAME = "Komisja prac dyplomowych"


def get_theses_board(exclude_advisors_for_thesis = None):
    """Returns all members of the board for specific thesis."""
    board = Employee.objects.select_related(
        'user'
        ).filter(user__groups__name=THESIS_BOARD_GROUP_NAME)
    if exclude_advisors_for_thesis is None:
        return board
    if exclude_advisors_for_thesis.supporting_advisor is None:
        return board.exclude(id__in=[exclude_advisors_for_thesis.advisor.id])
    return board.exclude(id__in=[exclude_advisors_for_thesis.advisor.id,
                                 exclude_advisors_for_thesis.supporting_advisor.id])


def get_num_board_members() -> int:
    """Returns the number of theses board members."""
    return get_theses_board().count()


def is_theses_board_member(user: User) -> bool:
    """Is the specified user a member of the theses board?"""
    return is_user_in_group(user, THESIS_BOARD_GROUP_NAME)


def is_master_rejecter(user: User) -> bool:
    """Is the specified user a master rejecter of theses board?"""
    return is_employee(user) and get_master_rejecter() == user.employee
