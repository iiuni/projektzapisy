from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django_rq import job

from apps.notifications.repositories import get_notifications_repository
from apps.notifications.utils import render_description
from apps.notifications.models import NotificationPreferencesStudent, NotificationPreferencesTeacher
from apps.users.models import BaseUser


@job('dispatch-notifications')
def dispatch_notifications_task(user):
    """Dispatch all pending notifications for the given user by email.

    It's purposely designed around processing all notification_s_
    at a time instead of handling them one by one
    so we can introduce a rate-limit and/or batch them together
    should there ever be a need to do so.
    """
    if BaseUser.is_employee(user):
        model, created = NotificationPreferencesTeacher.objects.get_or_create(user=user)
    else:
        model, created = NotificationPreferencesStudent.objects.get_or_create(user=user)

    repo = get_notifications_repository()
    pending_notifications = repo.get_unsent_for_user(user)

    for pn in pending_notifications:
        # User controls in account settings
        # what notifications will be send
        if not getattr(model, pn.description_id):
            continue

        ctx = {
            'content': render_description(
                pn.description_id, pn.description_args),
            'greeting': f'Dzień dobry, {user.first_name}',
        }

        send_mail(
            'Wiadomość od Systemu Zapisów IIUWr',  # FIXME (?)
            render_to_string('notifications/email_base.html', ctx),
            settings.MASS_MAIL_FROM,
            [user.email])

        repo.mark_as_sent(user, pn)
