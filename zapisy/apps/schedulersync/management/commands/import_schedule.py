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
 The --interactive flag causes the script to execute with interaction. Use it
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

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.term import Term
from apps.schedulersync.models import TermSyncData

from .scheduler_data import SchedulerData
from .scheduler_mapper import SchedulerMapper
from .slack import Slack


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
# id inside this touple refers to SchedulerAPIResult id, we treat this id as scheduler_id
SchedulerAPIGroup = collections.namedtuple('Group', ['id', 'teacher', 'course', 'group_type', 'limit'])
# strings in terms list are id's of SchedulerAPITerm tuples
SchedulerAPIResult = collections.namedtuple('Result', ['rooms', 'terms'])
SchedulerAPITerm = collections.namedtuple('Term', ['day', 'start_hour', 'end_hour'])
SchedulerAPITeacher = collections.namedtuple('Teacher', ['first_name', 'last_name'])


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--dry_run', action='store_true', help='no changes will be saved. Messages will'
                                                                   ' show up normally as without this flag')
        parser.add_argument('--slack', action='store_true', help='writes messages about changes to Slack')
        parser.add_argument('--dont_delete_terms', action='store_true', help='unused terms and groups will not'
                                                                             ' be deleted (in chosen semester)')
        parser.add_argument('--interactive', action='store_true', help='script will need keyboard interaction. Use'
                                                                       ' this during manually usage.')

    def create_or_update_group_and_term(self, term_data: 'SZTerm'):
        """ Check if group already exists in database, then create or update that group. Does the same for term,
            unless update or create are set to False """
        try:
            sync_data_object = TermSyncData.objects.select_related(
                'term', 'term__group').prefetch_related('term__classrooms').get(
                scheduler_id=term_data.scheduler_id, term__group__course__semester=self.semester)

            self.summary.used_scheduler_ids.append(sync_data_object.scheduler_id)
            diffs = []
            term = sync_data_object.term
            if term.group.course != term_data.course:
                raise CommandError(
                    f'Term \'{term}\' with group \'{term.group}\' changed course from \'{term.group.course}\''
                    f' to \'{term_data.course}\'\nPlease enter this change in django admin')

            if term.group.type != term_data.type:
                raise CommandError(
                    f'Term \'{term}\' with group \'{term.group}\' changed group type from \'{term.group.type}\''
                    f' to \'{term_data.type}\'\nPlease enter this change in django admin')

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
            diffs.extend(prop_updater(term.group, term_data, ['teacher', 'limit']))

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
            if term_data.type == 1:
                group = Group.objects.get_or_create(course=term_data.course, teacher=term_data.teacher,
                                                    type=term_data.type, limit=term_data.limit)[0]
            else:
                group = Group.objects.create(course=term_data.course, teacher=term_data.teacher,
                                             type=term_data.type, limit=term_data.limit)
            term = Term.objects.create(dayOfWeek=term_data.dayOfWeek, start_time=term_data.start_time,
                                       end_time=term_data.end_time, group=group)
            term.classrooms.set(term_data.classrooms)
            TermSyncData.objects.create(term=term, scheduler_id=term_data.scheduler_id)
            self.summary.used_scheduler_ids.append(term_data.scheduler_id)
            self.summary.created_terms.append(term)
            self.stdout.write(self.style.SUCCESS('term: {} with group {} created\n'.format(term, group)))

    def remove_unused_terms_groups(self):
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
        scheduler_data = SchedulerData('http://scheduler.gtch.eu/scheduler/api/config/wiosna-2019-2/',
                                       'http://scheduler.gtch.eu/scheduler/api/task/096a8260-5151-4491'
                                       '-82a0-f8e43e7be918/')
        scheduler_data.get_scheduler_data()
        scheduler_mapper = SchedulerMapper(interactive_flag, self.summary, self.semester)
        scheduler_mapper.map_scheduler_data(scheduler_data)
        for term in scheduler_data.terms:
            if term.course is not None:
                self.create_or_update_group_and_term(term)

        if not dont_delete_terms_flag:
            self.remove_unused_terms_groups()
        if write_to_slack_flag:
            slack = Slack()
            slack.prepare_slack_message(self.summary)
            slack.write_to_slack()
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
            self.stdout.write('All changes to database are committed instantly.\n\n')
            self.import_from_api(dont_delete_terms_flag, write_to_slack_flag, interactive_flag)
