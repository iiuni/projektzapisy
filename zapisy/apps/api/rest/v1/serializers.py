from django.contrib.auth.models import User
from rest_framework import serializers

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.semester import Semester
from apps.offer.desiderata.models import Desiderata, DesiderataOther
from apps.offer.vote.models import SingleVote, SystemState
from apps.schedule.models.specialreservation import SpecialReservation
from apps.users.models import Employee


class SemesterSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Semester
        fields = ('id', 'display_name')

    def get_display_name(self, obj):
        return obj.get_name()


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ('id', 'type', 'description', 'number', 'order', 'building', 'capacity',
                  'floor', 'can_reserve', 'slug')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = ('id', 'user', 'consultations', 'homepage', 'room')


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
    vote_points = serializers.SerializerMethodField()
    course_name = serializers.CharField(source='entity.name')

    def get_vote_points(self, vote_model):
        return max(vote_model.value, vote_model.correction)

    class Meta:
        model = SingleVote
        fields = ('student', 'course_name', 'vote_points')


class SystemStateSerializer(serializers.ModelSerializer):
    state_name = serializers.SerializerMethodField()

    def get_state_name(self, systemstate_model):
        return str(systemstate_model)

    class Meta:
        model = SystemState
        fields = ('id', 'state_name')
