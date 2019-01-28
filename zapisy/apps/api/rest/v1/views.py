from rest_framework import viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.semester import Semester
from apps.offer.desiderata.models import Desiderata, DesiderataOther
from apps.offer.vote.models import SystemState, SingleVote
from apps.schedule.models.specialreservation import SpecialReservation
from apps.users.models import Employee
from apps.users.utils import StaffPermission

from .serializers import (ClassroomSerializer, DesiderataOtherSerializer,
                          DesiderataSerializer, EmployeeSerializer,
                          SemesterSerializer, SpecialReservationSerializer,
                          SingleVoteSerializer, SystemStateSerializer)


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


class SingleVoteViewSet(viewsets.ModelViewSet):
    """Returns votes by selected state (or all votes otherwise).

    State is passed by GET parameter (e.g. url?state=n). Skips votes with no
    value for clarity.
    """
    http_method_names = ['get']
    permission_classes = (StaffPermission,)
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
    permission_classes = (StaffPermission,)
    queryset = SystemState.objects.all()
    serializer_class = SystemStateSerializer
    filter_fields = '__all__'
