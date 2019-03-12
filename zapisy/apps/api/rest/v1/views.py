from rest_framework import viewsets, pagination
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.permissions import IsAdminUser

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models import Course, CourseEntity, Group, Semester
from apps.enrollment.courses.models.term import Term
from apps.offer.desiderata.models import Desiderata, DesiderataOther
from apps.offer.vote.models import SystemState, SingleVote
from apps.schedule.models.specialreservation import SpecialReservation
from apps.users.models import Employee, Student

from .serializers import (CourseSerializer, GroupSerializer, TermSerializer, ClassroomSerializer,
                          DesiderataOtherSerializer, DesiderataSerializer, EmployeeSerializer,
                          StudentSerializer, SemesterSerializer, SpecialReservationSerializer,
                          SingleVoteSerializer, SystemStateSerializer)


class StandardResultsSetPagination(pagination.PageNumberPagination):
    """Paginates objects list."""
    page_size = 200


class SemesterViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Semester.objects.order_by('-semester_beginning')
    serializer_class = SemesterSerializer


class CourseViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Course.objects.select_related('entity', 'entity__type', 'semester')
    filter_fields = ['semester']
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination


class GroupViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Group.objects.select_related('course', 'course__entity', 'course__entity__type',
                                            'course__semester', 'teacher', 'teacher__user')
    filter_fields = ['course__semester']
    serializer_class = GroupSerializer
    pagination_class = StandardResultsSetPagination


class ClassroomViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer


class TermViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Term.objects.select_related('group', 'group__course', 'group__course__entity',
                                           'group__course__semester', 'group__teacher',
                                           'group__teacher__user').prefetch_related('classrooms')
    filter_fields = ['group__course__semester']
    serializer_class = TermSerializer
    pagination_class = StandardResultsSetPagination


class EmployeeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Employee.objects.select_related('user')
    serializer_class = EmployeeSerializer


class StudentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Student.objects.select_related('user')
    serializer_class = StudentSerializer


class DesiderataViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    queryset = Desiderata.objects.all()
    serializer_class = DesiderataSerializer
    filter_fields = '__all__'


class DesiderataOtherViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    queryset = DesiderataOther.objects.all()
    serializer_class = DesiderataOtherSerializer
    filter_fields = '__all__'


class SpecialReservationViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    queryset = SpecialReservation.objects.all()
    serializer_class = SpecialReservationSerializer
    filter_fields = '__all__'


class SingleVoteViewSet(viewsets.ModelViewSet):
    """Returns votes by selected state (or all votes otherwise).

    State is passed by GET parameter (e.g. url?state=n). Skips votes with no
    value for clarity.
    """
    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    serializer_class = SingleVoteSerializer
    filter_fields = '__all__'

    def get_queryset(self):
        queryset = SingleVote.objects.select_related('entity').exclude(value=0, correction=0)
        system_state_id = self.request.GET.get('state')
        if system_state_id:
            queryset = queryset.filter(state_id=system_state_id)

        return queryset


class SystemStateViewSet(viewsets.ModelViewSet):
    """Get all vote system states"""

    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    queryset = SystemState.objects.all()
    serializer_class = SystemStateSerializer
    filter_fields = '__all__'
