import json

from django.test import TestCase
from rest_framework.test import APIClient

from apps.api.rest.v1.views import SingleVoteViewSet, SystemStateViewSet
from apps.enrollment.courses.tests.factories import CourseEntityFactory
from apps.offer.vote.models import SystemState, SingleVote
from apps.users.tests.factories import StudentFactory


class VoteSystemTests(TestCase):

    def setUp(self):
        state1 = SystemState(year=2010)
        state1.save()
        state2 = SystemState(year=2018)
        state2.save()
        students = [StudentFactory(), StudentFactory()]
        courses = [CourseEntityFactory(name="Pranie"), CourseEntityFactory(name="Zmywanie")]
        SingleVote.objects.bulk_create([
            SingleVote(state=state1, student=students[0], entity=courses[0], value=2),
            SingleVote(state=state1, student=students[1], entity=courses[0], value=0),
            SingleVote(state=state1, student=students[0], entity=courses[1], value=3),
            SingleVote(state=state1, student=students[1], entity=courses[1], value=1),
            SingleVote(state=state2, student=students[0], entity=courses[0], value=0),
            SingleVote(state=state2, student=students[1], entity=courses[0], value=0, correction=1),
            SingleVote(state=state2, student=students[0], entity=courses[1], value=3),
            SingleVote(state=state2, student=students[1], entity=courses[1], value=1, correction=2),
        ])
        self.state1 = state1
        self.state2 = state2
        self.students = students

    def test_system_states_endpoint(self):
        """Tests system state api.

        Queries the api with two SystemState instances using HTTP client.
        Check if content is JSON and contains expected data.
        There were no states in db, so we get only states created in setUp
        """
        client = APIClient()
        response = client.get('/api/v1/systemstate/')
        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(json.dumps(response.data))
        self.assertEqual(len(resp_json), 2)
        self.assertEqual(resp_json[0], {"id": 1, "state_name": "Ustawienia systemu na rok 2010"})
        self.assertEqual(resp_json[1], {"id": 2, "state_name": "Ustawienia systemu na rok 2018"})

    def test_votes_endpoint(self):
        """Tests votes endpoint.

        Checks, that only votes with value in a requested System State are
        returned and their values are computed correctly.
        """
        client = APIClient()
        response = client.get('/api/v1/votes/', {'state': self.state2.pk}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertDictEqual(response.data[0], {
            'student': self.students[1].pk,
            'course_name': "Pranie",
            'vote_points': 1
        })
        self.assertDictEqual(response.data[1], {
            'student': self.students[0].pk,
            'course_name': "Zmywanie",
            'vote_points': 3
        })
        self.assertDictEqual(response.data[2], {
            'student': self.students[1].pk,
            'course_name': "Zmywanie",
            'vote_points': 2
        })
