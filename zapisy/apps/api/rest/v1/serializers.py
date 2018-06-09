from django.contrib.auth.models import User
from rest_framework import serializers

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.course import (Course, CourseDescription,
                                                   CourseEntity)
from apps.enrollment.courses.models.semester import Semester
from apps.offer.desiderata.models import Desiderata, DesiderataOther
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


class CourseEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEntity
        fields = '__all__'


class CourseDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDescription
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
