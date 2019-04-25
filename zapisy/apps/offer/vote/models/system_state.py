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
        raise ValidationError(
            "%(value)s does not comply to format YYYY/YY.", params={'value', value})
    year1 = int(match.group(1)) % 100
    year2 = int(match.group(2))
    if year1 + 1 != year2:
        raise ValidationError("Academic year should span two consecutive calendar years.")


def _get_default_summer_semester() -> Optional[Semester]:
    return _get_default_semester_for_season(Semester.TYPE_SUMMER)


class SystemState(models.Model):
    DEFAULT_MAX_POINTS = 50

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
