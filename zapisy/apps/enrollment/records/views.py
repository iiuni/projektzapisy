import csv
import json
import re
import io

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.http import Http404
from django.shortcuts import render
from django.shortcuts import redirect
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from django.utils.datastructures import MultiValueDictKeyError
from django.db import transaction
from django.core.cache import cache as mcache
from xhtml2pdf import pisa

from apps.enrollment.courses.models.course_type import Type
from apps.enrollment.courses.models.effects import Effects
from apps.enrollment.courses.models.student_options import StudentOptions
from apps.enrollment.courses.models.tag import Tag
from apps.enrollment.courses.utils import prepare_group_data
from apps.users.decorators import employee_required

from apps.cache_utils import cache_result
from apps.users.models import *
from apps.enrollment.records.models import *
from apps.enrollment.records.exceptions import *
from apps.enrollment.courses.views import prepare_courses_list_to_render
from apps.enrollment.records.utils import *
from apps.enrollment.utils import mailto

from libs.ajax_messages import *


@require_POST
@transaction.atomic
def prototype_set_pinned(request):
    """
        Response for AJAX query for pinning or un-pinning group from student's
        schedule.
    """
    if not request.user.is_authenticated:
        return AjaxFailureMessage('NotAuthenticated', 'Nie jesteś zalogowany.')

    try:
        group_id = int(request.POST['group'])
        set_pinned = request.POST['pin'] == 'true'
    except MultiValueDictKeyError:
        return AjaxFailureMessage('InvalidRequest', 'Nieprawidłowe zapytanie.')

    try:
        if set_pinned:
            Record.pin_student_to_group(request.user.id, group_id)
            return AjaxSuccessMessage(
                'Grupa została przypięta do Twojego planu.')
        else:
            Record.unpin_student_from_group(request.user.id, group_id)
            return AjaxSuccessMessage('Grupa została odpięta od Twojego planu.')
    except NonStudentException:
        transaction.rollback()
        return AjaxFailureMessage('NonStudent',
                                  'Nie możesz przypinać grup do planu, bo nie jesteś studentem.')
    except NonGroupException:
        transaction.rollback()
        return AjaxFailureMessage('NonGroup',
                                  'Nie możesz przypiąć tej grupy, bo już nie istnieje.')
    except AlreadyPinnedException:
        transaction.rollback()
        return AjaxSuccessMessage(
            'Grupa jest już przypięta do Twojego planu.')
    except AlreadyNotPinnedException:
        transaction.rollback()
        return AjaxSuccessMessage(
            'Grupa jest już odpięta od Twojego planu.')


@require_POST
@transaction.atomic
def set_enrolled(request, method):
    """
        Set student assigned (or not) to group.
    """
    # Used to roll the transaction back if an error occurrs.
    savept = transaction.savepoint()

    from django.db.models.query import QuerySet
    is_ajax = (method == '.json')
    message_context = None if is_ajax else request

    if not request.user.is_authenticated:
        return AjaxFailureMessage.auto_render(
            'NotAuthenticated', 'Nie jesteś zalogowany.', message_context)

    try:
        group_id = int(request.POST['group'])
        set_enrolled = request.POST['enroll'] == 'true'
    except MultiValueDictKeyError:
        return AjaxFailureMessage.auto_render(
            'InvalidRequest', 'Nieprawidłowe zapytanie.', message_context)

    try:
        if request.user.student.block:
            return AjaxFailureMessage.auto_render(
                'ScheduleLocked',
                'Twój plan jest zablokowany. Możesz go odblokować w prototypie',
                message_context)
        student = request.user.student
    except Student.DoesNotExist:
        transaction.savepoint_rollback(savept)
        return AjaxFailureMessage.auto_render('NonStudent',
                                              'Nie jesteś studentem.', message_context)

    try:
        group = Group.objects.get(id=group_id)
        course = Course.simple.select_for_update().get(id=group.course_id)
        group = Group.objects.select_for_update().get(id=group_id)
        group.course = course
    except ObjectDoesNotExist:
        transaction.savepoint_rollback(savept)
        return AjaxFailureMessage.auto_render(
            'NonGroup',
            'Nie możesz zapisać lub wypisać się z grupy, ponieważ ona nie istnieje.',
            message_context)

    if set_enrolled:
        result, messages_list = group.enroll_student(student)
    else:
        result, messages_list = group.remove_student(student)

    if result:
        run_rearanged(result, group)
    else:
        transaction.savepoint_rollback(savept)

    if is_ajax:
        message = ', '.join(messages_list)

        if result:
            return AjaxSuccessMessage(message, prepare_group_data(group.course, student))

        else:
            return AjaxFailureMessage.auto_render('SetEnrolledFailed',
                                                  message, message_context)

    else:
        for message in messages_list:
            messages.info(request, message)

        return redirect('course-page', slug=group.course_slug())


