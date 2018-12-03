from django.shortcuts import render

from apps.notifications2.repositories import get_notifications_repository
from apps.notifications2.utils import render_description


def index(request):

    repo = get_notifications_repository()

    notifications = [
        render_description(notification.description_id, notification.description_args)
        for notification in repo.get_all_for_user(request.user)
    ]

    return render(request, 'notifications2/index.html', {'notifications': notifications})
