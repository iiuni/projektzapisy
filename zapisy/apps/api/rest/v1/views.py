from rest_framework import viewsets

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.course import (Course, CourseDescription,
                                                   CourseEntity)
from apps.enrollment.courses.models.semester import Semester
from apps.offer.desiderata.models import Desiderata, DesiderataOther
from apps.schedule.models.specialreservation import SpecialReservation
from apps.users.models import Employee
from apps.users.utils import StaffPermission

from .serializers import (ClassroomSerializer, CourseDescriptionSerializer,
                          CourseEntitySerializer, CourseSerializer,
                          DesiderataOtherSerializer, DesiderataSerializer,
                          EmployeeSerializer, SemesterSerializer,
                          SpecialReservationSerializer)


class SemesterViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Semester.objects.order_by('-semester_beginning')
    serializer_class = SemesterSerializer


class ClassroomViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (StaffPermission,)
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class DesiderataViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (StaffPermission,)
    queryset = Desiderata.objects.all()
    serializer_class = DesiderataSerializer
    filter_fields = '__all__'


class DesiderataOtherViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (StaffPermission,)
    queryset = DesiderataOther.objects.all()
    serializer_class = DesiderataOtherSerializer
    filter_fields = '__all__'


class SpecialReservationViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = SpecialReservation.objects.all()
    serializer_class = SpecialReservationSerializer
    filter_fields = '__all__'


class CourseEntityViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = CourseEntity.objects.all()
    serializer_class = CourseEntitySerializer
    filter_fields = '__all__'


class CourseDescriptionViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = CourseDescription.objects.all()
    serializer_class = CourseDescriptionSerializer
    filter_fields = '__all__'


class CourseViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_fields = '__all__'
