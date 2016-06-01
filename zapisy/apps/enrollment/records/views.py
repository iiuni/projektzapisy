# -*- coding: utf-8 -*-
import StringIO
import csv
import re

from django.conf import settings


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.utils import simplejson
from django.views.decorators.http import require_POST
from django.utils.datastructures import MultiValueDictKeyError
from django.db import transaction
from django.core.cache import cache as mcache
from xhtml2pdf import pisa
from apps.enrollment.courses.utils import prepare_group_data
from apps.users.decorators import employee_required

from apps.enrollment.courses.models import *
from apps.users.models import *
from apps.enrollment.records.models import *
from apps.enrollment.records.exceptions import *
from apps.enrollment.courses.views import prepare_courses_list_to_render
from apps.enrollment.records.utils import *

from libs.ajax_messages import *


@require_POST
@transaction.commit_on_success
def prototype_set_pinned(request):
    """
        Response for AJAX query for pinning or un-pinning group from student's
        schedule.
    """
    if not request.user.is_authenticated():
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
@transaction.commit_on_success
def set_enrolled(request, method):
    """
        Set student assigned (or not) to group.
    """
    from django.db.models.query import QuerySet
    is_ajax = (method == '.json')
    message_context = None if is_ajax else request

    if not request.user.is_authenticated():
        return AjaxFailureMessage.auto_render('NotAuthenticated', 'Nie jesteś zalogowany.', message_context)

    try:
        group_id = int(request.POST['group'])
        set_enrolled = request.POST['enroll'] == 'true'
    except MultiValueDictKeyError:
        return AjaxFailureMessage.auto_render('InvalidRequest', 'Nieprawidłowe zapytanie.', message_context)

    if request.user.student.block:
        return AjaxFailureMessage.auto_render('ScheduleLocked',
            u'Twój plan jest zablokowany. Możesz go doblokować w prototypie', message_context)
    student = request.user.student


    try:
        group = Group.objects.get(id=group_id)
        course = Course.simple.select_for_update().get(id=group.course_id)
        group = Group.objects.select_for_update().get(id=group_id)
        group.course = course
    except ObjectDoesNotExist:
        transaction.rollback()
        return AjaxFailureMessage.auto_render('NonGroup',
            'Nie możesz zapisać lub wypisać się z grupy, ponieważ ona nie istnieje.', message_context)

    if set_enrolled:
        result, messages_list = group.enroll_student(student)
        if result:
            run_rearanged(result)

    else:
        result, messages_list = group.remove_student(student)
        if result:
            run_rearanged(result, group)

    if not result:
        transaction.rollback()

    if is_ajax:
        message = ', '.join(messages_list)
        return AjaxSuccessMessage(message, prepare_group_data(group.course, student))

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

    if not request.user.is_authenticated():
        return AjaxFailureMessage.auto_render('NotAuthenticated',
            'Nie jesteś zalogowany.', message_context)

    try:
        lock = request.POST['lock'] == 'true'
    except MultiValueDictKeyError:
        return AjaxFailureMessage.auto_render('InvalidRequest',
            'Nieprawidłowe zapytanie.', message_context)

    try:
        logger.info('User %s  <id: %d> %s his/her records' %\
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
@transaction.commit_on_success
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

        queue = Queue.objects.select_related('group').get(student=request.user.student, group__id=group_id, deleted=False)
        #priority = int(priority) WTF? to już jest int
        if priority > settings.QUEUE_PRIORITY_LIMIT or priority < 1:
            return AjaxFailureMessage.auto_render('FatalError',
                'Nieprawidłowa wartość priorytetu.', message_context)
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
            'all_students' : all_students,
            'students_in_group' : students_in_group,
            'students_in_queue' : students_in_queue,
            'group' : group,
        })
        return render_to_response('enrollment/records/records_list.html', data,
            context_instance=RequestContext(request))
    except NonGroupException:
        messages.info(request, "Podana grupa nie istnieje.")
        return render_to_response('common/error.html',
            context_instance=RequestContext(request))

@employee_required
def records_group_csv(request, group_id):
    try:
        students_in_group = Record.get_students_in_group(group_id)
        group = Group.objects.get(id=group_id)

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + re.sub(r'\s', '', slugify(str(group))) + '-group.csv'

        writer = UnicodeWriter(response)
        for s in students_in_group:
            writer.writerow([s.user.first_name, s.user.last_name, s.matricula, s.user.email])

        return response

    except (NonGroupException, ObjectDoesNotExist):
        raise Http404

