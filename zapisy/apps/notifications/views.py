import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from apps.notifications.datatypes import Notification
from apps.notifications.forms import PreferencesFormStudent, PreferencesFormTeacher
from apps.notifications.models import NotificationPreferencesStudent, NotificationPreferencesTeacher
from apps.notifications.repositories import get_notifications_repository
from apps.notifications.utils import render_description
from apps.notifications.serialization import DictTargetInfoSerializer


@login_required
def get_notifications(request):
    repo = get_notifications_repository()
    notifications = [
        _notification_to_dict(notification)
        for notification in repo.get_all_for_user(request.user)
    ]
    notifications.sort(key=lambda x: x['issued_on'], reverse=True)

    return JsonResponse(notifications, safe=False)


@require_POST
@login_required
def preferences_save(request):
    form = create_form(request)
    if form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        post.save()
        messages.success(request, 'Zmieniono ustawienia powiadomień')
    else:
        messages.error(request, "Wystąpił błąd, zmiany nie zostały zapisane. Proszę wypełnić formularz ponownie")
    return redirect('my-profile')


def create_form(request):
    """It is not a view itself, just factory for preferences and preferences_save."""
    if request.user.employee:
        instance, created = NotificationPreferencesTeacher.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            return PreferencesFormTeacher(request.POST, instance=instance)
        return PreferencesFormTeacher(instance=instance)

    instance, created = NotificationPreferencesStudent.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        return PreferencesFormStudent(request.POST, instance=instance)
    return PreferencesFormStudent(instance=instance)


@login_required
@require_POST
def delete_all(request):
    """Removes all user's notifications."""
    repo = get_notifications_repository()
    repo.remove_all(request.user)

    return get_notifications(request)


@login_required
@require_POST
def delete_one(request):
    """Removes one notification."""
    # Axios sends POST data in json rather than _Form-Encoded_.
    data = json.loads(request.body.decode('utf-8'))
    uuid = data.get('uuid')

    repo = get_notifications_repository()
    repo.remove_one_with_id(request.user, uuid)

    return get_notifications(request)


def _notification_to_dict(notification: Notification):
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
    return {
        'id': notification.id,
        'description':
            render_description(notification.description_id,
                               notification.description_args),
        'issued_on': notification.issued_on.strftime(DATE_TIME_FORMAT),
        'target': notification.target,
        'target_info': _get_target_info_dict(notification)
    }


def _get_target_info_dict(notification: Notification):
    if not notification.target_info:
        return None

    target_info_dict_serializer = DictTargetInfoSerializer()
    return target_info_dict_serializer.serialize(notification.target_info)
