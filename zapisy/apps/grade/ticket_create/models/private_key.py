from django.db import models

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


class PrivateKey(models.Model):
    poll = models.ForeignKey('poll.Poll', verbose_name='ankieta', on_delete=models.CASCADE)
    private_key = models.TextField(verbose_name='klucz prywatny')

    class Meta:
        verbose_name = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label = 'ticket_create'

    def __str__(self):
        return 'Klucz prywatny: {}'.format(self.poll)

    def sign_ticket(self, ticket):
        key = RSA.importKey(self.private_key)
        return pkcs1_15.new(key).sign(ticket)

    def verify_signature(self, ticket, signed_ticket):
        key = RSA.importKey(self.private_key)
        return pkcs1_15.new(key).verify(ticket, signed_ticket)
