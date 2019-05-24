from django.contrib.auth.models import Group as DjangoUserGroup
from django.contrib.auth.models import User
from django.test import TestCase

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.views import can_user_view_students_list_for_group
from apps.users.models import Employee


class StudentsInfoVisibilityForExternalContractorsTestCase(TestCase):

    fixtures = ['users', 'courses']  # order matters!

    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.get(pk=1)
        cls.teacher_user = User.objects.get(pk=2)
        cls.teacher_employee = Employee.objects.get(pk=2)
        cls.semester = Semester.objects.get(pk=1)
        cls.course = CourseInstance.objects.get(pk=1)
        cls.exercise_group = Group.objects.get(pk=1)
        ext_contractors_group, _ = DjangoUserGroup.objects.get_or_create(name='external_contractors')
        cls.teacher_user.groups.add(ext_contractors_group)

    def test_external_contractor_can_see_their_group(self):
        """
        If an external contractor is the teacher of a group,
        they should see names and surnames of all students attending.
        """

        self.assertTrue(
            can_user_view_students_list_for_group(self.teacher_user, self.exercise_group))

    def test_external_contractor_cannot_see_students_outside_of_their_group(self):
        """
        If an external contractor is _not_ the teacher of a group,
        they should only see the students which a regular student would see.
        """

        another_group = Group.objects.get(pk=2)

        self.assertFalse(
            can_user_view_students_list_for_group(self.teacher_user, another_group))

    def test_student_from_group_cannot_see_other_students(self):
        """
        A student should only see those students who gave their consent,
        even when they are in the same group.
        """

        self.assertFalse(
            can_user_view_students_list_for_group(self.student, self.exercise_group))
