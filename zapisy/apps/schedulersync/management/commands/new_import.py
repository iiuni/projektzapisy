from datetime import time
import json
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import environ
import requests

from apps.users.models import Employee
from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models import CourseInstance
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.term import Term
from apps.enrollment.courses.models.group import Group
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.schedulersync.models import TermSyncData, EmployeeMap, CourseMap
import collections

# The mapping between group types in scheduler and enrollment system
# w (wykład), p (pracownia), c (ćwiczenia), s (seminarium), r (ćwiczenio-pracownia),
# e (repetytorium), o (projekt), t (tutoring), m (proseminarium)
GROUP_TYPES = {'w': '1', 'e': '9', 'c': '2', 'p': '3',
               'r': '5', 's': '6', 'o': '10', 't': '11', 'm': '12'}

# The default limits for group types
LIMITS = {'1': 300, '9': 300, '2': 20, '3': 15, '5': 18, '6': 15, '10': 15}

EMPLOYEE_MAP = {
    'PLISOWSKI': '258497',
    'PRATIKGHOSAL': '268909',
    'AMORAWIEC': 'Nn',
    'AMALINOWSKI': 'Nn',
    'ARACZYNSKI': 'Nn',
    'EDAMEK': 'Nn',
    'FINGO': 'Nn',
    'GKARCH': 'Nn',
    'GPLEBANEK': 'Nn',
    'JDYMARA': 'Nn',
    'JDZIUBANSKI': 'Nn',
    'LNEWELSKI': 'Nn',
    'MPREISNER': 'Nn',
    'PKOWALSKI': 'Nn',
    'RSZWARC': 'Nn',
    'SCYGAN': 'Nn',
    'TELSNER': 'Nn',
    'TRZEPECKI': 'Nn',
    '5323': 'pawel.laskos-grabowski', # changed
    'NN1': 'Nn',
    'IM': 'Nn',
    'MKOWALCZYKIEWICZ': 'Nn',  # added
    'AKISIELEWICZ': 'Nn'  # added
}

