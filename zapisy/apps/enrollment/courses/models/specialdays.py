from django.core.validators import ValidationError
from django.db import models

from apps.common import days_of_week


class Freeday(models.Model):
    day = models.DateField(verbose_name='dzień wolny', unique=True)

    @classmethod
    def is_free(cls, date):
        """Returns true if date is an extra holiday.

        :param date: datetime.date
        """
        free = cls.objects.filter(day=date)
        if free:
            return True
        else:
            return False

    def __str__(self):
        return str(self.day)

    class Meta:
        verbose_name = 'dzień wolny od zajęć'
        verbose_name_plural = 'dni wolne od zajęć'
        app_label = 'courses'


class ChangedDay(models.Model):
    day = models.DateField(verbose_name='dzień wolny', unique=True)
    weekday = models.CharField(
        choices=days_of_week.DAYS_OF_WEEK,
        max_length=1,
        verbose_name='zmieniony na')

    def clean(self):
        if ChangedDay.get_official_day_of_week(self.day) == self.weekday:
            raise ValidationError(message={
                'weekday': ['To już jest ' + days_of_week.DAYS_OF_WEEK[self.day.weekday()][1]]
            },
                                  code='invalid')

    @classmethod
    def get_official_day_of_week(cls, date):
        """Returns actual schedule day, with respect to ChangedDays.

        :param date:
        """
        changes = ChangedDay.objects.filter(day=date)
        if changes:
            return changes[0].day
        else:
            return days_of_week.get_day_of_week(date)

    @staticmethod
    def get_added_days_of_week(start_date, end_date, day_of_week=None):
        added_days = ChangedDay.objects.filter(day__gte=start_date, day__lte=end_date)
        if day_of_week is None:
            return added_days
        else:
            return added_days.filter(weekday=day_of_week)

    def __str__(self):
        return "{0} -> {1}".format(str(self.day), str(self.get_weekday_display()))

    class Meta:
        verbose_name = 'dzień zmienony na inny'
        verbose_name_plural = 'dni zmienione na inne'
        app_label = 'courses'
