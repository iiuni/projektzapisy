from django.apps import AppConfig
from django.contrib.auth import get_user_model


class UsersConfig(AppConfig):
    name = 'apps.users'
    verbose_name = 'Users'

    def ready(self):
        super(UsersConfig, self).ready()

        def get_student(self):
            if hasattr(self, 'student_ptr'):
                return self.student_ptr
            else:
                return None

        def get_employee(self):
            if hasattr(self, 'employee_ptr'):
                return self.employee_ptr
            else:
                return None

        UserModel = get_user_model()
        setattr(UserModel, 'student', property(get_student))
        setattr(UserModel, 'employee', property(get_employee))
