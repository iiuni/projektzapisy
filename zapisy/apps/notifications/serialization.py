import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict

from apps.notifications.datatypes import (
    Notification, TargetInfo, NotificationTargetType, NewsTargetInfo,
    CourseTargetInfo, ThesisTargetInfo
)


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
        self.target_info_serializer = DictTargetInfoSerializer()

    def serialize(self, notification: Notification) -> str:
        # since the datetime type isn't properly serialized by the
        # standard library we need to process it manually
        json_friendly_issued_on = notification.issued_on.strftime(
            self.DATE_TIME_FORMAT)

        notification_dict = {
            'id': notification.id,
            'issued_on': json_friendly_issued_on,
            'description_id': notification.description_id,
            'description_args': notification.description_args,
            'target': notification.target,
        }

        # for legacy reasons target_info should be included only if not empty
        if notification.target_info:
            notification_dict['target_info'] = (
                self.target_info_serializer.serialize(notification.target_info)
            )

        return json.dumps(notification_dict, sort_keys=True, indent=None)

    def deserialize(self, serialized: str) -> Notification:
        notification_as_dict = json.loads(serialized)
        notification_as_dict['issued_on'] = datetime.strptime(
            notification_as_dict['issued_on'], self.DATE_TIME_FORMAT)
        if 'target_info' in notification_as_dict:
            notification_as_dict['target_info'] = (
                self.target_info_serializer.deserialize(
                    notification_as_dict['target_info']))
        return Notification(**notification_as_dict)


class DictTargetInfoSerializer:

    def serialize(self, target_info: TargetInfo) -> Dict:
        return vars(target_info)

    def deserialize(sefl, target_info_as_dict: Dict) -> TargetInfo:
        target_type = target_info_as_dict['type']
        if target_type == NotificationTargetType.NEWS:
            return NewsTargetInfo()
        elif target_type == NotificationTargetType.COURSE:
            return CourseTargetInfo(target_info_as_dict['course_id'])
        elif target_type == NotificationTargetType.THESIS:
            return ThesisTargetInfo()
        else:
            return None
