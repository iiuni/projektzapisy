from typing import Tuple

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from django.db import models


class PrivateKey(models.Model):
    poll = models.ForeignKey('poll.Poll', verbose_name='ankieta', on_delete=models.CASCADE)
    private_key = models.TextField(verbose_name='klucz prywatny')

    class Meta:
        verbose_name = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label = 'ticket_create'

    def __str__(self):
        return 'Klucz prywatny: {}'.format(self.poll)

    @staticmethod
    def _int_from_bytes(xbytes: bytes) -> int:
        return int.from_bytes(xbytes, 'big')

    # FIXME the return type of this method is due to legacy ticket
    # handling code in ticket_create/views and poll/utils
    def sign_ticket(self, ticket: str) -> Tuple[int]:
        key = RSA.importKey(self.private_key)
        ticket_hash = SHA256.new(ticket.encode("utf-8"))
        signed = pkcs1_15.new(key).sign(ticket_hash)
        signed_as_int = PrivateKey._int_from_bytes(signed)
        return (signed_as_int, )
