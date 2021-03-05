"""Gets data from scheduler API.

Get data from scheduler API urls and lays out that data to list of SchTerm.
SchTerm contains all necessary data to update or create term. That data is not
yet mapped to the Zapisy database — that is a role of `scheduler_mapper`.
"""
from dataclasses import dataclass
from datetime import time
from typing import Dict, List, Optional, Tuple, TypedDict, Set

import requests

from apps.enrollment.courses.models.group import GroupType

# The mapping between group types in scheduler and enrollment system
# w (wykład), p (pracownia), c (ćwiczenia), s (seminarium), r (ćwiczenio-pracownia),
# e (repetytorium), o (projekt), t (tutoring), m (proseminarium)
GROUP_TYPES = {
    'w': GroupType.LECTURE,
    'e': GroupType.COMPENDIUM,
    'c': GroupType.EXERCISES,
    'p': GroupType.LAB,
    'r': GroupType.EXERCISES_LAB,
    's': GroupType.SEMINAR,
    'o': GroupType.PROJECT,
    't': GroupType.TUTORING,
    'm': GroupType.PRO_SEMINAR
}

# Type & format definitions for JSON files coming from the Scheduler API.
# The first file, 'config', is an input to the scheduler. It contains the
# description of classes (to be scheduled), teachers, time-slots, classrooms.
GroupId = str
TeacherId = str
TermId = str
GroupExtra = TypedDict('GroupExtra', course=str, group_type=str)
TeacherExtra = TypedDict('TeacherExtra', first_name=str, last_name=str)


class SchedulerAPIGroup(TypedDict):
    """Represents a single term (meeting)."""
    id: GroupId
    extra: GroupExtra
    students_num: int
    teachers: List[TeacherId]


class SchedulerAPITeacher(TypedDict):
    id: str
    extra: TeacherExtra


SchedulerAPITermTime = TypedDict('TermTime', {'hour': int})


class SchedulerAPITerm(TypedDict):
    """Represents a (usually an hour long) pre-defined time slot."""
    id: TermId
    day: int
    start: SchedulerAPITermTime
    end: SchedulerAPITermTime


class SchedulerAPIConfig(TypedDict):
    teachers: List[SchedulerAPITeacher]
    groups: List[SchedulerAPIGroup]
    terms: List[SchedulerAPITerm]


# The second file is 'task': a product of a Scheduler run.
SchedulerAPIResult = TypedDict('Result', room=str, term=TermId)
SchedulerAPIResultMap = Dict[GroupId, List[SchedulerAPIResult]]
SchedulerAPITask = TypedDict(
    'Task', {'timetable': TypedDict('Timetable', {'results': SchedulerAPIResultMap})})


@dataclass
class SchTerm:
    """Single term imported from the Scheduler.

    Attributes:
        teacher: String identifier. Key in config['teachers'].
        course: String name.
        type: Group type as defined in `apps.enrollment.courses.models.group`.
        dayOfWeek: String as in `apps.common.days_of_week`.
        classrooms: List of room numbers.
    """
    scheduler_id: int
    teacher: TeacherId
    course: str
    type: GroupType
    limit: int
    dayOfWeek: str
    start_time: time
    end_time: time
    classrooms: List[str]


