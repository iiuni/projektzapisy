from datetime import date
from django.db import models
from django.db.models import Sum, Q, Count, Value
from django.db.models.functions import Concat

from apps.offer.vote.models.single_vote import SingleVote, SingleVoteQuerySet
from apps.offer.vote.models.system_state import SystemState
from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.enrollment.records.models.records import Record, RecordStatus
from apps.enrollment.courses.models.group import Group

from functools import reduce
from typing import List, Tuple

#import pygsheets


def get_subjects_data(subjects: List[Tuple[str, str, int]], years: int):
    # Function prepares data to create a necessary csv to assign classes. Given a course, it will look for previous instances
    # of the course (taking the newest one), and copy the group assigments from it. If such instance does not exist, it will
    # assign only the owner of the course.
    # Arguments:
    #   subjects: list of tuples (course name, course semester, course proposal id). Each course represented
    #             by course name will be present in return value.
    #   years: tells the function how many years back should it look for previous instances of
    #          the course to copy data from.
    # Return value: list of list of pairs. Each entry is a single group. Each pair is of (name, value) format:
    # | name      | desc                                   |
    # | course    | course name                            |
    # | semester  | either z or l                          |
    # | teacher   | group teacher                          |
    # | code      | teacher code                           |
    # | type      | group type (lecture, lab etc.)         |
    # | hours     | hours allocated for this type of class |

    course_data = {}
    states = get_year_list(years)

    for subject in subjects:
        course_data[subject[0]] = {'id': subject[2], 'semester': subject[1],
                                   'instance': CourseInstance.objects.filter(
            reduce(lambda x, y: x | y, [Q(semester__year=year.year) for year in states]), offer=subject[2],
            semester__type=subject[1]).order_by('-semester__year')}

    groups = []
    # Prepares data necessary to create csv.
    for course, data in course_data.items():
        proposal_info = Proposal.objects.get(id=data['id'])
        course_type = proposal_info.course_type
        if data['instance']:
            previous_groups = Group.objects.filter(course=data['instance'][0])
            for group in previous_groups:
                hours = {'Wykład': proposal_info.hours_lecture,
                         'Ćwiczenia': proposal_info.hours_exercise,
                         'Ćwiczenio-pracownia': proposal_info.hours_exercise_lab,
                         'Repetytorium': proposal_info.hours_recap,
                         'Seminarium': proposal_info.hours_seminar,
                         'Pracownia': proposal_info.hours_lab,
                         'Projekt': None}

                course_info = [('course', course),
                               ('semester', proposal_info.semester),
                               ('teacher', group.teacher.get_full_name()),
                               ('code', group.teacher.user.username), ('type', group.human_readable_type()), ('hours', hours[group.human_readable_type()])]
                groups.append(course_info)
        else:
            course_info = [('course', course), ('semester', proposal_info.semester),
                           ('teacher', proposal_info.owner.get_full_name()), ('code', proposal_info.owner.user.username)]
            if course_type.have_lecture:
                groups.append(
                    course_info + [('type', 'Wykład'), ('hours', proposal_info.hours_lecture)])
            if course_type.have_tutorial_lab:
                groups.append(
                    course_info + [('type', 'Ćwiczenio-pracownia'), ('hours', proposal_info.hours_exercise_lab)])
            if course_type.have_seminar:
                groups.append(
                    course_info + [('type', 'Seminarium'), ('hours', proposal_info.hours_seminar)])
            if course_type.have_tutorial:
                groups.append(
                    course_info + [('type', 'Ćwiczenia'), ('hours', proposal_info.hours_exercise)])
            if course_type.have_lab:
                groups.append(
                    course_info + [('type', 'Pracownia'), ('hours', proposal_info.hours_lab)])
            if course_type.have_review_lecture:
                groups.append(
                    course_info + [('type', 'Repetytorium'), ('hours', proposal_info.hours_recap)])
            if course_type.have_project:
                groups.append(
                    course_info + [('type', 'Projekt'), ('hours', None)])
    return groups


