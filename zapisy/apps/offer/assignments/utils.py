from collections import defaultdict
from typing import List, Dict, NamedTuple, Optional, Tuple

from django.db.models import Count, F, Q, Sum, Window
from django.db.models.functions import FirstValue
from django.template.defaultfilters import floatformat

from apps.enrollment.courses.models import CourseInstance
from apps.enrollment.courses.models.course_information import Language
from apps.enrollment.courses.models.group import Group, GroupType
from apps.enrollment.records.models.records import Record, RecordStatus
from apps.offer.proposal.models import Proposal, ProposalStatus, SemesterChoices
from apps.offer.vote.models.single_vote import SingleVote
from apps.offer.vote.models.system_state import SystemState
from apps.schedulersync.scheduler_data import GROUP_TYPES


class SingleAssignmentData(NamedTuple):
    """Represents a row in the Assignments sheet."""
    name: str
    proposal_id: int
    # full name, as in GROUP_TYPES
    group_type: str
    group_type_short: str
    hours_weekly: Optional[int]
    hours_semester: float
    equivalent: float
    # l (summer) or z (winter)
    semester: str
    teacher_username: str
    confirmed: bool
    # How many teachers assigned to the same group.
    multiple_teachers: int
    multiple_teachers_id: str


class ProcessedAssignment:
    course_name: str
    group_type: str
    hours_multiplier: float
    hours_semester: float
    hours_divisor: int
    hours_to_pensum: float

    def __init__(self, sa: SingleAssignmentData):
        self.course_name = sa.name
        self.group_type = sa.group_type
        self.hours_multiplier = sa.equivalent
        self.hours_semester = sa.hours_semester
        self.hours_divisor = sa.multiple_teachers
        self.hours_to_pensum = self.hours_multiplier * self.hours_semester / self.hours_divisor

    def hours_to_pensum_display(self) -> str:
        """Displays hours to pensum as a formula and its result."""
        has_pensum_modifiers = False
        hours_to_pensum_display = ""
        if self.hours_multiplier != 1:
            has_pensum_modifiers = True
            hours_to_pensum_display += f"{floatformat(self.hours_multiplier)}⋅"
        hours_to_pensum_display += f"{floatformat(self.hours_semester)}"
        if self.hours_divisor > 1:
            has_pensum_modifiers = True
            hours_to_pensum_display += f"÷{floatformat(self.hours_divisor)}"
        if has_pensum_modifiers:
            hours_to_pensum_display += f" = {floatformat(self.hours_to_pensum)}"
        return hours_to_pensum_display


class EmployeeData(NamedTuple):
    # 'pracownik' for full employee, 'doktorant' for PhD student, 'inny' for others.
    status: str
    username: str
    first_name: str
    last_name: str
    pensum: int
    balance: float
    hours_winter: float
    hours_summer: float
    courses_winter: List[ProcessedAssignment]
    courses_summer: List[ProcessedAssignment]


# Indexed by employee's code.
EmployeesSummary = Dict[str, EmployeeData]


class TeacherInfo(NamedTuple):
    username: str
    name: str


class CourseGroupTypeSummary(NamedTuple):
    hours: float
    teachers: Dict[TeacherInfo, int]


# Indexed by group type.
AssignmentsCourseInfo = Dict[str, CourseGroupTypeSummary]

# Indexed by course name.
AssignmentsViewSummary = Dict[str, AssignmentsCourseInfo]


# For get_votes function:
class SingleYearVoteSummary(NamedTuple):
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

ProposalSummary = List[SingleAssignmentData]


def suggest_teachers(picked: List[Tuple[int, str]]) -> ProposalSummary:
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
    REVERSE_GROUP_TYPES = {v: k for k, v in GROUP_TYPES.items()}
    EQUIVALENTS = {
        Language.POLISH: 1.0,
        Language.ENGLISH: 1.5,
    }
    proposal_ids = set(p for (p, _s) in picked)
    proposals = {
        p.id: p for p in Proposal.objects.filter(
            id__in=proposal_ids).select_related('owner', 'owner__user')
    }
    # We use an SQL Window function to get the most recent instance of each
    # course.
    past_instances = CourseInstance.objects.filter(offer__in=proposal_ids).annotate(
        last_instance=Window(
            expression=FirstValue('id'),
            partition_by=[F('offer')],
            order_by=F('semester').desc(),
        )).values_list('last_instance', flat=True).distinct()
    past_groups = Group.objects.filter(course__in=past_instances).select_related(
        'course', 'teacher', 'teacher__user')
    past_groups_by_proposal = defaultdict(list)
    for group in past_groups:
        past_groups_by_proposal[group.course.offer_id].append(group)

    for pid, semester in picked:
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
        if proposal.semester == SemesterChoices.UNASSIGNED:
            apx = 'zima' if semester == 'z' else 'lato'
            name = f"{proposal.name} ({apx})"
        else:
            name = proposal.name
        if pid in past_groups_by_proposal:
            groups.extend((SingleAssignmentData(
                proposal_id=proposal.pk,
                name=name,
                semester=semester,
                teacher_username=g.teacher.user.username,
                group_type=g.get_type_display(),
                group_type_short=REVERSE_GROUP_TYPES[g.type],
                hours_semester=hours[GroupType(g.type)],
                hours_weekly=None,
                equivalent=EQUIVALENTS[proposal.language],
                confirmed=False,
                multiple_teachers=1,
                multiple_teachers_id='',
            ) for g in past_groups_by_proposal[pid]))
        else:
            groups.extend((SingleAssignmentData(
                proposal_id=proposal.pk,
                name=name,
                semester=semester,
                teacher_username=proposal.owner.user.username,
                group_type=t.label,
                group_type_short=REVERSE_GROUP_TYPES[t.value],
                hours_semester=h,
                hours_weekly=None,
                equivalent=EQUIVALENTS[proposal.language],
                confirmed=False,
                multiple_teachers=1,
                multiple_teachers_id='',
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
                enrolled = records_summary.get((pvs.proposal.id, year, pvs.semester), None)
                pvs.voting[year] = votes_dict[(pvs.proposal.id, year)]._replace(enrolled=enrolled)
            except KeyError:
                # The proposal was not put to vote that year.
                pass
    return proposals
