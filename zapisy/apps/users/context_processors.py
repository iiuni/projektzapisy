from apps.users.models import is_external_contractor, is_employee, is_student


def roles(request):
    """Merge user's group membership info into template context."""
    return {
        'is_employee': is_employee(request.user),
        'is_external_contractor': is_external_contractor(request.user),
        'is_student': is_student(request.user),
    }
