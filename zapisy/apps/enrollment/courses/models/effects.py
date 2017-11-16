# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import smart_unicode


class Effects(models.Model):
    group_name = models.CharField(max_length=250, verbose_name=u'grupa efektów')
    description = models.TextField(verbose_name=u'opis', null=True, blank=True)

    class Meta:
        verbose_name = u'Grupa Efektów'
        verbose_name_plural = u'Grupy Efektów'
        app_label = 'courses'

    def __unicode__(self):
        return smart_unicode(self.group_name)

    def serialize_for_json(self):
        return {
            'id': self.pk,
            'name': self.group_name,
            'description': self.description
        }
