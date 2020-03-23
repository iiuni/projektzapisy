def mailto(author, students, bcc=False):
    """Helper method to create mailto links"""
    result = author.email

    if students:
        return result + ('?bcc=' if bcc else ',') + \
            ','.join([student.user.email.replace('+', '%2B') for student in students])
    return result
