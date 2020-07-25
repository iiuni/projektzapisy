from collections import defaultdict
import csv
import os
import re
from typing import Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import HttpResponse, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
import environ

from apps.offer.plan.sheets import (
    create_sheets_service,
    read_assignments_sheet,
    read_employees_sheet,
    update_employees_sheet,
    update_plan_proposal_sheet,
    update_voting_results_sheet,
)
from apps.offer.plan.utils import (
    AssignmentsViewSummary,
    CourseGroupTypeSummary,
    TeacherInfo,
    get_last_years,
    get_votes,
    propose,
    sort_subject_groups_by_type,
    suggest_teachers,
)
from apps.offer.vote.models.system_state import SystemState
from apps.users.decorators import employee_required

env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, os.pardir, 'env', '.env'))
VOTING_RESULTS_SPREADSHEET_ID = env('VOTING_RESULTS_SPREADSHEET_ID')
CLASS_ASSIGNMENT_SPREADSHEET_ID = env('CLASS_ASSIGNMENT_SPREADSHEET_ID')


@employee_required
def plan_view(request):
    """Displays assignments and pensa based on data from spreadsheets."""
    year = SystemState.get_current_state().year
    assignments_spreadsheet = create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID)
    teachers = read_employees_sheet(assignments_spreadsheet)
    assignments_from_sheet = read_assignments_sheet(assignments_spreadsheet)

    courses: Dict[str, AssignmentsViewSummary] = {'z': {}, 'l': {}}

    # The counters will count total hours per group type.
    stats = {'z': defaultdict(float), 'l': defaultdict(float)}

    if not teachers or not assignments_from_sheet:
        return render(request, 'plan/view-plan.html', {'year': year})

    hours_global = defaultdict(float)
    pensum_global = sum(e['pensum'] for e in teachers.values())
    for assignment in assignments_from_sheet:
        if not assignment.confirmed:
            continue
        if assignment.name not in courses[assignment.semester]:
            courses[assignment.semester][assignment.name] = {}
        if assignment.group_type not in courses[assignment.semester][assignment.name]:
            courses[assignment.semester][assignment.name][
                assignment.group_type] = CourseGroupTypeSummary(hours=0, teachers=set())
        courses[assignment.semester][assignment.name][
            assignment.group_type]['hours'] = assignment.hours_semester
        courses[assignment.semester][assignment.name][assignment.group_type]['teachers'].add(
            TeacherInfo(username=assignment.teacher_username, name=assignment.teacher))
        key = 'courses_winter' if assignment.semester == 'z' else 'courses_summer'
        teachers[assignment.teacher_username][key].append(assignment)
        stats[assignment.semester][
            assignment.group_type] += assignment.hours_semester / assignment.multiple_teachers
        hours_global[
            assignment.semester] += assignment.hours_semester / assignment.multiple_teachers

    context = {
        'year': year,
        'courses': courses,
        'teachers': teachers,
        'hours_total': hours_global['z'] + hours_global['l'],
        'hours': hours_global,
        'pensum': pensum_global,
        'stats_z': dict(stats['z']),
        'stats_l': dict(stats['l']),
    }
    return render(request, 'plan/view-plan.html', context)


@staff_member_required
def plan_creator(request):
    """Displays the 'assignments creator' view.

    The main logic of this function is devoted to suggesting which proposals
    should be picked.
    """
    courses_proposal = get_votes(get_last_years(3))
    assignments = read_assignments_sheet(create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID))
    courses_in_assignments_sheet = set(a.name for a in assignments)

    courses = []

    if not assignments:
        for key, value in courses_proposal.items():
            # First value is the name of course
            # Second is name for the input
            # Third value is the semester when the course is planned to be
            # Fourth value says if this course is proposed
            name = f'asgn-{value.proposal.pk}-{value.semester}'
            courses.append([key, name, value.semester, propose(value)])
    else:
        for key, value in courses_proposal.items():
            checked = key in courses_in_assignments_sheet

            name = f'asgn-{value.proposal.pk}-{value.semester}'
            courses.append([key, name, value.semester, checked])

    context = {
        'courses_proposal': courses,
        'voting_results_sheet_id': VOTING_RESULTS_SPREADSHEET_ID,
        'class_assignment_sheet_id': CLASS_ASSIGNMENT_SPREADSHEET_ID,
    }
    return render(request, 'plan/create-plan.html', context)