@require_POST
def records_set_locked(request, method):
    """
        Locks or unlocks records for student to prevent mistakes.
    """
    is_ajax = (method == '.json')
    message_context = None if is_ajax else request

    if not request.user.is_authenticated:
        return AjaxFailureMessage.auto_render('NotAuthenticated',
                                              'Nie jesteś zalogowany.', message_context)

    try:
        lock = request.POST['lock'] == 'true'
    except MultiValueDictKeyError:
        return AjaxFailureMessage.auto_render('InvalidRequest',
                                              'Nieprawidłowe zapytanie.', message_context)

    try:
        logger.info('User %s  <id: %d> %s his/her records' %
                    (request.user.username, request.user.id,
                     ('locks' if lock else 'unlocks')))
        request.user.student.records_set_locked(lock)

        message = 'Plan został ' + ('zablokowany.' if lock else ' odblokowany.')
        if is_ajax:
            return AjaxSuccessMessage(message)
        else:
            messages.info(request, message)
            return redirect('schedule-prototype')
    except Student.DoesNotExist:
        transaction.rollback()
        return AjaxFailureMessage.auto_render('NonStudent',
                                              'Nie jesteś studentem.', message_context)


@require_POST
@login_required
@transaction.atomic
def set_queue_priority(request, method):
    """
        Sets new priority for queue of some group
    """
    is_ajax = (method == '.json')
    message_context = None if is_ajax else request

    try:
        group_id = int(request.POST['id'])
        priority = int(request.POST['priority'])
    except MultiValueDictKeyError:
        return AjaxFailureMessage.auto_render('InvalidRequest',
                                              'Nieprawidłowe zapytanie.', message_context)

    try:
        if request.user.student.block:
            return AjaxFailureMessage.auto_render('ScheduleLocked',
                                                  'Twój plan jest zablokowany.', message_context)

        queue = Queue.objects.select_related('group').get(
            student=request.user.student, group__id=group_id, deleted=False)
        # priority = int(priority) WTF? to już jest int
        if priority > settings.QUEUE_PRIORITY_LIMIT or priority < 1:
            return AjaxFailureMessage.auto_render(
                'FatalError', 'Nieprawidłowa wartość priorytetu.', message_context)
        if queue.priority != priority:
            queue.set_priority(priority)
        if is_ajax:
            return AjaxSuccessMessage()
        else:
            return redirect("course-page", slug=queue.group_slug())
    except Queue.DoesNotExist:
        transaction.rollback()
        return AjaxFailureMessage.auto_render('NotQueued',
                                              'Nie jesteś w kolejce do tej grupy.', message_context)
    except Student.DoesNotExist:
        return AjaxFailureMessage.auto_render('NonStudent',
                                              'Nie jesteś studentem.', message_context)


@login_required
def records(request, group_id):
    """
        Group records view - list of all students enrolled and queued to group.
    """
    try:
        group = Group.objects.get(id=group_id)
        students_in_group = Record.get_students_in_group(group_id)
        students_in_queue = Queue.get_students_in_queue(group_id)
        all_students = Student.objects.all()
        data = prepare_courses_list_to_render(request)
        data.update({
            'all_students': all_students,
            'students_in_group': students_in_group,
            'students_in_queue': students_in_queue,
            'group': group,
            'mailto_group': mailto(request.user, students_in_group),
            'mailto_queue': mailto(request.user, students_in_queue),
            'mailto_group_bcc': mailto(request.user, students_in_group, True),
            'mailto_queue_bcc': mailto(request.user, students_in_queue, True),
        })
        return render(request, 'enrollment/records/records_list.html', data)
    except NonGroupException:
        messages.info(request, "Podana grupa nie istnieje.")
        return render(request, 'common/error.html')


