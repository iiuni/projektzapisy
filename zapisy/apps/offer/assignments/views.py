import csv
import re
from collections import defaultdict
from operator import attrgetter
from typing import Dict

from more_itertools import flatten

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import HttpResponse, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.offer.proposal.models import Proposal, ProposalStatus, SemesterChoices
from apps.offer.vote.models.system_state import SystemState
from apps.users.decorators import employee_required
from apps.users.models import Employee

from .sheets import (read_assignments_sheet, read_courses_sheet,
                     read_employees_sheet, read_opening_recommendations,
                     update_employees_sheet, update_assignments_sheet,
                     update_courses_sheet, update_voting_results_sheet,
                     voting_sheet_or_none, assignments_sheet_or_none,
                     VOTING_RESULTS_SPREADSHEET_ID, CLASS_ASSIGNMENT_SPREADSHEET_ID)
from .utils import (AssignmentsCourseInfo, AssignmentsViewSummary, CourseGroupTypeSummary, SingleCourseData,
                    EmployeeData, ProcessedAssignment, TeacherInfo, get_last_years, get_votes, suggest_teachers)


@employee_required
def plan_view(request):
    """Displays assignments and pensa based on data from spreadsheets."""
    year = SystemState.get_current_state().year
    try:
        assignments_sheet = assignments_sheet_or_none(request)
        assert assignments_sheet is not None
        teachers = read_employees_sheet(assignments_sheet)
        assignments_from_sheet = list(filter(lambda a: a.confirmed, read_assignments_sheet(assignments_sheet)))
    except (KeyError, ValueError) as error:
        messages.error(request, error)
        return render(request, 'assignments/view.html', {'year': year})
    except AssertionError:
        return render(request, 'assignments/view.html', {'year': year})

    courses: Dict[str, AssignmentsViewSummary] = {'z': {}, 'l': {}}

    # The counters will count total hours per group type.
    stats = {'z': defaultdict(float), 'l': defaultdict(float)}

    if not teachers or not assignments_from_sheet:
        return render(request, 'assignments/view.html', {'year': year})

    hours_global = defaultdict(float)
    pensum_global = sum(e.pensum for e in teachers.values())
    for assignment in assignments_from_sheet:
        semester, name, group_type = assignment.semester, assignment.name, assignment.group_type
        if name not in courses[semester]:
            courses[semester][name] = {}
        # Per-group type assignments for a single course.
        assignments_course_info: AssignmentsCourseInfo = courses[semester][name]
        if group_type not in assignments_course_info:
            assignments_course_info[group_type] = CourseGroupTypeSummary(
                hours=assignment.hours_semester, teachers={})
        if assignment.teacher_username not in teachers:
            messages.warning(
                request, f"Użytkownik <strong>{assignment.teacher_username}</strong> "
                "nie występuje w arkuszu <em>Pracownicy</em>. Przydział został pominięty.")
            continue
        teacher = teachers[assignment.teacher_username]
        teacher_info = TeacherInfo(username=assignment.teacher_username,
                                   name=f"{teacher.first_name} {teacher.last_name}")
        # We do not use a defaultdict or Counter because they conflict with django templates,
        # see https://docs.djangoproject.com/en/3.2/ref/templates/language/#template-variables
        count = assignments_course_info[group_type].teachers.get(teacher_info, 0)
        assignments_course_info[group_type].teachers[teacher_info] = count + 1
        processed_assignment = ProcessedAssignment(assignment)
        stats[semester][group_type] += processed_assignment.hours_to_pensum
        hours_global[semester] += processed_assignment.hours_to_pensum
        key = 'courses_winter' if assignment.semester == 'z' else 'courses_summer'
        getattr(teacher, key).append(processed_assignment)

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
    return render(request, 'assignments/view.html', context)


