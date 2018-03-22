import logging
from django.core.management.base import BaseCommand
from mailer.models import Message

logger = logging.getLogger('mailer.retry_deferred')


class Command(BaseCommand):
    help = 'Attempt to resend any deferred mail.'

    def handle(self, *args, **options):
        logger.info("-" * 72)
        count = Message.objects.retry_deferred()  # @@@ new_priority not yet supported
        logger.info("%s message(s) retried" % count)
