from django.contrib import messages
from django.shortcuts import redirect
from django.http import Http404
from django.views.decorators.http import require_POST

from apps.enrollment.courses.models import Group
from apps.enrollment.records.models.records import Record
from apps.users.decorators import student_required
from apps.users.models import Student


@student_required
@require_POST
def enqueue(request):
    """Puts the student into the group queue."""
    student: Student = request.user.student
    group: Group = None
    try:
        group_id = request.POST['group_id']
        group = Group.objects.select_related('course').get(pk=group_id)
    except (KeyError, Group.DoesNotExist):
        raise Http404

    if Record.enqueue_student(student, group):
        messages.success(
            request, (
                "Jesteś w kolejce. Jak tylko w grupie będzie wolne miejsce "
                "(być może natychmiast), zostaniesz do niej wciągnięty."
            )
        )
    else:
        messages.warning(request, "Nie udało się dopisać do kolejki.")
    return redirect('course-page', slug=group.course.slug)


@student_required
@require_POST
def dequeue(request):
    """Removes the student from the group or its queue."""
    student: Student = request.user.student
    group: Group = None
    try:
        group_id = request.POST['group_id']
        group = Group.objects.select_related('course').get(pk=group_id)
    except (KeyError, Group.DoesNotExist):
        raise Http404

    if Record.remove_from_group(student, group):
        messages.success(request, "Usunięto rekord z grupy/kolejki.")
    else:
        messages.warning(request, "Nie udało się usunąć z grupy/kolejki.")
    return redirect('course-page', slug=group.course.slug)
