"""Views for director's withdrawal requests (student-facing)."""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.enrollment.courses.models import CourseInstance
from apps.users.decorators import student_required

from . import services
from .models import DirectorWithdrawal


@student_required
def withdrawal_list(request):
    """Shows the student their director withdrawal requests and remaining quota."""
    student = request.user.student

    withdrawals = DirectorWithdrawal.objects.filter(student=student)
    withdrawals = withdrawals.select_related('course', 'course__semester', 'decided_by')

    used_total = services.get_withdrawals_used_total(student)
    remaining = max(0, student.withdrawal_limit - used_total)

    return render(request, 'withdrawals/withdrawal_list.html', {
        'withdrawals': withdrawals,
        'used_total': used_total,
        'withdrawal_limit': student.withdrawal_limit,
        'remaining': remaining,
    })


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

    return redirect('withdrawals:list')
