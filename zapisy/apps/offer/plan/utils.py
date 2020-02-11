import copy
import sys
from datetime import date
from functools import reduce
from operator import itemgetter
from functools import cmp_to_key
from django.db import models
from django.db.models import Avg, Count, Q, Sum, Value
from django.db.models.functions import Concat

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.group import GROUP_TYPE_CHOICES, Group
from apps.enrollment.records.models.records import Record, RecordStatus
from apps.offer.proposal.models import (Proposal, ProposalStatus,
                                        SemesterChoices)
from apps.offer.vote.models.single_vote import SingleVote, SingleVoteQuerySet
from apps.offer.vote.models.system_state import SystemState

if sys.version_info >= (3, 8):
    from typing import List, Tuple, Dict, NamedTuple, TypedDict, Optional
else:
    from typing import List, Tuple, Dict, NamedTuple, Optional
    from typing_extensions import TypedDict


class SingleYearVoteSummary(TypedDict):
    # Total of points awarded in a vote.
    total: int
    # Number of voters who awarded this course with maximum number of votes.
    count_max: int
    # Number of voters that voted for this course
    votes: int
    # Number of enrolled students. None if course was not given that year.
    enrolled: Optional[int]


class ProposalVoteSummary(NamedTuple):
    proposal: Proposal
    semester: str
    course_type: str
    # Indexed by the academic year.
    voting: Dict[str, SingleYearVoteSummary]


# Indexed by the Proposal name
VotingSummaryPerYear = Dict[str, ProposalVoteSummary]


class SingleGroupData(TypedDict):
    name: str
    semester: str
    teacher: str
    teacher_code: int
    group_type: str
    hours: int


AssigmentsSummary = List[SingleGroupData]


def propose(vote: ProposalVoteSummary):
    """A simple, heuristic function to propose, whether the course should be taught in the upcoming year."""

    current_year = SystemState.get_current_state().year
    proposal = Proposal.objects.get(id=vote.proposal)
    avg = SingleVote.objects.filter(state__year=current_year, value__gt=0).values('proposal').annotate(
        total=Sum('value')).aggregate(Avg('total'))
    previous_avg = 0
    years = 0
    percentage = 0.8

    for year, values in vote.voting.items():
        if not year == current_year:
            years += 1
            previous_avg = values['total']
    if proposal.course_type.obligatory:
        return True
    if proposal.recommended_for_first_year:
        return True
    if vote.voting[current_year]['total'] >= avg['total__avg']:
        return True
    if years > 0 and vote.voting[current_year]['total'] >= percentage * (previous_avg / years):
        return True
    return False


def get_subjects_data(subjects: List[Tuple[str, str, int]], years: List[str]) -> AssigmentsSummary:
    """Function prepares data to create a csv.

    Data returned by this function will be presented in a spreadsheet, where it will help with assigning classes. Given a course,
    it will look for previous instances of the course (taking the newest one) and copy the group assigments from it. If such
    instance does not exist, it will assign only the owner of the course.

    Args:
        subjects: list of tuples (course name, course semester, course proposal). Each tuple represents single course.
        years: list of years to look for data in.
    """

    course_data = {}

    for subject in subjects:
        course_name = subject[0]
        course_semester = subject[1]
        course_proposal = subject[2]
        course_data[course_name] = {'proposal': course_proposal, 'semester': course_semester,
                                    'instance': CourseInstance.objects.filter(semester__year__in=years, offer=course_proposal,
                                                                              semester__type=course_semester).order_by('-semester__year').first()}

    groups: AssigmentsSummary = []
    # Prepares data necessary to create csv.
    for course, data in course_data.items():
        proposal_info = data['proposal']
        semester = ''
        if course.endswith('(lato)'):
            semester = 'l'
        elif course.endswith('(zima)'):
            semester = 'z'

        semester = semester if semester else proposal_info.semester

        if data['instance']:
            previous_groups = Group.objects.filter(course=data['instance'])
            hours = {'Wykład': proposal_info.hours_lecture,
                     'Ćwiczenia': proposal_info.hours_exercise,
                     'Ćwiczenio-pracownia': proposal_info.hours_exercise_lab,
                     'Repetytorium': proposal_info.hours_recap,
                     'Seminarium': proposal_info.hours_seminar,
                     'Pracownia': proposal_info.hours_lab
                     }

            for group in previous_groups:
                course_hours = hours[group.human_readable_type(
                )] if group.human_readable_type() in hours else 0
                group_type = group.human_readable_type()
                teacher_code = group.teacher.user.username
                teacher_name = group.teacher.get_full_name()
                sgd: SingleGroupData = {'name': course, 'semester': semester, 'teacher': teacher_name,
                                        'teacher_code': teacher_code, 'group_type': group_type, 'hours': course_hours}
                groups.append(sgd)
        else:
            teacher_code = proposal_info.owner.user.username
            teacher_name = proposal_info.owner.get_full_name()
            teacher_code = proposal_info.owner.user.username

            if proposal_info.hours_lecture:
                course_hours = proposal_info.hours_lecture
                group_type = 'Wykład'
            if proposal_info.hours_exercise_lab:
                course_hours = proposal_info.hours_exercise_lab
                group_type = 'Ćwiczenio-pracownia'
            if proposal_info.hours_seminar:
                course_hours = proposal_info.hours_seminar
                group_type = 'Seminarium'
            if proposal_info.hours_exercise:
                course_hours = proposal_info.hours_exercise
                group_type = 'Ćwiczenia'
            if proposal_info.hours_lab:
                course_hours = proposal_info.hours_lab
                group_type = 'Pracownia'
            if proposal_info.hours_recap:
                course_hours = proposal_info.hours_recap
                group_type = 'Repetytorium'
            sgd: SingleGroupData = {'name': course, 'semester': semester, 'teacher': teacher_name,
                                    'teacher_code': teacher_code, 'group_type': group_type, 'hours': course_hours}
            groups.append(sgd)
    return groups