COURSES_MAP = {
    'MATEMATYKA DYSKRETNA L': 'MATEMATYKA DYSKRETNA (L)',
    'MATEMATYKA DYSKRETNA M': 'MATEMATYKA DYSKRETNA (M)',
    'OCHRONA WŁASNOŚCI INTELEKTUALNEJ (ZIMA)': 'OCHRONA WŁASNOŚCI INTELEKTUALNEJ',
    'PROJEKT DYPLOMOWY (ZIMA)': 'PROJEKT DYPLOMOWY',
    'PROJEKT: BUDOWA I ROZWÓJ ANALOGU ŁAZIKA MARSJAŃSKIEGO (ZIMA)': 'PROJEKT: BUDOWA I ROZWÓJ ANALOGU ŁAZIKA MARSJAŃSKIEGO',
    'PROJEKT: ROZWÓJ SCHEDULERA (ZIMA)': 'PROJEKT: ROZWÓJ SCHEDULERA',
    'PROJEKT: ROZWÓJ SYSTEMU ZAPISÓW (ZIMA)': 'PROJEKT: ROZWÓJ SYSTEMU ZAPISÓW',
    'TUTORING DATA SCIENCE (ZIMA)': 'MENTORING FOR DATA SCIENCE',
    'TUTORING INFORMATYKA (ZIMA)': 'TUTORING',
    'TUTORING ISIM (ZIMA)': 'TUTORING ISIM',
    'ANALIZA NUMERYCZNA L': 'ANALIZA NUMERYCZNA (L)',
    'ANALIZA NUMERYCZNA M': 'ANALIZA NUMERYCZNA (M)',
    'INNOVATIVE PROJECTS BY NOKIA (ZIMA)': 'INNOVATIVE PROJECTS BY NOKIA',
    'PRAKTYKA ZAWODOWA 3 TYGODNIE': 'PRAKTYKA ZAWODOWA - TRZY TYGODNIE',
    'PRAKTYKA ZAWODOWA 4 TYGODNIE': 'PRAKTYKA ZAWODOWA - CZTERY TYGODNIE',
    'PRAKTYKA ZAWODOWA 5 TYGODNI': 'PRAKTYKA ZAWODOWA - PIĘĆ TYGODNI',
    'PRAKTYKA ZAWODOWA 6 TYGODNI': 'PRAKTYKA ZAWODOWA - SZEŚĆ TYGODNI',
    'KURS 1/2: ODZYSKIWANIE DANYCH': 'KURS-½: ODZYSKIWANIE DANYCH',
    'SEMINARIUM: BEZPIECZEŃSTWO I OCHRONA INFORMACJI': 'PROSEMINARIUM: BEZPIECZEŃSTWO I OCHRONA INFORMACJI',
    'SEMINARIUM: INŻYNIERIA OPROGRAMOWANIA': 'METODY PROGRAMOWANIA',  # added
    'SEMINARIUM: LOGIKI OPISOWE, DEDUKCYJNE BAZY DANYCH I REPREZENTACJA WIEDZY': 'METODY PROGRAMOWANIA',  # added
    'TESTOWANIE OPROGRAMOWANIA': 'METODY PROGRAMOWANIA',  # added
    'ANALIZA DANYCH I WARIANCJI': 'METODY PROGRAMOWANIA',  # added
    'PRAKTYKA ZAWODOWA - 3 TYGODNIE': 'METODY PROGRAMOWANIA',  # added
    'PRAKTYKA ZAWODOWA - 4 TYGODNIE': 'METODY PROGRAMOWANIA',  # added
    'PRAKTYKA ZAWODOWA - 5 TYGODNI': 'METODY PROGRAMOWANIA',  # added
    'PRAKTYKA ZAWODOWA - 6 TYGODNI': 'METODY PROGRAMOWANIA',  # added
    'ALGEBRA I': 'METODY PROGRAMOWANIA',  # added
    'ALGEBRA LINIOWA 2': 'METODY PROGRAMOWANIA',  # added
    'ALGEBRA LINIOWA 2R': 'METODY PROGRAMOWANIA',  # added
    'ANALIZA MATEMATYCZNA II': 'METODY PROGRAMOWANIA',  # added
    'TOPOLOGIA': 'METODY PROGRAMOWANIA',  # added
    'RÓWNANIA RÓŻNICZKOWE 1': 'METODY PROGRAMOWANIA',  # added
    'RÓWNANIA RÓŻNICZKOWE 1R': 'METODY PROGRAMOWANIA',  # added
    'TEORIA PRAWDOPODOBIEŃSTWA 1': 'METODY PROGRAMOWANIA',  # added
    'FUNKCJE ANALITYCZNE 1': 'METODY PROGRAMOWANIA',  # added
    'SEMINARIUM: TEORIA KATEGORII W JĘZYKACH PROGRAMOWANIA': 'METODY PROGRAMOWANIA',  # added
    'ANALIZA MATEMATYCZNA I' : 'dont import',
    'ANALIZA MATEMATYCZNA II' : 'dont import',
    'ANALIZA MATEMATYCZNA III' : 'dont import',
    'ALGEBRA 1' : 'dont import',
    #    'ALGEBRA I',
    'ALGEBRA II' : 'dont import',
    'ALGEBRA LINIOWA 1R' : 'dont import',
    'ALGEBRA LINIOWA 2' : 'dont import',
    'ALGEBRA LINIOWA 2R' : 'dont import',
    'MIARA I CAŁKA' : 'dont import',
    'FUNKCJE ANALITYCZNE 1' : 'dont import',
    'RÓWNANIA RÓŻNICZKOWE 1' : 'dont import',
    'RÓWNANIA RÓŻNICZKOWE 1R' : 'dont import',
    'TEORIA PRAWDOPODOBIEŃSTWA 1' : 'dont import',
    'TOPOLOGIA' : 'dont import',
    'INSTYTUT MATEMATYCZNY' : 'dont import',
}

COURSES_DONT_IMPORT = [
    'ANALIZA MATEMATYCZNA I',
    'ANALIZA MATEMATYCZNA II',
    'ANALIZA MATEMATYCZNA III',
    'ALGEBRA 1',
    #    'ALGEBRA I',
    'ALGEBRA II',
    'ALGEBRA LINIOWA 1R',
    'ALGEBRA LINIOWA 2',
    'ALGEBRA LINIOWA 2R',
    'MIARA I CAŁKA',
    'FUNKCJE ANALITYCZNE 1',
    'RÓWNANIA RÓŻNICZKOWE 1',
    'RÓWNANIA RÓŻNICZKOWE 1R',
    'TEORIA PRAWDOPODOBIEŃSTWA 1',
    'TOPOLOGIA',
    'INSTYTUT MATEMATYCZNY']


