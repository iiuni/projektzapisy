# -*- coding: utf-8 -*-
from django.db                         import models


class Origin(models.Model):

    class Meta:
        verbose_name        = 'zestaw ankiet'
        verbose_name_plural = 'zestawy ankiet'
        app_label           = 'poll'
