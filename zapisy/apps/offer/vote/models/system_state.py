"""System State for vote application.

Voting cycle spans two semesters in one academic year. Thus the system state
corresponds to a single academic year.
"""
from datetime import date
import re
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models

from apps.enrollment.courses.models.semester import Semester


def _get_default_semester_for_season(season):
    """Finds a semester for upcoming year with specified type.

    Parameters:
      Season is supposed to be one of Semester.TYPE_CHOICES.
    """
    query = Semester.objects.filter(year=_get_default_year, type=season)
    try:
        return query.get().pk
    except Semester.DoesNotExist:
        return None


def _get_default_winter_semester() -> Optional[Semester]:
    return _get_default_semester_for_season(Semester.TYPE_WINTER)


def _get_default_year():
    """Usually we are creating a new system state for the upcoming year."""
    current_year = date.today().year
    return f"{current_year}/{current_year % 100 + 1}"


def _validate_year_format(value: str):
    """Verifies that the year is in format YYYY/YY."""
    match = re.fullmatch(r'(\d{4})/(\d{2})', value)
    if not match:
        raise ValidationError(f"{value} does not comply to format YYYY/YY.")
    year1 = int(match.group(1)) % 100
    year2 = int(match.group(2))
    if year1 + 1 != year2:
        raise ValidationError("Academic year should span two consecutive calendar years.")


def _get_default_summer_semester() -> Optional[Semester]:
    return _get_default_semester_for_season(Semester.TYPE_SUMMER)


class SystemState(models.Model):
    DEFAULT_MAX_POINTS = 40

    year = models.CharField(
        "Rok akademicki",
        max_length=7,
        default=_get_default_year,
        validators=[_validate_year_format])

    semester_winter = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        verbose_name="Semestr zimowy",
        related_name='+',  # Let's not pollute the semester with this.
        null=True,
        blank=True,
        default=_get_default_winter_semester)

    semester_summer = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        verbose_name="Semestr letni",
        related_name='+',  # Let's not pollute the semester with this.
        null=True,
        blank=True,
        default=_get_default_summer_semester)

    vote_beg = models.DateField("Początek głosowania", blank=True, null=True, default=None)
    vote_end = models.DateField("Koniec głosowania", blank=True, null=True, default=None)

    winter_correction_beg = models.DateField(
        "Początek korekty na semestr zimowy", blank=True, null=True)
    winter_correction_end = models.DateField(
        "Koniec korekty na semestr zimowy", blank=True, null=True)

    summer_correction_beg = models.DateField(
        "Początek korekty na semestr letni", blank=True, null=True)
    summer_correction_end = models.DateField(
        "Koniec korekty na semestr letni", blank=True, null=True)

    class Meta:
        verbose_name = 'ustawienia głosowania'
        verbose_name_plural = 'ustawienia głosowań'
        app_label = 'vote'

    def __str__(self):
        return f"Ustawienia systemu na rok akademicki {self.year}"

    @staticmethod
    def get_state_for_semester(semester: Semester) -> Optional['SystemState']:
        """Returns the state corresponding to the current semester.

        If one does not exist, returns None.
        """
        state: Optional[SystemState] = None
        if semester.type == Semester.TYPE_WINTER:
            try:
                state = SystemState.objects.get(semester_winter=semester)
            except SystemState.DoesNotExist:
                return None
        if semester.type == Semester.TYPE_SUMMER:
            try:
                state = SystemState.objects.get(semester_summer=semester)
            except SystemState.DoesNotExist:
                return None
        return state

    @staticmethod
    def get_current_state() -> Optional['SystemState']:
        """Returns an upcoming system state.

        This is a common use-case where we want a current (or upcoming if we are
        at the edge of the academic years) system state.
        """
        # Try to find current SystemState — most recent that already had voting
        # opened.
        qs = SystemState.objects.filter(vote_beg__lte=date.today())
        try:
            return qs.latest('vote_beg')
        except SystemState.DoesNotExist:
            raise

        # Edge case. Try current semester.
        semester = Semester.objects.get_next()
        return SystemState.get_state_for_semester(semester)

    def is_vote_active(self, day: Optional[date] = None) -> bool:
        """Checks if voting (not the correction) is active.

        We treat the beginning and end dates as a closed interval. Should voting
        only be active on one day, the dates should be the same.
        """
        if day is None:
            day = date.today()
        if self.vote_beg is None or self.vote_end is None:
            return False
        return self.vote_beg <= day <= self.vote_end

    def correction_active_semester(self, day: Optional[date] = None) -> Optional[Semester]:
        """Checks if correction is active.

        Returns a semester for which the correction is active, or None, if it is
        not.
        """
        if day is None:
            day = date.today()
        if self.winter_correction_beg is not None and self.winter_correction_end is not None:
            if self.winter_correction_beg <= day <= self.winter_correction_end:
                return self.semester_winter
        if self.summer_correction_beg is not None and self.summer_correction_end is not None:
            if self.summer_correction_beg <= day <= self.summer_correction_end:
                return self.semester_summer
        return None
