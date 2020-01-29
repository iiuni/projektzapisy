from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from apps.users.models import BaseUser
from django.urls import reverse
from apps.offer.vote.models.system_state import SystemState
from apps.offer.plan.sheets import create_sheets_service, update_voting_results_sheet, update_plan_proposal_sheet, read_entire_sheet
from apps.offer.plan.utils import get_votes, propose, get_subjects_data, prepare_assignments_data, prepare_employees_data, make_stats_record, sort_subject_groups_by_type
from apps.enrollment.courses.models.group import GROUP_TYPE_CHOICES
from django.http import JsonResponse, HttpResponse
from apps.offer.proposal.models import Proposal, ProposalStatus
from django.core.exceptions import ObjectDoesNotExist
import json
import csv


VOTING_RESULTS_SPREADSHEET_ID = '1pfLThuoKf4wxirnMXLi0OEksIBubWpjyrSJ7vTqrb-M'
CLASS_ASSIGNMENT_SPREADSHEET_ID = '1jy195Cvfly7SJ1BI_-eBDjB4tx706ra35GCdFqmGDVM'
EMPLOYEES_SPREADSHEET_ID = '1OGvQLfekTF5qRAZyYSkSi164WtnDwsI1RUEDz80nyhY'


def plan_view(request):
    year = SystemState.get_current_state().year
    employees = read_entire_sheet(
        create_sheets_service(EMPLOYEES_SPREADSHEET_ID))
    assignments = read_entire_sheet(
        create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID))

    if employees is None or assignments is None:
        return render(request, 'plan/view-plan.html', {'error': True, 'year': year})
    assignments_winter = []
    assignments_summer = []
    staff = {}
    phds = {}
    others = {}
    pensum = 0
    hours_summer = 0
    hours_winter = 0

    def make_stats_dict():
        return {'wykład': 0,
                'ćwiczenia': 0,
                'ćwiczenia+pracownia': 0,
                'pracownia': 0,
                'seminarium': 0,
                'repetytorium': 0,
                'sekretarz': 0}

    stats_summer = make_stats_dict()
    stats_winter = make_stats_dict()

    staff, phds, others, pensum = prepare_employees_data(employees)

    for value in assignments:
        code = value[11]
        data = {'name': value[1], 'weekly': value[5],
                'type': value[2], 'other': value[6], 'id': value[0]}

        # divide courses for summer and winter semester
        if value[9] == 'z' and value[-2] != 'FALSE':
            value[0] = int(value[0])
            assignments_winter.append(value)
            hours_winter += int(value[7])
            if code in staff:
                if value[5]:
                    staff[code]['weekly_winter'] += int(value[5])
                staff[code]['courses_winter'].append(data)
            elif code in phds:
                if value[5]:
                    phds[code]['weekly_winter'] += int(value[5])
                phds[code]['courses_winter'].append(data)
            elif code in others:
                if value[5]:
                    others[code]['weekly_winter'] += int(value[5])
                others[code]['courses_winter'].append(data)
            lecture_type, hours = make_stats_record(value)
            stats_winter[lecture_type] += hours

        elif value[9] == 'l' and value[-2] != 'FALSE':
            value[0] = int(value[0])
            assignments_summer.append(value)

            hours_summer += int(value[7])
            if code in staff:
                if value[5]:
                    staff[code]['weekly_summer'] += int(value[5])
                staff[code]['courses_summer'].append(data)
            elif code in phds:
                if value[5]:
                    phds[code]['weekly_summer'] += int(value[5])
                phds[code]['courses_summer'].append(data)
            elif code in others:
                if value[5]:
                    others[code]['weekly_summer'] += int(value[5])
                others[code]['courses_summer'].append(data)
            lecture_type, hours = make_stats_record(value)
            stats_summer[lecture_type] += hours

    is_empty = False if assignments_winter and assignments_summer else True

    if not is_empty:
        assignments_winter = prepare_assignments_data(assignments_winter)
        assignments_summer = prepare_assignments_data(assignments_summer)

        is_empty = False if assignments_winter and assignments_summer else True

        context = {
            'error': False,
            'year': year,
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
        return render(request, 'plan/view-plan.html', {'is_empty': is_empty, 'error': False, 'year': year})


def plan_create(request):
    if request.user.is_superuser:
        courses_proposal = get_votes(3)
        assignments = read_entire_sheet(
            create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID))

        courses = []
        current_year = SystemState.get_current_state().year

        if not assignments:
            for key, value in courses_proposal.items():
                # First value is the name of course
                # Second value is the semester when the course is planned to be
                # Third value says if this course is proposed
                courses.append(
                    [key, value[current_year]['semester'], propose(value)]
                )
        else:
            for key, value in courses_proposal.items():
                checked = False

                for item in assignments:
                    if key in item:
                        checked = True
                        break

                courses.append(
                    [key, value[current_year]['semester'], checked]
                )

        context = {
            'courses_proposal': courses,
            'voting_results_sheet_id': VOTING_RESULTS_SPREADSHEET_ID,
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
        picked_courses_accurate_info_z = []
        picked_courses_accurate_info_l = []
        current_year = SystemState.get_current_state().year
        for key, value in all_courses.items():
            if key in picked_courses:
                subject = (key, value[current_year]['semester'],
                           value[current_year]['proposal'])
                if value[current_year]['semester'] == 'z':
                    picked_courses_accurate_info_z.append(subject)
                else:
                    picked_courses_accurate_info_l.append(subject)

        sheet = create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID)
        proposal_z = get_subjects_data(picked_courses_accurate_info_z, 3)
        proposal_l = get_subjects_data(picked_courses_accurate_info_l, 3)

        proposal_z = sort_subject_groups_by_type(proposal_z)
        proposal_l = sort_subject_groups_by_type(proposal_l)
        proposal = proposal_z + proposal_l

        update_plan_proposal_sheet(sheet, proposal)
    return HttpResponseRedirect(reverse('plan-create'))


