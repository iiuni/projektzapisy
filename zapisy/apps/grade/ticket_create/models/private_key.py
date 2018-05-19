# -*- coding: utf-8 -*-
from django.db import models

from Crypto.PublicKey import RSA


class PrivateKey(models.Model):
    poll = models.ForeignKey('poll.Poll', verbose_name='ankieta', on_delete=models.CASCADE)
    private_key = models.TextField(verbose_name='klucz prywatny')

    class Meta:
        verbose_name = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label = 'ticket_create'

    def __unicode__(self):
        return u"Klucz prywatny: " + unicode(self.poll)
