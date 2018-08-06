from django.db import models
from Crypto.PublicKey import RSA


class PublicKey(models.Model):
    """
    Public RSA key in PEM format. It comes together with private key.
    See apps.grade.poll.models.private_key.py
    """
    poll = models.ForeignKey('poll.Poll', verbose_name='ankieta', on_delete=models.CASCADE)
    public_key = models.TextField(verbose_name='klucz publiczny')

    class Meta:
        verbose_name = 'klucz publiczny'
        verbose_name_plural = 'klucze publiczne'
        app_label = 'ticket_create'

    def __str__(self):
        return "Klucz publiczny: " + str(self.poll)

    def import_rsa_key(self):
        return RSA.importKey(self.public_key)
