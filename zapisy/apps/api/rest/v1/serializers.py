from django.contrib.auth.models import User
from rest_framework import serializers

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models import CourseEntity, Course, Group, Semester
from apps.enrollment.courses.models.term import Term
from apps.enrollment.records.models import Record
from apps.offer.desiderata.models import Desiderata, DesiderataOther
from apps.offer.vote.models import SingleVote, SystemState
from apps.schedule.models.specialreservation import SpecialReservation
from apps.users.models import Employee, Student


class SemesterSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Semester
        fields = ('id', 'display_name', 'usos_kod')
        read_only_fields = ('id', 'display_name')

    def get_display_name(self, obj):
        return obj.get_name()


class CourseEntitySerializer(serializers.ModelSerializer):
    """Serializer for CourseEntity

    When serializing multiple objects, it is important to use
    `select_related('type')`.
    """
    type_short_name = serializers.SerializerMethodField()

    class Meta:
        model = CourseEntity
        fields = ('id', 'name', 'type_short_name', 'usos_kod')
        read_only_fields = ('id', 'name', 'type_short_name')

    def get_type_short_name(self, obj):
        if obj.type is None:
            return None
        return obj.type.short_name


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course.

    When serializing multiple objects, it is important to use
    `select_related('entity', 'entity__type')`.
    """
    entity = CourseEntitySerializer(read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'entity', 'semester')
        read_only_fields = ('id', 'entity', 'semester')


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ('id', 'type', 'description', 'number', 'order', 'building', 'capacity', 'floor',
                  'can_reserve', 'slug', 'usos_id')
        read_only_fields = ('id', 'type', 'description', 'number', 'order', 'building', 'capacity',
                            'floor', 'can_reserve', 'slug')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'user', 'consultations', 'homepage', 'room', 'title', 'usos_id')
        read_only_fields = ('id', 'user', 'consultations', 'homepage', 'room')


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ('id', 'usos_id', 'matricula', 'ects', 'status', 'user')
        read_only_fields = ('id', 'matricula', 'user')


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
    """Serializes vote system state, get id and friendly name"""
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
    `select_related('course', 'course__entity', 'teacher', 'teacher__user')`.
    """
    course = CourseSerializer(read_only=True)
    teacher = EmployeeSerializer(read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'type', 'course', 'teacher', 'limit', 'usos_nr')
        read_only_fields = ('id', 'type', 'course', 'teacher', 'limit')


class ShallowGroupSerializer(serializers.ModelSerializer):
    """Serializes a Group instance by only showing its fields, not relations."""
    class Meta:
        model = Group
        fields = '__all__'


class TermSerializer(serializers.ModelSerializer):
    """Serializes a Term instance.

    When serializing multiple objects, query them with `select_related('group',
    'group__course', 'group__course__entity', 'group__teacher',
    'group__teacher__user').prefetch_related('classrooms')`.
    """
    group = ShallowGroupSerializer(read_only=True)
    classrooms = ClassroomSerializer(read_only=True, many=True)

    class Meta:
        model = Term
        fields = ('id', 'dayOfWeek', 'start_time', 'end_time', 'group', 'classrooms', 'usos_id')
        read_only_fields = ('id', 'dayOfWeek', 'start_time', 'end_time', 'group', 'classrooms')


class RecordSerializer(serializers.ModelSerializer):
    group = ShallowGroupSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = Record
        fields = ('id', 'group', 'student')
