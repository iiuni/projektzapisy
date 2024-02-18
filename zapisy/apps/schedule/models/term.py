import collections
import datetime
from typing import Set, Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.dispatch import receiver

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.term import Term as CourseTerm

from .event import Event


class Term(models.Model):
    event = models.ForeignKey(Event, verbose_name='Wydarzenie', on_delete=models.CASCADE)

    day = models.DateField(verbose_name='Dzień')

    start = models.TimeField(verbose_name='Początek')
    end = models.TimeField(verbose_name='Koniec')

    room = models.ForeignKey(
        to=Classroom,
        null=True,
        blank=True,
        verbose_name='Sala',
        on_delete=models.CASCADE,
        related_name='event_terms')
    place = models.CharField(max_length=255, null=True, blank=True, verbose_name='Miejsce')
    ignore_conflicts = models.BooleanField(default=False)

    def validate_against_event_terms(self):
        assert self.room is not None
        terms = Term.get_terms_for_dates(dates=[self.day],
                                         classroom=self.room,
                                         start_time=self.start,
                                         end_time=self.end)

        if self.pk:
            terms = terms.exclude(pk=self.pk)

        if terms:
            raise ValidationError(
                message={'__all__': ['W tym samym czasie ta sala jest zarezerwowana: ' +
                                     str(terms[0].event) + ' (wydarzenie)']},
                code='overlap')

    def validate_against_course_terms(self):
        assert self.room is not None
        semester = Semester.get_semester(self.day)
        if not semester:
            return
        if semester.lectures_beginning <= self.day and self.day <= semester.lectures_ending:

            course_terms = CourseTerm.get_terms_for_semester(semester=semester,
                                                             day=self.day,
                                                             classrooms=[self.room],
                                                             start_time=self.start,
                                                             end_time=self.end)
            if course_terms:
                raise ValidationError(
                    message={
                        '__all__': [
                            'W tym samym czasie w tej sali odbywają się zajęcia: ' +
                            course_terms[0].group.course.name +
                            ' ' +
                            str(
                                course_terms[0])]},
                    code='overlap')

    def clean(self):
        """Overloaded method from models.Model."""
        if self.start and self.end and self.start >= self.end:
            raise ValidationError(
                message={'end': ['Koniec musi następować po początku']},
                code='overlap')

        if not self.room and not self.place:
            raise ValidationError(
                message={'room': ['Musisz wybrać salę lub miejsce zewnętrzne'],
                         'place': ['Musisz wybrać salę lub miejsce zewnętrzne']},
                code='invalid'
            )

        if self.room:
            if not self.room.can_reserve:
                raise ValidationError(
                    message={'room': ['Ta sala nie jest przeznaczona do rezerwacji']},
                    code='invalid'
                )

            if self.day and self.start and self.end and not self.ignore_conflicts:
                self.validate_against_event_terms()
                self.validate_against_course_terms()

        super(Term, self).clean()

    class Meta:
        app_label = 'schedule'
        get_latest_by = 'end'
        ordering = ['day', 'start', 'end']
        verbose_name = 'termin'
        verbose_name_plural = 'terminy'

    def get_conflicted(self):
        if not self.room:
            return Term.objects.none()

        # X < B AND A < Y

        terms = Term.objects.filter(Q(room=self.room),
                                    Q(day=self.day),
                                    Q(event__status=Event.STATUS_ACCEPTED),
                                    Q(start__lt=self.end),
                                    Q(end__gt=self.start)) .select_related('event')

        if self.pk:
            terms = terms.exclude(pk=self.pk)
        return terms

    def pretty_print(self):
        """Verbose html info about term.

        Format: {start} - {end} {title_with_url} (author)
        """
        return '%s - %s <a href="%s">%s</a> (%s)' % (
            self.start, self.end, self.event.get_absolute_url(),
            self.event.title, self.event.author)

    def get_room(self):
        return self.room

    def get_day(self):
        return self.day

    @classmethod
    def get_exams(cls):
        """Get list of events with type 'exam'.

        @return: Term QuerySet
        """
        return cls.objects.filter(event__type__in=['0', '1']).order_by(
            'day', 'event__course__name', 'room').select_related('event', 'room', 'event__course',
                                                                 'event__course__semester')

    @classmethod
    def get_terms_for_dates(cls, dates, classroom, start_time=None, end_time=None):
        """Gets terms in specified classroom on specified days.

        :param end_time: datetime.time
        :param start_time: datetime.time
        :param classroom: enrollment.courses.models.Classroom
        :param dates: datetime.date list
        """
        if start_time is None:
            start_time = datetime.time(8)
        if end_time is None:
            end_time = datetime.time(21)

        terms = cls.objects.filter(day__in=dates,
                                   start__lt=end_time,
                                   end__gt=start_time,
                                   room=classroom,
                                   event__status=Event.STATUS_ACCEPTED).select_related('event')

        return terms

    @classmethod
    def prepare_conflict_dict(cls, start_time, end_time):
        """Returns a report of conflicting events.

        Head is top term for which next terms (if conflicted in terms of time)
        will be considered as conflicts. current_result stores conflicts for
        given current head

        @return OrderedDict[day][room][head|conflicted]
        """
        candidates = Term.objects.filter(
            day__gte=start_time,
            day__lte=end_time).order_by(
            'day',
            'room',
            'start',
            'end').select_related(
            'room',
            'event')
        conflicts = collections.OrderedDict()
        current_result = dict()
        head = None
        for term in candidates:
            if (head is not None and (term.day != head.day or term.room != head.room)) or head is None:
                if current_result and current_result['conflicted']:
                    if head.day not in conflicts:
                        conflicts[head.day] = dict()
                    if head.room not in conflicts[head.day]:
                        conflicts[head.day][head.room] = dict()
                        conflicts[head.day][head.room][head.pk] = dict()
                    conflicts[head.day][head.room][head.pk] = current_result
                head = term
                current_result = {}
                current_result['head'] = head
                current_result['conflicted'] = list()
            elif head.end >= term.end and term.start >= head.start:  # conflict
                current_result['conflicted'].append(term)
        return conflicts

    def __str__(self):
        return '{0:s}: {1:s} - {2:s}'.format(self.day, self.start, self.end)


