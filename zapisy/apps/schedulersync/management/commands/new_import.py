"""The script is used to fetch data from the Scheduler.

 Requires system variables: SLACK_WEBHOOK_URL, SCHEDULER_USERNAME, SCHEDULER_PASSWORD
 Required arguments are links to the api scheduler.
 First to api/config, second to api/task.
 The third argument is semester primary key. It is optional.
 Lack of third argument will result in running with the current semester.
 When using for the first time in a new semester, do not use the --slack flag,
 because writing to Slack so much notifications will cause an error.

 Without --interactive flag not found courses and employees will be mapped to
 not to import them in the future and they will not be imported. When the
 --slack flag is used, appropriate notifications will be sent to Slack about
 the mappings.

 The --slack flag sends notifications about changes in terms, groups, courses,
    proposals, employee and courses maps. Changes also include deleting
    and creating new objects.
 The --dont_delete_terms flag stops removing unused terms with groups
    in a given semester. It shouldn't be used. However,
    if for some reason you do want to use it, you can do it during manually usage.
 The --iteractive flag causes the script to execute with interaction. Use it
    for making sensible mappings.
 The --dry_run flag causes all changes to the database to be undone at the end
    of the script. The changes will be undone if an error occurs during
    the script execution or it is exited before end.
    It can be safely used for testing.

 Instructions for using flags:
    First use / manual: never --slack on first use in semester, use later,
        always --interactive, you shouldn't use --dont_delete_terms,
        --dry_run freely for testing - recommended on first use
    During the semester / automatic: always --slack, never --interactive,
        never --dont_delete_terms, never --dry_run
 Example usage: python manage.py import_schedule http://scheduler.gtch.eu/scheduler/api/config/wiosna-2019-2/
    http://scheduler.gtch.eu/scheduler/api/task/096a8260-5151-4491-82a0-f8e43e7be918/ --dry_run --delete_groups
"""

import collections
import json
import os
from datetime import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import environ
import requests
from apps.enrollment.courses.models import CourseInstance
from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.term import Term
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.schedulersync.models import CourseMap, EmployeeMap, TermSyncData
from apps.users.models import Employee


# The mapping between group types in scheduler and enrollment system
# w (wykład), p (pracownia), c (ćwiczenia), s (seminarium), r (ćwiczenio-pracownia),
# e (repetytorium), o (projekt), t (tutoring), m (proseminarium)
GROUP_TYPES = {'w': '1', 'e': '9', 'c': '2', 'p': '3',
               'r': '5', 's': '6', 'o': '10', 't': '11', 'm': '12'}

DAYS_OF_WEEK = {'1': 'poniedziałek', '2': 'wtorek', '3': 'środa',
                '4': 'czwartek', '5': 'piątek', '6': 'sobota', '7': 'niedziela'}


class Summary:
    """Stores information which objects to delete and what to write to Slack and at the end of script"""
    def __init__(self):
        self.created_courses = 0
        self.used_courses = 0
        self.updated_terms = []
        self.created_terms = []
        self.deleted_terms = []
        self.used_scheduler_ids = []
        self.multiple_proposals = []
        self.maps_added = []
        self.maps_deleted = []


SlackUpdate = collections.namedtuple('Update', ['name', 'old', 'new'])


class SchedulerData:
    """ All useful data laid out from Scheduler API, list and tuples of SchedulerAPIGroup,
        SchedulerAPITerm, SchedulerAPIResult, SchedulerAPIEmployee"""
    def __init__(self):
        self.groups = []
        self.terms = {}
        self.results = {}
        self.teachers = {}


# id inside this touple refers to SchedulerAPIResult id, we treat this id as scheduler_id
SchedulerAPIGroup = collections.namedtuple('Group', ['id', 'teacher', 'course', 'group_type', 'limit'])
# strings in terms list are id's of SchedulerAPITerm tuples
SchedulerAPIResult = collections.namedtuple('Result', ['rooms', 'terms'])
SchedulerAPITerm = collections.namedtuple('Term', ['day', 'start_hour', 'end_hour'])
SchedulerAPITeacher = collections.namedtuple('Teacher', ['first_name', 'last_name'])


class GroupData:
    """ Single group object data to save to SZ ( System Zapisów ) database"""
    def __init__(self):
        self.scheduler_id = int
        self.course = None
        self.teacher = None
        self.type = str
        self.limit = int


