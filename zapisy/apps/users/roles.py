from django.contrib.auth.models import User
from apps.users.models import is_user_in_group


class Roles:
    @staticmethod
    def is_student(user: User) -> bool:
        return hasattr(user, 'student')

    @staticmethod
    def is_employee(user: User) -> bool:
        return hasattr(user, 'employee')

    @staticmethod
    def is_external_contractor(user: User) -> bool:
        return is_user_in_group(user, 'external_contractors')