def plan_create_voting_sheet(request):
    voting = get_votes(3)
    sheet = create_sheets_service(VOTING_RESULTS_SPREADSHEET_ID)
    update_voting_results_sheet(sheet, voting)
    return HttpResponseRedirect(reverse('plan-create'))


def generate_scheduler_file(request, slug, format):
    if request.user.is_superuser:
        current_year = SystemState.get_current_state().year
        employees = read_entire_sheet(
            create_sheets_service(EMPLOYEES_SPREADSHEET_ID))
        assignments = read_entire_sheet(
            create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID))
        content = []
        semester = ""
        multiple_teachers = {}
        if slug == 'zima':
            semester = 'z'
        elif slug == 'lato':
            semester = 'l'
        else:
            return HttpResponse(status=404)
        groups = {}
        for group in GROUP_TYPE_CHOICES:
            groups[group[1]] = group[0]

        for employee in employees:
            if employee[4] != '' and employee[0] != 'pensum':
                if format == 'json':
                    content.append(
                        {'type': 'employee', 'id': employee[5], 'first_name': employee[2],
                         'last_name': employee[3], 'pensum': float(employee[0])})
                elif format == 'csv':
                    content.append(
                        ['employee', employee[5], employee[2], employee[3], float(employee[0])])
        index = 1
        lp = False
        for assignment in assignments:
            if lp and assignment[9] == semester and assignment[12] != 'FALSE':
                id = -1
                course_id = -1
                if assignment[2].lower() not in groups:
                    continue
                try:
                    proposal = Proposal.objects.filter(name=assignment[1])
                    for p in proposal:
                        if p.status != ProposalStatus.WITHDRAWN:
                            course_id = p.id
                            break
                except Proposal.ObjectDoesNotExist:
                    course_id = -1

                if assignment[-1]:
                    if assignment[1] in multiple_teachers and assignment[-1] in multiple_teachers[assignment[1]]:
                        id = multiple_teachers[assignment[1]][assignment[-1]]
                    else:
                        id = index
                        multiple_teachers[assignment[1]] = {}
                        multiple_teachers[assignment[1]
                                          ][assignment[-1]] = index
                else:
                    id = index
                if format == 'json':
                    content.append(
                        {'type': 'course', 'semester': semester, 'course_id': course_id, 'course_name': assignment[1], 'id': id,
                         'group_type': int(groups[assignment[2].lower()]), 'hours': int(assignment[5]), 'teacher_id': assignment[11]})
                elif format == 'csv':
                    content.append(['course', semester, course_id, assignment[1], id, int(
                        groups[assignment[2].lower()]), int(assignment[5]), assignment[11]])
                index += 1
            if assignment[0] == "Lp":
                lp = True

        if format == 'json':
            response = JsonResponse(content, safe=False)
            response['Content-Disposition'] = 'attachment; filename={0}'.format(
                "przydzial" + "_" + slug + "_" + str(current_year) + ".json")
            return response
        elif format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename={0}'.format(
                "przydzial" + "_" + slug + "_" + str(current_year) + ".csv")
            writer = csv.writer(response)
            writer.writerow(['Typ', 'ID', 'Imię', 'Nazwisko', 'Pensum'])
            reached_courses = False
            for c in content:
                if c[0] != 'employee' and not reached_courses:
                    writer.writerow([''])
                    writer.writerow(
                        ['Typ', 'Semestr', 'ID kursu', 'Nazwa kursu', 'ID grupy', 'Typ grupy', 'Godziny', 'ID nauczyciela'])
                    reached_courses = True
                writer.writerow(c)
            return response
    else:
        return HttpResponse(status=403)


def generate_scheduler_file_json(request, slug):
    return generate_scheduler_file(request, slug, 'json')


def generate_scheduler_file_csv(request, slug):
    return generate_scheduler_file(request, slug, 'csv')
