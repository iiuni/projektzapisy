"""
Various utils.
"""

from mailer import send_html_mail
from django.template import Context
from django.template.loader import get_template


MASS_MAIL_FROM = 'zapisy@cs.uni.wroc.pl'

def render_and_send_email(subject, template, template_html, data, recipient_list, from_email=MASS_MAIL_FROM):


    con = Context( data )
    tem = get_template(template)
    plaintext_body = tem.render(con)
    tem = get_template(template_html)
    html_body = tem.render(con)

    send_html_mail(subject, plaintext_body, html_body, from_email, recipient_list)