class SchedulerData:
    """ All useful data laid out from Scheduler API, list and tuples of SchedulerAPIGroup,
        SchedulerAPITerm, SchedulerAPIResult, SchedulerAPIEmployee"""
    groups = []
    terms = {}
    results = {}
    teachers = {}


# id inside this touple refers to SchedulerAPIResult id, we treat this id as scheduler_id
SchedulerAPIGroup = collections.namedtuple(
    'Group', ['id', 'teacher', 'course', 'group_type'])

SchedulerAPITerm = collections.namedtuple(
    'Term', ['day', 'start_hour', 'end_hour'])

# strings in terms list are id's of SchedulerAPITerm tuples
SchedulerAPIResult = collections.namedtuple('Result', ['rooms', 'terms'])

SchedulerAPITeacher = collections.namedtuple('Teacher', ['first_name', 'last_name'])


class GroupData:
    """ Single group object data to save to SZ ( System Zapisów ) database"""
    # oficjalnie jest to scheduler_id, ale w praktyce jest to id tabeli results w schedulerze. Jak to nazwać?
    scheduler_id = int
    course = None
    teacher = None
    type = str
    limit = int


class TermData:
    """ Single term object data to save to SZ ( System Zapisów ) database"""
    dayOfWeek = str
    start_time = time
    end_time = time
    group = None
    classrooms = set()


