from apps.users.roles import Roles


def roles(request):
    """Merge user's group membership info into template context."""
    return {
        'is_employee': Roles.is_employee(request.user),
        'is_external_contractor': Roles.is_external_contractor(request.user),
        'is_student': Roles.is_student(request.user),
    }
