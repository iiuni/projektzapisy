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
        time_in_semester = self.semester.semester_beginning + (self.semester.semester_ending -
                                                               self.semester.semester_beginning) / 2
        time_after_semester = self.semester.semester_ending + timedelta(days=1)
        with freeze_time(time_after_semester):
            # When semester is gone, no Polls should be available.
            self.assertListEqual(Poll.get_all_polls_for_student(self.student), [])
        with freeze_time(time_in_semester):
            # When grade is closed, no Polls should be available.
            self.assertListEqual(Poll.get_all_polls_for_student(self.student), [])

        self.semester.is_grade_active = True
        self.semester.save()
        with freeze_time(time_after_semester):
            # This still should be empty.
            self.assertListEqual(Poll.get_all_polls_for_student(self.student), [])
        with freeze_time(time_in_semester):
            # Three Polls should be available to the student.
            self.assertEqual(len(Poll.get_all_polls_for_student(self.student)), 3)
