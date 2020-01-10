"""opis skryptu"""

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

DAYS_OF_WEEK = {'1': 'poniedziałek', '2': 'wtorek', '3': 'środa',
                '4': 'czwartek', '5': 'piątek', '6': 'sobota', '7': 'niedziela'}


class Info:
    """Stores information which objects to delete and what to write to Slack and at the end of script"""
    created_terms = 0
    updated_terms = 0
    created_courses = 0
    used_courses = 0
    all_updates = []
    all_creations = []
    all_deletions = []
    used_map_courses = []
    used_map_employees = []
    used_scheduler_ids = []


SlackUpdate = collections.namedtuple('Update', ['name', 'old', 'new'])


class SchedulerData:
    """ All useful data laid out from Scheduler API, list and tuples of SchedulerAPIGroup,
        SchedulerAPITerm, SchedulerAPIResult, SchedulerAPIEmployee"""
    groups = []
    terms = {}
    results = {}
    teachers = {}


# id inside this touple refers to SchedulerAPIResult id, we treat this id as scheduler_id
SchedulerAPIGroup = collections.namedtuple('Group', ['id', 'teacher', 'course', 'group_type', 'limit'])
# strings in terms list are id's of SchedulerAPITerm tuples
SchedulerAPIResult = collections.namedtuple('Result', ['rooms', 'terms'])
SchedulerAPITerm = collections.namedtuple('Term', ['day', 'start_hour', 'end_hour'])
SchedulerAPITeacher = collections.namedtuple('Teacher', ['first_name', 'last_name'])


