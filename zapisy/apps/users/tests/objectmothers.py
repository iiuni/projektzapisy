from apps.users.models import User, UserProfile, Employee


class UserObjectMother():

    @staticmethod
    def user_jan_kowalski():
        user = User(first_name="Jan",
                    last_name="Kowalski",
                    is_staff=False,
                    is_superuser=False,
                    username="jkowalski",
                    password="jkowalski")
        user.full_clean()
        return user

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
