# -*- coding: utf-8 -*-

"""
    Proposal views
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from django.forms.models import inlineformset_factory

from apps.enrollment.courses.models.effects import Effects
from apps.enrollment.courses.models.tag import Tag
from apps.enrollment.courses.models.course import CourseEntity, CourseDescription, Course
from apps.enrollment.courses.models.points import PointsOfCourseEntities, PointTypes
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.course_type import Type

from apps.offer.proposal.forms import ProposalForm, ProposalDescriptionForm, SyllabusForm
from apps.offer.proposal.models import Syllabus, StudentWork
from apps.offer.proposal.exceptions import  NotOwnerException

import json
import logging
from apps.offer.proposal.utils import proposal_for_offer, employee_proposal, send_notification_to_3d
from apps.users.decorators import employee_required
from apps.users.models import Employee

logger = logging.getLogger("")


def offer(request, slug=None):
    """
    if slug is None, this view shows offer main page,
    else show proposal page
    """
    proposal = proposal_for_offer(slug)
    proposals  = CourseEntity.get_proposals(request.user.is_authenticated())
    serialized_proposals = [prop.serialize_for_json()
                            for prop in proposals]
    proposals_json = json.dumps(serialized_proposals)
    types_list = Type.get_all_for_jsfilter()
    teachers   = Employee.get_actives()

    return TemplateResponse(request, 'offer/offer.html', {
        "proposal": proposal,
        "proposals": proposals,
        "proposals_json": proposals_json,
        "types_list": types_list,
        "teachers": teachers,
        "effects": Effects.objects.all(),
        "tags": Tag.objects.all(),
    })

@permission_required('proposal.can_create_offer')
def select_for_voting(request):
    courses = CourseEntity.noremoved.all()
    courses = filter((lambda course: 1 <= course.get_status() <= 3), courses)
    if request.method == 'POST':
        for course in courses:
            ids_for_voting = set(map(int, request.POST.getlist('for_voting')))
            if not course.is_in_voting() and course.id in ids_for_voting:
                course.mark_for_voting()
                course.save()
            elif course.is_in_voting() and course.id not in ids_for_voting:
                course.status = 1
                course.save()
        return redirect('/offer/manage/select_for_voting')
    else:
        return TemplateResponse(request, 'offer/manage/select_for_voting.html', {'courses': courses})

def all_groups(request):
    semester = Semester.get_current_semester()
    courses = Course.objects.filter(semester=semester).all()
    return TemplateResponse(request, 'offer/manage/courses.html', {'courses': courses})

def course_groups(request, slug):
    if request.method == 'GET':
        teachers_by_preference_tutorial = {-1:[], 0:[], 1:[], 2:[], 3: []}
        course = Course.objects.select_related('groups').get(slug=slug)
        teachers = Employee.objects.all()

        for teacher in teachers:
            prefs = teacher.get_preferences().filter(proposal=course.entity).all()
            pref = None
            if len(prefs) > 0:
                pref = prefs[len(prefs)-1].tutorial

            if pref == None:
                teachers_by_preference_tutorial[-1].append(teacher)
            else:
                teachers_by_preference_tutorial[pref].append(teacher)

        teachers_by_preference_tutorial = [
            ('Chętnie', teachers_by_preference_tutorial[3]),
            ('Być może', teachers_by_preference_tutorial[2]),
            ('Raczej nie', teachers_by_preference_tutorial[1]),
            ('Nie', teachers_by_preference_tutorial[0]),
            ('Bez preferencji', teachers_by_preference_tutorial[-1]),
        ]

        groups_with_teachers = []
        for group in course.groups.order_by('id').all():
            if group.type == '2':
                groups_with_teachers.append((group, teachers_by_preference_tutorial))
            else:
                groups_with_teachers.append((group, None))

        return TemplateResponse(request, 'offer/manage/groups.html',
            {'course': course, 'teachers': teachers,
            'groups_with_teachers': groups_with_teachers, 'path': request.path})
    elif request.method == 'POST':
        for group_id, teacher_id in request.POST.iteritems():
            if group_id[:6] != "group_":
                continue
            group_id = group_id[6:]
            group = Group.objects.get(pk=group_id)
            teacher = Employee.objects.get(pk=teacher_id)
            if group.teacher != teacher:
                group.teacher = teacher
                group.save()
        return redirect(request.path)

def main(request):
    return TemplateResponse(request, 'offer/main.html', {} )

@login_required
@employee_required
def proposal(request, slug=None):
    """
      List of user proposal
    """
    try:
        proposals = CourseEntity.get_employee_proposals(request.user)
        for_review = filter((lambda course: course.get_status() == 5), proposals)
        not_accepted = filter((lambda course: course.get_status() == 0), proposals)
        in_offer = filter((lambda course: 1 <= course.get_status() <= 3), proposals)
        removed = filter((lambda course: course.get_status() == 4), proposals)
        proposal  = employee_proposal(request.user, slug)
    except NotOwnerException:
        return redirect('offer-page', slug=slug)
    except Http404:
        raise Http404

    if proposal:
        return TemplateResponse(request, 'offer/proposal/proposal.html', locals())
    else:
        return TemplateResponse(request, 'offer/proposal/employee_proposals.html', locals())

@login_required
@employee_required
def proposal_edit(request, slug=None):
    proposal = None
    description = None
    syllabus = None
    ects_field = None
    ects = 6
    types = Type.objects.all
    pt = PointTypes.objects.get(name='ECTS')

    if slug:
        try:
            proposal = CourseEntity.get_employee_proposal(request.user, slug)
            description = CourseDescription.objects.filter(entity=proposal).order_by('-id')[0]
            syllabus, _ = Syllabus.objects.get_or_create(entity=proposal)
            ects_field, _ = PointsOfCourseEntities.objects.get_or_create(entity=proposal, type_of_point=pt, program__isnull=True)
            ects = ects_field.value
        except NotOwnerException:
            raise Http404
        except ObjectDoesNotExist:
            raise Http404
        if (not request.user.is_staff) and (proposal.owner != request.user.employee):
            raise Http404
    full_edit = False
    if request.user.has_perm('proposal.can_create_offer'):
        full_edit = True
    proposal_form = ProposalForm(data=request.POST or None, instance=proposal, prefix='entity', initial={'ects': ects}, full_edit=True)
    description_form = ProposalDescriptionForm(data=request.POST or None, instance=description, prefix='description')

    syllabus_form = SyllabusForm(data=request.POST or None, instance=syllabus, prefix='syllabus')
    initial_data = [{'name':'studiowanie tematyki wykładów i literatury'},
                    {'name':'przygotowanie do ćwiczeń'},
                    {'name':'przygotowanie do pracowni'},
                    {'name':'praca nad projektem'},
                    {'name':'przygotowanie do sprawdzianów/kolokwiów'},
                    {'name':'przygotowanie do egzaminu'},
                    {'name':'przygotowanie raportu/prezentacji'}]
    extrafields = 8
    if request.method == "POST" or (syllabus is not None and len(syllabus.studentwork_set.all())>0):
        extrafields = 1
    StudentWorkFormset = inlineformset_factory(Syllabus, StudentWork,extra=extrafields)
    if extrafields == 1:
        student_work_formset = StudentWorkFormset(request.POST or None, instance = syllabus)
    else:
        student_work_formset = StudentWorkFormset(request.POST or None, instance = syllabus,initial=initial_data)
    if request.method == "POST":
        if proposal_form.is_valid() and description_form.is_valid() and syllabus_form.is_valid() and student_work_formset.is_valid():
            sendnotification = False
            new_proposal = False
            if proposal is None:
                new_proposal = True
            proposal = proposal_form.save(commit=False)
            description = description_form.save(commit=False)
            syllabus = syllabus_form.save(commit=False)

            if not proposal.owner:
                proposal.owner = request.user.employee
            if new_proposal or proposal.status == 5:
                proposal.status = 0
                sendnotification = True
 
            proposal.save()

            description.author = request.user.employee
            description.entity_id = proposal.id

            if proposal.is_proposal():
                description.save()
            else:
                description.save_as_copy()

            syllabus.entity_id = proposal.id
            syllabus.save()
            syllabus_form.save_m2m()
            student_work_formset.instance = syllabus
            student_work_formset.save()

            if not ects_field:
                ects_field, _ = PointsOfCourseEntities.objects.get_or_create(entity=proposal, type_of_point=pt, program__isnull=True)
            ects_field.value = proposal_form.cleaned_data['ects'];
            ects_field.save()
            description_form.save_m2m()
            proposal_form.save_m2m()

            proposal = proposal_for_offer(proposal.slug)
            proposal.save()

            messages.success(request, u'Propozycja zapisana')
            if sendnotification:
                send_notification_to_3d(proposal, new_proposal)
                messages.success(request, u'Wysłano wiadomość do DDD z prośbą o zaakceptowanie propozycji przedmiotu')

            return redirect('my-proposal-show', slug=proposal.slug)
        else:
            messages.error(request, u'Popraw błędy w formularzu')

    return TemplateResponse(request, 'offer/proposal/form.html', {
        "form": proposal_form,
        "desc": description_form,
        "syllabus": syllabus_form,
        "student_work_formset": student_work_formset,
        "proposal": proposal,
        "types_data": Type.get_types_for_syllabus()
        })

@permission_required('proposal.can_create_offer')
def manage(request):
    proposals = CourseEntity.noremoved.filter(status=0).all()
    return TemplateResponse(request, 'offer/manage/proposals.html', locals())

@permission_required('proposal.can_create_offer')
def proposal_accept(request, slug=None):
    proposal = proposal_for_offer(slug)
    proposal.mark_as_accepted()
    proposal.save()
    messages.success(request, u'Zaakceptowano przedmiot '+proposal.name)
    return redirect('manage')

@permission_required('proposal.can_create_offer')
def proposal_for_review(request, slug=None):
    proposal = proposal_for_offer(slug)
    proposal.mark_for_review()
    proposal.save()
    return redirect('manage')
