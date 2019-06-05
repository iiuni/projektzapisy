from django.test import SimpleTestCase
import random
from datetime import datetime

from apps.notifications.datatypes import Notification
from apps.notifications.serialization import JsonNotificationSerializer


class NotificationsSerializationTestCase(SimpleTestCase):

    def test_json_serialization_is_reversible(self):
        before = Notification("123456789", datetime(2019, 5, 5, 20, 35, 0, 0), 'aaa{foo}bbb', {'foo': 'bar'})
        serialized = JsonNotificationSerializer().serialize(before)
        after = JsonNotificationSerializer().deserialize(serialized)

        self.assertEqual(before.issued_on, after.issued_on)
        self.assertEqual(before.target, after.target)
        self.assertEqual(before.description_id, after.description_id)
        self.assertEqual(before.description_args, after.description_args)
        self.assertEqual(before.id, after.id)
