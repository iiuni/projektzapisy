from rest_framework import routers

from .views import (CourseViewSet, GroupViewSet, ClassroomViewSet, TermViewSet, RecordViewSet,
                    DesiderataOtherViewSet, DesiderataViewSet, EmployeeViewSet, StudentViewSet,
                    SemesterViewSet, SpecialReservationViewSet, SystemStateViewSet,
                    SingleVoteViewSet)

router = routers.DefaultRouter()
router.register(r'semesters', SemesterViewSet)
router.register(r'classrooms', ClassroomViewSet)
router.register(r'courses', CourseViewSet, 'courses')
router.register(r'groups', GroupViewSet)
router.register(r'records', RecordViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'students', StudentViewSet)
router.register(r'desideratas', DesiderataViewSet)
router.register(r'desiderata-others', DesiderataOtherViewSet)
router.register(r'special-reservation', SpecialReservationViewSet)
router.register(r'systemstate', SystemStateViewSet)
router.register(r'votes', SingleVoteViewSet, 'Votes')
router.register(r'terms', TermViewSet)
