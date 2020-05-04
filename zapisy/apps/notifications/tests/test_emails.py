from django.core import mail
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.utils.html import strip_tags

from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.tests.factories import GroupFactory
from apps.notifications.custom_signals import teacher_changed
from apps.notifications.templates import NotificationType
from apps.notifications.utils import render_description
from apps.users.tests.factories import EmployeeFactory


@override_settings(RUN_ASYNC=False)
class NotificationsEmailTestCase(TestCase):
    def test_teacher_changed(self):
        teacher = EmployeeFactory()
        group = GroupFactory()
        mail.outbox = []

        teacher_changed.send(sender=Group, instance=group)

        ctx = {
            'content':
            render_description(
                NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER, {
                    "course_name": group.course.name
                }),
            'greeting':
            f'Dzień dobry, {teacher.user.first_name}',
        }
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].body,
                         strip_tags(render_to_string('notifications/email_base.html', ctx)))
