"""Module opening_times takes care of managing enrollment time constraints.

Every student has his T0 - the time, when his enrollment starts. For some
courses he has a time advantage coming from his votes. Additionally, some groups
will have their own opening time. Some groups will also provide a time advantage
for a selected group of students (ex. ISIM students).
"""
from datetime import datetime, timedelta
from typing import List, Dict

from django.db import models, transaction

from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.group import Group
from apps.users.models import Student
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
        """Checks, whether the T0 for student has passed.

        The function will return False if student is inactive, his T0 is not in
        the database, the enrollment is closed in the semester or has not yet
        started.
        """
        if not student.is_active():
            return False
        if time > semester.records_closing:
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
        their participation in .

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
                # that over nighttime.
                record.time -= timedelta(minutes=((student.ects * 5) // 720) * 720)
                # Every ECTS point additionally gives 5
                # minutes advantage
                record.time -= timedelta(minutes=5) * student.ects
                # Every participation in classes grading gives a day worth
                # advantage.
                student_generated_tickets = generated_tickets.get(student.pk, 0)
                record.time -= timedelta(days=1) * student_generated_tickets
                # We may add some bonus by hand.
                record.time -= timedelta(minutes=1) * student.records_opening_bonus_minutes
                # Finally, everyone gets 2 hours for some reason.
                record.time -= timedelta(hours=2)
                created.append(record)
            cls.objects.bulk_create(created)


class GroupOpeningTimes(models.Model):
    """Stores student opening times for groups.

    The primary reason for a student to have this time specified is, that he
    voted for the course and gets a bonus (for all groups in that course).
    Moreover we will use that to give special preferences to ISIM students and
    to split groups into subgroups with different opening times during
    freshmen enrollment.
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
        """Checks if group is open for the student to enroll.

        We first look at the relation between the group and the student. If
        there is none, the group might have its own opening and closing times.
        Finally, we look at the student's T0.
        """
        try:
            record = cls.objects.get(student=student, group=group)
            return record.time <= time <= group.course.semester.records_closing
        except cls.DoesNotExist:
            pass

        if group.course.records_start is not None and group.course.records_end is not None:
            return group.course.records_start <= time <= group.course.records_end
        if T0Times.is_after_t0(student, group.course.semester, time):
            return True
        return False

    @classmethod
    def are_groups_open_for_student(cls, student: Student, groups: List[Group],
                                    time: datetime) -> Dict[int, bool]:
        """For each group in groups checks, if the group is open for the student.

        The function will assume, that all the groups are in the same semester.
        """
        if not groups:
            return []
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
    def populate_opening_times(cls, semester: Semester):
        """Computes opening times (bonuses) for students that cast votes.

        Voting for a course results in a quicker enrollment. The function will
        throw a DatabaseError if operation is unsuccessful.
        """
        # First make sure, that all SingleVotes have their course field
        # populated.
        SingleVote.populate_scheduled_courses(semester)
        with transaction.atomic():
            # First delete all already existing records for this semester.
            cls.objects.filter(group__course__semester_id=semester.id).delete()
            # We need T0 of each student.
            t0times: Dict[int, int] = dict(
                T0Times.objects.filter(semester_id=semester.id).values_list("student_id", "time")
            )

            opening_time_objects: List[cls] = []
            single_vote: SingleVote
            for single_vote in SingleVote.objects.filter(
                course__semester_id=semester.id
            ).select_related("course").prefetch_related("course__groups"):
                # Every point gives a day worth of bonus.
                for group in single_vote.course.groups.all():
                    bonus_obj = cls(student=single_vote.student, group=group)
                    bonus_obj.time = max(
                        filter(
                            None,
                            [
                                # The opening cannot be earlier than the group is opened
                                # (if that is specified).
                                single_vote.course.records_start,
                                # If the student does not have T0, we use
                                # the general records opening time in the
                                # semester.
                                t0times.get(single_vote.student_id, semester.records_opening) -
                                timedelta(days=single_vote.correction),
                            ]
                        )
                    )
                    opening_time_objects.append(bonus_obj)
            cls.objects.bulk_create(opening_time_objects)
