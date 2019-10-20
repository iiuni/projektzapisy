"""
Various utils.
"""

from django.conf import settings
from mailer import send_html_mail
from django.template import Context
from django.template.loader import get_template
import codecs

MASS_MAIL_FROM = 'zapisy@cs.uni.wroc.pl'


def render_email_enrollment_from_queue(student, group):
    """
    Renders email to a student that has benn enrolled from queue.
    """
    con = Context({
        'group': group,
        'term': str(group.term),
        'student': student,
    })
    tem = get_template('enrollment/email_queue_plaintext.html')
    plaintext_body = tem.render(con)
    tem = get_template('enrollment/email_queue_html.html')
    html_body = tem.render(con)
    from_email = MASS_MAIL_FROM
    course = settings.EMAIL_COURSE_PREFIX + 'Przepisanie z kolejki do grupy'
    return (course, plaintext_body, html_body)


def send_mail(msg_parts, user):
    """
    Queue mail to the user.
    """
    (course, text_body, html_body) = msg_parts
    email = user.user.email
    if email:
        send_html_mail(course, text_body, html_body,
                       MASS_MAIL_FROM, [email])


def mailto(author, students, bcc=False):
    """Helper method to create mailto links"""
    result = author.email

    if students:
        return result + ('?bcc=' if bcc else ',') + \
            ','.join([student.user.email.replace('+', '%2B') for student in students])
    return result
