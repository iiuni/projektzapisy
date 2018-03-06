
# tests marked by comment "TIME DEPENDENCY" should be free from this dependency

from django.test import TestCase
from django.contrib.auth.models import User

from apps.enrollment.courses.models import Course, Group, StudentOptions, Semester
from apps.enrollment.records.models import Record, Queue
from apps.enrollment.records.exceptions import NonStudentException, NonGroupException, AlreadyAssignedException, OutOfLimitException, AlreadyNotAssignedException, AssignedInThisTypeGroupException, RecordsNotOpenException, AlreadyQueuedException, InactiveStudentException
from apps.enrollment.courses.exceptions import NonCourseException
from apps.users.models import Employee, Student

from datetime import datetime, timedelta

class AddStudentToGroupTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__courses']

    def setUp(self):
        """
        EXERCISE_GROUP:
                "fields": {
                    "limit": 120,
                    "type": "2",
                    "teacher": 3,
                    "course": 1
                }
            LECTURE_GROUPS:
                    "fields": {
                    "limit": 120,
                    "type": "1",
                    "teacher": 3,
                    "course": 1
                },
                    "fields": {
                    "limit": 100,
                    "type": "1",
                    "teacher": 3,
                    "course": 1
                }

        """
        self.user = User.objects.get(id=5)
        self.exercise_group = Group.objects.get(id=1)
        self.lecture_group = Group.objects.get(id=3)
        self.lecture_group2 = Group.objects.get(id=5)

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Record.add_student_to_group, self.user, self.exercise_group)

    def testWithInactiveStudent(self):
        self.user.student.status = 1
        self.user.student.save()
        self.assertRaises(InactiveStudentException, Record.add_student_to_group, self.user, self.exercise_group)

    def testWithoutGivenGroup(self):
        self.exercise_group.delete()
        self.assertRaises(NonGroupException, Record.add_student_to_group, self.user, self.exercise_group)

    def testWithGroupLimitExceeded(self):
        self.exercise_group.limit = 0
        self.exercise_group.save()
        self.assertRaises(OutOfLimitException, Record.add_student_to_group, self.user, self.exercise_group)

#TIME DEPENDENCY
    def testCourseWithRecordsNotOpenForStudent(self):
        self.user.student.records_opening_bonus_minutes = 0
        self.user.student.save()
        self.exercise_group.course.semester.records_opening = datetime.now()
        self.exercise_group.course.semester.records_closing = datetime.now()
        self.exercise_group.course.semester.save()
        student_options = StudentOptions.objects.get(student=self.user.student, course=self.exercise_group.course)
        student_options.records_opening_bonus_hours = 10
        student_options.save()
        self.assertRaises(RecordsNotOpenException, Record.add_student_to_group, self.user, self.exercise_group)

    def testAddStudentToLectureGroupOnly(self):
        self.assertEqual(Record.objects.count(), 0)
        records = Record.add_student_to_group(self.user, self.lecture_group)
        self.assertEqual(records[0].group, self.lecture_group)

    def testAddStudentToNonLectureGroupAndAutomaticalyAddToLectureGroup(self):
        self.assertEqual(Record.objects.count(), 0)
        records = Record.add_student_to_group(self.user, self.exercise_group)
        groups_records = [r.group for r in records]
        self.assertTrue(len(groups_records) == 3)
        self.assertTrue(self.exercise_group in groups_records)
        self.assertTrue(self.lecture_group in groups_records)
        self.assertTrue(self.lecture_group2 in groups_records)

class RemoveStudentFromGroupTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__courses']

    def setUp(self):
        self.user = User.objects.get(id=5)
        self.group = Group.objects.get(id=3)
        self.group.course.semester.semester_beginning = datetime.now().date() - timedelta(days=1)
        self.group.course.semester.semester_ending = datetime.now().date() + timedelta(days=1)
        self.group.course.semester.save()
        self.records = Record.add_student_to_group(self.user, self.group)

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Record.remove_student_from_group, self.user, self.group)

    def testWithoutGivenGroup(self):
        self.group.delete()
        self.assertRaises(NonGroupException, Record.remove_student_from_group, self.user, self.group)

    def testStudentNotAssignedToGroup(self):
        self.records[0].delete()
        self.assertEqual(Record.objects.count(), 0)
        self.assertRaises(AlreadyNotAssignedException, Record.remove_student_from_group, self.user, self.group)
        self.assertEqual(Record.objects.count(), 0)

    def testAfterRecordsClosing(self):
        semester = self.group.course.semester
        semester.semester_ending = datetime.now().date() + timedelta(days=1)
        semester.records_closing = datetime.now().date() - timedelta(days=1)
        semester.save()
        self.assertTrue(semester.is_current_semester())
        self.assertRaises(RecordsNotOpenException, Record.remove_student_from_group, self.user, self.group)

    def testRemoveStudentFromGroup(self):
        self.assertEqual(Record.objects.count(), 1)
        Record.remove_student_from_group(self.user, self.group)
        self.assertEqual(Record.objects.count(), 0)

class IsStudentInCourseGroupTypeTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__courses']


    def setUp(self):
        self.user = User.objects.get(id=5)
        self.lecture_group = Group.objects.get(id=3)
        self.exercise_group = Group.objects.get(id=1)
        self.course = Course.objects.get(id=1)
        self.record = Record.add_student_to_group(self.user, self.lecture_group)

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Record.is_student_in_course_group_type, self.user, self.course.slug, self.lecture_group.type)

    def testWithNonCourse(self):
        course_slug = self.course.slug
        self.course.delete()
        self.assertRaises(NonCourseException, Record.is_student_in_course_group_type, self.user, course_slug, self.lecture_group.type)

    def testStudentInCourseGroupType(self):
        self.assertTrue(Record.is_student_in_course_group_type(self.user, self.course.slug, self.lecture_group.type))
        self.assertFalse(Record.is_student_in_course_group_type(self.user, self.course.slug, self.exercise_group.type))

class GetGroupsForStudentTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__courses']

    def setUp(self):
        """
        lecture_group_2 and exercise_group belong to same course
        lecture_group_2 belongs to different course
        """
        self.user = User.objects.get(id=5)
        self.lecture_group_1 = Group.objects.get(id=3)
        self.lecture_group_2 = Group.objects.get(id=5)
        self.exercise_group = Group.objects.get(id=1)

        self.lecture_group_3 = Group.objects.get(id=4)

        #Automaticaly add student to lecture_group_1
        self.records_1 = Record.add_student_to_group(self.user, self.exercise_group)

        self.records_2 = Record.add_student_to_group(self.user, self.lecture_group_3)

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Record.get_groups_for_student, self.user)

    def testGetGroupsForStudent(self):
        groups = Record.get_groups_for_student(self.user)
        self.assertTrue(len(groups) == 4)
        self.assertTrue(self.lecture_group_1 in groups)
        self.assertTrue(self.lecture_group_2 in groups)
        self.assertTrue(self.exercise_group in groups)
        self.assertTrue(self.lecture_group_3 in groups)

class GetStudentsInGroupTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__courses']

    def setUp(self):
        self.user = User.objects.get(id=5)
        self.group = Group.objects.get(id=1)
        self.record = Record.add_student_to_group(self.user, self.group)

    def testWithNonExistsGroup(self):
        self.group.delete()
        self.assertRaises(NonGroupException, Record.get_students_in_group, self.group.id)

    def testGetStudentsInGroup(self):
        students = Record.get_students_in_group(self.group.id)
        self.assertEqual(students, [self.user.student])


