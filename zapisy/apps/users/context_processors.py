from apps.users.models import is_employee, is_external_contractor, is_student
from django.contrib.messages.api import get_messages


def roles(request):
    """Merge user's group membership info into template context."""
    return {
        'is_employee': is_employee(request.user),
        'is_external_contractor': is_external_contractor(request.user),
        'is_student': is_student(request.user),
    }


def messages(request):
    """Remove duplicated messages"""
    unique_messages = {(m.level, m.message): m for m in get_messages(request)}
    return {'messages': unique_messages.values()}
