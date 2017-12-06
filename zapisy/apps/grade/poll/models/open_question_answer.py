# -*- coding: utf-8 -*-
from django.db import models

from .base_answer   import BaseAnswer
from .open_question import OpenQuestion

class OpenQuestionAnswer( BaseAnswer ):
    question = models.ForeignKey( OpenQuestion, verbose_name = 'pytanie' )
    content  = models.TextField( verbose_name = 'treść', blank = True, null = True )

    class Meta:
        verbose_name_plural = 'odpowiedzi na pytania otwarte'
        verbose_name        = 'odpowiedź na pytanie otwarte'
        app_label           = 'poll'

    def __str__( self ):
        return str( self.content )
