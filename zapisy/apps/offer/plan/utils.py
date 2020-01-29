from datetime import date
from django.db import models
from django.db.models import Sum, Q, Count, Value, Avg
from django.db.models.functions import Concat

from apps.offer.vote.models.single_vote import SingleVote, SingleVoteQuerySet
from apps.offer.vote.models.system_state import SystemState
from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.enrollment.records.models.records import Record, RecordStatus
from apps.enrollment.courses.models.group import Group, GROUP_TYPE_CHOICES
from functools import reduce
from typing import List, Tuple


def propose(vote):
    # A simple function to propose, whether the course should be taught in upcoming year.
    # As an argument, it takes a single dictionary entry from get_votes function.
    current_year = SystemState.get_current_state().year
    proposal = Proposal.objects.get(id=vote[current_year]['proposal'])
    avg = SingleVote.objects.filter(state__year=current_year, value__gt=0).values('proposal').annotate(
        total=Sum('value')).aggregate(Avg('total'))
    previous_avg = 0
    years = 0
    percentage = 0.8

    for year, values in vote.items():
        if not year == current_year:
            years += 1
            previous_avg = values['total']
    if proposal.course_type.obligatory:
        return True
    if proposal.recommended_for_first_year:
        return True
    if vote[current_year]['total'] >= avg['total__avg']:
        return True
    if years > 0 and vote[current_year]['total'] >= percentage * (previous_avg / years):
        return True
    return False


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
        if data['instance']:
            previous_groups = Group.objects.filter(course=data['instance'][0])
            for group in previous_groups:
                semester = ''
                if course.endswith('(lato)'):
                    semester = 'l'
                elif course.endswith('(zima)'):
                    semester = 'z'

                hours = {'Wykład': proposal_info.hours_lecture,
                         'Ćwiczenia': proposal_info.hours_exercise,
                         'Ćwiczenio-pracownia': proposal_info.hours_exercise_lab,
                         'Repetytorium': proposal_info.hours_recap,
                         'Seminarium': proposal_info.hours_seminar,
                         'Pracownia': proposal_info.hours_lab
                         }

                course_info = [('course', course),
                               ('semester', semester if semester else proposal_info.semester),
                               ('teacher', group.teacher.get_full_name()),
                               ('code', group.teacher.user.username),
                               ('type', group.human_readable_type(
                               ) if group.human_readable_type() != 'Projekt' else 'Pracownia'),
                               ('hours', hours[group.human_readable_type()]) if group.human_readable_type() in hours else ('hours', 0)]
                groups.append(course_info)
        else:
            semester = ''
            if course.endswith('(lato)'):
                semester = 'l'
            elif course.endswith('(zima)'):
                semester = 'z'
            course_info = [('course', course), ('semester', semester if semester else proposal_info.semester),
                           ('teacher', proposal_info.owner.get_full_name()), ('code', proposal_info.owner.user.username)]
            if proposal_info.hours_lecture:
                groups.append(
                    course_info + [('type', 'Wykład'), ('hours', proposal_info.hours_lecture)])
            if proposal_info.hours_exercise_lab:
                groups.append(
                    course_info + [('type', 'Ćwiczenio-pracownia'), ('hours', proposal_info.hours_exercise_lab)])
            if proposal_info.hours_seminar:
                groups.append(
                    course_info + [('type', 'Seminarium'), ('hours', proposal_info.hours_seminar)])
            if proposal_info.hours_exercise:
                groups.append(
                    course_info + [('type', 'Ćwiczenia'), ('hours', proposal_info.hours_exercise)])
            if proposal_info.hours_lab:
                groups.append(
                    course_info + [('type', 'Pracownia'), ('hours', proposal_info.hours_lab)])
            if proposal_info.hours_recap:
                groups.append(
                    course_info + [('type', 'Repetytorium'), ('hours', proposal_info.hours_recap)])
    return groups


def get_votes(years: int):
    # years argument specifies how many years back we want to collect data from.
    # Return value: Dict[str, Dict[str, Dict[...]]]
    # Each dictionary entry describes a various data about course in a single year, whether it was already taught or is still
    # voted upon.
    # First dictionary is indexed by course's name, and each entry is another dictionary.
    # Second dictionary is indexed by course's year, and each entry is dictionary with such fields:
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
    # | 'name'                           | string | true course name

    votes = SingleVote.objects.filter(
        reduce(lambda x, y: x | y, [Q(state__year=year.year) for year in states])).values(
            'proposal__name', 'state__year', 'proposal__semester', 'proposal', 'proposal__course_type__name').annotate(
                total=Sum('value'), count_max=Count('value', filter=Q(value=max_vote_value)),
                votes=Count('proposal__name'),
                teacher=Concat('proposal__owner__user__first_name', Value(' '),
                               'proposal__owner__user__last_name')).order_by('proposal__name', '-state__year')

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
                'type': vote['proposal__course_type__name'], 'teacher': vote['teacher'],
                'proposal': vote['proposal'], 'name': vote['proposal__name']}

        if vote['proposal__semester'] == 'u':
            data['semester'] = 'l'
            courses_data[vote['proposal__name'] +
                         ' (lato)'][vote['state__year']] = dict(data)

            data['semester'] = 'z'
            courses_data[vote['proposal__name'] +
                         ' (zima)'][vote['state__year']] = dict(data)
        else:
            data['semester'] = vote['proposal__semester']
            courses_data[vote['proposal__name']][
                vote['state__year']] = dict(data)

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