class AssignmentToGroupsWithSameTypes(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__courses']

    def setUp(self):
        self.user = User.objects.get(id=5)

        self.group1 = Group.objects.get(id=1)
        self.group2 = Group.objects.get(id=2)
        self.lecture11 = Group.objects.get(id=3)
        self.lecture12 = Group.objects.get(id=5)
        self.lecture2 = Group.objects.get(id=4)

        semester = self.group1.course.semester
        semester.semester_beginning = datetime.now().date() - timedelta(days=1)
        semester.semester_ending = datetime.now().date() + timedelta(days=1)
        semester.save()

        self.record = Record.objects.create(student=self.user.student, group=self.lecture11)

    def testAssignToAnotherLecture(self):
        Record.add_student_to_group(self.user, self.lecture2)
        self.assertEqual(Record.objects.count(), 2)

    def testAssignToGroupForFirstTime(self):
        Record.add_student_to_group(self.user, self.group1)
        self.assertEqual(Record.objects.count(), 3)

    def testAssignToCurrentlyBookedGroupWithSameType(self):
        self.assertEqual(Record.objects.count(), 1)
        Record.add_student_to_group(self.user, self.group1)
        self.assertEqual(Record.objects.count(), 3)
        Record.add_student_to_group(self.user, self.group2)
        self.assertEqual(Record.objects.count(), 3)

class MoveStudentFromQueueToGroup(TestCase):
    fixtures =  ['fixtures__priority_queue']

#TIME DEPENDENCY
    def setUp(self):
        self.student_to_remove = User.objects.get(id=100)
        self.student_to_remove2 = User.objects.get(id=104)

        self.student_first_in_queue = User.objects.get(id=101)
        self.student_second_in_queue = User.objects.get(id=102)

        self.full_group = Group.objects.get(id=100)
        self.same_type_group = Group.objects.get(id=101)
        self.other_type_group = Group.objects.get(id=102)
        self.same_type_group_hp = Group.objects.get(id=103)
        self.same_type_group_ep = Group.objects.get(id=104)
        self.empty_queue_group = Group.objects.get(id=105)
        self.congested_group = Group.objects.get(id=106) # with non empty queue

        self.semester = Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()

    def testEmptyQueue(self):
        self.assertEqual(Record.objects.filter(group=self.empty_queue_group.id).count(), 1)
        Record.remove_student_from_group(self.student_to_remove, self.empty_queue_group)
        self.assertEqual(Record.objects.filter(group=self.empty_queue_group.id).count(), 0)
        self.assertEqual(Queue.objects.filter(group=self.empty_queue_group.id).count(), 0)

    def testNotEmptyQueue(self):
        Record.remove_student_from_group(self.student_to_remove, self.full_group)
        self.assertEqual(Record.objects.filter(student=self.student_to_remove.id, group=self.full_group.id).count(), 0)
        self.assertEqual(Record.objects.filter(student=self.student_first_in_queue.id, group=self.full_group.id).count(), 1)
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.full_group.id).count(), 0)

    def testWithNoFreePlaceInGroup(self):
        self.assertEqual(Record.objects.filter(group=self.congested_group.id).count(), self.congested_group.limit + 1)
        queue_count_before = Queue.objects.filter(group=self.congested_group.id).count()
        Record.remove_student_from_group(self.student_to_remove, self.congested_group)
        queue_count_after = Queue.objects.filter(group=self.congested_group.id).count()
        self.assertEqual(queue_count_before, queue_count_after)

    def testRemoveStudentLowerPriorityRecords(self):
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group.id).count(), 1)
        Record.remove_student_from_group(self.student_to_remove, self.full_group)
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group.id).count(), 0)

    def testRemoveStudentEqualPriorityRecords(self):
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group_ep.id).count(), 1)
        Record.remove_student_from_group(self.student_to_remove, self.full_group)
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group_ep.id).count(), 0)

    def testNotRemoveStudentLowerPriorityRecordsWithOtherGroupType(self):
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.other_type_group.id).count(), 1)
        Record.remove_student_from_group(self.student_to_remove, self.full_group)
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.other_type_group.id).count(), 1)

    def testNotRemoveStudentHigherPriorityRecords(self):
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group_hp.id).count(), 1)
        Record.remove_student_from_group(self.student_to_remove, self.full_group)
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group_hp.id).count(), 1)

    def testChangeStudentGroup(self):
        """ if student is enrolled to some group and there is a free place in the same type group and student is in that group queue than enroll student to group"""
        Record.remove_student_from_group(self.student_to_remove, self.full_group)
        Record.remove_student_from_group(self.student_to_remove2, self.same_type_group_hp)
        self.assertEqual(Record.objects.filter(student=self.student_first_in_queue.id, group=self.full_group.id).count(), 0)
        self.assertEqual(Record.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group_hp.id).count(), 1)

class GetStudentsInQueue(TestCase):
    fixtures =  ['fixtures__queue']

#TIME DEPENDENCY
    def setUp(self):
        self.user = User.objects.get(id=100)
        self.student = User.objects.get(id=100)
        self.group = Group.objects.get(id=100)
        self.group2 = Group.objects.get(id=103)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()

    def testWithoutGivenGroup(self):
        group_id = self.group.id
        self.group.delete()
        self.assertRaises(NonGroupException, Queue.get_students_in_queue, group_id)

    def testWithEmptyGroup(self):
        self.assertEqual(Queue.objects.filter(group=100).count(), 0)
        queued_students = Queue.get_students_in_queue(self.group.id)
        self.assertEqual(len(queued_students),0)

    def testWithNonEmptyGroup(self):
        queued_students = Queue.get_students_in_queue(self.group2.id)
        self.assertEqual(len(queued_students),3)

