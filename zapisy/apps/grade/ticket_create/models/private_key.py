from django.db import models
from Crypto.PublicKey import RSA


class PrivateKey(models.Model):
    """
    Private RSA key for poll in PEM format.
    """
    poll = models.ForeignKey('poll.Poll', verbose_name='ankieta', on_delete=models.CASCADE)
    private_key = models.TextField(verbose_name='klucz prywatny')

    class Meta:
        verbose_name = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label = 'ticket_create'

    def __str__(self):
        return f'Klucz prywatny: {self.poll}'

    def import_rsa_key(self):
        return RSA.importKey(self.private_key)
