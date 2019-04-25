from datetime import date
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.template.response import TemplateResponse
from apps.enrollment.courses.models.course import CourseEntity

from apps.offer.vote.models import SingleVote, SystemState
from apps.enrollment.courses.models.course_type import Type
from apps.enrollment.courses.models.semester import Semester
from apps.users.decorators import student_required

from .forms import prepare_vote_formset


@student_required
def vote(request):
    semester = Semester.objects.get_next()
    system_state = SystemState.get_state_for_semester(semester)

    if not system_state.is_vote_active() and system_state.correction_active_semester() is None:
        messages.warning(request, "Głosowanie nie jest w tym momencie aktywne.")
        return redirect('vote-main')

    if request.method == 'POST':
        formset = prepare_vote_formset(system_state, request.user.student, post=request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Zapisano głos.")
        else:
            messages.error(request, "\n".join(formset.non_form_errors()))

    else:
        formset = prepare_vote_formset(system_state, request.user.student)

    return render(request, 'vote/form.html', {'formset': formset})


@login_required
def vote_main(request):
    """
        Vote main page
    """
    semester = Semester.objects.get_next()
    sytem_state = SystemState.get_state_for_semester(semester)
    data = {'isVoteActive': sytem_state.is_vote_active(), 'max_points': 3,
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
