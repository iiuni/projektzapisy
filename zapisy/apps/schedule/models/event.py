from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import ValidationError
from django.db import models
from django.http import Http404

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.group import Group
from apps.enrollment.records.models import Record, RecordStatus
from apps.users.models import BaseUser


class Event(models.Model):
    """
    Model of Event
    """
    TYPE_EXAM = '0'
    TYPE_TEST = '1'
    TYPE_GENERIC = '2'
    TYPE_CLASS = '3'
    TYPE_OTHER = '4'

    STATUS_PENDING = '0'
    STATUS_ACCEPTED = '1'
    STATUS_REJECTED = '2'

    STATUSES = [(STATUS_PENDING, 'Do rozpatrzenia'),
                (STATUS_ACCEPTED, 'Zaakceptowane'),
                (STATUS_REJECTED, 'Odrzucone')]

    TYPES = [(TYPE_EXAM, 'Egzamin'),
             (TYPE_TEST, 'Kolokwium'),
             (TYPE_GENERIC, 'Wydarzenie'),
             (TYPE_CLASS, 'Zajęcia'),
             (TYPE_OTHER, 'Inne')]

    TYPES_FOR_STUDENT = [(TYPE_GENERIC, 'Wydarzenie')]

    TYPES_FOR_TEACHER = [(TYPE_EXAM, 'Egzamin'),
                         (TYPE_TEST, 'Kolokwium'),
                         (TYPE_GENERIC, 'Wydarzenie')]

    title = models.CharField(max_length=255, verbose_name='Tytuł', null=True, blank=True)
    description = models.TextField(verbose_name='Opis', blank=True)
    type = models.CharField(choices=TYPES, max_length=1, verbose_name='Typ')
    visible = models.BooleanField(verbose_name='Wydarzenie jest publiczne', default=False)

    status = models.CharField(choices=STATUSES, max_length=1, verbose_name='Stan', default='0')

    course = models.ForeignKey(CourseInstance, null=True, blank=True, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE)
    reservation = models.ForeignKey(
        'schedule.SpecialReservation',
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    interested = models.ManyToManyField(User, related_name='interested_events')

    author = models.ForeignKey(User, verbose_name='Twórca', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        from django.urls import reverse

        if self.group:
            return reverse('group-view', args=[str(self.group_id)])
        return reverse('events:show', args=[str(self.pk)])

    class Meta:
        app_label = 'schedule'
        verbose_name = 'wydarzenie'
        verbose_name_plural = 'wydarzenia'
        ordering = ('-created',)
        permissions = (
            ("manage_events", "Może zarządzać wydarzeniami"),
        )

    def clean(self, *args, **kwargs):
        """
        Overload clean method.
        If author is employee and try reserve room for exam - accept it
        If author has perms to manage events - accept it
        """

        # if this is a new item

        if not self.pk:

            # if author is an employee, accept any exam and test events
            if ((BaseUser.is_employee(self.author) and self.type in (Event.TYPE_EXAM, Event.TYPE_TEST)) or
                    self.author.has_perm('schedule.manage_events')):
                self.status = self.STATUS_ACCEPTED

            # all exams and tests should be public

            if self.type in [Event.TYPE_EXAM, Event.TYPE_TEST]:
                self.visible = True

            # students can only add generic events that have to be accepted first

            if BaseUser.is_student(self.author) and not self.author.has_perm(
                    'schedule.manage_events'):
                if self.type != Event.TYPE_GENERIC:
                    raise ValidationError(
                        message={'type': ['Nie masz uprawnień aby dodawać wydarzenia tego typu']},
                        code='permission')

                if self.status != Event.STATUS_PENDING:
                    raise ValidationError(
                        message={
                            'status': ['Nie masz uprawnień aby dodawać zaakceptowane wydarzenia']},
                        code='permission')

        else:
            old = Event.objects.get(pk=self.pk)

            # if status is changed
            if old.status != self.status:

                # if status changes to accepted, validate all term objects
                if self.status == Event.STATUS_ACCEPTED:
                    from .term import Term
                    for term in Term.objects.filter(event=self):
                        term.clean()

        super(Event, self).clean()

    def remove(self):
        """
            Removing all terms bounded with given event

        """
        from .term import Term
        terms = Term.objects.filter(event=self)
        for term in terms:
            term.delete()
        self.delete()

    def _user_can_see_or_404(self, user):
        """

        Private method. Return True if user can see event, otherwise False.

        @param user: auth.User
        @return: Boolean
        """
        if not self.author == user and not user.has_perm('schedule.manage_events'):
            if(not self.visible or
               self.type not in [self.TYPE_EXAM, self.TYPE_TEST, self.TYPE_GENERIC] or
               self.status != self.STATUS_ACCEPTED):
                return False

        return True

    @classmethod
    def get_event_or_404(cls, id, user):
        """

        If events exist and user can see it - return
        otherwise raise Http404

        @param id: Integer Number
        @param user:  auth.User
        @return: Event object
        """
        try:
            event = cls.objects.select_related('group', 'course', 'author') \
                .prefetch_related('term_set', 'term_set__room').get(pk=id)
        except ObjectDoesNotExist:
            raise Http404

        if event._user_can_see_or_404(user):
            return event
        else:
            raise Http404

    @classmethod
    def get_event_for_moderation_or_404(cls, id, user):
        """

        If events exist and user can send moderation message - return it
        otherwise raise Http404

        @param id: Integer Number
        @param user:  auth.User
        @return: Event object
        """
        try:
            event = cls.objects.select_related('group', 'course', 'author') \
                .prefetch_related('term_set', 'term_set__room').get(pk=id)
        except ObjectDoesNotExist:
            raise Http404

        if event.author == user or user.has_perm('schedule.manage_events'):
            return event
        else:
            raise Http404

    @classmethod
    def get_event_for_moderation_only_or_404(cls, id, user):
        """

        If events exist and user can send moderation message - return it
        otherwise raise Http404

        @param id: Integer Number
        @param user:  auth.User
        @return: Event object
        """
        try:
            event = cls.objects.select_related('group', 'course', 'author') \
                .prefetch_related('term_set', 'term_set__room').get(pk=id)
        except ObjectDoesNotExist:
            raise Http404

        if user.has_perm('schedule.manage_events'):
            return event
        else:
            raise Http404

    @classmethod
    def get_all(cls):
        """

        Return all events with all needed select_related and prefetch_related

        @return: Event QuerySet
        """
        return cls.objects.all().select_related('group', 'course', 'author') \
            .prefetch_related('term_set', 'term_set__room')

    @classmethod
    def get_all_without_courses(cls):
        """

        Return all events with all needed select_related and prefetch_related

        @return: Event QuerySet
        """
        return cls.get_all().exclude(type=Event.TYPE_CLASS)

    @classmethod
    def get_for_user(cls, user):
        """
        Get list of events, where user is author

        @param user: auth.User object
        @return: Event QuerySet
        """
        return cls.objects.filter(author=user).select_related('course', 'author')\
            .prefetch_related('term_set')

    @classmethod
    def get_exams(cls):
        """
        Return list of all exam

        @return Event QuerySet
        """
        return cls.objects.filter(type=Event.TYPE_EXAM, status=Event.STATUS_ACCEPTED)\
            .order_by('-created').select_related('course')

    def get_followers(self):
        if self.type in [Event.TYPE_EXAM, Event.TYPE_TEST]:
            emails = Record.objects.filter(group__course=self.course,
                                           status=RecordStatus.ENROLLED).values_list(
                                               'student__user__email', flat=True).distinct()
            return emails

        return self.interested.values_list('email', flat=True)

    def __str__(self):
        return '%s %s' % (self.title, self.description)
