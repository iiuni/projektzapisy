from django import test
from django.core import mail

from apps.news.models import News, PriorityChoices
from apps.users.tests.factories import EmployeeFactory, StudentFactory

from ..models import NotificationPreferencesStudent, NotificationPreferencesTeacher


@test.override_settings(RUN_ASYNC=False)
class PreferencesTestCase(test.TestCase):
    def setUp(self):
        self.s1 = StudentFactory()
        self.s2 = StudentFactory()
        self.s3 = StudentFactory(is_active=False)
        self.t1 = EmployeeFactory()
        self.t2 = EmployeeFactory()

        NotificationPreferencesStudent.objects.create(user=self.s1.user, news_has_been_added=True)
        NotificationPreferencesStudent.objects.create(user=self.s2.user, news_has_been_added=False)
        NotificationPreferencesStudent.objects.create(user=self.s3.user, news_has_been_added=True)
        NotificationPreferencesTeacher.objects.create(user=self.t1.user, news_has_been_added=True)
        NotificationPreferencesTeacher.objects.create(user=self.t2.user, news_has_been_added=False)

    def inspect_outbox(self, outbox):
        """Lists recipients of outgoing e-mail notifications."""
        for m in outbox:
            self.assertEqual(len(m.to), 1)
            yield m.to[0]

    def test_regular_news(self):
        """Tests that users' preferences are adhered to when a news is added.

        But only active users and only for regular news.
        """
        n = News.objects.create(title="Tytuł zwykłego newsa",
                                body="Bardzo ciekawa wiadomość",
                                author=self.t1.user)
        self.assertCountEqual(self.inspect_outbox(mail.outbox),
                              [self.s1.user.email, self.t1.user.email])

    def test_urgent_news(self):
        """Tests that students' preferences are not adhered to when an urgent news is added.

        But the employees still have a say.
        """
        n = News.objects.create(title="Tytuł pilnego newsa",
                                body="Bardzo ciekawa i ważna wiadomość",
                                author=self.t1.user,
                                priority=PriorityChoices.HIGH)
        self.assertCountEqual(self.inspect_outbox(mail.outbox),
                              [self.s1.user.email, self.s2.user.email, self.t1.user.email])