@staff_member_required
def assignments_wizard(request):
    """Displays the 'assignments creator' view.

    The main logic of this function is devoted to suggesting which proposals
    should be picked.
    """
    proposals = Proposal.objects.filter(status=ProposalStatus.IN_VOTE).order_by('name')
    try:
        assignments = []
        assignments_sheet = assignments_sheet_or_none(request)
        if assignments_sheet is not None:
            assignments = list(read_assignments_sheet(assignments_sheet))
    except (KeyError, ValueError) as error:
        messages.error(request, error)

    if assignments:
        picks = set(a.proposal_id for a in assignments)
    else:
        voting_spreadsheet = voting_sheet_or_none(request)
        if voting_spreadsheet is None:
            picks = set()
        else:
            picks = read_opening_recommendations(voting_spreadsheet)

    courses = []
    for proposal in proposals:
        checked = proposal.pk in picks
        # First value is the name of course
        # Second is name for the input
        # Third value is the semester when the course is planned to be
        # Fourth value says if this course is proposed
        if proposal.semester == SemesterChoices.UNASSIGNED:
            for apx, s in [('zima', 'z'), ('lato', 'l')]:
                name = f'asgn-{proposal.pk}-{s}'
                courses.append([f"{proposal.name} ({apx})", name, s, checked])
        else:
            name = f'asgn-{proposal.pk}-{proposal.semester}'
            courses.append([proposal.name, name, proposal.semester, checked])

    context = {
        'courses_proposal': courses,
        'voting_results_sheet_id': VOTING_RESULTS_SPREADSHEET_ID,
        'class_assignment_sheet_id': CLASS_ASSIGNMENT_SPREADSHEET_ID,
    }
    return render(request, 'assignments/wizard.html', context)


@require_POST
@staff_member_required
def create_assignments_sheet(request):
    """Generates assignments and employees sheets for picked courses.

    Makes sure that modifications made to the assignments sheet so far are not
    overridden.
    """
    try:
        assignments_sheet = assignments_sheet_or_none(request)
        assert assignments_sheet is not None
        current_assignments = defaultdict(list)
        for assignment in read_assignments_sheet(assignments_sheet):
            current_assignments[(assignment.proposal_id, assignment.semester)].append(assignment)
        teachers = read_employees_sheet(assignments_sheet)
    except (KeyError, ValueError) as error:
        messages.error(
            request, f"""<p>
            Nie udało się sparsować aktualnego arkusza i jego nowa wersja nie
            została wygenerowana w obawie przed nadpisaniem istniejących
            przydziałów. Proszę poprawić dane w arkuszu lub go opróżnić.</p>
            {error}""")
        return redirect(reverse('assignments-wizard'))
    except AssertionError:
        return redirect(reverse('assignments-wizard'))

    current_courses = dict()
    for course in read_courses_sheet(assignments_sheet):
        current_courses[(course.proposal_id, course.semester)] = course

    # Read selections from the form.
    regex = re.compile(r'asgn-(?P<proposal_id>\d+)-(?P<semester>[zl])')
    picked_courses = set()
    for course in request.POST:
        # Filter out fields other than courses.
        match = regex.fullmatch(course)
        if not match:
            continue
        picked_courses.add((int(match.group('proposal_id')), match.group('semester')))

    # Drop newly unselected assignments.
    for pick in list(current_assignments.keys()):
        if pick not in picked_courses:
            del current_assignments[pick]
    for pick in list(current_courses.keys()):
        if pick not in picked_courses:
            del current_courses[pick]

    # Filter new picks, so they don't override existing data in the sheet.
    new_picks = [pick for pick in picked_courses if pick not in current_assignments]
    missing_courses_picks = [pick for pick in picked_courses if pick not in current_courses]

    proposal_ids = set(p for (p, _) in new_picks) | set(p for (p, _) in missing_courses_picks)
    proposals = {
        p.id: p for p in Proposal.objects
        .filter(id__in=proposal_ids)
        .select_related('owner', 'owner__user', 'course_type')
        .prefetch_related('tags')
    }

    # update Assignments sheet
    try:
        suggested_groups = suggest_teachers(new_picks, proposals)
    except KeyError as error:
        messages.error(
            request, f"""<p>
            Nieznane ID propozycji przedmiotu. Nie wprowadzono zmian w arkuszach.</p>
            {error}""")
        return redirect(reverse('assignments-wizard'))
    all_groups = list(flatten(current_assignments.values())) + suggested_groups
    suggested_groups = sorted(all_groups, key=attrgetter('semester', 'name', 'group_type'))
    update_assignments_sheet(assignments_sheet, suggested_groups)

    # update Employees sheet
    new_usernames = set(
        g.teacher_username for g in suggested_groups if g.teacher_username not in teachers)
    is_external_contractor = models.Count(
        'user__groups', filter=models.Q(user__groups__name='external_contractors'))
    is_phd_student = models.Count('user__groups',
                                  filter=models.Q(user__groups__name='phd_students'))
    employees = Employee.objects.filter(
        user__username__in=new_usernames).select_related('user').annotate(
            is_external_contractor=is_external_contractor).annotate(is_phd_student=is_phd_student)
    for e in employees:
        teachers[e.user.username] = EmployeeData(
            username=e.user.username,
            first_name=e.user.first_name,
            last_name=e.user.last_name,
            status='inny' if e.is_external_contractor else 'doktorant' if e.is_phd_student else 'pracownik',
            pensum=0,
            balance=0,
            hours_winter=0,
            hours_summer=0,
            courses_winter=[],
            courses_summer=[],
        )
    teachers = sorted(teachers.values(), key=attrgetter('status', 'last_name', 'first_name'))
    update_employees_sheet(assignments_sheet, teachers)

    # update Courses sheet
    courses_data = list(current_courses.values())
    for pid, semester in missing_courses_picks:
        proposal: Proposal = proposals[pid]
        courses_data.append(
            SingleCourseData(
                proposal_id=pid,
                name=proposal.get_course_name(semester),
                course_type=proposal.course_type.name,
                tags=', '.join(map(lambda x: x[0], proposal.tags.values_list('short_name'))),
                ects=proposal.points,
                semester=semester
            )
        )
    courses_data.sort(key=attrgetter('semester', 'name'))
    update_courses_sheet(assignments_sheet, courses_data)
    return redirect(reverse('assignments-wizard')+'#step-3')


