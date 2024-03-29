from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.core.validators import ValidationError
from django.db import models

from apps.common import days_of_week

from .term import Term


class Semester(models.Model):
    """Semester in academic year."""
    TYPE_WINTER = 'z'
    TYPE_SUMMER = 'l'
    TYPE_CHOICES = [(TYPE_WINTER, 'zimowy'), (TYPE_SUMMER, 'letni')]

    visible = models.BooleanField(verbose_name='widoczny', default=False)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, verbose_name='rodzaj semestru')
    year = models.CharField(max_length=7, default='0', verbose_name='rok akademicki')
    records_opening = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Czas otwarcia zapisów',
        help_text='Godzina powinna być ustawiona na 00:00:00, by studenci mieli otwarcie między 10:00 a 22:00.')
    records_closing = models.DateTimeField(
        null=True, blank=True, verbose_name='Czas zamkniecia zapisów')
    records_ending = models.DateTimeField(
        null=True, blank=True, verbose_name='Czas zamknięcia wypisów')

    lectures_beginning = models.DateField(
        null=True, blank=True, verbose_name='Dzień rozpoczęcia zajęć')
    lectures_ending = models.DateField(
        null=True, blank=True, verbose_name='Dzień zakończenia zajęć')

    semester_beginning = models.DateField(null=False, verbose_name='Data rozpoczęcia semestru')
    semester_ending = models.DateField(null=False, verbose_name='Data zakończenia semestru')

    is_grade_active = models.BooleanField(verbose_name='Ocena aktywna', default=False)
    records_ects_limit_abolition = models.DateTimeField(
        null=True, verbose_name='Czas zniesienia limitu 35 ECTS')

    t0_are_ready = models.BooleanField(verbose_name='T0 zostały ustalone', default=False)

    first_grade_semester = models.ForeignKey(
        'self',
        verbose_name='Pierwszy semestr oceny',
        null=True,
        blank=True,
        related_name='fgrade',
        on_delete=models.CASCADE)
    second_grade_semester = models.ForeignKey(
        'self',
        verbose_name='Drugi semester oceny',
        null=True,
        blank=True,
        related_name='sgrade',
        on_delete=models.CASCADE)

    usos_kod = models.CharField(
        blank=True,
        null=True,
        unique=True,
        max_length=20,
        verbose_name='Kod semestru w systemie USOS')

    def clean(self):
        """Overloaded clean method.

        Checks for any conflicts between this SpecialReservation and other
        SpecialReservations, Terms of Events and Terms of Course Groups.
        """
        if self.records_ending and not (
                self.records_opening <= self.records_ending <= self.records_closing):
            raise ValidationError(
                message={
                    'records_ending': ['Koniec wypisów musi byćw przedziale <otwarcie zapisów, zamknięcie zapisów>']
                },
                code='invalid'
            )

    def can_remove_record(self, time: Optional[datetime] = None) -> bool:
        """Checks if the given timestamp is before semester's unenrolling deadline."""
        if time is None:
            time = datetime.now()
        return self.records_ending is None or time <= self.records_ending

    def is_closed(self, time: Optional[datetime] = None) -> bool:
        """Checks if the enrollment is finished in the semester."""
        if time is None:
            time = datetime.now()
        return self.records_closing is not None and self.records_closing <= time

    def get_current_limit(self, timestamp: Optional[datetime] = None) -> int:
        """Returns the enrollment ECTS limit at the timestamp."""
        if timestamp is None:
            timestamp = datetime.now()
        if self.records_ects_limit_abolition is not None:
            if timestamp < self.records_ects_limit_abolition:
                return settings.ECTS_INITIAL_LIMIT
        return settings.ECTS_FINAL_LIMIT

    def get_name(self):
        """Returns name of semester."""
        # TODO: wymuszanie formatu roku "XXXX/YY" zamiast "XXXX"
        if len(self.year) != 7:
            return '(BŁĄD) {0} {1}'.format(self.year, self.get_type_display())
        return '{0} {1}'.format(self.year, self.get_type_display())

    def get_short_name(self):
        if self.type == self.TYPE_WINTER:
            return 'zima {0}'.format(self.year)
        elif self.type == self.TYPE_SUMMER:
            return 'lato {0}'.format(self.year)
        return self.year

    def is_current_semester(self):
        if self.semester_beginning is None or self.semester_ending is None:
            return False
        return self.semester_beginning <= datetime.now().date() <= self.semester_ending

    def get_all_days_of_week(self, day_of_week, start_date=None):
        """Get all dates when the specifies day of week schedule is valid.

        :param day_of_week: DAYS_OF_WEEK
        :param start_date: datetime.date
        """
        date = self.lectures_beginning
        if start_date:
            date = start_date
        python_weekday = Term.get_python_day_of_week(day_of_week)

        # ensure first date in while loop is a candidate
        if date.weekday() < python_weekday:
            date += timedelta(days=python_weekday - date.weekday())
        elif date.weekday() == python_weekday:
            pass
        else:
            date += timedelta(days=7 - date.weekday() + python_weekday)

        assert Term.get_day_of_week(date) == day_of_week

        dates = []
        while date <= self.lectures_ending:
            # if its not a free day
            if not Freeday.is_free(date):
                # if it wasnt changed
                if ChangedDay.get_day_of_week(date) == day_of_week:
                    # add to list
                    dates.append(date)
            # move date to next week
            date += timedelta(days=7)

        dates.extend(self.get_all_added_days_of_week(day_of_week, start_date))

        return dates

    def get_all_added_days_of_week(self, day_of_week, start_date=None):
        """Finds all days with switched weekday.

        Args:
            day_of_week: Filters by day of week the date is switched to.
            start_date: If provided, the switched days starting with this date
                are returned. Otherwise the search is limited to the current
                semester.
        """
        from_date = self.lectures_beginning
        if start_date:
            from_date = start_date

        added_days = ChangedDay.get_added_days_of_week(from_date,
                                                       self.lectures_ending,
                                                       day_of_week)
        return [x.day for x in added_days]

    def get_all_weeks(self) -> List[Tuple[datetime, datetime]]:
        """Returns list of all weeks in semester.

        Each tuple contains first and last day of the week.
        """
        week_start = self.semester_beginning - timedelta(days=self.semester_beginning.weekday())
        weeks = []
        while week_start <= self.semester_ending:
            week_end = week_start + timedelta(days=6)
            weeks.append((week_start, week_end))
            week_start += timedelta(days=7)
        return weeks

    @staticmethod
    def get_semester(date) -> Optional['Semester']:
        """Get semester for a specified date. More versatile than get_current_semester.

        Args:
            date: Choose semester with date included

        Returns:
            Semester or None

        Raises:
            MultipleObjectsReturned: Wrong semesters' dates
        """
        try:
            return Semester.objects.get(semester_beginning__lte=date,
                                        semester_ending__gte=date)
        except Semester.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise

    @staticmethod
    def get_upcoming_semester(strict: bool = False) -> Optional['Semester']:
        """Returns either upcomming or current semester or None.

        Upcoming semester is the one, enrolment into which has already
        been scheduled but has not ended. It may be useful when students
        want to plan their timetables.
        If there is no semester for which enrolment has been scheduled and has not
        ended, the behaviour depends on the optional argument: if it is set to True,
        None is returned; otherwise current_semester is returned.

        Raises:
            MultipleObjectsReturned: Wrong semesters' dates
        """
        try:
            return Semester.objects.filter(
                visible=True, records_closing__gte=datetime.now()).earliest('records_closing')
        except Semester.DoesNotExist:
            if strict:
                return None
            return Semester.get_current_semester()

    @staticmethod
    def get_current_semester() -> Optional['Semester']:
        """If exists, it returns current semester, otherwise return None.

        Raises:
            MultipleObjectsReturned: Wrong semesters' dates
        """
        return Semester.get_semester(datetime.today())

    def serialize_for_json(self):
        return {
            "id": self.pk,
            "year": self.year,
            "type": self.get_type_display()
        }

    @staticmethod
    def is_visible(id):
        """Answers if semester is set as visible (displayed on course lists)."""
        param = id
        return Semester.objects.get(id=param).visible

    @staticmethod
    def get_semester_year_from_raw_year(raw_year):
        """Converts a numeric year to the string format used in the Semester model.

        Example:
            2017 is converted to 2017/18.
        """
        return "{}/{}".format(raw_year, raw_year % 100 + 1)

    class Meta:
        verbose_name = 'semestr'
        verbose_name_plural = 'semestry'
        app_label = 'courses'
        unique_together = (('type', 'year'),)
        ordering = ['-year', 'type']

    def __str__(self):
        return self.get_name()


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
        if Term.get_day_of_week(self.day) == self.weekday:
            raise ValidationError(message={
                'weekday': ['To już jest ' + days_of_week.DAYS_OF_WEEK[self.day.weekday()][1]]
            },
                                  code='invalid')

    @classmethod
    def get_day_of_week(cls, date):
        """Returns actual schedule day, with respect to ChangedDays.

        :param date:
        """
        changes = ChangedDay.objects.filter(day=date)
        if changes:
            return changes[0].day
        else:
            return Term.get_day_of_week(date)

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
