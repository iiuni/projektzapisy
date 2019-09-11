import time

from django.conf import settings
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django_rq import job

from apps.notifications.repositories import get_notifications_repository
from apps.notifications.utils import render_description
from apps.notifications.models import NotificationPreferencesStudent, NotificationPreferencesTeacher
from apps.users.models import BaseUser

THROTTLE_SECONDS = 30


@job('dispatch-notifications')
def dispatch_notifications_task(user):
    """Dispatch all pending notifications for the given user by email.

    We batch all the e-mails for the user together and send them using one SMTP
    connection. We also wait for THROTTLE_SECONDS until we let the next task in
    the work queue to send emails. This rate limiting is introduced for Gmail to
    accept our queries.
    """
    if BaseUser.is_employee(user):
        model, created = NotificationPreferencesTeacher.objects.get_or_create(user=user)
    else:
        model, created = NotificationPreferencesStudent.objects.get_or_create(user=user)

    repo = get_notifications_repository()
    pending_notifications = repo.get_unsent_for_user(user)
    if not pending_notifications:
        return

    messages = []
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

        messages.append((
            'Wiadomość od Systemu Zapisów IIUWr',  # FIXME (?)
            render_to_string('notifications/email_base.html', ctx),
            settings.MASS_MAIL_FROM,
            [user.email],
        ))
    send_mass_mail(messages, fail_silently=False)

    # Only mark the notifications as sent if the e-mails went out successfully.
    for pn in pending_notifications:
        repo.mark_as_sent(user, pn)

    time.sleep(THROTTLE_SECONDS)
