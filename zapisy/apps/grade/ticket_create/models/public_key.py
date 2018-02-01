# -*- coding: utf-8 -*-
from django.db                import models

class PublicKey( models.Model ):
    poll       = models.ForeignKey( 'poll.Poll', verbose_name = 'ankieta' , on_delete=models.CASCADE)
    public_key = models.TextField(  verbose_name = 'klucz publiczny' )
    
    class Meta:
        verbose_name        = 'klucz publiczny'
        verbose_name_plural = 'klucze publiczne'
        app_label           = 'ticket_create'
        
    def __unicode__( self ):
        return u"Klucz publiczny: " + unicode( self.poll )
