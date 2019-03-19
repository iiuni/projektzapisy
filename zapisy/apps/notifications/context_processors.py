from apps.notifications.repositories import get_notifications_repository


def notification_ico(request):
    repo = get_notifications_repository()
    return {"notification_counter": repo.get_count_for_user(request.user)}
