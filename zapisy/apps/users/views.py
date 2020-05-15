import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import Http404, redirect, render, reverse
from django.views.decorators.http import require_POST

from apps.enrollment.courses.models import Group, Semester
from apps.enrollment.records.models import GroupOpeningTimes, Record, RecordStatus, T0Times
from apps.enrollment.timetable.views import build_group_list
from apps.grade.ticket_create.models.student_graded import StudentGraded
from apps.notifications.views import create_form
from apps.users.decorators import employee_required, external_contractor_forbidden

from .forms import EmailChangeForm, EmployeeDataForm
from .models import Employee, PersonalDataConsent, Student

logger = logging.getLogger()


@login_required
@external_contractor_forbidden
def students_view(request, user_id: int = None):
    """View for students list and student profile if user id in URL is provided."""
    students_queryset = Student.get_active_students().select_related('user')
    if not request.user.employee:
        students_queryset = students_queryset.filter(consent__granted=True)
    students = {
        s.pk: {
            'last_name': s.user.last_name,
            'first_name': s.user.first_name,
            'id': s.user.id,
            'album': s.matricula,
            'email': s.user.email
        }
        for s in students_queryset
    }
    data = {
        'students': students,
        'user_link': reverse('students-list'),
    }

    if user_id is not None:
        try:
            student: Student = Student.objects.select_related('user', 'consent').get(user_id=user_id)
        except Student.DoesNotExist:
            raise Http404

        # We will not show the student profile if he decides to hide it.
        if not request.user.employee and not student.consent_granted():
            messages.warning(request, "Student ukrył swój profil")
            return redirect('students-list')

        semester = Semester.objects.get_next()

        records = Record.objects.filter(
            student=student,
            group__course__semester=semester, status=RecordStatus.ENROLLED).select_related(
            'group__teacher', 'group__teacher__user', 'group__course').prefetch_related(
            'group__term', 'group__term__classrooms')
        groups = [r.group for r in records]

        # Highlight groups shared with the viewer in green.
        viewer_groups = Record.common_groups(request.user, groups)
        for g in groups:
            g.is_enrolled = g.pk in viewer_groups

        group_dicts = build_group_list(groups)

        data.update({
            'student': student,
            'groups_json': json.dumps(group_dicts, cls=DjangoJSONEncoder),
        })
    return render(request, 'users/users_view.html', data)


def employees_view(request, user_id: int = None):
    """View for employees list and employee profile if user id in URL is provided."""
    employees_queryset = Employee.get_actives().select_related('user')
    employees = {
        e.pk: {
            'last_name': e.user.last_name,
            'first_name': e.user.first_name,
            'id': e.user.id,
            'email': e.user.email,
        }
        for e in employees_queryset
    }
    data = {
        'employees': employees_queryset,
        'employees_dict': employees,
        'user_link': reverse('employees-list'),
    }

    if user_id is not None:
        try:
            employee = Employee.objects.select_related('user').get(user_id=user_id)
        except Employee.DoesNotExist:
            raise Http404

        semester = Semester.objects.get_next()
        groups = Group.objects.filter(
            course__semester_id=semester.pk, teacher=employee).select_related(
            'teacher', 'teacher__user', 'course').prefetch_related('term', 'term__classrooms')
        groups = list(groups)

        # Highlight groups shared with the viewer in green.
        viewer_groups = Record.common_groups(request.user, groups)
        for g in groups:
            g.is_enrolled = g.pk in viewer_groups

        group_dicts = build_group_list(groups)

        data.update({
            'employee': employee,
            'groups_json': json.dumps(group_dicts, cls=DjangoJSONEncoder),
        })
    return render(request, 'users/users_view.html', data)


@login_required
def email_change(request):
    """Allows users to change email address."""
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            logger.info(f"{request.user} changed email to {form.cleaned_data['email']}")
            messages.success(request, message="Twój adres e-mail został zmieniony.")
            return redirect('my-profile')
    else:
        form = EmailChangeForm(instance=request.user)
    return render(request, 'users/form.html', {'form': form})


@employee_required
def employee_data_change(request):
    employee = request.user.employee
    if request.method == 'POST':
        form = EmployeeDataForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Twoje dane zostały zmienione.")
            return redirect('my-profile')
    else:
        form = EmployeeDataForm(instance=employee)
    return render(request, 'users/form.html', {'form': form})


@login_required
def my_profile(request):
    """User profile page.

    The profile page displays user settings (e-mail address, notifications). If
    he is a student, his opening times will be displayed. If the user is an
    employee, the page allows him to modify his public information (office,
    consultations).
    """
    semester = Semester.objects.get_next()

    data = {
        'semester': semester,
    }

    if request.user.employee:
        data.update({
            'consultations': request.user.employee.consultations,
            'room': request.user.employee.room,
            'homepage': request.user.employee.homepage,
            'title': request.user.employee.title,
        })

    if semester and request.user.student:
        student: Student = request.user.student
        groups_opening_times = GroupOpeningTimes.objects.filter(
            student_id=student.pk, group__course__semester_id=semester.pk).select_related(
            'group', 'group__course', 'group__teacher',
            'group__teacher__user').prefetch_related('group__term', 'group__term__classrooms')
        groups_times = []
        got: GroupOpeningTimes
        for got in groups_opening_times:
            group: Group = got.group
            group.opening_time = got.time
            groups_times.append(group)
        t0_time_obj = T0Times.objects.filter(student_id=student.pk, semester_id=semester.pk)
        try:
            t0_time = t0_time_obj.get().time
        except T0Times.DoesNotExist:
            t0_time = None
        grade_info = StudentGraded.objects.filter(
            student=student).select_related('semester').order_by('-semester__records_opening')
        semesters_participated_in_grade = [x.semester for x in grade_info]
        current_semester_ects = Record.student_points_in_semester(student, semester)
        data.update({
            't0_time': t0_time,
            'groups_times': groups_times,
            'semesters_participated_in_grade': semesters_participated_in_grade,
            'current_semester_ects': current_semester_ects,
        })

    notifications_form = create_form(request)
    data.update({
        'form': notifications_form,
    })

    return render(request, 'users/my_profile.html', data)


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
    return redirect(request.META.get('HTTP_REFERER'))
