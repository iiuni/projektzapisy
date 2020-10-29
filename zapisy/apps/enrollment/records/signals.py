"""This module will define signals triggering asynchronous actions.

Every user of the `enrollment.records` app can send this signal instead of
running the job directly. This will be useful for testing, where we can patch
the signal receiver.
"""
from django.dispatch import Signal

# Signal senders must provide a `group_id` argument.
GROUP_CHANGE_SIGNAL = Signal()
