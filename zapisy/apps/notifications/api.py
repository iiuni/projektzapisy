from typing import List

from django.conf import settings
from django.contrib.auth.models import User

from apps.notifications.datatypes import Notification
from apps.notifications.repositories import get_notifications_repository
from apps.notifications.tasks import dispatch_notifications_task


def notify_user(user: User, notification: Notification, repo=None):
    """Dispatch one notification to one user.

    Repository saves notification to redis.
    Then we queue user to send (regarding preferences)
    all his pending notifications, including this one.

    Notifications repository can be initialised outside for perfomance reasons.
    """
    if repo is None:
        repo = get_notifications_repository()
    repo.save(user, notification)
    if not settings.RUN_ASYNC:
        dispatch_notifications_task(user)
    else:
        dispatch_notifications_task.delay(user)


def notify_selected_users(users: List[User], notification: Notification):
    """Dispatch one notification to multiple users."""
    repo = get_notifications_repository()
    for user in users:
        notify_user(user, notification, repo)
