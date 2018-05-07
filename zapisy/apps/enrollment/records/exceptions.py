class NonStudentException(Exception):
    """is thrown when student does not exists"""
    pass


class NonGroupException(Exception):
    """is thrown when group does not exists"""
    pass


class AlreadyNotAssignedException(Exception):
    """is thrown when student try to sign out from not enrolled group"""
    pass


class AlreadyPinnedException(Exception):
    """is thrown when user tries to enroll to the same group twice"""
    pass


class AlreadyNotPinnedException(Exception):
    """is thrown when user tries to sign out of the group twice in row"""
    pass
