class NonCourseException(Exception):
    """is thrown when course does not exists"""
    pass

class NonSemesterException(Exception):
    """is thrown when semester does not exists"""
    pass

class MoreThanOneCurrentSemesterException(Exception):
    """is thrown when two or more semesters take place in the same time"""
    pass

class MoreThanOneSemesterWithOpenRecordsException(Exception):
    """is thrown when enrollments for more than one semester are open in the same time"""
    pass
