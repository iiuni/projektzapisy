import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict
from enum import Enum

from apps.notifications.datatypes import (
    Notification, TargetInfo, NewsTargetInfo,
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


class TargetTypes(str, Enum):
    NEWS = 'news'
    COURSE = 'course'
    THESIS = 'thesis'


class DictTargetInfoSerializer:

    def serialize(self, target_info: TargetInfo) -> Dict:
        target_info_as_dict = vars(target_info)
        if isinstance(target_info, NewsTargetInfo):
            target_info_as_dict['type'] = TargetTypes.NEWS
        elif isinstance(target_info, CourseTargetInfo):
            target_info_as_dict['type'] = TargetTypes.COURSE
        elif isinstance(target_info, ThesisTargetInfo):
            target_info_as_dict['type'] = TargetTypes.THESIS
        else:
            raise TypeError("Unknown type of TargetInfo")
        return target_info_as_dict

    def deserialize(sefl, target_info_as_dict: Dict) -> TargetInfo:
        target_type = target_info_as_dict['type']
        if target_type == TargetTypes.NEWS:
            return NewsTargetInfo()
        elif target_type == TargetTypes.COURSE:
            return CourseTargetInfo(target_info_as_dict['course_id'])
        elif target_type == TargetTypes.THESIS:
            return ThesisTargetInfo()
        else:
            raise TypeError("Unknown type of TargetInfo")
