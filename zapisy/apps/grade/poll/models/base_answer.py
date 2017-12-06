# -*- coding: utf-8 -*-
from django.db import models

from .saved_ticket import SavedTicket
from .section      import Section

class BaseAnswer( models.Model ):
    saved_ticket = models.ForeignKey( SavedTicket, verbose_name = 'zapisany bilet' )
    section      = models.ForeignKey( Section,     verbose_name = 'sekcja' )
    time         = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