@employee_required
def records_group_csv(request, group_id):
    try:
        students_in_group = Record.get_students_in_group(group_id)
        group = Group.objects.get(id=group_id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + \
            re.sub(r'\s', '', slugify(str(group))) + '-group.csv'

        writer = csv.writer(response)
        for s in students_in_group:
            writer.writerow(
                [s.user.first_name, s.user.last_name, s.matricula, s.user.email]
            )

        return response

    except (NonGroupException, ObjectDoesNotExist):
        raise Http404


@employee_required
def records_queue_csv(request, group_id):
    try:
        students_in_queue = Queue.get_students_in_queue(group_id)
        group = Group.objects.get(id=group_id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + \
            re.sub(r'\s', '', slugify(str(group))) + '-queue.csv'

        writer = csv.writer(response)
        for s in students_in_queue:
            writer.writerow(
                [s.user.first_name, s.user.last_name, s.matricula, s.user.email]
            )

        return response

    except (NonGroupException, ObjectDoesNotExist):
        raise Http404


@login_required
def own(request):
    """ own schedule view """

    default_semester = Semester.objects.get_next()
    if not default_semester:
        raise RuntimeError('Brak aktywnego semestru')

    employee = None
    student = None
    if BaseUser.is_student(request.user):
        student = request.user.student
        groups = Course.get_student_courses_in_semester(student, default_semester)
        sum_points = student.get_points()

    if not BaseUser.is_student(request.user) and \
       not BaseUser.is_employee(request.user):
        messages.info(request, 'Nie jesteś pracownikiem ani studentem.')
        return render(request, 'common/error.html')

    return TemplateResponse(request, 'enrollment/records/schedule.html', locals())


@cache_result
def get_schedule_prototype_courselist(student):
    courses = prepare_courses_with_terms()
    return [course.serialize_for_json(
        student=student, terms=terms, includeWasEnrolled=True)
        for course, terms in courses]


@cache_result
def get_schedule_prototype_grouplist(semester):
    return Group.get_groups_by_semester_opt(semester)


def schedule_prototype(request):
    """ schedule prototype view """

    if BaseUser.is_student(request.user):
        student = request.user.student
        student_id = student.id
    else:
        student = None
        student_id = 'None'

    should_allow_leave = Semester.get_default_semester().can_remove_record()

    default_semester = Semester.objects.get_next()
    if not default_semester:
        messages.info(request, 'Brak aktywnego semestru.')
        data = {
            'student_records': [],
            'groups_json': '',
            'semester': 'nieokreślony',
            'effects': '',
            'tags': '',
            'types_list': [],
            'is_leaving_allowed': should_allow_leave,
        }
        return render(request, 'enrollment/records/schedule_prototype.html', data)
    if student:
        StudentOptions.preload_cache(student, default_semester)

    prototype_courses = get_schedule_prototype_courselist(student)
    courses_json = json.dumps(prototype_courses)

    groups = get_schedule_prototype_grouplist(default_semester)
    all_groups_json = prepare_groups_json(
        default_semester, groups, student=student)

    data = {
        # Info needed by the JS prototype code
        'courses_json': courses_json,
        # Needed by the template to generate a list of courses
        'courses': prototype_courses,
        'groups_json': all_groups_json,
        'semester': default_semester,
        'effects': Effects.objects.all(),
        'tags': Tag.objects.all(),
        'types_list': Type.get_all_for_jsfilter(),
        'priority_limit': settings.QUEUE_PRIORITY_LIMIT,
        'allow_leave_course': should_allow_leave,
    }
    return render(request, 'enrollment/records/schedule_prototype.html', data)


@employee_required
def records_group_pdf(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        raise Http404

    data = {
        'group': group,
        'students_in_group': Record.get_students_in_group(group_id),
        'pagesize': 'A4',
        'report': True
    }

    template = get_template('records/group_pdf.html')
    html = template.render(data)
    result = io.BytesIO()

    pisa.pisaDocument(io.StringIO(html), result, encoding='UTF-8')

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + \
        re.sub(r'\s', '', slugify(str(group))) + '-group.pdf'

    return response


@employee_required
def records_queue_pdf(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        raise Http404

    data = {
        'group': group,
        'students_in_queue': Queue.get_students_in_queue(group_id),
        'pagesize': 'A4',
        'report': True
    }

    template = get_template('records/queue_pdf.html')
    html = template.render(data)
    result = io.BytesIO()

    pisa.pisaDocument(io.StringIO(html), result, encoding='UTF-8')
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + \
        re.sub(r'\s', '', slugify(str(group))) + '-queue.pdf'

    return response
