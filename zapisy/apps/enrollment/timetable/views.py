"""Views for timetable and prototype."""
import json
from typing import List

from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import Http404, HttpResponse, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.cache_utils import cache_result_for
from apps.enrollment.courses.models import Course, Group, Semester
from apps.enrollment.courses.templatetags.course_types import \
    decode_class_type_singular
from apps.enrollment.records.models import Record, RecordStatus
from apps.enrollment.timetable.models import Pin
from apps.users.decorators import student_required


def build_group_list(groups: List[Group]):
    """Builds a serializable object containing relevant information about groups

    The information must be sufficient to display information in the timetable
    and perform actions (enqueuing/dequeuing).
    """
    stats = Record.groups_stats(groups)
    group_dicts = []
    group: Group
    for group in groups:
        group_dict = model_to_dict(group, fields=['id', 'limit', 'extra'])
        term_dicts = []
        for term in group.term.all():
            term_dict = model_to_dict(term, fields=['dayOfWeek', 'start_time', 'end_time'])
            term_dict['classrooms'] = term.numbers()
            term_dicts.append(term_dict)
        group_dict.update({
            'course': {
                'url': reverse('course-page', args=(group.course.slug, )),
                'entity': model_to_dict(group.course.entity, fields=['name', 'shortName']),
            },
            'type': decode_class_type_singular(group.type),
            'url': reverse('group-view', args=(group.pk, )),
            'teacher': {
                'id': group.teacher_id,
                'url': reverse('employee-profile', args=(group.teacher.user_id, )),
                'name': group.teacher.user.get_full_name(),
            },
            'num_enrolled': stats.get(group.pk).get('num_enrolled'),
            'term': term_dicts,
            'is_enrolled': getattr(group, 'is_enrolled', None),
            'is_enqueued': getattr(group, 'is_enqueued', None),
            'is_pinned': getattr(group, 'is_pinned', None),
            'can_enqueue': getattr(group, 'can_enqueue', None),
            'can_dequeue': getattr(group, 'can_dequeue', None),
            'action_url': reverse('prototype-action', args=(group.pk, )),
        })
        group_dicts.append(group_dict)
    return group_dicts


def list_courses_in_semester(semester: Semester):
    """Returns a JSON of all the course names in semester.

    This list will be used in prototype.
    """
    courses = Course.objects.filter(semester=semester).select_related('entity').values(
        'id', 'entity__name')
    for course in courses:
        course.update({
            'url': reverse('prototype-get-course', args=(course['id'], )),
        })
    return json.dumps(list(courses))


@student_required
def my_timetable(request):
    """Shows the student his own timetable page."""
    student = request.user.student
    semester = Semester.objects.get_next()
    # This costs an additional join, but works if there is no current semester.
    records = Record.objects.filter(
        student=student, group__course__semester=semester, status=RecordStatus.ENROLLED
    ).select_related(
        'group__teacher', 'group__teacher__user', 'group__course', 'group__course__entity'
    ).prefetch_related('group__term', 'group__term__classrooms')
    groups = [r.group for r in records]
    group_dicts = build_group_list(groups)

    data = {
        'groups_json': json.dumps(group_dicts, cls=DjangoJSONEncoder),
    }
    return render(request, 'timetable/timetable.html', data)


@student_required
def my_prototype(request):
    """Renders the prototype with enrolled, enqueued, and pinned groups."""
    student = request.user.student
    semester = Semester.objects.get_next()

    # This costs an additional join, but works if there is no current semester.
    records = Record.objects.filter(
        student=student, group__course__semester=semester
    ).exclude(status=RecordStatus.REMOVED).select_related(
        'group__teacher', 'group__teacher__user', 'group__course', 'group__course__semester',
        'group__course__entity'
    ).prefetch_related('group__term', 'group__term__classrooms')
    pinned = Pin.student_pins_in_semester(student, semester)
    pinned = list(pinned)
    all_groups_by_id = {r.group_id: r.group for r in records}
    all_groups_by_id.update({p.pk: p for p in pinned})
    all_groups = list(all_groups_by_id.values())
    can_enqueue_dict = Record.can_enqueue_groups(student, all_groups)
    can_dequeue_dict = Record.can_dequeue_groups(student, all_groups)

    for record in records:
        group = all_groups_by_id.get(record.group_id)
        group.is_enrolled = record.status == RecordStatus.ENROLLED
        group.is_enqueued = record.status == RecordStatus.QUEUED

    for pin in pinned:
        group = all_groups_by_id.get(pin.pk)
        group.is_pinned = True

    all_groups = all_groups_by_id.values()
    for group in all_groups:
        group.can_enqueue = can_enqueue_dict.get(group.pk)
        group.can_dequeue = can_dequeue_dict.get(group.pk)

    group_dicts = build_group_list(all_groups)

    courses_json = list_courses_in_semester(semester)
    data = {
        'groups_json': json.dumps(group_dicts, cls=DjangoJSONEncoder),
        'courses_json': courses_json,
    }
    return render(request, 'timetable/prototype.html', data)


@student_required
@require_POST
def prototype_action(request, group_id):
    """Performs actions requested by timetable prototype.

    HTTP response 204 (successful with no content to send back) will be returned
    if the pin operation is performed with no obstacles. If the student is not
    allowed to perform an operation, 403 (forbidden) status shall be returned.
    """
    student = request.user.student
    group: Group
    try:
        group = Group.objects.get(pk=group_id)
    except Group.DoesNotExist:
        raise Http404
    # Axios sends POST data in json rather than _Form-Encoded_.
    data = json.loads(request.body.decode('utf-8'))
    action = data.get('action')
    if action == 'pin':
        Pin.objects.get_or_create(student_id=student.pk, group_id=group_id)
        return HttpResponse(status=204)
    if action == 'unpin':
        Pin.objects.filter(student_id=student.pk, group_id=group_id).delete()
        return HttpResponse(status=204)
    if action == 'enqueue':
        group_ids = Record.enqueue_student(student, group)
        if group_ids:
            # When the student joins the queue of a class, the accompanying
            # lecture group might need to be displayed (if he is automatically
            # enqueued in that). We hence send him the information about these
            # groups.
            groups = Group.objects.filter(pk__in=group_ids).select_related(
                'teacher', 'teacher__user', 'course', 'course__semester', 'course__entity'
            ).prefetch_related('term', 'term__classrooms')
            for group in groups:
                group.is_enqueued = True
            groups_dicts = build_group_list(groups)
            return JsonResponse(groups_dicts, safe=False)
        else:
            return HttpResponse(status=403)
    if action == 'dequeue':
        group_ids = Record.remove_from_group(student, group)
        if group_ids:
            return JsonResponse(group_ids, safe=False)
        else:
            return HttpResponse(status=403)
    # If the request action is not among the above, we return Bad Request
    # response.
    return HttpResponse(status=400, content=action)


@student_required
def prototype_get_course(request, course_id):
    """Retrieves the annotated groups of a single course."""
    student = request.user.student
    course = Course.objects.get(pk=course_id)
    groups = course.groups.all().select_related(
        'course', 'course__entity', 'teacher', 'course__semester', 'teacher__user'
    ).prefetch_related('term', 'term__classrooms')
    can_enqueue_dict = Record.can_enqueue_groups(student, groups)
    can_dequeue_dict = Record.can_dequeue_groups(student, groups)
    for group in groups:
        group.can_enqueue = can_enqueue_dict.get(group.pk)
        group.can_dequeue = can_dequeue_dict.get(group.pk)
    group_dicts = build_group_list(groups)
    return JsonResponse(group_dicts, safe=False)
