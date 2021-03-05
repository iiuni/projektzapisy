from datetime import time

from django.test import TestCase

from apps.common import days_of_week
from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.group import Group, GroupType
from apps.enrollment.courses.models.term import Term
from apps.enrollment.courses.tests import factories as courses_factories
from apps.schedulersync.management.commands.import_schedule import Command, SZTerm, Slack
from apps.users.tests import factories as users_factories


class SchedulerImportTestCase(TestCase):
    """Tests the subsequent import operation between Scheduler and Zapisy."""
    @classmethod
    def setUpTestData(cls):
        cls.bolek = users_factories.EmployeeFactory()
        cls.lolek = users_factories.EmployeeFactory()

        cls.r1 = courses_factories.ClassroomFactory()

        # Semester one will have no groups yet. It will have CourseInstances
        # created by SchedulerMapper.
        cls.s1 = courses_factories.SemesterFactory()
        cls.c1 = courses_factories.CourseInstanceFactory(semester=cls.s1)

    def test_import(self):
        """Imports a simple schedule.

        We test subsequent operations in subtests, so the failure is traceable
        and we do not need to prepare separate data for each test
        (https://stackoverflow.com/a/50868492).
        """
        terms = [
            SZTerm(scheduler_id=1,
                   teacher=self.bolek,
                   course=self.c1,
                   type=GroupType.LECTURE,
                   limit=25,
                   dayOfWeek=days_of_week.MONDAY,
                   start_time=time(hour=12),
                   end_time=time(hour=14),
                   classrooms=[self.r1]),
            SZTerm(scheduler_id=2,
                   teacher=self.bolek,
                   course=self.c1,
                   type=GroupType.LECTURE,
                   limit=25,
                   dayOfWeek=days_of_week.THURSDAY,
                   start_time=time(hour=8),
                   end_time=time(hour=10),
                   classrooms=[self.r1]),
            SZTerm(scheduler_id=3,
                   teacher=self.bolek,
                   course=self.c1,
                   type=GroupType.EXERCISES,
                   limit=13,
                   dayOfWeek=days_of_week.MONDAY,
                   start_time=time(hour=10),
                   end_time=time(hour=12),
                   classrooms=[self.r1]),
            SZTerm(scheduler_id=4,
                   teacher=self.bolek,
                   course=self.c1,
                   type=GroupType.EXERCISES,
                   limit=13,
                   dayOfWeek=days_of_week.THURSDAY,
                   start_time=time(hour=10),
                   end_time=time(hour=12),
                   classrooms=[self.r1]),
        ]

        with self.subTest(msg="Fresh import"):
            """No groups are in the database yet."""
            ims = Command()
            ims.semester = self.s1
            ims.update_terms(terms, False)
            self.assertEqual(CourseInstance.objects.count(), 1)
            # Two lecture group terms should be merged.
            self.assertEqual(self.c1.groups.count(), 3)
            self.assertEqual(self.c1.groups.get(type=GroupType.LECTURE).term.count(), 2)
            self.assertEqual(Term.objects.count(), 4)
            # All these groups should be taught by Bolek.
            self.assertEqual(Group.objects.filter(teacher=self.bolek).count(), 3)

        with self.subTest(msg="Add new term"):
            """New term is added. It creates a new group for the second course."""
            # Second course will be created by the mapper.
            self.c2 = courses_factories.CourseInstanceFactory(semester=self.s1)
            terms.append(
                SZTerm(scheduler_id=5,
                       teacher=self.lolek,
                       course=self.c2,
                       type=GroupType.LAB,
                       limit=13,
                       dayOfWeek=days_of_week.THURSDAY,
                       start_time=time(hour=10),
                       end_time=time(hour=12),
                       classrooms=[self.r1]))
            ims = Command()
            ims.semester = self.s1
            ims.update_terms(terms, False)
            # Nothing should change for the first course.
            self.assertEqual(self.c1.groups.count(), 3)
            t = Term.objects.filter(group__course=self.c1, group__type=GroupType.EXERCISES).first()
            self.assertCountEqual(t.classrooms.all(), [self.r1])
            # A new group should be created for the second course.
            self.assertEqual(self.c2.groups.count(), 1)

        with self.subTest(msg="None mappings"):
            """Terms with course=None should be ignored."""
            # course=None means that the course could not be identified by the mapper.
            terms.append(
                SZTerm(scheduler_id=7,
                       teacher=self.lolek,
                       course=None,
                       type=GroupType.EXERCISES,
                       limit=13,
                       dayOfWeek=days_of_week.THURSDAY,
                       start_time=time(hour=10),
                       end_time=time(hour=12),
                       classrooms=[self.r1]))
            ims = Command()
            ims.semester = self.s1
            ims.update_terms(terms, False)
            slack = Slack("")
            slack.prepare_message(ims.summary)
            slack.write_to_screen()
            # No new groups should turn up.
            self.assertEqual(self.c1.groups.count(), 3)
            self.assertEqual(self.c2.groups.count(), 1)
            self.assertEqual(Group.objects.count(), 4)
            self.assertEqual(Term.objects.count(), 5)

        with self.subTest(msg="Do not delete flag"):
            """Removing terms with and without dont_delete_terms flag."""
            # We leave only c1 terms. One is unscheduled and one has unknown teacher.
            terms = terms[:4]
            ims = Command()
            ims.semester = self.s1
            ims.update_terms(terms, True)
            # No terms will be deleted.
            self.assertEqual(CourseInstance.objects.count(), 2)
            self.assertEqual(Group.objects.count(), 4)
            self.assertEqual(Term.objects.count(), 5)

            ims.update_terms(terms, False)
            # This should delete entire c2 and only leave 3 groups of c1.
            self.assertEqual(CourseInstance.objects.count(), 1)
            self.assertEqual(Group.objects.count(), 3)
            self.assertEqual(Term.objects.count(), 4)
