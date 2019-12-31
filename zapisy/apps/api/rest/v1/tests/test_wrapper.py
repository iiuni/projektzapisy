from datetime import datetime

from unittest.mock import patch

from rest_framework.test import APILiveServerTestCase
from rest_framework.test import RequestsClient
from rest_framework.authtoken.models import Token

from apps.enrollment.courses.tests.factories import (SemesterFactory,
                                                     CourseInstanceFactory,
                                                     ClassroomFactory,
                                                     GroupFactory,
                                                     TermFactory)
from apps.users.tests.factories import (StudentFactory,
                                        UserFactory,
                                        EmployeeFactory)
# from apps.schedule.tests.factories import TermFactory
from apps.api.rest.v1.api_wrapper.sz_api import ZapisyApi


class WrapperTests(APILiveServerTestCase):
    """E2E tests for ZapisyApi wrapper

    First to check when these tests fail:
        models in api_wrapper.sz_api.models.py should be up to date
        and reflect serializers in serializers.py and corresponding
        django models. So if you have changed some django model and seeing
        below tests failing, it may be the case.

    """

    def setUp(self):
        # we ca't use patch decorador
        # because it wouldn't patch inside of setUp method.
        patcher = patch(
            'apps.api.rest.v1.api_wrapper.sz_api.sz_api.requests',
            new=RequestsClient())
        patcher.start()
        self.addCleanup(patcher.stop)

        employee = UserFactory(is_staff=True)
        token = Token.objects.create(user=employee)
        self.wrapper = ZapisyApi(
            "Token " + token.key, "http://testserver/api/v1/")

    def test_semester(self):
        semester = SemesterFactory()
        result = list(self.wrapper.semesters())
        self.assertEqual(len(result), 1)
        res_semester = result[0]
        self.assertEqual(res_semester.id, semester.id)
        self.assertEqual(res_semester.display_name, semester.get_name())
        self.assertEqual(res_semester.year, semester.year)
        self.assertEqual(res_semester.type, semester.type)
        self.assertEqual(res_semester.usos_kod, semester.usos_kod)

    def test_current_semester(self):
        semester = SemesterFactory(semester_beginning=datetime.now().date(),
                                   semester_ending=datetime.now().date())
        res_semester = self.wrapper.current_semester()

        self.assertEqual(res_semester.id, semester.id)

    def test_current_semester_None(self):
        SemesterFactory()
        res_semester = self.wrapper.current_semester()

        self.assertEqual(res_semester, None)

    def test_single_record(self):
        semester = SemesterFactory()
        res_semester = self.wrapper.semester(semester.id)

        self.assertEqual(res_semester.id, semester.id)
        self.assertEqual(res_semester.display_name, semester.get_name())
        self.assertEqual(res_semester.year, semester.year)
        self.assertEqual(res_semester.type, semester.type)
        self.assertEqual(res_semester.usos_kod, semester.usos_kod)

    def test_student(self):
        student1, student2 = StudentFactory(), StudentFactory()
        student1.save()
        student2.save()
        result = list(self.wrapper.students())
        self.assertEqual(len(result), 2)
        res_student = result[0]

        self.assertEqual(res_student.id, student1.id)
        self.assertEqual(res_student.matricula, student1.matricula)
        self.assertEqual(res_student.ects, student1.ects)
        self.assertEqual(res_student.status, student1.status)
        self.assertEqual(res_student.user.id, student1.user.id)
        self.assertEqual(res_student.user.username, student1.user.username)
        self.assertEqual(res_student.user.first_name, student1.user.first_name)
        self.assertEqual(res_student.user.last_name, student1.user.last_name)
        self.assertEqual(res_student.usos_id, student1.usos_id)

    def test_save_student(self):
        student = StudentFactory()
        [res_student] = list(self.wrapper.students())
        self.assertEqual(res_student.id, student.id)
        res_student.usos_id = 666
        self.wrapper.save(res_student)

        [changed_student] = list(self.wrapper.students())

        self.assertEqual(changed_student.status, student.status)
        self.assertEqual(changed_student.usos_id, 666)

    def test_pagination(self):
        StudentFactory.create_batch(210)
        result = list(self.wrapper.students())
        self.assertEqual(len(result), 210)

    def test_employee(self):
        employee = EmployeeFactory()
        [res_employee] = list(self.wrapper.employees())

        self.assertEqual(employee.id, res_employee.id)
        self.assertEqual(employee.consultations, res_employee.consultations)
        self.assertEqual(employee.homepage, res_employee.homepage)
        self.assertEqual(employee.room, res_employee.room)
        self.assertEqual(employee.title, res_employee.title)
        self.assertEqual(employee.usos_id, res_employee.usos_id)

    def test_course(self):
        course = CourseInstanceFactory()
        [res_course] = list(self.wrapper.courses())

        self.assertEqual(res_course.id, course.id)
        self.assertEqual(res_course.name, course.name)
        self.assertEqual(res_course.short_name, course.short_name)
        self.assertEqual(res_course.points, course.points)
        self.assertEqual(res_course.has_exam, course.has_exam)
        self.assertEqual(res_course.description, course.description)
        self.assertEqual(res_course.semester, course.semester.id)
        self.assertEqual(res_course.course_type, course.course_type.short_name)
        self.assertEqual(res_course.usos_kod, course.usos_kod)

    def test_classroom(self):
        classroom = ClassroomFactory()
        [res_classroom] = list(self.wrapper.classrooms())

        self.assert_declared_fields(
            ('id', 'type', 'description', 'number', 'order', 'building',
             'capacity', 'floor', 'can_reserve', 'slug', 'usos_id'),
            res_classroom,
            classroom
        )

    def test_group(self):
        group = GroupFactory()
        [res_group] = list(self.wrapper.groups())

        self.assert_declared_fields(
            ('id', 'type', 'course.id', 'teacher.id',
             'limit', 'export_usos', 'usos_nr'),
            res_group,
            group
        )
        self.assertEqual(res_group.human_readable_type,
                         group.human_readable_type())
        self.assertEqual(res_group.teacher_full_name,
                         group.get_teacher_full_name())

    def test_term(self):
        term = TermFactory()
        [res_term] = list(self.wrapper.terms())

        self.assert_declared_fields(
            ('id', 'dayOfWeek', 'group.id', 'usos_id'),
            res_term,
            term
        )

        self.assertEqual(
            res_term.start_time, term.start_time.isoformat())
        self.assertEqual(
            res_term.end_time, term.end_time.isoformat())

    def assert_declared_fields(self, fields, res_obj, expected_obj):
        """test if given fields are equal in res_obj and orig_obj.

        It can test nested objects:
            for example, one can pass fields =
                ('normal_field', 'nested_model.normal_field')
        """
        for field in fields:
            for attr in field.split("."):
                val = getattr(res_obj, attr)
                expected_val = getattr(expected_obj, attr)

            self.assertEqual(val, expected_val,
                             msg=f"field name: {field}")
