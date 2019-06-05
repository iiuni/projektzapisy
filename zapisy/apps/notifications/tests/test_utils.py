from django.test import TestCase

from apps.notifications.templates import NotificationType
from apps.notifications.exceptions import DescriptionArgumentMissingException
from apps.notifications.utils import render_description


class NotificationsUtilsTestCase(TestCase):

    def test_added_new_group_renders_properly(self):
        descr_args = {'course_name': 'matematyka dyskretna', 'teacher': 'Jan Kowalski'}

        rendered = render_description(
            NotificationType.ADDED_NEW_GROUP, descr_args)

        self.assertEqual(
            'W przedmiocie "matematyka dyskretna" została dodana grupa prowadzona przez Jan Kowalski.',
            rendered)

    def test_assigned_to_new_group_as_teacher_renders_properly(self):
        descr_args = {'course_name': 'matematyka dyskretna'}

        rendered = render_description(
            NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER, descr_args)

        self.assertEqual(
            'Przydzielono Cię do grupy przedmiotu "matematyka dyskretna" jako prowadzącego.',
            rendered)

    def test_trying_to_render_with_insufficient_arguments_raises(self):
        descr_args = {}

        with self.assertRaises(DescriptionArgumentMissingException):
            rendered = render_description(
                NotificationType.TEACHER_HAS_BEEN_CHANGED_ENROLLED, descr_args)
