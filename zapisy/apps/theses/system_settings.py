"""Queries to the Thesis settings singleton.

The functions in this module permit interaction with the theses system settings
implemented as a single instance of models.ThesesSystemSettings.
"""
from apps.theses.enums import ThesisStatus, ThesisVote

from . import models


def _get_settings():
    """Get only existing instance of theses system settings object."""
    # There should only be one such object created in migrations
    # Deleting it/adding new ones is disabled in the admin, see admin.py
    return models.ThesesSystemSettings.objects.get()


def get_num_required_votes():
    """How many board members must vote "yes" before a thesis is accepted?"""
    return _get_settings().num_required_votes


def get_master_rejecter():
    """Get the special board member responsible for rejecting theses."""
    return _get_settings().master_rejecter


def change_status(thesis, vote):
    """Implements status changes.

    Status changes automatically of a thesis depending on previous votes, new
    vote and assigned students.
    """
    if vote == ThesisVote.ACCEPTED and thesis.get_accepted_votes() >= get_num_required_votes() - 1:
        if thesis.has_no_students_assigned:
            thesis.status = ThesisStatus.ACCEPTED
        else:
            thesis.status = ThesisStatus.IN_PROGRESS
        thesis.save()