def get_last_years(n: int) -> List[str]:
    """Lists last n academic years, current included."""
    current_year = SystemState.get_current_state().year
    last_states = SystemState.objects.filter(year__lte=current_year)[:n]
    return [s.year for s in last_states]


def get_votes(years: List[str]) -> VotingSummaryPerYear:
    """ This function prepares the voting data, that'll be put in a spreadsheet. """
    max_vote_value = max(SingleVote.VALUE_CHOICES)[0]

    # Collect the information on Proposals currently in vote. Leave voting blank
    # for now.
    in_vote = Proposal.objects.filter(
        status=ProposalStatus.IN_VOTE).order_by('name').select_related('course_type')
    proposals: VotingSummaryPerYear = {}
    for p in in_vote:
        if p.semester == SemesterChoices.UNASSIGNED:
            proposals.update({
                f'{p.name} (zima)': ProposalVoteSummary(p, SemesterChoices.WINTER, p.course_type.name, {}),
                f'{p.name} (lato)': ProposalVoteSummary(p, SemesterChoices.SUMMER, p.course_type.name, {}),
            })
        else:
            proposals.update({p.name: ProposalVoteSummary(
                p, p.semester, p.course_type.name, {})})

    # Collect voting history for these proposals.
    votes = SingleVote.objects.filter(
        state__year__in=years, proposal__status=ProposalStatus.IN_VOTE).values('proposal_id', 'state__year').annotate(
            total=Sum('value'), count_max=Count('value', filter=Q(value=max_vote_value)), votes=Count('value', filter=Q(value__gt=0))).order_by('proposal_id', '-state__year')

    votes_dict = {(v['proposal_id'], v['state__year']): SingleYearVoteSummary(
        total=v['total'], count_max=v['count_max'], votes=v['votes'], enrolled=None)
        for v in votes}

    # Collect enrolment numbers.
    records = Record.objects.filter(
        status=RecordStatus.ENROLLED, group__course__offer__status=ProposalStatus.IN_VOTE).values(
            'group__course__offer_id', 'group__course__semester__year',
            'group__course__semester__type').annotate(
                # The number of distinct students enrolled into a course.
                enrolled=Count('student_id', distinct=True))
    records_summary = {(r['group__course__offer_id'], r['group__course__semester__year'],
                        r['group__course__semester__type']): r['enrolled']
                       for r in records}

    # Put all information into proposals.
    for pvs in proposals.values():
        for year in years:
            try:
                syv = copy.copy(votes_dict[(pvs.proposal.id, year)])
                syv['enrolled'] = records_summary.get(
                    (pvs.proposal.id, year, pvs.semester), None)
                pvs.voting[year] = syv
            except KeyError:
                # The proposal was not put to vote that year.
                pass
    return proposals


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

# prepares data about employee to put into html
# arg employees is data loaded from employees Google sheet


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
                    'courses_summer': []
                    }
            if value[1] == 'prac':
                staff[value[5]] = data
            elif value[1] == 'doktorant':
                phds[value[5]] = data
            else:
                others[value[5]] = data
    return staff, phds, others, pensum

# arg stats is a single row from assigments sheet
# this function extracts important data from that row, used to generate statistics


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
def sort_subject_groups_by_type(semester: AssigmentsSummary) -> AssigmentsSummary:
    """ Sorts subjects by their name and then group type. """
    return sorted(semester, key=GroupOrder)


class GroupOrder:
    def __init__(self, sgd):
        self.sgd = sgd

    def __lt__(self, other):
        if self.sgd['name'] == other.sgd['name']:
            types = {'Wykład': 1,
                     'Repetytorium': 2,
                     'Ćwiczenia': 3,
                     'Ćwiczenio-pracownia': 4,
                     'Pracownia': 5,
                     'Seminarium': 6
                     }
            return types[self.sgd['group_type']] < types[other.sgd['group_type']]
        return self.sgd['name'] < other.sgd['name']
