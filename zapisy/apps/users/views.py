# -*- coding: utf-8 -*-

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_POST
from django.contrib.auth.views import login
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.http import QueryDict, HttpResponse
from django.template.response import TemplateResponse
from django.utils import simplejson
from django.utils.translation import check_for_language
from django.db.models import Q

from django.conf import settings
from apps.grade.ticket_create.models.student_graded import StudentGraded
from apps.offer.vote.models.single_vote import SingleVote

from apps.users.exceptions import NonUserException, NonEmployeeException,\
                                 NonStudentException
from apps.enrollment.courses.exceptions import MoreThanOneCurrentSemesterException
from apps.users.utils import prepare_ajax_students_list,\
                             prepare_ajax_employee_list

from apps.users.models import Employee, Student, BaseUser
from apps.enrollment.courses.models import Semester, Group
from apps.enrollment.records.models import Record
from apps.enrollment.utils import mailto

from apps.users.forms import EmailChangeForm, BankAccountChangeForm, ConsultationsChangeForm, EmailToAllStudentsForm

from apps.enrollment.records.utils import *

from datetime import timedelta
from libs.ajax_messages import AjaxFailureMessage, AjaxSuccessMessage
import datetime
from mailer.models import Message

import logging

from django.core.cache import cache as mcache
from apps.notifications.forms import NotificationFormset
from apps.notifications.models import NotificationPreferences
logger = logging.getLogger()
import vobject


GTC = {'1' : 'wy', '2': 'cw', '3': 'pr',
        '4': 'cw', '5': 'cw+prac',
        '6': 'sem', '7': 'lek', '8': 'WF',
        '9': 'rep', '10': 'proj'}


