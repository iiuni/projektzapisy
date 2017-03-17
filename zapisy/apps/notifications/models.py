# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import Context, render_to_string, select_template
from django.utils.html import strip_tags
from mailer.models import Message
from apps.users.models import Employee, Student

NOTIFICATION_TYPES = (
    ('News', {
        'all': [
            ('send-news', u'Dodano nowy news'),
            #('send-dev-news', u'Dodano nowy news developerski'),
        ],
        'student': [
            #('send-user_change', u'Nastąpiła automatyczna zmiana Twoich danych w systemie')
        ],
        'employee': []
    }),
    ('Przedmioty', {
        'all': [
            #('course-new_semester', u'Pojawiły się przedmioty na przyszły semestr'),
            #('courses-new_schedule', u'Pojawił się plan na następny semestr'),
            #('course-message', u'Wykładowca napisał nową wiadomość do zapisanych'),
        ],
        'student': [
            #('change-group-time', u'Zmieniono termin grupy, do której jesteś zapisany/a'),
            #('change-group-time-q', u'Zmieniono termin grupy, do której jesteś w kolejce'),
            #('change-course', u'Zmieniono opis przedmiotu na który jesteś zapisany/a'),
            #('change-course-q', u'Zmieniono opis przedmiotu, do którego stoisz w kolejce'),
            #('change-course-p', u'Zmieniono opis przedmiotu przypiętego przez Ciebie do planu'),
            #('group-message', u'Prowadzący napisał nową wiadomość do grupy'),
        ],
        'employee': [
            #('change-course-teacher', u'Zmieniono opis przedmiotu z którego prowadzisz zajęcia'),
        ]
    }),
    ('Zapisy', {
        'all': [
        ],
        'student': [
            #('enrollment-t0', u'Ustalono Twój czas otwarcia zapisów'),
            #('enrolled', u'Nastąpiło zapisanie do grupy'),
            #('enrolled-again', u'Nastąpiło przepisanie do grupy'),
            #('enrolled-remove', u'Nastąpiło wypisanie z grupy'),
            #('queue-remove', u'Nastąpiło wypisanie z kolejki'),
            #('enrollment-finish', u'Pozostały 24 godziny do końca zapisów'),
            #('enrollment-finish-dir', u'Pozostały 24 godziny do końca wypisów dyrektorskich'),
            #('enrollment-started', u'Twoje zapisy się rozpoczęły'),
            ('enrollment-limit', u'Podniesiono limit ECTS'),
        ],
        'employee': [
            #('student-enrolled', u'Po pierwszym tygodniu do grupy dołączył nowy student'),
            #('student-removed', u'Po pierwszym tygodniu z grupy wypisał się student')
        ]
    }),
    ('Oferta', {
        'all': [
            #('desiderata', u'Przypomnienie o wypełnieniu dezyderaty'),
            #('preferences', u'Przypomnienie o aktualizacji preferencji'),
            #('offer', u'Przypomnienie o aktualizacji oferty')
        ],
        'student': [
            ('vote-start', u'Rozpoczęło się głosowanie'),
            #('vote-finish', u'Zostało 24 godziny do końca głosowania'),
            #('vote-correction', u'Rozpoczęła się korekta głosowania'),
            #('vote-correction-finish', u'Zostało 24 godziny do końca korekty'),
            #('vote-summary', u'Wyślij podsumowanie oddanego głosu'),
            ('grade-start', u'Rozpoczęła się ocena')
            #('grade-finish', u'Pozostało 24 godzin do końca oceny'),
            #('grade-info', u'Wyślij potwierdzenie wygenerowania kluczy')
        ],
        'employee': []
    }),
    ('Wydarzenia', {
        'all': [
            #('new-event', u'Dodano nowe wydarzenie w Instytucie'),
            #('new-cancell', u'Interesujące Cię wydarzenie zostało odwołane'),
            #('new-finish', u'Interesujące Cię wydarzenie odbędzie się jutro'),
            #('message-in-event', u'Organizator wydarzenia napisał nową wiadomość'),
            #('new-zosia', u'Wyślij informacje o rozpoczęciu zapisów na nową ZOSIę')
        ],
        'student': [
            #('exam-info', u'Ustalono termin egzaminu lub kolokwium z przedmiotu na który jesteś zapisany/a'),
        ],
        'employee': [
            #('exam-info-e', u'Ustalono termin egzaminu lub kolokwium z przedmiotu do którego prowadzisz zajęcia'),
        ]
    }),
    ('Wnioski', {
        'all': [
            #('petition-accepted', u'Twój wniosek został zaakceptowany'),
            #('petition-deny', u'Twój wniosek został odrzucony')
        ],
        'student': [],
        'employee': []
    })
)

