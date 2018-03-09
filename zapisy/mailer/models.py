from datetime import datetime

from django.db import models


PRIORITIES = (
    ('1', 'wysoki'),
    ('2', 'średni'),
    ('3', 'niski'),
    ('4', 'odroczona'),
)



class MessageManager(models.Manager):

    def high_priority(self):
        """
        the high priority messages in the queue
        """

        return self.filter(priority='1')

    def medium_priority(self):
        """
        the medium priority messages in the queue
        """

        return self.filter(priority='2')

    def low_priority(self):
        """
        the low priority messages in the queue
        """

        return self.filter(priority='3')

    def non_deferred(self):
        """
        the messages in the queue not deferred
        """

        return self.filter(priority__lt='4')

    def deferred(self):
        """
        the deferred messages in the queue
        """

        return self.filter(priority='4')

    def retry_deferred(self, new_priority=2):
        count = 0
        for message in self.deferred():
            if message.retry(new_priority):
                count += 1
        return count


class Message(models.Model):

    objects = MessageManager()

    to_address = models.CharField(max_length=50, verbose_name = 'odbiorca')
    from_address = models.CharField(max_length=50, verbose_name = 'nadawca')
    subject = models.CharField(max_length=100, verbose_name = 'temat')
    message_body = models.TextField(verbose_name = 'treść')
    message_body_html = models.TextField(blank=True, verbose_name = 'treść html')
    when_added = models.DateTimeField(default=datetime.now, verbose_name = 'dodano')
    priority = models.CharField(max_length=1, choices=PRIORITIES, default='2', verbose_name = 'priorytet')
    # @@@ campaign?
    # @@@ content_type?

    class Meta:
        verbose_name        = 'wiadomość'
        verbose_name_plural = 'wiadomości'

    def defer(self):
        self.priority = '4'
        self.save()

    def retry(self, new_priority=2):
        if self.priority == '4':
            self.priority = new_priority
            self.save()
            return True
        else:
            return False


class DontSendEntryManager(models.Manager):

    def has_address(self, address):
        """
        is the given address on the don't send list?
        """

        if self.filter(to_address=address).count() > 0: # @@@ is there a better way?
            return True
        else:
            return False


class DontSendEntry(models.Model):

    objects = DontSendEntryManager()

    to_address = models.CharField(max_length=50,  verbose_name = 'adres')
    when_added = models.DateTimeField(verbose_name = 'od kiedy')
    # @@@ who added?
    # @@@ comment field?

    class Meta:
        verbose_name = 'blokada'
        verbose_name_plural = 'blokady'


RESULT_CODES = (
    ('1', 'sukces'),
    ('2', 'nie wysłane'),
    ('3', 'niepowodzenie'),
    # @@@ other types of failure?
)


class MessageLogManager(models.Manager):

    def log(self, message, result_code, log_message = ''):
        """
        create a log entry for an attempt to send the given message and
        record the given result and (optionally) a log message
        """

        message_log = self.create(
            to_address = message.to_address,
            from_address = message.from_address,
            subject = message.subject,
            message_body = message.message_body,
            message_body_html = message.message_body_html,
            when_added = message.when_added,
            priority = message.priority,
            # @@@ other fields from Message
            result = result_code,
            log_message = log_message,
        )
        message_log.save()


class MessageLog(models.Model):

    objects = MessageLogManager()

    # fields from Message
    to_address = models.CharField(max_length=50, verbose_name = 'odbiorca')
    from_address = models.CharField(max_length=50, verbose_name = 'nadawca')
    subject = models.CharField(max_length=100, verbose_name = 'temat')
    message_body = models.TextField(verbose_name = 'treść')
    message_body_html = models.TextField(blank=True, verbose_name = 'treść html')
    when_added = models.DateTimeField(verbose_name = 'dodano')
    priority = models.CharField(max_length=1, choices=PRIORITIES, verbose_name = 'priorytet')
    # @@@ campaign?

    # additional logging fields
    when_attempted = models.DateTimeField(default=datetime.now, verbose_name = 'czas próby')
    result = models.CharField(max_length=1, choices=RESULT_CODES, verbose_name = 'wynik')
    log_message = models.TextField(verbose_name = 'wiadomość') # jakaś lepsza nazwa?

    class Meta:
        verbose_name = 'log'
        verbose_name_plural = 'logi'
