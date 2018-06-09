from rest_framework import routers

from .views import (ClassroomViewSet, CourseDescriptionViewSet,
                    CourseEntityViewSet, CourseViewSet, DesiderataOtherViewSet,
                    DesiderataViewSet, EmployeeViewSet, SemesterViewSet,
                    SpecialReservationViewSet)

router = routers.DefaultRouter()
router.register(r'semesters', SemesterViewSet)
router.register(r'classrooms', ClassroomViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'desideratas', DesiderataViewSet)
router.register(r'desiderata-others', DesiderataOtherViewSet)
router.register(r'special-reservation', SpecialReservationViewSet)
router.register(r'course-entities', CourseEntityViewSet)
router.register(r'course-descriptions', CourseDescriptionViewSet)
router.register(r'courses', CourseViewSet)
