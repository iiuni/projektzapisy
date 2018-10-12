from django.contrib.auth.models import Group
from django.test import TransactionTestCase

from apps.enrollment.records.utils import can_user_view_students_list_for_group

from apps.enrollment.records.tests.factories import (
    create_course,
    create_exercise_group,
    create_semester,
    create_student_user,
    create_teacher
)


class RecordsUtilsTestCase(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        cls.student = create_student_user()
        cls.teacher_user, cls.teacher_employee = create_teacher()
        cls.semester = create_semester()
        cls.course = create_course(cls.semester)
        cls.exercise_group = create_exercise_group(cls.course, cls.teacher_employee)
        ext_contractors_group, _ = Group.objects.get_or_create(name='external_contractors')
        cls.teacher_user.groups.add(ext_contractors_group)

    def test_external_contractor_can_see_their_group(self):
        self.assertTrue(
            can_user_view_students_list_for_group(self.teacher_user, self.exercise_group))

    def test_external_contractor_cannot_see_students_outside_of_their_group(self):
        another_teacher_user, another_teacher_employee = create_teacher()
        another_semester = create_semester()
        another_course = create_course(another_semester)
        another_group = create_exercise_group(another_course, another_teacher_employee)

        self.assertFalse(
            can_user_view_students_list_for_group(self.teacher_user, another_group))

    def test_student_from_group_cannot_see_other_students(self):
        self.assertFalse(
            can_user_view_students_list_for_group(self.student, self.exercise_group))
