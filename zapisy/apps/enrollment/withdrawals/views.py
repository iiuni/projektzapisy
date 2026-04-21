"""Views for director's withdrawal requests (student-facing)."""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from apps.enrollment.courses.models import CourseInstance
from apps.users.decorators import student_required

from . import services


@student_required
@require_POST
def request_withdrawal(request):
    """Submits a director withdrawal request for a course."""
    student = request.user.student

    try:
        course_id = request.POST['course_id']
        course = CourseInstance.objects.select_related('semester').get(pk=course_id)
    except (KeyError, CourseInstance.DoesNotExist):
        raise Http404

    try:
        services.request_withdrawal(student, course)
        messages.success(
            request,
            f'Wniosek o wypis dyrektorski z przedmiotu „{course.name}" '
            'został złożony i oczekuje na decyzję administratora.'
        )
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('course-page', slug=course.slug)
