"""System State for vote application.

Voting cycle spans two semesters in one academic year. Thus the system state
corresponds to a single academic year.
"""
from datetime import date
import re
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

from apps.enrollment.courses.models.semester import Semester

DEFAULT_MAX_POINTS = 50
DEFAULT_MAX_VOTE = 3


class SystemState(models.Model):

    semester_winter = models.ForeignKey(Semester, on_delete=models.CASCADE,
                                        verbose_name="Semestr zimowy",
                                        related_name='winter_votes',
                                        null=True, blank=True)

    semester_summer = models.ForeignKey(Semester,
                                        on_delete=models.CASCADE,
                                        verbose_name="Semestr letni",
                                        related_name='summer_votes',
                                        null=True, blank=True)

    def get_default_year():
        """Usually we are creating a new system state for the upcoming year."""
        current_year = date.today().year
        return f"{current_year}/{current_year % 100 + 1}"

    def validate_year_format(value: str):
        """Verifies that the year is in format YYYY/YY."""
        m = re.fullmatch('(\d{4})/(\d{2})', value)
        if not m:
            raise ValidationError(
                "%(value)s does not comply to format YYYY/YY.", params={'value', value})
        y1 = int(m.group(1)) % 100
        y2 = int(m.group(2))
        if y1 + 1 != y2:
            raise ValidationError("Academic year should span two calendar years.")


    year = models.CharField("Rok akademicki", max_length=7,
        default=get_default_year, validators=[validate_year_format])

    vote_beg = models.DateField("Początek głosowania", null=True, default=None)
    vote_end = models.DateField("Koniec głosowania", null=True, default=None)

    winter_correction_beg = models.DateField(
        "Początek korekty na semestr zimowy", null=True, default=None)
    winter_correction_end = models.DateField(
        "Koniec korekty na semestr zimowy", null=True, default=None)

    summer_correction_beg = models.DateField(
        "Początek korekty na semestr letni", null=True, default=None)
    summer_correction_end = models.DateField(
        "Koniec korekty na semestr letni", null=True, default=True)

    class Meta:
        verbose_name = 'ustawienia głosowania'
        verbose_name_plural = 'ustawienia głosowań'
        app_label = 'vote'

    def __str__(self):
        return f"Ustawienia systemu na rok akademicki {self.year}"

    @staticmethod
    def get_current_state() -> Optional['SystemState']:
        """Returns the state corresponding to the current semester.
        
        If one does not exist, returns None.
        """
        state: Optional[SystemState] = None
        s = Semester.objects.get_next()
        if s.type == Semester.TYPE_WINTER:
            try:
                state = SystemState.objects.get(semester_winter=s)
            except SystemState.DoesNotExist:
                return None
        if s.type == Semester.TYPE_SUMMER:
            try:
                state = SystemState.objects.get(semester_summer=s)
            except SystemState.DoesNotExist:
                return None
        return state
