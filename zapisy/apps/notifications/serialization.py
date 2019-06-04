from abc import ABC, abstractmethod
from datetime import datetime
import json

from apps.notifications.datatypes import Notification


class NotificationSerializer(ABC):

    @abstractmethod
    def serialize(self, notification: Notification) -> str:
        pass

    @abstractmethod
    def deserialize(self, serialized: str) -> Notification:
        pass


class JsonNotificationSerializer(NotificationSerializer):

    def __init__(self):
        # year-month-day hour:minute:second.microsecond
        self.DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def serialize(self, notification: Notification) -> str:
        # since the datetime type isn't properly serialized by the
        # standard library we need to process it manually
        json_friendly_issued_on = notification.issued_on.strftime(
            self.DATE_TIME_FORMAT)
        return json.dumps({
            'id': notification.id,
            'issued_on': json_friendly_issued_on,
            'description_id': notification.description_id,
            'description_args': notification.description_args,
            'target': notification.target,
        }, sort_keys=True, indent=None)

    def deserialize(self, serialized: str) -> Notification:
        notification_as_dict = json.loads(serialized)
        notification_as_dict['issued_on'] = datetime.strptime(
            notification_as_dict['issued_on'], self.DATE_TIME_FORMAT)
        return Notification(**notification_as_dict)
