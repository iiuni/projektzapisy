# -*- coding: utf-8 -*-
import datetime
import json

from traceback import format_tb
from sys import exc_info, path
import codecs
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction, connection
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from tempfile import NamedTemporaryFile
from django.template.response import TemplateResponse
from apps.enrollment.courses.models import Course, Semester, Group, Classroom
from apps.enrollment.courses.models.term import Term
from apps.enrollment.records.models import Record
from apps.enrollment.records.utils import run_rearanged
from apps.users.models import Employee, Student
from .importschedule import import_semester_schedule
from apps.enrollment.courses.forms import Parser
import os

FEREOL_PATH = os.getcwd()
path.append(FEREOL_PATH + '/dbimport/schedule')

@staff_member_required
@transaction.atomic
def add_student(request):
    try:
        group_id = int(request.POST.get('group_id', -1))
        student_id = int(request.POST.get('student', -1))
    except (UnicodeEncodeError, ValueError):
        raise Http404

    if group_id < 0 or student_id < 0:
        raise Http404

    try:
        course = Course.objects.select_for_update().filter(groups=group_id)
        group = Group.objects.get(id=group_id)
        student = Student.objects.get(id=student_id)
    except ObjectDoesNotExist:
        raise Http404

    result, __ = group.add_student(student)
    if result:
        run_rearanged(result, group)

    url = reverse('admin:{}_{}_change'.format(group._meta.app_label, group._meta.model_name), args=[group.id])
    return HttpResponseRedirect(url)


@staff_member_required
@transaction.atomic
def remove_student(request):
    try:
        group_id = int(request.POST.get('group_id', -1))
        record_id = int(request.POST.get('recordid', -1))
    except (UnicodeEncodeError, ValueError):
        raise Http404

    if group_id < 0 or record_id < 0:
        raise Http404

    try:
        course = Course.objects.select_for_update().filter(groups=group_id)
        group = Group.objects.get(id=group_id)
        student = Record.objects.get(id=record_id).student
    except ObjectDoesNotExist:
        raise Http404

    result, messages_list = group.remove_student(student, is_admin=True)
    if result:
        run_rearanged(result, group)

    url = reverse('admin:{}_{}_change'.format(group._meta.app_label, group._meta.model_name), args=[group.id])
    return HttpResponseRedirect(url)

@staff_member_required
@transaction.atomic
def change_group_limit(request):
    try:
        group_id = int(request.POST.get('group_id', -1))
        limit = int(request.POST.get('limit', -1))
    except (UnicodeEncodeError, ValueError):
        raise Http404

    if group_id < 0 or limit < 0:
        raise Http404

    try:
        course = Course.objects.select_for_update().filter(groups=group_id)
        group = Group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        raise Http404

    if limit < group.limit:
        group.limit = limit
        group.save()
    else:
        while group.limit < limit:
            group.limit += 1
            group.save()
            run_rearanged(None, group)

    url = reverse('admin:{}_{}_change'.format(group._meta.app_label, group._meta.model_name), args=[group.id])
    return HttpResponseRedirect(url)



class SemesterImportForm(forms.Form):
    file = forms.FileField(max_length=255, label='Plik XML')

@staff_member_required
def import_semester(request):
    if request.method == 'POST':
        form = SemesterImportForm(request.POST, request.FILES)

        if form.is_valid():
            xmlfile = NamedTemporaryFile();

            for chunk in request.FILES['file'].chunks():
                xmlfile.write(chunk)

            xmlfile.seek(0)

            try:
                import_semester_schedule(xmlfile)
            except Exception:
                errormsg = str(exc_info()[0]) + ' ' + str(exc_info()[1]) + '\n\n'
                errormsg += 'Traceback:\n'
                errormsg += ''.join([str for str in format_tb(exc_info()[2])])
                messages.error(request, "Błąd!")
            else:
                errormsg = None
                messages.success(request, "Plik został zaimportowany.")
            finally:
                xmlfile.close()

            return render_to_response(
                'enrollment/courses/admin/import_semester.html',
                {'form': form,
                'errormsg': errormsg,
                },
                RequestContext(request, {}),
            )
    else:
        form = SemesterImportForm()

    return render_to_response(
        'enrollment/courses/admin/import_semester.html',
        {'form': form,
        },
        RequestContext(request, {}),
    )



class ScheduleImportForm(forms.Form):
    file = forms.FileField(max_length=255, label='Plik z planem zajęć')

@staff_member_required
def import_schedule(request):
    form = ScheduleImportForm(request.POST or None, request.FILES or None)

    if form.is_valid():

        result = Parser(request.FILES['file']).get_result()
        semester = Semester.objects.get_next()
        to_print = []
        for item in result:
            try:
                item['course'] = Course.objects.get(entity__name__iexact=item['name'], semester=semester).id
            except ObjectDoesNotExist:
                item['course'] = ''

            to_print.append(json.dumps(item))


        return TemplateResponse(request, 'enrollment/courses/admin/import_schedule_step2.html', locals())

    return TemplateResponse(request, 'enrollment/courses/admin/import_schedule.html', locals())

@staff_member_required
def refresh_semester(request):
    semester = Semester.objects.get_next()
    cursor = connection.cursor()
    cursor.execute("SELECT users_openingtimesview_refresh_for_semester(%s);" % str(semester.id))
    connection.commit()
    return HttpResponseRedirect('/fereol_admin/courses')

@staff_member_required
def finish_import_schedule(request):
    courses = request.POST.getlist('courses')
    semester = Semester.objects.get_next()
    for course in courses:
        obj = json.loads(course)
        c = Course.objects.get(id=obj['course'])

        for g in obj['groups']:
            gr = Group()
            gr.course = c
            if g['teacher'] != '':
                gr.teacher_id = Employee.objects.get(user__id=g['teacher']).id
            gr.type = g['type']
            gr.limit = 0
            gr.save()

            t = Term()
            t.dayOfWeek = g['day']
            t.start_time = datetime.time(int(g['start']), 0)
            t.end_time = datetime.time(int(g['end']), 0)
            t.group = gr
            t.save()

            for r in g['rooms']:
                try:
                    t.classrooms.add( Classroom.objects.get(number=r) )
                except:
                    pass


    return TemplateResponse(request, 'enrollment/courses/admin/import_schedule.html', locals())