_categorycache = {}


def get_category(type_name):
    if not _categorycache:
        for t in NOTIFICATION_TYPES:
            for item in t[1]['all']:
                _categorycache[item[0]] = t[0]

            for item in t[1]['student']:
                _categorycache[item[0]] = t[0]

            for item in t[1]['employee']:
                _categorycache[item[0]] = t[0]

    return _categorycache[type_name]


def types_list(student=False, employee=False):
    types = []

    for elem in NOTIFICATION_TYPES:
        types.extend(elem[1]['all'])

        if student:
            types.extend(elem[1]['student'])

        if employee:
            types.extend(elem[1]['employee'])

    return types


class NotificationManager(models.Manager):

    def create_and_get(self, user):
        types = types_list(not user.student is None, not user.employee is None)
        used = self.filter(user=user).distinct().values_list('type', flat=True)
        new_objects = []

        for t in types:
            if not t[0] in used:
                new_objects.append(NotificationPreferences(user=user, type=t[0]))

        self.bulk_create(new_objects)

        return self.filter(user=user)

    @classmethod
    def user_has_notification_on(cls, user, notification):
        try:
            preference = NotificationPreferences.objects.get(user=user, type=notification)
            return preference.value
        except NotificationPreferences.DoesNotExist:
            return False


class NotificationPreferences(models.Model):
    user = models.ForeignKey(User, verbose_name=u'użytkownik')
    type = models.CharField(choices=types_list(True, True), max_length=50, verbose_name=u'typ')
    value = models.BooleanField(default=True, verbose_name=u'wartość')

    objects = NotificationManager()

    class Meta:
        unique_together = ('user', 'type')

        ordering = ['id']
        verbose_name = u'Ustawienie Notyfikacji'
        verbose_name_plural = u'Ustawienia Notyfikacji'


class Notification(object):

    @classmethod
    def send_notification(cls, user, notification, context):
        preference = NotificationManager.user_has_notification_on(user, notification)
        if user.email and preference:
            template_plaintext, template_html = _find_notification_templates(notification)
            context['user'] = user
            body_html = template_html.render(context)
            body_plaintext = template_plaintext.render(context)
            Message.objects.create(to_address=user.email, subject=preference.get_type_display(), message_body=body_plaintext, message_body_html=body_html)

    @classmethod
    def send_notifications(cls, notification, context={}):
        """
        Sends given notification to all subscribed users.
        """

        def _find_notification_name(notification):
            types = types_list(True, True)
            for type in types:
                if type[0] == notification:
                    return type[1]
            return ''

        def _find_notification_templates(notification):
            template_html = 'notifications/%s.html' % notification
            return (select_template(['notifications/plaintext/%s.html' % notification, template_html]), select_template([template_html]))

        def _send_to_users(users, notification, subject, context):
            template_plaintext, template_html = _find_notification_templates(notification)
            for u in users:
                preference = NotificationManager.user_has_notification_on(u.user, notification)
                address = u.user.email
                if address and preference:
                    context['user'] = u.user
                    body_html = template_html.render(context)
                    body_plaintext = template_plaintext.render(context)
                    Message.objects.create(to_address=address, subject=subject, message_body=body_plaintext, message_body_html=body_html)

        subject = context['subject'] if 'subject' in context else _find_notification_name(notification)
        context = Context(context)
        _send_to_users(Employee.get_actives(), notification, subject, context)
        _send_to_users(Student.get_active_students(), notification, subject, context)

