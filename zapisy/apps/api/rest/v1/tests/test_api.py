import json

from django.test import TestCase
from rest_framework.test import APIClient

from apps.enrollment.courses.tests.factories import (CourseInstanceFactory, SemesterFactory)
from apps.offer.proposal.tests.factories import ProposalFactory
from apps.offer.vote.models import SystemState, SingleVote
from apps.users.tests.factories import EmployeeFactory, StudentFactory, UserFactory


class VoteSystemTests(TestCase):

    def setUp(self):
        state1 = SystemState(year="2010/11")
        state1.save()
        state2 = SystemState(year="2018/19")
        state2.save()
        students = [StudentFactory(), StudentFactory()]
        proposals = [ProposalFactory(name="Pranie"), ProposalFactory(name="Zmywanie")]
        SingleVote.objects.bulk_create([
            SingleVote(state=state1, student=students[0], proposal=proposals[0], value=2),
            SingleVote(state=state1, student=students[1], proposal=proposals[0], value=0),
            SingleVote(state=state1, student=students[0], proposal=proposals[1], value=3),
            SingleVote(state=state1, student=students[1], proposal=proposals[1], value=1),
            SingleVote(state=state2, student=students[0], proposal=proposals[0], value=0),
            SingleVote(
                state=state2, student=students[1], proposal=proposals[0], value=0, correction=1),
            SingleVote(state=state2, student=students[0], proposal=proposals[1], value=3),
            SingleVote(
                state=state2, student=students[1], proposal=proposals[1], value=1, correction=2),
        ])
        self.state1 = state1
        self.state2 = state2
        self.students = students
        self.employee = EmployeeFactory()

        self.semester = SemesterFactory()
        self.course_instance = CourseInstanceFactory(offer=proposals[1], semester=self.semester)

        self.staff_member = UserFactory(is_staff=True)

    def test_authorisation(self):
        """Tests API permissions.

        Checks that an unauthorised caller or a student is not able to perform
        API calls.
        """
        client = APIClient()
        response = client.get('/api/v1/systemstate/')
        self.assertEqual(response.status_code, 401)

        client.force_authenticate(user=self.students[0].user)
        response = client.get('/api/v1/systemstate/')
        self.assertEqual(response.status_code, 403)

    def test_system_states_endpoint(self):
        """Tests system state api.

        Queries the api with two SystemState instances using HTTP client.
        Check if content is JSON and contains expected data.
        There were no states in db, so we get only states created in setUp
        """
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        response = client.get('/api/v1/systemstate/')
        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(json.dumps(response.data))
        self.assertEqual(len(resp_json), 2)
        self.assertEqual(resp_json[0], {
            "id": self.state1.pk,
            "state_name": "Ustawienia systemu na rok akademicki 2010/11"
        })
        self.assertEqual(resp_json[1], {
            "id": self.state2.pk,
            "state_name": "Ustawienia systemu na rok akademicki 2018/19"
        })

    def test_votes_endpoint(self):
        """Tests votes endpoint.

        Checks, that only votes with value in a requested System State are
        returned and their values are computed correctly.
        """
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        response = client.get('/api/v1/votes/', {'state': self.state2.pk}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        self.assertCountEqual(response.data['results'], [
            {
                'student': self.students[1].pk,
                'course_name': "Pranie",
                'vote_points': 1
            }, {
                'student': self.students[0].pk,
                'course_name': "Zmywanie",
                'vote_points': 3
            }, {
                'student': self.students[1].pk,
                'course_name': "Zmywanie",
                'vote_points': 2
            }
        ])

    def test_can_set_semester_usos_kod(self):
        """Tests semester endpoint.

        Checks that the user is able to set/modify the `usos_kod` field of a
        semester.
        """
        client = APIClient()
        client.force_authenticate(user=self.staff_member)
        semester_list_response = client.get('/api/v1/semesters/')
        self.assertEqual(semester_list_response.data, [{
            'id': self.semester.pk,
            'display_name': self.semester.get_name(),
            'usos_kod': None,
        }])

        semester_change_response = client.patch(f'/api/v1/semesters/{self.semester.pk}/',
                                                {'usos_kod': 'Nowy Kod USOS'})
        self.assertEqual(semester_change_response.status_code, 200)
        self.assertDictEqual(semester_change_response.data, {
            'id': self.semester.pk,
            'display_name': self.semester.get_name(),
            'usos_kod': 'Nowy Kod USOS',
        })
        self.semester.refresh_from_db()
        self.assertEqual(self.semester.usos_kod, 'Nowy Kod USOS')

    def test_can_set_course_usos_kod(self):
        """Tests course endpoint.

        Checks that the user is able to set/modify the `usos_kod` field of a
        CourseInstance object.
        """
        client = APIClient()
        client.force_authenticate(user=self.staff_member)

        response = client.get(f'/api/v1/courses/?semester={self.semester.pk}')
        self.assertEqual(response.data['count'], 1)
        course_dict = response.data['results'][0]
        self.assertEqual(course_dict['name'], self.course_instance.name)
        self.assertEqual(course_dict['usos_kod'], '')

        response = client.patch(f'/api/v1/courses/{self.course_instance.id}/', {
            'usos_kod': '12-SM-ZMYWANIE',
        })
        self.assertEqual(response.status_code, 200)
        self.course_instance.refresh_from_db()
        self.assertEqual(self.course_instance.usos_kod, '12-SM-ZMYWANIE')

    def test_set_employee_consultations_permissions(self):
        """Tests employee endpoint permissions.

        Checks that the user is able to modify the `usos_id` field but is not
        able to set/modify the `consultations` field of an employee.

        The REST API does not explicitly forbid these requests. It just does not
        change the field if it should not be changed.
        """
        client = APIClient()
        client.force_authenticate(user=self.staff_member)

        response = client.patch(f'/api/v1/employees/{self.employee.pk}/', {'usos_id': 17})
        self.assertEqual(response.status_code, 200)
        self.employee.refresh_from_db()

        response = client.patch(f'/api/v1/employees/{self.employee.pk}/',
                                {'consultations': "Wtorek godz. 17"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['consultations'], None)
        self.employee.refresh_from_db()
        self.assertNotEqual(self.employee.consultations, "Wtorek godz. 17")
