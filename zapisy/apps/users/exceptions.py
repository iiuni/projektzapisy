class NonUserException(Exception):
    """Thrown when an object does not represent a user"""
    pass


class InvalidUserException(Exception):
    """
    Thrown when a user is considered to be invalid
    in a certain context
    """
    pass
