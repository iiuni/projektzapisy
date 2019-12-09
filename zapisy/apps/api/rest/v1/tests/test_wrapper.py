
from pprint import pprint
from unittest.mock import patch

from rest_framework.test import APILiveServerTestCase
from rest_framework.test import RequestsClient
from rest_framework.authtoken.models import Token

from apps.enrollment.courses.tests.factories import SemesterFactory
from apps.users.tests.factories import (StudentFactory,
                                        UserFactory)
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

        token = Token.objects.create(user=UserFactory(is_staff=True))
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
        pprint(result)
