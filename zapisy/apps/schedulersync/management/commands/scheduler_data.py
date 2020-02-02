""" Get data from scheduler API urls and lays out that data to list of SZTerm.
    Szterm contains all necessary data to update or create term.
    That data lacks courses and teachers mapping, so prepare all teachers
    and courses to map in seperate dict and set."""

import collections
from datetime import time

import requests
from apps.enrollment.courses.models.classroom import Classroom


URL_LOGIN = 'http://scheduler.gtch.eu/admin/login/'

# The mapping between group types in scheduler and enrollment system
# w (wykład), p (pracownia), c (ćwiczenia), s (seminarium), r (ćwiczenio-pracownia),
# e (repetytorium), o (projekt), t (tutoring), m (proseminarium)
GROUP_TYPES = {'w': '1', 'e': '9', 'c': '2', 'p': '3',
               'r': '5', 's': '6', 'o': '10', 't': '11', 'm': '12'}

# id inside this touple refers to SchedulerAPIResult id, we treat this id as scheduler_id
SchedulerAPIGroup = collections.namedtuple('Group', ['id', 'teacher', 'course', 'group_type', 'limit'])
# strings in terms list are id's of SchedulerAPITerm tuples
SchedulerAPIResult = collections.namedtuple('Result', ['rooms', 'terms'])
SchedulerAPITerm = collections.namedtuple('Term', ['day', 'start_hour', 'end_hour'])
# System Zapisow term data
SZTerm = collections.namedtuple('Term', ['scheduler_id', 'teacher', 'course', 'type', 'limit',
                                         'dayOfWeek', 'start_time', 'end_time', 'classrooms'])


class SchedulerData:
    def __init__(self, api_config_url, api_task_url, scheduler_username, scheduler_password):
        self.api_config_url = api_config_url
        self.api_task_url = api_task_url
        self.scheduler_username = scheduler_username
        self.scheduler_password = scheduler_password
        self.terms = []
        self.teachers = {}
        self.courses = set()

    def __map_scheduler_types(self, sh_results: 'Dict[int, SchedulerApiResult]',
                              sh_terms: 'Dict[int, SchedulerAPITerm]', term: SZTerm) -> SZTerm:
        """ Change SZTerm data with data in SZ format. Does not map course and employee """

        def get_day_of_week(scheduler_term: 'SchedulerAPITerm') -> 'str':
            """ map scheduler numbers of days of week to SZ numbers """
            day = scheduler_term.day
            return str(day + 1)

        def get_start_time(scheduler_terms: 'List[SchedulerAPITerm]') -> 'time(hour)':
            """ Returns earliest starting time among the SchedulerAPITerms."""
            hour = min(term.start_hour for term in scheduler_terms)
            return time(hour=hour)

        def get_end_time(scheduler_terms: 'List[SchedulerAPITerm]') -> 'time(hour)':
            """ Returns latest starting time among the SchedulerAPITerms."""
            hour = max(term.end_hour for term in scheduler_terms)
            return time(hour=hour)

        def get_classrooms(rooms: 'List[str]') -> 'Set[Classroom]':
            """ Finds Classroom objects from with given room numbers. """
            return set(Classroom.objects.filter(number__in=rooms))

        def get_group_type(group_type: 'str') -> 'str':
            """ map scheduler group type to SZ group type"""
            return GROUP_TYPES[group_type]

        scheduler_rooms = sh_results[term.scheduler_id].rooms
        scheduler_terms = []
        for id in sh_results[term.scheduler_id].terms:
            scheduler_terms.append(sh_terms[id])

        start_time = get_start_time(scheduler_terms)
        end_time = get_end_time(scheduler_terms)
        dayOfWeek = get_day_of_week(scheduler_terms[0])
        classrooms = get_classrooms(scheduler_rooms)
        type = get_group_type(term.type)
        return SZTerm(term.scheduler_id, term.teacher, term.course, type,
                      term.limit, dayOfWeek, start_time, end_time, classrooms)

    def get_scheduler_data(self):
        """ Get data from scheduler API and lays out that data to SZTerm, which has all
            necessary data to update or create term in SZ. That data
            lacks employee and course mapping"""
        def get_logged_client():
            client = requests.session()
            client.get(URL_LOGIN)
            cookie = client.cookies['csrftoken']
            login_data = {'username': self.scheduler_username, 'password': self.scheduler_password,
                          'csrfmiddlewaretoken': cookie}
            client.post(URL_LOGIN, data=login_data)
            return client

        def get_results_data(results: 'Dict[int, Dict]') -> 'Dict[int, SchedulerApiResult]':
            """ Lays out (room x term) data coming from scheduler """
            data = {}
            for id in results:
                rooms = set(rec['room'] for rec in results[id])
                terms = set(int(rec['term']) for rec in results[id])
                data[int(id)] = SchedulerAPIResult(rooms, terms)
            return data

        def get_groups_data(groups: 'List[int, List, Dict]') -> 'List[SchedulerAPIGroup]':
            """ Lays out (id, teachers, extra) data coming from scheduler """
            data = []
            for rec in groups:
                id = int(rec['id'])
                teacher = rec['teachers'][0]
                course = rec['extra']['course']
                group_type = rec['extra']['group_type']
                limit = rec['students_num']
                data.append(SchedulerAPIGroup(id, teacher, course, group_type, limit))
            return data

        def get_terms_data(terms: 'List[int, int, Dict, Dict]') -> 'Dict[int, SchedulerAPITerm]':
            """ Lays out (id, day, start, end) data coming from scheduler """
            data = {}
            for rec in terms:
                day = rec['day']
                start_hour = rec['start']['hour']
                end_hour = rec['end']['hour']
                data[int(rec['id'])] = SchedulerAPITerm(
                    day, start_hour, end_hour)
            return data

        def get_teachers_data(teachers: 'List[str, Dict]') -> 'Dict[str, str]':
            """ Lays out (first_name, last_name) data coming from scheduler """
            data = {}
            for teacher in teachers:
                first_name = teacher['extra']['first_name']
                last_name = teacher['extra']['last_name']
                data[teacher['id']] = first_name + " " + last_name
            return data

        client = get_logged_client()
        response = client.get(self.api_config_url)
        api_config = response.json()
        response = client.get(self.api_task_url)
        api_task = response.json()
        scheduler_results = get_results_data(api_task['timetable']['results'])
        scheduler_groups = get_groups_data(api_config['groups'])
        scheduler_terms = get_terms_data(api_config['terms'])

        for sh_group in scheduler_groups:
            term = SZTerm(sh_group.id, sh_group.teacher, sh_group.course, sh_group.group_type,
                          sh_group.limit, "", time(), time(), set())
            term = self.__map_scheduler_types(scheduler_results, scheduler_terms, term)
            self.terms.append(term)

        teachers_names = get_teachers_data(api_config['teachers'])
        teachers = set(term.teacher for term in self.terms)
        for teacher in teachers:
            self.teachers[teacher] = teachers_names[teacher]
        self.courses = set(term.course for term in self.terms)
