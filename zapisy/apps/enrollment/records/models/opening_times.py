"""Module opening_times takes care of managing enrollment time constraints.

Every student has his T0 - the time, when his enrollment starts. For some
courses he has a time advantage coming from his votes. Additionally, some groups
will have their own opening time. Some groups will also provide a time advantage
for a selected group of students (ex. ISIM students).
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict

from django.conf import settings
from django.db import models, transaction

from apps.enrollment.courses.models import CourseInstance, Group, Semester
from apps.users.models import Program, Student
from apps.grade.ticket_create.models.student_graded import StudentGraded
from apps.offer.vote.models.single_vote import SingleVote


class T0Times(models.Model):
    """This model stores a T0 for a student.

    T0 is a time when he can enroll into each groups (except of those that are
    still closed).
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    time = models.DateTimeField()

    class Meta:
        unique_together = ("student", "semester")
        indexes = [
            models.Index(fields=["student", "semester"]),
        ]

    @classmethod
    def is_after_t0(cls, student: Student, semester: Semester, time: datetime) -> bool:
        """Checks whether the T0 for student has passed.

        The function will return False if student is inactive, his T0 is not in
        the database, the enrollment is closed in the semester or has not yet
        started.
        """
        if not student.is_active():
            return False
        if semester.records_closing is not None and time > semester.records_closing:
            return False
        t0_record = None
        try:
            t0_record = cls.objects.get(student=student, semester=semester)
        except cls.DoesNotExist:
            return False
        if time < t0_record.time:
            return False
        return True

    @classmethod
    def populate_t0(cls, semester: Semester):
        """Computes T0's for all active students based on their ECTS points and
        their participation in courses grading. The additional administrative
        bonus is also taken into account.

        The function will throw a DatabaseError if something goes wrong.
        """
        with transaction.atomic():
            # First we delete all T0 records in current semester.
            cls.objects.filter(semester=semester).delete()

            created: List[cls] = []
            # For each student_id we want to know, how many times he has
            # generated grading tickets in the last two semesters.
            generated_tickets: Dict[int, int] = dict(
                StudentGraded.objects.filter(semester_id__in=[
                    semester.first_grade_semester_id, semester.second_grade_semester_id
                ]).values("student_id").annotate(num_tickets=models.Count("id")).values_list(
                    "student_id", "num_tickets"))

            student: Student
            for student in Student.get_active_students():
                record = cls(student=student, semester=semester)
                record.time = semester.records_opening
                # Every ECTS gives 5 minutes bonus, but with logic splitting
                # that over nighttime. 720 minutes is equal to12 hours. If
                # ((student.ects * ECTS_BONUS) // 12 hours) is odd, we subtract
                # additional 12 hours from T0. This way T0's are separated by
                # ECTS_BONUS minutes per point, but never fall in the nighttime.
                record.time -= timedelta(
                    minutes=((student.ects * settings.ECTS_BONUS) // 720) * 720)
                record.time -= timedelta(minutes=settings.ECTS_BONUS) * student.ects
                # Every participation in classes grading gives a day worth
                # advantage.
                student_generated_tickets = generated_tickets.get(student.pk, 0)
                record.time -= timedelta(days=1) * student_generated_tickets
                # We may add some bonus by hand.
                record.time -= timedelta(minutes=1) * student.records_opening_bonus_minutes
                # Finally, everyone gets 2 hours. This way, nighttime pause is
                # shifted from 00:00-12:00 to 22:00-10:00.
                record.time -= timedelta(hours=2)
                created.append(record)
            cls.objects.bulk_create(created)


class GroupOpeningTimes(models.Model):
    """Stores student opening times for groups.

    The primary reason for a student to have this time specified is, that he
    voted for the course and gets a bonus (for all groups in that course).
    Moreover we will use that to split groups into subgroups with different
    opening times during freshmen enrollment.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    time = models.DateTimeField()

    class Meta:
        unique_together = ("student", "group")
        indexes = [
            models.Index(fields=["student", "group"]),
        ]

    @classmethod
    def is_group_open_for_student(cls, student: Student, group: Group, time: datetime) -> bool:
        """Checks if group is open for the student to enroll."""
        return cls.are_groups_open_for_student(student, [group], time)[group.pk]

    @classmethod
    def are_groups_open_for_student(cls, student: Student, groups: List[Group],
                                    time: datetime) -> Dict[int, bool]:
        """For each group in groups checks if the group is open for the student.

        For a single group, we first look at the relation between the group and
        the student (GroupOpeningTimes). If there is none, the group might have
        its own opening and closing times. Finally, we look at the student's T0.

        The function will assume, that all the groups are in the same semester.
        In order to ensure the performance of this function, Groups should be
        fetched with select_related('course', 'course__semester').
        """
        if not groups:
            return {}
        # We assume all the groups are in the same semester.
        is_after_t0 = T0Times.is_after_t0(student, groups[0].course.semester, time)

        groups: Dict[int, Group] = {g.id: g for g in groups}

        for k in groups:
            groups[k].opening_time_for_student = None
        for rec in cls.objects.filter(student=student, group__in=groups):
            groups[rec.group_id].opening_time_for_student = rec.time

        ret: Dict[int, bool] = {}
        for k, group in groups.items():
            if group.opening_time_for_student is not None:
                ret[k] = (
                    group.opening_time_for_student <= time <= group.course.semester.records_closing
                )
                continue
            if group.course.records_start is not None and group.course.records_end is not None:
                ret[k] = group.course.records_start <= time <= group.course.records_end
                continue
            if not is_after_t0:
                ret[k] = False
                continue
            ret[k] = True
        return ret

    @classmethod
    def is_enrollment_open(cls, course: CourseInstance, time: datetime):
        """Decides if enrollment is open for this course in general.

        Usually enrollment is for all courses at the beginning of the semester,
        but some courses may have a different, additional enrollment period.
        """
        is_course_open = False
        if course.records_start is not None and course.records_end is not None:
            is_course_open = course.records_start <= time <= course.records_end
        is_semester_open = not course.semester.is_closed(time)
        return is_course_open or is_semester_open

    @classmethod
    @transaction.atomic
    def populate_opening_times(cls, semester: Semester):
        """Computes opening times (bonuses) for students that cast votes.

        Voting for a course results in a quicker enrollment. The function will
        throw a DatabaseError if operation is unsuccessful.
        """
        # First make sure, that all SingleVotes have their course field
        # populated.
        # First delete all already existing records for this semester.
        cls.objects.filter(group__course__semester_id=semester.id).delete()
        # We need T0 of each student.
        t0times: Dict[int, datetime] = dict(
            T0Times.objects.filter(semester_id=semester.id).values_list("student_id", "time")
        )

        opening_time_objects: List['GroupOpeningTimes'] = []
        votes = SingleVote.objects.meaningful().in_semester(semester=semester)
        groups = Group.objects.filter(course__semester=semester).select_related('course')

        votes_by_proposal: Dict[int, List[SingleVote]] = defaultdict(list)
        for vote in votes:
            votes_by_proposal[vote.proposal_id].append(vote)

        groups_by_proposal: Dict[int, List[Group]] = defaultdict(list)
        for group in groups:
            groups_by_proposal[group.course.offer_id].append(group)

        for proposal_id, groups in groups_by_proposal.items():
            single_vote: SingleVote
            for single_vote in votes_by_proposal[proposal_id]:
                # Every point gives a day worth of bonus.
                for group in groups:
                    bonus_obj = cls(student_id=single_vote.student_id, group_id=group.pk)
                    bonus_obj.time = max(
                        filter(
                            None,
                            (
                                # The opening cannot be earlier than the group is opened
                                # (if that is specified).
                                group.course.records_start,
                                # If the student does not have T0, we use
                                # the general records opening time in the
                                # semester.
                                t0times.get(single_vote.student_id, semester.records_opening) -
                                timedelta(days=single_vote.val),
                            )
                        )
                    )
                    opening_time_objects.append(bonus_obj)
        cls.objects.bulk_create(opening_time_objects)

    @classmethod
    @transaction.atomic
    def populate_single_group_opening_times(cls, group: Group):
        """Computes opening times for a single course group.

        The function does the same as `populate_opening_times` but for a single
        group.
        """
        # First delete all already existing records for this group.
        cls.objects.filter(group=group).delete()
        # We need T0 of each student.
        t0times: Dict[int, datetime] = dict(
            T0Times.objects.filter(semester_id=group.course.semester_id).values_list(
                "student_id", "time"))
        # We also need votes for the course.
        votes = SingleVote.objects.meaningful().in_semester(semester=group.course.semester).filter(
            proposal=group.course.offer)
        opening_time_objects: List['GroupOpeningTimes'] = []
        single_vote: SingleVote
        for single_vote in votes:
            # Every point gives a day worth of bonus.
            bonus_obj = cls(student=single_vote.student, group=group)
            bonus_obj.time = max(
                filter(
                    None,
                    [
                        # The opening cannot be earlier than the group is opened
                        # (if that is specified).
                        group.course.records_start,
                        # If the student does not have T0, we use
                        # the general records opening time in the
                        # semester.
                        t0times.get(single_vote.student_id, group.course.semester.records_opening) -
                        timedelta(days=single_vote.val),
                    ]))
            opening_time_objects.append(bonus_obj)
        cls.objects.bulk_create(opening_time_objects)
