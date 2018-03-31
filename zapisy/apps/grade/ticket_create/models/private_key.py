from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from django.db import models

def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')

class PrivateKey(models.Model):
    poll = models.ForeignKey('poll.Poll', verbose_name='ankieta', on_delete=models.CASCADE)
    private_key = models.TextField(verbose_name='klucz prywatny')

    class Meta:
        verbose_name = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label = 'ticket_create'

    def __str__(self):
        return 'Klucz prywatny: {}'.format(self.poll)

    def sign_ticket(self, ticket: str) -> str:
        key = RSA.importKey(self.private_key)
        ticket_hash = SHA256.new(ticket.encode("utf-8"))
        signed = pkcs1_15.new(key).sign(ticket_hash)
        signed_as_int = int_from_bytes(signed)
        return (signed_as_int, )
