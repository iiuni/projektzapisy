from collections import defaultdict
import collections
import copy
from operator import itemgetter
import sys

from django.db.models import Avg, Count, Q, Sum, Max

from apps.enrollment.courses.models.group import Group, GroupType
from apps.enrollment.records.models.records import Record, RecordStatus
from apps.offer.proposal.models import Proposal, ProposalStatus, SemesterChoices
from apps.offer.vote.models.single_vote import SingleVote
from apps.offer.vote.models.system_state import SystemState

if sys.version_info >= (3, 8):
    from typing import List, Dict, NamedTuple, TypedDict, Optional, Set
else:
    from typing import List, Dict, NamedTuple, Optional, Set
    from typing_extensions import TypedDict


class SingleAssignmentData(NamedTuple):
    """Represents a row in the Assignments sheet."""
    name: str
    index: int
    # full name, as in GROUP_TYPES
    group_type: str
    group_type_short: str
    hours_weekly: int
    hours_semester: float
    # l (summer) or z (winter)
    semester: str
    teacher: str
    teacher_username: str
    confirmed: bool
    # How many teachers assigned to the same group.
    multiple_teachers: int


class EmployeeData(TypedDict):
    # 'pracownik' for full employee, 'doktorant' for PhD student, 'inny' for others.
    status: str
    username: str
    first_name: str
    last_name: str
    pensum: float
    balance: float
    hours_winter: float
    hours_summer: float
    courses_winter: List[SingleAssignmentData]
    courses_summer: List[SingleAssignmentData]


# Indexed by employee's code.
EmployeesSummary = Dict[str, EmployeeData]


class TeacherInfo(NamedTuple):
    username: str
    name: str


class CourseGroupTypeSummary(TypedDict):
    hours: float
    teachers: Set[TeacherInfo]


# Indexed by group type.
AssignmentsCourseInfo = Dict[str, CourseGroupTypeSummary]

# Indexed by course name.
AssignmentsViewSummary = Dict[str, AssignmentsCourseInfo]


# For get_votes function:
class SingleYearVoteSummary(TypedDict):
    # Total of points awarded in a vote.
    total: int
    # Number of voters who awarded this course with maximum number of votes.
    count_max: int
    # Number of voters that voted for this course.
    votes: int
    # Number of enrolled students. None if course was not given that year.
    enrolled: Optional[int]


class ProposalVoteSummary(NamedTuple):
    proposal: Proposal
    semester: str
    course_type: str
    # Indexed by the academic year.
    voting: Dict[str, SingleYearVoteSummary]


# Indexed by the Proposal name.
VotingSummaryPerYear = Dict[str, ProposalVoteSummary]


# For get_subjects_data:
class SingleGroupData(TypedDict):
    name: str
    semester: str
    teacher: str
    teacher_username: str
    # One of GROUP_TYPE_SHEETS.
    group_type: str
    # Hours per week.
    hours: int


ProposalSummary = List[SingleGroupData]


def propose(vote: ProposalVoteSummary):
    """A heuristic suggesting, whether to teach the course in upcoming year."""
    current_year = SystemState.get_current_state().year
    proposal = vote.proposal
    avg = SingleVote.objects.filter(
        state__year=current_year,
        value__gt=0).values('proposal').annotate(total=Sum('value')).aggregate(Avg('total'))
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