def get_votes(years: int):
    # years argument specifies how many years back we want to collect data from.
    # Return value: Dict[str, Dict[str, Dict[...]]]
    # Each dictionary entry describes a various data about course in a single year, whether it was already taught or is still
    # voted upon.
    # This dictionary is indexed by course's name, and each entry is another dictionary.
    # That dictionary is indexed by course's year, and each entry is dictionary with such fields:
    # | field name                       | type   | desc                                                                       |
    # --------------------------------------------------------------------------------------------------------------------------
    # | 'semester'                       | string | course's semester (either z, meaning winter, or l, meaning summer)         |
    # | 'proposal'                       | int    | course's proposal id (see proposal model)                                  |
    # | 'type'                           | string | course's type                                                              |
    # | 'total'                          | int    | number of points gathered by course across all votes in a single year      |
    # | 'count_max'                      | int    | number of votes for this proposal with value = max_vote_value              |
    # | 'votes'                          | int    | number of students that voted for this course                              |
    # | 'teacher'                        | string | lecturer/teacher of this course                                            |
    # | 'enrolled                        | int    | sum of enrolled students. If it's proposal for current year, field is None |

    states_all = SystemState.objects.all().order_by('-year')
    current_year = SystemState.get_current_state().year
    states = []

    for (i, state) in enumerate(states_all):
        if i >= years:
            break
        states.append(state)
    max_vote_value = max(SingleVote.VALUE_CHOICES)[0]

    # Creates set of dictionaries with various data about courses put on the vote.
    # Each dictionary is described by those fields:
    # | field name                       | type   | desc                                                                       |
    # --------------------------------------------------------------------------------------------------------------------------
    # | 'proposal__name'                 | string | course's name                                                              |
    # | 'state__year'                    | string | year in which this instance of the course was put on the vote              |
    # | 'proposal__semester'             | string | course's semester (either z, l, u)                                         |
    # | 'proposal'                       | int    | course's proposal id (see proposal model)                                  |
    # | 'proposal__course_type__name'    | string | course's type                                                              |
    # | 'total'                          | int    | number of points gathered by course across all votes in a single year      |
    # | 'count_max'                      | int    | number of votes for this proposal with value = max_vote_value              |
    # | 'votes'                          | int    | number of students that voted for this course                              |
    # | 'teacher'                        | string | lecturer/teacher of this course                                            |

    votes = SingleVote.objects.filter(
        reduce(lambda x, y: x | y, [Q(state__year=year.year) for year in states])).values(
            'proposal__name', 'state__year', 'proposal__semester', 'proposal', 'proposal__course_type__name').annotate(
                total=Sum('value'), count_max=Count('value', filter=Q(value=max_vote_value)),
                votes=Count('proposal__name'),
                teacher=Concat('proposal__owner__user__first_name', Value(' '), 'proposal__owner__user__last_name')).order_by('proposal__name', '-state__year')

    courses_data = {}
    # Get rid of courses that existed in previous years, but weren't in this year's vote
    for vote in votes:
        if vote['proposal__name'] not in courses_data:
            if current_year == vote['state__year']:
                if vote['proposal__semester'] == 'u':
                    if vote['proposal__name'] + ' (lato)' not in courses_data:
                        courses_data[vote['proposal__name'] + ' (lato)'] = {}
                    if vote['proposal__name'] + ' (zima)' not in courses_data:
                        courses_data[vote['proposal__name'] + ' (zima)'] = {}
                else:
                    courses_data[vote['proposal__name']] = {}
            else:
                continue
        data = {'total': vote['total'], 'votes': vote['votes'], 'count_max': vote['count_max'],
                'type': vote['proposal__course_type__name'], 'teacher': vote['teacher'], 'proposal': vote['proposal'], 'name': vote['proposal__name']}

        if vote['proposal__semester'] == 'u':
            data['semester'] = 'l'
            courses_data[vote['proposal__name'] +
                         ' (lato)'][vote['state__year']] = dict(data)

            data['semester'] = 'z'
            courses_data[vote['proposal__name'] +
                         ' (zima)'][vote['state__year']] = dict(data)
        else:
            data['semester'] = vote['proposal__semester']
            courses_data[vote['proposal__name']
                         ][vote['state__year']] = dict(data)

    # Rearrange data and if course existed in previous years count how many students were enrolled
    for course in courses_data.values():
        for semester, data in course.items():
            instance = CourseInstance.objects.filter(
                offer=data['proposal'], semester__year=semester, semester__type=data['semester'])
            if not instance:
                data['enrolled'] = None
            else:
                data['enrolled'] = count_students_in_course(instance)
    return courses_data


def count_students_in_groups(groups: List[Group]) -> int:
    # Counts students in groups
    students = Record.objects.filter(
        reduce(lambda x, y: x | y, [Q(group=group)for group in groups]), status=RecordStatus.ENROLLED).distinct().count()
    return students


def count_students_in_course(courses: CourseInstance) -> int:
    # Counts students enrolled for a course
    enrolled = 0
    for course in courses:
        groups = Group.objects.filter(
            course=course, type=Group.GROUP_TYPE_LECTURE)
        if groups:
            enrolled += count_students_in_groups(groups)
        else:
            groups = Group.objects.filter(course=course)
            enrolled += count_students_in_groups(groups)
    return enrolled


def get_year_list(years):
    states_all = SystemState.objects.all().order_by('-year')
    states = []

    for (i, state) in enumerate(states_all):
        if i >= years:
            break
        states.append(state)
    return states


""" Not ready yet
def votes_to_sheets(votes, states):
    file = open('text.txt', 'w')
    for vote in votes:
        file.write(str(votes[vote]) + '\n')
    file.close()
    gc = pygsheets.authorize(service_file='creds.json')

    try:
        sheet = gc.open('ZapisyTest').sheet1
    except pygsheets.SpreadsheetNotFound:
        sheet = gc.create('ZapisyTest').sheet1

    sheet.clear()
    row_head = [["Nazwa przedmiotu"]]
    row_head2 = [["Głosy"], ["Głosujący"],
                 ["Za 3"], ["Typ"], ["Semestr"], ["Wykładowca"], ["Zapisani"], [""]]

    width = len(states) * len(row_head2) + len(row_head)

    for (i, state) in enumerate(states):
        sheet.update_value((1, i*len(row_head2) + 2), state.year)
        row_head.extend(row_head2)

    sheet.update_col(1, row_head, 1)

    current_year = SystemState.get_current_state().year
    row_course = []
    for key, value in votes.items():
        current_row = []
        current_row.append(key)
        for state in states:
            year = state.year
            if year in value:
                for k2, v2 in value[year].items():
                    if k2 == 'enrolled':
                        current_row.append(str(value[year][k2]))
                    elif k2 != 'proposal' and k2 != 'name':
                        current_row.append(value[year][k2])
            else:
                current_row.extend(["", "", "", "", "", "", ""])
            current_row.append("")
        row_course.append(current_row)
    length = len(row_course)
    sheet.update_values(crange='A3:Y' + str(length + 2),
                        values=row_course)
"""
