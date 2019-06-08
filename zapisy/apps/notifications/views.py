from datetime import datetime

from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from apps.users.models import BaseUser
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from apps.notifications.forms import PreferencesFormStudent, PreferencesFormTeacher
from apps.notifications.models import NotificationPreferencesStudent, NotificationPreferencesTeacher
from apps.notifications.repositories import get_notifications_repository
from apps.notifications.utils import render_description

from libs.ajax_messages import AjaxFailureMessage


def index(request):
    if not request.user.is_authenticated:
        return AjaxFailureMessage.auto_render(
            'NotAuthenticated', 'Nie jesteś zalogowany.', request)
    now = datetime.now()
    repo = get_notifications_repository()
    notifications = [
        render_description(notification.description_id, notification.description_args)
        for notification in repo.get_all_for_user(request.user)
    ]
    repo.remove_all_older_than(request.user, now)

    return render(request, 'notifications/index.html', {'notifications': notifications})


@require_POST
@login_required
def preferences_save(request):
    form = create_form(request)
    if form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        post.save()
        return HttpResponseRedirect(reverse('notifications:preferences'))
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
