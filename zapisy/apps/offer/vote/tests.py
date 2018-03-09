from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.db import connection

from apps.offer.vote.models.system_state import SystemState
from apps.users.models import Student

from apps.users.tests.factories import StudentFactory


def create_active_system_state():
    SystemState.objects.create(
        vote_beg=timezone.now() - timezone.timedelta(10),
        vote_end=timezone.now() + timezone.timedelta(10),
    )


def create_inactive_system_state_in_past():
    SystemState.objects.create(
        vote_beg=timezone.now() - timezone.timedelta(30),
        vote_end=timezone.now() - timezone.timedelta(10),
    )


def create_inactive_system_state_in_future():
    SystemState.objects.create(
        vote_beg=timezone.now() + timezone.timedelta(30),
        vote_end=timezone.now() + timezone.timedelta(50),
    )


class VoteLinkTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.VOTE_LINK = '<a href="%s">głosuj</a>' % reverse('vote')

        cls.s1 = StudentFactory()
        cls.s2 = StudentFactory(status=1)

        sql_calls = [
            """
                CREATE TABLE courses_studentpointsview (
                    value smallint,
                    student_id integer,
                    entity_id integer
                );
            """
            ]

        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)
            connection.commit()

    @classmethod
    def tearDownClass(cls):
        cls.s1.delete()
        cls.s2.delete()
        sql_calls = [
            "DROP TABLE courses_studentpointsview;",
        ]
        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)
            connection.commit()

    def generic_voting_active_view_test_case(self, urlname):
        create_active_system_state()
        response = self.client.get(reverse(urlname))
        self.assertEqual(response.context['is_voting_active'], True)
        self.assertContains(response, self.VOTE_LINK, 1, html=True)

    def _generic_voting_inactive_view_test_case(self, urlname):
        response = self.client.get(reverse(urlname))
        self.assertEqual(response.context['is_voting_active'], False)
        self.assertNotContains(response, self.VOTE_LINK, html=True)

    def generic_voting_inactive_view_past_test_case(self, urlname):
        create_inactive_system_state_in_past()
        self._generic_voting_inactive_view_test_case(urlname)

    def generic_voting_inactive_view_future_test_case(self, urlname):
        create_inactive_system_state_in_future()
        self._generic_voting_inactive_view_test_case(urlname)

    def test_vote_link_in_vote_view_when_system_is_active(self):
        self.client.login(username=self.s1.user.username, password='test')
        self.generic_voting_active_view_test_case('vote-view')

    def test_vote_link_in_vote_view_when_system_is_active_baduser(self):
        self.client.login(username=self.s2.user.username, password='test')
        create_active_system_state()
        response = self.client.get(reverse('vote-view'), follow=True)
        self.assertNotContains(response, self.VOTE_LINK, html=True)

    def test_vote_link_in_vote_view_when_system_is_inactive_in_past(self):
        self.client.login(username=self.s1.user.username, password='test')
        self.generic_voting_inactive_view_past_test_case('vote-view')

    def test_vote_link_in_vote_view_when_system_is_inactive_in_future(self):
        self.client.login(username=self.s1.user.username, password='test')
        self.generic_voting_inactive_view_future_test_case('vote-view')

    def test_vote_link_in_vote_summary_when_system_is_active(self):
        self.client.login(username=self.s1.user.username, password='test')
        self.generic_voting_active_view_test_case('vote-summary')

    def test_vote_link_in_vote_summary_when_system_is_inactive_in_past(self):
        self.client.login(username=self.s1.user.username, password='test')
        self.generic_voting_inactive_view_past_test_case('vote-summary')

    def test_vote_link_in_vote_summary_when_system_is_inactive_in_future(self):
        self.client.login(username=self.s1.user.username, password='test')
        self.generic_voting_inactive_view_future_test_case('vote-summary')
