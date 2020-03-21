import copy
import csv
import os

import environ
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.enrollment.courses.models.group import GROUP_TYPE_CHOICES
from apps.offer.plan.sheets import (create_sheets_service, read_entire_sheet,
                                    update_plan_proposal_sheet,
                                    update_voting_results_sheet)
from apps.offer.plan.utils import (AssignmentsViewSummary, EmployeeData,
                                   EmployeesSummary, SingleAssignmentData,
                                   Statistics, TeacherInfo, get_last_years,
                                   get_subjects_data, get_votes, propose,
                                   sort_subject_groups_by_type)
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.offer.vote.models.system_state import SystemState

env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, os.pardir, 'env', '.env'))

VOTING_RESULTS_SPREADSHEET_ID = env('VOTING_RESULTS_SPREADSHEET_ID')
CLASS_ASSIGNMENT_SPREADSHEET_ID = env('CLASS_ASSIGNMENT_SPREADSHEET_ID')
EMPLOYEES_SPREADSHEET_ID = env('EMPLOYEES_SPREADSHEET_ID')


def plan_view(request):
    if not request.user.is_superuser and not request.user.employee:
        raise PermissionDenied
    year = SystemState.get_current_state().year
    employees_from_sheet = read_entire_sheet(
        create_sheets_service(EMPLOYEES_SPREADSHEET_ID))
    assignments_from_sheet = read_entire_sheet(
        create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID))

    assignments_winter: AssignmentsViewSummary = {}
    assignments_summer: AssignmentsViewSummary = {}
    staff: EmployeesSummary = {}
    phds: EmployeesSummary = {}
    others: EmployeesSummary = {}

    pensum_global = 0
    hours_winter = 0
    hours_summer = 0

    def make_stats_dict():
        return {'w': 0, 'ćw': 0, 'prac': 0, 'ćw_prac': 0, 'rep': 0, 'sem': 0, 'admin': 0}

    def make_teachers_dict():
        return {'w': [], 'ćw': [], 'prac': [], 'ćw_prac': [], 'rep': [], 'sem': [], 'admin': []}

    stats_summer: Statistics = make_stats_dict()
    stats_winter: Statistics = make_stats_dict()

    if employees_from_sheet is None or assignments_from_sheet is None:
        messages.error(request, "Arkusz nie istnieje")
        return render(request, 'plan/view-plan.html', {'error': True, 'year': year})

    for employee in employees_from_sheet:
        # Skip header
        try:
            pensum = float(employee[0])
        except ValueError:
            continue
        status = employee[1].lower()
        if status == 'prac':
            status = 'pracownik'
        elif status != 'doktorant':
            status = 'inny'

        name = employee[2] + ' ' + employee[3]
        code = employee[4]
        balance = float(employee[11]) if employee[11] else 0
        ed: EmployeeData(status, name, pensum, balance) = {
            'status': status, 'name': name, 'pensum': pensum, 'balance': balance, 'courses_winter': [], 'courses_summer': []}
        if status == 'pracownik':
            staff[code] = copy.copy(ed)
        elif status == 'doktorant':
            phds[code] = copy.copy(ed)
        else:
            others[code] = copy.copy(ed)
        pensum_global += pensum

    for assignment in assignments_from_sheet:
        if assignment[-2] == 'TRUE':
            assignment_confirmed = True
        else:
            assignment_confirmed = False
        # continue to next assignment if this assignment not confirmed
        if not assignment_confirmed:
            continue
        # if index is not castable to int, skip
        try:
            index = int(assignment[0])
        except ValueError:
            continue
        name = assignment[1]
        group_type = assignment[2].lower()
        group_type_short = assignment[3]
        if not group_type_short:
            continue
        semester = assignment[9]
        teacher = assignment[10]
        code = assignment[11]
        hours_weekly = float(assignment[5]) if assignment[5] else 0
        hours_semester = float(assignment[7]) if assignment[7] else 0
        multiple_teachers = int(assignment[-1]) if assignment[-1] else None

        assignmentData = SingleAssignmentData(name, index, group_type, group_type_short,
                                              hours_weekly, hours_semester, semester, teacher, code, multiple_teachers)
        if semester == 'l':
            if name not in assignments_summer:
                assignments_summer[name] = {
                    'index': index, 'teachers': make_teachers_dict(), 'stats': make_stats_dict()}
            if code in staff:
                staff[code]['courses_summer'].append(assignmentData)
            elif code in phds:
                phds[code]['courses_summer'].append(assignmentData)
            elif code in others:
                others[code]['courses_summer'].append(assignmentData)

            assignments_summer[name]['stats'][group_type_short] = hours_weekly
            assignments_summer[name]['teachers'][group_type_short].append(
                TeacherInfo(code, teacher))
            hours_summer += hours_semester
            stats_summer[group_type_short] += hours_semester
        else:
            if name not in assignments_winter:
                assignments_winter[name] = {
                    'index': index, 'teachers': make_teachers_dict(), 'stats': make_stats_dict()}

            if code in staff:
                staff[code]['courses_winter'].append(assignmentData)
            elif code in phds:
                phds[code]['courses_winter'].append(assignmentData)
            elif code in others:
                others[code]['courses_winter'].append(assignmentData)

            assignments_winter[name]['stats'][group_type_short] = hours_weekly
            assignments_winter[name]['teachers'][group_type_short].append(
                TeacherInfo(code, teacher))
            stats_winter[group_type_short] += hours_semester
            hours_winter += hours_semester

    is_empty = False if assignments_winter or assignments_summer else True
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
        'pensum': pensum_global,
        'stats_winter': stats_winter,
        'stats_summer': stats_summer,
        'balance': hours_summer + hours_winter - pensum_global
    }
    return render(request, 'plan/view-plan.html', context)


