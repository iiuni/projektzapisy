from django.contrib.auth.models import User

from apps.users.models import is_user_in_group


def is_defect_manager(user: User) -> bool:
    return is_user_in_group(user, "defect_managers")
