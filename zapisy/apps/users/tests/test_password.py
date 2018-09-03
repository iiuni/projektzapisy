from django.contrib.auth.models import User
from django.test import TestCase
from apps.users.tests.factories import UserFactory
from django.urls import reverse
from apps.users.models import Employee, Student


class BaseUserTestCase(TestCase):
    def test_password_check(self) -> None:
        u = UserFactory()
        self.assertTrue(u.check_password('test'))

    def test_password_reset(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)


class GroupsTestCase(TestCase):

    def test_employee_model(self) -> None:
        """Check if for each entry in Employee model, related user belongs to employees group."""
        for employee in Employee.objects.all():
            user = employee.user
            self.assertTrue(user.groups.filter(name="employees").exists())

    def test_student_model(self) -> None:
        """Check if for each entry in Student model, related user belongs to students group."""
        for student in Student.objects.all():
            user = student.user
            self.assertTrue(user.groups.filter(name="students").exists())

    def test_employees_group(self) -> None:
        """Check if for each user in employees group there is related Employee entry"""
        for employee in User.objects.filter(groups__name='employees'):
            self.assertIsNotNone(employee.employee)

    def test_students_group(self) -> None:
        """Check if for each user in students group there is related Student entry"""
        for student in User.objects.filter(groups__name='students'):
            self.assertIsNotNone(student.student)
