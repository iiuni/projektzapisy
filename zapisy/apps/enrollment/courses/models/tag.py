# -*- coding: utf-8 -*-
from django.db import models


class Tag(models.Model):
    short_name = models.CharField(max_length=50, verbose_name='nazwa skrócona')
    full_name = models.CharField(max_length=250, verbose_name='nazwa pełna')
    description = models.TextField(verbose_name='opis')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tagi'
        app_label = 'courses'

    def __str__(self):
        return str(self.short_name) + ' (' + str(self.full_name) + ')'

    def serialize_for_json(self):
        return {
            'id': self.pk,
            'short_name': self.short_name,
            'full_name': self.full_name,
            'description': self.description
        }