class SchedulerData:
    def __init__(self, api_login_url, api_config_url, api_task_url, scheduler_username, scheduler_password):
        self.api_login_url = api_login_url
        self.api_config_url = api_config_url
        self.api_task_url = api_task_url
        self.scheduler_username = scheduler_username
        self.scheduler_password = scheduler_password
        self.terms = []
        self.teachers = {}
        self.courses = set()
        self.classrooms = set()
        self._scheduler_results: SchedulerAPIResultMap = {}
        self._scheduler_terms: Dict[TermId, SchedulerAPITerm] = {}

    def _map_scheduler_types(self, group: SchedulerAPIGroup) -> Optional[SchTerm]:
        """Collects a single term (group) from Scheduler's data.

        A single term is described in Scheduler in different places: The group
        info (teacher, type, etc.) is in 'config'; The classroom is in
        'results'; The time is in 'SchedulerAPITerm's (time slots) which the
        'results' point to.
        """

        def translate_day_of_week(scheduler_day: int) -> str:
            """Map scheduler numbers of days of week to SZ numbers."""
            return str(scheduler_day + 1)

        def get_start_time(scheduler_terms: List[SchedulerAPITerm]) -> time:
            """Returns earliest starting time among the SchedulerAPITerms."""
            hour = min(term['start']['hour'] for term in scheduler_terms)
            return time(hour=hour)

        def get_end_time(scheduler_terms: List[SchedulerAPITerm]) -> time:
            """Returns latest starting time among the SchedulerAPITerms."""
            hour = max(term['end']['hour'] for term in scheduler_terms)
            return time(hour=hour)

        def translate_group_type(group_type: 'str') -> 'GroupType':
            """Translates scheduler group type to SZ group type."""
            return GROUP_TYPES[group_type]

        group_id = group['id']
        if group_id not in self._scheduler_results:
            # Group without term. Not imported.
            return None
        rooms: Set[str] = set()
        terms: List[SchedulerAPITerm] = []
        for result in self._scheduler_results[group_id]:
            rooms.add(result['room'])
            terms.append(self._scheduler_terms[result['term']])
        return SchTerm(
            scheduler_id=int(group_id),
            teacher=group['teachers'][0],
            course=group['extra']['course'],
            type=translate_group_type(group['extra']['group_type']),
            limit=group['students_num'],
            dayOfWeek=translate_day_of_week(terms[0]['day']),
            start_time=get_start_time(terms),
            end_time=get_end_time(terms),
            classrooms=list(rooms),
        )

    def fetch_data_from_scheduler(self) -> Tuple[SchedulerAPIConfig, SchedulerAPITask]:
        """Authenticates with Scheduler API and fetches the data."""
        def get_logged_client():
            client = requests.session()
            client.get(self.api_login_url)
            cookie = client.cookies['csrftoken']
            login_data = {'username': self.scheduler_username, 'password': self.scheduler_password,
                          'csrfmiddlewaretoken': cookie}
            client.post(self.api_login_url, data=login_data)
            return client

        client = get_logged_client()
        response = client.get(self.api_config_url)
        api_config = response.json()
        response = client.get(self.api_task_url)
        api_task = response.json()
        return api_config, api_task

    def lay_out_scheduler_data(self, api_config: SchedulerAPIConfig, api_task: SchedulerAPITask):
        """Lays out the data fetched from Scheduler in a useful manner.

        Puts a list of SchTerm in self.terms. This list contains all necessary
        data to update or create term in SZ. That data lacks employee, course
        and classroom mapping. Fills self.teachers, self.courses and
        self.classrooms with teachers, courses names and classroom numbers for
        future mapping.
        """

        def map_terms(terms: List[SchedulerAPITerm]) -> Dict[TermId, SchedulerAPITerm]:
            """Lays out (id, day, start, end) data coming from scheduler."""
            return {t['id']: t for t in terms}

        def map_teachers_names(teachers: List[SchedulerAPITeacher],
                               filter: Set[TeacherId]) -> Dict[TeacherId, str]:
            """Lays out (first_name, last_name) data coming from scheduler."""
            data = {}
            for teacher in teachers:
                if teacher['id'] not in filter:
                    continue
                first_name = teacher['extra']['first_name']
                last_name = teacher['extra']['last_name']
                data[teacher['id']] = first_name + " " + last_name
            return data

        self._scheduler_results = api_task['timetable']['results']
        self._scheduler_terms = map_terms(api_config['terms'])
        scheduler_groups = api_config['groups']

        active_teachers = set()
        for sh_group in scheduler_groups:
            term = self._map_scheduler_types(sh_group)
            if term:
                self.terms.append(term)
                active_teachers.add(term.teacher)

        self.teachers = map_teachers_names(api_config['teachers'], active_teachers)
        self.courses = set(term.course for term in self.terms)
        self.classrooms = set().union(*(term.classrooms for term in self.terms))

    def get_scheduler_data(self):
        """Combines fetching and laying out the Scheduler data."""
        api_config, api_task = self.fetch_data_from_scheduler()
        self.lay_out_scheduler_data(api_config, api_task)
