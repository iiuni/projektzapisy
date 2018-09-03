from django.db.models import QuerySet

from rest_framework import mixins
from rest_framework import generics
from apps.users.models import Student, Employee
from apps.users.serializers import StudentSerializer, EmployeeSerializer


class StudentList(generics.ListAPIView):
    model = Student
    serializer_class = StudentSerializer

    def get_queryset(self) -> QuerySet:
        return super(StudentList, self).get_queryset().filter(status=1).select_related('user')


class StudentDetails(mixins.RetrieveModelMixin):
    model = Student
    serializer = StudentSerializer


class EmployeeList(generics.ListAPIView):
    model = Employee
    serializer_class = EmployeeSerializer
