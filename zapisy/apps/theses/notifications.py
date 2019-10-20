"""
Implements theses email notifications
"""
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

from apps.users.models import Employee
from .system_settings import get_master_rejecter

SUBJECT_PREFIX = "[Zapisy – prace dyplomowe] "

ACCEPTED_SUBJECT = SUBJECT_PREFIX + "Temat zaakceptowany"
ACCEPTED_BODY = "Temat pracy „{}” został zaakceptowany."

REJECTED_SUBJECT = SUBJECT_PREFIX + "Temat zwrócony do poprawek"
REJECTED_BODY = "Temat pracy „{}” został zwrócony do poprawek. Podano następujący powód:\n\n{}"

REJECTING_VOTE_CAST_SUBJECT = SUBJECT_PREFIX + "Zgłoszono uwagi do tematu"
REJECTING_VOTE_CAST_BODY = "{} zgłosił(a) następujące uwagi do tematu „{}”:\n\n{}"


def notify_thesis_accepted(thesis: 'Thesis'):
    """Let the advisor(s) know that their thesis has been accepted"""
    recipients = []
    if thesis.advisor:
        recipients.append(thesis.advisor.user.email)
    if thesis.supporting_advisor:
        recipients.append(thesis.supporting_advisor.user.email)
    if recipients:
        formatted_body = ACCEPTED_BODY.format(thesis.title)
        send_mail(ACCEPTED_SUBJECT, formatted_body, settings.MASS_MAIL_FROM, recipients)


def notify_thesis_rejected(thesis: 'Thesis'):
    """Let the advisor(s) know that their thesis has been rejected.
    Includes the reason specified by the master rejecter, and CC's them for the record
    """
    recipients = []
    if thesis.advisor:
        recipients.append(thesis.advisor.user.email)
    if thesis.supporting_advisor:
        recipients.append(thesis.supporting_advisor.user.email)
    formatted_body = REJECTED_BODY.format(thesis.title, thesis.rejection_reason)
    rejecter = get_master_rejecter()
    msg = EmailMessage(
        REJECTED_SUBJECT,
        formatted_body,
        settings.MASS_MAIL_FROM,
        recipients,
        cc=[rejecter.user.email] if rejecter else []
    )
    msg.send()


def notify_rejecting_vote_cast(thesis: 'Thesis', caster: Employee, reason: str):
    """Let the master rejecter know that a rejecting vote has been cast"""
    rejecter = get_master_rejecter()
    if not rejecter:
        return
    formatted_body = REJECTING_VOTE_CAST_BODY.format(caster.get_full_name(), thesis.title, reason)
    send_mail(REJECTING_VOTE_CAST_SUBJECT, formatted_body, settings.MASS_MAIL_FROM, [rejecter.user.email])
