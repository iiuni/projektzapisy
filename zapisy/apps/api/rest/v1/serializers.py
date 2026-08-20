from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from apps.effects.models import CompletedCourses
from apps.enrollment.courses.models import CourseInstance, Group, Semester
from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.term import Term
from apps.enrollment.records.models import Record
from apps.offer.desiderata.models import Desiderata, DesiderataOther
from apps.offer.vote.models import SingleVote, SystemState
from apps.schedule.models.specialreservation import SpecialReservation
from apps.users.models import Employee, Program, Student


class SemesterSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Semester
        fields = ('id', 'display_name', 'year', 'type', 'usos_kod')
        read_only_fields = ('id', 'display_name', 'year', 'type')

    def get_display_name(self, obj):
        return obj.get_name()


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for CourseInstance class.

    For performance reasons use `select_related('course_type')` in the queryset.
    """
    course_type = serializers.SerializerMethodField()
    usos_kod = serializers.CharField(max_length=20, read_only=False)

    class Meta:
        model = CourseInstance
        fields = ('id', 'name', 'short_name', 'points', 'has_exam', 'description', 'language',
                  'semester', 'course_type', 'usos_kod')
        read_only_fields = ('id', 'name', 'short_name', 'points', 'has_exam', 'description',
                            'language', 'course_type')

    def get_course_type(self, obj):
        if obj.course_type is None:
            return None
        return obj.course_type.short_name


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ('id', 'type', 'description', 'number', 'building', 'capacity', 'floor',
                  'can_reserve', 'slug', 'usos_id')
        read_only_fields = ('id', 'type', 'description', 'number', 'building', 'capacity',
                            'floor', 'can_reserve', 'slug')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        extra_kwargs = {
            'username': {'validators': []},
        }


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'user', 'consultations', 'homepage', 'room', 'title', 'usos_id')
        read_only_fields = ('id', 'user', 'consultations', 'homepage', 'room')


class ProgramRelatedField(serializers.RelatedField):
    def display_value(self, instance):
        return instance

    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        try:
            return Program.objects.get(name=data)
        except Program.DoesNotExist:
            raise serializers.ValidationError("Program o podanej nazwie nie istnieje.")


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    program = ProgramRelatedField(queryset=Program.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Student
        fields = ('id', 'usos_id', 'matricula', 'ects', 'is_active', 'user', 'program',
                  'semestr',)

    @transaction.atomic
    def create(self, validated_data):
        students = AuthGroup.objects.get(name='students')
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        students.user_set.add(user)
        students.save()
        student = Student.objects.create(
            user=user, **validated_data)
        return student

    @transaction.atomic
    def update(self, instance, validated_data):
        # User field shouldn't be changed.
        validated_data.pop('user', None)
        # Matricula field shouldn't be changed.
        validated_data.pop('matricula', None)
        return super().update(instance, validated_data)


class DesiderataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desiderata
        fields = '__all__'


class DesiderataOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesiderataOther
        fields = '__all__'


class SpecialReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialReservation
        fields = '__all__'


class SingleVoteSerializer(serializers.ModelSerializer):
    """Serializes single student vote.

    Gets correct vote value, course name and student id.
    """
    vote_points = serializers.SerializerMethodField()
    course_name = serializers.CharField(source='proposal.name')

    def get_vote_points(self, vote_model):
        """Getter function for vote_points field."""
        return max(vote_model.value, vote_model.correction)

    class Meta:
        model = SingleVote
        fields = ('student', 'course_name', 'vote_points')


class SystemStateSerializer(serializers.ModelSerializer):
    """Serializes vote system state, get id and friendly name."""
    state_name = serializers.SerializerMethodField()

    def get_state_name(self, systemstate_model):
        """Getter function for system state_name field."""
        return str(systemstate_model)

    class Meta:
        model = SystemState
        fields = ('id', 'state_name')


class GroupSerializer(serializers.ModelSerializer):
    """Serializes a Group instance.

    When serializing multiple objects, they should be queried with
    `select_related('course', 'teacher', 'teacher__user')`.
    """
    course = CourseSerializer(read_only=True)
    teacher = EmployeeSerializer(read_only=True)

    human_readable_type = serializers.SerializerMethodField()
    teacher_full_name = serializers.SerializerMethodField()

    def get_human_readable_type(self, group_model):
        return group_model.get_type_display()

    def get_teacher_full_name(self, group_model):
        return group_model.get_teacher_full_name()

    class Meta:
        model = Group
        fields = ('id', 'type', 'course', 'teacher', 'limit', 'human_readable_type',
                  'teacher_full_name', 'export_usos', 'usos_nr')
        read_only_fields = ('id', 'type', 'course', 'teacher', 'limit',
                            'human_readable_type', 'teacher_full_name')


class ShallowGroupSerializer(serializers.ModelSerializer):
    """Serializes a Group instance by only showing its fields, not relations."""
    class Meta:
        model = Group
        fields = '__all__'


class TermSerializer(serializers.ModelSerializer):
    """Serializes a Term instance.

    When serializing multiple objects, query them with
    `select_related('group').prefetch_related('classrooms')`.
    """

    class Meta:
        model = Term
        fields = ('id', 'dayOfWeek', 'start_time', 'end_time', 'group', 'classrooms', 'usos_id')
        read_only_fields = ('id', 'dayOfWeek', 'start_time', 'end_time', 'group', 'classrooms')


class RecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Record
        fields = ('id', 'group', 'student')


class StudentRelatedField(serializers.RelatedField):
    def display_value(self, instance):
        return instance

    def to_representation(self, value):
        return value.usos_id

    def to_internal_value(self, data):
        try:
            return Student.objects.get(usos_id=data)
        except (ValueError, TypeError, Student.DoesNotExist):
            raise serializers.ValidationError("Błędny usos_id.")


class CompletedCoursesSerializer(serializers.ModelSerializer):
    """Serializes a CompletedCourses record."""
    student = StudentRelatedField(queryset=Student.objects.filter(is_active=True))
    program = ProgramRelatedField(queryset=Program.objects.all())
    course = CourseSerializer()

    @transaction.atomic
    def create(self, validated_data):
        course_data = validated_data.pop('course')
        course_usos_kod = course_data['usos_kod']
        semester__id = course_data['semester'].id
        try:
            course_instance = CourseInstance.objects.get(
                usos_kod=course_usos_kod, semester__id=semester__id)
        except CourseInstance.DoesNotExist:
            raise serializers.ValidationError(
                "Kurs o podanym usos_kod nie istnieje lub nie występuje w wybranym semestrze.")
        return CompletedCourses.objects.create(course=course_instance, **validated_data)

    class Meta:
        model = CompletedCourses
        fields = ('id', 'student', 'program', 'course')