@require_POST
@staff_member_required
def create_assignments_sheet(request):
    """Generates assignments and employees sheets for picked courses."""
    regex = re.compile(r'asgn-(?P<proposal_id>\d+)-(?P<semester>[zl])')
    sheet = create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID)

    picked_courses = {}
    for course in request.POST:
        # Filter out fields other than courses.
        match = regex.fullmatch(course)
        if not match:
            continue
        picked_courses[int(match.group('proposal_id'))] = match.group('semester')

    suggested_groups = suggest_teachers(picked_courses)
    suggested_groups = sort_subject_groups_by_type(suggested_groups)

    update_plan_proposal_sheet(sheet, suggested_groups)

    teachers = set(g['teacher_username'] for g in suggested_groups)
    update_employees_sheet(sheet, teachers)
    return redirect(reverse('plan-creator'))


@staff_member_required
def create_voting_sheet(request):
    """Prepares the voting sheet."""
    years = get_last_years(3)
    voting = get_votes(years)
    sheet = create_sheets_service(VOTING_RESULTS_SPREADSHEET_ID)
    update_voting_results_sheet(sheet, voting, years)
    return redirect(reverse('plan-creator'))


@staff_member_required
def generate_scheduler_file(request, semester, fmt):
    """Creates a file for scheduler system to use.

    Generates a json file used by scheduler or puts the very same data in csv
    file, depending on format argument. Data comes from both employees and
    assignments Google sheets.

    Args:
        slug: represents semester, 'lato' for summer, 'zima' for winter.
        format: format of requested file, either 'csv' or 'json'.

    Returns:
        File in the desired format in a response.
    """
    if semester not in ['z', 'l']:
        messages.error(f"Niepoprawny semestr: '{ semester }'")
        redirect('plan-creator')
    if fmt not in ['csv', 'json']:
        messages.error(f"Niepoprawny format: '{ fmt }'")
    current_year = SystemState.get_current_state().year
    assignments_spreadsheet = create_sheets_service(CLASS_ASSIGNMENT_SPREADSHEET_ID)
    teachers = read_employees_sheet(assignments_spreadsheet)
    assignments = read_assignments_sheet(assignments_spreadsheet)

    content = []
    multiple_teachers = {}

    for employee in teachers.values():
        scheduler_employee = {
            'type': 'employee',
            'id': employee['username'],
            'first_name': employee['first_name'],
            'last_name': employee['last_name'],
            'pensum': employee['pensum'],
        }
        content.append(scheduler_employee)

    index = 1
    for assignment in assignments:
        if not assignment.confirmed:
            continue
        if assignment.semester != semester:
            continue
        # If single group is taught by several teachers, remember the index number
        # that points to that group.
        if assignment.multiple_teachers_id:
            if (assignment.proposal_id, assignment.multiple_teachers_id) in multiple_teachers:
                id = multiple_teachers[(assignment.proposal_id, assignment.multiple_teachers_id)]
            else:
                id = index
                multiple_teachers[(assignment.proposal_id, assignment.multiple_teachers_id)] = index
        else:
            id = index

        scheduler_assignment = {
            'type': 'course',
            'semester': semester,
            'course_id': assignment.proposal_id,
            'course_name': assignment.name,
            'id': id,
            'group_type': assignment.group_type_short,
            'hours': assignment.hours_weekly,
            'teacher_id': assignment.teacher_username
        }
        content.append(scheduler_assignment)
        index += 1

    if fmt == 'json':
        response = JsonResponse(content, safe=False)
        response[
            'Content-Disposition'] = f'attachment; filename=przydzial_{semester}_{str(current_year)}.json'
        return response
    elif fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = f'attachment; filename=przydzial_{semester}_{str(current_year)}.csv'
        writer = csv.writer(response, delimiter="|")
        writer.writerow(['Typ', 'ID', 'Imię', 'Nazwisko', 'Pensum'])
        reached_courses = False
        for c in content:
            if not reached_courses and c['type'] != 'employee':
                # if c[0] != 'employee' and not reached_courses:
                writer.writerow([])
                writer.writerow([
                    'Typ', 'Semestr', 'ID kursu', 'Nazwa kursu', 'ID grupy', 'Typ grupy', 'Godziny',
                    'ID nauczyciela'
                ])
                reached_courses = True
            if reached_courses:
                row = [
                    c['type'], c['semester'], c['course_id'], c['course_name'], c['id'],
                    c['group_type'], c['hours'], c['teacher_id']
                ]
            else:
                row = [c['type'], c['id'], c['first_name'], c['last_name'], c['pensum']]
            writer.writerow(row)
        return response