@employee_required
def records_queue_csv(request, group_id):
    try:
        students_in_queue = Queue.get_students_in_queue(group_id)
        group = Group.objects.get(id=group_id)

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + re.sub(r'\s', '', slugify(str(group))) + '-queue.csv'

        writer = UnicodeWriter(response)
        for s in students_in_queue:
            writer.writerow([s.user.first_name, s.user.last_name, s.matricula, s.user.email])

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
    student  = None
    if request.user.student:
        student = request.user.student
        groups = Course.get_student_courses_in_semester(student, default_semester)
        points, sum_points = student.get_points()


    if student is None and request.user.employee is None:
        messages.info(request, 'Nie jesteś pracownikiem ani studentem.')
        return render_to_response('common/error.html',
            context_instance=RequestContext(request))




    return TemplateResponse(request, 'enrollment/records/schedule.html', locals())


def schedule_prototype(request):
    """ schedule prototype view """

    if hasattr(request.user, 'student') and request.user.student:
        student = request.user.student
        student_id = student.id
    else:
        student = None
        student_id = 'None'

    default_semester = Semester.objects.get_next()
    if not default_semester:
        messages.info(request, 'Brak aktywnego semestru.')
        data = {
            'student_records': [],
            'courses' : [],
            'semester' : 'nieokreślony',
            'types_list' : []
        }
        return render_to_response('enrollment/records/schedule_prototype.html',
            data, context_instance = RequestContext(request))
    if student:
        StudentOptions.preload_cache(student, default_semester)
    cached_courses = mcache.get("schedule_prototype_courses_%s_%s" % (default_semester.id, student_id), 'DoesNotExist')
    if cached_courses == 'DoesNotExist':
        logger.debug("missed cache schedule_prototype_courses_%s_%s" % (default_semester.id, student_id))
        terms = Term.get_all_in_semester(default_semester )
        courses = prepare_courses_with_terms( terms )
        ccourses = []
        for course in courses:
            jsons = []
            for term in course['terms']:
                term.update({ # TODO: do szablonu
                    'json': simplejson.dumps(term['info'])
                })
                jsons.append({'json': simplejson.dumps(term['info'])})
            course['info'].update({
                'is_recording_open': False,
                #TODO: kod w prepare_courses_list_to_render moim zdaniem nie
                #      zadziała
                'was_enrolled': 'False',
	        'english': course['object'].english,
	        'exam': course['object'].exam,
	        'suggested_for_first_year': course['object'].suggested_for_first_year,
            'terms':jsons
            })
            ccourses.append(course['info'])
        cached_courses = ccourses
        mcache.set("schedule_prototype_courses_%s_%s" % (default_semester.id, student_id), cached_courses)
#    else:
#        logger.debug("in cache schedule_prototype_courses_%s_%s" % (default_semester.id, student_id))
                   

    cached_all_groups = mcache.get("schedule_prototype_all_groups_%s" % default_semester.id, 'DoesNotExist')   
    if cached_all_groups == 'DoesNotExist':

#        logger.debug('Cache miss with semester id: %s' % \
#                default_semester.id)
        mcache.delete("schedule_prototype_courses_json_%s" % student_id)
        cached_all_groups = Group.get_groups_by_semester_opt(default_semester)
        mcache.set("schedule_prototype_all_groups_%s" % default_semester.id, cached_all_groups)                
        
    all_groups_json = prepare_groups_json(default_semester, cached_all_groups,
        student=student)

    cached_test = mcache.get("test_cache", "DoesNotExist")

    if cached_test == 'DoesNotExist':
#        logger.debug("test missed")
        mcache.set("test_cache", 2)
#    else:
#        logger.debug("test is in cache")
    cached_courses_json = mcache.get("schedule_prototype_courses_json_%s" % student_id, 'DoesNotExist')
    if cached_courses_json == 'DoesNotExist':
#        logger.debug("miss schedule_prototype_courses_json_%s" % student.id)
        cached_courses_json = prepare_courses_json(cached_all_groups, student) #OK!
        mcache.set("schedule_prototype_courses_json_%s" % student_id, cached_courses_json)
#    else:
#        logger.debug("in cache schedule_prototype_courses_json_%s" % student.id)
        
    data = {
        'courses_json': cached_courses_json,
        'groups_json': all_groups_json,
        'courses' : cached_courses,
        'semester' : default_semester,
        'types_list' : Type.get_all_for_jsfilter(),
        'priority_limit': settings.QUEUE_PRIORITY_LIMIT
    }
    return render_to_response('enrollment/records/schedule_prototype.html',
        data, context_instance = RequestContext(request))

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
    context = Context(data)

    template = get_template('records/group_pdf.html')
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf      = pisa.pisaDocument(StringIO.StringIO(html.encode('UTF-8')), result, encoding='UTF-8')
    response = HttpResponse(result.getvalue(), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + re.sub(r'\s', '', slugify(str(group))) + '-group.pdf'

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
    context = Context(data)

    template = get_template('records/queue_pdf.html')
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf      = pisa.pisaDocument(StringIO.StringIO(html.encode('UTF-8')), result, encoding='UTF-8')
    response = HttpResponse(result.getvalue(), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + re.sub(r'\s', '', slugify(str(group))) + '-queue.pdf'

    return response
