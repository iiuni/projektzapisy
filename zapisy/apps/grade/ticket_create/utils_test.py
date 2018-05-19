from django.test import SimpleTestCase

from Crypto.PublicKey import RSA

KEY_LENGTH = 256


class UtilsTestCase(SimpleTestCase):
    @classmethod
    def setUpTestData(cls):
        rsa = RSA.generate(KEY_LENGTH)
        cls.private_key = rsa.exportKey()
        cls.public_key = rsa.publicKey().exportKey()

    def test_should_blind_ticket(self):
        pass
