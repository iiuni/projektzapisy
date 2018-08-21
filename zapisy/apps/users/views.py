import logging
import datetime
import unidecode
import re
from typing import Any, Optional

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.utils.translation import check_for_language, LANGUAGE_SESSION_KEY
from django.conf import settings

from vobject import iCalendar

from apps.users.utils import prepare_ajax_students_list, prepare_ajax_employee_list
from apps.users.models import Employee, Student, BaseUser, PersonalDataConsent
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.group import Group
from apps.enrollment.records.models import Record
from apps.enrollment.utils import mailto
from apps.users.forms import EmailChangeForm, ConsultationsChangeForm, EmailToAllStudentsForm
from apps.users.exceptions import InvalidUserException
from libs.ajax_messages import AjaxSuccessMessage
from mailer.models import Message

logger = logging.getLogger()

GTC = {'1': 'wy', '2': 'cw', '3': 'pr',
       '4': 'cw', '5': 'cw+prac',
       '6': 'sem', '7': 'lek', '8': 'WF',
       '9': 'rep', '10': 'proj'}
BREAK_DURATION = datetime.timedelta(minutes=15)


@login_required
def student_profile(request: HttpRequest, user_id: int) -> HttpResponse:
    """student profile"""
    pass


def employee_profile(request: HttpRequest, user_id: int) -> HttpResponse:
    """employee profile"""
    pass


