from datetime import timedelta
from typing import List

from django import test
from freezegun import freeze_time

from apps.enrollment.courses.tests import factories as courses
from apps.enrollment.records.models import Record, RecordStatus
from apps.grade.poll.models import Poll
from apps.users.tests import factories as users


class APITest(test.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.student: users.Student = users.StudentFactory()
        cls.semester: courses.Semester = courses.SemesterFactory()
        course_exam = courses.CourseInstanceFactory(semester=cls.semester)
        course_no_exam = courses.CourseInstanceFactory(semester=cls.semester, has_exam=False)
        cls.groups: List[courses.Group] = [
            courses.GroupFactory(course=course_exam),
            courses.GroupFactory(course=course_no_exam)
        ]

    def test_polls_created(self):
        """Exactly four Polls should exist.

        One for each group, one for the exam and one for semester.
        """
        self.assertEqual(Poll.objects.all().count(), 4)

    def test_available_polls(self):
        Record.objects.create(student=self.student,
                              group=self.groups[0],
                              status=RecordStatus.ENROLLED)

        time_in_semester = self.semester.semester_grade_beginning
        time_after_semester = self.semester.semester_ending + timedelta(days=1)

        with freeze_time(time_after_semester):
            # When semester is gone, no Polls should be available.
            self.assertListEqual(Poll.get_all_polls_for_student(self.student), [])
        with freeze_time(time_in_semester):
            # Three Polls should be available to the student.
            self.assertEqual(len(Poll.get_all_polls_for_student(self.student)), 3)

        # Extend time for graded classes by a few after semester.
        self.semester.semester_grade_ending = \
            self.semester.semester_ending + timedelta(days=3)
        self.semester.save()

        with freeze_time(time_after_semester):
            # Three Polls should be available a day after end of the semester.
            self.assertEqual(len(Poll.get_all_polls_for_student(self.student)), 3)
        with freeze_time(time_in_semester):
            # Three Polls should be still available to the student.
            self.assertEqual(len(Poll.get_all_polls_for_student(self.student)), 3)