@staff_member_required
def create_voting_sheet(request):
    """Prepares the voting sheet."""
    voting_sheet = voting_sheet_or_none(request)
    if voting_sheet is None:
        return redirect(reverse('assignments-wizard'))
    years = get_last_years(3)
    voting = get_votes(years)
    update_voting_results_sheet(voting_sheet, voting, years)
    return redirect(reverse('assignments-wizard')+'#step-1')


@staff_member_required
def generate_scheduler_file(request, semester, fmt):
    """Creates a file for scheduler system to use.

    Generates a json file used by scheduler or puts the very same data in csv
    file, depending on format argument. Data comes from both employees and
    assignments Google sheets.

    Args:
        semester: represents semester, 'l' for summer, 'z' for winter.
        fmt: format of requested file, either 'csv' or 'json'.

    Returns:
        File in the desired format in a response.
    """
    if semester not in ['z', 'l']:
        messages.error(request, f"Niepoprawny semestr: '{ semester }'")
        return redirect('assignments-wizard')
    if fmt not in ['csv', 'json']:
        messages.error(request, f"Niepoprawny format: '{ fmt }'")
        return redirect('assignments-wizard')

    try:
        assignments_sheet = assignments_sheet_or_none(request)
        assert assignments_sheet is not None
        teachers = read_employees_sheet(assignments_sheet)
        assignments = list(read_assignments_sheet(assignments_sheet))
    except (KeyError, ValueError) as error:
        messages.error(request, error)
        return redirect('assignments-wizard')
    except AssertionError:
        return redirect('assignments-wizard')

    content_teachers = [{
        'type': 'employee',
        'id': employee.username,
        'first_name': employee.first_name,
        'last_name': employee.last_name,
        'pensum': employee.pensum,
    } for employee in teachers.values()]

    content_assignments = []
    multiple_teachers = {}
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
        content_assignments.append(scheduler_assignment)
        index += 1

    current_year = SystemState.get_current_state().year
    if fmt == 'json':
        response = JsonResponse(content_teachers + content_assignments, safe=False)
        response[
            'Content-Disposition'] = f'attachment; filename=przydzial_{semester}_{str(current_year)}.json'
    else:
        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = f'attachment; filename=przydzial_{semester}_{str(current_year)}.csv'
        writer = csv.DictWriter(response, fieldnames=['type', 'id', 'first_name', 'last_name', 'pensum'])
        writer.writeheader()
        writer.writerows(content_teachers)
        writer = csv.DictWriter(response,
                                fieldnames=[
                                    'type', 'semester', 'course_id', 'course_name', 'id',
                                    'group_type', 'hours', 'teacher_id'
                                ])
        writer.writeheader()
        writer.writerows(content_assignments)
    return response
