# -*- coding: utf-8 -*-
from django.template import Context
from django.template.loader import get_template
from mailer import send_html_mail

from django.conf import settings


class Notification(object):

    def create(self, template, template_html, data, recipient_list,
               subject = 'Powiadomienie z Systemu Zapisów',
               from_email=settings.MASS_MAIL_FROM, sign=False):

        con = Context( data )
        tem = get_template(template)
        plaintext_body = tem.render(con)
        tem = get_template(template_html)
        html_body = tem.render(con)

        send_html_mail(subject, plaintext_body, html_body, from_email, recipient_list)
