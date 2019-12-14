
from unittest.mock import patch

from rest_framework.test import APILiveServerTestCase
from rest_framework.test import RequestsClient
from rest_framework.authtoken.models import Token

from apps.enrollment.courses.tests.factories import SemesterFactory
from apps.users.tests.factories import (StudentFactory,
                                        UserFactory,
                                        EmployeeFactory)
from apps.api.rest.v1.api_wrapper.sz_api import ZapisyApi


# @patch('apps.api.rest.v1.api_wrapper.sz_api.sz_api.requests',
#        new=RequestsClient())
class WrapperTests(APILiveServerTestCase):

    def setUp(self):
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
        result = list(self.wrapper.get_semesters())
        self.assertEqual(len(result), 1)
        res_semester = result[0]
        self.assertEqual(res_semester.id, semester.id)
        self.assertEqual(res_semester.display_name, semester.get_name())
        self.assertEqual(res_semester.year, semester.year)
        self.assertEqual(res_semester.type, semester.type)
        self.assertEqual(res_semester.usos_kod, semester.usos_kod)

    def test_student(self):
        student1, student2 = StudentFactory(), StudentFactory()
        student1.save()
        student2.save()
        result = list(self.wrapper.get_students())
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

    def test_pagination(self):
        StudentFactory.create_batch(210)
        result = list(self.wrapper.get_students())
        self.assertEqual(len(result), 210)

    def test_employee(self):
        employee = EmployeeFactory()
        [res_employee] = list(self.wrapper.get_employees())

        self.assertEqual(employee.id, res_employee.id)
        self.assertEqual(employee.consultations, res_employee.consultations)
        self.assertEqual(employee.homepage, res_employee.homepage)
        self.assertEqual(employee.room, res_employee.room)
        self.assertEqual(employee.title, res_employee.title)
        self.assertEqual(employee.usos_id, res_employee.usos_id)