@staff_member_required
def plan_create(request):
    courses_proposal = get_votes(get_last_years(3))
    assignments = read_entire_sheet(
        create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID))

    courses = []

    if not assignments:
        for key, value in courses_proposal.items():
            # First value is the name of course
            # Second is name for the input
            # Third value is the semester when the course is planned to be
            # Fourth value says if this course is proposed
            name = 'asgn' + key
            courses.append(
                [key, name, value.semester, propose(value)]
            )
    else:
        for key, value in courses_proposal.items():
            checked = False

            for item in assignments:
                if key in item:
                    checked = True
                    break

            name = 'asgn' + key
            courses.append(
                [key, name, value.semester, checked]
            )

    context = {
        'courses_proposal': courses,
        'voting_results_sheet_id': VOTING_RESULTS_SPREADSHEET_ID,
        'class_assignment_sheet_id': CLASS_ASSIGNMENT_SPREADSHEET_ID,
        'employees_sheet_id': EMPLOYEES_SPREADSHEET_ID
    }
    return render(request, 'plan/create-plan.html', context)


@require_POST
@staff_member_required
def plan_vote(request):
    picked_courses = []
    for course in request.POST:
        if course[:4] == 'asgn':
            picked_courses.append(course[4:])
    picked_courses.sort()
    for a in picked_courses:
        print(a)
    all_courses = get_votes(get_last_years(1))
    picked_courses_accurate_info_z = []
    picked_courses_accurate_info_l = []
    for course in picked_courses:
        if course in all_courses:
            semester = all_courses[course].semester
            proposal = all_courses[course].proposal
            subject = (course, semester, proposal)
            if semester == 'z':
                picked_courses_accurate_info_z.append(subject)
            else:
                picked_courses_accurate_info_l.append(subject)

    sheet = create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID)
    proposal_z = get_subjects_data(
        picked_courses_accurate_info_z, get_last_years(3))
    proposal_l = get_subjects_data(
        picked_courses_accurate_info_l, get_last_years(3))

    proposal_z = sort_subject_groups_by_type(proposal_z)
    proposal_l = sort_subject_groups_by_type(proposal_l)
    proposal = proposal_z + proposal_l

    update_plan_proposal_sheet(sheet, proposal)
    return HttpResponseRedirect(reverse('plan-create'))


