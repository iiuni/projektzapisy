import django

django.setup()

from datetime import datetime, timedelta
from django.test import TestCase

from apps.enrollment.courses.tests.factories import CourseFactory, GroupFactory, SemesterFactory
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.models import PrivateKey, PublicKey
from apps.users.tests.factories import StudentFactory

KEY_LENGTH = 256

"""
1. create user
2. create courses
3. create enrollment record
4. create polls for course groups
5. create keys for polls
6. try flows
"""


class ViewTestCase(TestCase):
    def setUp(self):
        print("starting setup")
        student = StudentFactory()
        course = CourseFactory()
        today = datetime.now()
        semester = SemesterFactory(
            records_opening=today + timedelta(days=-1),
            records_closing=today + timedelta(days=6),
            records_ects_limit_abolition=today + timedelta(days=3))
        group1 = GroupFactory(
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6)
        )
        group2 = GroupFactory(
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6)
        )
        print("created groups")
        group1.enroll_student(student)
        poll1 = Poll(semester=semester, group=group1)
        poll1.save()
        print("saved polls")
        poll2 = Poll(semester=semester, group=group2)
        poll2.save()

        priv1 = PrivateKey(poll=poll1, private_key="priv1")
        pub1 = PublicKey(poll=poll1, public_key="pub1")

        priv2 = PrivateKey(poll=poll2, private_key="priv2")
        pub2 = PublicKey(poll=poll2, public_key="pub2")

    def test_user_gets_keys_for_polls(self):
        print("starting test case")
        self.client.login("testuser_0", "test")
        response = self.client.get("/grade/ticket/keys_list")
        self.assertEqual(response.status_code, 200)