def get_terms(course_term: CourseTerm):
    """Retrieves Terms corresponding to a CourseTerm."""
    dates = course_term.group.course.semester.get_all_days_of_week(course_term.dayOfWeek)
    matching_terms = Term.objects.filter(event__group=course_term.group,
                                         day__in=dates,
                                         start=course_term.start_time,
                                         end=course_term.end_time)
    return matching_terms


def delete_terms(course_term: CourseTerm, room_pk_set: Optional[Set[int]] = None):
    """Deletes Terms corresponding to a CourseTerm and (optionally) a set of rooms."""
    matching_terms = get_terms(course_term)
    if room_pk_set:
        matching_terms = matching_terms.filter(room__pk__in=room_pk_set)
    matching_terms.delete()


def create_terms(course_term: CourseTerm, room_pk_set: Optional[Set[int]] = None):
    """Creates Terms corresponding to a CourseTerm and (optionally) a set of rooms."""
    dates = course_term.group.course.semester.get_all_days_of_week(course_term.dayOfWeek)
    event, _ = Event.objects.get_or_create(group=course_term.group,
                                           course=course_term.group.course,
                                           title=course_term.group.course.get_short_name(),
                                           type=Event.TYPE_CLASS,
                                           visible=True,
                                           status=Event.STATUS_ACCEPTED,
                                           author=course_term.group.teacher.user)

    rooms = []
    if course_term.pk and room_pk_set:
        rooms = Classroom.objects.filter(pk__in=room_pk_set)
    elif course_term.pk and not room_pk_set:
        rooms = course_term.classrooms.all()
    if not rooms:
        rooms = [None]

    for day in dates:
        for room in rooms:
            Term.objects.create(event=event,
                                day=day,
                                start=course_term.start_time,
                                end=course_term.end_time,
                                room=room)


