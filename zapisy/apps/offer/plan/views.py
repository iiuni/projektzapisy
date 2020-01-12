from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from apps.users.models import BaseUser
from django.urls import reverse
from apps.offer.vote.models.system_state import SystemState

from apps.offer.plan.sheets import create_sheets_service, update_voting_results_sheet, update_plan_proposal_sheet, \
    read_entire_sheet
from apps.offer.plan.utils import get_votes, propose, get_subjects_data, prepare_assignments_data

VOTING_RESULTS_SPREADSHEET_ID = '1pfLThuoKf4wxirnMXLi0OEksIBubWpjyrSJ7vTqrb-M'
PLAN_PROPOSAL_SPREADSHEET_ID = '17fDGtuZVUZlUztXqtBn1tuOqkZjCTPJUb14p5YQrnck'
CLASS_ASSIGNMENT_SPREADSHEET_ID = '1jy195Cvfly7SJ1BI_-eBDjB4tx706ra35GCdFqmGDVM'
EMPLOYEES_SPREADSHEET_ID = '1OGvQLfekTF5qRAZyYSkSi164WtnDwsI1RUEDz80nyhY'


def plan_view(request):
    if request.user.is_superuser or BaseUser.is_employee(request.user):
        employees = read_entire_sheet(
            create_sheets_service(EMPLOYEES_SPREADSHEET_ID))
        assignments = read_entire_sheet(
            create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID))
        assignments_winter = []
        assignments_summer = []
        employee = {}
        phd = {}
        others = {}

        for value in employees:
            if value[4] != '' and value[0] != 'pensum':
                data = {'name': value[2] + ' ' + value[3],
                        'pensum': value[0],
                        'balance': value[13],
                        'weekly_winter': 0,
                        'weekly_summer': 0,
                        'courses_winter': [],
                        'courses_summer': []
                        }
                if value[1] == 'prac':
                    employee[value[4]] = dict(data)
                elif value[1] == 'doktorant':
                    phd[value[4]] = dict(data)
                else:
                    others[value[4]] = dict(data)

        for value in assignments:
            if value[9] == 'z' and value[-1] == 'TRUE':
                value[0] = int(value[0])
                assignments_winter.append(value)

                code = value[11]
                data = {'name': value[1], 'weekly': value[5],
                        'type': value[2], 'other': value[6], 'id': value[0]}
                if code in employee:
                    employee[code]['weekly_winter'] += int(value[5])
                    employee[code]['courses_winter'].append(data)
                elif code in phd:
                    phd[code]['weekly_winter'] += int(value[5])
                    phd[code]['courses_winter'].append(data)
                elif code in others:
                    others[code]['weekly_winter'] += int(value[5])
                    others[code]['courses_winter'].append(data)

            elif value[9] == 'l' and value[-1] == 'TRUE':
                value[0] = int(value[0])
                assignments_summer.append(value)

                code = value[11]
                data = {'name': value[1], 'weekly': value[5],
                        'type': value[2], 'other': value[6], 'id': value[5]}
                if code in employee:
                    employee[code]['weekly_summer'] += int(value[5])
                    employee[code]['courses_summer'].append(data)
                elif code in phd:
                    phd[code]['weekly_summer'] += int(value[5])
                    phd[code]['courses_summer'].append(data)
                elif code in others:
                    others[code]['weekly_summer'] += int(value[5])
                    others[code]['courses_summer'].append(data)

        is_empty = False if assignments_winter and assignments_summer else True

        if not is_empty:
            assignments_winter = prepare_assignments_data(assignments_winter)
            assignments_summer = prepare_assignments_data(assignments_summer)

        print(employee)
        context = {
            'is_empty': is_empty,
            'winter': assignments_winter,
            'summer': assignments_summer,
            'employees': employee,
            'phds': phd,
            'others': others
        }
        return render(request, 'plan/view-plan.html', context)
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
            'plan_proposal_sheet_id': PLAN_PROPOSAL_SPREADSHEET_ID,
            'class_assignment_sheet_id': CLASS_ASSIGNMENT_SPREADSHEET_ID,
            'employees_sheet_id': EMPLOYEES_SPREADSHEET_ID
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
                subject = (key, value[current_year]['semester'],
                           value[current_year]['proposal'])
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


def generate_plan_html(request):
    return HttpResponseRedirect(reverse('plan-view'))
