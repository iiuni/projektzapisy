import re
from datetime import time
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import requests

from apps.users.models import Employee
from apps.enrollment.courses.models import (
    Classroom, Course, Semester, CourseEntity, Group, Term
)
from apps.schedulersync.models import TermSyncData

URL_LOGIN = 'http://scheduler.gtch.eu/admin/login/'

SLACK_WEBHOOK_URL = (
    'https://hooks.slack.com/services/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'
)

LIMITS = {'1': 300, '9': 300, '2': 20, '3': 15, '5': 18, '6': 15}
GROUP_TYPES = {'w': '1', 'e': '9', 'c': '2', 'p': '3',
               'r': '5', 's': '6'}

EMPLOYEE_MAP = {
    'PWL': 'PWN',
    'MBI': 'MBIEŃKOWSKI',
    'KBACLAWSKI': 'KBACŁAWSKI',
    'MABI': 'MBIERNACKA',
    'PWI': '48',
    'IFD': 'IDO',
    'JMA': '31',
    'ANL': 'AŁU',
    'PAWIECZOREK': '526',
    'LPI': 'ŁPI',
    'DABI': 'DBIERNACKI',
    'MPIROG': 'MPIRÓG',
    'WKWASNICKI': 'WKWAŚNICKI',
    'ASIERON': 'ASIEROŃ',
    'ZPLOSKI': 'ZPŁOSKI',
    'ZSPLAWSKI': 'ZSPŁAWSKI',
    'PACHOLSKI LESZEK': 'LPA',
    'MML': 'MMŁ',
    'LJE': 'ŁJE',
    'MPI': 'MPIOTRÓW',
    'SZDUDYCZ': 'SDUDYCZ'
}

COURSES_MAP = {
    'ALGORYTMY I STRUKTURY DANYCH M': 'ALGORYTMY I STRUKTURY DANYCH (M)',
    'KURS PHP': 'Kurs: Projektowanie i implementacja zaawansowanych aplikacji PHP',
    'PROJEKT DYPLOMOWY (LATO)': 'PROJEKT DYPLOMOWY',
    'PROJEKT: SYSTEM ZAPISÓW (LATO)': 'PROJEKT: ROZWÓJ SYSTEMU ZAPISÓW',
    'PROJEKT ZESPOŁOWY: SILNIK UNITY3D I WIRTUALNA RZECZYWISTOŚĆ 2':
        'Projekt zespołowy: silnik Unity3D i wirtualna rzeczywistość LATO',
    'SEMINARIUM: ALGORYTMY  WYSZUKIWANIA ŚCIEŻEK': 'SEMINARIUM: ALGORYTMY WYSZUKIWANIA ŚCIEŻEK',
    'TUTORING (LATO)': 'Kształtowanie ścieżki akademicko-zawodowej'
}

COURSES_DONT_IMPORT = ['XIV LO LATO', 'ZASADY KRYTYCZNEGO MYŚLENIA']