# prepares assignment data to be displayed in template
# return type is a list of records boilerplate(look up)
def prepare_assignments_data(data: List[List]):
    final = []
    length = len(data)
    lp = data[0][0]
    # boilerplate for record, a list of those is our return type
    record = {
        'id': 0,
        'course': '',
        'w': {
            'weekly': '',
            'teachers': []
        },
        'rep': {
            'weekly': '',
            'teachers': []
        },
        'ćw': {
            'weekly': '',
            'teachers': []
        },
        'prac': {
            'weekly': '',
            'teachers': []
        },
        'ćw_prac': {
            'weekly': '',
            'teachers': []
        },
        'sem': {
            'weekly': '',
            'teachers': []
        },
        'admin': {
            'weekly': '',
            'teachers': []
        }
    }
    for value in data:
        if value[0] == lp:
            if value[-2] == 'FALSE':
                continue

            record = process_value(record, value)
            # check if it's last elem in list
            if value == data[length - 1]:
                record = clean_up(record)
                final.append(record)
        else:
            lp += 1
            if record['course'] != '':
                record = clean_up(record)
                final.append(record)
                record = {
                    'course': '',
                    'id': 0,
                    'w': {
                        'weekly': '',
                        'teachers': []
                    },
                    'rep': {
                        'weekly': '',
                        'teachers': []
                    },
                    'ćw': {
                        'weekly': '',
                        'teachers': []
                    },
                    'prac': {
                        'weekly': '',
                        'teachers': []
                    },
                    'ćw_prac': {
                        'weekly': '',
                        'teachers': []
                    },
                    'sem': {
                        'weekly': '',
                        'teachers': []
                    },
                    'admin': {
                        'weekly': '',
                        'teachers': []
                    }
                }
            if value[-2] == 'FALSE':
                continue

            record = process_value(record, value)
            if value == data[length - 1]:
                record = clean_up(record)
                final.append(record)
    return final


# this function interprets a single line form sheet
# return type is a record boilerplate(look up)
def process_value(record: dict, value: List):
    record['course'] = value[1]
    record['id'] = value[0]
    if value[3] == 'w':
        record = process_data_row(record, value, value[3])
    elif value[3] == 'rep':
        record = process_data_row(record, value, value[3])
    elif value[3] == 'ćw':
        record = process_data_row(record, value, value[3])
    elif value[3] == 'prac':
        record = process_data_row(record, value, value[3])
    elif value[3] == 'ćw+prac':
        record = process_data_row(record, value, 'ćw_prac')
    elif value[3] == 'sem':
        record = process_data_row(record, value, value[3])
    elif value[3] == 'admin':
        record = process_data_row(record, value, value[3])

    return record


# return type is a record boilerplate(look up)
def process_data_row(record: dict, value: List, class_type: str):
    record[class_type]['weekly'] = value[5]
    record[class_type]['teachers'].append({
        'name': value[-3],
        'code': value[-2],
    })
    return record


# this function removes empty elements from dict
# return type is a record boilerplate(look up) without some values
def clean_up(record: dict):
    if record['w']['weekly'] == '':
        record.pop('w')
    if record['rep']['weekly'] == '':
        record.pop('rep')
    if record['ćw']['weekly'] == '':
        record.pop('ćw')
    if record['prac']['weekly'] == '':
        record.pop('prac')
    if record['ćw_prac']['weekly'] == '':
        record.pop('ćw_prac')
    if record['sem']['weekly'] == '':
        record.pop('sem')
    if record['admin']['weekly'] == '':
        record.pop('admin')

    return record


def prepare_employees_data(employees: List):
    staff = {}
    phds = {}
    others = {}
    pensum = 0
    for value in employees:
        if value[4] != '' and value[0] != 'pensum':
            pensum += int(value[0])

            data = {'name': value[2] + ' ' + value[3],
                    'pensum': value[0],
                    'balance': float(value[13]) if value[13] else float(value[11]),
                    'weekly_winter': 0,
                    'weekly_summer': 0,
                    'courses_winter': [],
                    'courses_summer': [],
                    'id': value[5]
                    }
            if value[1] == 'prac':
                staff[value[5]] = data
            elif value[1] == 'doktorant':
                phds[value[5]] = data
            else:
                others[value[5]] = data
    return staff, phds, others, pensum


def make_stats_record(stats: List):
    types = {'w': 'wykład',
             'ćw': 'ćwiczenia',
             'ćw+prac': 'ćwiczenia+pracownia',
             'prac': 'pracownia',
             'sem': 'seminarium',
             'rep': 'repetytorium',
             'admin': 'sekretarz'
             }
    return types[stats[3]], float(stats[7])


# this function divides semester into subject's groups
# and sorts them by type(wyk, rep, ćw, prac, itd...)
# function returns a List[List]
def sort_subject_groups_by_type(semester: List[List]):
    sorted_semester = []

    group = []
    last_name = semester[0][0][1]
    i = 1
    for val in semester:
        if val[0][1] == last_name:
            group.append(val)
            if i == len(semester):
                group = sort_by_type(group)
                sorted_semester += group
        else:
            last_name = val[0][1]
            group = sort_by_type(group)
            sorted_semester += group
            group = [val]
            if i == len(semester):
                sorted_semester += group
        i += 1

    return sorted_semester


# this function sorts subject's groups by type
# function returns a List[List]
def sort_by_type(group: List[List]):
    sorted_group = []
    main_type = ['Wykład', 'Repetytorium', 'Ćwiczenia', 'Pracownia']

    for item in group:
        if item[4][1] == main_type[0]:
            sorted_group.append(item)

    for item in group:
        if item[4][1] == main_type[1]:
            sorted_group.append(item)

    for item in group:
        if item[4][1] == main_type[2]:
            sorted_group.append(item)

    for item in group:
        if item[4][1] == main_type[3]:
            sorted_group.append(item)

    for item in group:
        if item[4][1] not in main_type:
            sorted_group.append(item)

    return sorted_group