def plan_create_voting_sheet(request):
    years = get_last_years(3)
    voting = get_votes(years)
    sheet = create_sheets_service(VOTING_RESULTS_SPREADSHEET_ID)
    update_voting_results_sheet(sheet, voting, years)
    return HttpResponseRedirect(reverse('plan-create'))


# generates a json file used by scheduler or puts the very same data in csv file, depending on format argument
# data comes from both employees and assignments Google sheets
@staff_member_required
def generate_scheduler_file(request, slug, format):
    """Creates a file for scheduler system to use.

    Args:
        slug: represents semester, 'lato' for summer, 'zima' for winter.
        format: format of requested file, either 'csv' or 'json'.
    Returns:
        File in the desired format in a response.
    """
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
        return render(request, '404.html')

    groups = {}
    for group in GROUP_TYPE_CHOICES:
        groups[group[1]] = group[0]

    for employee in employees:
        # if pensum is not castable to float, just skip this row
        try:
            pensum = float(employee[0])
        except ValueError:
            continue
        code = employee[4]
        first_name = employee[2]
        last_name = employee[3]
        entry_type = 'employee'
        scheduler_employee = {'type': entry_type, 'id': code,
                              'first_name': first_name, 'last_name': last_name, 'pensum': pensum}
        content.append(scheduler_employee)

    index = 1
    for assignment in assignments:
        confirmed_assignment = assignment[12]
        # if assignment is not confirmed or if cell has value other than TRUE/FALSE, skip this row
        if confirmed_assignment == 'FALSE' or confirmed_assignment != 'TRUE':
            continue
        assignment_semester = assignment[9]
        # if it's assignment for different semester, skip it
        if assignment_semester != semester:
            continue

        id = -1
        course_id = -1
        group_type = assignment[2].lower()
        assignment_multiple_teachers = assignment[-1]
        course_name = assignment[1]
        # skip if hours per week is not float castable
        try:
            hours = float(assignment[5])
        except ValueError:
            continue
        # if group type is invalid, skip
        if group_type not in groups:
            continue
        group_type = int(groups[group_type])
        code = assignment[11]
        # find proposal id of course
        try:
            proposal = Proposal.objects.filter(name=assignment[1])
            for p in proposal:
                if p.status != ProposalStatus.WITHDRAWN:
                    course_id = p.id
                    break
        except Proposal.ObjectDoesNotExist:
            course_id = -1

        # if single group is taught by few teachers, remember the index number that points to that group
        if assignment_multiple_teachers:
            if (course_name, assignment_multiple_teachers) in multiple_teachers:
                id = multiple_teachers[(
                    course_name, assignment_multiple_teachers)]
            else:
                id = index
                multiple_teachers[(
                    course_name, assignment_multiple_teachers)] = index
        else:
            id = index

        scheduler_assignment = {'type': 'course', 'semester': semester, 'course_id': course_id,
                                'course_name': course_name, 'id': id, 'group_type': group_type, 'hours': hours, 'teacher_id': code}
        content.append(scheduler_assignment)
        index += 1

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
            if not reached_courses and c['type'] != 'employee':
                # if c[0] != 'employee' and not reached_courses:
                writer.writerow([''])
                writer.writerow(
                    ['Typ', 'Semestr', 'ID kursu', 'Nazwa kursu', 'ID grupy', 'Typ grupy', 'Godziny', 'ID nauczyciela'])
                reached_courses = True
            if reached_courses:
                row = [c['type'], c['semester'], c['course_id'],
                       c['course_name'], c['id'], c['group_type'], c['hours'], c['teacher_id']]
            else:
                row = [c['type'], c['id'], c['first_name'],
                       c['last_name'], c['pensum']]
            writer.writerow(row)
        return response


def generate_scheduler_file_json(request, slug):
    return generate_scheduler_file(request, slug, 'json')


def generate_scheduler_file_csv(request, slug):
    return generate_scheduler_file(request, slug, 'csv')
