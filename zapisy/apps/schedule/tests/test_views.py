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
        datetime.datetime.strptime('2024-02-06', self.input_date_format)
        self.wednesday = datetime.datetime.strptime('2024-02-07', self.input_date_format)
        datetime.datetime.strptime('2024-02-08', self.input_date_format)
        self.friday = datetime.datetime.strptime('2024-02-09', self.input_date_format)
        self.saturday = datetime.datetime.strptime('2024-02-10', self.input_date_format)

        self.changed_day1 = enrollment_factories.ChangedDayForFridayFactory(day=self.monday)
        self.changed_day2 = enrollment_factories.ChangedDayForFridayFactory(day=self.wednesday)
        self.changed_day3 = enrollment_factories.ChangedDayForFridayFactory(day=self.friday)
        self.freeday1 = enrollment_factories.FreedayFactory(day=self.monday)
        self.freeday2 = enrollment_factories.FreedayFactory(day=self.wednesday)
        self.freeday3 = enrollment_factories.FreedayFactory(day=self.friday)

    def test_freeday_endpoint(self):
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        formatted_start = self.monday.strftime(self.output_date_format)
        formatted_end = self.friday.strftime(self.output_date_format)

        response = client.get('/freedays/', {
            'start': formatted_start,
            'end': formatted_end
        })

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [
            {"id": self.freeday1.id, "day": "2024-02-05"},
            {"id": self.freeday2.id, "day": "2024-02-07"},
            {"id": self.freeday3.id, "day": "2024-02-09"}])

    def test_freeday_endpoint_empty_response(self):
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        formatted_start = self.saturday.strftime(self.output_date_format)
        formatted_end = self.saturday.strftime(self.output_date_format)

        response = client.get('/freedays/', {
            'start': formatted_start,
            'end': formatted_end
        })

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [])

    def test_freeday_endpoint_missing_params_returns_404(self):
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        formatted_start = self.friday.strftime(self.output_date_format)

        response = client.get('/freedays/', {
            'start': formatted_start
        })

        self.assertEqual(response.status_code, 400)

    def test_changeddays_endpoint(self):
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        formatted_start = self.monday.strftime(self.output_date_format)
        formatted_end = self.friday.strftime(self.output_date_format)

        response = client.get('/changeddays/', {
            'start': formatted_start,
            'end': formatted_end
        })

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [
            {"id": self.changed_day1.id, "day": "2024-02-05", "weekday": self.changed_day1.weekday},
            {"id": self.changed_day2.id, "day": "2024-02-07", "weekday": self.changed_day2.weekday},
            {"id": self.changed_day3.id, "day": "2024-02-09", "weekday": self.changed_day3.weekday}
            ])

    def test_changeddays_endpoint_empty_response(self):
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        formatted_start = self.saturday.strftime(self.output_date_format)
        formatted_end = self.saturday.strftime(self.output_date_format)

        response = client.get('/changeddays/', {
            'start': formatted_start,
            'end': formatted_end
        })

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [])

    def test_changeddays_endpoint_missing_params_returns_404(self):
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        formatted_start = self.friday.strftime(self.output_date_format)

        response = client.get('/changeddays/', {
            'start': formatted_start
        })

        self.assertEqual(response.status_code, 400)
