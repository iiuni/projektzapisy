from datetime import datetime
from typing import Dict, Union
from enum import Enum


class NewsNotificationType(str, Enum):
    NEWS_HAS_BEEN_ADDED = 'news_has_been_added'
    NEWS_HAS_BEEN_ADDED_HIGH_PRIORITY = 'news_has_been_added_high_priority'


class CourseNotificationType(str, Enum):
    NOT_PULLED_FROM_QUEUE = 'not_pulled_from_queue'
    PULLED_FROM_QUEUE = 'pulled_from_queue'
    ADDED_NEW_GROUP = 'added_new_group'
    ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER = 'assigned_to_new_group_as_teacher'
    TEACHER_HAS_BEEN_CHANGED_ENROLLED = 'teacher_has_been_changed_enrolled'
    TEACHER_HAS_BEEN_CHANGED_QUEUED = 'teacher_has_been_changed_queued'


class ThesisNotificationType(str, Enum):
    THESIS_VOTING_HAS_BEEN_ACTIVATED = 'thesis_voting_has_been_activated'


NotificationType = Union[
    NewsNotificationType, CourseNotificationType, ThesisNotificationType
]


class NotificationTargetType(str, Enum):
    NEWS = 'news'
    COURSE = 'course'
    THESIS = 'thesis'


class Notification:

    def __init__(self, id: str, issued_on: datetime,
                 description_id: NotificationType,
                 description_args: Dict, target: str = "#"):
        self.id = id
        self.issued_on = issued_on
        self.description_id = description_id
        self.description_args = description_args
        self.target = target

    @property
    def is_course_related(self):
        return _belongs_to_enum(self.description_id, CourseNotificationType)

    @property
    def is_news_related(self):
        return _belongs_to_enum(self.description_id, NewsNotificationType)

    @property
    def is_thesis_related(self):
        return _belongs_to_enum(self.description_id, ThesisNotificationType)


def _belongs_to_enum(value, enum):
    return value in set(id.value for id in enum)
