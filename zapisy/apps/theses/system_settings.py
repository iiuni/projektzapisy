"""Permits interaction with the theses system settings
implemented as a single instance of models.ThesesSystemSettings
"""
from . import models


def _get_settings():
    # There should only be one such object created in migrations
    # Deleting it/adding new ones is disabled in the admin, see admin.py
    return models.ThesesSystemSettings.objects.get()


def get_num_required_votes():
    """How many theses board members need to vote "yes" before a thesis
    is considered accepted
    """
    return _get_settings().num_required_votes


def get_master_rejecter():
    """Get the special board member responsible for rejecting theses"""
    return _get_settings().master_rejecter
