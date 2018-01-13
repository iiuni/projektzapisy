# -*- coding: utf-8 -*-

"""
    Vote views
"""
from datetime import date
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from apps.enrollment.courses.models.course import CourseEntity

from apps.offer.vote.models import SingleVote, SystemState
from apps.enrollment.courses.models import Type
from apps.enrollment.courses.models import Semester

from apps.users.decorators import student_required


@student_required
def vote(request):
    from vote_form import VoteFormsets

    student = request.user.student
    state = SystemState.get_state()

    if not state.is_system_active():
        raise Http404

    SingleVote.make_votes(student, state=state)

    kwargs = {'student': student, 'state': state}
    if request.method == 'POST':
        kwargs['post'] = request.POST

    formset = VoteFormsets(**kwargs)

    if request.method == 'POST':

        if formset.is_valid():
            formset.save()
            messages.success(request, "Oddano poprawny głos")
            return redirect('vote')

        else:
            messages.error(request, "Nie udało się oddać głosu")
            for error in formset.errors:
                messages.error(request, error)

    data = {'formset': formset,
            'proposalTypes': Type.objects.all().select_related('group'),
            'isCorrectionActive': state.is_correction_active()}

    return render(request, 'offer/vote/form.html', data)


@login_required
def vote_main(request):
    """
        Vote main page
    """
    sytem_state = SystemState.get_state()
    data = {'isVoteActive': sytem_state.is_system_active(), 'max_points': sytem_state.max_points,
            'semester': Semester.get_current_semester()}
    return render(request, 'offer/vote/index.html', data)


@student_required
def vote_view(request):
    """
        View of once given vote
    """
    votes = SingleVote.get_votes(request.user.student)
    is_voting_active = SystemState.get_state(date.today().year).is_system_active()

    return TemplateResponse(request, 'offer/vote/view.html', locals())


@login_required
def vote_summary(request):
    """
        summary for vote
    """
    summer = []
    winter = []
    unknown = []

    year = date.today().year
    state = SystemState.get_state(year)

    subs = CourseEntity.get_vote()
    subs = SingleVote.add_vote_count(subs, state)

    for sub in subs:
        if sub.semester == 'z':
            winter.append((sub.votes, sub.voters, sub))
        elif sub.semester == 'l':
            summer.append((sub.votes, sub.voters, sub))
        elif sub.semester == 'u':
            unknown.append((sub.votes, sub.voters, sub))

    data = {
        'winter': winter,
        'summer': summer,
        'unknown': unknown,
        'is_voting_active': state.is_system_active()
    }

    return render(request, 'offer/vote/summary.html', data)


@login_required
def proposal_vote_summary(request, slug):
    """
        Summary for given course
    """
    try:
        course = CourseEntity.noremoved.get(slug=slug)
    except ObjectDoesNotExist:
        raise Http404

    points, votes, voters = SingleVote.get_points_and_voters(course)

    data = {'proposal': course,
            'points': points,
            'votes': votes,
            'voters': voters}

    return render(request, 'offer/vote/proposal_summary.html', data)
