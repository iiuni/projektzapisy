"""
    Proposal views
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe

from apps.enrollment.courses.models.effects import Effects
from apps.enrollment.courses.models.tag import Tag
from apps.enrollment.courses.models.course import CourseEntity, CourseDescription, Course
from apps.enrollment.courses.models.points import PointsOfCourseEntities, PointTypes
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.course_type import Type
from apps.offer.preferences.models import Preference

from apps.offer.proposal.forms import ProposalForm, ProposalDescriptionForm, SyllabusForm, EditProposalForm
from apps.offer.proposal.models import Syllabus, StudentWork, Proposal, ProposalStatus
from apps.offer.proposal.exceptions import NotOwnerException
from .forms import SelectVotingForm

import json
import logging
from apps.offer.proposal.utils import proposal_for_offer, employee_proposal, send_notification_to_3d
from apps.users.models import Employee
from apps.users.decorators import employee_required

logger = logging.getLogger(__file__)


def offer(request, slug=None):
    """
    if slug is None, this view shows offer main page,
    else show proposal page
    """
    if slug is not None:
        proposal = get_object_or_404(Proposal, slug=slug)
    else:
        proposal = None

    filter_statuses = [ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE, ProposalStatus.WITHDRAWN]
    proposal_list = Proposal.objects.filter(
        status__in=filter_statuses).select_related('course_type', 'owner__user').order_by('name')

    return TemplateResponse(request, 'proposal/offer.html', {
        "proposal": proposal,
        "proposals": proposal_list,
    })


@permission_required('proposal.can_create_offer')
def select_for_voting(request):
    courses = CourseEntity.noremoved.filter(
        status__in=[CourseEntity.STATUS_IN_OFFER, CourseEntity.STATUS_TO_VOTE])
    courses_choices = [(x.pk, x.name) for x in courses]

    if request.method == 'POST':
        form = SelectVotingForm(request.POST)
        form.fields['courses'].choices = courses_choices
        if form.is_valid():
            selected_courses_ids = [
                int(x) for x in form.cleaned_data['courses']
            ]
            for course in courses:
                if (not course.is_in_voting() and course.id in selected_courses_ids):
                    course.mark_for_voting()
                    course.save()
                elif (course.is_in_voting() and course.id not in selected_courses_ids):
                    course.status = CourseEntity.STATUS_IN_OFFER
                    course.save()
        return redirect('/offer/manage/select_for_voting')
    else:
        courses_in_voting = courses.filter(status=CourseEntity.STATUS_TO_VOTE)
        form = SelectVotingForm(
            initial={'courses': [x.pk for x in courses_in_voting]})
        form.fields["courses"].choices = courses_choices
    return TemplateResponse(
        request, 'offer/manage/select_for_voting.html', {'form': form})


def all_groups(request):
    semester = Semester.get_current_semester()
    courses = Course.objects.filter(semester=semester).all()
    return TemplateResponse(request, 'offer/manage/courses.html', {'courses': courses})


def course_groups(request, slug):
    if request.method == 'GET':
        teachers_by_preference_tutorial = {-1: [], 0: [], 1: [], 2: [], 3: []}
        course = Course.objects.prefetch_related("groups").get(slug=slug)
        teachers = Employee.objects.all()

        for teacher in teachers:
            prefs = Preference.for_employee(teacher).filter(proposal=course.entity).all()
            pref = None
            if len(prefs) > 0:
                pref = prefs[len(prefs) - 1].tutorial

            if pref is None:
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

        return TemplateResponse(request,
                                'offer/manage/groups.html',
                                {'course': course,
                                 'teachers': teachers,
                                 'groups_with_teachers': groups_with_teachers,
                                 'path': request.path})
    elif request.method == 'POST':
        for group_id, teacher_id in request.POST.items():
            if group_id[:6] != "group_":
                continue
            group_id = group_id[6:]
            group = Group.objects.get(pk=group_id)
            teacher = Employee.objects.get(pk=teacher_id)
            if group.teacher != teacher:
                group.teacher = teacher
                group.save()
        return redirect(request.path)


@employee_required
def my_proposals(request, slug=None):
    proposals_list = Proposal.objects.filter(owner=request.user.employee)
    proposal = None
    if slug is not None:
        proposal = get_object_or_404(Proposal, slug=slug)
    return render(request, 'proposal/my-proposals.html', {
        'proposals_list': proposals_list,
        'proposal': proposal,
    })


# FIXME: course descriptions and course entities have a two way foreign key
# relationship, and we have special form code in the admin UI to make sure
# both foreign keys are pointing at each other. If the admin forgets to
# create a corresponding course description after creating a course entity
# we create a default one below. (This can be removed when the courses
# app is refactored)
def _create_missing_course_description(request, proposal):
    description = CourseDescription.objects.create(
        entity=proposal,
        author=request.user.employee)
    proposal.information = description
    proposal.save()
    return description


@employee_required
def proposal_edit(request, slug=None):
    if slug is not None:
        # Editing existing proposal.
        proposal = get_object_or_404(Proposal, slug=slug)

        # Check if the user is allowed to edit this proposal.
        if request.user.employee != proposal.owner and not request.user.is_staff:
            raise PermissionDenied
        form = EditProposalForm(instance=proposal)
    if request.method == "POST":
        # Handling filled-in proposal form.
        form = EditProposalForm(request.POST, instance=proposal, user=request.user)
        if form.is_valid():
            form.save()
        else:
            form_errors_message = ("Formularz niezapisany: " +
                                   ";".join(form.non_field_errors()))
            messages.error(request, form_errors_message)
    if slug is None and request.method == "GET":
        # Display an empty form for new proposal.
        form = EditProposalForm()
    return render(request, 'proposal/edit-proposal.html', {
        'form': form,
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
    messages.success(request, 'Zaakceptowano przedmiot ' + proposal.name)
    return redirect('manage')


@permission_required('proposal.can_create_offer')
def proposal_for_review(request, slug=None):
    proposal = proposal_for_offer(slug)
    proposal.mark_for_review()
    proposal.save()
    return redirect('manage')
