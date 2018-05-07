from rest_framework import routers

from .views import ClassroomViewSet, SemesterViewSet, EmployeeViewSet

router = routers.DefaultRouter()
router.register(r'semesters', SemesterViewSet)
router.register(r'classrooms', ClassroomViewSet)
router.register(r'employees', EmployeeViewSet)
