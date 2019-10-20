"""Defines custom error classes used from DRF-powered endpoints"""
from rest_framework.exceptions import APIException
from rest_framework import status


class ThesisNameConflict(APIException):
    """Raised when the user tries to set a duplicate thesis title"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Duplicate thesis title"
