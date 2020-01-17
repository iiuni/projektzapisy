from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from apps.users.models import BaseUser
from django.urls import reverse
from apps.offer.vote.models.system_state import SystemState
from apps.offer.plan.sheets import create_sheets_service, update_voting_results_sheet, update_plan_proposal_sheet, read_entire_sheet
from apps.offer.plan.utils import get_votes, propose, get_subjects_data, prepare_assignments_data, prepare_employees_data, make_stats_record
import os.path

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
        staff = {}
        phds = {}
        others = {}
        pensum = 0
        hours_summer = 0
        hours_winter = 0
        stats_summer = []
        stats_winter = []

        staff, phds, others, pensum = prepare_employees_data(employees)

        for value in assignments:
            code = value[11]
            data = {'name': value[1], 'weekly': value[5],
                    'type': value[2], 'other': value[6], 'id': value[0]}

            # divide courses for summer and winter semester
            if value[9] == 'z':
                value[0] = int(value[0])
                assignments_winter.append(value)

                hours_winter += int(value[7])
                if code in staff:
                    staff[code]['weekly_winter'] += int(value[5])
                    staff[code]['courses_winter'].append(data)
                elif code in phds:
                    phds[code]['weekly_winter'] += int(value[5])
                    phds[code]['courses_winter'].append(data)
                elif code in others:
                    others[code]['weekly_winter'] += int(value[5])
                    others[code]['courses_winter'].append(data)

            elif value[9] == 'l':
                value[0] = int(value[0])
                assignments_summer.append(value)

                hours_summer += int(value[7])
                if code in staff:
                    staff[code]['weekly_summer'] += int(value[5])
                    staff[code]['courses_summer'].append(data)
                elif code in phds:
                    phds[code]['weekly_summer'] += int(value[5])
                    phds[code]['courses_summer'].append(data)
                elif code in others:
                    others[code]['weekly_summer'] += int(value[5])
                    others[code]['courses_summer'].append(data)

            elif value[0] == 'z':
                stats_winter.append(make_stats_record(value))
            elif value[0] == 'l':
                stats_summer.append(make_stats_record(value))

        is_empty = False if assignments_winter and assignments_summer else True

        if not is_empty:
            assignments_winter = prepare_assignments_data(assignments_winter)
            assignments_summer = prepare_assignments_data(assignments_summer)

        context = {
            'is_empty': is_empty,
            'winter': assignments_winter,
            'summer': assignments_summer,
            'staff': staff,
            'phds': phds,
            'others': others,
            'hours_summer': hours_summer,
            'hours_winter': hours_winter,
            'pensum': pensum,
            'stats_winter': stats_winter,
            'stats_summer': stats_summer,
            'balance': hours_summer + hours_winter - pensum
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


def generate_scheduler_file(request, slug):
    if request.user.is_superuser:
        current_year = SystemState.get_current_state().year
        employees = read_entire_sheet(
            create_sheets_service(EMPLOYEES_SPREADSHEET_ID))
        assignments = read_entire_sheet(
            create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID))
        content = ""
        semester = ""
        if slug == 'zima':
            semester = 'z'
        elif slug == 'lato':
            semester = 'l'
        else:
            return HttpResponse(status=404)

        for employee in employees:
            if employee[4] != '' and employee[0] != 'pensum':
                content += "o|" + \
                    employee[5] + "|" + employee[2] + "|" + \
                    employee[7] + "|" + employee[3] + "|" + employee[0] + "|\n"

        index = 1
        lp = False
        for assigment in assignments:
            if lp and assigment[9] == semester:
                content += "1|" + \
                    str(index) + "|" + assigment[1] + \
                    "|" + assigment[3] + "|" + assigment[5] + \
                    '|' + assigment[11] + "|\n"
                index += 1
            if assigment[0] == "Lp":
                lp = True

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            "przydzial" + slug + str(current_year) + ".txt")
        return response
    else:
        return HttpResponse(status=403)
