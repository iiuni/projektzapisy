import datetime
import json

from traceback import format_tb
from sys import exc_info, path
import codecs
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.db import transaction, connection
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from tempfile import NamedTemporaryFile
from django.template.response import TemplateResponse
from apps.enrollment.courses.models.course import Course
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.term import Term
from apps.enrollment.records.models import T0Times, GroupOpeningTimes
from apps.users.models import Employee, Student
from apps.enrollment.courses.forms import Parser
import os

FEREOL_PATH = os.getcwd()
path.append(FEREOL_PATH + '/dbimport/schedule')


class SemesterImportForm(forms.Form):
    file = forms.FileField(max_length=255, label='Plik XML')


@staff_member_required
def import_semester(request):
    return HttpResponse('Not implemented', status=501)


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
                item['course'] = Course.objects.get(
                    entity__name__iexact=item['name'], semester=semester).id
            except ObjectDoesNotExist:
                item['course'] = ''

            to_print.append(json.dumps(item))

        return TemplateResponse(
            request,
            'enrollment/courses/admin/import_schedule_step2.html',
            locals())

    return TemplateResponse(request, 'enrollment/courses/admin/import_schedule.html', locals())


@staff_member_required
def refresh_semester(request):
    """Computes Opening times for all students."""
    semester = Semester.objects.get_next()
    T0Times.populate_t0(semester)
    GroupOpeningTimes.populate_opening_times(semester)
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
                    t.classrooms.add(Classroom.objects.get(number=r))
                except BaseException:
                    pass

    return TemplateResponse(request, 'enrollment/courses/admin/import_schedule.html', locals())
