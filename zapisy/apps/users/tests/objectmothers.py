from apps.users.models import UserProfile, Employee


class UserObjectMother:
    @staticmethod
    def student_profile(user):
        profile = UserProfile(user=user,
                              is_student=True)
        profile.full_clean()
        return profile

    @staticmethod
    def teacher_profile(user):
        profile = UserProfile(user=user,
                              is_employee=True)
        profile.full_clean()
        return profile

    @staticmethod
    def employee(user):
        employee = Employee(user=user)
        employee.full_clean()
        return employee