@receiver(models.signals.pre_delete, sender=CourseTerm)
def sync_course_term_delete(**kwargs):
    """Deletes all Terms associated with a CourseTerm when it is deleted."""
    # the current version of the CourseTerm, possibly with unsaved changes
    instance_curr: CourseTerm = kwargs['instance']
    if instance_curr.pk:
        # the version of the CourseTerm stored in the database
        instance_db: CourseTerm = CourseTerm.objects.get(pk=instance_curr.pk)
        delete_terms(instance_db)


@receiver(models.signals.pre_save, sender=CourseTerm)
def sync_course_term_save(**kwargs):
    """Creates or updates Terms associated with a CourseTerm when it is saved.

    If the CourseTerm is not present in the database yet, new Terms
    corresponding to it will be created.
    If the CourseTerm is already in the database and its start time or end time
    are being changed, Terms corresponding to it will be updated accordingly.
    However, if the day of the week is also being changed, the Terms will
    instead be deleted and new ones (with updated fields) will be created.
    New terms are created using the attributes of instance_curr, because
    these attributes are about to be saved to the database (this is a pre_save
    signal receiver).
    Recreating Terms is the most suitable solution in this last case, because
    updating them would be too complex and error-prone.
    """
    # the current version of the CourseTerm, possibly with unsaved changes
    # that are about to be saved
    instance_curr: CourseTerm = kwargs['instance']

    if not instance_curr.pk:
        create_terms(instance_curr)
        return

    # the version of the CourseTerm stored in the database
    instance_db: CourseTerm = CourseTerm.objects.get(pk=instance_curr.pk)

    changed_fields = []
    for field in ['dayOfWeek', 'start_time', 'end_time']:
        if getattr(instance_db, field) != getattr(instance_curr, field):
            changed_fields.append(field)

    if len(changed_fields) == 0:
        return
    elif 'dayOfWeek' in changed_fields:
        delete_terms(instance_db)
        create_terms(instance_curr)
    else:
        for term in get_terms(instance_db):
            term.start = instance_curr.start_time
            term.end = instance_curr.end_time
            term.save()


@receiver(models.signals.m2m_changed, sender=CourseTerm.classrooms.through)
def sync_course_term_m2m(**kwargs):
    """Creates or deletes Terms associated with a CourseTerm when its set of classrooms changes.

    If a classroom has been removed from the set, Terms taking place in it
    will be deleted. If there are no Terms left after the deletion,
    Terms with the room set to None will be created.
    If the set of classrooms has been cleared, all Terms associated with the
    CourseTerm will be deleted and Terms with the room set to None will be created.
    If a classroom has been added to the set, new Terms taking place in it
    will be created. Any existing Terms with the room set to None will be deleted.
    As opposed to sync_course_term_save, the Terms are not created using the
    attributes of instance_curr. This is because some of these attributes
    (day, start time and end time) might not have been saved to the database
    and may not ultimately be saved (this is not a pre_save signal receiver).
    However, the set of classrooms is up to date for both instance_curr and
    instance_db (this is a m2m_changed signal receiver for post_* actions only).
    Thus create_terms(instance_db) has access to an updated set of classrooms.
    When the attributes of instance_curr are saved, the sync_course_term_save
    signal receiver will update the Terms created by this function accordingly.
    """
    action = kwargs['action']
    if not action.startswith('post_'):
        return

    pk_set = kwargs['pk_set']
    # the current version of the CourseTerm, possibly with unsaved changes
    instance_curr: CourseTerm = kwargs['instance']
    # the version of the CourseTerm stored in the database
    instance_db: CourseTerm = CourseTerm.objects.get(pk=instance_curr.pk)

    if action == 'post_remove' and pk_set:
        delete_terms(instance_db, pk_set)
        # if there are no Terms left after the deletion,
        # create Terms with the room set to None
        if not get_terms(instance_db):
            create_terms(instance_db)
    elif action == 'post_clear':
        delete_terms(instance_db)
        # create Terms with the room set to None
        create_terms(instance_db)
    elif action == 'post_add' and pk_set:
        # if there are any Terms with the room set to None, delete them
        if get_terms(instance_db).filter(room=None):
            delete_terms(instance_db)
        create_terms(instance_db, pk_set)
