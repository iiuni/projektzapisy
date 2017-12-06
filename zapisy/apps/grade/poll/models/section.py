# -*- coding: utf-8 -*-
from sys       import maxsize
from django.db import models

from .open_question            import OpenQuestionOrdering
from .single_choice_question   import SingleChoiceQuestionOrdering
from .multiple_choice_question import MultipleChoiceQuestionOrdering
from .utils                    import ordering_cmp

class Section( models.Model ):
    title       = models.CharField( max_length = 50,  verbose_name = 'tytuł' )
    description = models.TextField( blank = True, verbose_name = 'opis' )
    poll        = models.ManyToManyField( 'Poll', verbose_name = 'ankieta',
                                          through = 'SectionOrdering' )
    deleted     = models.BooleanField( blank = False, null = False, default = False, verbose_name = 'usunięta' )

    class Meta:
        verbose_name        = 'sekcja'
        verbose_name_plural = 'sekcje'
        app_label           = 'poll'
        ordering            = ['title']

    def __str__( self ):
        return str( self.title )

    def all_questions( self ):
        open            = OpenQuestionOrdering.objects.filter( sections = self ).select_related('question')
        single_choice   = SingleChoiceQuestionOrdering.objects.filter( sections = self ).select_related()
        multiple_choice = MultipleChoiceQuestionOrdering.objects.filter( sections = self ).select_related()

        orderings = list( open ) + list( single_choice ) + list( multiple_choice )
        orderings.sort( ordering_cmp )
        return [o.question for o in orderings]

    def all_answers( self, poll ):
        result = []
        for question in self.all_questions():
            result.append( question.get_all_answers_from_poll( poll, self ))
        return self, result

    def all_answers_for_ticket( self, poll, ticket ):
        result = []
        for question in self.all_questions():
            result.append( question.get_all_answers_from_poll_for_ticket( poll, self, ticket ))
        return self, result

class SectionOrdering( models.Model ):
    poll     = models.ForeignKey( 'Poll',      verbose_name = 'ankieta' )
    section  = models.ForeignKey( Section, verbose_name = 'sekcja' )
    position = models.IntegerField( verbose_name = 'pozycja' )

    class Meta:
        verbose_name_plural = 'pozycje sekcji'
        verbose_name        = 'pozycja sekcji'
        ordering            = [ 'poll', 'position' ]
        unique_together     = [ 'poll', 'position' ]
        app_label           = 'poll'

    def __str__( self ):
        return str( self.position ) + '[' + str( self.poll ) + ']' + str( self.section )
