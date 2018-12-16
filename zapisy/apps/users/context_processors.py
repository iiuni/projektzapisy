from apps.users.models import BaseUser


def roles(request):
    """Merge user's group membership info into template context."""
    return {
        'is_employee': BaseUser.is_employee(request.user),
        'is_external_contractor': BaseUser.is_external_contractor(request.user),
        'is_student': BaseUser.is_student(request.user),
    }
