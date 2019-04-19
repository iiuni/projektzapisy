import json
from apps.notifications.repositories import get_notifications_repository
from apps.notifications.utils import render_description


def notification_ico(request):
    repo = get_notifications_repository()
    notifications = [
        render_description(notification.description_id, notification.description_args)
        for notification in repo.get_all_for_user(request.user)
    ]
    notification_counter = repo.get_count_for_user(request.user)

    return {
        "notification_counter": notification_counter,
        #"notification_counter_json": json.dumps(notification_counter),
        "notifications_json": json.dumps(notifications),
    }