class GroupData:
    """ Single group object data to save to SZ ( System Zapisów ) database"""
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
    def add_arguments(self, parser):
        parser.add_argument('--dry_run', action='store_true', help='no changes will be saved. Messages will'
                                                                   ' show up normally as without this flag')
        parser.add_argument('--slack', action='store_true', help='writes messages about changes to Slack')
        parser.add_argument('--delete_groups', action='store_true', help='delete unused terms, groups, employees maps'
                                                                         ' and courses maps')

    def create_or_update_group_and_term(self, group_data: 'GroupData', term_data: 'TermData'):
        """ Check if group already exists in database, then create or update that group. Does the same for term,
            unless update or create are set to False """
        try:
            sync_data_object = TermSyncData.objects.select_related(
                'term', 'term__group').prefetch_related('term__classrooms').get(
                scheduler_id=group_data.scheduler_id, term__group__course__semester=self.semester)

            self.info.used_scheduler_ids.append(sync_data_object.scheduler_id)
            diffs = []
            changed = False
            term = sync_data_object.term
            if term.group.course != group_data.course:
                raise CommandError(
                    f'Term \'{term}\' with group \'{term.group}\' changed course from \'{term.group.course}\''
                    f' to \'{group_data.course}\'\nPlease enter this change in django admin')

            if term.group.type != group_data.type:
                raise CommandError(
                    f'Term \'{term}\' with group \'{term.group}\' changed group typr from \'{term.group.type}\''
                    f' to \'{group_data.type}\'\nPlease enter this change in django admin')

            if term.dayOfWeek != term_data.dayOfWeek:
                changed = True
                diffs.append(
                    SlackUpdate('day of week', DAYS_OF_WEEK[term.dayOfWeek], DAYS_OF_WEEK[term_data.dayOfWeek]))
                term.dayOfWeek = term_data.dayOfWeek

            if term.start_time != term_data.start_time:
                changed = True
                diffs.append(SlackUpdate('start time', term.start_time, term_data.start_time))
                term.start_time = term_data.start_time

            if term.end_time != term_data.end_time:
                changed = True
                diffs.append(SlackUpdate('end time', term.end_time, term_data.end_time))
                term.end_time = term_data.end_time

            if set(term.classrooms.all()) != term_data.classrooms:
                changed = True
                diffs.append(SlackUpdate('classrooms', term.classrooms.all(), term_data.classrooms))
                term.classrooms.set(term_data.classrooms)

            if term.group.teacher != group_data.teacher:
                changed = True
                diffs.append(SlackUpdate('teacher', term.group.teacher, group_data.teacher))
                term.group.teacher = group_data.teacher

            if term.group.limit != group_data.limit:
                changed = True
                diffs.append(SlackUpdate('group limit', term.group.limit, group_data.limit))
                term.group.limit = group_data.limit

            if changed:
                term.save()
                term.group.save()
                self.stdout.write(self.style.SUCCESS('term: {} with group {} changes:'.format(term, term.group)))
                for diff in diffs:
                    self.stdout.write('  {}: '.format(diff[0]), ending='')
                    self.stdout.write(self.style.NOTICE(str(diff[1])), ending='')
                    self.stdout.write(' -> ', ending='')
                    self.stdout.write(self.style.SUCCESS(str(diff[2])))
                self.info.all_updates.append((term, diffs))
                self.info.updated_terms += 1
                self.stdout.write('')
        except TermSyncData.DoesNotExist:
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
            TermSyncData.objects.create(term=term, scheduler_id=group_data.scheduler_id)
            self.info.used_scheduler_ids.append(group_data.scheduler_id)
            self.info.created_terms += 1
            self.info.all_creations.append(term)
            self.stdout.write(self.style.SUCCESS('term: {} with group {} created\n'.format(term, group)))

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
            for room in rooms:
                try:
                    classrooms.add(Classroom.objects.get(number=room))
                except Classroom.DoesNotExist:
                    raise CommandError(f"Couldn't find classroom for {room}")
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

        def get_proposal(course_name: 'str') -> '(Proposal or None, bool)':
            """ return tuple of Proposal object from SZ database or None if course is set to not import. Second return
                True if CourseInstance with entered name should be mapped or False in opposite"""
            map = CourseMap.objects.filter(scheduler_course__iexact=course_name)
            if map.count():
                self.info.used_map_courses.append(map[0].pk)
                if map[0].course is None:
                    return (None, False)
                else:
                    return (map[0].course.offer, False)
            try:
                prop = Proposal.objects.get(
                    name__iexact=course_name, status__in=[ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE])
                return (prop, False)
            except Proposal.DoesNotExist:
                while True:
                    self.stdout.write(self.style.WARNING(">Couldn't find proposal for '{}' "
                                                         "which status is IN_OFFER or IN_VOTE".format(course_name)))
                    self.stdout.write("Please enter proper proposal name, so course instance could be found or created"
                                      " with this proposal \nLeave blank (press enter) to set this name to not import"
                                      " (CourseMap) and continue script. \nType 'quit' to quit script."
                                      " You will be asked again if course name cannot be found.")
                    new_course_name = input('Course name (Capitalization does not matter): ')
                    if not new_course_name:
                        map = CourseMap.objects.create(scheduler_course=course_name.upper(), course=None)
                        self.info.used_map_courses.append(map.pk)
                        self.stdout.write(self.style.SUCCESS(
                            ">Course '{}' was set to not import (CourseMap). Continue script..\n".format(course_name)))
                        return (None, False)
                    elif new_course_name == 'quit':
                        self.stdout.write('Exiting script..')
                        exit()
                    else:
                        prop = Proposal.objects.filter(name__iexact=new_course_name,
                                                status__in=[ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE])
                        if prop.count():
                            # recursion in case Proposal.MultipleObjectsReturned with new course name
                            prop, bool_dont_matter = get_proposal(new_course_name)
                            return (prop, True)

                    self.stdout.write(self.style.WARNING(">Still could't find proposal course '{}' which status is"
                                                             " IN_OFFER or IN_VOTE\n".format(new_course_name)))
            except Proposal.MultipleObjectsReturned:
                # Prefer proposals IN_VOTE to those IN_OFFER.
                props = Proposal.objects.filter(
                    name__iexact=course_name, status__in=[ProposalStatus.IN_OFFER,
                                                          ProposalStatus.IN_VOTE]).order_by('-status', '-id')
                self.stdout.write(self.style.WARNING('>Multiple course proposals. Took first among:'))
                for prop in props:
                    self.stdout.write(self.style.WARNING('  {}, status = {}'.format(prop, prop.status)))
                self.stdout.write("Leave blank (press enter) to contiue script."
                                  " Type 'quit' or anything else to quit script.")
                decision = input("Decision: ")
                if decision:
                    self.stdout.write('Exiting script..')
                    exit()
                prop = props[0]
                return (prop, False)

        def get_course(proposal: 'Proposal') -> 'CourseInstance':
            """ return CourseInstance object from SZ database"""
            course = None
            try:
                course = CourseInstance.objects.get(semester=self.semester, offer=proposal)
                self.info.used_courses += 1
            except CourseInstance.DoesNotExist:
                course = CourseInstance.create_proposal_instance(proposal, self.semester)
                self.info.created_courses += 1
                self.stdout.write(self.style.SUCCESS(">Course instance '{}' created\n".format(proposal.name)))
            return course

        def get_employee(username: 'str', teachers: 'Dict[str, str]') -> 'Employee':
            emp = Employee.objects.filter(user__username=username)
            if emp.count():
                return emp[0]
            else:
                map = EmployeeMap.objects.filter(scheduler_username=username)
                if map.count():
                    self.info.used_map_employees.append(map[0].pk)
                    return map[0].employee
                else:
                    first_name, last_name = teachers[username]
                    while True:
                        self.stdout.write(self.style.WARNING(
                            ">Employee with username '{}' not found".format(username)))
                        self.stdout.write(
                            "First name: {}, last name: {}\n"
                            "Please enter proper username. You will be asked again if username cannot be found.\n"
                            "Leave it blank (press enter) to set 'nieznany prowadzący'. Type 'quit' to quit script".
                            format(first_name, last_name))
                        new_username = input('Username: ')
                        if not new_username:
                            nieznany = Employee.objects.get(user__username='Nn')
                            map = EmployeeMap.objects.create(scheduler_username=username, employee=nieznany)
                            self.info.used_map_employees.append(map.pk)
                            self.stdout.write(self.style.SUCCESS(">Employee '{}' was set to 'nieznany prowadzacy."
                                                                 " Continue script..\n".format(username)))
                            return nieznany
                        elif new_username == 'quit':
                            self.stdout.write('Exiting script..')
                            exit()
                        else:
                            new_emp = Employee.objects.filter(user__username=new_username)
                            if new_emp.count():
                                map = EmployeeMap.objects.create(scheduler_username=username, employee=new_emp[0])
                                self.info.used_map_employees.append(map.pk)
                                self.stdout.write(self.style.SUCCESS(">Employee '{}' was set to '{}'. Continue"
                                                                     " script..\n".format(username, new_username)))
                                return new_emp[0]
                            self.stdout.write(
                                self.style.WARNING(">Username '{}' still not found\n".format(new_username)))

        scheduler_course = scheduler_data.groups[group_id].course
        scheduler_teacher = scheduler_data.groups[group_id].teacher
        scheduler_group_type = scheduler_data.groups[group_id].group_type

        group_data = GroupData()
        proposal, add_map = get_proposal(scheduler_course)
        if proposal is None:
            return group_data
        group_data.course = get_course(proposal)
        if add_map:
            map = CourseMap.objects.create(scheduler_course=scheduler_course.upper(), course=group_data.course)
            self.info.used_map_courses.append(map.pk)
            self.stdout.write(self.style.SUCCESS(">Course instance '{}' mapped (CourseMap)".format(group_data.course)))
        group_data.teacher = get_employee(scheduler_teacher, scheduler_data.teachers)
        group_data.type = get_group_type(scheduler_group_type)
        group_data.limit = scheduler_data.groups[group_id].limit
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
                limit = rec['students_num']
                data.append(SchedulerAPIGroup(id, teacher, course, group_type, limit))
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

    def prepare_slack_message(self):
        attachments = []
        for term in self.info.all_creations:
            text = "day: {}\nstart_time: {}\nend_time: {}\nteacher: {}".format(
                term.dayOfWeek, term.start_time, term.end_time, term.group.teacher
            )
            attachment = {
                "color": "good",
                "title": "Created: {}".format(term.group),
                "text": text
            }
            attachments.append(attachment)
        for term, diffs in self.info.all_updates:
            text = ""
            for diff in diffs:
                text = text + "{}: {}->{}\n".format(diff[0], diff[1], diff[2])
            attachment = {
                "color": "warning",
                "title": "Updated: {}".format(term.group),
                "text": text
            }
            attachments.append(attachment)
        for term_str, group_str in self.info.all_deletions:
            attachment = {
                "color": "danger",
                "title": "Deleted a term:",
                "text": "group: {}\nterm: {}".format(group_str, term_str)
            }
            attachments.append(attachment)
        return attachments

    def write_to_slack(self):
        slack_data = {
            'text': "The following groups were updated in fereol (scheduler's sync):",
            'attachments': self.prepare_slack_message()
        }
        secrets_env = self.get_secrets_env()
        slack_webhook_url = secrets_env.str('SLACK_WEBHOOK_URL')
        response = requests.post(
            slack_webhook_url, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )

    def remove_unused_maps_terms_groups(self):
        maps = CourseMap.objects.all()
        for map in maps:
            if map.pk not in self.info.used_map_courses:
                map.delete()
        maps = EmployeeMap.objects.all()
        for map in maps:
            if map.pk not in self.info.used_map_employees:
                map.delete()

        groups_to_remove = set()
        sync_data_objects = TermSyncData.objects.filter(term__group__course__semester=self.semester)
        for sync_data_object in sync_data_objects:
            if sync_data_object.scheduler_id not in self.info.used_scheduler_ids:
                groups_to_remove.add(sync_data_object.term.group)
                self.stdout.write(self.style.NOTICE('Term {} for group {} removed'.
                                                    format(sync_data_object.term, sync_data_object.term.group)))
                self.info.all_deletions.append((str(sync_data_object.term),
                                                str(sync_data_object.term.group)))
                sync_data_object.term.delete()
                sync_data_object.delete()
        for group in groups_to_remove:
            if not Term.objects.filter(group=group):
                group.delete()

    def import_from_api(self, delete_courses_flag, write_to_slack_flag):
        scheduler_data = self.get_scheduler_data()
        for group_id in range(len(scheduler_data.groups)):
            group_data = self.get_group_data(group_id, scheduler_data)
            # course is mapped to not import
            if group_data.course is None:
                continue
            term_data = self.get_term_data(group_data.scheduler_id, scheduler_data)
            self.create_or_update_group_and_term(group_data, term_data)

        if delete_courses_flag:
            self.remove_unused_maps_terms_groups()
        if write_to_slack_flag:
            self.write_to_slack()
        self.stdout.write(self.style.SUCCESS('Created {} courses successfully! '
                                             'Moreover {} courses were already there.'
                                             .format(self.info.created_courses, self.info.used_courses)))
        self.stdout.write(self.style.SUCCESS('Created {} terms and updated {} terms successfully!'
                                             .format(self.info.created_terms, self.info.updated_terms)))

    def handle(self, *args, **options):
        # potem zmień semestr by było ustawiane jako argument do komendy skryptu
        self.semester = Semester.objects.get(year="2018/19", type='l')
        self.info = Info()
        delete_courses_flag = options['delete_groups']
        dry_run_flag = options['dry_run']
        write_to_slack_flag = options['slack']

        if dry_run_flag:
            self.stdout.write('Dry run is on. Nothing will be saved or deleted. All messages are informational.\n\n')
            with transaction.atomic():
                self.import_from_api(delete_courses_flag, write_to_slack_flag)
                transaction.set_rollback(True)
            self.stdout.write('\nDry run was on. Nothing was saved or deleted. All messages were informational.')
        else:
            self.import_from_api(delete_courses_flag, write_to_slack_flag)