@login_required
def student_profile(request, user_id):
    """student profile"""
    try:
        student = Student.objects.select_related('user').get(user=user_id)
        courses = prepare_schedule_courses(request, for_student=student)
        votes   = SingleVote.get_votes(student)
        data = prepare_schedule_data(request, courses)
        data.update({
            'courses': courses,
            'student': student,
            'votes': votes
        })

        if request.is_ajax():
            return render_to_response('users/student_profile_contents.html', data, context_instance=RequestContext(request))
        else:
            begin = student.user.last_name[0]
            students = Student.get_list(begin)
            students = Record.recorded_students(students)
            data['students'] = students
            data['char']     = begin
            return render_to_response('users/student_profile.html', data, context_instance=RequestContext(request))

    except Student.DoesNotExist:
        logger.error('Function student_profile(id = %d) throws NonStudentException while acessing to non existing student.' % int(user_id) )
        messages.error(request, "Nie ma takiego studenta.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except User.DoesNotExist:
        logger.error('Function student_profile(id = %d) throws User.DoesNotExist while acessing to non existing user.' % int(user_id) )
        messages.error(request, "Nie ma takiego użytkownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

def employee_profile(request, user_id):
    """employee profile"""
    try:
        user = User.objects.select_related('employee').get(id=user_id)
        employee = user.employee

        if not employee:
            raise Employee.DoesNotExist

    except Employee.DoesNotExist:
        logger.error('Function employee_profile(user_id = %s) throws NonEmployeeException while acessing to non existing employee.' % str(user_id) )
        messages.error(request, "Nie ma takiego pracownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except User.DoesNotExist:
        logger.error('Function employee_profile(id = %s) throws User.DoesNotExist while acessing to non existing user.' % str(user_id) )
        messages.error(request, "Nie ma takiego użytkownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

    try:
        courses = prepare_schedule_courses(request, for_employee=employee)
        data = prepare_schedule_data(request, courses)
        data.update({
            'courses': courses,
            'employee': employee
        })

        if request.is_ajax():
            return render_to_response('users/employee_profile_contents.html',
                data, context_instance=RequestContext(request))
        else:
            begin = user.last_name[0] if user.last_name else 'All'
            employees = Employee.get_list(begin)
            semester = Semester.get_current_semester()
            employees = Group.teacher_in_present(employees, semester)

            for e in employees:
                e.short_new = e.user.first_name[:1] + e.user.last_name[:2] if e.user.first_name and e.user.last_name else None
                e.short_old = e.user.first_name[:2] + e.user.last_name[:2] if e.user.first_name and e.user.last_name else None

            data['employees'] = employees
            data['char'] = begin

            return render_to_response('users/employee_profile.html', data, context_instance=RequestContext(request))


    except MoreThanOneCurrentSemesterException:
        data = {'employee' : employee}
        logger.error('Function employee_profile throws MoreThanOneCurrentSemesterException.' )
        messages.error(request, "Przepraszamy, system jest obecnie nieaktywny z powodu niewłaściwej konfiguracji semestrów. Prosimy spróbować później.")
        return render_to_response('users/employee_profile.html', data, context_instance=RequestContext(request))

@login_required
def set_language(request):
    """
    Redirect to a given url while setting the chosen language in the
    session or cookie. The url and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    if request.method == 'POST':
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            account = UserProfile.objects.get(user=request.user)
            account.preferred_language = lang_code
            account.save()
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


@login_required
def email_change(request):
    """function that enables mail changing"""
    if request.POST:
        data = request.POST.copy()
        form = EmailChangeForm(data, instance=request.user)
        if form.is_valid():
            email = form.cleaned_data['email']

            user = User.objects.filter(email=email)

            if user and user <> request.user:
                messages.error(request, "Podany adres jest już przypisany do innego użytkownika!")
                return render_to_response('users/email_change_form.html', {'form':form}, context_instance=RequestContext(request))

            form.save()
            logger.info('User (%s) changed email' % request.user.get_full_name())
            messages.success(request, message="Twój adres e-mail został zmieniony.")
            return HttpResponseRedirect(reverse('my-profile'))
    else:
        form = EmailChangeForm({'email' : request.user.email})
    return render_to_response('users/email_change_form.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def bank_account_change(request):
    """function that enables bank account changing"""
    if request.POST:
        data = request.POST.copy()
        zamawiany = Student.get_zamawiany(request.user.id)
        form = BankAccountChangeForm(data, instance=zamawiany)
        if form.is_valid():
            form.save()
            logger.info('User (%s) changed bank account' % request.user.get_full_name())
            messages.success(request, "Twój numer konta bankowego został zmieniony.")
            return HttpResponseRedirect(reverse('my-profile'))
    else:
        zamawiany = Student.get_zamawiany(request.user.id)
        form = BankAccountChangeForm({'bank_account': zamawiany.bank_account})
    return render_to_response('users/bank_account_change_form.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def consultations_change(request):
    """function that enables consultations changing"""
    try:
        employee = request.user.employee
        if request.POST:
            data = request.POST.copy()
            form = ConsultationsChangeForm(data, instance=employee)
            if form.is_valid():
                form.save()
                logger.info('User (%s) changed consultations' % request.user.get_full_name())
                messages.success(request, "Twoje dane zostały zmienione.")
                return HttpResponseRedirect(reverse('my-profile'))
        else:
            form = ConsultationsChangeForm({'consultations': employee.consultations, 'homepage': employee.homepage, 'room': employee.room})
        return render_to_response('users/consultations_change_form.html', {'form':form}, context_instance=RequestContext(request))
    except Employee.DoesNotExist:
        messages.error(request, 'Nie jesteś pracownikiem.')
        return render_to_response('common/error.html',
                context_instance=RequestContext(request))

@login_required
def password_change_done(request):
    """informs if password were changed"""
    logger.info('User (%s) changed password' % request.user.get_full_name())
    messages.success(request, "Twoje hasło zostało zmienione.")
    return HttpResponseRedirect(reverse('my-profile'))

@login_required
def my_profile(request):
    """profile site"""
    semester = Semester.objects.get_next()
    zamawiany = Student.get_zamawiany(request.user.id)
    comments = zamawiany and zamawiany.comments or ''
    points = zamawiany and zamawiany.points or 0

    notifications = NotificationFormset(queryset=NotificationPreferences.objects.create_and_get(request.user))

    if hasattr(request.user, 'employee') and request.user.employee:
        consultations = request.user.employee.consultations
        room = request.user.employee.room
        homepage = request.user.employee.homepage
        room = room and room or ''
        homepage = homepage and homepage or ''
    else:
        consultations = ''
        homepage = ''
        room = ''

    grade = {}

    if semester and Student.does_exist_for_user(request.user):

        try:
            student = Student.get_for_user(request.user)
            courses = OpeningTimesView.objects.get_courses(student, semester)
            grade = [x.semester for x in StudentGraded.objects.filter(student=student).select_related('semester')]

        except (KeyError, Student.DoesNotExist):
            grade = {}
            courses = None


    else:
        grade = None
        courses = None

    return TemplateResponse(request, 'users/my_profile.html', locals())

def employees_list(request, begin = 'All', query=None):

    employees = Employee.get_list(begin)

    if request.is_ajax():
        employees = prepare_ajax_employee_list(employees)
        return AjaxSuccessMessage(message="ok", data=employees)
    else:
        data = {
            "employees" : employees,
            "char": begin,
            "query": query
            }

    return render_to_response('users/employees_list.html', data, context_instance=RequestContext(request))

def consultations_list(request, begin='A'):

    employees = Employee.get_list('All')
    semester = Semester.get_current_semester()
    employees = Group.teacher_in_present(employees, semester)

    if request.is_ajax():
        employees = prepare_ajax_employee_list(employees)
        return AjaxSuccessMessage(message="ok", data=employees)
    else:
        data = {
            "employees" : employees,
            "char": begin
            }
        return render_to_response('users/consultations_list.html', data, context_instance=RequestContext(request))


@login_required
def students_list(request, begin = 'All', query=None):
    students = Student.get_list(begin)
#    students = Record.recorded_students(students)

    if request.is_ajax():
        students = prepare_ajax_students_list(students)
        return AjaxSuccessMessage(message="ok", data=students)
    else:
        data = {
            "students" : students,
            "char": begin,
            "query": query,
            'mailto_group': mailto(request.user, students),
            'mailto_group_bcc': mailto(request.user, students, True)
        }
        return render_to_response('users/students_list.html', data, context_instance=RequestContext(request))

@login_required
def logout(request):
    """logout"""
    logger.info('User %s <id: %s> is logged out ' % (request.user.username, request.user.id))
    auth.logout(request)
    return HttpResponseRedirect('/')

def login_plus_remember_me(request, *args, **kwargs):
    """ funkcja logowania uzględniająca zapamiętanie sesji na życzenie użytkownika"""

    if 'polls' in request.session:
        del request.session['polls']

    if 'finished' in request.session:
        del request.session['finished']

    if request.method == 'POST':
        if request.POST.get('remember_me', None):
            request.session.set_expiry(datetime.timedelta(14))
        else:
            request.session.set_expiry(0) # on browser close
    return login(request, *args, **kwargs)

@login_required
def create_ical_file(request):
    user = request.user
    user_full_name = user.get_full_name()
    semester = Semester.get_default_semester()

    cal = vobject.iCalendar()
    cal.add('x-wr-timezone').value = 'Europe/Warsaw'
    cal.add('version').value = '2.0'
    cal.add('prodid').value = 'Fereol'
    cal.add('calscale').value = 'GREGORIAN'
    cal.add('calname').value = user_full_name + ' - schedule'
    cal.add('method').value = 'PUBLISH'

    groups_employee = []
    groups_student = []
    try:
        groups_student = filter(lambda x: x.course.semester==semester, Record.get_groups_for_student(user))
    except Student.DoesNotExist:
        pass
    try:
        groups_employee = map(lambda x: x, Group.objects.filter(course__semester = semester, teacher = user.employee))
    except Employee.DoesNotExist:
        pass
    groups = groups_employee + groups_student
    for group in groups:
        course_name = group.course.name
        group_type = group.human_readable_type().decode('utf-8').lower()
        try:
            terms = group.get_all_terms_for_export()
        except IndexError:
            continue
        for term in terms:
            start_time = term.start
            end_time = term.end
            date = term.day
            dt = datetime.datetime.combine(date, datetime.time(0, 0))
            start_datetime = dt + start_time
            end_datetime = dt + end_time

            event = cal.add('vevent')
            event.add('summary').value = '%s - %s' % (course_name, group_type)
            if term.room:
                event.add('location').value = 'sala '+term.room.number \
                    + u', Instytut Informatyki Uniwersytetu Wrocławskiego'

            event.add('description').value = u'prowadzący: ' \
                + group.get_teacher_full_name()
            event.add('dtstart').value = start_datetime
            event.add('dtend').value = end_datetime

    cal_str = cal.serialize()
    response = HttpResponse(cal_str, content_type='application/calendar')
    response['Content-Disposition'] = 'attachment; filename=schedule.ical'
    return response


@permission_required('users.mailto_all_students')
def email_students(request):
    """function that enables mailing all students"""
    students = Student.get_list('All')
    if students:
        studentsmails = ','.join([student.user.email for student in students])

    if request.POST:
        data = request.POST.copy()
        form = EmailToAllStudentsForm(data)
        form.fields['sender'].widget.attrs['readonly'] = True
        if form.is_valid():
            counter = 0
            body = form.cleaned_data['message']
            subject = form.cleaned_data['subject']
            for student in students:
                address = student.user.email
                if address:
                    counter += 1
                    Message.objects.create(to_address=address, from_address=form.cleaned_data['sender'], subject=subject, message_body=body)
            if form.cleaned_data['cc_myself'] == True:
                Message.objects.create(to_address=request.user.email, from_address=form.cleaned_data['sender'], subject=subject, message_body=body)
            messages.success(request, u'Wysłano wiadomość do %d studentów' % counter)
            return HttpResponseRedirect(reverse('my-profile'))
        else:
            messages.error(request, u'Wystąpił błąd przy wysyłaniu wiadomości')
    else:
        form = EmailToAllStudentsForm(initial={'sender': 'zapisy@cs.uni.wroc.pl'})
        form.fields['sender'].widget.attrs['readonly'] = True
    return render_to_response('users/email_students.html', {'form':form, 'students_mails': studentsmails}, context_instance=RequestContext(request))