class Command(BaseCommand):
    help = 'Imports the timetable for the next semester from the external scheduler.'

    def add_arguments(self, parser):
        parser.add_argument('url_assignments', help='Should look like this: '
                            '/scheduler/api/config/2017-18-lato3-2/')
        parser.add_argument('url_schedule', help='Should look like this: '
                            'http://scheduler.gtch.eu/scheduler/api/task/'
                            '07164b02-de37-4ddc-b81b-ddedab533fec/')
        parser.add_argument('-semester', type=int, default=0)
        parser.add_argument('--create_courses', action='store_true', dest='create_courses')
        parser.add_argument('--dry-run', action='store_true', dest='dry_run')
        parser.add_argument('--slack', action='store_true', dest='write_to_slack')
        parser.add_argument('--delete-groups', action='store_true', dest='delete_groups')

    def get_entity(self, name):
        name = name.upper()
        if name in COURSES_MAP:
            name = COURSES_MAP[name]
        if name in COURSES_DONT_IMPORT:
            return None
        ce = None
        try:
            ce = CourseEntity.objects.get(name_pl__iexact=name)
        except CourseEntity.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(">Couldn't find course entity for {}".format(name))
            )
        except CourseEntity.MultipleObjectsReturned:
            ces = CourseEntity.objects.filter(name_pl__iexact=name, status=2).order_by('-id')
            if self.verbosity >= 1:
                self.stdout.write(self.style.WARNING('Multiple course entity. Took first among:'))
                for ce in ces:
                    self.stdout.write(self.style.WARNING('  {}'.format(str(ce))))
                self.stdout.write('')
            ce = ces[0]
        return ce

    def get_course(self, entity, create_courses=False):
        course = None
        try:
            course = Course.objects.get(semester=self.semester, entity=entity)
            self.used_courses.add(course)
        except Course.DoesNotExist:
            if entity.slug is None:
                self.stdout.write(
                    self.style.ERROR("Couldn't find slug for {}".format(entity))
                )
            else:
                newslug = '{}_{}'.format(entity.slug,
                                         re.sub(r'[^\w]', '_', self.semester.get_short_name()))
                if create_courses:
                    course = Course(entity=entity, information=entity.information,
                                    semester=self.semester, slug=newslug)
                    course.save()
                    self.created_courses += 1
        return course

    def get_classrooms(self, rooms):
        classrooms = []
        for room in rooms:
            try:
                if room.replace(' ', '') != '':
                    classrooms.append(Classroom.objects.get(number=room))
            except Classroom.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR("Couldn't find classroom for {}".format(room))
                )
        return classrooms

    def get_employee(self, name):
        name = name.upper()
        if name in EMPLOYEE_MAP:
            name = EMPLOYEE_MAP[name]
        try:
            int(name)
            emps = Employee.objects.filter(id=name)
        except ValueError:
            if name == 'NN':
                emps = Employee.objects.filter(user__first_name='Nieznany')
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

    def create_or_update_group(self, course, data, create_terms=True):
        try:
            sync_data_object = TermSyncData.objects.get(scheduler_id=data['id'],
                                                        term__group__course__semester=self.semester)
        except TermSyncData.DoesNotExist:
            if create_terms:
                # Create the group in the enrollment system
                if data['group_type'] == '1':
                    # The lecture always has a single group but possibly many terms
                    group = Group.objects.get_or_create(course=course,
                                                        teacher=data['teacher'],
                                                        type=data['group_type'],
                                                        limit=data['limit'])[0]
                else:
                    group = Group.objects.create(course=course,
                                                 teacher=data['teacher'],
                                                 type=data['group_type'],
                                                 limit=data['limit'])
                term = Term.objects.create(dayOfWeek=data['dayOfWeek'],
                                           start_time=data['start_time'],
                                           end_time=data['end_time'],
                                           group=group)
                term.classrooms = data['classrooms']
                term.save()
                self.all_creations.append(term)
                TermSyncData.objects.create(term=term, scheduler_id=data['id'])
            self.stdout.write(self.style.SUCCESS('Group with scheduler_id={} created!'
                                                 .format(data['id'])))
            self.stdout.write(self.style.SUCCESS('  time: {}-{}'
                                                 .format(data['start_time'], data['end_time'])))
            self.stdout.write(self.style.SUCCESS('  teacher: {}'
                                                 .format(data['teacher'])))
            self.stdout.write(self.style.SUCCESS('  classrooms: {}\n'
                                                 .format(data['classrooms'])))
            self.created_terms += 1
        else:
            term = sync_data_object.term
            diff_track_fields = ['dayOfWeek', 'start_time', 'end_time']
            diffs = [(k, (getattr(term, k), data[k])) for k in diff_track_fields
                     if getattr(term, k) != data[k]]
            if term.group.type != data['group_type']:
                diffs.append(('type', (term.group.type, data['group_type'])))
            if term.group.teacher != data['teacher']:
                diffs.append(('teacher', (term.group.teacher, data['teacher'])))
            term.dayOfWeek = data['dayOfWeek']
            term.start_time = data['start_time']
            term.end_time = data['end_time']
            term.group.type = data['group_type']
            term.group.teacher = data['teacher']
            if set(term.classrooms.all()) != set(data['classrooms']):
                diffs.append(('classroom', (set(term.classrooms.all()), set(data['classrooms']))))
                if create_terms:
                    term.classrooms = data['classrooms']  # this already saves the relation!
            if diffs:
                if create_terms:
                    term.save()
                    term.group.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        'Group {} {} updated. Difference:'.format(term.group, term)
                    )
                )
                for diff in diffs:
                    self.stdout.write(self.style.WARNING('  {}: '.format(diff[0])), ending='')
                    self.stdout.write(self.style.NOTICE(diff[1][0]), ending='')
                    self.stdout.write(self.style.WARNING(' -> '), ending='')
                    self.stdout.write(self.style.SUCCESS(diff[1][1]))
                self.stdout.write('\n')
                self.all_updates.append((term, diffs))
                self.updated_terms += 1

    def prepare_group(self, g, results, terms):
        """Convert information about group from scheduler format."""
        if g['id'] not in results:
            return None
        group = {
            'id': g['id'],
            'entity_name': g['extra']['course'],
            'group_type': GROUP_TYPES[g['extra']['group_type']],
            'teacher': self.get_employee(g['teachers'][0])
        }

        # start_time will be determined as the minimum start_time among all terms
        # end_time - as maximum. All the terms in scheduler are one hour long.
        start_time = 24  # acts as inifinity
        end_time = 0
        classrooms = set()
        for t in results[g['id']]:
            t_start = terms[t['term']]['start']['hour']
            t_end = terms[t['term']]['end']['hour']
            if t_start < start_time:
                start_time = t_start
            if t_end > end_time:
                end_time = t_end
            group['dayOfWeek'] = str(terms[t['term']]['day'] + 1)
            classrooms.add(t['room'])
        group['start_time'] = time(hour=int(start_time))
        group['end_time'] = time(hour=int(end_time))
        group['classrooms'] = self.get_classrooms(list(classrooms))
        group['limit'] = LIMITS[group['group_type']]
        return group

    def get_groups(self):
        client = requests.session()
        client.get(URL_LOGIN)
        csrftoken = client.cookies['csrftoken']
        login_data = {'username': 'test', 'password': 'test', 'csrfmiddlewaretoken': csrftoken,
                      'next': self.url_assignments}
        r = client.post(URL_LOGIN, data=login_data)
        r2 = client.get(self.url_schedule)
        results = r2.json()['timetable']['results']
        groups = []
        terms = {}
        data = r.json()
        for t in data['terms']:
            terms[t['id']] = t
        for g in data['groups']:
            prepared_group = self.prepare_group(g, results, terms)
            if prepared_group is not None:
                groups.append(prepared_group)
            else:
                self.stdout.write(self.style.WARNING('Group number {} does not have a term ({})\n'
                                                     .format(g['id'], g['extra']['course'])))
        return groups

    def remove_groups(self):
        groups_to_remove = set()
        sync_data_objects = TermSyncData.objects.filter(term__group__course__semester=self.semester)
        for sync_data_object in sync_data_objects:
            if sync_data_object.scheduler_id not in self.scheduler_ids:
                groups_to_remove.add(sync_data_object.term.group)
                self.stdout.write(
                    self.style.NOTICE(
                        'Term {} for group {} removed\n' .format(
                            sync_data_object.term,
                            sync_data_object.term.group)))
                self.all_deletions.append((str(sync_data_object.term),
                                           str(sync_data_object.term.group)))
                if self.delete_groups:
                    sync_data_object.term.delete()
                    sync_data_object.delete()
        for group in groups_to_remove:
            if not Term.objects.filter(group=group):
                if self.remove_groups:
                    group.delete()

    @transaction.atomic
    def import_from_api(self, create_courses=False, create_terms=True):
        self.created_terms = 0
        self.updated_terms = 0
        self.created_courses = 0
        self.all_updates = []
        self.all_creations = []
        self.all_deletions = []
        self.used_courses = set()
        self.scheduler_ids = set()
        groups = self.get_groups()
        for g in groups:
            self.scheduler_ids.add(int(g['id']))
            entity = self.get_entity(g['entity_name'])
            if entity is not None:
                course = self.get_course(entity, create_courses)
                if course is None:
                    raise CommandError('Course {} does not exist! Check your input file.'
                                       .format(entity))
                self.create_or_update_group(course, g, create_terms)
        self.remove_groups()
        self.stdout.write(self.style.SUCCESS('Created {} courses successfully! '
                                             'Moreover {} courses were already there.'
                                             .format(self.created_courses, len(self.used_courses))))
        self.stdout.write(self.style.SUCCESS('Created {} terms and updated {} terms successfully!'
                                             .format(self.created_terms, self.updated_terms)))

    def prepare_slack_message(self):
        attachments = []
        for term in self.all_creations:
            text = "day: {}\nstart_time: {}\nend_time: {}\nteacher: {}".format(
                term.dayOfWeek, term.start_time, term.end_time, term.group.teacher
            )
            attachment = {
                "color": "good",
                "title": "Created: {}".format(term.group),
                "text": text
            }
            attachments.append(attachment)
        for term, diffs in self.all_updates:
            text = ""
            for diff in diffs:
                text = text + "{}: {}->{}\n".format(diff[0], diff[1][0], diff[1][1])
            attachment = {
                "color": "warning",
                "title": "Updated: {}".format(term.group),
                "text": text
            }
            attachments.append(attachment)
        for term_str, group_str in self.all_deletions:
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
        response = requests.post(
            SLACK_WEBHOOK_URL, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )

    def handle(self, *args, **options):
        self.semester = (Semester.objects.get_next() if options['semester'] == 0
                         else Semester.objects.get(pk=int(options['semester'])))
        self.url_assignments = options['url_assignments']
        self.url_schedule = options['url_schedule']
        self.verbosity = options['verbosity']
        if self.verbosity >= 1:
            self.stdout.write('Adding to semester: {}\n'.format(self.semester))
        self.delete_groups = True if options['delete_groups'] else False
        if options['dry_run']:
            if self.verbosity >= 1:
                self.stdout.write('Dry run is on. Nothing will be saved.')
            self.import_from_api(False, False)
        else:
            self.import_from_api(options['create_courses'])
        if options['write_to_slack']:
            self.write_to_slack()
