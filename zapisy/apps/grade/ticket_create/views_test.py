from datetime import datetime, timedelta
from django.test import TestCase

from apps.enrollment.courses.tests.factories import CourseFactory, GroupFactory, SemesterFactory
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.models import PrivateKey, PublicKey
from apps.users.tests.factories import StudentFactory, EmployeeFactory, UserFactory

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
    @classmethod
    def setUpClass(cls):
        super(ViewTestCase, cls).setUpClass()

    def setUp(self):
        today = datetime.now()
        self.student_user = UserFactory()
        self.student = StudentFactory(
            user=self.student_user
        )
        author_user = EmployeeFactory()

        semester = SemesterFactory(
            is_grade_active=True,
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
        group1.add_student(self.student)
        group1.save()

        poll1 = Poll(semester=semester, group=group1, author=author_user)
        poll1.save()
        poll2 = Poll(semester=semester, group=group2, author=author_user)
        poll2.save()

        priv1 = PrivateKey(poll=poll1, private_key="priv1")
        priv1.save()
        pub1 = PublicKey(poll=poll1, public_key="pub1")
        pub1.save()

        priv2 = PrivateKey(poll=poll2, private_key="priv2")
        priv2.save()
        pub2 = PublicKey(poll=poll2, public_key="pub2")
        pub2.save()

    def test_user_gets_keys_for_polls(self):
        self.client.force_login(self.student_user)
        response = self.client.get("/grade/ticket/keys_list")

        public_keys = response.context['public_keys']

        self.assertEqual(response.status_code, 200)
        self.assertEqual((len(public_keys)), 1)
        self.assertEqual(public_keys[0].public_key, "pub1")
