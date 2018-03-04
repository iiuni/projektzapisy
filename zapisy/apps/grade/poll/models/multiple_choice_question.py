# -*- coding: utf-8 -*-
from django.db     import models

from .base_question import BaseQuestion
from .option        import Option
from .saved_ticket  import SavedTicket

class MultipleChoiceQuestion( BaseQuestion ):
    sections     = models.ManyToManyField( 'Section',
                                            verbose_name = 'sekcje',
                                            through = 'MultipleChoiceQuestionOrdering' )
    has_other    = models.BooleanField(     verbose_name = 'opcja inne' , default=False)
    choice_limit = models.IntegerField(     verbose_name = 'maksimum opcji do wyboru' )
    options      = models.ManyToManyField(  Option,
                                            verbose_name = 'odpowiedzi' )

    class Meta:
        verbose_name_plural = 'pytania wielokrotnego wyboru'
        verbose_name        = 'pytanie wielokrotnego wyboru'
        app_label           = 'poll'
        abstract            = False

    def get_all_answers_from_poll( self, poll, section ):
        sts = SavedTicket.objects.filter( poll = poll )
        result = []
        for st in sts:
            result += st.multiplechoicequestionanswer_set.filter( question = self, section = section )
        return self, result

    def get_all_answers_from_poll_for_ticket(self, poll, section, ticket):
        result = []
        result += ticket.multiplechoicequestionanswer_set.filter( question = self, section = section )
        return self, result


class MultipleChoiceQuestionOrdering( models.Model ):
    question = models.ForeignKey( MultipleChoiceQuestion, on_delete=models.CASCADE, verbose_name = 'pytanie' )
    sections = models.ForeignKey( 'Section', verbose_name = 'sekcja', on_delete=models.CASCADE)
    position = models.IntegerField( verbose_name = 'pozycja' )

    class Meta:
        verbose_name_plural = 'pozycje pytań wielokrotnego wyboru'
        verbose_name        = 'pozycja pytań wielokrotnego wyboru'
        ordering            = [ 'sections', 'position' ]
        unique_together     = [ 'sections', 'position' ]
        app_label           = 'poll'

    def __str__( self ):
        return str( self.position ) + '[' + str( self.sections ) + ']' + str( self.question )
