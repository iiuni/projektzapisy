"""The task defined in this module will be run asynchronously by a worker pool.

They will perform actions that must be taken but should not block server
threads. A typical example is, when a student decides to leave a group, we
should not make him wait for another student being pulled from the queue to take
place he leaves vacant.
"""
from django.conf import settings
from django.dispatch import receiver
from django_rq import job

from apps.enrollment.records.models.records import Record
from apps.enrollment.records.signals import GROUP_CHANGE_SIGNAL


@job
def pull_from_queue(group_id: int):
    """This function will pull students from the queue as long as possible."""
    while Record.pull_record_into_group(group_id):
        pass


@receiver(GROUP_CHANGE_SIGNAL)
def pull_from_queue_signal_receiver(sender, **kwargs):
    """Receives the signal call and runs pull_from_queue.

    Depending on RQ_QUEUES setting it will either run eagerly or asynchronously.
    """
    group_id = kwargs.get('group_id')
    if not settings.RUN_ASYNC:
        pull_from_queue(group_id)
    else:
        pull_from_queue.delay(group_id)
