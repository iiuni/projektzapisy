# -*- coding: utf-8 -*-

"""
    Proposal views
"""
from django.contrib                 import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.http                    import Http404
from django.shortcuts               import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http   import require_POST
from apps.enrollment.courses.models.course import CourseEntity, CourseDescription, Course
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.course_type import Type

from apps.offer.proposal.forms import ProposalForm, ProposalDescriptionForm
from apps.offer.proposal.exceptions      import  NotOwnerException


import logging
from apps.offer.proposal.utils import proposal_for_offer, employee_proposal
from apps.users.decorators import employee_required, offer_manager_required
from apps.users.models import Employee

logger = logging.getLogger("")


def offer(request, slug=None):
    """
    if slug is None, this view shows offer main page,
    else show proposal page
    """
    proposal   = proposal_for_offer(slug)
    proposals  = CourseEntity.get_proposals()
    types_list = Type.get_all_for_jsfilter()
    teachers   = Employee.get_actives()

    return TemplateResponse(request, 'offer/offer.html', locals())

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

    if slug:
        try:
            proposal = CourseEntity.get_employee_proposal(request.user, slug)
            description = CourseDescription.objects.filter(entity=proposal).order_by('-id')[0]
        except NotOwnerException:
            raise Http404
        except ObjectDoesNotExist:
            raise Http404

    proposal_form      = ProposalForm(data=request.POST or None,
                                    instance=proposal, prefix='entity')
    description_form = ProposalDescriptionForm(data=request.POST or None,
                                               instance=description, prefix='description')

    if proposal_form.is_valid() and description_form.is_valid():
        proposal = proposal_form.save(commit=False)
        description = description_form.save(commit=False)
        if not proposal.owner:
            proposal.owner = request.user.employee
        if proposal.status == 5:
            proposal.status = 0
        proposal.save()

        description.author = request.user.employee
        description.entity_id = proposal.id

        if proposal.is_proposal():
            description.save()
        else:
            description.save_as_copy()

        description_form.save_m2m()
        proposal_form.save_m2m()

        proposal = proposal_for_offer(proposal.slug)
        proposal.save()

        messages.success(request, u'Propozycja zapisana')

        return redirect('my-proposal-show', slug=proposal.slug)

    return TemplateResponse(request, 'offer/proposal/form.html', {
        "form": proposal_form,
        "desc": description_form,
        "proposal": proposal
        })

@offer_manager_required
def manage(request):
    proposals = CourseEntity.noremoved.filter(status=0).all()
    return TemplateResponse(request, 'offer/manage/proposals.html', locals())

@offer_manager_required
def proposal_accept(request, slug=None):
    proposal = proposal_for_offer(slug)
    proposal.mark_as_accepted()
    proposal.save()
    messages.success(request, u'Zaakceptowano przedmiot '+proposal.name)
    return redirect('manage')

@offer_manager_required
def proposal_for_review(request, slug=None):
    proposal = proposal_for_offer(slug)
    proposal.mark_for_review()
    proposal.save()
    return redirect('manage')
