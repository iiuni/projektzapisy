from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
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
                "(być może natychmiast), zostaniesz do niej wciągnięty przez "
                "asynchroniczny proces."
            )
        )
        if not Record.can_enroll(student, group):
            messages.warning(request,
                             ("W tym momencie nie spełniasz kryteriów zapisu do tej grupy. "
                              "Jeśli nie  zmieni się to do czasu wciągania Twojego rekordu "
                              "z  kolejki, zostanie on usunięty."))
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


@student_required
@require_POST
def queue_set_priority(request):
    """Sets the queue priority."""
    student: Student = request.user.student
    try:
        group_id = request.POST['group_id']
        group = Group.objects.select_related('course').get(pk=group_id)
    except (KeyError, Group.DoesNotExist):
        raise Http404
    priority = int(request.POST['priority'])
    if Record.set_queue_priority(student, group, priority):
        messages.success(request, "Zmieniono priorytet kolejki.")
    else:
        messages.warning(request, "Priorytet kolejki nie zmieniony.")
    return redirect('course-page', slug=group.course.slug)
