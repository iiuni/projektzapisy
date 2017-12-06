# -*- coding: utf-8 -*-
from django.db     import models

from .base_question import BaseQuestion
from .option        import Option
from .saved_ticket  import SavedTicket
    
class SingleChoiceQuestion( BaseQuestion ):
    sections = models.ManyToManyField( 'Section',    
                                       verbose_name = 'sekcje', 
                                       through = 'SingleChoiceQuestionOrdering' )
                                      
    is_scale = models.BooleanField(    verbose_name = 'skala', default=False)
    options  = models.ManyToManyField( Option, 
                                       verbose_name = 'odpowiedzi' )
    
    class Meta:
        verbose_name_plural = 'pytania jednokrotnego wyboru'
        verbose_name        = 'pytanie jednokrotnego wyboru'
        app_label           = 'poll'
        abstract            = False
        
    def get_all_answers_from_poll( self, poll, section ):
        sts = SavedTicket.objects.filter( poll = poll )
        result = []
        for st in sts:
            result += st.singlechoicequestionanswer_set.filter( question = self, section = section )
        return self, result

    def get_all_answers_from_poll_for_ticket(self, poll, section, ticket):
        result = []
        result += ticket.singlechoicequestionanswer_set.filter( question = self, section = section )
        return self, result         

class SingleChoiceQuestionOrdering( models.Model ):
    question   = models.ForeignKey( SingleChoiceQuestion, 
                                    verbose_name = 'pytanie' )
    sections   = models.ForeignKey( 'Section', verbose_name = 'sekcja' )
    position   = models.IntegerField( verbose_name = 'pozycja' )
    is_leading = models.BooleanField( verbose_name = 'pytanie wiodące', default=False )
    hide_on    = models.ManyToManyField( Option,
                                         verbose_name = 'ukryj sekcję przy \
                                                         odpowiedziach',
                                         blank = True )
    class Meta:
        verbose_name_plural = 'pozycje pytań jednokrotnego wyboru'
        verbose_name        = 'pozycja pytań jednokrotnego wyboru'
        ordering            = [ 'sections', '-is_leading', 'position' ]
        unique_together     = [ 'sections', 'is_leading', 'position' ]
        app_label           = 'poll' 

    def __unicode__( self ):
        return str( self.position ) + '[' + str( self.sections ) + ']' + str( self.question )
