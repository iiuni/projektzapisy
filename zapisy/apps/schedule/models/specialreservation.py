from django.db import models
from django.core.validators import ValidationError
from datetime import date, datetime

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.semester import Semester
from apps.schedule.models.event import Event

from zapisy import common

from apps.enrollment.courses.models.term import Term as CourseTerm


class SpecialReservationQuerySet(models.query.QuerySet):
    def on_day_of_week(self, day_of_week):
        return self.filter(dayOfWeek=day_of_week)

    def this_semester(self):
        return self.filter(semester=Semester.get_current_semester())

    def any_semester(self, semester):
        return self.filter(semester=semester)

    def in_classroom(self, classroom):
        return self.filter(classroom=classroom)

    def in_classrooms(self, classrooms):
        return self.filter(classroom__in=classrooms)

    def between_hours(self, start_time, end_time):
        return self.filter(start_time__lt=end_time, end_time__gt=start_time)


class SpecialReservationManager(models.Manager):
    def get_queryset(self):
        return SpecialReservationQuerySet(self.model, using=self._db)

    def on_day_of_week(self, day_of_week):
        return self.get_queryset().on_day_of_week(day_of_week)

    def this_semester(self):
        return self.get_queryset().this_semester()

    def any_semester(self, semester):
        return self.get_queryset().any_semester(semester)

    def in_classroom(self, classroom):
        return self.get_queryset().in_classroom(classroom)

    def in_classrooms(self, classrooms):
        return self.get_queryset().in_classrooms(classrooms)

    def between_hours(self, start_time, end_time):
        return self.get_queryset().between_hours(start_time, end_time)


class SpecialReservation(models.Model):

    semester = models.ForeignKey(Semester, verbose_name='semestr', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='nazwa', max_length=255)
    classroom = models.ForeignKey(Classroom, verbose_name='sala', on_delete=models.CASCADE)
    dayOfWeek = models.CharField(max_length=1,
                                 choices=common.DAYS_OF_WEEK,
                                 verbose_name='dzień tygodnia')
    start_time = models.TimeField(verbose_name='rozpoczęcie', blank=False)
    end_time = models.TimeField(verbose_name='zakończenie', blank=False)
    ignore_conflicts = False

    objects = SpecialReservationManager()

    @classmethod
    def get_reservations_for_semester(
            cls,
            semester,
            day=None,
            classrooms=None,
            start_time=None,
            end_time=None):
        """
        A versatile function returning SpecialReservations. day is either datetime.date or string

        :param semester: enrollment.courses.model.Semester
        :param day: common.DAYS_OF_WEEK or datetime.date
        """

        query = cls.objects.any_semester(semester)

        if day is not None:
            if isinstance(day, date):
                day_of_week = CourseTerm.get_day_of_week(day)
            else:
                day_of_week = day
            query = query.on_day_of_week(day_of_week)

        if classrooms:
            query = query.in_classrooms(classrooms)

        if start_time and end_time:
            query = query.between_hours(start_time, end_time)

        return query

    def validate_against_all_terms(self):

        course_terms = CourseTerm.get_terms_for_semester(semester=self.semester,
                                                         day=self.dayOfWeek,
                                                         classrooms=[self.classroom],
                                                         start_time=self.start_time,
                                                         end_time=self.end_time)

        from .term import Term
        candidate_days = self.semester.get_all_days_of_week(
            self.dayOfWeek, start_date=max(
                datetime.now().date(), self.semester.lectures_beginning))

        terms = Term.get_terms_for_dates(dates=candidate_days,
                                         classroom=self.classroom,
                                         start_time=self.start_time,
                                         end_time=self.end_time)
        msg_list = []

        if course_terms:
            for t in course_terms:
                msg_list.append(
                    'W tym samym czasie w tej sali odbywają się zajęcia: ' +
                    t.group.course.name +
                    ' ' +
                    str(t))

        if terms:
            for t in terms:
                if t.event.reservation != self and t.event.type != Event.TYPE_CLASS:
                    msg_list.append(
                        'W tym samym czasie ta sala jest zarezerwowana (wydarzenie): ' + str(t.event) + ' ' + str(t))

        if len(msg_list) > 0:
            raise ValidationError(message={'__all__': msg_list}, code='overlap')

    def clean(self):
        """
        Overloaded clean method. Checks for any conflicts between this SpecialReservation
        and other SpecialReservations, Terms of Events and Terms of Course Groups

        """
        if self.end_time <= self.start_time:
            raise ValidationError(
                message={'end_time': ['Koniec rezerwacji musi natępować po początku']},
                code='invalid'
            )

        if not self.classroom.can_reserve:
            raise ValidationError(
                message={'classroom': ['Ta sala nie jest przeznaczona do rezerwacji']},
                code='invalid'
            )

        if not self.ignore_conflicts:
            self.validate_against_all_terms()

        super(SpecialReservation, self).clean()

    class Meta:
        app_label = 'schedule'
        verbose_name = 'rezerwacja stała'
        verbose_name_plural = 'rezerwacje stałe'

    def create_event(self, author_id):
        from .term import Term
        from .event import Event

        Event.objects.filter(reservation=self).delete()

        semester = self.semester

        ev = Event()
        ev.title = self.title
        ev.description = 'Rezerwacja cykliczna - ' + self.title
        ev.reservation = self
        ev.type = Event.TYPE_GENERIC
        ev.visible = True
        ev.status = Event.STATUS_ACCEPTED
        ev.author_id = author_id
        ev.save()

        term_days = semester.get_all_days_of_week(
            day_of_week=self.dayOfWeek, start_date=max(
                datetime.now().date(), semester.lectures_beginning))

        for day in term_days:
            term = Term()
            term.event = ev
            term.day = day
            term.start = self.start_time
            term.end = self.end_time
            term.room = self.classroom
            term.save()

    def save(self, author_id, *args, **kwargs):
        super(SpecialReservation, self).save(*args, **kwargs)
        self.create_event(author_id)

    def __str__(self):
        return '%s: %s - %s %s - %s' % (self.semester, self.title, self.get_dayOfWeek_display(),
                                        self.start_time, self.end_time)