class AddStudentToQueue(TestCase):
    fixtures =  ['fixtures__queue']

    def setUp(self):
        self.user = User.objects.get(id=100)
        self.student = User.objects.get(id=100)
        self.employee = User.objects.get(id=1000)
        self.group = Group.objects.get(id=100)
        self.group2 = Group.objects.get(id=101)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Queue.add_student_to_queue, self.user.id, self.group.id)

    def testWithoutGivenGroup(self):
        group_id = self.group.id
        self.group.delete()
        self.assertRaises(NonGroupException, Queue.add_student_to_queue, self.student.id, group_id)

    def testStudentAssignedToGroup(self):
        Record.add_student_to_group(self.student, self.group)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 0)
        self.assertRaises(AlreadyAssignedException, Queue.add_student_to_queue, self.student.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 0)

    def testStudentNotAssignedToQueue(self):
        Queue.add_student_to_queue(self.student.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 1)


    def testStudenAssignedToQueue(self):
        Queue.add_student_to_queue(self.student.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 1)
        self.assertRaises(AlreadyQueuedException, Queue.add_student_to_queue, self.student.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 1)

    def testWithRecordsNotOpenForStudent(self):
        self.user.student.records_opening_bonus_hours = 0
        self.user.student.save()
        self.group.course.semester.records_opening = datetime.now()
        self.group.course.semester.records_closing = datetime.now()
        self.group.course.semester.save()
        student_options = StudentOptions.objects.get(student=self.user.student, course=self.group.course)
        student_options.records_opening_bonus_minutes = 10
        student_options.save()
        self.assertRaises(RecordsNotOpenException, Queue.add_student_to_queue, self.user.id, self.group.id)

class RemoveStudentFromQueue(TestCase):
    fixtures =  ['fixtures__queue']

#TIME DEPENDENCY
    def setUp(self):
        self.user = User.objects.get(id=101)
        self.student1 = User.objects.get(id=100)
        self.student2 = User.objects.get(id=101)
        self.employee = User.objects.get(id=1000)
        self.group = Group.objects.get(id=101)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Queue.remove_student_from_queue, self.user.id, self.group.id)

    def testWithoutGivenGroup(self):
        group_id = self.group.id
        self.group.delete()
        self.assertRaises(NonGroupException, Queue.remove_student_from_queue, self.student1.id, group_id)

    def testStudentNotAssignedToQueue(self):
        self.assertRaises(AlreadyNotAssignedException, Queue.remove_student_from_queue, self.student1.id, self.group.id)

    def testAfterRecordsClosing(self):
        semester = self.group.course.semester
        semester.semester_ending = datetime.now().date() + timedelta(days=1)
        semester.records_closing = datetime.now().date() - timedelta(days=1)
        semester.save()
        self.assertTrue(semester.is_current_semester())
        self.assertRaises(RecordsNotOpenException, Queue.remove_student_from_queue, self.user.id, self.group.id)

    def testRemoveStudentFromQueue(self):
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 1)
        Queue.remove_student_from_queue(self.student2.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 0)

class RemoveFirstStudentFromQueue(TestCase):
    fixtures =  ['fixtures__queue']

#TIME DEPENDENCY
    def setUp(self):
        self.user = User.objects.get(id=101)
        self.student1 = User.objects.get(id=100)
        self.student2 = User.objects.get(id=101)
        self.student3 = User.objects.get(id=102)
        self.student4 = User.objects.get(id=105)
        self.employee = User.objects.get(id=1000)
        self.group = Group.objects.get(id=100)
        self.group2 = Group.objects.get(id=103)
        self.group3 = Group.objects.get(id=104)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()

    def testEmptyQueue(self):
        self.assertEqual(Queue.remove_first_student_from_queue(self.group), None)

#Checking same as test below - WHY?
    def testWithECTSLimitExceeded(self):
        self.assertEqual(Queue.remove_first_student_from_queue(self.group3), None)

    def testRemoveFirstStudentFromQueue(self):
        removed = Queue.objects.get(group=self.group2.id, student=self.student2.id).student
        self.assertEqual(Queue.remove_first_student_from_queue(self.group2).student, removed)

#TIME DEPENDENCY
class RemoveStudentLowPriorityRecords(TestCase):
    fixtures =  ['fixtures__queue']

    def setUp(self):
        self.user = User.objects.get(id=101)
        self.student1 = User.objects.get(id=100)
        self.student2 = User.objects.get(id=101)
        self.student3 = User.objects.get(id=102)
        self.employee = User.objects.get(id=1000)
        self.group = Group.objects.get(id=100)
        self.group2 = Group.objects.get(id=103)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()


    def testWithoutGivenGroup(self):
        group_id = self.group2.id
        self.group2.delete()
        self.assertRaises(NonGroupException, Queue.remove_student_low_priority_records, self.student1.id, group_id, 10)

    def testRemoveStudentLowPriorityRecords(self):
        Queue.remove_student_low_priority_records(self.student2.id, self.group2.id,10)
        self.assertEqual(Queue.objects.filter(group=101, student=self.student2).count(), 0)
