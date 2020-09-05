import json
import os.path
from typing import List, Union

from django.contrib.postgres.fields import JSONField
from django.db import models

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.group import Group, GroupType
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records import models as records_models
from apps.users.models import Student


class PollType(models.IntegerChoices):
    LECTURE = 1, 'ankieta dla wykładu'
    EXERCISE = 2, 'ankieta dla ćwiczeń'
    LABS = 3, 'ankieta dla pracowni'
    EXERCISE_LABS = 5, 'ankieta dla ćwiczenio-pracowni'
    SEMINAR = 6, 'ankieta dla seminarium'
    LECTORATE = 7, 'ankieta dla lektoratu'
    PHYSICAL_EDUCATION = 8, 'ankieta dla zajęć wf'
    REPETITORY = 9, 'ankieta dla repetytorium'
    PROJECT = 10, 'ankieta dla projektu'
    EXAM = 1000, 'ankieta dla egzaminu'
    GENERAL = 1001, 'ankieta ogólna'


class PollManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'group', 'group__teacher__user', 'course', 'course__owner__user', 'semester'
        )


class Poll(models.Model):
    """Represents the default entity used for identifying a single poll.

    New Polls don't have to be created manually - everything is handled
    by signal receivers defined in `apps.grade.poll.signals`.

    A new Poll instance should consist of just one reference to one of the
    following: a group, a course or a semester.

    :param group: if present, the created poll will inherit the type
        of the group
    :param course: if present, the created poll will be of
        `PollType.EXAM` type
    :param semester: if present, the created poll will be of
        `PollType.GENERAL` type
    """
    objects = PollManager()

    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(CourseInstance, on_delete=models.CASCADE, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'ankieta'
        verbose_name_plural = 'ankiety'

    @property
    def type(self) -> Union[PollType, GroupType]:
        """Determines the PollType by checking foreign keys references."""
        if self.group:
            return self.group.type
        if self.course:
            return PollType.EXAM
        return PollType.GENERAL

    @property
    def get_semester(self):
        """Determines the semester of the poll."""
        if self.semester:
            return self.semester
        if self.course:
            return self.course.semester
        if self.group:
            return self.group.course.semester

    def __str__(self):
        """Provides a human-readable string that serves as the title of the Poll."""
        if self.group:
            group_type = self.group.get_type_display().capitalize()
            teacher_name = self.group.get_teacher_full_name()

            return f"{group_type}: {teacher_name}"
        elif self.course:
            return f"Egzamin: {self.course.owner}"
        elif self.semester:
            return "Ogół zajęć w Instytucie"

        return "Ankieta ogólna"

    @property
    def category(self) -> str:
        """Determines a category for a Poll.

        This method fetches the name of the course or assumes a general type.
        """
        if self.course:
            return self.course.name
        elif self.group:
            return self.group.course.name
        else:
            return "Ankiety ogólne"

    @property
    def subcategory(self) -> str:
        """Determines a subcategory for a Poll.

        This method uses `__str__` for type projection by default.
        """
        return self.__str__()

    def serialize_for_signing_protocol(self) -> dict:
        """Serializes the Poll to the format accepted by TicketCreate.

        :returns: a dictionary consisting of 'id', 'name' and 'type' keys.
        """
        result = {'id': self.pk, 'name': self.subcategory, 'type': self.category}

        return result

    def is_student_entitled_to_poll(self, student: Student) -> bool:
        """Checks whether the student is allowed to participate in this Poll.

        :param student:
        """
        if self.group:
            if not records_models.Record.is_enrolled(student.id, self.group_id):
                return False
        if self.course:
            return records_models.Record.objects.filter(
                student=student,
                group__course=self.course,
                status=records_models.RecordStatus.ENROLLED
            ).exists()
        return True

    @staticmethod
    def get_all_polls_for_student(student: Student, semester: Semester = None) -> List:
        """Checks the eligibility of a student and returns a list of polls.

        :param student: a valid instance of `Student` class.
        :param semester: if no semester is given, assumes a current one.
        :returns: a list of all available polls for a given student.
        """
        if not student.is_active:
            return []

        current_semester = semester
        if current_semester is None:
            current_semester = Semester.get_current_semester()
        if current_semester is None:
            return []
        if not current_semester.is_grade_active:
            return []

        polls = []
        poll_for_semester = Poll.objects.filter(semester=current_semester).first()
        if poll_for_semester:
            polls.append(poll_for_semester)

        # Retrieves only the groups that the Student is enrolled in
        records = records_models.Record.objects.filter(
            student=student,
            status=records_models.RecordStatus.ENROLLED,
            group__course__semester=current_semester,
        ).select_related('group')

        for record in records:
            group = record.group
            course = group.course
            semester = course.semester

            if semester == current_semester:
                if course.has_exam:
                    poll_for_course = Poll.objects.get(course=course)
                    if poll_for_course and poll_for_course not in polls:
                        polls.append(poll_for_course)

                poll_for_group = Poll.objects.get(group=group)
                if poll_for_group:
                    polls.append(poll_for_group)

        return polls

    @staticmethod
    def get_all_polls_for_semester(user, semester: Semester = None) -> List['Poll']:
        """Returns all polls that user may see the submissions for.

        The polls will be annotated with submission counts.
        """
        current_semester = semester
        if current_semester is None:
            current_semester = Semester.get_current_semester()

        is_superuser = user.is_superuser
        is_employee = user.employee

        if not is_superuser and not is_employee:
            return Poll.objects.none()
        poll_for_semester = Poll.objects.filter(semester=current_semester)

        if is_superuser:
            polls_for_courses = Poll.objects.filter(
                course__semester=current_semester
            )
            polls_for_groups = Poll.objects.filter(
                group__course__semester=current_semester
            )
        elif is_employee:
            polls_for_courses = Poll.objects.filter(
                course__semester=current_semester,
                course__owner=user.employee,
            ) | Poll.objects.filter(group__course__semester=current_semester,
                                    group__course__owner=user.employee)
            polls_for_groups = Poll.objects.filter(
                group__course__semester=current_semester,
                group__teacher=user.employee,
            )

        qs = poll_for_semester | polls_for_courses | polls_for_groups

        sub_count_ann = models.Count('submission', filter=models.Q(submission__submitted=True))
        return list(qs.annotate(number_of_submissions=sub_count_ann))


class Schema(models.Model):
    """Handles JSON-based templates for creating submissions.

    An example of a correctly defined schema would be:
    {
        "version": 1,
        "schema": [
            {
                "question": "Does participating in the `Project:
                             Development of the Enrollment System`
                             bring you joy? Please elaborate on your
                             feelings without using swear words.",
                "type": "textarea"
            },
            {
                "question": "Would you rather be doing something else?",
                "type": "radio",
                "choices": ["absolutely", "obviously!", "ehmm... yes?"]
            }
        ]
    }

    :param questions: a proprietary schema in JSON format.
    :param type: a type of poll for the defined `questions` schema.
    """

    questions = JSONField(default=dict)
    type = models.SmallIntegerField("Kategoria", choices=PollType.choices)

    class Meta:
        verbose_name = 'szablon'
        verbose_name_plural = 'szablony'

    def __str__(self):
        return self.get_type_display()

    @classmethod
    def get_schema_from_file(cls, poll_type: PollType, schema_path: str = None):
        """Fetches the default schema for a given poll type from a local file.

        The default schema is defined in `assets/default_schema.json`
        in the Poll app directory.

        :param poll_type: an instance of `PollType` Enum class.
        :param schema_path: path to the file containing the schema. (optional)
        :returns: a dictionary containing a schema and it's version.
        """
        if schema_path is None:
            schema_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'assets/default_schema.json'
            )
        with open(schema_path, 'r') as schema_file:
            schema = json.load(schema_file)

            # For the purposes of compatibility with old GroupType tuple
            # TODO: Decide whether it should reside in the PollType Enum class
            if isinstance(poll_type, str):
                options = PollType.options()
                values = PollType.values()
                poll_type = options[values.index(int(poll_type))]
            elif isinstance(poll_type, tuple):
                poll_type = poll_type[0]
            schema_name = f'{poll_type.__class__.__name__}.{poll_type.name}'

            if schema_name in schema:
                return schema[schema_name]
            return schema['default']

    @classmethod
    def get_latest(cls, poll_type):
        """Retrieves the most recent schema defined for a given `poll_type`.

        :param poll_type: PollType
        :returns: an instance of `Schema`
        """
        schema = cls.objects.filter(type=poll_type).last()
        if not schema:
            schema = cls(
                questions=cls.get_schema_from_file(poll_type=poll_type), type=poll_type
            )
            schema.save()

        return schema

    def get_schema_with_default_answers(self):
        """Fetches the Submission's schema and populates it with default answers.

        :returns: a schema with additional `answer` keys.
        """
        if (
            self.questions and
            'version' in self.questions and
            self.questions['version'] == 1 and
            'schema' in self.questions
        ):
            updated_schema_entries = []
            for entry in self.questions['schema']:
                entry['answer'] = ""
                updated_schema_entries.append(entry)

            return {
                'version': self.questions['version'],
                'schema': updated_schema_entries,
            }

        return {'version': 1, 'schema': []}


class SubmissionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'poll', 'poll__group', 'poll__group__teacher__user', 'poll__course',
            'poll__course__owner__user', 'poll__semester'
        )


class Submission(models.Model):
    """Represents a single submission for a referenced poll.

    Holds a value for `submitted` which is set only when the user
    submits correct answers for all required questions defined in
    the schema.

    Although the schema is referenced by a foreign key, modifying it
    directly (or unintentionally by a third party) leaves the Submission
    intact. The schema is fetched at the creation time and stored
    inside the `answers` JSON field with all the necessary information
    used for recreating the form.
    """
    objects = SubmissionManager()

    schema = models.ForeignKey(Schema, on_delete=models.SET_NULL, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.SET_NULL, null=True)
    answers = JSONField(default=dict)
    ticket = models.TextField(unique=True)
    submitted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'złoszenie'
        verbose_name_plural = 'zgłoszenia'

    def __str__(self):
        return str(self.poll)

    @property
    def category(self) -> str:
        return self.poll.category

    @property
    def subcategory(self) -> str:
        return self.__str__()

    @classmethod
    def get_or_create(cls, poll: Poll, ticket: int) -> "Submission":
        """Makes sure that there exists only submission for a poll and ticket.

        Returns:
          An instance of `Submission` class. Either existing or a new one.
        """
        submission = cls.objects.filter(ticket=ticket).first()
        if not submission:
            schema = Schema.get_latest(poll_type=poll.type)
            answers = schema.get_schema_with_default_answers()
            submission = cls(schema=schema, answers=answers, ticket=ticket, poll=poll)
            submission.save()

        return submission
