"""This module will define signals triggering asynchronous actions.

Every user of the `enrollment.records` app can send this signal instead of
running the job directly. This will be useful for testing, where we can patch
the signal receiver.
"""
from django.dispatch import Signal

GROUP_CHANGE_SIGNAL = Signal(providing_args=['group_id'])
