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
from apps.schedulersync.models import TermSyncData
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
    #   'AMORAWIEC': 'NN',
    'AMORAWIEC': '540',  # added
    #   'AMALINOWSKI': 'NN',
    'AMALINOWSKI': '540',  # added
    #   'ARACZYNSKI': 'NN',
    'ARACZYNSKI': '540',  # added
    #   'EDAMEK': 'NN',
    'EDAMEK': '540',  # added
    #   'FINGO': 'NN',
    'FINGO': '540',  # added
    #   'GKARCH': 'NN',
    'GKARCH': '540',  # added
    #   'GPLEBANEK': 'NN',
    'GPLEBANEK': '540',  # added
    #   'JDYMARA': 'NN',
    'JDYMARA': '540',  # added
    #   'JDZIUBANSKI': 'NN',
    'JDZIUBANSKI': '540',  # added
    #   'LNEWELSKI': 'NN',
    'LNEWELSKI': '540',  # added
    #   'MPREISNER': 'NN',
    'MPREISNER': '540',  # added
    #   'PKOWALSKI': 'NN',
    'PKOWALSKI': '540',  # added
    #   'RSZWARC': 'NN',
    'RSZWARC': '540',  # added
    #   'SCYGAN': 'NN',
    'SCYGAN': '540',  # added
    #    'TELSNER': 'NN',
    'TELSNER': '540',  # added
    'TRZEPECKI': 'NN',
    '5323': 'PAWEL.LASKOS-GRABOWSKI',
    'NN1': 'NN',
    'IM': 'NN',
    'MKOWALCZYKIEWICZ': '540',  # added
    'AKISIELEWICZ': '540'  # added
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
    'TESTOWANIE OPROGRAMOWANIA': 'PRAKTYKA ZAWODOWA - PIĘĆ TYGODNI',  # added
    'ANALIZA DANYCH I WARIANCJI': 'METODY PROGRAMOWANIA',  # added
    'PRAKTYKA ZAWODOWA - 3 TYGODNIE': 'PRAKTYKA ZAWODOWA - TRZY TYGODNIE',  # added
    'PRAKTYKA ZAWODOWA - 4 TYGODNIE': 'PRAKTYKA ZAWODOWA - CZTERY TYGODNIE',  # added
    'PRAKTYKA ZAWODOWA - 5 TYGODNI': 'PRAKTYKA ZAWODOWA - PIĘĆ TYGODNI',  # added
    'PRAKTYKA ZAWODOWA - 6 TYGODNI': 'PRAKTYKA ZAWODOWA - SZEŚĆ TYGODNI',  # added
    'ALGEBRA I': 'METODY PROGRAMOWANIA',  # added
    'ALGEBRA LINIOWA 2': 'METODY PROGRAMOWANIA',  # added
    'ALGEBRA LINIOWA 2R': 'METODY PROGRAMOWANIA',  # added
    'ANALIZA MATEMATYCZNA II': 'METODY PROGRAMOWANIA',  # added
    'TOPOLOGIA': 'PRAKTYKA ZAWODOWA - TRZY TYGODNIE',  # added
    'RÓWNANIA RÓŻNICZKOWE 1': 'PRAKTYKA ZAWODOWA - SZEŚĆ TYGODNI',  # added
    'RÓWNANIA RÓŻNICZKOWE 1R': 'METODY PROGRAMOWANIA',  # added
    'TEORIA PRAWDOPODOBIEŃSTWA 1': 'PRAKTYKA ZAWODOWA - TRZY TYGODNIE',  # added
    'FUNKCJE ANALITYCZNE 1': 'METODY PROGRAMOWANIA',  # added
    'SEMINARIUM: TEORIA KATEGORII W JĘZYKACH PROGRAMOWANIA': 'PRAKTYKA ZAWODOWA - TRZY TYGODNIE',  # added
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
        SchedulerAPITerm, SchedulerAPIResult"""
    groups = []
    terms = {}
    results = {}


# id inside this touple refers to SchedulerAPIResult id, we treat this id as scheduler_id
SchedulerAPIGroup = collections.namedtuple(
    'Group', ['id', 'teacher', 'course', 'group_type'])

SchedulerAPITerm = collections.namedtuple(
    'Term', ['day', 'start_hour', 'end_hour'])

# strings in terms list are id's of SchedulerAPITerm tuples
SchedulerAPIResult = collections.namedtuple('Result', ['rooms', 'terms'])


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
    classrooms = []


class Command(BaseCommand):
    def create_or_update_group_and_term(self, group_data: 'GroupData', term_data: 'TermData',
                                        update=False, create=False):
        """ Check if group already exists in database, then create or update that group. Does the same for term,
            unless update or create are set to False """
        try:
            # return corespodning term from SZ database to scheduler group id
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

            if term.classrooms != term_data.classrooms:
                changed = True
                self.stdout.write(self.style.WARNING('term can update classrooms from {} to {}'.format(
                    term.classrooms, term_data.classrooms)))
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

        def get_classrooms(rooms: 'List[str]') -> 'List[Classroom]':
            """ returns list of Classroom objects from SZ databse looking at room number """
            classrooms = []
            for room in rooms:
                try:
                    classrooms.append(Classroom.objects.get(number=room))
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
            course_name = course_name.upper()
            if course_name in COURSES_MAP:
                course_name = COURSES_MAP[course_name]
            prop = None
            try:
                prop = Proposal.objects.get(
                    name__iexact=course_name, status__in=[ProposalStatus.IN_OFFER,
                                                          ProposalStatus.IN_VOTE])
            except Proposal.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(">Couldn't find course proposal for {}".format(course_name))
                )
            except Proposal.MultipleObjectsReturned:
                # Prefer proposals IN_VOTE to those IN_OFFER.
                props = Proposal.objects.filter(
                    name__iexact=course_name, status__in=[ProposalStatus.IN_OFFER,
                                                          ProposalStatus.IN_VOTE]).order_by('-status', '-id')
                #            if self.verbosity >= 1:
                self.stdout.write(
                    self.style.WARNING('Multiple course proposals. Took first among:'))
                for prop in props:
                    self.stdout.write(self.style.WARNING('  {}'.format(str(prop))))
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
                    self.created_courses += 1

            if course is None:
                if proposal is None:
                    raise CommandError(
                        f'Proposal is None. Check your input file.')
                else:
                    raise CommandError(
                        f'Course {proposal.name} does not exist! Check your input file.')
            return course

        def get_employee(self, name: 'str') -> 'Employee':
            """ Tries to match employee name in scheduler to the employee user in the enrollment system.

            First, it replaces name using handy mapping to fix eventual typos
            The order of checks is the following:
            1) the name is integer -> then this corresponds to employee_id in the enrollment system
            2) the name is equal to the login
            3) the name is a 3 letter shortcut of first and last name
            4) the name is a first letter of a first name and a last name

            If more employees are matched or the employee does not exists,
            the function will fail with an error
            """
            name = name.upper()
            if name in EMPLOYEE_MAP:
                print(name)  # added
                name = EMPLOYEE_MAP[name]
            try:
                int(name)
                emps = Employee.objects.filter(id=name)
            except ValueError:
                if name == 'NN':
                    emps = Employee.objects.filter(user__first_name='Nieznany')
                elif Employee.objects.filter(user__username__iexact=name).exists():
                    emps = Employee.objects.filter(user__username__iexact=name)
                elif len(name) == 3:
                    emps = Employee.objects.filter(user__first_name__istartswith=name[0],
                                                   user__last_name__istartswith=name[1:3],
                                                   status=0)
                else:
                    emps = Employee.objects.filter(user__first_name__istartswith=name[0],
                                                   user__last_name__istartswith=name[1:],
                                                   status=0)
            if not emps:
                emps = Employee.objects.filter(user__username__istartswith=name)
            if len(emps) == 1:
                return emps[0]
            elif len(emps) > 1:
                self.stdout.write(self.style.ERROR('Multiple employee matches for {}. Choices are:'
                                                   .format(name)))
                for e in emps:
                    self.stdout.write(self.style.ERROR(' -{}'.format(e.user.get_full_name())))
            else:
                raise CommandError('Employee {} does not exists! Fix your input file.'.format(name))

            return None

        scheduler_course = scheduler_data.groups[group_id].course
        scheduler_teacher = scheduler_data.groups[group_id].teacher
        scheduler_group_type = scheduler_data.groups[group_id].group_type

        group_data = GroupData()
        proposal = get_proposal(self, course_name=scheduler_course)
        group_data.course = get_course(self, proposal, create_courses=False)
        group_data.teacher = get_employee(self, name=scheduler_teacher)
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
            login_data = {'username': 'kkasprzyk', 'password': '0GA6bAFb5GZgrzLH',
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

        client = get_logged_client()
        response = client.get(
            'http://scheduler.gtch.eu/scheduler/api/config/wiosna-2019-2/')
        api_config = response.json()
        response = client.get(
            'http://scheduler.gtch.eu/scheduler/api/task/096a8260-5151-4491-82a0-f8e43e7be918/')
        api_task = response.json()

        api_groups = api_config['groups']
        api_terms = api_config['terms']
        api_results = api_task['timetable']['results']

        scheduler_data = SchedulerData()
        scheduler_data.results = get_results_data(api_results)
        scheduler_data.groups = get_groups_data(api_groups)
        scheduler_data.terms = get_terms_data(api_terms)

        return scheduler_data

    def check_if_import(self, course_name: 'str') -> 'bool':
        course_name = course_name.upper()
        if course_name in COURSES_MAP:
            course_name = COURSES_MAP[course_name]
        if course_name in COURSES_DONT_IMPORT:
            return False
        else:
            return True

    def handle(self, *args, **options):
        # potem zmień semestr by było ustawiane jako argument do komendy skryptu
        self.semester = Semester.objects.get(year="2018/19", type='l')
        scheduler_data = self.get_scheduler_data()
        # pętla od zera do len(scheduler_data.groups), tak samo jak są ustawione klucze podstawowe w schedulerze
        for group_id in range(len(scheduler_data.groups)):
            scheduler_course = scheduler_data.groups[group_id].course
            if self.check_if_import(scheduler_course):
                group_data = self.get_group_data(group_id, scheduler_data)
                term_data = self.get_term_data(group_data.scheduler_id, scheduler_data)
                self.create_or_update_group_and_term(group_data, term_data, True, True)
            else:
                continue

        # for group in Duplicates:
        #     try:
        #         gr = Group.objects.get(course=group.course, teacher=group.teacher,
        #                                type=group.type, limit=group.limit)
        #         print("grupa, która wcześniej miała duplikat: ", gr)
        #     except Group.MultipleObjectsReturned:
        #         self.stdout.write(self.style.WARNING('course = {}, teacher = {}, type = {} limit = {},'
        #                                              'multiple objects returned'.format(group.course,
        #                                                                                 group.teacher,
        #                                                                                 group.type,
        #                                                                                 group.limit)))
        #         print("prop info=", group.course.offer.name)
        #         res = Group.objects.filter(course=group.course, teacher=group.teacher,
        #                                    type=group.type, limit=group.limit)
        #         for dup in res:
        #             print("klucz podstawowy dupliaku grupy ", dup, " to: ", dup.pk)

        # # print(scheduler_data.config_groups[10])
        # # print(type(scheduler_data.config_terms[109].day))
        # # print(scheduler_data.task_results[109].terms[0])
        # # print(type(scheduler_data.task_results[10].rooms[0]))
        #
        # print("group data:")
        # for attr in vars(group_data):
        #     print("%s = %r" % (attr, getattr(group_data, attr)))
        #
        # print("tern data:")
        # for attr in vars(term_data):
        #     print("%s = %r" % (attr, getattr(term_data, attr)))
