from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse

from apps.enrollment.courses.models import CourseEntity, Semester
from apps.offer.vote.models import SingleVote, SystemState
from apps.users.decorators import student_required

from .forms import prepare_vote_formset


@student_required
def vote(request):
    """Renders voting form to the student and handles voting POST requests."""
    system_state = SystemState.get_current_state()

    if not system_state.is_vote_active() and (system_state.correction_active_semester() is None):
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
    """Vote main page."""
    system_state = SystemState.get_current_state()
    is_vote_active = system_state.is_vote_active() or system_state.correction_active_semester()
    data = {
        'is_vote_active': is_vote_active,
        'max_points': SystemState.DEFAULT_MAX_POINTS,
        'semester': Semester.get_current_semester()
    }
    return render(request, 'vote/index.html', data)


@student_required
def my_vote(request):
    """Shows the student his own vote."""
    system_state = SystemState.get_current_state()
    votes = SingleVote.objects.meaningful().filter(state=system_state, student=request.user.student)

    is_vote_active = system_state.is_vote_active() or system_state.correction_active_semester()

    return TemplateResponse(request, 'vote/my_vote.html', {
        'votes': votes,
        'is_vote_active': is_vote_active,
    })


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