class Command(BaseCommand):
    def create_or_update_group_and_term(self, group_data: 'GroupData', term_data: 'TermData',
                                        update=False, create=False):
        """ Check if group already exists in database, then create or update that group. Does the same for term,
            unless update or create are set to False """
        try:
            # return corespodning term from SZ database to scheduler group id
            # Sprawdź, czy to zapytanie powoduje, że później nie ma dodatkowych zapytań dzięki select_related i prefetch
            sync_data_object = TermSyncData.objects.select_related(
                'term', 'term__group').prefetch_related('term__classrooms').get(
                scheduler_id=group_data.scheduler_id, term__group__course__semester=self.semester)

            # sync_data_object = TermSyncData.objects.get(
            #     scheduler_id=group_data.scheduler_id, term__group__course__semester=self.semester).select_related(
            #     'term', 'term__group').prefetch_related('term__classrooms')

            changed = False
            term = sync_data_object.term
            self.stdout.write(self.style.WARNING('messages from create_or_update after term found, term: {}, group: {}'
                                                 .format(term, term.group)))

            if term.dayOfWeek != term_data.dayOfWeek:
                changed = True
                self.stdout.write(self.style.WARNING('term can update dayOfWeek from {} to {}'.format(
                    term.dayOfWeek, term_data.dayOfWeek)))
                term.dayOfWeek = term_data.dayOfWeek

            if term.start_time != term_data.start_time:
                changed = True
                self.stdout.write(self.style.WARNING('term can update start_time from {} to {}'.format(
                    term.start_time, term_data.start_time)))
                term.start_time = term_data.start_time

            if term.end_time != term_data.end_time:
                changed = True
                self.stdout.write(self.style.WARNING('term can update end_time from {} to {}'.format(
                    term.end_time, term_data.end_time)))
                term.end_time = term_data.end_time

            if set(term.classrooms.all()) != term_data.classrooms:
                changed = True
                self.stdout.write(self.style.WARNING('term can update classrooms from {} to {}'.format(
                    set(term.classrooms.all()), term_data.classrooms)))
                if update:
                    term.classrooms.set(term_data.classrooms)

            if term.group.course != group_data.course:
                changed = True
                self.stdout.write(self.style.WARNING('group can update course from {} to {}'.format(
                    term.group.course, group_data.course)))
                term.group.course = group_data.course

            if term.group.teacher != group_data.teacher:
                changed = True
                self.stdout.write(self.style.WARNING('group can update teacher from {} to {}'.format(
                    term.group.teacher, group_data.teacher)))
                term.group.teacher = group_data.teacher

            if term.group.type != group_data.type:
                changed = True
                self.stdout.write(self.style.WARNING('group can update type from {} to {}'.format(
                    term.group.type, group_data.type)))
                term.group.type = group_data.type

            if term.group.limit != group_data.limit:
                changed = True
                self.stdout.write(self.style.WARNING('group can update limit from {} to {}'.format(
                    term.group.limit, group_data.limit)))
                term.group.limit = group_data.limit

            if update and changed:
                term.save()
                term.group.save()
                self.stdout.write(self.style.SUCCESS('updated successfully term: {}, group: {}'.
                                                     format(term, term.group)))

        except TermSyncData.DoesNotExist:
            if create:
                self.stdout.write(self.style.WARNING('messages from create_or_update after term not found'
                                                     ' under scheduler id: {}'.format(group_data.scheduler_id)))
                # The lecture always has a single group but possibly many terms
                if group_data.type == 1:
                    group = Group.objects.get_or_create(course=group_data.course, teacher=group_data.teacher,
                                                        type=group_data.type, limit=group_data.limit)[0]
                else:
                    group = Group.objects.create(course=group_data.course, teacher=group_data.teacher,
                                                 type=group_data.type, limit=group_data.limit)


                term = Term.objects.create(dayOfWeek=term_data.dayOfWeek, start_time=term_data.start_time,
                                           end_time=term_data.end_time, group=group)

                term.classrooms.set(term_data.classrooms)
                term.save()
                TermSyncData.objects.create(term=term, scheduler_id=group_data.scheduler_id)

                self.stdout.write(self.style.SUCCESS('term: {} with {} created'.format(term, group)))
            else:
                self.stdout.write(self.style.WARNING('term with scheduler id {} not found and not created'.format(
                    group_data.scheduler_id)))

    def get_term_data(self, scheduler_id: 'int',
                      scheduler_data: 'SchedulerData') -> 'TermData[str, time, time, None, List[Classroom]]':
        """ Fill TermData object with data necessary to save group to SZ database, but without group,
            because it refers to group object saved in SZ database """

        def get_day_of_week(scheduler_term: 'SchedulerAPITerm') -> 'str':
            """ map scheduler numbers of days of week to SZ numbers """
            day = scheduler_term.day
            return str(day + 1)

        def get_start_time(scheduler_terms: 'List[SchedulerAPITerm]') -> 'time(hour)':
            """ returns most early hour from list of SchedulerAPITerm data, which
            containins data about time of current group"""
            hour = 24
            for term in scheduler_terms:
                if term.start_hour < hour:
                    hour = term.start_hour
            return time(hour=hour)

        def get_end_time(scheduler_terms: 'List[SchedulerAPITerm]') -> 'time(hour)':
            """ returns most late hour from list of SchedulerAPITerm data, which
            containins data about time of current group"""
            hour = 0
            for term in scheduler_terms:
                if term.end_hour > hour:
                    hour = term.end_hour
            return time(hour=hour)

        def get_classrooms(rooms: 'List[str]') -> 'Set[Classroom]':
            """ returns list of Classroom objects from SZ databse looking at room number """
            classrooms = set()
            # Czy sprawdzanie czy sala istnieje w instytucie jest potrzebna?
            for room in rooms:
                try:
                    classrooms.add(Classroom.objects.get(number=room))
                except Classroom.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR("Couldn't find classroom for {}".format(room))
                    )
            return classrooms

        scheduler_rooms = scheduler_data.results[scheduler_id].rooms
        scheduler_terms = []
        for id in scheduler_data.results[scheduler_id].terms:
            scheduler_terms.append(scheduler_data.terms[id])

        term_data = TermData()
        term_data.start_time = get_start_time(scheduler_terms)
        term_data.end_time = get_end_time(scheduler_terms)
        term_data.dayOfWeek = get_day_of_week(scheduler_terms[0])
        term_data.classrooms = get_classrooms(scheduler_rooms)
        return term_data

    def get_group_data(self, group_id: 'int',
                       scheduler_data: 'SchedulerData') -> 'GroupData[CourseInstance, Employee, str, int]':
        """ Fill GroupData object with data necessary to save group to SZ database"""

        def get_group_type(group_type: 'str') -> 'str':
            """ map scheduler group type to SZ group type"""
            return GROUP_TYPES[group_type]

        def get_limit(group_type: 'str') -> 'int':
            """ get limit of course type by looking at SZ group type"""
            return LIMITS[group_type]

        def get_proposal(self, course_name: 'str') -> 'Proposal':
            """ return Proposal object from SZ database"""
            # __iexact
            prop = None
            try:
                prop = Proposal.objects.get(
                    name__iexact=course_name, status__in=[ProposalStatus.IN_OFFER,
                                                          ProposalStatus.IN_VOTE])
            except Proposal.DoesNotExist:
                while(True):
                    self.stdout.write(
                        self.style.WARNING(">Couldn't find course proposal for {}".format(course_name)))
                    self.stdout.write(
                        'Please enter proper course name. You will be asked again if course name cannot be found.')
                    new_course_name = input('Course name:')
                    if Proposal.objects.filter(name__iexact=new_course_name).count():
                        CourseMap.objects.create(scheduler_course=course_name.upper(), course=new_course_name.upper())
                        # na wypadek, gdyby nowa nazwa kursu miała kilka propozycji przedmiotu
                        return get_proposal(self, new_course_name)
                    else:
                        EmployeeMap.objects.create(scheduler_username=scheduler_username, employee_username='Nn')
                        break

            except Proposal.MultipleObjectsReturned:
                # Prefer proposals IN_VOTE to those IN_OFFER.
                # Czy może kolejność na odwrót, lub wyrzucić błąd?
                props = Proposal.objects.filter(
                    name__iexact=course_name, status__in=[ProposalStatus.IN_OFFER,
                                                          ProposalStatus.IN_VOTE]).order_by('-status', '-id')
                #            if self.verbosity >= 1:
                self.stdout.write(
                    self.style.WARNING('Multiple course proposals. Took first among:'))
                for prop in props:
                    self.stdout.write(self.style.WARNING('  {}, status = {}'.format(prop,prop.status)))
                self.stdout.write('')
                prop = props[0]
            return prop

        def get_course(self, proposal: 'Proposal', create_courses=False) -> 'CourseInstance':
            """ return CourseInstance object from SZ database"""
            course = None
            try:
                course = CourseInstance.objects.get(semester=self.semester, offer=proposal)
            #            self.used_courses.add(course)
            except CourseInstance.DoesNotExist:
                if create_courses:
                    course = CourseInstance.create_proposal_instance(proposal, self.semester)
                   # self.created_courses += 1

            if course is None:
                raise CommandError(
                    f'Course {proposal.name} does not exist and create_courses = False. Check your input file.')
            return course

        def get_employee(self, username: 'str') -> 'Employee':

            #Odkomentuj i zakomentuj resztę, by dodać maskę z początku skryptu do bazy danych do EmployeeMap
            emp = Employee.objects.filter(user__username=username)
            if emp.count():
                return emp[0]
            else:
                map = EmployeeMap.objects.filter(scheduler_username=username)
                if map.count():
                    return Employee.objects.get(user__username=map[0].employee_username)
                else:
                    SZ_username = username.upper()
                    SZ_username = EMPLOYEE_MAP[SZ_username]
                    EmployeeMap.objects.create(scheduler_username=username, employee_username=SZ_username)
                    return Employee.objects.get(user__username=SZ_username)
            """
            emp = Employee.objects.filter(user__username=username)
            if emp.count():
                return emp[0]
            else:
                map = EmployeeMap.objects.filter(scheduler_username=username)
                if map.count():
                    return Employee.objects.get(user__username=map[0].employee_username)
                else:
                    raise Employee.DoesNotExist(username)
                
            """
        scheduler_course = scheduler_data.groups[group_id].course
        scheduler_teacher = scheduler_data.groups[group_id].teacher
        scheduler_group_type = scheduler_data.groups[group_id].group_type

        group_data = GroupData()
        proposal = get_proposal(self, course_name=scheduler_course)
        group_data.course = get_course(self, proposal, create_courses=False)
        group_data.teacher = get_employee(self, username=scheduler_teacher)
        group_data.type = get_group_type(group_type=scheduler_group_type)
        group_data.limit = get_limit(group_type=group_data.type)
        group_data.scheduler_id = scheduler_data.groups[group_id].id
        return group_data

    def get_scheduler_data(self) -> 'Scheduler_data[List[SchedulerAPIGroup], \
                                    Dict[SchedulerAPITerm], Dict[SchedulerAPIResult]]':
        def get_logged_client():
            url_login = 'http://scheduler.gtch.eu/admin/login/'
            client = requests.session()
            client.get(url_login)
            cookie = client.cookies['csrftoken']
            login_data = {'username': os.environ['scheduler_login'], 'password': os.environ['scheduler_password'],
                          'csrfmiddlewaretoken': cookie}
            client.post(url_login, data=login_data)
            return client

        def get_results_data(results: 'Dict[int, Dict]') -> 'Dict[int, SchedulerApiResult]':
            """ Lays out (room x term) data coming from scheduler """
            data = {}
            for id in results:
                rooms = []
                terms = []
                for rec in results[id]:
                    if rec['room'] not in rooms:
                        rooms.append(rec['room'])
                    if rec['term'] not in terms:
                        terms.append(int(rec['term']))
                data[int(id)] = SchedulerAPIResult(rooms, terms)
            return data

        def get_groups_data(groups: 'List[int, List, Dict]') -> 'List[int, str, str, str]':
            """ Lays out (id, teachers, extra) data coming from scheduler """
            data = []
            for rec in groups:
                id = int(rec['id'])
                teacher = rec['teachers'][0]
                course = rec['extra']['course']
                group_type = rec['extra']['group_type']
                data.append(SchedulerAPIGroup(id, teacher, course, group_type))
            return data

        def get_terms_data(terms: 'List[int, int, Dict, Dict]') -> 'Dict[int, int, int, int, int]':
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
                data[teacher['id']] = SchedulerAPITeacher(first_name, last_name)
            return data

        client = get_logged_client()
        response = client.get(
            'http://scheduler.gtch.eu/scheduler/api/config/wiosna-2019-2/')
        api_config = response.json()
        response = client.get(
            'http://scheduler.gtch.eu/scheduler/api/task/096a8260-5151-4491-82a0-f8e43e7be918/')
        api_task = response.json()
        scheduler_data = SchedulerData()
        scheduler_data.groups = get_groups_data(api_config['groups'])
        scheduler_data.terms = get_terms_data(api_config['terms'])
        scheduler_data.teachers = get_teachers_data(api_config['teachers'])
        scheduler_data.results = get_results_data(api_task['timetable']['results'])
        return scheduler_data

    def save_proper_username(self, teachers: 'Dict[str, str]', scheduler_username: 'str'):
        """Get username from script user and add that username to EmployeeMap"""
        first_name, last_name = teachers[scheduler_username]
        while True:
            self.stdout.write(self.style.WARNING(
                'Employee with username \'{}\' not found'.format(scheduler_username)))
            self.stdout.write(
                'First name: {}, last name: {}\n'
                'Please enter proper username. You will be asked again if username cannot be found.\n'
                'Leave it blank (press enter) to set \'nieznany prowadzący\''.format(first_name, last_name))
            new_username = input('Username:')
            if new_username:
                if Employee.objects.filter(user__username=new_username).count():
                    EmployeeMap.objects.create(scheduler_username=scheduler_username, employee_username=new_username)
                    break
                self.stdout.write(self.style.WARNING('\nUsername \'{}\' still not found'.format(new_username)))
            else:
                EmployeeMap.objects.create(scheduler_username=scheduler_username, employee_username='Nn')
                break

    def handle(self, *args, **options):
        # potem zmień semestr by było ustawiane jako argument do komendy skryptu
        self.semester = Semester.objects.get(year="2018/19", type='l')
        scheduler_data = self.get_scheduler_data()
        # pętla od zera do len(scheduler_data.groups), tak samo jak są ustawione klucze podstawowe w schedulerze
        for group_id in range(len(scheduler_data.groups)):
            scheduler_course = scheduler_data.groups[group_id].course
            map = CourseMap.objects.filter(scheduler_course=scheduler_course)
            if map.count():
                if map[0].course == 'dont import':
                    continue
                else:
                    scheduler_course = map[0].course


            # do testów, usuń potem. Pamiętaj, że zmieniasz litery na duże i bez iexact nie zadziała skrypt
            new_course_name = scheduler_course.upper()
            if new_course_name in COURSES_MAP:
                new_course_name = COURSES_MAP[new_course_name]
                CourseMap.objects.get_or_create(scheduler_course=scheduler_course.upper(), course=new_course_name)
                if new_course_name == 'dont import':
                    continue

            scheduler_data.groups[group_id] = scheduler_data.groups[group_id]._replace(course=new_course_name)
            try:
                group_data = self.get_group_data(group_id, scheduler_data)
            except Employee.DoesNotExist as err:
                self.save_proper_username(scheduler_data.teachers, err.args[0])
                group_data = self.get_group_data(group_id, scheduler_data)
            term_data = self.get_term_data(group_data.scheduler_id, scheduler_data)
            self.create_or_update_group_and_term(group_data, term_data, True, True)
