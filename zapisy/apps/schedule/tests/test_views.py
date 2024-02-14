import datetime

from rest_framework.test import APIClient
from django.test import TestCase

from apps.users.tests.factories import UserFactory
import apps.enrollment.courses.tests.factories as enrollment_factories


class ChangedDayFreedayEndpointTestCase(TestCase):

    def setUp(self):
        self.staff_member = UserFactory(is_staff=True)
        self.output_date_format = "%Y-%m-%dT%H:%M:%S.000Z"
        self.input_date_format = "%Y-%m-%d"
        self.monday = datetime.datetime.strptime('2024-02-05', self.input_date_format)
        self.tuesday = datetime.datetime.strptime('2024-02-06', self.input_date_format)
        self.wednesday = datetime.datetime.strptime('2024-02-07', self.input_date_format)
        self.thursday = datetime.datetime.strptime('2024-02-08', self.input_date_format)
        self.friday = datetime.datetime.strptime('2024-02-09', self.input_date_format)

        enrollment_factories.ChangedDayForFridayFactory(day=self.wednesday)
        enrollment_factories.ChangedDayForFridayFactory(day=self.thursday)
        enrollment_factories.FreedayFactory(day=self.monday)
        enrollment_factories.FreedayFactory(day=self.tuesday)

    def test_freeday_endpoint(self):
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        formatted_start = self.monday.strftime(self.output_date_format)
        formatted_end = self.friday.strftime(self.output_date_format)

        response = client.get('/freeday/', {
            'start': formatted_start,
            'end': formatted_end
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['day'], self.monday.strftime(self.input_date_format))
        self.assertEqual(response.data[1]['day'], self.tuesday.strftime(self.input_date_format))

    def test_freeday_endpoint_empty_response(self):
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        formatted_start = self.friday.strftime(self.output_date_format)
        formatted_end = self.friday.strftime(self.output_date_format)

        response = client.get('/freeday/', {
            'start': formatted_start,
            'end': formatted_end
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_changeday_endpoint(self):
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        formatted_start = self.monday.strftime(self.output_date_format)
        formatted_end = self.friday.strftime(self.output_date_format)

        response = client.get('/changeday/', {
            'start': formatted_start,
            'end': formatted_end
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['day'], self.wednesday.strftime(self.input_date_format))
        self.assertEqual(response.data[1]['day'], self.thursday.strftime(self.input_date_format))
        self.assertEqual(response.data[0]['weekday'], '5')
        self.assertEqual(response.data[1]['weekday'], '5')

    def test_changeday_endpoint_empty_response(self):
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        formatted_start = self.friday.strftime(self.output_date_format)
        formatted_end = self.friday.strftime(self.output_date_format)

        response = client.get('/changeday/', {
            'start': formatted_start,
            'end': formatted_end
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
