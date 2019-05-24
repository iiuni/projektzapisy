from datetime import time, date

from django.db import models
from django.db.models import signals
from django.core.cache import cache as mcache
from zapisy import common
import logging

backup_logger = logging.getLogger('project.backup')

HOURS = [(str(hour), "%s.00" % hour) for hour in range(8, 23)]


class Term(models.Model):
    """terms of groups"""

    dayOfWeek = models.CharField(
        max_length=1,
        choices=common.DAYS_OF_WEEK,
        verbose_name='dzień tygodnia')
    start_time = models.TimeField(verbose_name='rozpoczęcie')
    end_time = models.TimeField(verbose_name='zakończenie')
    classroom = models.ForeignKey(
        'Classroom',
        verbose_name='sala',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    group = models.ForeignKey(
        'Group',
        verbose_name='grupa',
        related_name='term',
        on_delete=models.CASCADE)
    classrooms = models.ManyToManyField(
        'Classroom',
        related_name='new_classrooms',
        verbose_name='sale',
        blank=True)

    usos_id = models.PositiveIntegerField(
        null=True, blank=True, unique=True, verbose_name='Kod terminu w systemie USOS')

    class Meta:
        # TO DO /pkacprzak/ add advanced constraint - example: start_time <
        # end_time, any pair of terms can't overlap
        verbose_name = 'termin'
        verbose_name_plural = 'terminy'
        ordering = ['dayOfWeek']
        app_label = 'courses'

    def day_in_zero_base(self):
        return int(self.dayOfWeek) - 1

    def length_in_minutes(self):
        return (self.end_time.hour - self.start_time.hour) * 60 + \
            (self.end_time.minute - self.start_time.minute)

    def time_from_in_minutes(self):
        "Returns number of minutes from start of day (midnight) to term beggining"""
        return (self.start_time.hour) * 60 + (self.start_time.minute)

    def time_from(self):
        "Returns hourFrom in time format"""
        return self.start_time

    def time_to(self):
        "Returns hourTo in time format"""
        return self.end_time

    def _convert_string_to_time(self, str):
        hour, minute = [int(x) for x in str.split('.')]
        return time(hour=hour, minute=minute)

    def period_string(self):
        return "%s – %s" % (self.start_time.strftime("%H"), self.end_time.strftime("%H"))

    def get_dayOfWeek_display_short(self):
        return {
            '1': 'pn',
            '2': 'wt',
            '3': 'śr',
            '4': 'cz',
            '5': 'pt',
            '6': 'so',
            '7': 'nd',
        }[self.dayOfWeek]

    @staticmethod
    def get_day_of_week(date):
        return common.DAYS_OF_WEEK[date.weekday()][0]

    @staticmethod
    def get_python_day_of_week(day_of_week):
        return [x[0] for x in common.DAYS_OF_WEEK].index(day_of_week)

    def numbers(self):
        if not self.id:
            return ''

        if hasattr(self, 'classrooms_as_string'):
            return self.classrooms_as_string
        classrooms = self.classrooms.all()
        if len(classrooms) > 0:
            classrooms = ', '.join((x.number for x in classrooms))
        else:
            classrooms = ''

        return classrooms

    @classmethod
    def get_terms_for_semester(
            cls,
            semester,
            day=None,
            classrooms=None,
            start_time=None,
            end_time=None):
        """
        A versatile function returning Terms. day is either datetime.date or string

        :param semester: enrollment.courses.model.Semester
        :param day: common.DAYS_OF_WEEK or datetime.date
        """
        from .semester import ChangedDay, Freeday
        query = cls.objects.filter(group__course__semester=semester)

        if day is None:
            pass
        else:
            if isinstance(day, date):
                if Freeday.is_free(day):
                    return cls.objects.none()
                day_of_week = ChangedDay.get_day_of_week(day)
            else:
                day_of_week = day
            query = query.filter(dayOfWeek=day_of_week)

        if classrooms:
            query = query.filter(classrooms__in=classrooms)

        if start_time and end_time:
            query = query.filter(start_time__lt=end_time, end_time__gt=start_time)

        return query.select_related('group__course')

    def serialize_for_json(self):
        return {
            'id': self.pk,
            'group': self.group.pk,
            'classroom': self.classrooms_as_string,
            'day': int(self.dayOfWeek),
            'start_time': ("%d:%d" % (self.start_time.hour, self.start_time.minute)),
            'end_time': ("%d:%d" % (self.end_time.hour, self.end_time.minute)),
        }

    def __str__(self):
        """Represents the term as a string.

        Normally calling this function makes a separate query to the Term's
        classrooms. To avoid it use `prefetch_related` when getting the Term
        object.
        """
        classrooms = self.numbers()
        return "%s %s-%s (s. %s)" % (
            self.get_dayOfWeek_display_short(), self.start_time.strftime("%H:%M"),
            self.end_time.strftime("%H:%M"), classrooms
        )


def recache(sender, **kwargs):
    mcache.clear()


signals.post_save.connect(recache, sender=Term)
signals.post_delete.connect(recache, sender=Term)
