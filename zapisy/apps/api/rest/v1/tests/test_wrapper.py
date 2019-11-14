import json
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import RequestsClient
from rest_framework.authtoken.models import Token


from apps.enrollment.courses.tests.factories import (CourseInstanceFactory, SemesterFactory)
from apps.offer.proposal.tests.factories import ProposalFactory
from apps.offer.vote.models import SystemState, SingleVote
from apps.users.tests.factories import EmployeeFactory, StudentFactory, UserFactory
from apps.api.rest.v1.api_wrapper.sz_api import ZapisyApi



class WrapperTests(TestCase):

    @patch('apps.api.rest.v1.api_wrapper.sz_api.sz_api.requests', new_callable=RequestsClient)
    def setUp(self,):
        self.staff_member = UserFactory(is_staff=True)
        client.force_authenticate(user=self.staff_member)
        self.wrapper = ZapisyApi("Token " + token.key, "http://testserver/")

    def test_init(self):
        print(self.wrapper.get_semesters())
