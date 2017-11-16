# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import smart_unicode


class Tag(models.Model):
    short_name = models.CharField(max_length=50, verbose_name=u'nazwa skrócona')
    full_name = models.CharField(max_length=250, verbose_name=u'nazwa pełna')
    description = models.TextField(verbose_name=u'opis')

    class Meta:
        verbose_name = u'Tag'
        verbose_name_plural = u'Tagi'
        app_label = 'courses'

    def __unicode__(self):
        return smart_unicode(self.short_name) + u' (' + smart_unicode(self.full_name) + u')'

    def serialize_for_json(self):
        return {
            'id': self.pk,
            'short_name': self.short_name,
            'full_name': self.full_name,
            'description': self.description
        }
