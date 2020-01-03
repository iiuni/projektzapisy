from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from apps.users.models import BaseUser
from django.urls import reverse
from apps.offer.vote.models.system_state import SystemState

from apps.offer.plan.sheets import create_sheets_service, update_voting_results_sheet, update_plan_proposal_sheet
from apps.offer.plan.utils import get_votes, propose, get_subjects_data

VOTING_RESULTS_SPREADSHEET_ID = '1pfLThuoKf4wxirnMXLi0OEksIBubWpjyrSJ7vTqrb-M'
PLAN_PROPOSAL_SPREADSHEET_ID = '17fDGtuZVUZlUztXqtBn1tuOqkZjCTPJUb14p5YQrnck'


def plan_view(request):
    if request.user.is_superuser or BaseUser.is_employee(request.user):
        return render(request, 'plan/view-plan.html')
    else:
        return HttpResponse(status=403)


def plan_create(request):
    if request.user.is_superuser:
        courses_proposal = get_votes(3)
        courses = []
        current_year = SystemState.get_current_state().year
        for key, value in courses_proposal.items():
            # First value is the name of course
            # Second value is the semester when the course is planned to be
            # Third value says if this course is proposed
            courses.append(
                [key, value[current_year]['semester'], propose(value)]
            )

        context = {
            'courses_proposal': courses,
            'voting_results_sheet_id': VOTING_RESULTS_SPREADSHEET_ID,
            'plan_proposal_sheet_id': PLAN_PROPOSAL_SPREADSHEET_ID
        }
        return render(request, 'plan/create-plan.html', context)
    else:
        return HttpResponse(status=403)


def plan_vote(request):
    if request.method == 'POST':
        picked_courses = []
        for course in request.POST:
            if course != 'csrfmiddlewaretoken':
                picked_courses.append(course)
        picked_courses.sort()
        all_courses = get_votes(1)
        picked_courses_accurate_info = []
        current_year = SystemState.get_current_state().year
        for key, value in all_courses.items():
            if key in picked_courses:
                subject = (key, value[current_year]['semester'], value[current_year]['proposal'])
                picked_courses_accurate_info.append(subject)

        sheet = create_sheets_service(PLAN_PROPOSAL_SPREADSHEET_ID)
        proposal = get_subjects_data(picked_courses_accurate_info, 3)
        update_plan_proposal_sheet(sheet, proposal)
    return HttpResponseRedirect(reverse('plan-create'))


def plan_create_voting_sheet(request):
    voting = get_votes(3)
    sheet = create_sheets_service(VOTING_RESULTS_SPREADSHEET_ID)
    update_voting_results_sheet(sheet, voting)
    return HttpResponseRedirect(reverse('plan-create'))
