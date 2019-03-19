from django.core import mail
from django.test import TestCase, override_settings
from django.template.loader import render_to_string

from apps.enrollment.courses.tests.factories import GroupFactory, CourseFactory
from apps.users.tests.factories import StudentFactory
from apps.notifications.templates import NotificationType
from apps.notifications.utils import render_description
from apps.notifications.custom_signals import student_pulled

from apps.enrollment.courses.models.group import Group


@override_settings(RUN_ASYNC=False)
class NotificationsEmailTestCase(TestCase):
    def test_pulled_from_queue(self):
        student = StudentFactory()
        course = CourseFactory()
        group = GroupFactory(course=course)
        mail.outbox = []

        student_pulled.send(sender=Group, instance=group, user=student.user)

        ctx = {
            'content': render_description(NotificationType.PULLED_FROM_QUEUE, {
                "course_name": group.course.information.entity.name,
                "teacher": group.teacher.user.get_full_name(),
                "type": group.human_readable_type().lower()
            }),
            'greeting': f'Dzień dobry, {student.user.first_name}',
        }
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].body, render_to_string('notifications/email_base.html', ctx))
