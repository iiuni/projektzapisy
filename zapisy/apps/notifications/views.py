from datetime import datetime

import json
from django.core.serializers.json import DjangoJSONEncoder

from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from apps.users.models import BaseUser
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from apps.notifications.forms import PreferencesFormStudent, PreferencesFormTeacher
from apps.notifications.models import NotificationPreferencesStudent, NotificationPreferencesTeacher
from apps.notifications.repositories import get_notifications_repository, RedisNotificationsRepository
from apps.notifications.utils import render_description
from libs.ajax_messages import AjaxFailureMessage
from apps.users import views


@login_required
def get_notifications(request):
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
    now = datetime.now()
    repo = get_notifications_repository()
    notifications = [
        [ render_description(notification.description_id, notification.description_args), notification.issued_on.strftime(DATE_TIME_FORMAT) ]
        for notification in repo.get_all_for_user(request.user)
    ]
    key_list = [ i for i in range(len(notifications))]
    d = [[key]+value for (key, value) in zip(key_list, notifications)]

    return HttpResponse(json.dumps(d), content_type="application/json")


@login_required
def get_counter(request):
    repo = get_notifications_repository()
    notification_counter = repo.get_count_for_user(request.user)

    return HttpResponse(json.dumps(notification_counter), content_type="application/json")


@require_POST
@login_required
def preferences_save(request):
    form = create_form(request)
    if form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        post.save()
        return HttpResponseRedirect(reverse(views.my_profile))
    else:
        messages.error(request, "Wystąpił błąd, zmiany nie zostały zapisane. Proszę wypełnić formularz ponownie")


def preferences(request):
    form = create_form(request)
    return render(request, 'notifications/preferences.html', {'form': form})


def create_form(request):
    """It is not a view itself, just factory for preferences and preferences_save"""
    if BaseUser.is_employee(request.user):
        instance, created = NotificationPreferencesTeacher.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            return PreferencesFormTeacher(request.POST, instance=instance)
        return PreferencesFormTeacher(instance=instance)

    instance, created = NotificationPreferencesStudent.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        return PreferencesFormStudent(request.POST, instance=instance)
    return PreferencesFormStudent(instance=instance)


@login_required
def deleteAll(request):
    """Removes all user's notifications"""
    now = datetime.now()
    repo = get_notifications_repository()
    repo.remove_all_older_than(request.user,now)

    return get_notifications(request)


@login_required
def deleteOne(request):
    """Removes one notification"""
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    issued_on = request.GET.get('issued_on')
    issued_on = datetime.strptime(issued_on, DATE_TIME_FORMAT)

    repo = get_notifications_repository()
    t = repo.remove_one_issued_on(request.user, issued_on)

    return get_notifications(request)
