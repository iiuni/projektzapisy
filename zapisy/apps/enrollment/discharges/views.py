"""Views for director's discharge requests (student-facing)."""

from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from apps.enrollment.courses.models import CourseInstance
from apps.users.decorators import student_required

from .models import DirectorDischarge, DischargeStatus


@student_required
@require_POST
def request_discharge(request: HttpRequest) -> HttpResponse:
    """Submits a director discharge request for a course."""
    student = request.user.student

    try:
        course_id = request.POST['course_id']
        course = CourseInstance.objects.select_related('semester').get(pk=course_id)
    except (KeyError, CourseInstance.DoesNotExist):
        raise Http404

    allowed, msg = DirectorDischarge.can_request(student, course)
    if not allowed:
        messages.error(request, msg)
    else:
        DirectorDischarge.objects.create(
            student=student,
            course=course,
            status=DischargeStatus.PENDING,
        )
        messages.success(
            request,
            f'Wniosek o wypis dyrektorski z przedmiotu „{course.name}" '
            'został złożony i oczekuje na decyzję administratora.'
        )

    return redirect('course-page', slug=course.slug)
