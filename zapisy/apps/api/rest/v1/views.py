from rest_framework import viewsets, pagination
from rest_framework.permissions import IsAdminUser

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models import CourseInstance, Group, Semester
from apps.enrollment.courses.models.term import Term
from apps.enrollment.records.models import Record, RecordStatus
from apps.offer.desiderata.models import Desiderata, DesiderataOther
from apps.offer.vote.models import SystemState, SingleVote
from apps.schedule.models.specialreservation import SpecialReservation
from apps.users.models import Employee, Student

from apps.api.rest.v1 import serializers


class StandardResultsSetPagination(pagination.PageNumberPagination):
    """Paginates objects list."""
    page_size = 200


class SemesterViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Semester.objects.order_by('-semester_beginning')
    serializer_class = serializers.SemesterSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """Lists all courses.

    To only show courses in a given semester, query:
        /api/v1/?semester={semester_id}
    """
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = CourseInstance.objects.select_related('course_type', 'semester').order_by('id')
    filter_fields = ['semester']
    serializer_class = serializers.CourseSerializer
    pagination_class = StandardResultsSetPagination


class GroupViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Group.objects.select_related('course', 'course__semester', 'teacher',
                                            'teacher__user')
    filter_fields = ['course__semester']
    serializer_class = serializers.GroupSerializer
    pagination_class = StandardResultsSetPagination


class ClassroomViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Classroom.objects.all()
    serializer_class = serializers.ClassroomSerializer


class TermViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Term.objects.select_related('group').prefetch_related('classrooms')
    filter_fields = ['group__course__semester']
    serializer_class = serializers.TermSerializer
    pagination_class = StandardResultsSetPagination


class RecordViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    queryset = Record.objects.filter(status=RecordStatus.ENROLLED).select_related(
        'group', 'group__course', 'group__course__semester', 'student', 'student__user')
    filter_fields = ['group__course__semester']
    serializer_class = serializers.RecordSerializer
    pagination_class = StandardResultsSetPagination


class EmployeeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Employee.objects.select_related('user')
    serializer_class = serializers.EmployeeSerializer


class StudentViewSet(viewsets.ModelViewSet):
    """Dumps the list of all the students.

    To only list active students query:
        /api/v1/students/?status=0.
    """
    http_method_names = ['get', 'patch']
    permission_classes = (IsAdminUser,)
    queryset = Student.objects.select_related('user')
    serializer_class = serializers.StudentSerializer
    pagination_class = StandardResultsSetPagination
    filter_fields = ['status']


class DesiderataViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    queryset = Desiderata.objects.all()
    serializer_class = serializers.DesiderataSerializer
    filter_fields = '__all__'


class DesiderataOtherViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    queryset = DesiderataOther.objects.all()
    serializer_class = serializers.DesiderataOtherSerializer
    filter_fields = '__all__'


class SpecialReservationViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    queryset = SpecialReservation.objects.all()
    serializer_class = serializers.SpecialReservationSerializer
    filter_fields = '__all__'


class SingleVoteViewSet(viewsets.ModelViewSet):
    """Returns votes by selected state (or all votes otherwise).

    State is passed by GET parameter (e.g. url?state=n). Skips votes with no
    value for clarity.
    """
    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    serializer_class = serializers.SingleVoteSerializer
    pagination_class = StandardResultsSetPagination
    filter_fields = '__all__'

    def get_queryset(self):
        queryset = SingleVote.objects.select_related('proposal').meaningful()
        system_state_id = self.request.GET.get('state')
        if system_state_id:
            queryset = queryset.filter(state_id=system_state_id)

        return queryset


class SystemStateViewSet(viewsets.ModelViewSet):
    """Get all vote system states"""

    http_method_names = ['get']
    permission_classes = (IsAdminUser,)
    queryset = SystemState.objects.all()
    serializer_class = serializers.SystemStateSerializer
    filter_fields = '__all__'
