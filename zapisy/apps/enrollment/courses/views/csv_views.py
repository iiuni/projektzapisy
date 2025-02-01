from django.http import Http404
from apps.enrollment.courses.models.group import Group
from apps.enrollment.records.models import RecordStatus
from apps.enrollment.courses import utils
from apps.users.decorators import employee_required


@employee_required
def group_enrolled_csv(request, group_id: int):
    if not Group.objects.filter(id=group_id).exists():
        raise Http404
    return utils.recorded_students_csv([group_id], RecordStatus.ENROLLED, request.user)


@employee_required
def group_queue_csv(request, group_id: int):
    if not Group.objects.filter(id=group_id).exists():
        raise Http404
    return utils.recorded_students_csv([group_id], RecordStatus.QUEUED, request.user, preserve_ordering=True)


@employee_required
def course_enrolled_csv(request, course_slug: str):
    _, course_short_name, group_ids = utils.get_all_group_ids_for_course_slug(course_slug)
    for group_id in group_ids:
        if not Group.objects.filter(id=group_id).exists():
            raise Http404
    return utils.recorded_students_csv(group_ids, RecordStatus.ENROLLED, request.user, course_short_name)


@employee_required
def course_queue_csv(request, course_slug: str):
    _, course_short_name, group_ids = utils.get_all_group_ids_for_course_slug(course_slug)
    for group_id in group_ids:
        if not Group.objects.filter(id=group_id).exists():
            raise Http404
    group_data = utils.get_group_data(group_ids, request.user, status=RecordStatus.ENROLLED)
    students_enrolled = set()
    for group in group_data.values():
        students_enrolled.update(group.get("students", []))
    return utils.recorded_students_csv(
        group_ids,
        RecordStatus.QUEUED,
        request.user,
        course_short_name,
        exclude_students=students_enrolled
    )
