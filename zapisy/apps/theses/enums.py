"""Defines several thesis-related enums.

Using a separate file for these definitions helps prevent
circular dependencies
"""
from django.db import models


class ThesisKind(models.IntegerChoices):
    MASTERS = 0, "mgr"
    ENGINEERS = 1, "inż"
    BACHELORS = 2, "lic"
    ISIM = 3, "isim"
    # Certain theses will be appropriate for both bachelor and engineer degrees
    BACHELORS_ENGINEERS = 4, "lic+inż"
    BACHELORS_ENGINEERS_ISIM = 5, "lic+inż+isim"


class ThesisStatus(models.IntegerChoices):
    BEING_EVALUATED = 1, "weryfikowana przez komisję"
    RETURNED_FOR_CORRECTIONS = 2, "zwrócona do poprawek"
    ACCEPTED = 3, "zaakceptowana"
    IN_PROGRESS = 4, "w realizacji"
    DEFENDED = 5, "obroniona"


class ThesisVote(models.IntegerChoices):
    NONE = 1, "brak głosu"
    REJECTED = 2, "odrzucona"
    ACCEPTED = 3, "zaakceptowana"
