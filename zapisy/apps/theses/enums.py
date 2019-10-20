"""Defines several thesis-related enums.
Using a separate file for these definitions helps prevent
circular dependencies
"""
from enum import Enum
from choicesenum import ChoicesEnum


class ThesisKind(ChoicesEnum):
    MASTERS = 0, "mgr"
    ENGINEERS = 1, "inż"
    BACHELORS = 2, "lic"
    ISIM = 3, "isim"
    # Certain theses will be appropriate for both bachelor and engineer degrees
    BACHELORS_ENGINEERS = 4, "lic+inż"
    BACHELORS_ENGINEERS_ISIM = 5, "lic+inż+isim"


class ThesisStatus(ChoicesEnum):
    BEING_EVALUATED = 1, "weryfikowana przez komisję"
    RETURNED_FOR_CORRECTIONS = 2, "zwrócona do poprawek"
    ACCEPTED = 3, "zaakceptowana"
    IN_PROGRESS = 4, "w realizacji"
    DEFENDED = 5, "obroniona"


class ThesisTypeFilter(Enum):
    """Various values for the "thesis type" filter in the main UI view
    Must match values in backend_callers.ts (this is what client code
    will send to us)
    """
    EVERYTHING = 0
    CURRENT = 1
    ARCHIVED = 2
    MASTERS = 3
    ENGINEERS = 4
    BACHELORS = 5
    BACHELORS_OR_ENGINEERS = 6
    ISIM = 7
    AVAILABLE_MASTERS = 8
    AVAILABLE_ENGINEERS = 9
    AVAILABLE_BACHELORS = 10
    AVAILABLE_BACHELORS_OR_ENGINEERS = 11
    AVAILABLE_ISIM = 12
    UNGRADED = 13

    DEFAULT = EVERYTHING


# Determines the thesis kinds that match given filter values
# i.e. if the user asks for all engineer theses, we assume they want
# all theses suitable for engineer degrees, so bachelors+engineers should
# be returned as well
ENGINEERS_KINDS = (
    ThesisKind.ENGINEERS, ThesisKind.BACHELORS_ENGINEERS, ThesisKind.BACHELORS_ENGINEERS_ISIM
)
BACHELORS_KINDS = (
    ThesisKind.BACHELORS, ThesisKind.BACHELORS_ENGINEERS, ThesisKind.BACHELORS_ENGINEERS_ISIM
)
BACHELORS_OR_ENGINEERS_KINDS = tuple(set(ENGINEERS_KINDS + BACHELORS_KINDS))
ISIM_KINDS = (
    ThesisKind.ISIM, ThesisKind.BACHELORS_ENGINEERS_ISIM
)

# Thesis with these statuses are not ready for "public consumption"
# and so won't be shown to students
NOT_READY_STATUSES = (
    ThesisStatus.BEING_EVALUATED,
    ThesisStatus.RETURNED_FOR_CORRECTIONS
)


class ThesisVote(ChoicesEnum):
    NONE = 1, "brak głosu"
    REJECTED = 2, "odrzucona"
    ACCEPTED = 3, "zaakceptowana"


"""Voting for a thesis in one of these statuses is not permitted
for regular board members
"""
UNVOTEABLE_STATUSES = (
    ThesisStatus.ACCEPTED,
    ThesisStatus.IN_PROGRESS,
    ThesisStatus.DEFENDED
)


class ThesisUserType(Enum):
    """Used only by serializers, to tell frontend client code
    about various user types
    """
    STUDENT = 0
    REGULAR_EMPLOYEE = 1
    ADMIN = 2
    NONE = 3
