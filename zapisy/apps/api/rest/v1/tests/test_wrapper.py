import json
from pprint import pprint
from unittest.mock import patch
import requests

from rest_framework.test import APILiveServerTestCase
from rest_framework.test import RequestsClient
from rest_framework.authtoken.models import Token

from apps.enrollment.courses.tests.factories import (CourseInstanceFactory,
                                                     SemesterFactory)
from apps.offer.proposal.tests.factories import ProposalFactory
from apps.offer.vote.models import SystemState, SingleVote
from apps.users.tests.factories import (EmployeeFactory,
                                        StudentFactory,
                                        UserFactory)
from apps.api.rest.v1.api_wrapper.sz_api import ZapisyApi


@patch('apps.api.rest.v1.api_wrapper.sz_api.sz_api.requests',
       new=RequestsClient())
class WrapperTests(APILiveServerTestCase):

    def setUp(self):
        self.staff_member = UserFactory(is_staff=True)
        token = Token.objects.create(user=self.staff_member)
        self.wrapper = ZapisyApi("Token " + token.key, "http://testserver/api/v1/")

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
