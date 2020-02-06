from Crypto.PublicKey import RSA
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.models.rsa_keys import RSAKeys
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Poll)
def save_keys_on_poll_created(sender, instance, created, **kwargs):
    if created:
        keys = generate_key()
        save_keys(instance, keys)


def save_keys(poll, keys):
    rsa_keys = RSAKeys(poll=poll, private_key=keys[0], public_key=keys[1])
    rsa_keys.save()


def generate_key():
    length = 1024
    key = RSA.generate(length)
    private_key = key.exportKey('PEM').\
        decode(encoding='ascii', errors='strict')
    public_key = key.publickey().exportKey('PEM').\
        decode(encoding='ascii', errors='strict')
    return (private_key, public_key)
