# -*- coding: utf-8 -*-
from django.db import models

class Option( models.Model ):
    content  = models.CharField( max_length = 250, verbose_name = 'treść' )
    
    class Meta:
        verbose_name_plural = 'opcje'
        verbose_name        = 'opcja'
        app_label           = 'poll'
        
    def __unicode__( self ):
        return str( self.content )