def suggest_teachers(picked: Dict[int, str]) -> ProposalSummary:
    """Suggests teachers based on the past instances of the course.

    Data returned by this function will be presented in a spreadsheet, where it
    will help with assigning classes. Given a course, it will look for previous
    instances of the course (taking the newest one) and copy the group
    Assignments from it. If such instance does not exist, it will assign only
    the owner of the course.

    Args:
        picked: Dictionary of proposals selected to be taught in the upcoming
        year. The dictionary is keyed by Proposal ID and the value is 'z' or
        'l'.
    """
    groups: ProposalSummary = []
    proposals = {
        p.id: p for p in Proposal.objects.filter(
            id__in=picked.keys()).select_related('owner', 'owner__user').annotate(
                last_instance=Max('courseinstance__id'))
    }
    past_instances = [p.last_instance for p in proposals.values()]
    past_groups = Group.objects.filter(course__in=past_instances).select_related(
        'course', 'teacher', 'teacher__user')
    past_groups_by_proposal = defaultdict(list)
    for group in past_groups:
        past_groups_by_proposal[group.course.offer_id].append(group)

    for pid, semester in picked.items():
        proposal: Proposal = proposals[pid]
        hours = defaultdict(int)
        hours.update({
            GroupType.LECTURE: proposal.hours_lecture,
            GroupType.EXERCISES: proposal.hours_exercise,
            GroupType.LAB: proposal.hours_lab,
            GroupType.EXERCISES_LAB: proposal.hours_exercise_lab,
            GroupType.SEMINAR: proposal.hours_seminar,
            GroupType.COMPENDIUM: proposal.hours_recap,
        })
        if pid in past_groups_by_proposal:
            groups.extend((SingleGroupData(
                name=proposal.name,
                semester=semester,
                teacher=g.teacher.get_full_name(),
                teacher_username=g.teacher.user.username,
                group_type=g.type,
                hours=hours[GroupType(g.type)]
            ) for g in past_groups_by_proposal[pid]))
        else:
            groups.extend((SingleGroupData(
                name=proposal.name,
                semester=semester,
                teacher=proposal.owner.get_full_name(),
                teacher_username=proposal.owner.user.username,
                group_type=t.value,
                hours=h,
            ) for (t, h) in hours.items() if h))
    return groups


def get_last_years(n: int) -> List[str]:
    """Lists last n academic years, current included."""
    current_year = SystemState.get_current_state().year
    last_states = SystemState.objects.filter(year__lte=current_year).order_by('-year')[:n]
    return [s.year for s in last_states]


def get_votes(years: List[str]) -> VotingSummaryPerYear:
    """Prepares the voting data, that'll be put in a spreadsheet."""
    max_vote_value = max(SingleVote.VALUE_CHOICES)[0]

    # Collect the information on Proposals currently in vote. Leave voting blank
    # for now.
    in_vote = Proposal.objects.filter(
        status=ProposalStatus.IN_VOTE).order_by('name').select_related('course_type')
    proposals: VotingSummaryPerYear = {}
    for p in in_vote:
        if p.semester == SemesterChoices.UNASSIGNED:
            proposals.update({
                f'{p.name} (zima)':
                    ProposalVoteSummary(p, SemesterChoices.WINTER, p.course_type.name, {}),
                f'{p.name} (lato)':
                    ProposalVoteSummary(p, SemesterChoices.SUMMER, p.course_type.name, {}),
            })
        else:
            proposals.update({p.name: ProposalVoteSummary(p, p.semester, p.course_type.name, {})})

    # Collect voting history for these proposals.
    votes = SingleVote.objects.filter(
        state__year__in=years,
        proposal__status=ProposalStatus.IN_VOTE).values('proposal_id', 'state__year').annotate(
            total=Sum('value'),
            count_max=Count('value', filter=Q(value=max_vote_value)),
            votes=Count('value', filter=Q(value__gt=0))).order_by('proposal_id', '-state__year')

    votes_dict = {(v['proposal_id'], v['state__year']):
                  SingleYearVoteSummary(total=v['total'],
                                        count_max=v['count_max'],
                                        votes=v['votes'],
                                        enrolled=None) for v in votes}

    # Collect enrolment numbers.
    records = Record.objects.filter(
        status=RecordStatus.ENROLLED, group__course__offer__status=ProposalStatus.IN_VOTE).values(
            'group__course__offer_id', 'group__course__semester__year',
            'group__course__semester__type').annotate(
                # The number of distinct students enrolled into a course.
                enrolled=Count('student_id', distinct=True))
    records_summary = {(r['group__course__offer_id'], r['group__course__semester__year'],
                        r['group__course__semester__type']): r['enrolled'] for r in records}

    # Put all information into proposals.
    for pvs in proposals.values():
        for year in years:
            try:
                syv = copy.copy(votes_dict[(pvs.proposal.id, year)])
                syv['enrolled'] = records_summary.get((pvs.proposal.id, year, pvs.semester), None)
                pvs.voting[year] = syv
            except KeyError:
                # The proposal was not put to vote that year.
                pass
    return proposals


def sort_subject_groups_by_type(semester: ProposalSummary) -> ProposalSummary:
    """Sorts subjects by their name and then group type."""
    return sorted(semester, key=itemgetter('semester', 'name', 'group_type'))