class TermData:
    """ Single term object data to save to SZ ( System Zapisów ) database"""
    def __init__(self):
        self.dayOfWeek = str
        self.start_time = time
        self.end_time = time
        self.group = None
        self.classrooms = set()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--dry_run', action='store_true', help='no changes will be saved. Messages will'
                                                                   ' show up normally as without this flag')
        parser.add_argument('--slack', action='store_true', help='writes messages about changes to Slack')
        parser.add_argument('--dont_delete_terms', action='store_true', help='unused terms and groups will not'
                                                                             ' be deleted (in chosen semester)')
        parser.add_argument('--interactive', action='store_true', help='script will need keyboard interaction. Use'
                            ' this during manually usage.')

    def create_or_update_group_and_term(self, group_data: 'GroupData', term_data: 'TermData'):
        """ Check if group already exists in database, then create or update that group. Does the same for term,
            unless update or create are set to False """
        try:
            sync_data_object = TermSyncData.objects.select_related(
                'term', 'term__group').prefetch_related('term__classrooms').get(
                scheduler_id=group_data.scheduler_id, term__group__course__semester=self.semester)

            self.summary.used_scheduler_ids.append(sync_data_object.scheduler_id)
            diffs = []
            term = sync_data_object.term
            if term.group.course != group_data.course:
                raise CommandError(
                    f'Term \'{term}\' with group \'{term.group}\' changed course from \'{term.group.course}\''
                    f' to \'{group_data.course}\'\nPlease enter this change in django admin')

            if term.group.type != group_data.type:
                raise CommandError(
                    f'Term \'{term}\' with group \'{term.group}\' changed group type from \'{term.group.type}\''
                    f' to \'{group_data.type}\'\nPlease enter this change in django admin')

            def prop_updater(a, b, props):
                """Updates selected fields of a with b.
                 Both objects must have the fields specified in `props` defined.
                Returns:
                        List of SlackUpdate objects describing the updates.
                """
                diffs = []
                for prop in props:
                    term_val = getattr(a, prop)
                    sched_val = getattr(b, prop)
                    if term_val != sched_val:
                        diffs.append(SlackUpdate(prop, term_val, sched_val))
                        setattr(a, prop, sched_val)
                return diffs

            diffs.extend(prop_updater(term, term_data, ['dayOfWeek', 'start_time', 'end_time']))
            diffs.extend(prop_updater(term.group, group_data, ['teacher', 'limit']))

            if set(term.classrooms.all()) != term_data.classrooms:
                diffs.append(SlackUpdate('classrooms', term.classrooms.all(), term_data.classrooms))
                term.classrooms.set(term_data.classrooms)

            if diffs:
                term.save()
                term.group.save()
                self.stdout.write(self.style.SUCCESS('term: {} with group {} changes:'.format(term, term.group)))
                for diff in diffs:
                    self.stdout.write('  {}: '.format(diff.name), ending='')
                    self.stdout.write(self.style.NOTICE(str(diff.old)), ending='')
                    self.stdout.write(' -> ', ending='')
                    self.stdout.write(self.style.SUCCESS(str(diff.new)))
                self.summary.updated_terms.append((term, diffs))
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
            self.summary.used_scheduler_ids.append(group_data.scheduler_id)
            self.summary.created_terms.append(term)
            self.stdout.write(self.style.SUCCESS('term: {} with group {} created\n'.format(term, group)))

    def get_term_data(self, scheduler_id: int, scheduler_data: 'SchedulerData') -> TermData:
        """ Fill TermData object with data necessary to save group to SZ database, but without group,
            because it refers to group object saved in SZ database """

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

    def get_group_data(self, scheduler_group: SchedulerAPIGroup, scheduler_data: SchedulerData,
                       interactive: bool = True) -> GroupData:
        """ Fill GroupData object with data necessary to save group to SZ database"""

        def get_group_type(group_type: 'str') -> 'str':
            """ map scheduler group type to SZ group type"""
            return GROUP_TYPES[group_type]

        def get_proposal(course_name: str, interactive: bool = True) -> 'Optional[Proposal]':
            """Finds a proposal in offer with a given name.

             If the proposal is not found, in interactive mode this function will
             prompt the user for the correct proposal and add it to the mapping.

            Returns:
                    Proposal if the match is found or None if the course should be ignored.
            """
            # First try the mapping.
            try:
                return CourseMap.objects.get(scheduler_course__iexact=course_name).proposal
            except CourseMap.DoesNotExist:
                pass
            # In interactive mode we will try to find proposal until we succeed.
            name = course_name
            while True:
                error = ""
                try:
                    proposal = None if name == 'None' else Proposal.objects.filter(
                        status__in=[ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE]).get(name__iexact=name)
                    if name != course_name:
                        CourseMap.objects.create(scheduler_course=course_name.upper(), proposal=proposal)
                        self.summary.maps_added.append((scheduler_course, str(proposal)))
                        self.stdout.write(self.style.SUCCESS(">Proposal '{}' mapped".format(proposal)))
                    return proposal
                except Proposal.DoesNotExist:
                    error = "No proposal was found"
                    if not interactive:
                        map = CourseMap.objects.create(scheduler_course=course_name.upper(), proposal=None)
                        self.summary.maps_added.append((course_name, "None"))
                        return None
                except Proposal.MultipleObjectsReturned:
                    error = "Multiple proposal were found"
                    if not interactive:
                        self.summary.multiple_proposals.append(course_name)
                        return None
                self.stdout.write(f"{error} for name {name}\nPlease provide correct name of the course "
                    "proposal in the database.\nType 'None' to mark the course to be ignored.")
                name = input('Proposal name (Capitalization does not matter): ')
                self.stdout.write("\n")

        def get_course(proposal: 'Proposal') -> 'CourseInstance':
            """ return CourseInstance object from SZ database"""
            course = None
            try:
                course = CourseInstance.objects.get(semester=self.semester, offer=proposal)
                self.summary.used_courses += 1
            except CourseInstance.DoesNotExist:
                course = CourseInstance.create_proposal_instance(proposal, self.semester)
                self.summary.created_courses += 1
                self.stdout.write(self.style.SUCCESS(">Course instance '{}' created\n".format(proposal.name)))
            return course

        def get_employee(username: str, full_name: str, interactive: bool = True) -> Employee:
            """Finds matching employee in the database.

            If the employee with a given username is not found, in interactive
            mode it will ask the user to provide correct username and add it to
            the mapping.

            Args:
                username: The username coming from Scheduler API.
                full_name: The full name of the employee for convenience of the
                    interactive mode.
                interactive: A boolean flag enabling interactive mode.

            Returns:
                The matched Employee object or 'Nieznany Prowadzący' object
            """
            # First, use the mapping.
            try:
                return EmployeeMap.objects.get(scheduler_username=username).employee
            except EmployeeMap.DoesNotExist:
                pass

            # In interactive mode we will try to find the employee until we
            # succeed.
            sh_username = username
            while True:
                try:
                    emp = Employee.objects.get(user__username='Nn') if username == 'None' \
                        else Employee.objects.get(user__username=username)
                    if sh_username != username:
                        EmployeeMap.objects.create(scheduler_username=sh_username, employee=emp)
                        self.summary.maps_added.append((username, str(emp)))
                    return emp
                except Employee.DoesNotExist:
                    pass
                if not interactive:
                    nieznany = Employee.objects.get(user__username='Nn')
                    EmployeeMap.objects.create(scheduler_username=username, employee=nieznany)
                    self.summary.maps_added.append((username, str(nieznany)))
                    return nieznany
                self.stdout.write(
                    f"No employee found for username {username}\nPlease provide the correct "
                    f"username for {full_name}.\nType 'None' if that teacher should be replaced with "
                    "'Nieznany Prowadzący'")
                username = input("Username: ")
                self.stdout.write("\n")


        group_data = GroupData()
        proposal = get_proposal(scheduler_group.course, interactive)
        if proposal is None:
            return group_data
        group_data.course = get_course(proposal)
        first_name, last_name = scheduler_data.teachers[scheduler_group.teacher]
        group_data.teacher = get_employee(scheduler_group.teacher, first_name + " " + last_name, interactive)
        group_data.type = get_group_type(scheduler_group.group_type)
        group_data.limit = scheduler_group.limit
        group_data.scheduler_id = scheduler_group.id
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
                rooms = set(rec['room'] for rec in results[id])
                terms = set(int(rec['term']) for rec in results[id])
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
        for term in self.summary.created_terms:
            text = "day: {}\nstart_time: {}\nend_time: {}\nteacher: {}".format(
                term.dayOfWeek, term.start_time, term.end_time, term.group.teacher
            )
            attachment = {
                "color": "good",
                "title": "Created: {}".format(term.group),
                "text": text
            }
            attachments.append(attachment)
        for term, diffs in self.summary.updated_terms:
            text = ""
            for diff in diffs:
                text = text + "{}: {}->{}\n".format(diff[0], diff[1], diff[2])
            attachment = {
                "color": "warning",
                "title": "Updated: {}".format(term.group),
                "text": text
            }
            attachments.append(attachment)
        for term_str, group_str in self.summary.deleted_terms:
            attachment = {
                "color": "danger",
                "title": "Deleted a term:",
                "text": "group: {}\nterm: {}".format(group_str, term_str)
            }
            attachments.append(attachment)
        for scheduler_data_str, map_str in self.summary.maps_added:
            attachment = {
                "color": "good",
                "title": "Added map:",
                "text": "{} mapped to {}".format(scheduler_data_str, map_str)
            }
            attachments.append(attachment)
        for prop_str in self.summary.multiple_proposals:
            attachment = {
                "color": "warning",
                "title": "Multiple proposals:",
                "text": "proposal {} has multiple instances with different status".format(prop_str)
            }
            attachments.append(attachment)
        return attachments

    def write_to_slack(self):
        slack_data = {
            'text': "The following groups were updated in fereol (scheduler's sync):",
            'attachments': self.prepare_slack_message()
        }
        slack_webhook_url = os.environ['slack_url']
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
        groups_to_remove = set()
        sync_data_objects = TermSyncData.objects.filter(term__group__course__semester=self.semester)
        for sync_data_object in sync_data_objects:
            if sync_data_object.scheduler_id not in self.summary.used_scheduler_ids:
                groups_to_remove.add(sync_data_object.term.group)
                self.stdout.write(self.style.NOTICE('Term {} for group {} removed'.
                                                    format(sync_data_object.term, sync_data_object.term.group)))
                self.summary.deleted_terms.append((str(sync_data_object.term),
                                                   str(sync_data_object.term.group)))
                sync_data_object.term.delete()
                sync_data_object.delete()
        for group in groups_to_remove:
            if not Term.objects.filter(group=group):
                group.delete()

    def import_from_api(self, dont_delete_terms_flag, write_to_slack_flag, interactive_flag):
        scheduler_data = self.get_scheduler_data()
        for scheduler_group in scheduler_data.groups:
            group_data = self.get_group_data(scheduler_group, scheduler_data, interactive_flag)
            # course is mapped to not import
            if group_data.course is None:
                continue
            term_data = self.get_term_data(group_data.scheduler_id, scheduler_data)
            self.create_or_update_group_and_term(group_data, term_data)

        if not dont_delete_terms_flag:
            self.remove_unused_maps_terms_groups()
        if write_to_slack_flag:
            self.write_to_slack()
        self.stdout.write(self.style.SUCCESS('Created {} courses successfully! '
                                             'Moreover {} courses were already there.'
                                             .format(self.summary.created_courses, self.summary.used_courses)))
        self.stdout.write(self.style.SUCCESS('Created {} terms and updated {} terms successfully!'
                                             .format(len(self.summary.created_terms), len(self.summary.updated_terms))))

    def handle(self, *args, **options):
        # potem zmień semestr by było ustawiane jako argument do komendy skryptu
        self.semester = Semester.objects.get(year="2018/19", type='l')
        self.summary = Summary()
        dont_delete_terms_flag = options['dont_delete_terms']
        dry_run_flag = options['dry_run']
        write_to_slack_flag = options['slack']
        interactive_flag = options['interactive']

        if dry_run_flag:
            self.stdout.write('Dry run is on. Nothing will be saved or deleted. All messages are informational.\n\n')
            with transaction.atomic():
                self.import_from_api(dont_delete_terms_flag, write_to_slack_flag, interactive_flag)
                transaction.set_rollback(True)
            self.stdout.write('\nDry run was on. Nothing was saved or deleted. All messages were informational.')
        else:
            self.import_from_api(dont_delete_terms_flag, write_to_slack_flag, interactive_flag)
