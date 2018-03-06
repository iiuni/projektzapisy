
"""
    System State for vote
    Default values are dafined as module variables
"""
from django.core.exceptions import ObjectDoesNotExist

from django.db import models
from datetime  import date
from apps.enrollment.courses.models.semester import Semester

DEFAULT_YEAR       = date.today().year - 2
DEFAULT_MAX_POINTS = 50
DEFAULT_MAX_VOTE   = 3
DEFAULT_DAY_BEG    = 1          #
DEFAULT_DAY_END    = 31         # Te dane trzeba będzie tak ustawić
DEFAULT_MONTH_BEG  = 1          # żeby były prawdziwe. Na razie tak
DEFAULT_MONTH_END  = 7         # jest wygodnie, chociażby do testów
DEFAULT_VOTE_BEG   = date(DEFAULT_YEAR, 6, 10)
DEFAULT_VOTE_END   = date(DEFAULT_YEAR, 7, 10)
DEFAULT_CORRECTION_BEG   = date(DEFAULT_YEAR, DEFAULT_MONTH_BEG, DEFAULT_DAY_BEG)
DEFAULT_CORRECTION_END   = date(DEFAULT_YEAR, DEFAULT_MONTH_END, DEFAULT_DAY_END)

class SystemState( models.Model ):
    """
        System state for vote
    """

    semester_winter  = models.ForeignKey(Semester, on_delete=models.CASCADE,
                                         verbose_name= 'Semestr zimowy',
                                         related_name = 'winter_votes',
                                         null=True, blank=True)

    semester_summer = models.ForeignKey(Semester,
                                        on_delete=models.CASCADE,
                                        verbose_name = 'Semestr letni',
                                        related_name = 'summer_votes',
                                        null=True, blank=True)

    year      = models.IntegerField(
                    verbose_name = 'Rok akademicki',
                    default      = date.today().year)

    max_points = models.IntegerField(
                    verbose_name = 'Maksimum punktów na przedmioty',
                    default      = DEFAULT_MAX_POINTS )

    max_vote   = models.IntegerField(
                    verbose_name = 'Maksymalna wartość głosu',
                    default      =  DEFAULT_MAX_VOTE)

    vote_beg   = models.DateField(
                    verbose_name = 'Początek głosowania',
                    default      = DEFAULT_VOTE_BEG )

    vote_end   = models.DateField(
                    verbose_name = 'Koniec głosowania',
                    default      = DEFAULT_VOTE_END)

    winter_correction_beg   = models.DateField(
                    verbose_name = 'Początek korekty zimowej',
                    default      = DEFAULT_CORRECTION_BEG )

    winter_correction_end   = models.DateField(
                    verbose_name = 'Koniec korekty zimowej',
                    default      = DEFAULT_CORRECTION_END)


    summer_correction_beg   = models.DateField(
                    verbose_name = 'Początek korekty letniej',
                    default      = DEFAULT_CORRECTION_BEG )

    summer_correction_end   = models.DateField(
                    verbose_name = 'Koniec korekty letniej',
                    default      = DEFAULT_CORRECTION_END)

    class Meta:
        verbose_name        = 'ustawienia głosowania'
        verbose_name_plural = 'ustawienia głosowań'
        app_label           = 'vote'

    def __str__( self ):
        return "Ustawienia systemu na rok " + str(self.year)

    @staticmethod
    def get_state(year = None):
        """
            Gets actual system state from database
            Creates one if necessary
        """
        if not year:
            year = date.today().year
        try:
            return SystemState.objects.get(year=year)
        except ObjectDoesNotExist:
            return SystemState.create_default_state(year)

    @staticmethod
    def create_default_state(year = None):
        """
            Creates system state from default variables
        """
        if not year:
            year = date.today().year
        new_state = SystemState()
        new_state.year      = year
        new_state.max_points = DEFAULT_MAX_POINTS
        new_state.vote_beg   = date(year, 6, 10)
        new_state.vote_end   = date(year, 7, 10)
        new_state.save()
        return new_state


    def is_system_active(self):
        return self.is_vote_active() or self.is_correction_active()

    def is_vote_active(self):
        """
            Checks if vote is active
        """
        today = date.today()

        return self.vote_beg <= today <= self.vote_end


    def is_correction_active(self):
        """
            Checks if correction is active
        """

        return self.is_winter_correction_active() or self.is_summer_correction_active()


    def is_winter_correction_active(self):
        today = date.today()

        return self.winter_correction_beg <= today <= self.winter_correction_end

    def is_summer_correction_active(self):
        today = date.today()

        return self.summer_correction_beg <= today <= self.summer_correction_end
