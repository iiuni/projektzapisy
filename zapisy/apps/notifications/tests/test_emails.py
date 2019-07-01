from django.core import mail
from django.template.loader import render_to_string
from django.test import TestCase, override_settings

from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.tests.factories import CourseFactory, GroupFactory
from apps.notifications.custom_signals import teacher_changed
from apps.notifications.templates import NotificationType
from apps.notifications.utils import render_description
from apps.users.tests.factories import EmployeeFactory


@override_settings(RUN_ASYNC=False)
class NotificationsEmailTestCase(TestCase):
    def test_teacher_changed(self):
        teacher = EmployeeFactory()
        course = CourseFactory()
        group = GroupFactory(course=course)
        mail.outbox = []

        teacher_changed.send(sender=Group, instance=group)

        ctx = {
            'content':
            render_description(
                NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER, {
                    "course_name": group.course.information.entity.name
                }),
            'greeting':
            f'Dzień dobry, {teacher.user.first_name}',
        }
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].body, render_to_string('notifications/email_base.html', ctx))
