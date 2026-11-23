from django.contrib.auth.models import User

from apps.enrollment.courses.models.group import Group
from apps.users.models import is_external_contractor


def can_user_view_students_list_for_group(user: User, group: Group) -> bool:
    is_user_proper_employee = user.employee and not is_external_contractor(user)
    is_user_group_teacher = group.teacher and user == group.teacher.user
    return is_user_proper_employee or is_user_group_teacher
