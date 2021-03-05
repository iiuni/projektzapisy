from datetime import time

from django.test import TestCase

from apps.common import days_of_week
from apps.enrollment.courses.models.group import GroupType
from apps.schedulersync import scheduler_data

# Config file is an input to the Scheduler.
# We only use 'teachers', 'groups', and 'terms'.
config = {
    'id': 'wiosna-2',
    'year': 2021,
    'term': 1,
    'file': 'wiosna',
    'rooms': [{
        'capacity': 36,
        'id': '103',
        'labels': ['wyklad', 'cwiczenia', '103'],
        # A room may be booked outside of the Scheduler.
        'reservations': [{
            'day': 5,
            'end': {'hour': 21, 'minute': 0},
            'start': {'hour': 8, 'minute': 0},
            'title': 'Instytut Dziennikarstwa'
        }, {
            'day': 6,
            'end': {'hour': 21, 'minute': 0},
            'start': {'hour': 8, 'minute': 0},
            'title': 'Instytut Dziennikarstwa'
        }],
        # Terms are pre-defined time-slots.
        'terms': ['8', '9', '10', '11']
    }, {
        'capacity': 20,
        'id': '108',
        'labels': ['pracownia', 'windows', 'linux', '107'],
        'reservations': [],
        'terms': ['8', '9', '10', '11', '116', '117'],
    }],
    'teachers': [{
        # The usernames here often do not match those in Zapisy.
        'id': 'bchrobry',
        'extra': {
            'first_name': 'Bolesław',
            'last_name': 'Chrobry',
            'notes': '',
            'pensum': 90,
            # This is legacy. There was an (now abandoned) idea that we fix
            # incorrect usernames problem in Scheduler.
            'sz_username': None},
        # From Desiderata. Not used by us.
        'terms': ['18', '417', '116', '218', '17', '416', '316', '219', '117']
    }],
    # A "group" corresponds to a single term in Zapisy, not a single group.
    'groups': [{
        'diff_term_groups': [],
        'extra': {
            'course': 'Lepienie garnków (lato)',
            # Project
            'group_type': 'o',
            'notes': ''
        },
        'id': '122',
        # Expects a specific type of room.
        'room_labels': [[['pracownia']]],
        # This tells Scheduler to schedule different groups at the same time.
        'same_term_groups': [],
        'students_num': 15,
        'teachers': ['bchrobry'],
    }],
    # Describes all the time-slots. We DO use this.
    'terms': [
        {'id': '8', 'day': 0, 'start': {'hour': 8, 'minute': 15}, 'end': {'hour': 9, 'minute': 0}},
        {'id': '9', 'day': 0, 'start': {'hour': 9, 'minute': 15}, 'end': {'hour': 10, 'minute': 0}},
        {'id': '10', 'day': 0, 'start': {'hour': 10, 'minute': 15}, 'end': {'hour': 11, 'minute': 0}},
        {'id': '11', 'day': 0, 'start': {'hour': 11, 'minute': 15}, 'end': {'hour': 12, 'minute': 0}},
        {'id': '116', 'day': 1, 'start': {'hour': 16, 'minute': 15}, 'end': {'hour': 17, 'minute': 0}},
        {'id': '117', 'day': 1, 'start': {'hour': 17, 'minute': 15}, 'end': {'hour': 18, 'minute': 0}},
    ]
}  # yapf: disable


class SchedulerDataTestCase(TestCase):
    """Tests the data layer between Scheduler output and Zapisy."""

    def test_standard_data(self):
        """This test provides the functions with a standard scheduler output."""
        # Task file is a product of the Scheduler's run.
        # We do not care about its 'status',
        task = {'timetable': {'results': {
            # Every result is indexed by 'id' from config['groups'].
            '122': [{'room': '108', 'term': '116'}, {'room': '108', 'term': '117'}],
        }}}  # yapf: disable
        # Instantiate SchedulerData without credentials. We only test its
        # ability to understand data, not to fetch them.
        sd = scheduler_data.SchedulerData('', '', '', '', '')
        sd.lay_out_scheduler_data(config, task)
        self.assertCountEqual(sd.terms, [
            scheduler_data.SchTerm(
                scheduler_id=122,
                teacher='bchrobry',
                course='Lepienie garnków (lato)',
                type=GroupType.PROJECT,
                limit=15,
                dayOfWeek=days_of_week.TUESDAY,
                start_time=time(hour=16),
                end_time=time(hour=18),
                classrooms=['108'],
            )
        ])
        self.assertCountEqual(sd.teachers, {
            'bchrobry': 'Bolesław Chrobry',
        })
        self.assertCountEqual(sd.courses, ['Lepienie garnków (lato)'])
        self.assertCountEqual(sd.classrooms, ['108'])

    def test_unscheduled_group(self):
        """Gives group data in 'config' but no terms for it in 'task'."""
        task = {'timetable': {'results': {}}}
        sd = scheduler_data.SchedulerData('', '', '', '', '')
        sd.lay_out_scheduler_data(config, task)
        self.assertCountEqual(sd.terms, [])
        self.assertCountEqual(sd.teachers, {})
        self.assertCountEqual(sd.courses, [])
        self.assertCountEqual(sd.classrooms, [])

    def test_incorrect_term(self):
        """Schedules group in an undefined term."""
        task = {'timetable': {'results': {
            # Terms 20 and 21 are not defined.
            '122': [{'room': '108', 'term': '20'}, {'room': '108', 'term': '21'}],
        }}}  # yapf: disable
        sd = scheduler_data.SchedulerData('', '', '', '', '')
        with self.assertRaises(KeyError):
            # The function is expected to fail.
            sd.lay_out_scheduler_data(config, task)
