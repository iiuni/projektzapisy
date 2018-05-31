from datetime import datetime, timedelta
from django.test import TestCase
from django.core.urlresolvers import reverse
from Crypto.PublicKey import RSA

from apps.enrollment.courses.tests.factories import GroupFactory, SemesterFactory
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.models import PrivateKey, PublicKey
from apps.users.tests.factories import StudentFactory, EmployeeFactory, UserFactory

KEY_LENGTH = 1024


class ViewTestCase(TestCase):
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

        self.poll1 = Poll(semester=semester, group=group1, author=author_user)
        self.poll1.save()
        self.poll2 = Poll(semester=semester, group=group2, author=author_user)
        self.poll2.save()

    def test_user_gets_keys_for_polls(self):
        priv1 = PrivateKey(poll=self.poll1, private_key="priv1")
        priv1.save()
        pub1 = PublicKey(poll=self.poll1, public_key="pub1")
        pub1.save()

        priv2 = PrivateKey(poll=self.poll2, private_key="priv2")
        priv2.save()
        pub2 = PublicKey(poll=self.poll2, public_key="pub2")
        pub2.save()

        self.client.force_login(self.student_user)
        response = self.client.get(reverse("grade-ticket-keys-list"))

        self.assertEqual(response.status_code, 200)
        public_keys = response.context['public_keys']
        self.assertIsNotNone(response.context['public_keys'])
        self.assertEqual((len(public_keys)), 1)
        self.assertEqual(public_keys[0].public_key, "pub1")

    def test_user_cannot_sign_empty_tickets(self):
        self.client.force_login(self.student_user)
        response = self.client.post(reverse("grade-ticket-sign-tickets"), {'tickets': ''})

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['messages'])
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nie podano kuponów do podpisu')

    def test_sign_user_tickets(self):
        rsa = RSA.generate(KEY_LENGTH)
        private_key = rsa.exportKey()
        public_key = rsa.publickey().exportKey()

        priv1 = PrivateKey(poll=self.poll1, private_key=private_key)
        priv1.save()
        pub1 = PublicKey(poll=self.poll1, public_key=public_key)
        pub1.save()

        self.client.force_login(self.student_user)
        response = self.client.post(reverse("grade-ticket-sign-tickets"),
                                    {'tickets': 'poll_id:1\r\n1234567890\r\n**********************************'})

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['signatures'])

        signatures = response.context['signatures']
        self.assertEqual(len(signatures), 1)
        self.assertEqual(signatures[0].poll_id, 1)
        self.assertIsNotNone(signatures[0].signature)
