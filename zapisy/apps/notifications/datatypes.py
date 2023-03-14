from datetime import datetime
from typing import Dict
from enum import Enum


class NotificationType(str, Enum):
    NEWS_HAS_BEEN_ADDED = 'news_has_been_added'
    NEWS_HAS_BEEN_ADDED_HIGH_PRIORITY = 'news_has_been_added_high_priority'
    NOT_PULLED_FROM_QUEUE = 'not_pulled_from_queue'
    PULLED_FROM_QUEUE = 'pulled_from_queue'
    ADDED_NEW_GROUP = 'added_new_group'
    ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER = 'assigned_to_new_group_as_teacher'
    TEACHER_HAS_BEEN_CHANGED_ENROLLED = 'teacher_has_been_changed_enrolled'
    TEACHER_HAS_BEEN_CHANGED_QUEUED = 'teacher_has_been_changed_queued'
    THESIS_VOTING_HAS_BEEN_ACTIVATED = 'thesis_voting_has_been_activated'


class TargetInfo:
    def __init__(self):
        pass


class CourseTargetInfo(TargetInfo):
    def __init__(self, course_id: str):
        super().__init__()
        self.course_id = course_id


class NewsTargetInfo(TargetInfo):
    def __init__(self):
        super().__init__()


class ThesisTargetInfo(TargetInfo):
    def __init__(self):
        super().__init__()


class Notification:

    def __init__(self, id: str, issued_on: datetime,
                 description_id: NotificationType,
                 description_args: Dict, target: str = "#",
                 target_info: TargetInfo = None):
        self.id = id
        self.issued_on = issued_on
        self.description_id = description_id
        self.description_args = description_args
        self.target = target
        self.target_info = target_info
