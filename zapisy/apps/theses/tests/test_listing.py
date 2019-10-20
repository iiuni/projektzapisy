from typing import Optional

from rest_framework import status
from django.urls import reverse

from apps.users.models import BaseUser
from ..models import ThesisStatus
from ..enums import NOT_READY_STATUSES
from .base import ThesesBaseTestCase, PAGE_SIZE


class ThesesListingTestCase(ThesesBaseTestCase):
    """Tests theses listing functionality: is the limit setting respected,
    are permissions granted correctly"""
    @classmethod
    def setUpTestData(cls):
        super(ThesesListingTestCase, cls).setUpTestData()
        cls.create_theses()

    @classmethod
    def create_theses(cls):
        cls.num_theses = PAGE_SIZE
        cls.theses = [cls.make_thesis() for _ in range(cls.num_theses)]

    def _check_theses_response_data(self, data, expected_len: Optional[int]=None):
        self.assertTrue(isinstance(data, dict))
        self.assertTrue("count" in data)
        self.assertTrue("results" in data)
        results = data["results"]
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), PAGE_SIZE if expected_len is None else expected_len)

    def _test_user_can_list_theses(self, user: BaseUser, expected_len: Optional[int]=None):
        self.login_as(user)
        response = self.get_response_with_data()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_theses_response_data(response.data, expected_len)

    def test_logged_in_can_list_theses(self):
        self._test_user_can_list_theses(self.get_random_emp())
        self._test_user_can_list_theses(self.get_random_board_member())
        self._test_user_can_list_theses(self.get_admin())
        # Students cannot see theses that are not "ready"
        ready = list(filter(lambda t: ThesisStatus(t.status) not in NOT_READY_STATUSES, self.theses))
        self._test_user_can_list_theses(
            self.get_random_student(),
            min(len(ready), PAGE_SIZE)
        )

    def test_logged_out_cannot_list_theses(self):
        response = self.client.get(reverse("theses:theses-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