@login_required
def set_language(request: HttpRequest) -> HttpResponse:
    """
    Redirect to a given url while setting the chosen language in the
    session or cookie. The url and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    redirect_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    response = HttpResponseRedirect(redirect_url)
    if request.method == 'POST':
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session[LANGUAGE_SESSION_KEY] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


@login_required
def email_change(request: HttpRequest) -> HttpResponse:
    """function that enables mail changing"""
    if request.POST:
        data = request.POST.copy()
        form = EmailChangeForm(data, instance=request.user)
        if form.is_valid():
            email = form.cleaned_data['email']

            user = User.objects.filter(email=email)

            if user and user != request.user:
                messages.error(request, "Podany adres jest już przypisany do innego użytkownika!")
                return render(request, 'users/email_change_form.html', {'form': form})

            form.save()
            logger.info('User (%s) changed email' % request.user.get_full_name())
            messages.success(request, message="Twój adres e-mail został zmieniony.")
            return HttpResponseRedirect(reverse('my-profile'))
    else:
        form = EmailChangeForm({'email': request.user.email})
    return render(request, 'users/email_change_form.html', {'form': form})


@login_required
def consultations_change(request: HttpRequest) -> HttpResponse:
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
            form = ConsultationsChangeForm(
                {'consultations': employee.consultations, 'homepage': employee.homepage, 'room': employee.room})
        return render(request, 'users/consultations_change_form.html', {'form': form})
    except Employee.DoesNotExist:
        messages.error(request, 'Nie jesteś pracownikiem.')
        return render(request, 'common/error.html')


@login_required
def password_change_done(request: HttpRequest) -> HttpResponse:
    """informs if password were changed"""
    logger.info('User (%s) changed password' % request.user.get_full_name())
    messages.success(request, "Twoje hasło zostało zmienione.")
    return HttpResponseRedirect(reverse('my-profile'))


@login_required
def my_profile(request: HttpRequest) -> HttpResponse:
    """profile site"""
    pass


def employees_list(request: HttpRequest, begin: str='All', query: Optional[str]=None) -> HttpResponse:

    employees = Employee.get_list(begin)

    if request.is_ajax():
        employees = prepare_ajax_employee_list(employees)
        return AjaxSuccessMessage(message="ok", data=employees)
    else:
        data = {
            "employees": employees,
            "char": begin,
            "query": query
        }

    return render(request, 'users/employees_list.html', data)


def consultations_list(request: HttpRequest, begin: str='A') -> HttpResponse:

    employees = Employee.get_list('All')
    semester = Semester.get_current_semester()
    employees = Group.teacher_in_present(employees, semester)

    if request.is_ajax():
        employees = prepare_ajax_employee_list(employees)
        return AjaxSuccessMessage(message="ok", data=employees)
    else:
        data = {
            "employees": employees,
            "char": begin
        }
        return render(request, 'users/consultations_list.html', data)


@login_required
def students_list(request: HttpRequest, begin: str='All', query: Optional[str]=None) -> HttpResponse:
    students = Student.get_list(begin, not BaseUser.is_employee(request.user))

    if request.is_ajax():
        students = prepare_ajax_students_list(students)
        return AjaxSuccessMessage(message="ok", data=students)
    else:
        data = {
            "students": students,
            "char": begin,
            "query": query,
            'mailto_group': mailto(request.user, students),
            'mailto_group_bcc': mailto(request.user, students, True)
        }
        return render(request, 'users/students_list.html', data)


@login_required
def logout(request: HttpRequest) -> HttpResponse:
    """logout"""
    logger.info('User %s <id: %s> is logged out ' % (request.user.username, request.user.id))
    auth.logout(request)
    return HttpResponseRedirect('/')


def login_plus_remember_me(request: HttpRequest, **kwargs: Any) -> HttpResponse:
    """
    Sign-in function with an option to save the session.
    If the user clicked the 'Remember me' button (we read it from POST data), the
    session will expire after two weeks.
    """
    if request.user.is_authenticated:
        return redirect("main-page")
    if 'polls' in request.session:
        del request.session['polls']
    if 'finished' in request.session:
        del request.session['finished']

    if request.method == 'POST':
        if request.POST.get('remember_me', None):
            request.session.set_expiry(datetime.timedelta(14).total_seconds())
        else:
            request.session.set_expiry(0)  # Expires on browser closing.
    return LoginView.as_view(**kwargs)(request)


def get_ical_filename(user: User, semester: Semester) -> str:
    name_with_semester = "{}_{}".format(user.get_full_name(), semester.get_short_name())
    name_ascii_only = unidecode.unidecode(name_with_semester)
    path_safe_name = re.sub(r"[\s+/]", "_", name_ascii_only)
    return "fereol_schedule_{}.ical".format(path_safe_name.lower())


@login_required
def create_ical_file(request: HttpRequest) -> HttpResponse:
    user = request.user
    student = user.student
    semester = Semester.get_default_semester()

    cal = iCalendar()
    cal.add('x-wr-timezone').value = 'Europe/Warsaw'
    cal.add('version').value = '2.0'
    cal.add('prodid').value = 'Fereol'
    cal.add('calscale').value = 'GREGORIAN'
    cal.add('calname').value = "{} - schedule".format(user.get_full_name())
    cal.add('method').value = 'PUBLISH'

    if BaseUser.is_student(user):
        records = Record.objects.filter(
            student_id=student.pk, group__course__semester_id=semester.pk
        ).select_related('group', 'group__course', 'group__course__entity')
        groups = [r.group for r in records]
    elif BaseUser.is_employee(user):
        groups = list(Group.objects.filter(course__semester=semester, teacher=user.employee))
    else:
        raise InvalidUserException()
    group: Group
    for group in groups:
        course_name = group.course.name
        group_type = group.human_readable_type().lower()
        try:
            terms = group.get_all_terms_for_export()
        except IndexError:
            continue
        for term in terms:
            start_datetime = datetime.datetime.combine(term.day, term.start)
            start_datetime += BREAK_DURATION
            end_datetime = datetime.datetime.combine(term.day, term.end)
            event = cal.add('vevent')
            event.add('summary').value = "{} - {}".format(course_name, group_type)
            if term.room:
                event.add('location').value = 'sala ' + term.room.number \
                    + ', Instytut Informatyki Uniwersytetu Wrocławskiego'

            event.add('description').value = 'prowadzący: ' \
                + group.get_teacher_full_name()
            event.add('dtstart').value = start_datetime
            event.add('dtend').value = end_datetime

    cal_str = cal.serialize()
    response = HttpResponse(cal_str, content_type='application/calendar')
    ical_file_name = get_ical_filename(user, semester)
    response['Content-Disposition'] = "attachment; filename={}".format(ical_file_name)
    return response


@permission_required('users.mailto_all_students')
def email_students(request: HttpRequest) -> HttpResponse:
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
                    Message.objects.create(
                        to_address=address,
                        from_address=form.cleaned_data['sender'],
                        subject=subject,
                        message_body=body)
            if form.cleaned_data['cc_myself']:
                Message.objects.create(
                    to_address=request.user.email,
                    from_address=form.cleaned_data['sender'],
                    subject=subject,
                    message_body=body)
            messages.success(request, 'Wysłano wiadomość do %d studentów' % counter)
            return HttpResponseRedirect(reverse('my-profile'))
        else:
            messages.error(request, 'Wystąpił błąd przy wysyłaniu wiadomości')
    else:
        form = EmailToAllStudentsForm(initial={'sender': 'zapisy@cs.uni.wroc.pl'})
        form.fields['sender'].widget.attrs['readonly'] = True
    return render(request, 'users/email_students.html',
                  {'form': form, 'students_mails': studentsmails})


@login_required
@require_POST
def personal_data_consent(request):
    if request.POST:
        if 'yes' in request.POST:
            PersonalDataConsent.objects.update_or_create(student=request.user.student,
                                                         defaults={'granted': True})
            messages.success(request, 'Zgoda udzielona')
        if 'no' in request.POST:
            PersonalDataConsent.objects.update_or_create(student=request.user.student,
                                                         defaults={'granted': False})
            messages.success(request, 'Brak zgody zapisany')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
